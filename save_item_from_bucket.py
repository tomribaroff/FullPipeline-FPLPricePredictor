from gcloud import storage
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
import date


def save_file_from_bucket(local_file_path, bucket_file_path, bucket_name):

    load_dotenv()
    creds = os.getenv('JSON_SA_BATCH_PREDICTION_PATH')
    gcp_project_id = os.getenv('GCP_PROJECT_ID')

    with open(creds) as json_file:
        data = json.load(json_file)
    
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(data)

    client = storage.Client(credentials=credentials, project=gcp_project_id)

    bucket = client.get_bucket(bucket_name)

    # Get the blob from the bucket
    blob = bucket.blob(bucket_file_path)

    # Download the blob contents to the local file
    blob.download_to_filename(local_file_path)

# Get today's date
today = date.today() 

input_file_path_csv = Path('./Pipeline-Steps/Saved_Data/{}/{}.csv'.format(today,today)) 
bucket_file_path = today
bucket = 'batch_prediction_store_bucket'
save_file_from_bucket(input_file_path, bucket_file_path, bucket)
