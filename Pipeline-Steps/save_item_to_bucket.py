from gcloud import storage
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
import pandas as pd
from pathlib import Path 

def save_item_to_bucket(input_file_path, bucket_file_path, bucket_name):

    with open('Pipeline-Steps/high-producer-412815-3b916fb32033.json') as json_file:
        data = json.load(json_file)
    
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(data)

    client = storage.Client(credentials=credentials, project='high-producer-412815')

    bucket = client.get_bucket(bucket_name)
    #blob = bucket.blob(input_file_path)
    #blob.upload_from_string(name) 
       
    # Create a blob in the bucket
    blob = bucket.blob(bucket_file_path)

    # Upload the contents of the CSV file to the blob
    with open(input_file_path, 'rb') as csv_file:
        blob.upload_from_filename(input_file_path) #the opposite function is download_to_filename

input_file_path = Path('./Pipeline-Steps/Saved_DataFrames/2024-01-31/2024-01-31.csv')
bucket_file_path = '2024-01-31/2024-01-31.csv'
bucket = 'batch_prediction_store_bucket'
save_item_to_bucket(input_file_path, bucket_file_path,'batch_prediction_store_bucket')