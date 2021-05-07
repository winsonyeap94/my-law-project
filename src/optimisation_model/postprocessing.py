import pyomo.environ as aml
from config import Logger
import json

class Postprocessing(object):
    
    def __init__(self, model, processed_data):
        self._logger = Logger().logger
        self.model = model
        self.processed_data = processed_data
        self.__assignment_data()
        self.__technicians_data()
        self.__utilization_data()
        
    def __assignment_data(self):
        self._logger.debug("[PostProcessing] Technicians' assignment detail is as such...")
        for j in self.processed_data.customer_list:
            if self.model.g[j.name]() > 0.5:
                jobStr = f"Nobody assigned to {j.name} ({j.job.name}) in {j.loc}"
            else:
                for k in self.model.K:
                    if self.model.x[j.name, k]() > 0.5:
                        jobStr = f"{k} assigned to {j.name} ({j.job.name}) in {j.loc}. Start at t= {self.model.t[j.loc]()}."
                    if self.model.z[j.name]() > 1e-6:
                        jobStr += f" {self.model.z[j.name]()} minutes late."
                    if self.model.xa[j.name]() > 1e-6:
                        jobStr += f" Start time corrected by {self.model.xa[j.name]()} minutes."
                    if self.model.xb[j.name]() > 1e-6:
                        jobStr += f" End time corrected by {self.model.xb[j.name]()} minutes."
            self._logger.info(f"[PostProcessing] {jobStr}")
    
    def __technicians_data(self):
        self._logger.debug(" ")
        self._logger.debug("[PostProcessing] Technicians' assigned route is as such...")
        for k in self.processed_data.technician_list:
            if self.model.u[k.name]() > 0.5:
                cur = k.depot
                route = k.depot
                while True:
                    for j in self.processed_data.customer_list:
                        if self.model.y[cur,j.loc,k.name]() > 0.5:
                            route += f" -> {self.model.location[j.name]} (dist={self.processed_data.dist[cur, self.model.location[j.name]]}, t={self.model.t[self.model.location[j.name]]}, proc={self.model.dur[j.name]})"
                            cur = self.model.location[j.name]
                    for i in self.model.D:
                        if self.model.y[cur,i,k.name]() > 0.5:
                            route += " -> {} (dist={})".format(i, self.processed_data.dist[cur,i])
                            cur = i
                            break
                    if cur == k.depot:
                        break
                self._logger.info(f"[PostProcessing] {k.name}'s route: {route}")
            else:
                self._logger.info(f"[PostProcessing] {k.name} is not used")

    def __utilization_data(self):
        self._logger.debug(" ")
        self._logger.debug("[PostProcessing] Technicians' individual utilization rate and total utilization rate is as such...")
        for k in self.model.K:
            used = aml.value(self.model.capLHS[k])
            total = self.model.cap[k]
            util = used/total if total > 0 else 0
            self._logger.info(f"[PostProcessing] {k}'s utilization is {round(util, 2)} ({used}/{total})")
            #print(f"{k}'s utilization is {round(util, 2)} ({used}/{total})")
        totUsed = sum(aml.value(self.model.capLHS[k]) for k in self.model.K)
        totCap = sum(self.model.cap[k] for k in self.model.K)
        totUtil = totUsed / totCap if totCap > 0 else 0
        self._logger.info(f"[PostProcessing] Total technician utilization is {round(totUtil, 2)} ({round(totUsed, 2)}/{round(totCap, 2)})")
