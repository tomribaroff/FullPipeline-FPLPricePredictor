from google.cloud import storage
from google.oauth2 import service_account
from dotenv import load_dotenv
import os
import json
import pandas as pd
from io import StringIO

def download_yesterday_csv_from_bucket(bucket_file_path, bucket_name):
    """
    Downloads a CSV file from a Google Cloud Storage bucket and returns its contents as a Pandas DataFrame.

    Parameters:
    - bucket_file_path (str): Path of the CSV file within the Google Cloud Storage bucket.
    - bucket_name (str): Name of the Google Cloud Storage bucket.

    Returns:
    - pd.DataFrame: Contents of the downloaded CSV file as a DataFrame.
    """

    # Load environment variables from .env file
    load_dotenv()

    # Retrieve Google Cloud Storage service account JSON path and project ID from environment variables
    creds = os.getenv('JSON_SA_RAW_DATA_PATH')
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

    # Get the blob (CSV file) from the bucket
    blob = bucket.blob(bucket_file_path)

    # Download the contents of the blob as a string
    csv_content = blob.download_as_text()

    # Create a Pandas DataFrame from the CSV content
    df = pd.read_csv(StringIO(csv_content))

    return df
