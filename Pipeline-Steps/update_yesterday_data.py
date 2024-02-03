def update_yesterday_data():
    #update yesterday's dataframe with today's results 

    #get yesterday's saved results 
    yesterday_filepath = Path('/Users/thomasribaroff/Documents/GitHub/FullPipeline-FPLPricePredictor/Pipeline-Steps/Saved_DataFrames/{}/{}.csv'.format(yesterday,yesterday))
    yesterday_data = pandas.read_csv(yesterday_filepath,index_col=['player_ids'])

    #ensure rows align, accounting for players being added/removed overnight
    yesterday_data = update_yesterday_data_rows(yesterday_data, today_data, 'player_ids')

    #updates 
    yesterday_data.price_change_this_night = today_data.player_prices_today - yesterday_data.player_prices_today
    yesterday_data.net_transfers_in_out_since_yesterday = today_data.net_transfers_in_out_overall_as_of_today - yesterday_data.net_transfers_in_out_overall_as_of_today

    # Update net transfer since last price change in today's data (including reset rule if price change occured overnight)
    today_data.net_transfers_in_out_since_last_price_change = yesterday_data.net_transfers_in_out_since_last_price_change + yesterday_data.net_transfers_in_out_since_yesterday
    boolean_player_changes = [today_data.price_change_this_night != 0]
    today_data.net_transfers_in_out_since_last_price_change = [0 if b else a for a, b in zip(today_data.net_transfers_in_out_since_last_price_change, boolean_player_changes[0])]

    #rewrite yesterday's file 
    yesterday_data.to_csv(yesterday_filepath) 

    return yesterday_data