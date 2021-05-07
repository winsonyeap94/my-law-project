"""
DatabaseFileConnector script includes reading and writing to Postgresql, MySQL, MSSQL.
"""

import pandas as pd
from sqlalchemy import create_engine
from config import Logger


class DatabaseConnector:
    
    DEFAULT_SCHEMAS = {
        'postgresql': 'public',
        'mssql': 'dbo',
        'mysql': None,
    }

    def __init__(self, host: str, port: str, username: str, password: str, database: str,
                 db_type='postgresql', schema_name=None):

        self._logger = Logger().logger
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.db_type = db_type
        if self.db_type not in self.DEFAULT_SCHEMAS.keys():
            self._logger.exception("[DatabaseConnector] Type of connection is not found. Please check for typos.")
        self.schema_name = schema_name or self.DEFAULT_SCHEMAS[db_type]

    def load(self, table_name, sql_query_statement=None, **kwargs):
        """
        Load database table based on SQL query.

        Args:
            table_name ([str]): [name of database table]
            sql_query_statement ([str]): [SQL Query if any. Defaults to None]
            **kwargs ([dict]): [dictionary of extra arguments for instance server_name for mssql connection]
        Returns:
            db_loader([dataframe]): [dataframe]
        """

        try:
            # Establishing connection
            self._logger.debug("[DatabaseConnector] Establishing connection...")
            engine_conn = self._create_engine()
            self._logger.debug("[DatabaseConnector] SQL connection established...")

            # Loading data
            self._logger.info("[DatabaseConnector] Executing SQL query...")
            if self.schema_name is not None:
                schema_table_name = str(self.schema_name) + "." + str(table_name)
            else:
                schema_table_name = table_name
            sql_query_statement = sql_query_statement or self._query_table(schema_table_name)
            db_loader = pd.read_sql(sql_query_statement, con=engine_conn, **kwargs)
            self._logger.info("[DatabaseConnector] SQL query executed successfully.")
            return db_loader

        except Exception as error:
            self._logger.exception(f"[DatabaseConnector] SQL Query Failed. Error: {error}")

        finally:
            engine_conn.dispose()
            self._logger.debug("[DatabaseConnector] SQL connection disposed.")
    
    def save(self, data_df, table_name, if_exist_do='replace', **kwargs):
        """
        Save dataframe to database table.

        Args:
            data_df ([dataframe]): [dataframe to be saved out to database]
            table_name ([str]): [name of database table]
            if_exist_do ([str]): [{'replace', 'append', 'fail'}. Defaults to 'replace']
            **kwargs ([dict]): [dictionary of extra arguments]
        """
        try:

            # Establishing connection
            self._logger.debug("[DatabaseConnector] Establishing connection...")
            engine_conn = self._create_engine()
            self._logger.debug("[DatabaseConnector] SQL connection established...")

            # Saving data
            self._logger.info(f"[DatabaseConnector] Saving data_df to SQL {table_name}...")
            data_df.to_sql(name=table_name, con=engine_conn, if_exists=if_exist_do, index=False, **kwargs)
            self._logger.info(f"[DatabaseConnector] data_df saved to SQL {table_name} successfully.")

            self._logger.info("Dataframe saved out to database successfully. ")

        except Exception as error:
            self._logger.exception(f"[DatabaseConnector] SQL Query Failed. Error: {error}")

        finally:
            engine_conn.dispose()
            self._logger.debug("[DatabaseConnector] SQL connection disposed.")
    
    def _create_engine(self):
        sql_connectors = {
            'postgresql': 'postgresql',
            'mysql': 'mysql+pymysql',
            'mssql': 'mssql+pyodbc'
        }
        sql_connector = sql_connectors[self.db_type]
        if self.db_type == 'mssql':
            engine_conn = create_engine(
                f"{sql_connector}://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
                f"?driver=SQL+Server"
            )
        else:
            engine_conn = create_engine(
                f"{sql_connector}://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
            )
        return engine_conn

    @staticmethod
    def _query_table(table_name):
        """
        Default sql query

        Args:
            table_name ([str]): [name of database table]
        """
        return 'select * from {} '.format(table_name)

