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

def extract_current_data_from_api_personal(
        team_id: int = 3402291
        current_gameweek: int = 1) -> Optional[Dict]:
    """
    Extract data from the Fantasy Football Data API that contains data on all player transfers 

    IMPORTANT NOTE: a Complete Guide to the API’s that Fantasy Football offers can be found here:
https://www.game-change.co.uk/2023/02/10/a-complete-guide-to-the-fantasy-premier-league-fpl-api/

    Args:
        team_number: the number that represents your team. It can be found in the url of the website, when you navigate to the points tab of your own team. For example, when I navigated to the points tab after logging into FF, my url was https://fantasy.premierleague.com/entry/3402291/event/21 and my team number was 3402291

    Returns:
          A dictionary of extracted data
    """
    r_my_team = requests.get(base_url+'entry/{}/event/{}/picks/'.format(team_id,current_gameweek)).json()

    return r_my_team