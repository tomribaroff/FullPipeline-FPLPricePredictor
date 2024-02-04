
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
    feature_descriptions = [
        {
            "name": "datetime_gmt",
            "description": """
                            Datetime interval in GMT when the data was observed.
                            """,
            "validation_rules": "Always full hours, i.e. minutes are 00",
        },
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