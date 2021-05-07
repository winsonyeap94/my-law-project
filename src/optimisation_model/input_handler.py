"""
INPUT HANDLER CLASS

This class serves as the main data getter class.
All data loading should come from this class to ensure standardised and structured data loading across scripts.
"""

import pandas as pd
from conf import Config
from pathlib import Path
from src.data_connectors import PandasFileConnector

pd.set_option("max.columns", 20)
pd.set_option("display.width", 2000)


class InputHandler:
    
    @classmethod
    def get_districts_data(cls):
        data_df = PandasFileConnector.load(
            Path(Config.FILES["MODEL_INPUT_DATA"], "districts_df.csv")
        )
        return data_df

    @classmethod
    def get_warehouse_options(cls):
        
        data_df = PandasFileConnector.load(
            Path(Config.FILES["MODEL_INPUT_DATA"], "Warehouse Options.xlsx")
        )
        return data_df


