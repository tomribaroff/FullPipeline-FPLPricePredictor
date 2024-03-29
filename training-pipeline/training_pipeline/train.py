import json
from collections import OrderedDict
import os
from pathlib import Path
from typing import OrderedDict as OrderedDictType, Optional, Tuple

import fire
import hopsworks
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import wandb
from sktime.performance_metrics.forecasting import (
    mean_squared_percentage_error,
    mean_absolute_percentage_error,
)
from sktime.utils.plotting import plot_series


from training_pipeline import utils
from training_pipeline.settings import SETTINGS, OUTPUT_DIR
from training_pipeline.data import load_dataset_from_feature_store

import lightgbm as lgb

from sktime.forecasting.compose import make_reduction, ForecastingPipeline
from sklearn.dummy import DummyClassifier
from sktime.transformations.series.date import DateTimeFeatures
from sktime.transformations.series.summarize import WindowSummarizer

from training_pipeline import transformers


logger = utils.get_logger(__name__)

def from_best_config(
    feature_view_version: Optional[int] = None,
    training_dataset_version: Optional[int] = None,
) -> dict:
    """Train and evaluate on the test set the best model found in the hyperparameter optimization run.
    After training and evaluating it uploads the artifacts to wandb & hopsworks model registries.

    Args:
        feature_view_version (Optional[int], optional): feature store - feature view version.
             If none, it will try to load the version from the cached feature_view_metadata.json file. Defaults to None.
        training_dataset_version (Optional[int], optional): feature store - feature view - training dataset version.
            If none, it will try to load the version from the cached feature_view_metadata.json file. Defaults to None.

    Returns:
        dict: Dictionary containing metadata about the training experiment.
    """

    feature_view_metadata = utils.load_json("feature_view_metadata.json")
    if feature_view_version is None:
        feature_view_version = feature_view_metadata["feature_view_version"]
    if training_dataset_version is None:
        training_dataset_version = feature_view_metadata["training_dataset_version"]

    y_train, y_test, X_train, X_test = load_dataset_from_feature_store(
        feature_view_version=feature_view_version,
        training_dataset_version=training_dataset_version,
    )

    training_length= len(y_train)
    testing_length = len(y_test)
    
    logger.info(
        f"Training model on {training_length} data instances."
    )
    logger.info(
        f"Testing model on {testing_length} data instances."
    )

    with utils.init_wandb_run(
        name="best_model",
        job_type="train_best_model",
        group="train",
        reinit=True,
        add_timestamp_to_name=True,
    ) as run:
        run.use_artifact("split_train:latest")
        run.use_artifact("split_test:latest")
        # Load the best config from sweep.
        best_config_artifact = run.use_artifact(
            "best_config:latest",
            type="model",
        )
        download_dir = best_config_artifact.download()
        config_path = Path(download_dir) / "best_config.json"
        with open(config_path) as f:
            config = json.load(f)
        # Log the config to the experiment.
        run.config.update(config)

        # # Baseline model
        baseline_forecaster = build_baseline_model()
        baseline_forecaster = train_model(baseline_forecaster, y_train, X_train)
        _, metrics_baseline = evaluate(baseline_forecaster, y_test, X_test)
        
        for k, v in metrics_baseline.items():
            logger.info(f"Baseline test {k}: {v}")
        wandb.log({"test": {"baseline": metrics_baseline}})
        

        # Build & train best model.
        best_model = build_model(config)
        best_classifier = train_model(best_model, y_train, X_train)

        # Evaluate best model
        y_pred, metrics = evaluate(best_model, y_test, X_test)

        for k, v in metrics.items():
            logger.info(f"Model test {k}: {v}")
        wandb.log({"test": {"model": metrics}})

        # Render best model on the test set.
        results = OrderedDict({"y_train": y_train, "y_test": y_test, "y_pred": y_pred})
       

        # Update best model with the test set.
        # NOTE: Method update() is not supported by LightGBM + Sktime. Instead we will retrain the model on the entire dataset.
        # best_forecaster = best_forecaster.update(y_test, X=X_test)
        best_classifier = train_model(
            model=best_classifier,
            y_train=pd.concat([y_train, y_test]).sort_index(),
            X_train=pd.concat([X_train, X_test]).sort_index()
        )

        # Save best model.
        save_model_path = OUTPUT_DIR / "best_model.pkl"
        utils.save_model(best_classifier, save_model_path)
        metadata = {
            "experiment": {
                "feature_view_version": feature_view_version,
                "training_dataset_version": training_dataset_version,
                "training_dataset_length": training_length,
                "testing_dataset_length": testing_length,
            },
            "results": {"test": metrics},
        }
        artifact = wandb.Artifact(name="best_model", type="model", metadata=metadata)
        artifact.add_file(str(save_model_path))
        run.log_artifact(artifact)

        run.finish()
        artifact.wait()

    model_version = add_best_model_to_model_registry(artifact)

    metadata = {"model_version": model_version}
    utils.save_json(metadata, file_name="train_metadata.json")

    return metadata

def train_model(model, y_train: pd.DataFrame, X_train: pd.DataFrame):
    """Train a classifier on the given training set."""

    model.fit(y_train, X_train) 

    return model

def evaluate(
    model, y_test: pd.DataFrame, X_test: pd.DataFrame
) -> Tuple[pd.DataFrame, dict]:
    """Evaluate the model on the test set by computing the following metrics:
        - RMSPE
        - MAPE

    Args:
        model: model as defined by user, either DummyClassifier or LightGBM Classifier
        y_test (pd.DataFrame): players price changes to predict
        X_test (pd.DataFrame): exogenous variables

    Returns:
        The predictions as a pd.DataFrame and a dict of metrics.
    """

    y_pred = model.predict(X=X_test)

    # Compute aggregated metrics.
    results = dict()
    rmspe = mean_squared_percentage_error(y_test, y_pred, squared=False) 
    results["RMSPE"] = rmspe
    mape = mean_absolute_percentage_error(y_test, y_pred, symmetric=False)
    results["MAPE"] = mape

    return y_pred, results


def add_best_model_to_model_registry(best_model_artifact: wandb.Artifact) -> int:
    """Adds the best model artifact to the model registry."""

    project = hopsworks.login(
        api_key_value=SETTINGS["FS_API_KEY"], project=SETTINGS["FS_PROJECT_NAME"]
    )

    # Upload the model to the Hopsworks model registry.
    best_model_dir = best_model_artifact.download()
    best_model_path = Path(best_model_dir) / "best_model.pkl"
    best_model_metrics = best_model_artifact.metadata["results"]["test"]

    mr = project.get_model_registry()
    py_model = mr.python.create_model("best_model", metrics=best_model_metrics)
    py_model.save(best_model_path)

    return py_model.version


if __name__ == "__main__":
    fire.Fire(from_best_config)





