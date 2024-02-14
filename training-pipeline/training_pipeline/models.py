import lightgbm as lgb

from sktime.forecasting.compose import make_reduction, ForecastingPipeline
from sktime.forecasting.naive import NaiveForecaster
from sktime.transformations.series.date import DateTimeFeatures
from sktime.transformations.series.summarize import WindowSummarizer


def build_model(config: dict): 
    """
    Build an LightGBM model using the given config.
    """
    model = lgb.LGBMClassifier(**config)

    return model


def build_baseline_model(seasonal_periodicity: int):
    """Builds a dummy classifier baseline model that predicts zero price change for all players."""

    model = DummyClassifier(strategy='constant', constant=0)

    return model)
