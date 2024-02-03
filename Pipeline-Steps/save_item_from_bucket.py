from gcloud import storage
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
import date

def save_file_from_bucket(local_file_path, bucket_file_path, bucket_name):
    """
    Downloads a file (or files) from a Google Cloud Storage bucket and saves it locally.

    Parameters:
    - local_file_path (str): Local path where the downloaded file(s) will be saved.
    - bucket_file_path (str): Path of the file(s) within the Google Cloud Storage bucket.
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

    # Get the blob (file(s)) from the bucket
    blob = bucket.blob(bucket_file_path)

    # Download the contents of the blob to the specified local file path
    blob.download_to_filename(local_file_path)

# Get today's date
# today = date.today() 
# input_file_path_csv = Path('./Pipeline-Steps/Saved_Data/{}/{}.csv'.format(today,today)) 
# bucket_file_path = today
# bucket = 'batch_prediction_store_bucket'
# save_file_from_bucket(input_file_path, bucket_file_path, bucket)
