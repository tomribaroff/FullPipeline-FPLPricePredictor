from pipeline import feature_engineering

def create_todays_dataframe(overall_events_data: pd.DataFrame -> pd.DataFrame):
    # Create DataFrame from dictionary of all this transfer data
    # Player transfer data from the API is updated at least every 40 minutes, and probably every 15 - 30 mins. 

        all_players_price_change_for_current_event = feature_engineering.extract_all_players_price_changes_this_event(todays_player_data)
        total_active_players_estimate = feature_engineering.estimate_active_players(overall_events_data)
        boolean_list_of_players_injured = feature_engineering.extract_all_players_injured(todays_player_data)
        all_players_prices_today = feature_engineering.extract_all_players_prices_now(todays_player_data)
        net_transfers_overall_today = feature_engineering.calculate_net_transfers_overall(todays_player_data)


    price_change_dict = {
        "price_change_this_night": numpy.nan, #currently unknown
        "net_transfers_in_out_since_last_price_change": 0, #currently unknown
        "net_transfers_in_out_since_yesterday": 0, #currently unknown
        "price_change_so_far_for_this_event ": all_players_price_change_for_current_event,
        "total_active_players_estimate": total_active_players_estimate,
        "players_injured": boolean_list_of_players_injured,
        "player_prices_today" : all_players_prices_today,
        "net_transfers_in_out_overall_as_of_today" : net_transfers_overall_today, 
        "player_ids" : todays_player_data.id
    }

    # Turn dictionary into DataFrame
    today_data = pandas.DataFrame(price_change_dict)
    today_data.set_index("player_ids", inplace = True)

    return today_data



