import fire
import pandas as pd

import logs,validation
from preprocess_data import preprocess_data_from_json
from fetch_data_from_api import extract_current_data_from_api_overall
from create_todays_dataframe import create_todays_dataframe_from_raw_csvs
from download_file_from_bucket import download_yesterday_csv_from_bucket
from update_yesterday_data import update_yesterday_data_values
from save_today_files_to_bucket import save_today_data_to_bucket
from overwrite_yesterdays_data import overwrite_yesterdays_csv
#from save_data_to_feature_store import to_feature_store

from datetime import date
from datetime import timedelta

logger = logs.get_logger(__name__)

# Get today's date
today = date.today() 

# Get yesterday date
yesterday = today - timedelta(days = 1) 

def run(today_date):
    """
    Extract data from the API, 
    transform it, 
    save json and CSV to a GCP bucket, 
    update past CSV with new information, 
    overwrite past CSV in bucket with updated past CSV, 
    upload updated past CSV to feature store

    """

    logger.info(f"ETL Pipeline run on {today_date}")

    logger.info(f"Extracting data from API.")
    today_json = extract_current_data_from_api_overall
    logger.info("Successfully extracted data from API.")

    logger.info(f"Preprocessing data.")
    overall_events_data, todays_player_data, total_players = preprocess_data_from_json(today_json)
    logger.info("Successfully preprocessed data.")

    logger.info(f"Create today's DataFrame.")
    today_df = create_todays_dataframe_from_raw_csvs(overall_events_data, todays_player_data, total_players)
    logger.info(f"Sucessfully created today's DataFrame.")

    logger.info(f"Download yesterday's DataFrame.")
    yesterday_df = download_yesterday_csv_from_bucket('{}/{}.csv'.format(yesterday, yesterday))
    logger.info(f"Successfully downloaded yesterday's DataFrame.")

    logger.info(f"Update yesterday's df according to today's df and vice versa.")
    yesterday_df, today_df = update_yesterday_data_values(yesterday_df, today_df) 
    logger.info(f"Successfully updated Dataframes")

    logger.info(f"Save today's CSV and JSON to bucket")
    save_today_data_to_bucket(today_df, today_json, '{}/{}.csv'.format(today, today))
    logger.info(f"Successfully saved today's CSV and JSON to bucket")

    logger.info(f"Overwrite yesterday's CSV to bucket")
    overwrite_yesterdays_csv(yesterday_df, '{}/{}.csv'.format(yesterday, yesterday)) 
    logger.info(f"Successfully overwritten yesterday's CSV to bucket")

    # logger.info("Building validation expectation suite.")
    # validation_expectation_suite = validation.build_expectation_suite()
    # logger.info("Successfully built validation expectation suite.")

    # logger.info(f"Validating data and loading yesterday's complete dataset to the feature store.")
    # save_data_to_feature_store.to_feature_store(
    #     data,
    #     validation_expectation_suite=validation_expectation_suite,
    #     feature_group_version=feature_group_version,
    # )
    # logger.info("Successfully validated data and loaded it to the feature store.")

    logger.info(f"Successfully completion of ETL pipeline loop")

if __name__ == "__main__":
    fire.Fire(run)