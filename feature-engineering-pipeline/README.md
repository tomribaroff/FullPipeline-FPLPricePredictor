The feature engineering pipeline follows the following steps:

Extract data from the API as a JSON <br>
↓ <br>
Transform JSON into CSVs
↓
Save JSON and CSVs to a GCP bucket (our raw data storage)
↓
Update yesterday's CSV with new information from today's CSV (ie today's data will inform us if prices changed overnight)
↓
Update today's CSV with context of yesterday's CSV (ie today's net transfers is calculated using the difference of today's overall transfers to date and yesterday's overall transfers to date)
↓
Overwrite and save yesterday and today's CSVs to GCP bucket
↓
Upload yesterday's complete CSV to Hopswork (our feature store) 
