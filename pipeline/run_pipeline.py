import datetime
from typing import Optional
import fire
import pandas as pd

from pipeline import logs

logger = logs.get_logger(__name__)


# def run():
#     """
#     Extract data from the API, transform it, load it to a GCP bucket, and update past uploads with new information

#     """

#     logger.info(f"Extracting data from API.")
#     data, metadata = extract.from_file(
#         export_end_reference_datetime, days_delay, days_export, url
#     )
#     if metadata["num_unique_samples_per_time_series"] < days_export * 24:
#         raise RuntimeError(
#             f"Could not extract the expected number of samples from the api: {metadata['num_unique_samples_per_time_series']} < {days_export * 24}. \
#             Check out the API at: https://www.energidataservice.dk/tso-electricity/ConsumptionDE35Hour "
#         )
#     logger.info("Successfully extracted data from API.")

#     logger.info(f"Transforming data.")
#     data = transform(data)
#     logger.info("Successfully transformed data.")

#     logger.info("Building validation expectation suite.")
#     validation_expectation_suite = validation.build_expectation_suite()
#     logger.info("Successfully built validation expectation suite.")

#     logger.info(f"Validating data and loading it to the feature store.")
#     load.to_feature_store(
#         data,
#         validation_expectation_suite=validation_expectation_suite,
#         feature_group_version=feature_group_version,
#     )
#     metadata["feature_group_version"] = feature_group_version
#     logger.info("Successfully validated data and loaded it to the feature store.")

#     logger.info(f"Wrapping up the pipeline.")
#     utils.save_json(metadata, file_name="feature_pipeline_metadata.json")
#     logger.info("Done!")

#     return metadata


# def transform(data: pd.DataFrame):
#     """
#     Wrapper containing all the transformations from the ETL pipeline.
#     """

#     data = cleaning.rename_columns(data)
#     data = cleaning.cast_columns(data)
#     data = cleaning.encode_area_column(data)

#     return data


# if __name__ == "__main__":
#     fire.Fire(run)