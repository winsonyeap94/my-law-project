import json
from conf import Config
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

# ================================================================================
# Example JSON Inputs to be displayed on Swagger docs UI
# ================================================================================
EXAMPLE_JSON = {
    'OptimisationModelInput': {
        "optimisation_scenario": Config.SELECTED_OPTIMISATION_SCENARIO,
        "add_delivery_time_constraint": Config.ADD_DELIVERY_TIME_CONSTRAINT,
        "add_despatcher_hiring_cost": Config.ADD_DESPATCHER_HIRING_COST,
        "add_delivery_cost": Config.ADD_DELIVERY_COST,
        "despatch_hiring_cost": Config.OPT_PARAMS['despatch_hiring_cost'],
        "delivery_speed": Config.OPT_PARAMS['delivery_speed'],
        "despatch_volume_limit": Config.OPT_PARAMS['despatch_volume_limit'],
        "cost_of_delivery": Config.OPT_PARAMS['cost_of_delivery'],
        "working_hours_per_day": Config.OPT_PARAMS['working_hours_per_day'],
        "maximum_delivery_hrs_constraint": Config.OPT_PARAMS['maximum_delivery_hrs_constraint'],
        "profit_per_sales_volume": Config.OPT_PARAMS['profit_per_sales_volume']
    }
}


# ================================================================================
# OPTIMISATION INPUTS
# ================================================================================
class OptimisationModelInput(BaseModel):
    """Optimisation input parameters"""

    optimisation_scenario: Optional[int] = Config.SELECTED_OPTIMISATION_SCENARIO
    add_delivery_time_constraint: Optional[bool] = Config.ADD_DELIVERY_TIME_CONSTRAINT
    add_despatcher_hiring_cost: Optional[bool] = Config.ADD_DESPATCHER_HIRING_COST
    add_delivery_cost: Optional[bool] = Config.ADD_DELIVERY_COST
    despatch_hiring_cost: Optional[float] = Config.OPT_PARAMS['despatch_hiring_cost']
    delivery_speed: Optional[float] = Config.OPT_PARAMS['delivery_speed']
    despatch_volume_limit: Optional[float] = Config.OPT_PARAMS['despatch_volume_limit']
    cost_of_delivery: Optional[float] = Config.OPT_PARAMS['cost_of_delivery']
    working_hours_per_day: Optional[float] = Config.OPT_PARAMS['working_hours_per_day']
    maximum_delivery_hrs_constraint: Optional[float] = Config.OPT_PARAMS['maximum_delivery_hrs_constraint']
    profit_per_sales_volume: Optional[float] = Config.OPT_PARAMS['profit_per_sales_volume']

