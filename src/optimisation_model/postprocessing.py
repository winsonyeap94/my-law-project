import json
import pandas as pd
from pathlib import Path
import pyomo.environ as aml
from conf import Config, Logger
from src.data_connectors import PandasFileConnector


class Postprocessing:
    
    def __init__(self, model, solver_results, processed_data, export=False):
        self._logger = Logger().logger
        self.model = model
        self.solver_results = solver_results
        self.processed_data = processed_data
        self.warehouse_selection_data = self.__warehouse_selection_data()
        self.warehouse_township_assignment_data = self.__warehouse_township_assignment_data()

        # Exporting results
        if export:
            self._logger.debug("[Data Export] initiated...")
            PandasFileConnector.save(self.warehouse_selection_data, 
                                     Path(Config.FILES['MODEL_OUTPUT'], "Warehouse Selection.csv"))
            PandasFileConnector.save(self.warehouse_township_assignment_data, 
                                     Path(Config.FILES['MODEL_OUTPUT'], "Warehouse Township Assignment.csv"))
            self._logger.debug("[Data Export] completed successfully.")

    def __warehouse_selection_data(self):
        self._logger.debug("[PostProcessing] Warehouses' assignment detail is as such:")
        warehouse_data = pd.DataFrame()
        for w in self.model.W:
            append_row = pd.DataFrame({
                'Name': w,
                'Selected': True if self.model.x[w]() == 1 else False,
            }, index=[0])
            warehouse_data = pd.concat([warehouse_data, append_row], axis=0)
            self._logger.debug(f"--> Warehouse: {append_row['Name'].values[0]} | Selected: {append_row['Selected'].values[0]}")
        return warehouse_data

    def __warehouse_township_assignment_data(self):
        warehouse_assignment_data = {}
        for w in self.model.W:
            single_warehouse_dict = {}
            for t in self.model.T:
                single_warehouse_dict[t] = self.model.x_assign[w, t]()
            warehouse_assignment_data[w] = single_warehouse_dict
        warehouse_assignment_data = pd.DataFrame(warehouse_assignment_data)
        return warehouse_assignment_data

