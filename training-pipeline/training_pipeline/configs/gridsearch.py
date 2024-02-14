# NOTE: In a production environment, we would move this to a YAML file and load it from there.
#       Also, we would use random or bayesian search + early stopping to speed up the process

sweep_configs = {
    "method": "grid",
    "metric": {"name": "multi_logloss", "goal": "minimize"},  # Using multi_logloss for multi-class classification
    "parameters": {
        "n_jobs": {"values": [-1]},  # Set the number of jobs for parallel processing
        "n_estimators": {"values": [100, 200, 300]},  # Number of boosting rounds
        "learning_rate": {"values": [0.05, 0.1, 0.15]},  # Step size shrinkage to prevent overfitting
        "max_depth": {"values": [5, 10, 15]},  # Maximum depth of the tree
        "reg_lambda": {"values": [0, 0.01, 0.1]},  # L2 regularization term on weights
    },
}
