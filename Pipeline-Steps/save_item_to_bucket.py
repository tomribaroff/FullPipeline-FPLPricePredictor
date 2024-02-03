from gcloud import storage
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
import date


def save_file_to_bucket(input_file_path_csv, input_file_path_json, bucket_file_path, bucket_name):

    load_dotenv()
    creds = os.getenv('JSON_SA_BATCH_PREDICTION_PATH')
    gcp_project_id = os.getenv('GCP_PROJECT_ID')

    with open(creds) as json_file:
        data = json.load(json_file)
    
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(data)

    client = storage.Client(credentials=credentials, project=gcp_project_id)

    bucket = client.get_bucket(bucket_name)

    # Create a blob in the bucket
    blob = bucket.blob(bucket_file_path)

    # Upload the contents of the CSV file to the blob
    with open(input_file_path_csv, 'rb') as csv_file:
        blob.upload_from_filename(input_file_path_csv) #the opposite function is download_to_filename

    # Upload the contents of the json file to the blob
    with open(input_file_path_json, 'rb') as json_file:
        blob.upload_from_filename(input_file_path_json) #the opposite function is download_to_filename

# Get today's date
today = date.today() 

input_file_path_csv = Path('./Pipeline-Steps/Saved_Data/{}/{}.csv'.format(today,today)) 
input_file_path_json = Path('./Pipeline-Steps/Saved_Data/{}/{}.json'.format(today,today)') 
#bucket_file_path = '2024-01-31/2024-01-31.csv' #TODO make sure these dates change dynamically 
bucket_file_path = today
bucket = 'batch_prediction_store_bucket'
save_file_to_bucket(input_file_path_csv, input_file_path_json, bucket_file_path, bucket)

