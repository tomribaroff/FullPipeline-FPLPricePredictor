from typing import Dict, List
import pandas as pd

def preprocess_data(json_file: Dict) -> Tuple[pd.DataFrame, pd.DataFrame, int]:
    """
    Extracts information from a JSON file and returns two DataFrames and a total player count.

    Parameters:
    - json_file (Dict): A dictionary containing 'events', 'elements', and 'total_players'.

    Returns:
    - pd.DataFrame: DataFrame containing overall events data.
    - pd.DataFrame: DataFrame containing today's player data.
    - int: Total number of players.
    """
    
    overall_events_data = pd.DataFrame(json_file['events'])
    todays_player_data = pd.DataFrame(json_file['elements'])
    total_players = int(json_file['total_players'])

    return overall_events_data, todays_player_data, total_players
