from datetime import date, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from airflow.providers.google.cloud.transfers.gcs_to_local import GCSToLocalFilesystemOperator
from airflow.providers.google.cloud.transfers.gcs_to_gcs import GCSToGCSOperator
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import datetime
import os
import json
from io import StringIO
from google.cloud import storage
from google.oauth2 import service_account
import requests
from typing import Dict, Optional, Tuple

import feature_engineering
from update_yesterday_data_rows import update_yesterday_data_rows_align

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 2, 20),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

#TODO test each airflow task runs locally https://airflow.apache.org/docs/apache-airflow/stable/start.html

#TODO test entire pipeline can run locally 

#TODO instead of then asking Airflow to run this daily, we are going to run it in VertexAI https://cloud.google.com/vertex-ai/docs/pipelines/introduction
#we could write 

dag = DAG(
    'data_processing_dag',
    default_args=default_args,
    description='DAG for fetching, processing, and uploading data',
    schedule=timedelta(days=1),  # Runs daily
)

# Get today's date
today = date.today() 

# Get yesterday date
yesterday = today - timedelta(days = 1) 

def extract_current_data_from_api_overall(**kwargs) -> Optional[Dict]:
    """
    Extract data from the Fantasy Football Data API that contains data on all player transfers 

    IMPORTANT NOTE: a Complete Guide to the API’s that Fantasy Football offers can be found here:
https://www.game-change.co.uk/2023/02/10/a-complete-guide-to-the-fantasy-premier-league-fpl-api/

    Args:
        kwargs: Airflow task context

    Returns:
          A dictionary of extracted data
    """
    base_url = 'https://fantasy.premierleague.com/api/'
    r_all_players_today = requests.get(base_url+'bootstrap-static/').json()

    # Push the data to XComs
    kwargs['ti'].xcom_push(key='json_data', value=r_all_players_today)

    return r_all_players_today

def preprocess_data_from_json(**kwargs) -> Tuple[pd.DataFrame, pd.DataFrame, int]:
    """
    Extracts information from a JSON file and returns two DataFrames and a total player count.

    Parameters:
    - json_file (Dict): A dictionary containing 'events', 'elements', and 'total_players'.

    Returns:
    - pd.DataFrame: DataFrame containing overall events data.
    - pd.DataFrame: DataFrame containing today's player data.
    - int: Total number of players.
    """

    # Pull the JSON data from XComs
    json_file = kwargs['ti'].xcom_pull(task_ids='extract_data', key='json_data')

    
    overall_events_data = pd.DataFrame(json_file['events'])
    todays_player_data = pd.DataFrame(json_file['elements'])
    total_players = int(json_file['total_players'])

    # Push the data to XComs
    kwargs['ti'].xcom_push(key='overall_events_data', value=overall_events_data)
    kwargs['ti'].xcom_push(key='todays_player_data', value=todays_player_data)
    kwargs['ti'].xcom_push(key='total_players', value=total_players)

    return overall_events_data, todays_player_data, total_players

def create_todays_dataframe_from_raw_csvs(**kwargs) -> pd.DataFrame:
                                         
    # Create DataFrame from dictionary of all this transfer data
    # Player transfer data from the API is updated at least every 40 minutes, and probably every 15 - 30 mins. 

    # Pull the JSON data from XComs
    overall_events_data = kwargs['ti'].xcom_pull(task_ids='preprocess_data', key='overall_events_data')
    todays_player_data = kwargs['ti'].xcom_pull(task_ids='preprocess_data', key='todays_player_data')
    total_players = kwargs['ti'].xcom_pull(task_ids='preprocess_data', key='total_players')


    all_players_price_change_for_current_event = feature_engineering.extract_all_players_price_changes_this_event(todays_player_data)
    total_active_players_estimate = feature_engineering.estimate_active_players(overall_events_data, total_players)
    boolean_list_of_players_injured = feature_engineering.extract_all_players_injured(todays_player_data)
    all_players_prices_today = feature_engineering.extract_all_players_prices_now(todays_player_data)
    net_transfers_overall_today = feature_engineering.calculate_net_transfers_overall(todays_player_data)

    # Create DataFrame from dictionary of all this transfer data

    price_change_dict = {
        "price_change_this_night": np.nan, #tomorrow, we define this as today_data.player_prices_today - yesterday_data.player_prices_today
        "net_transfers_in_out_since_last_price_change": 0, #tomorrow, we define this as yesterday_data.net_transfers_in_out_since_last_price_change + today_data_net_transfers_in_out_since_yesterday, unless price change occurs, then we reset to ="Net Transfers In/Out since yesterday
        "net_transfers_in_out_this_day": 0, #tomorrow, we define this as today_data.net_transfers_in_out_overall_as_of_today - yesterday_data.net_transfers_in_out_overall_as_of_today
        "price_change_so_far_for_this_event ": all_players_price_change_for_current_event,
        "total_active_players_estimate": total_active_players_estimate,
        "players_injured": boolean_list_of_players_injured,
        "player_prices_today" : all_players_prices_today,
        "net_transfers_in_out_overall_as_of_today" : net_transfers_overall_today, #not to be used in modelling
        "player_ids" : todays_player_data.id,
        "player_name": todays_player_data.web_name
    }

    # Dictionary into DataFrame
    today_data = pd.DataFrame(price_change_dict)

    # Push the data to XComs
    kwargs['ti'].xcom_push(key='today_data', value=today_data)

    return today_data

