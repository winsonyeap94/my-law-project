import mlflow
import shutil
import inspect
import collections
from conf import Config
from pathlib import Path
from src.data_connectors import PandasFileConnector

mlflow.set_tracking_uri(Config.MLFLOW["TRACKING_URI"])  # Setting location to save models
mlflow.set_experiment(Config.MLFLOW["EXPERIMENT_NAME"])


class MLFlowLogger:

    @classmethod
    def log(cls, post_process_output):

        with mlflow.start_run():
            cls.__log_config()
            cls.__log_opt_model(post_process_output)

    @classmethod
    def __log_opt_model(cls, post_process_output):

        artifact_folder = Config.MLFLOW['TEMP_ARTIFACT_DIR']
        Path(artifact_folder).mkdir(parents=True, exist_ok=True)

        # Solver Results
        post_process_output.solver_results.results.write(
            filename=str(Path(artifact_folder, 'solver_results.json')), format='json'
        )
        results_dict = PandasFileConnector.load(Path(artifact_folder, 'solver_results.json'))
        for k, v in results_dict.items():
            results_dict[k] = v[0]
        results_dict = cls.flatten(results_dict)
        params_results_dict = {k: v for k, v in results_dict.items() if type(v) == str}
        metrics_results_dict = {k: v for k, v in results_dict.items() if type(v) != str}

        # Post-processed results
        warehouse_selection_data = post_process_output.warehouse_selection_data
        warehouse_township_assignment_data = post_process_output.warehouse_township_assignment_data
        despatchers_data = post_process_output.despatchers_data

        PandasFileConnector.save(warehouse_selection_data,
                                 Path(artifact_folder, "warehouse_selection_data.csv"))
        PandasFileConnector.save(warehouse_township_assignment_data,
                                 Path(artifact_folder, "warehouse_township_assignment_data.csv"))
        PandasFileConnector.save(despatchers_data,
                            Path(artifact_folder, "despatchers_data.csv"))

        # Logging to mlflow
        mlflow.log_params(params_results_dict)
        mlflow.log_metrics(metrics_results_dict)
        mlflow.log_artifacts(artifact_folder, artifact_path='postprocessing')

        shutil.rmtree(artifact_folder)  # Deleting temp folder

    @classmethod
    def __log_config(cls):

        # Getting Config attributes
        attributes = inspect.getmembers(Config, lambda x: not(inspect.isroutine(x)))
        attributes = [a for a in attributes if not (a[0].startswith('__') and a[0].endswith('__'))]
        attributes = dict(attributes)

        # List of attributes that we want to log
        log_attributes = [
            'NAME', 'OPTIMISATION_MODEL_CONFIG', 'OPTIMISATION_SCENARIO', 'ADD_DELIVERY_TIME_CONSTRAINT',
            'ADD_DESPATCHER_CONSTRAINT', 'OPT_PARAMS'
        ]

        # Subsetting the list of attributes
        attributes = {k: v for k, v in attributes.items() if k in log_attributes}
        attributes = cls.flatten(attributes)

        mlflow.log_params(attributes)

    @classmethod
    def flatten(cls, d, parent_key='', sep='_'):
        items = []
        for k, v in d.items():
            new_key = parent_key + sep + k if parent_key else k
            if isinstance(v, collections.MutableMapping):
                items.extend(cls.flatten(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
