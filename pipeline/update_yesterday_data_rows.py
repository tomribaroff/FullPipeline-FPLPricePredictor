def update_yesterday_data_rows(yesterday_df, today_df, id_column):
    # compare the ids from both datasets -> where a new player appears today, make sure you add that row to yesterday with nulls filling it
    #                                    -> where a player is removed today, make sure you remove that row yesterday 
    
    # Get the set of row identifiers from yesterday and today
    yesterday_ids = set(yesterday_df[id_column])
    today_ids = set(today_df[id_column])

    # Find new rows added today
    new_rows = today_ids - yesterday_ids

    # Add new rows with null values to yesterday's dataframe
    if new_rows:
        new_rows_data = today_df[today_df[id_column].isin(new_rows)]
        yesterday_df = pd.concat([yesterday_df, new_rows_data], ignore_index=True)

    # Find rows removed today
    removed_rows = yesterday_ids - today_ids

    # Remove rows from yesterday's dataframe
    if removed_rows:
        yesterday_df = yesterday_df[~yesterday_df[id_column].isin(removed_rows)]

    return yesterday_df