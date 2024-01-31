from gcloud import storage
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def save_file_to_bucket(input_file_path, bucket_file_path, bucket_name):

    creds = os.getenv('JSON_SA_BATCH_PREDICTION_PATH')

    print(creds)

    with open(creds) as json_file:
        data = json.load(json_file)
    
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(data)

    client = storage.Client(credentials=credentials, project='high-producer-412815')

    bucket = client.get_bucket(bucket_name)

    # Create a blob in the bucket
    blob = bucket.blob(bucket_file_path)

    # Upload the contents of the CSV file to the blob
    with open(input_file_path, 'rb') as csv_file:
        blob.upload_from_filename(input_file_path) #the opposite function is download_to_filename

    #TODO UPLOAD THE CONTENTS OF THAT DAYS JSON FILE PULLED FROM THE API IN ITS RAW FORM TOO

input_file_path = Path('./Pipeline-Steps/Saved_DataFrames/2024-01-31/2024-01-31.csv') #TODO make sure these dates change dynamically 
bucket_file_path = '2024-01-31/2024-01-31.csv' #TODO make sure these dates change dynamically 
bucket = 'batch_prediction_store_bucket'
save_file_to_bucket(input_file_path, bucket_file_path,'batch_prediction_store_bucket')

#TODO WRITE FUNCTION THAT DOES THE OPPOSITE, IN ANOTHER FILE OR RENAME THIS FILE TO BUCKET_UTILITIES_FUNCTION