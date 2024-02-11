
def to_feature_store(
    data: pd.DataFrame,
    validation_expectation_suite: ExpectationSuite,
    feature_group_version: int,
) -> FeatureGroup:
    """
    This function takes in a pandas DataFrame and a validation expectation suite,
    performs validation on the data using the suite, and then saves the data to a
    feature store in the feature store.
    """

    # Connect to feature store.
    project = hopsworks.login(
        api_key_value=SETTINGS["FS_API_KEY"], project="fplpredictpipeline"
    )
    feature_store = project.get_feature_store()

    # Create feature group.
    energy_feature_group = feature_store.get_or_create_feature_group(
        name="fpl_player_prices",
        version=feature_group_version,
        description="FPL player transfer data",
        event_time="datetime_gmt",
        online_enabled=False,
        expectation_suite=validation_expectation_suite,
    )
    # Upload data.
    energy_feature_group.insert(
        features=data,
        overwrite=False,
        write_options={
            "wait_for_job": True,
        },
    )

    # Add feature descriptions.
        "price_change_this_night": numpy.nan, #currently unknown
        "net_transfers_in_out_since_last_price_change": 0, #currently unknown
        "net_transfers_in_out_since_yesterday": 0, #currently unknown
        "price_change_so_far_for_this_event ": all_players_price_change_for_current_event,
        "total_active_players_estimate": total_active_players_estimate,
        "players_injured": boolean_list_of_players_injured,
        "player_prices_today" : all_players_prices_today,
        "net_transfers_in_out_overall_as_of_today" : net_transfers_overall_today, 
        "player_ids" : todays_player_data.id

    feature_descriptions = [
        {
            "name": "price_change_this_night",
            "description": """
                            Overnight price changes that will occur for this dataset. Price changes happen approximately 6 hours after this data is pulled from API. 
                            """,
            "validation_rules": "+1, -1 or 0",
        },

        {
            "name": "net_transfers_in_out_since_last_price_change",
            "description": """
                            Cumulative sum of transfer that occur since the last price change for this player. 
                            It is calculated as an interative sum of "net_transfers_in_out_since_yesterday", unless a price change occurs, in which case it resets to just "net_transfers_in_out_since_yesterday"
                            """,
            "validation_rules": "Always integer values",
        },

        {
            "name": "net_transfers_in_out_since_yesterday",
            "description": """
                            Daily net transfers that occured for each player. 
                            """,
            "validation_rules": "Always integer values",
        },

        {
            "name": "price_change_so_far_for_this_event",
            "description": """
                            Overall price change that has occured for each player during this gameweek (event). 
                            """,
            "validation_rules": "Must be integer values between 3 and -3 (including 3 and -3)",
        },

        {
            "name": "total_active_players_estimate",
            "description": """
                            Estimate of the number of active players still in the game. 
                            """,
            "validation_rules": "Integer value less than Total Players and above zero",
        },

        {
            "name": "players_injured",
            "description": """
                            Boolean list of player injury status
                            """,
            "validation_rules": "True for injured players, False for all else",
        },

        {
            "name": "net_transfers_in_out_overall_as_of_today",
            "description": """
                            Overall transfers for each player since the start of the game. Not to be used for modelling, but is used to calculate daily values. 
                            """,
            "validation_rules": "Always integer values",
        },

        {
            "name": "player_ids",
            "description": """
                            ID number for each player, to help align rows when comparing yesterday and today's data 
                            """,
            "validation_rules": "Always positive integer values"
        }
    ]

    for description in feature_descriptions:
        energy_feature_group.update_feature_description(
            description["name"], description["description"]
        )

    # Update statistics.
    energy_feature_group.statistics_config = {
        "enabled": True,
        "histograms": True,
        "correlations": True,
    }
    energy_feature_group.update_statistics_config()
    energy_feature_group.compute_statistics()

    return energy_feature_group