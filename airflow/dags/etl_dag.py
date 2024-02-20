from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from airflow.providers.google.cloud.transfers.gcs_to_gcs import GCSToGCSOperator

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 2, 20),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'data_processing_dag',
    default_args=default_args,
    description='DAG for fetching, processing, and uploading data',
    schedule=timedelta(days=1),  # Runs daily
)

def fetch_data(**kwargs):

    import requests
    #call today's data from the API
    base_url = 'https://fantasy.premierleague.com/api/'
    r_all_players_today = requests.get(base_url+'bootstrap-static/').json()
    return r_all_players_today

def feature_engineering(**kwargs):

    import pandas as pd
    import numpy as np

    #split json into dataframes
    json_file = kwargs['json_file']
    overall_events_data = pd.DataFrame(json_file['events'])
    todays_player_data = pd.DataFrame(json_file['elements'])
    total_players = int(json_file['total_players'])

    # Create DataFrame from dictionary of all this transfer data
    # Player transfer data from the API is updated at least every 40 minutes, and probably every 15 - 30 mins. 

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

    return today_data

def save_to_gcs(**kwargs):
    # Your code to save data to GCS bucket
    pass

def update_yesterday_data(**kwargs):
    # Your code to update yesterday's data in GCS bucket
    pass

def upload_to_feature_store(**kwargs):
    # Your code to upload data to the feature store
    pass

fetch_task = PythonOperator(
    task_id='fetch_data',
    python_callable=fetch_data,
    dag=dag,
)

feature_engineering_task = PythonOperator(
    task_id='feature_engineering',
    python_callable=feature_engineering,
    dag=dag,
)

save_to_gcs_task = PythonOperator(
    task_id='save_to_gcs',
    python_callable=save_to_gcs,
    dag=dag,
)

update_yesterday_data_task = PythonOperator(
    task_id='update_yesterday_data',
    python_callable=update_yesterday_data,
    dag=dag,
)

upload_to_feature_store_task = PythonOperator(
    task_id='upload_to_feature_store',
    python_callable=upload_to_feature_store,
    dag=dag,
)

# Define dependencies
fetch_task >> feature_engineering_task >> save_to_gcs_task
save_to_gcs_task >> update_yesterday_data_task
update_yesterday_data_task >> upload_to_feature_store_task
