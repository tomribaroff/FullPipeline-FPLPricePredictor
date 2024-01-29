
def estimate_active_players(api_dict: dict) -> int:
    """
    Estimate total Active players in the game at this point in time

       Args:
        api_dict = Dictionary created from fetch_data_from_api.extract_current_data_from_api_overall()
    """

    r_all_players_today = api_dict.copy()

    # find current gameweek from dict
    current_event = [item for item, condition in zip(r_all_players_today['events'], boolean_list_of_all_events_status) if condition]
    current_gameweek = current_event[0].get('id')

    # Rename columns
    total_active_players_estimate = int(round(r_all_players_today['total_players']*(0.97)**current_gameweek,))

    return total_active_players_estimate

def calculate_net_transfers_overall(api_dict: dict) -> numpy.array:
    """
    Calculate total net transfer of each player this season at this moment in time

       Args:
        api_dict = Dictionary created from fetch_data_from_api.extract_current_data_from_api_overall()
    """

    r_all_players_today = api_dict.copy()

    # Calculate total net transfers in for each player
    all_players_transfers_in = list(map(operator.itemgetter('transfers_in'), r_all_players_today['elements']))

    # Calculate total net transfers out for each player
    all_players_transfers_out = list(map(operator.itemgetter('transfers_out'), r_all_players_today['elements']))

    # Calculate total net transfers for each player
    net_transfers_overall_today = numpy.array(all_players_transfers_in) - numpy.array(all_players_transfers_out)

    return net_transfers_overall_today

def extract_all_players_prices_now(api_dict: dict) -> list:
    """
    Extract current price of each player at this moment in time

       Args:
        api_dict = Dictionary created from fetch_data_from_api.extract_current_data_from_api_overall()
    """

    r_all_players_today = api_dict.copy()

    # Extract players prices from dict
    all_players_prices_today = list(map(operator.itemgetter('now_cost'), r_all_players_today['elements']))

    return all_players_prices_today

def extract_all_players_price_changes_this_event(api_dict: dict) -> list:
    """
    Extract how much each play has changed price so far this event

       Args:
        api_dict = Dictionary created from fetch_data_from_api.extract_current_data_from_api_overall()
    """

    r_all_players_today = api_dict.copy()

    # Extract players prices from dict
    all_players_price_change_for_current_event = list(map(operator.itemgetter('cost_change_event'), r_all_players_today['elements']))

    return all_players_price_change_for_current_event


def extract_all_players_injured(api_dict: dict) -> list:
    """
    Extract boolean list of all players which is True if they are injured and False otherwise

       Args:
        api_dict = Dictionary created from fetch_data_from_api.extract_current_data_from_api_overall()
    """

    r_all_players_today = api_dict.copy()

    # Extract which players are currently injured
    list_of_all_players_status = list(map(operator.itemgetter('status'), r_all_players_today['elements']))
    boolean_list_of_players_injured = [True if x == 'i' else False for x in list_of_all_players_status] 

    return boolean_list_of_players_injured