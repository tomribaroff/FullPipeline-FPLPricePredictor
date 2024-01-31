from google.cloud import storage
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
import pandas as pd

def save_item_to_bucket(input_file_path, input_file, bucket):

    with open('Pipeline-Steps/high-producer-412815-3b916fb32033.json') as json_file:
        data = json.load(json_file)
    
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(data)

    client = storage.Client(credentials=credentials, project='high-producer-412815')

    bucket = client.get_bucket(bucket)
    blob = bucket.blob(input_file_path)
    blob.upload_from_string(name) 

input_file_path = 'Saved_DataFrames/2024-01-30/2024-01-30.csv'
input_file = pd.read_csv('Saved_DataFrames/2024-01-30/2024-01-30.csv')
bucket = batch_prediction_store_bucket
save_item_to_bucket(input_file_path, input_file,'batch_prediction_store_bucket')

    # Create a blob in the bucket
    blob = bucket.blob(destination_blob_name)

    # Upload the contents of the CSV file to the blob
    with open(input_file_path, 'rb') as csv_file:
        blob.upload_from_file(input_file, content_type='application/octet-stream')


def save_item_from_bucket(file_name, bucket):

    with open('Pipeline-Steps/high-producer-412815-3b916fb32033.json') as json_file:
        data = json.load(json_file)
    
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(data)

    client = storage.Client(credentials=credentials, project='high-producer-412815')

    bucket = client.get_bucket(bucket)
    blob = bucket.blob(file_name)
    blob.download_as_text() 