from datetime import date, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
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

@task.virtualenv(
        task_id="run_feature_pipeline",
        requirements=[
            "--trusted-host 172.17.0.1",
            "--extra-index-url http://172.17.0.1",
            "feature_pipeline",
        ],
        python_version="3.9",
    )
    def run_feature_pipeline():
        """
        Run the feature engineering pipeline.
        """

        from feature_engineering_pipeline import run_pipeline

        return run_pipeline.run(
            date.today() 
        )


run_feature_pipeline

# # Define dependencies
# fetch_task >> feature_engineering_task >> save_to_gcs_task
# save_to_gcs_task >> update_yesterday_data_task
# update_yesterday_data_task #>> upload_to_feature_store_task

