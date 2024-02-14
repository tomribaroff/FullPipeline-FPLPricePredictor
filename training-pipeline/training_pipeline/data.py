from typing import Tuple
import hopsworks
import pandas as pd
import wandb

from sklearn.model_selection import train_test_split

from training_pipeline.utils import init_wandb_run
from training_pipeline.settings import SETTINGS


def load_dataset_from_feature_store(
    feature_view_version: int, training_dataset_version: int
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load features from feature store.

    Args:
        feature_view_version (int): feature store feature view version to load data from
        training_dataset_version (int): feature store training dataset version to load data from

    Returns:
        Train and test splits loaded from the feature store as pandas dataframes.
    """

    project = hopsworks.login(
        api_key_value=SETTINGS["FS_API_KEY"], project=SETTINGS["FS_PROJECT_NAME"]
    )
    fs = project.get_feature_store()

    with init_wandb_run(
        name="load_training_data", job_type="load_feature_view", group="dataset"
    ) as run:
        feature_view = fs.get_feature_view(
            name="player_price_changes_view", version=feature_view_version
        )
        data, _ = feature_view.get_training_data(
            training_dataset_version=training_dataset_version
        )

        fv_metadata = feature_view.to_dict()
        fv_metadata["query"] = fv_metadata["query"].to_string()
        fv_metadata["features"] = [f.name for f in fv_metadata["features"]]
        fv_metadata["link"] = feature_view._feature_view_engine._get_feature_view_url(
            feature_view
        )
        fv_metadata["feature_view_version"] = feature_view_version
        fv_metadata["training_dataset_version"] = training_dataset_version

        raw_data_at = wandb.Artifact(
            name="player_price_changes_feature_view",
            type="feature_view",
            metadata=fv_metadata,
        )
        run.log_artifact(raw_data_at)

        run.finish()

    with init_wandb_run(
        name="train_test_split", job_type="split_dataset", group="dataset"
    ) as run:
        run.use_artifact("player_price_changes_feature_view:latest")

        y_train, y_test, X_train, X_test = prepare_data(data)

        for split in ["train", "test"]:
            split_X = locals()[f"X_{split}"]
            split_y = locals()[f"y_{split}"]

            split_metadata = {
                "timespan": [
                    split_X.index.get_level_values(-2).min(),
                    split_X.index.get_level_values(-2).max(),
                ],
                "dataset_size": len(split_X),
                "num_areas": len(split_X.index.get_level_values(0).unique()),
                "num_consumer_types": len(split_X.index.get_level_values(1).unique()),
                "y_features": split_y.columns.tolist(),
                "X_features": split_X.columns.tolist(),
            }
            artifact = wandb.Artifact(
                name=f"split_{split}",
                type="split",
                metadata=split_metadata,
            )
            run.log_artifact(artifact)

        run.finish()

    return y_train, y_test, X_train, X_test


def prepare_data(
    data: pd.DataFrame, target: str = "price_change_this_night"
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Split the Dataset into train and test sets 
    """
    # Defining our X (features) and y (target) values
    features = data.drop(columns=[target])
    target = data[[target]]
 
    # Splitting the dataset into train and validation sets
    X_train, X_test, y_train, y_test = train_test_split(features, target,
                                        random_state=2023,
                                        test_size=0.20)

    return y_train, y_test, X_train, X_test
