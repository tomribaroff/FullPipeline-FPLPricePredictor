from gcloud import storage
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
from importlib.metadata import version

def save_item_to_bucket(input_file_path, bucket, name):

    with open('Pipeline-Steps/high-producer-412815-3b916fb32033.json') as json_file:
        data = json.load(json_file)
    
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(data)

    client = storage.Client(credentials=credentials, project='high-producer-412815')

    bucket = client.get_bucket(bucket)
    print(version('construct'))
    blobs = client.list_blobs(batch_prediction_store_bucket)
    #blob = bucket.blob(input_file_path)
    #blob.upload_from_string(name) 
    # Note: The call returns a response only when the iterator is consumed.
    for blob in blobs:
        print(blob.name)

save_item_to_bucket('Dockerfile', 'batch_prediction_store_bucket','myDockerPracticeFile')