def download_yesterday_csv_from_bucket(bucket_file_path = '{}/{}.csv'.format(yesterday, yesterday), **kwargs):
    """
    Downloads a CSV file from a Google Cloud Storage bucket and returns its contents as a Pandas DataFrame.

    Parameters:
    - bucket_file_path (str): Path of the CSV file within the Google Cloud Storage bucket.

    Returns:
    - pd.DataFrame: Contents of the downloaded CSV file as a DataFrame.
    """

    # Load environment variables from .env file
    load_dotenv()

    # Retrieve Google Cloud Storage service account JSON path and project ID from environment variables
    creds = os.getenv('JSON_SA_READ_WRITE_PATH')
    gcp_project_id = os.getenv('GCP_PROJECT_ID')
    gcp_bucket_name = os.getenv('GCP_BUCKET_NAME')

    # Load service account credentials from JSON file
    with open(creds) as json_file:
        data = json.load(json_file)

    # Create service account credentials from JSON keyfile
    credentials = service_account.Credentials.from_service_account_info(data)

    # Create a Google Cloud Storage client with the provided credentials and project ID
    client = storage.Client(credentials=credentials, project=gcp_project_id)

    # Get the specified bucket
    bucket = client.get_bucket(gcp_bucket_name)

    # Get the blob (CSV file) from the bucket
    blob = bucket.blob(bucket_file_path)

    # Download the contents of the blob as a string
    csv_content = blob.download_as_text()

    # Create a Pandas DataFrame from the CSV content
    df = pd.read_csv(StringIO(csv_content))

    # Push the data to XComs
    kwargs['ti'].xcom_push(key='yesterday_data', value=df)

    return df

def update_yesterday_data_values(yesterday_df, today_df, **kwargs):

    # Pull the JSON data from XComs
    yesterday_data = kwargs['ti'].xcom_pull(task_ids='download_yesterday_data', key='yesterday_data')
    today_data = kwargs['ti'].xcom_pull(task_ids='create_today_data', key='today_data')
    

    yesterday_data, today_data = update_yesterday_data_rows_align(yesterday_data, today_data)

    # #updates 
    yesterday_data.price_change_this_night = today_data.player_prices_today - yesterday_data.player_prices_today
    today_data.net_transfers_in_out_this_day = today_data.net_transfers_in_out_overall_as_of_today - yesterday_data.net_transfers_in_out_overall_as_of_today
    today_data.net_transfers_in_out_since_last_price_change = yesterday_data.net_transfers_in_out_since_last_price_change

    # Update net transfer since last price change in today's data 
    yesterday_data.net_transfers_in_out_since_last_price_change = yesterday_data.net_transfers_in_out_since_last_price_change + yesterday_data.net_transfers_in_out_this_day

    #reset rule if price changed overnight 
    boolean_player_changes = np.squeeze(yesterday_data.price_change_this_night != 0)
    today_data.net_transfers_in_out_since_last_price_change = [today_data.net_transfers_in_out_this_day[i] if boolean_player_changes[i] else today_data.net_transfers_in_out_since_last_price_change[i] for i in today_data.net_transfers_in_out_since_last_price_change.index]

    # Push the data to XComs
    kwargs['ti'].xcom_push(key='yesterday_data', value=yesterday_data)
    kwargs['ti'].xcom_push(key='today_data', value=today_data)

    return yesterday_df, today_df

