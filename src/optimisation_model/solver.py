import pyomo.environ as pyo
from datetime import datetime
from conf import Config, Logger
from pyomo.opt import SolverStatus, TerminationCondition


class ModelSolver:

    def __init__(self, model) -> None:
        self._logger = Logger().logger
        self.model = model
        self.results = None
        self.__solve()

    def __solve(self) -> None:
        """
        optimization model solver function. The solver function has
        transformations, which detects fixed variables and detects trival 
        constraints in oder to remove them.
        """
        pyo.TransformationFactory("contrib.detect_fixed_vars").apply_to(self.model)  # type: ignore
        pyo.TransformationFactory("contrib.deactivate_trivial_constraints").apply_to(self.model)  # type: ignore

        # initialise the solver object
        self._logger.debug("[ModelSolver] Solver object initiated...")
        solver = Config.OPTIMISATION_MODEL_CONFIG['SOLVER_TYPE']
        opt = pyo.SolverFactory(solver)
        if Config.OPTIMISATION_MODEL_CONFIG['SOLVER_OPTION'].get(solver) is not None:
            for k, v in Config.OPTIMISATION_MODEL_CONFIG['SOLVER_OPTION'].get(solver).items():
                opt.options[k] = v

        try:
            start_time = datetime.now()
            self._logger.debug("[ModelSolver] Solver starting...")
            results = opt.solve(self.model, tee=True)
            self.results = results
            end_time = datetime.now()
            self._logger.info(f"[ModelSolver] Solver completed in {end_time - start_time}.")
        except Exception as e:
            raise Exception(f"Model optimisation failed with {solver} with error message {e}.")

        if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
            self._logger.info("Solution is feasible and optimal")
            results.write()
        elif results.solver.termination_condition == TerminationCondition.infeasible:
            raise ValueError("Model optimisation resulted into an infeasible solution")

        self.model.optimised = True


if __name__ == "__main__":
    
    test = ModelSolver()
    print(test)
