import sys
import pandas as pd
from typing import List, Dict
from conf import Config, Logger
from collections import defaultdict
from src.optimisation_model.input_handler import InputHandler


class Warehouse:
    def __init__(self, name: str, latitude: float, longitude: float, area: float, capacity: float,
                 monthly_price_per_sqft: float, monthly_cost: float):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.area = area
        self.capacity = capacity
        self.monthly_price_per_sqft = monthly_price_per_sqft
        self.monthly_cost = monthly_cost

    def __str__(self):
        return f"Warehouse {self.name} --> Lat/Long: ({self.latitude:.3f}, {self.longitude:.3f}) | "\
               f"Capacity: {self.capacity:.2f} | Area: {self.area:.2f} sqft | Cost: RM{self.monthly_cost:.0f}/month"


class Township:
    def __init__(self, name: str, district: str, latitude: float, longitude: float, demand: float):
        self.name = name
        self.district = district
        self.latitude = latitude
        self.longitude = longitude
        self.demand = demand

    def __str__(self):
        return f"Township {self.name} ({self.district})--> Lat/Long: ({self.latitude:.3f}, {self.longitude:.3f}) | "\
               f"Demand: {self.demand:.0f}"


class Preprocessing:
    """
    This class is intended to pre-process the data,
    such that it can be ingested by the optimisation 
    model class.
    """
    
    def __init__(self):
        self._logger = Logger().logger
        self.warehouse_list: List[Warehouse] = []
        self.township_list: List[Township] = []
        self.__process_warehouses()
        self.__process_townships()

    def __process_warehouses(self):
        """
        This function processes the technician dataset
        and save the data into the technician list.
        """
        self._logger.debug("[Preprocessing] __process_warehouses() initiated.")

        # Loading warehouse data
        warehouses_df = InputHandler.get_warehouse_options()

        # Selecting required columns and appending them to self.warehouse_list
        for _, warehouse_row in warehouses_df.iterrows():
            thisWarehouse = Warehouse(name=warehouse_row['Warehouse Location'],
                                      latitude=warehouse_row['Latitude'],
                                      longitude=warehouse_row['Longitude'],
                                      area=warehouse_row['Area (sqft)'],
                                      capacity=warehouse_row['Capacity (ft3)'],
                                      monthly_price_per_sqft=warehouse_row['Price (RM/sqft/month)'],
                                      monthly_cost=warehouse_row['Cost (RM/month)'])
            self.warehouse_list.append(thisWarehouse)
            
        self._logger.debug("[Preprocessing] __process_warehouses() completed.")
            
    def __process_townships(self):
        """
        This function processes the technician dataset
        and save the job details into the job list.
        """
        self._logger.debug("[Preprocessing] __process_townships() initiated.")

        # Loading townships data
        townships_df = InputHandler.get_districts_data()
        
        # Selecting required columns and appending them to self.township_list
        for _, township_row in townships_df.iterrows():
            thisTownship = Township(name=township_row['Township'],
                                    district=township_row['District'],
                                    latitude=township_row['Latitude'],
                                    longitude=township_row['Longitude'],
                                    demand=township_row['Demand'])
            self.township_list.append(thisTownship)
        self._logger.debug("[Preprocessing] __process_townships() completed.")
    
    @property
    def warehouse_data(self):
        return self.warehouse_list
    
    @property
    def township_data(self):
        return self.township_list
        

if __name__ == "__main__":

    Preprocessing()
