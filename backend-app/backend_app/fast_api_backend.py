from fastapi import FastAPI
from fastapi.responses import JSONResponse
from google.cloud import storage
from datetime import date

# TODO test these APIs locally using POSTMAN

app = FastAPI()

@app.get("/get_prediction")
async def get_prediction(): # TODO test this locally with dummy data 
    # Replace 'your-gcp-bucket' and 'your-blob-path' with your GCP bucket and blob path
    bucket_name = "batch_prediction_store_bucket"
    today = date.today()
    blob_path = f"{today}/{today}.csv"

    # Download the image from the GCS bucket
    # TODO When pulling data from the bucket, you need to have a try catch, to handle any GCP external errors 
    client = storage.Client() # TODO you're going to need credentials here
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)
    content = blob.download_as_text()

    # 

    # Replace 'prediction_result' with the actual prediction result
    df = csv.reader(StringIO(content))
    df = df[df.predicted_price_change_this_night != 0] #TODO this line will need to change according to how the CSV is saved in the bucket and loaded from the bucket

    prediction_result = {"players_predicted_to_change_price": df}

    return JSONResponse(content=prediction_result)


@app.get("/get_yesterday_results")
async def get_yesterday_results():
    # Replace 'your-gcp-bucket' and 'your-blob-path' with your GCP bucket and blob path
    bucket_name = "raw_data_and_features_bucket"

    # Calculate yesterday's date
    yesterday_date = today - datetime.timedelta(days=1)
    
    # Specify the CSV file path in the GCS bucket
    blob_path = f"{yesterday_date}/{yesterday_date}.csv"

    # Download the CSV file from the GCS bucket
    client = storage.Client() # TODO you're going to need credentials here
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)
    content = blob.download_as_text()

    # Perform any additional data processing based on your CSV structure
    df = pd.read_csv(StringIO(content))
    df_filtered = df[df['price_change_this_night'] != 0]

    # Replace 'players_predicted_to_change_price' with the relevant data from your DataFrame
    result_data = {"players_predicted_to_change_price": df_filtered.to_dict(orient='records')}

    return JSONResponse(content=result_data)
