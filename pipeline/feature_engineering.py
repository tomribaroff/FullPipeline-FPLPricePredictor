import numpy as np
import pandas as pd

def estimate_active_players(overall_events_data: pd.DataFrame, total_players: int) -> int:
    """
    Estimate total active players in the game at this point in time.

    Args:
        overall_events_data (pd.DataFrame): DataFrame created from fetch_data_from_api.extract_current_data_from_api_overall().
        total_players (int): Integer value extracted from fetch_data_from_api.extract_current_data_from_api_overall().
    """
    # Total active players in the game at this point in time (estimate)
    current_gameweek = np.where(overall_events_data.is_current)[0][0] + 1
    total_active_players_estimate = int(round(total_players * (0.97) ** current_gameweek))
    return total_active_players_estimate

def calculate_net_transfers_overall(todays_player_data: pd.DataFrame) -> np.array:
    """
    Calculate total net transfer of each player this season at this moment in time.

    Args:
        todays_player_data (pd.DataFrame): DataFrame created from fetch_data_from_api.extract_current_data_from_api_overall().
    """
    # Net transfers of players at this moment in time
    net_transfers_overall_today = todays_player_data.transfers_in - todays_player_data.transfers_out
    return net_transfers_overall_today

def extract_all_players_prices_now(todays_player_data: pd.DataFrame) -> np.array:
    """
    Extract the current prices of players at this moment in time from the supplied DataFrame.

    Args:
        todays_player_data (pd.DataFrame): DataFrame created from fetch_data_from_api.extract_current_data_from_api_overall().
    """
    # Price Change so far this event
    all_players_prices_today = todays_player_data.now_cost
    return all_players_prices_today

def extract_all_players_price_changes_this_event(todays_player_data: pd.DataFrame) -> np.array:
    """
    Extract the changes of price for players during this event window from the supplied DataFrame.

    Args:
        todays_player_data (pd.DataFrame): DataFrame created from fetch_data_from_api.extract_current_data_from_api_overall().
    """
    # Extract players prices from dict
    # Price Change so far this event
    all_players_price_change_for_current_event = todays_player_data.cost_change_event
    return all_players_price_change_for_current_event

def extract_all_players_injured(todays_player_data: pd.DataFrame) -> np.array:
    """
    Extract a boolean list of all players which is True if they are injured and False otherwise.

    Args:
        todays_player_data (pd.DataFrame): DataFrame created from fetch_data_from_api.extract_current_data_from_api_overall().
    """
    # Player currently flagged red
    boolean_list_of_players_injured = [status == 'i' for status in todays_player_data.status]
    return boolean_list_of_players_injured
