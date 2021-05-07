"""
Dataset connector script includes PandasFileConnector, DatabaseFileConnector, APIFileConnector, CloudFileConnector, YAMLFileConnector
"""

import yaml
from conf import Logger


class YAMLFileConnector:

    _logger = Logger().logger

    @classmethod
    def load(cls, filepath, **kwargs):
        """
        Read a YAML file and return the list of dictionaries.

        Args:
            filepath ([str]): [filepath]
        Returns:
            dict_file ([dict]): [list of dictionaries]
        """

        with open(filepath, 'r') as file:
            try:
                data_dict = yaml.safe_load(file, **kwargs)
                cls._logger.info(f"[YAMLFileConnector] YAML file ({filepath}) loaded successfully.")

                return data_dict
            except Exception as error:
                return error

    @classmethod
    def save(cls, data_dict, filepath, **kwargs):
        """
        Save out dictionary file as yaml file format.

        Args:
            data_dict ([dict]): [list of dictionaries to be saved out as yaml file]
            filepath ([str]): [filepath]
        """

        try:
            with open(filepath, 'w') as file:
                yaml.dump(data_dict, file, sort_keys=False, **kwargs)
            cls._logger.info(f"[YAMLFileConnector] List of dictionaries saved as YAML file successfully to {filepath}.")

        except Exception as error:
            return error


if __name__ == "__main__":

    yaml_file = YAMLFileConnector.load('data/testing.yaml')
    YAMLFileConnector.save(yaml_file, 'data/testing_sub.yaml')
    print(yaml_file)
