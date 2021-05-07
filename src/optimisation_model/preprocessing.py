from conf import Config, Logger
import sys
from collections import defaultdict
import pandas as pd
from typing import List, Dict
from src.optimisation_model.input_handler import InputHandler


class Technician():
    def __init__(self, name:str, cap:int, depot:int):
        self.name = name
        self.cap = cap
        self.depot = depot

    def __str__(self):
        return f"Technician: {self.name}\n  Capacity: {self.cap}\n  Depot: {self.depot}"
    
class Job():
    def __init__(self, name:str, priority:float, duration:float, coveredBy:List[Technician]):
        self.name = name
        self.priority = priority
        self.duration = duration
        self.coveredBy = coveredBy

    def __str__(self):
        about = f"Job: {self.name}\n  Priority: {self.priority}\n  Duration: {self.duration}\n  Covered by: "
        about += ", ".join(t.name for t in self.coveredBy)
        return about
    
class Customer():
    def __init__(self, name:str, loc:str, job:int, tStart:float, tEnd:float, tDue:float):
        self.name = name
        self.loc = loc
        self.job = job
        self.tStart = tStart
        self.tEnd = tEnd
        self.tDue = tDue

    def __str__(self):
        coveredBy = ", ".join(t.name for t in self.job.coveredBy)
        return f"Customer: {self.name}\n  Location: {self.loc}\n  Job: {self.job.name}\n  Priority: {self.job.priority}\n  Duration: {self.job.duration}\n  Covered by: {coveredBy}\n  Start time: {self.tStart}\n  End time: {self.tEnd}\n  Due time: {self.tDue}"


class Preprocessing(object):
    """
    This class is intended to pre-process the data,
    such that it can be ingested by the optimisation 
    model class.
    """
    
    def __init__(self):
        self._logger = Logger().logger
        self.technician_list: List[Technician] = []
        self.customer_list: List[Customer] = []
        self.job_list: List[Job] = []
        self.dist:Dict = None
        self.technician_dataset:str = "technicians"
        self.locations_dataset:str = "locations"
        self.customers_dataset:str = "customers"
        self.__process_technicians()
        self.__process_jobs()
        self.__process_location()
        self.__process_customer()
        
        
    def __process_technicians(self):
        """
        This function processes the technician dataset
        and save the data into the technician list.
        """
        df_technician = InputHandler.get_data_technicians()
        df_technician = df_technician.iloc[2:,:]
        for _, row in df_technician.iterrows():
            thisTech = Technician(*row.iloc[:3])
            self.technician_list.append(thisTech)
        self._logger.debug(f"[DataProcessing] Processed data for {self.technician_dataset}.")
            
    def __process_jobs(self):
        """
        This function processes the technician dataset
        and save the job details into the job list.
        """
        df_technician = InputHandler.get_data_technicians()
        # get Jobs covered by the technician
        for j, col in enumerate(df_technician.iloc[:,3:]):
            coveredBy = [t for i,t in enumerate(self.technician_list) if df_technician.iloc[2+i,3+j] == 1]
            # Create Job object
            jobdata = [col, df_technician.iloc[0,3+j], df_technician.iloc[1,3+j]]
            thisJob = Job(*jobdata, coveredBy)
            self.job_list.append(thisJob)
        self._logger.debug(f"[DataProcessing] Processed data for {self.technician_dataset}.")
    
    def __process_location(self):
        """
        This function processes the location dataset
        and save the location duration into the location list.
        """
        df_location = InputHandler.get_data_locations()
        locations = df_location.iloc[:, 1:]
        self.dist = {(l, l) : 0 for l in locations}
        for i,l1 in enumerate(locations):
            for j,l2 in enumerate(locations):
                if i < j:
                    self.dist[l1,l2] = locations.iloc[i, j]
                    self.dist[l2,l1] = self.dist[l1,l2]
        self._logger.debug(f"[DataProcessing] Processed data for {self.locations_dataset}.")
                    
    def __process_customer(self):
        """
        This function processes the customer dataset
        and save the customer details into the customer list.
        """
        df_customer = InputHandler.get_data_customers()
        for i in range(len(df_customer)):
            for b in self.job_list:
                if b.name == df_customer.iloc[i, 2]:
                    # Create Customer object using corresponding Job object
                    rowVals = df_customer.iloc[i,:]
                    thisCustomer = Customer(*rowVals.iloc[:2], b, *rowVals.iloc[3:])
                    self.customer_list.append(thisCustomer)
        self._logger.debug(f"[DataProcessing] Processed data for {self.customers_dataset}.")
    
    @property
    def customer_data(self):
        return self.customer_list
    
    @property
    def technician_data(self):
        return self.technician_list
    
    @property
    def distance(self):
        return self.dist
        

if __name__ == "__main__":
    Preprocessing()
        
        
        
    