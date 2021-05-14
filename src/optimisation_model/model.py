import pyomo.environ as pyo
from conf import Config, Logger
from src.optimisation_model.preprocessing import Preprocessing


class OptimisationModel(object):
    """
    This class defines the optimisation model objectives
    and its associated costraints.
    """
    
    def __init__(self, processed_data: Preprocessing):
        self._logger = Logger().logger
        self.processed_data = processed_data
        self.model = pyo.ConcreteModel()
        self.model.optimised = False
        self.__build_model()
        
    def __build_model(self):
        self._logger.debug("[OptimisationModel] Defining model indicies and sets initiated...")

        # ================================================================================
        # Defining sets
        # ================================================================================
        self.model.W = pyo.Set(initialize=[k.name for k in self.processed_data.warehouse_list])
        self.model.T = pyo.Set(initialize=[c.name for c in self.processed_data.township_list])
        self._logger.info("[OptimisationModel] Defining model indicies and sets completed successfully.")

        # ================================================================================
        # Defining parameters
        # ================================================================================
        self._logger.debug("[OptimisationModel] Defining model parameters initiated...")
        
        # Warehouse Parameters
        self.model.w_latitude = pyo.Param(self.model.W, initialize={w.name: w.latitude for w in self.processed_data.warehouse_list}, domain=pyo.Any)
        self.model.w_longitude = pyo.Param(self.model.W, initialize={w.name: w.longitude for w in self.processed_data.warehouse_list}, domain=pyo.Any)        
        self.model.w_volume = pyo.Param(self.model.W, initialize={
            w.name: w.area * Config.OPT_PARAMS['warehouse_storage_height'] for w in self.processed_data.warehouse_list
        }, domain=pyo.Any)
        self.model.w_cost = pyo.Param(self.model.W, initialize={w.name: w.monthly_cost for w in self.processed_data.warehouse_list}, domain=pyo.Any)
        
        # Township parameters
        self.model.t_latitude = pyo.Param(self.model.T, initialize={t.name: t.latitude for t in self.processed_data.township_list}, domain=pyo.Any)
        self.model.t_longitude = pyo.Param(self.model.T, initialize={t.name: t.longitude for t in self.processed_data.township_list}, domain=pyo.Any)
        self.model.t_demand = pyo.Param(self.model.T, initialize={t.name: t.demand for t in self.processed_data.township_list}, domain=pyo.Any)

        self._logger.info("[OptimisationModel] Defining model parameters completed successfully.")

        # self.model.cap = pyo.Param(self.model.K, initialize={k.name: k.cap for k in self.processed_data.technician_list}, domain=pyo.Any)
        # self.model.location = pyo.Param(self.model.C, initialize={j.name: j.loc for j in self.processed_data.customer_list}, domain=pyo.Any)
        # self.model.depot = pyo.Param(self.model.K, initialize={k.name: k.depot for k in self.processed_data.technician_list}, domain=pyo.Any)
        # self.model.canCover = pyo.Param(self.model.C, initialize={j.name: [k.name for k in j.job.coveredBy] for j in self.processed_data.customer_list}, domain=pyo.Any)
        # self.model.dur = pyo.Param(self.model.C, initialize= {j.name: j.job.duration for j in self.processed_data.customer_list}, domain=pyo.Any)
        # self.model.tstart = pyo.Param(self.model.C, initialize={j.name: j.tStart for j in self.processed_data.customer_list}, domain=pyo.Any)
        # self.model.tend = pyo.Param(self.model.C, initialize={j.name : j.tEnd for j in self.processed_data.customer_list}, domain=pyo.Any)
        # self.model.tDue = pyo.Param(self.model.C, initialize={j.name : j.tDue for j in self.processed_data.customer_list}, domain=pyo.Any)
        # self.model.priority = pyo.Param(self.model.C, initialize={j.name : j.job.priority for j in self.processed_data.customer_list}, domain=pyo.Any)
        
        # ================================================================================
        # Defining decision variables
        # ================================================================================
        self._logger.debug("[OptimisationModel] Defining model decision variables initiated...")
        
        # Warehouse location selection
        self.model.x = pyo.Var(self.model.W, domain=pyo.Binary)  # TODO: Do I still need this?
        
        # Warehouse-township assignment
        self.model.x_assign = pyo.Var(self.model.W, self.model.T, domain=pyo.Binary)
        
        # TODO: Number of despatchers assigned to township t from warehouse w

        # Volume supply to township
        self.model.t_supply = pyo.Var(self.model.T, domain=pyo.PositiveReals)

        self._logger.info("[OptimisationModel] Defining model decision variables completed successfully.")
        
        # # Customer-technician assignment
        # self.model.x = pyo.Var(self.model.C, self.model.K, domain=pyo.Binary)
        # # Technician assignment
        # self.model.u = pyo.Var(self.model.K,  domain=pyo.Binary)
        # # Edge-route assignment to technician
        # self.model.y = pyo.Var(self.model.L, self.model.L, self.model.K, domain=pyo.Binary)
        # # start time of service
        # self.model.t = pyo.Var(self.model.L, domain = pyo.PositiveReals)
        # # Lateness of service
        # self.model.z = pyo.Var(self.model.C, domain = pyo.PositiveReals)
        # # Artificial variables to correct time window upper and lower limits
        # self.model.xa = pyo.Var(self.model.C, domain = pyo.PositiveReals)
        # self.model.xb = pyo.Var(self.model.C, domain = pyo.PositiveReals)
        # # Unfilled jobs
        # self.model.g = pyo.Var(self.model.C, domain= pyo.Binary)
        
        # ================================================================================
        # Defining objective function
        # ================================================================================
        self._logger.debug("[OptimisationModel] Defining model objective function initiated...")
        self.model.obj = pyo.Objective(rule=self.objective, sense=pyo.minimize)
        self._logger.info("[OptimisationModel] Defining model objective function completed successfully.")

        # set Constraints
        self.__add_constraints()
        
    def __add_constraints(self):
        self._logger.info("[OptimisationModel] Defining model constraint function initiated...")

        # Warehouse supply constraint
        self.model.warehouse_supply_constraint = pyo.ConstraintList()
        self.__warehouse_supply_constraint()

        # Township demand fulfillment
        self.model.township_demand_fulfillment_constraint = pyo.ConstraintList()
        self.__township_demand_fulfillment_constraint()
        
        self._logger.info("[OptimisationModel] Defining model constraint function completed successfully.")

        # # technician constraints
        # self.__technician_constraint()
        # # A technician must be assigned to a job, or a gap is declared (1)
        # self.model.technician_job = pyo.ConstraintList()
        # self.__technician_job()
        # # At most one technician can be assigned to a job
        # self.model.one_technician_constraint = pyo.ConstraintList()
        # self.__one_technician_constraint()
        # # Technician capacity constraints
        # self.model.technician_capacity = pyo.ConstraintList()
        # self.__technician_capacity()
        # # Technician tour constraints
        # self.model.technician_tour_constraint = pyo.ConstraintList()
        # self.__technician_tour_constraint()
        # # Same depot constraints 
        # self.model.same_depot_constraint = pyo.ConstraintList()
        # self.__same_depot_constraint()
        # # Temporal constraints for customer locations
        # self.model.temporal_customer_constraint =  pyo.ConstraintList()
        # self.__temporal_customer_constraint()
        # # Temporal constraints for depot locations
        # self.model.temporal_depot_constraint =  pyo.ConstraintList()
        # self.__temporal_depot_constraint()
        # # Time window constraints
        # self.model.time_window_constraint =  pyo.ConstraintList()
        # self.__time_window_constraint()
        # # Lateness constraint
        # self.model.lateness_constraint =  pyo.ConstraintList()
        # self.__lateness_constraint()
    
    @staticmethod
    def objective(model):
        
        monthly_warehouse_cost = 0
        monthly_despatcher_hiring_cost = 0  # TODO
        monthly_despatcher_travel_cost = 0  # TODO
        sales_revenue = 0  # TODO
        for w in model.W:
            monthly_warehouse_cost += model.W[w] * model.w_cost[w]
            
        return monthly_warehouse_cost
            
    @property
    def optimisation_model(self):
        return self.model

    def __warehouse_supply_constraint(self):
        """
        Warehouse supply to townships must not exceed warehouse's capacity (volume).
        """
        for w in self.model.W:
            self.model.township_demand_fulfillment_constraint.add(
                pyo.quicksum(self.model.x_assign[w, t] for t in self.model.T) <= self.model.w_volume[w]
            )

    def __township_demand_fulfillment_constraint(self):
        """
        All township demands must be fulfilled.
        """
        for t in self.model.T:
            self.model.township_demand_fulfillment_constraint.add(
                pyo.quicksum(self.model.x_assign[w, t] for w in self.model.W) >= self.model.t_demand[t]
            )
    
    def __technician_constraint(self):
        """
        Technician cannot leave or return to a depot that is not its base
        """
        for k in  self.processed_data.technician_list:
            for d in self.model.D:
                if k.depot != d:
                    for i in self.model.L:
                        self.model.y[i,d,k.name].fix(0)
                        self.model.y[d,i,k.name].fix(0)
                        
    def __technician_job(self):
        """
        A technician must be assigned to a job, or a gap is declared.
        """
        for j in self.model.C:
            self.model.technician_job.add(pyo.quicksum(self.model.x[j,k] 
                                                       for k in self.model.canCover[j]) +  self.model.g[j] == 1)
    
    def __one_technician_constraint(self):
        """
        At most one technician can be assigned to a job
        """
        for j in self.model.C:
            exp = pyo.quicksum(self.model.x[j,k] for k in self.model.K)
            self.model.one_technician_constraint.add(exp <= 1)
            
    def __technician_capacity(self):
        """
        Technician capacity constraints
        """

        self.model.capLHS = {k : pyo.quicksum(self.model.dur[j]*self.model.x[j,k] for j in self.model.C) +\
                pyo.quicksum(self.processed_data.dist[i,j]*self.model.y[i,j,k] for i in self.model.L for j in self.model.L) for k in self.model.K}
        for k in self.model.K:
            self.model.technician_capacity.add(self.model.capLHS[k] <= self.model.cap[k]*self.model.u[k])

    
    def __technician_tour_constraint(self):
        """
        Technician tour constraints.
        """
        for j in self.model.C:
            for k in self.model.K:
                exp1 = pyo.quicksum(self.model.y[l,self.model.location[j], k] for l in self.model.L)
                exp2 = pyo.quicksum(self.model.y[self.model.location[j],l, k] for l in self.model.L)
                self.model.technician_tour_constraint.add(exp1 == self.model.x[j,k])
                self.model.technician_tour_constraint.add(exp2 == self.model.x[j,k])
    
    def __same_depot_constraint(self):
        """
        Same depot constraints 
        """
        for k in self.model.K:
            exp1 = pyo.quicksum(self.model.y[j, self.model.depot[k], k] for j in self.model.J)
            exp2 = pyo.quicksum(self.model.y[self.model.depot[k],j, k] for j in self.model.J)
            self.model.same_depot_constraint.add(exp1 == self.model.u[k])
            self.model.same_depot_constraint.add(exp2 == self.model.u[k])
            
    def __temporal_customer_constraint(self):
        """
        Temporal constraints for depot locations
        """
        for j in self.model.C:
            for i in self.model.C:
                M = 600 + self.model.dur[i] + self.processed_data.dist[self.model.location[i],self.model.location[j]]
                exp = self.model.t[self.model.location[i]] + self.model.dur[i] + \
                    self.processed_data.dist[self.model.location[i], self.model.location[j]] - \
                        M*(1 - pyo.quicksum(self.model.y[self.model.location[i], self.model.location[j], k] for k in self.model.K))
                self.model.temporal_customer_constraint.add(self.model.t[self.model.location[j]] >= exp)
    
    def __temporal_depot_constraint(self):
        """
        Temporal constraints for depot locations
        """
        for j in self.model.C:
            for i in self.model.D:
                M = 600 + self.processed_data.dist[i, self.model.location[j]]
                exp = self.model.t[i] + self.processed_data.dist[i, self.model.location[j]] - \
                        M*(1 - pyo.quicksum(self.model.y[i, self.model.location[j], k] for k in self.model.K))
                self.model.temporal_depot_constraint.add(self.model.t[self.model.location[j]] >= exp)
        
    def __time_window_constraint(self):
        """
        Time window constraints
        """
        for j in self.model.C:
            self.model.time_window_constraint.add(self.model.t[self.model.location[j]] + self.model.xa[j] >= self.model.tstart[j])
            self.model.time_window_constraint.add(self.model.t[self.model.location[j]] - self.model.xb[j] <= self.model.tend[j])
            
    def __lateness_constraint(self):
        """
        Lateness constraint
        """
        for j in self.model.C:
            self.model.lateness_constraint.add(self.model.z[j] >= self.model.t[self.model.location[j]] + self.model.dur[j] \
                - self.model.tDue[j])
        