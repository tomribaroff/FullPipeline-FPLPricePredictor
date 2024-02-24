import datetime
from io import StringIO
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from google.cloud import storage
from datetime import date
from dotenv import load_dotenv
import os
from google.oauth2 import service_account
import json 
import pandas as pd
import numpy as np

# TODO test the APIs using Postman 
# TODO deploy the APIs using Cloud Run and then put the given url into the streamlit app 

load_dotenv()

creds = os.getenv('JSON_SA_READ_WRITE_PATH')
gcp_project_id = os.getenv('GCP_PROJECT_ID')

app = FastAPI()

today = date.today()
yesterday = today - datetime.timedelta(1)

@app.get("/get_prediction")
async def get_prediction():
    
    gcp_bucket_name = os.getenv('GCP_BUCKET_NAME_PREDICTIONS')
    bucket_file_path = f"{today}.csv"

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

    # Filter results for just those who's price change we predict 
    df = df[df.predicted_price_change != 0] 

    prediction_result = {"players_predicted_to_change_price": df}

    return JSONResponse(content=prediction_result)


@app.get("/get_yesterday_results")
async def get_yesterday_results():

    gcp_bucket_name = os.getenv('GCP_BUCKET_NAME_STORE')
    bucket_file_path = f"{yesterday}/{yesterday}.csv"

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

    # Filter results for just those who's price change we predict 
    df = df[df.price_change_this_night != 0] 

    prediction_result = {"players_who_changed_price": df}

    return JSONResponse(content=prediction_result)
