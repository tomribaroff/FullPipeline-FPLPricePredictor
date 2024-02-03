from gcloud import storage
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
import date


def save_file_to_bucket(input_file_path_csv, input_file_path_json, bucket_file_path, bucket_name):
    """
    Uploads a CSV and a JSON file to a Google Cloud Storage bucket.

    Parameters:
    - input_file_path_csv (str): Local path of the CSV file to be uploaded.
    - input_file_path_json (str): Local path of the JSON file to be uploaded.
    - bucket_file_path (str): Path within the bucket to save both files.
    - bucket_name (str): Name of the Google Cloud Storage bucket.

    Returns:
    - None
    """

    # Load environment variables from .env file
    load_dotenv()

    # Retrieve Google Cloud Storage service account JSON path and project ID from environment variables
    creds = os.getenv('JSON_SA_BATCH_PREDICTION_PATH')
    gcp_project_id = os.getenv('GCP_PROJECT_ID')

    # Load service account credentials from JSON file
    with open(creds) as json_file:
        data = json.load(json_file)

    # Create service account credentials from JSON keyfile
    credentials = service_account.Credentials.from_service_account_info(data)

    # Create a Google Cloud Storage client with the provided credentials and project ID
    client = storage.Client(credentials=credentials, project=gcp_project_id)

    # Get the specified bucket
    bucket = client.get_bucket(bucket_name)

    # Create a blob (file) in the bucket with the specified path
    blob = bucket.blob(bucket_file_path)

    # Upload the contents of the CSV file to the blob
    with open(input_file_path_csv, 'rb') as csv_file:
        blob.upload_from_file(csv_file, content_type='application/octet-stream')

    # Upload the contents of the JSON file to the blob
    with open(input_file_path_json, 'rb') as json_file:
        blob.upload_from_file(json_file, content_type='application/json')


# Get today's date
# today = date.today() 
# input_file_path_csv = Path('./Pipeline-Steps/Saved_Data/{}/{}.csv'.format(today,today)) 
# input_file_path_json = Path('./Pipeline-Steps/Saved_Data/{}/{}.json'.format(today,today)') 
# bucket_file_path = today
# bucket = 'batch_prediction_store_bucket'
# save_file_to_bucket(input_file_path_csv, input_file_path_json, bucket_file_path, bucket)

