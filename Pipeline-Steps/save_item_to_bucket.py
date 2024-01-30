from gcloud import storage
from oauth2client.service_account import ServiceAccountCredentials
import os
import json

def save_item_to_bucket(input_file_path, bucket, name):

    with open('high-producer-412815-3b916fb32033.json') as json_file:
        data = json.load(json_file)
    
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(data)

    client = storage.Client(credentials=credentials, project='high-producer-412815')

    print(client, credentials)
    bucket = client.get_bucket(bucket)
    blob = bucket.blob(input_file_path)
    blob.upload_from_filename(name) 

save_item_to_bucket('Dockerfile', 'batch_prediction_store_bucket','myDockerPracticeFile')

