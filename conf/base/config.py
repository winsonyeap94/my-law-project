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
    MLFLOW = dict(
        TRACKING_URI="./mlruns/",  # Location where mlflow artifacts will be stored, can also be AWS S3 or Azure Bucket
        EXPERIMENT_NAME="Experiment-1",
        TEMP_ARTIFACT_DIR="./tmp/",  # Temporary directory for storing artifacts, will be automatically deleted
    )

    # ================================================================================
    # Optimisation Model Configurations by Solver Types
    # ================================================================================
    OPTIMISATION_MODEL_CONFIG = dict(
        
        SOLVER_TYPE='cbc',

        SOLVER_OPTION=dict(
            cbc={
                'ratioGap': 0.01,
                'nodeStrategy': 'hybrid',
                'seconds': 600,
            }
        ),        
    )

    # ================================================================================
    # High-Level Optimisation Scenario Settings
    # ================================================================================
    OPTIMISATION_SCENARIO = {
        '1': '100% Demand Coverage',
        '2': 'Maximise Profit', 
    }

    SELECTED_OPTIMISATION_SCENARIO = 1

    # Additional Objective Functions
    ADD_DESPATCHER_HIRING_COST = False
    ADD_DELIVERY_COST = False

    # Additional Constraints
    ADD_DELIVERY_TIME_CONSTRAINT = False

    # ================================================================================
    # Optimisation Parameters
    # ================================================================================
    OPT_PARAMS = dict(
        total_demand=1_000_000, 
        delivery_speed=60,  # km/h
        cost_of_delivery=3,  # RM/h
        despatch_hiring_cost=2000,  # RM/month
        despatch_volume_limit=20,
        station_storage_as_warehouse=0,  # TODO: Proportion of station (sqft) to be used as warehouse storage
        warehouse_storage_height=3,  # for calculation of warehouse volume = warehouse area * storage height
        working_hours_per_day=12,
        profit_per_sales_volume=10,  # RM/ft3
        maximum_delivery_hrs_constraint=3,
    )
