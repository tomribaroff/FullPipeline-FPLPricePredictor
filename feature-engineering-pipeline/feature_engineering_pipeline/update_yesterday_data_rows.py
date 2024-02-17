def update_yesterday_data_rows_align(yesterday_df, today_df):
    # compare the ids from both datasets -> where a new player appears today, make sure you add that row to yesterday with nulls filling it
    #                                    -> where a player is removed today, make sure you remove that row yesterday 
    
    # Get the set of row identifiers from yesterday and today
    yesterday_ids = set(yesterday_df.player_ids)
    today_ids = set(today_df.player_ids)

    # Find new rows added today
    new_rows = today_ids - yesterday_ids

    # Add new rows with null values to yesterday's dataframe
    if new_rows:
        new_rows_data = today_df[today_df.player_ids.isin(new_rows)]
        yesterday_df = pandas.concat([yesterday_df, new_rows_data], ignore_index=True)

    # Find rows removed today
    removed_rows = yesterday_ids - today_ids

    # Remove rows from yesterday's dataframe
    if removed_rows:
        yesterday_df = yesterday_df[~yesterday_df.player_ids.isin(removed_rows)]
        
    # rename index
    today_df.index.rename('ids', inplace=True)
    yesterday_df.index.rename('ids', inplace=True)

    # sort values
    yesterday_df = yesterday_df.sort_values(by='player_ids')
    today_df = today_df.sort_values(by='player_ids')

    # reset indexes
    today_df.set_index('player_ids', inplace=True)
    yesterday_df.set_index('player_ids', inplace=True)

    return yesterday_df, today_df
