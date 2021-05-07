
from src.optimisation_model.preprocessing import Preprocessing
from src.optimisation_model.model import OptimisationModel
from src.optimisation_model.solver import ModelSolver
from src.optimisation_model.postprocessing import Postprocessing
from conf import Logger

_logger = Logger().logger

def main():
    """
    This function represents the main entry-point function,
    which does the processing, creates the optimsiation model,
    and does the post-processing.
    """
    # process the data using Preprocessing class
    _logger.debug("[MainPreprocessing] initiated...")
    processData = Preprocessing()
    _logger.debug("[MainPreprocessing] completed successfully.")

    # build the optimisation model, where objectives and constraints are defined.
    _logger.debug("[OptimisationModel] initiated...")
    model_builder = OptimisationModel(processData)
    # get the created model
    opt_model = model_builder.model
    #solver the optimisation model
    ModelSolver(opt_model)
    _logger.debug("[OptimisationModel] completed successfully.")

    # post-processing of the solved model
    _logger.debug("[PostProcessing] initiated...")
    postprocess_output = Postprocessing(opt_model, processData)
    _logger.debug("[PostProcessing] completed successfully.")

    return postprocess_output

if __name__ == "__main__":
    main()
    