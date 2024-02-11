from gcloud import storage
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
import date


def save_today_data_to_bucket(csv_data, json_data, bucket_file_path):
    """
    Upload today's CSV and JSON data to a Google Cloud Storage bucket.

    Parameters:
    - csv_data (str): CSV data to be uploaded.
    - json_data (str): JSON data to be uploaded.
    - bucket_file_path (str): Path within the bucket to save both files.

    Returns:
    - None
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

    # Create a blob (file) in the bucket with the specified path
    blob = bucket.blob(bucket_file_path)

    # Upload the CSV data to the blob
    blob.upload_from_string(csv_data, content_type='text/csv')

    # Upload the JSON data to the blob
    blob.upload_from_string(json_data, content_type='application/json')
