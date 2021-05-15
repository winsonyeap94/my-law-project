from conf import Logger
from src.optimisation_model.preprocessing import Preprocessing
from src.optimisation_model.model import OptimisationModel
from src.optimisation_model.solver import ModelSolver
from src.optimisation_model.postprocessing import Postprocessing

_logger = Logger().logger


def main():
    """
    This function represents the main entry-point function,
    which does the processing, creates the optimisation model,
    and does the post-processing.
    """
    
    # process the data using Preprocessing class
    _logger.debug("[MainPreprocessing] initiated...")
    processed_data = Preprocessing()
    _logger.debug("[MainPreprocessing] completed successfully.")

    # build the optimisation model, where objectives and constraints are defined.
    _logger.debug("[OptimisationModel] initiated...")
    model_builder = OptimisationModel(processed_data)
    
    # get the created model
    opt_model = model_builder.model
    
    # solve the optimisation model
    ModelSolver(opt_model)
    _logger.debug("[OptimisationModel] completed successfully.")

    # post-processing of the solved model
    _logger.debug("[PostProcessing] initiated...")
    post_process_output = Postprocessing(opt_model, processed_data, export=True)
    _logger.debug("[PostProcessing] completed successfully.")

    return post_process_output


if __name__ == "__main__":

    opt_results = main()

    # ============================== VISUALISATION ==============================
    from src.viz import viz_warehouse_selection
    import plotly.io as pio
    pio.renderers.default = "browser"

    from src.optimisation_model.input_handler import InputHandler
    warehouses_df = InputHandler.get_warehouse_options()
    townships_df = InputHandler.get_districts_data()
    selected_warehouses_df = opt_results.warehouse_selection_data
    warehouse_township_assignment_df = opt_results.warehouse_township_assignment_data

    fig = viz_warehouse_selection(warehouses_df, townships_df, selected_warehouses_df, warehouse_township_assignment_df)
    fig.show()
