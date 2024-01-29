
#access the apis

def extract_current_data_from_api_overall(
) -> Optional[Dict]:
    """
    Extract data from the Fantasy Football Data API that contains data on all player transfers 

    IMPORTANT NOTE: a Complete Guide to the API’s that Fantasy Football offers can be found here:
https://www.game-change.co.uk/2023/02/10/a-complete-guide-to-the-fantasy-premier-league-fpl-api/

    Args:
        None Required

    Returns:
          A dictionary of extracted data
    """
    base_url = 'https://fantasy.premierleague.com/api/'
    r_all_players_today = requests.get(base_url+'bootstrap-static/').json()

    return r_all_players_today