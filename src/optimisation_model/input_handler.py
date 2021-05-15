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
        data_df['Proportion Sales'] = data_df['Proportion Sales'] / data_df['Proportion Sales'].sum()
        data_df = data_df.drop_duplicates(subset='Township', keep='first')
        data_df['Demand'] = data_df['Proportion Sales'] * Config.OPT_PARAMS['total_demand']
        return data_df

    @classmethod
    def get_warehouse_options(cls):
        
        data_df = PandasFileConnector.load(
            Path(Config.FILES["MODEL_INPUT_DATA"], "Warehouse Options.xlsx")
        )
        data_df['Capacity (ft3)'] = data_df['Area (sqft)'] * Config.OPT_PARAMS['warehouse_storage_height']
        return data_df


