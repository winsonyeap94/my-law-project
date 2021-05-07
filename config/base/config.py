import os
from pathlib import Path
from collections import OrderedDict
from datetime import timedelta
import inspect


class Config(object):

    # ================================================================================
    # Project details & folders
    # ================================================================================
    NAME = dict(
        full="PyOpt Framework v0.0.1",
        short="PyOpt",
    )

    # File structure
    FILES = dict(
        RAW_DATA=Path('data', '01_raw'),
        INTERMEDIATE_DATA=Path('data', '02_intermediate'),
        PRIMARY_DATA=Path('data', '03_primary'),
        FEATURE_DATA=Path('data', '04_feature'),
        MODEL_INPUT_DATA=Path('data', '05_model_input'),
        MODELS_DATA=Path('data', '06_models'),
        MODEL_OUTPUT=Path('data', '07_model_output'),
        REPORTING=Path('data', '08_reporting'),
    )

    for file, file_path in FILES.items():
        Path(file_path).mkdir(parents=True, exist_ok=True)

    # ================================================================================
    # MLFlow Settings
    # For more information refer to: https://www.mlflow.org/docs/latest/python_api/mlflow.html#mlflow.set_tracking_uri
    # ================================================================================
    # TODO
    MLFLOW = dict(
        TRACKING_URI="./mlruns/",  # Location where mlflow artifacts will be stored, can also be AWS S3 or Azure Bucket
        EXPERIMENT_NAME="Experiment-1",
        # LOG_TRAINPIPELINE=True,  # Toggle between True/False to log at different levels
        LOG_MLTRAINER=True,  # Toggle between True/False to log at different levels
        LOG_MLPIPELINE=True,  # Toggle between True/False to log at different levels
        TEMP_ARTIFACT_DIR="./tmp/",  # Temporary directory for storing artifacts, will be automatically deleted
    )

    # ================================================================================
    # Variable List
    # List of variables with their names and units. This is to be recorded as part of documentation.
    # ================================================================================
    VARS = [
        dict(filename="technicians", filepath='./data/01_raw/technicians.csv'),
        dict(filename="locations", filepath='./data/01_raw/locations.csv'),
        dict(filename="customers", filepath='./data/01_raw/customers.csv')
    ]
        

    # ================================================================================
    # Optimisation Model Configurations by Solver Types
    # ================================================================================
    OPTIMISATION_MODELLING_CONFIG = dict(
        SOLVER_TYPE='cbc',

        SOLVER_OPTION=dict(
            cbc={
            'ratioGap': 0.01,
            'nodeStrategy': 'hybrid',
            'seconds': 600,
            }
        ),
    )