def save_today_data_to_bucket(bucket_file_path = '{}/{}.csv'.format(today, today), **kwargs):
    """
    Upload today's CSV and JSON data to a Google Cloud Storage bucket.

    Parameters:
    - bucket_file_path (str): Path within the bucket to save both files.

    Returns:
    - None
    """

    # Pull the JSON data from XComs
    csv_data = kwargs['ti'].xcom_pull(task_ids='update_yesterday_data', key='today_data')
    json_data = kwargs['ti'].xcom_pull(task_ids='extract_data', key='json_data')
    

    # Load environment variables from .env file
    load_dotenv()

    # Retrieve Google Cloud Storage service account JSON path and project ID from environment variables
    creds = os.getenv('JSON_SA_READ_WRITE_PATH')
    gcp_project_id = os.getenv('GCP_PROJECT_ID')
    gcp_bucket_name = os.getenv('GCP_BUCKET_NAME')

    # Load service account credentials from JSON file
    with open(creds) as json_file:
        data = json.load(json_file)

    # Create service account credentials from JSON keyfile
    credentials = service_account.Credentials.from_service_account_info(data)

    # Create a Google Cloud Storage client with the provided credentials and project ID
    client = storage.Client(credentials=credentials, project=gcp_project_id)

    # Get the specified bucket
    bucket = client.get_bucket(gcp_bucket_name)

    # Create a blob (file) in the bucket with the specified path
    blob = bucket.blob(bucket_file_path)

    # Upload the CSV data to the blob
    blob.upload_from_string(csv_data, content_type='text/csv')

    # Upload the JSON data to the blob
    blob.upload_from_string(json_data, content_type='application/json')

def overwrite_yesterdays_csv(bucket_file_path = '{}/{}.csv'.format(yesterday, yesterday), **kwargs):
    """
    Deletes existing file for yesterday's data, and then uploads the updated copy to a Google Cloud Storage bucket.

    Parameters:
    - local_file_path (str): Local path of the file to be uploaded.
    - bucket_file_path (str): Path to the destination file within the Google Cloud Storage bucket.

    Returns:
    - None
    """

    # Pull the JSON data from XComs
    yesterday_csv_updated = kwargs['ti'].xcom_pull(task_ids='update_yesterday_data', key='yesterday_data')

    # Load service account credentials from JSON file
    creds = os.getenv('JSON_SA_READ_WRITE_PATH')
    credentials = service_account.Credentials.from_service_account_file(creds)
    gcp_bucket_name = os.getenv('GCP_BUCKET_NAME')

    # Create a Google Cloud Storage client with the provided credentials
    client = storage.Client(credentials=credentials)

    # Get the specified bucket
    bucket = client.get_bucket(gcp_bucket_name)

    # Get the blob (file) from the bucket with the same name, if it exists
    blob = bucket.blob(bucket_file_path)

    # Delete the existing file (if it exists)
    blob.delete()

    # Upload the new file
    blob.upload_from_string(yesterday_csv_updated, content_type='text/csv')


extract_data_task = PythonOperator(
    task_id='extract_data',
    python_callable=extract_current_data_from_api_overall,
    provide_context=True,
    dag=dag,
)

#TODO https://airflow.apache.org/docs/apache-airflow-providers-google/stable/operators/transfer/local_to_gcs.html
# Actually, I think it is better not to save the files locally at all. I can use functions to download files locally 
# as variables and then push them to xcoms. 
#TODO https://airflow.apache.org/docs/apache-airflow-providers-google/stable/connections/gcp.html
# I believe this should work now that the .env file has the information it needs

preprocess_data_task = PythonOperator(
    task_id='preprocess_data',
    provide_context=True,
    python_callable=preprocess_data_from_json,
    dag=dag,
)

create_today_data_task = PythonOperator(
    task_id='create_today_data',
    provide_context=True,
    python_callable=create_todays_dataframe_from_raw_csvs,
    dag=dag,
)

download_yesterday_data_task = PythonOperator(
    task_id='download_yesterday_data',
    provide_context=True,
    python_callable=download_yesterday_csv_from_bucket,
    dag=dag,
)

update_yesterday_data_task = PythonOperator(
    task_id='update_yesterday_data',
    provide_context=True,
    python_callable=update_yesterday_data_values,
    dag=dag,
)

save_today_data_task = PythonOperator(
    task_id='save_today_data',
    provide_context=True,
    python_callable=save_today_data_to_bucket,
    dag=dag,
)
overwrite_yesterdays_csv_task = PythonOperator(
    task_id='overwrite_yesterdays_csv',
    provide_context=True,
    python_callable=overwrite_yesterdays_csv,
    dag=dag,
)

#TODO get this validation suite done 

# build_validation_suite_task = PythonOperator(
#     task_id='build_validation_suite',
#     python_callable=build_validation_suite,
#     dag=dag,
# )

# save_data_to_feature_store_task = PythonOperator(
#     task_id='save_data_to_feature_store',
#     python_callable=save_data_to_feature_store,
#     dag=dag,
# )

#TODO with dag() ?
# No, this syntax should work 

# Define dependencies
extract_data_task >> preprocess_data_task >> create_today_data_task
download_yesterday_data_task >> update_yesterday_data_task
save_today_data_task >> overwrite_yesterdays_csv_task
#build_validation_suite_task >> save_data_to_feature_store_task