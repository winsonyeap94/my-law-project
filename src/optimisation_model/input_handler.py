"""
INPUT HANDLER CLASS

This class serves as the main data getter class.
All data loading should come from this class to ensure standardised and structured data loading across scripts.
"""

import pandas as pd
from src.data_connectors import PandasFileConnector

pd.set_option("max.columns", 20)
pd.set_option("display.width", 2000)


class InputHandler:
    
    @classmethod
    def get_data_technicians(cls):

        data_df = PandasFileConnector.load(
            "./data/01_raw/technicians.csv",
            file_type='csv'
        )
        return data_df

    @classmethod
    def get_data_locations(cls):

        data_df = PandasFileConnector.load(
            "./data/01_raw/locations.csv",
            file_type='csv'
        )
        return data_df

    @classmethod
    def get_data_customers(cls):

        data_df = PandasFileConnector.load(
            "./data/01_raw/customers.csv",
            file_type='csv'
        )
        return data_df

