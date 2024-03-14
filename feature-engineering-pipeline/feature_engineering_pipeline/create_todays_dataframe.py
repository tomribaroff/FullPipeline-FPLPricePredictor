import numpy as np
import pandas as pd
from feature_engineering_pipeline import feature_engineering

def create_todays_dataframe_from_raw_csvs(overall_events_data: pd.DataFrame,
                                         todays_player_data: pd.DataFrame,
                                         total_players: int) -> pd.DataFrame:
    # Create DataFrame from dictionary of all this transfer data
    # Player transfer data from the API is updated at least every 40 minutes, and probably every 15 - 30 mins. 

    all_players_price_change_for_current_event = feature_engineering.extract_all_players_price_changes_this_event(todays_player_data)
    total_active_players_estimate = feature_engineering.estimate_active_players(overall_events_data, total_players)
    boolean_list_of_players_injured = feature_engineering.extract_all_players_injured(todays_player_data)
    all_players_prices_today = feature_engineering.extract_all_players_prices_now(todays_player_data)
    net_transfers_overall_today = feature_engineering.calculate_net_transfers_overall(todays_player_data)



# Create DataFrame from dictionary of all this transfer data

    price_change_dict = {
    "price_change_this_night": np.nan, #tomorrow, we define this as today_data.player_prices_today - yesterday_data.player_prices_today
    "net_transfers_in_out_since_last_price_change": 0, #tomorrow, we define this as yesterday_data.net_transfers_in_out_since_last_price_change + today_data_net_transfers_in_out_since_yesterday, unless price change occurs, then we reset to ="Net Transfers In/Out since yesterday
    "net_transfers_in_out_this_day": 0, #tomorrow, we define this as today_data.net_transfers_in_out_overall_as_of_today - yesterday_data.net_transfers_in_out_overall_as_of_today
    "price_change_so_far_for_this_event ": all_players_price_change_for_current_event,
    "total_active_players_estimate": total_active_players_estimate,
    "players_injured": boolean_list_of_players_injured,
    "player_prices_today" : all_players_prices_today,
    "net_transfers_in_out_overall_as_of_today" : net_transfers_overall_today, #not to be used in modelling
    "player_ids" : todays_player_data.id,
    "player_name": todays_player_data.web_name
}

    # Dictionary into DataFrame
    today_data = pd.DataFrame(price_change_dict)

    return today_data