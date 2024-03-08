import datetime
from io import StringIO
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from google.cloud import storage
from datetime import date
from dotenv.main import load_dotenv
import os
from google.oauth2 import service_account
import json 
import pandas as pd
import numpy as np


load_dotenv(override=True)

creds = os.getenv('JSON_SA_READ_WRITE_PATH')
gcp_project_id = os.getenv('GCP_PROJECT_ID')

app = FastAPI()

today = date.today()
yesterday = today - datetime.timedelta(1)

@app.get("/get_prediction")
async def get_prediction():
    
    gcp_bucket_name = os.getenv('GCP_BUCKET_NAME_PREDICTIONS')
    #bucket_file_path = f"{today}.csv"
    bucket_file_path = "2024-02-23.csv"

    # Load service account credentials from JSON file
    with open(creds) as json_file:
        data = json.load(json_file)

    # Create service account credentials from JSON keyfile
    credentials = service_account.Credentials.from_service_account_info(data)

    # Create a Google Cloud Storage client with the provided credentials and project ID
    client = storage.Client(credentials=credentials, project=gcp_project_id)

    # Get the specified bucket
    bucket = client.get_bucket(gcp_bucket_name)

    # Get the blob (CSV file) from the bucket
    blob = bucket.blob(bucket_file_path)

    # Download the contents of the blob as a string
    csv_content = blob.download_as_text()

    # Create a Pandas DataFrame from the CSV content
    df = pd.read_csv(StringIO(csv_content))

    # Encode dataframe as json
    json_data = df.to_json()

    # Return 
    return JSONResponse(content=json_data)


@app.get("/get_yesterday_results")
async def get_yesterday_results():

    gcp_bucket_name = os.getenv('GCP_BUCKET_NAME_STORE')
    #bucket_file_path = f"{yesterday}/{yesterday}.csv"
    bucket_file_path = "2024-02-23/2024-02-23.csv"

    # Load service account credentials from JSON file
    with open(creds) as json_file:
        data = json.load(json_file)

    # Create service account credentials from JSON keyfile
    credentials = service_account.Credentials.from_service_account_info(data)

    # Create a Google Cloud Storage client with the provided credentials and project ID
    client = storage.Client(credentials=credentials, project=gcp_project_id)

    # Get the specified bucket
    bucket = client.get_bucket(gcp_bucket_name)

    # Get the blob (CSV file) from the bucket
    blob = bucket.blob(bucket_file_path)

    # Download the contents of the blob as a string
    csv_content = blob.download_as_text()

    # Create a Pandas DataFrame from the CSV content
    df = pd.read_csv(StringIO(csv_content))

    # Encode dataframe as json
    json_data = df.to_json()

    # Return 
    return JSONResponse(content=json_data)
