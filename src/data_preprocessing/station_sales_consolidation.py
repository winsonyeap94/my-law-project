import pandas as pd
import geopy.distance
from pathlib import Path
from src.data_connectors import PandasFileConnector


class DataPreprocessor:

    EXPORT_DIR = {
        "raw": "./data/01_raw",
        "intermediate": "./data/02_intermediate",
        "primary": "./data/03_primary",
        "feature": "./data/04_feature",
        "model_input": "./data/05_model_input",
    }

    def __init__(self):
        pass

    @classmethod
    def get_station_sales(cls):
        data_df = PandasFileConnector.load(Path(cls.EXPORT_DIR['raw'], "dmr_final_forecast_central.csv"))
        data_df['sales'] = pd.to_numeric(data_df['sales'], errors='coerce')
        data_df = data_df.groupby(['id', 'product', 'region'])['sales'].mean().reset_index(drop=False)
        data_df = data_df.pivot(index=['region', 'id'], columns='product', values='sales').reset_index(drop=False)
        sales_colnames = [str(x) for x in data_df.columns if x not in ['region', 'id']]
        data_df = data_df.rename(columns={int(x): 'Sales_' + x for x in sales_colnames})
        data_df['Total Sales'] = data_df[['Sales_' + x for x in sales_colnames]].sum(axis=1)
        return data_df

    @classmethod
    def get_station_list(cls):
        data_df = PandasFileConnector.load(Path(cls.EXPORT_DIR['raw'], "STATION LIST_GPS_DS.xlsx"), skiprows=3)
        data_df = data_df.drop("Unnamed: 0", axis=1)
        return data_df

    @classmethod
    def get_district_coords(cls):
        data_df = PandasFileConnector.load(Path(cls.EXPORT_DIR['raw'], "Klang Valley Districts.xlsx"))
        data_df['Latitude'] = data_df['Latitude'].str.replace("° N", "").astype(float)
        data_df['Longitude'] = data_df['Longitude'].str.replace("° E", "").astype(float)
        return data_df

    @classmethod
    def merge_data(cls):
        
        # Merging station list and sales
        station_list_df = cls.get_station_list()
        station_sales_df = cls.get_station_sales()
        station_merged_df = station_list_df.merge(station_sales_df, how='inner', left_on="Fuel Acc", right_on="id")

        # Associating each station to the closest district
        districts_df = cls.get_district_coords()

        # Assigning closest district
        station_merged_df['Assigned Township'] = station_merged_df.apply(
            lambda x: cls.assign_closest_township(x['Latitude'], x['Longitude'], districts_df), axis=1
        )

        # Exporting data
        PandasFileConnector.save(station_merged_df, Path(cls.EXPORT_DIR['intermediate'], "station_merged_df.csv"))

        # Summarising by township
        station_summary_df = station_merged_df.groupby(['Assigned Township'])['Total Sales'].sum()
        districts_df = districts_df.merge(station_summary_df, how='left', left_on='Township', 
                                          right_on='Assigned Township')

        # Removing townships with no sales
        districts_df = districts_df.loc[districts_df['Total Sales'] > 0, :].copy()

        # Calculating relative proportions
        districts_df['Proportion Sales'] = districts_df['Total Sales'] / districts_df['Total Sales'].sum()

        # Exporting data
        PandasFileConnector.save(districts_df, Path(cls.EXPORT_DIR['model_input'], "districts_df.csv"))


    @classmethod
    def assign_closest_township(cls, lat, long, districts_df):
        temp_districts_df = districts_df.copy()
        temp_districts_df['Station Latitude'] = lat
        temp_districts_df['Station Longitude'] = long
        temp_districts_df['Distance'] = temp_districts_df.apply(
            lambda x: cls.calc_distance(
                (x['Latitude'], x['Longitude']), (x['Station Latitude'], x['Station Longitude'])
            ), axis=1
        )
        closest_township = temp_districts_df.sort_values('Distance', ascending=True)['Township'].values[0]
        return closest_township

    @staticmethod
    def calc_distance(coords_1, coords_2):
        return geopy.distance.distance(coords_1, coords_2)
        

if __name__ == "__main__":
    
    DataPreprocessor.merge_data()
    