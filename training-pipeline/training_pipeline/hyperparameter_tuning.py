from functools import partial
from typing import Optional

import fire
import numpy as np
import pandas as pd
import wandb

from matplotlib import pyplot as plt
from sktime.forecasting.model_evaluation import evaluate as cv_evaluate
from sktime.forecasting.model_selection import ExpandingWindowSplitter
from sktime.performance_metrics.forecasting import MeanAbsolutePercentageError
from sktime.utils.plotting import plot_windows

from training_pipeline import utils
from training_pipeline.configs import gridsearch as gridsearch_configs
from training_pipeline.data import load_dataset_from_feature_store, prepare_data, split_data
from training_pipeline.models import build_model
from training_pipeline.utils import init_wandb_run
from training_pipeline.settings import SETTINGS, OUTPUT_DIR


logger = utils.get_logger(__name__)


def run(
    feature_view_version: Optional[int] = None,
    training_dataset_version: Optional[int] = None,
) -> dict:
    """Run hyperparameter optimization search.

    Args:
        feature_view_version (Optional[int], optional): feature store - feature view version.
             If none, it will try to load the version from the cached feature_view_metadata.json file. Defaults to None.
        training_dataset_version (Optional[int], optional): feature store - feature view - training dataset version.
            If none, it will try to load the version from the cached feature_view_metadata.json file. Defaults to None.

    Returns:
        dict: Dictionary containing metadata about the hyperparameter optimization run.
    """

    feature_view_metadata = utils.load_json("feature_view_metadata.json")
    if feature_view_version is None:
        feature_view_version = feature_view_metadata["feature_view_version"]
    if training_dataset_version is None:
        training_dataset_version = feature_view_metadata["training_dataset_version"]

    y_train, _, X_train, _ = load_dataset_from_feature_store(
        feature_view_version=feature_view_version,
        training_dataset_version=training_dataset_version
    )

    sweep_id = run_hyperparameter_optimization(y_train, X_train)

    metadata = {"sweep_id": sweep_id}
    utils.save_json(metadata, file_name="last_sweep_metadata.json")

    return metadata


def run_hyperparameter_optimization(
    y_train: pd.DataFrame, X_train: pd.DataFrame
):
    """Runs hyperparameter optimization search using W&B sweeps."""

    sweep_id = wandb.sweep(
        sweep=gridsearch_configs.sweep_configs, project=SETTINGS["WANDB_PROJECT"]
    )

    wandb.agent(
        project=SETTINGS["WANDB_PROJECT"],
        sweep_id=sweep_id,
        function=partial(run_sweep, y_train=y_train, X_train=X_train),
    )

    return sweep_id
 

def run_sweep(y_train: pd.DataFrame, X_train: pd.DataFrame):
    """Runs a single hyperparameter optimization step using W&B sweeps."""

    with init_wandb_run(
        name="experiment", job_type="hpo", group="train", add_timestamp_to_name=True
    ) as run:
        run.use_artifact("split_train:latest")

        config = wandb.config
        config = dict(config)
        model = build_model(config)

        model, results = train_model(model, y_train, X_train)
        wandb.log(results)

        metadata = {
            "experiment": {"name": run.name},
            "results": results,
            "config": config,
        }
        artifact = wandb.Artifact(
            name=f"config",
            type="model",
            metadata=metadata,
        )
        run.log_artifact(artifact)

        run.finish()


def train_model(
    model, y_train: pd.DataFrame, X_train: pd.DataFrame
):
    """Train and evaluate the given model"""

    model.fit(X_train,y_train)


    results = model.score(X_train,y_train)

    results = {"training accuracy": results}

    logger.info(f"Training Accuracy: {results['training accuracy']:.2f}")

    return model, results

if __name__ == "__main__":
    fire.Fire(run)
