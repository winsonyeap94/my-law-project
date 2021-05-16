import pyomo.environ as pyo
from conf import Config, Logger
from haversine import haversine
from src.optimisation_model.preprocessing import Preprocessing


class OptimisationModel(object):
    """
    This class defines the optimisation model objectives
    and its associated constraints.
    """
    
    def __init__(self, processed_data: Preprocessing):
        self._logger = Logger().logger
        self.processed_data = processed_data
        self.model = pyo.ConcreteModel()
        self.model.optimised = False
        self.__build_model()
        
    def __build_model(self):
        self._logger.debug("[OptimisationModel] Defining model indices and sets initiated...")

        # ================================================================================
        # Defining sets
        # ================================================================================
        self.model.W = pyo.Set(initialize=[w.name for w in self.processed_data.warehouse_list])
        self.model.T = pyo.Set(initialize=[t.name for t in self.processed_data.township_list])
        self._logger.info("[OptimisationModel] Defining model indices and sets completed successfully.")

        # ================================================================================
        # Defining parameters
        # ================================================================================
        self._logger.debug("[OptimisationModel] Defining model parameters initiated...")
        
        # Warehouse Parameters
        self.model.w_latitude = pyo.Param(self.model.W, initialize={w.name: w.latitude for w in self.processed_data.warehouse_list}, domain=pyo.Any)
        self.model.w_longitude = pyo.Param(self.model.W, initialize={w.name: w.longitude for w in self.processed_data.warehouse_list}, domain=pyo.Any)        
        self.model.w_volume = pyo.Param(self.model.W, initialize={w.name: w.capacity for w in self.processed_data.warehouse_list}, domain=pyo.Any)
        self.model.w_cost = pyo.Param(self.model.W, initialize={w.name: w.monthly_cost for w in self.processed_data.warehouse_list}, domain=pyo.Any)
        
        # Township parameters
        self.model.t_latitude = pyo.Param(self.model.T, initialize={t.name: t.latitude for t in self.processed_data.township_list}, domain=pyo.Any)
        self.model.t_longitude = pyo.Param(self.model.T, initialize={t.name: t.longitude for t in self.processed_data.township_list}, domain=pyo.Any)
        self.model.t_demand = pyo.Param(self.model.T, initialize={t.name: t.demand for t in self.processed_data.township_list}, domain=pyo.Any)

        # Warehouse-Township distances
        self.model.w_t_distance = pyo.Param(
            self.model.W, self.model.T,
            initialize={
                (w.name, t.name): max(0.001, haversine((w.latitude, w.longitude), (t.latitude, t.longitude)))
                for t in self.processed_data.township_list
                for w in self.processed_data.warehouse_list
            },
            domain=pyo.Any
        )

        self._logger.info("[OptimisationModel] Defining model parameters completed successfully.")

        # ================================================================================
        # Defining decision variables
        # ================================================================================
        self._logger.debug("[OptimisationModel] Defining model decision variables initiated...")
        
        # Warehouse location selection
        self.model.x = pyo.Var(self.model.W, domain=pyo.Binary)  # TODO: Do I still need this?

        # Warehouse-township assignment
        self.model.x_assign = pyo.Var(self.model.W, self.model.T, domain=pyo.NonNegativeReals)
        
        # Number of despatchers assigned to township t from warehouse w
        self.model.n_despatchers = pyo.Var(self.model.W, self.model.T, domain=pyo.NonNegativeIntegers)

        # Volume supply to township
        self.model.t_supply = pyo.Var(self.model.T, domain=pyo.NonNegativeReals)

        self._logger.info("[OptimisationModel] Defining model decision variables completed successfully.")
        
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

        # Warehouse selection constraint
        self.model.warehouse_selection_constraint = pyo.ConstraintList()
        self.__warehouse_selection_constraint()

        # Warehouse supply constraint
        self.model.warehouse_supply_constraint = pyo.ConstraintList()
        self.__warehouse_supply_constraint()

        # Township demand fulfillment
        self.model.township_demand_fulfillment_constraint = pyo.ConstraintList()
        self.__township_demand_fulfillment_constraint()

        # Number of despatchers required to serve each warehouse-township assignment
        self.model.despatcher_requirement_constraint = pyo.ConstraintList()
        self.__despatcher_requirement_constraint()

        # Delivery speed constraint
        if Config.ADD_DELIVERY_TIME_CONSTRAINT:
            self.model.delivery_time_constraint = pyo.ConstraintList()
            self.__delivery_time_constraint()

        self._logger.info("[OptimisationModel] Defining model constraint function completed successfully.")
    
    @staticmethod
    def objective(model):
        
        monthly_warehouse_cost = 0
        monthly_despatcher_hiring_cost = 0
        monthly_delivery_travel_cost = 0
        sales_revenue = 0  # TODO

        # Warehouse Costs
        for w in model.W:
            monthly_warehouse_cost += model.x[w] * model.w_cost[w]
        total_cost = monthly_warehouse_cost

        # Despatcher hiring costs
        if Config.ADD_DESPATCHER_HIRING_COST:
            for w in model.W:
                for t in model.T:
                    monthly_despatcher_hiring_cost += \
                        model.n_despatchers[w, t] * Config.OPT_PARAMS['despatch_hiring_cost']
            total_cost += monthly_despatcher_hiring_cost

        # Delivery/travelling cost
        if Config.ADD_DELIVERY_COST:
            for w in model.W:
                for t in model.T:
                    # Time to complete a delivery (to-and-fro)
                    time_per_delivery = (model.w_t_distance[w, t] / Config.OPT_PARAMS['delivery_speed']) * 2
                    # Delivery trips required
                    n_delivery_trips = model.x_assign[w, t] / Config.OPT_PARAMS['despatch_volume_limit']
                    # Total cost of delivery
                    monthly_delivery_travel_cost += \
                        n_delivery_trips * time_per_delivery * Config.OPT_PARAMS['cost_of_delivery']
            total_cost += monthly_delivery_travel_cost

        return total_cost
            
    @property
    def optimisation_model(self):
        return self.model

    def __warehouse_selection_constraint(self):
        """
        Warehouse selection constraint to apply fixed monthly cost if any supply is provided from a warehouse.
        """
        for w in self.model.W:
            self.model.warehouse_selection_constraint.add(
                pyo.quicksum(self.model.x_assign[w, t] for t in self.model.T) <= 9_999_999 * self.model.x[w]
            )

    def __warehouse_supply_constraint(self):
        """
        Warehouse supply to townships must not exceed warehouse's capacity (volume).
        """
        for w in self.model.W:
            self.model.warehouse_supply_constraint.add(
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

    def __despatcher_requirement_constraint(self):
        """
        Constraint to determine number of despatchers required for each warehouse-township assignment.
        """
        for w in self.model.W:
            for t in self.model.T:
                # Time to complete a delivery (to-and-fro)
                time_per_delivery = (self.model.w_t_distance[w, t] / Config.OPT_PARAMS['delivery_speed']) * 2
                # Frequency of deliveries in a month
                monthly_delivery_freq = 30 * Config.OPT_PARAMS['working_hours_per_day'] / time_per_delivery
                # Minimum required despatchers
                min_required_despatchers = \
                    self.model.x_assign[w, t] / (Config.OPT_PARAMS['despatch_volume_limit'] * monthly_delivery_freq)
                # Constraint
                self.model.despatcher_requirement_constraint.add(
                    self.model.n_despatchers[w, t] >= min_required_despatchers
                )

    def __delivery_time_constraint(self):
        """
        All deliveries should be completed within the time constraint given.
        """
        for w in self.model.W:
            for t in self.model.T:
                self.model.delivery_time_constraint.add(
                    (self.model.w_t_distance[w, t] / Config.OPT_PARAMS['delivery_speed']) * self.model.x[w] <=
                    Config.OPT_PARAMS['maximum_delivery_hrs_constraint']
                )
