def overwrite_yesterdays_csv(yesterday_csv_updated, bucket_file_path, bucket_name):
    """
    Deletes existing file for yesterday's data, and then uploads the updated copy to a Google Cloud Storage bucket.

    Parameters:
    - local_file_path (str): Local path of the file to be uploaded.
    - bucket_file_path (str): Path to the destination file within the Google Cloud Storage bucket.
    - bucket_name (str): Name of the Google Cloud Storage bucket.

    Returns:
    - None
    """

    # Load service account credentials from JSON file
    creds = os.getenv('JSON_SA_RAW_DATA_PATH')
    credentials = service_account.Credentials.from_service_account_file(creds)

    # Create a Google Cloud Storage client with the provided credentials
    client = storage.Client(credentials=credentials)

    # Get the specified bucket
    bucket = client.get_bucket(bucket_name)

    # Get the blob (file) from the bucket with the same name, if it exists
    blob = bucket.blob(bucket_file_path)

    # Delete the existing file (if it exists)
    blob.delete()

    # Upload the new file
    blob.upload_from_string(yesterday_csv_updated, content_type='text/csv')