import pyomo.environ as pyo
from conf import Config, Logger
from pyomo.opt import SolverStatus, TerminationCondition


class ModelSolver(object):

    def __init__(self, model) -> None:
        self._logger = Logger().logger
        self.model = model
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
            self._logger.debug("[ModelSolver] Solver starting...")
            results = opt.solve(self.model, tee=True)
            self._logger.info("[ModelSolver] Solver completed.")
        except Exception as e:
            raise Exception(f"Model optimisation failed with {solver} with error message {e}.")

        if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
            self._logger.info("Solution is feasible and optimal")
            results.write()
        elif results.solver.termination_condition == TerminationCondition.infeasible:
            raise ValueError("Model optimisation resulted into an infeasible solution")

        self.model.optimised = True


if __name__ == "__main__":
    # TODO: write main method
    test = ModelSolver()
    print(test)
