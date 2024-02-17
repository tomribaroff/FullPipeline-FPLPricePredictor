from update_yesterday_data_rows import update_yesterday_data_rows_align

def update_yesterday_data_values(yesterday_df, today_df):

    yesterday_data, today_data = update_yesterday_data_rows_align(yesterday_data, today_data)

    # #updates 
    yesterday_data.price_change_this_night = today_data.player_prices_today - yesterday_data.player_prices_today
    today_data.net_transfers_in_out_this_day = today_data.net_transfers_in_out_overall_as_of_today - yesterday_data.net_transfers_in_out_overall_as_of_today
    today_data.net_transfers_in_out_since_last_price_change = yesterday_data.net_transfers_in_out_since_last_price_change

    # Update net transfer since last price change in today's data 
    yesterday_data.net_transfers_in_out_since_last_price_change = yesterday_data.net_transfers_in_out_since_last_price_change + yesterday_data.net_transfers_in_out_this_day

    #reset rule if price changed overnight 
    boolean_player_changes = numpy.squeeze(yesterday_data.price_change_this_night != 0)
    today_data.net_transfers_in_out_since_last_price_change = [today_data.net_transfers_in_out_this_day[i] if boolean_player_changes[i] else today_data.net_transfers_in_out_since_last_price_change[i] for i in today_data.net_transfers_in_out_since_last_price_change.index]

    return yesterday_df, today_df
