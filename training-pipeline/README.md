# Training Pipeline

The training pipeline pulls training data from the Hopswork feature store, and trains models using W&B runs. It can perform hyperparameter tuning, using a set of configurations (see ***) for the LightGBM model we use to model the data. It evaluates the test set of the best model found after hyperparameter tuning. It also creates a baseline model, which always predicts no price change, as a comparison point for our metrics. 

After training and evaluating it uploads the model artifacts to the W&B and Hopsworks model registries, for use in the batch prediction pipeline. 
