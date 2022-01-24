import os

import sqlalchemy
import psycopg2
import psycopg2.extras
import pandas as pd
from pandas import DataFrame
import logging
import time


class DatabaseConnector:
    def __init__(self):
        self.hostname = "localhost"
        # self.hostname = "database"
        self.port = 5432

        self.alchemy_engine = None
        self.alchemy_connection = None
        self.psycopg2_connection = None

        self.b_connected = False

        self._connect()

    def _connect(self) -> bool:
        """
        Function to connect to the database. Tests if connection exists and retries until a connection has been made.
        :return:
        bool
            Connection status after function ended
        """
        while self.b_connected is False:
            try:
                self.alchemy_engine = sqlalchemy.create_engine(
                    f'postgresql+psycopg2://postgres:1234@{self.hostname}:{self.port}/postgres')
                self.alchemy_connection = self.alchemy_engine.connect()
                self.psycopg2_connection = psycopg2.connect(database="postgres", user="postgres", port=self.port,
                                                            password="1234", host=self.hostname)
                self.b_connected = True
                print("Database Connected")
                logging.info("Connected to DB")
            except Exception as an_exception:
                logging.error(an_exception)
                logging.error("Not connected to DB")
                time.sleep(5)
        return True

    def execute_sql(self, sql: str) -> bool:
        """
        Function to use when calling a procedure or transaction in Psycopg2
        :param sql: SQL query as string
        :return:
        List
             bool: Success of operation
             list: Return value of operation
        """

        try:
            db_cursor = self.psycopg2_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
            db_cursor.execute(sql)
            try:
                result = db_cursor.fetchall()
            except psycopg2.errors.ProgrammingError:
                result = None

            self.psycopg2_connection.commit()
            db_cursor.close()
            logging.info("Executed SQL query successfully")
            return True, result
        except psycopg2.errors.InFailedSqlTransaction:
            self.b_connected = False
            self._connect()
            logging.error("Transaction Failed - Review given inputs! Reestablished connection to database backend")
            return False, None

    # def example_init(self):
    #     status = self._check_initialisation()
    #     if status is False:
    #         logging.error("Executing Example Init")
    #         for root, dirs, files in os.walk("/src/"):
    #             if "example.sql" in files:
    #                 path = os.path.join(root, "example.sql")
    #                 logging.info(f"Path für Example in Docker: {path}")
    #         with open(path) as file:
    #             sql_string = file.read()
    #         self.execute_sql(sql_string)
    #     else:
    #         logging.error("Already initialized.")

    def get_select(self, sql_query: str) -> DataFrame:
        """
        The function returns the result of a given SQL select query as Pandas DataFrame.
        :param sql_query: SELECT statement in SQL
        :return:
        DataFrame or bool
            The resulting table of the query
        """
        try:
            df = pd.read_sql_query(sql_query, self.alchemy_connection)
        except Exception as an_exception:
            logging.error(an_exception)
            logging.error("Query couldn't be executed.")
            return False
        return df

    def _check_initialisation(self) -> bool:
        usernames = self.get_select("SELECT * FROM LB_USER")
        if len(usernames.index) > 0:
            self.initialized = True
            return True
        else:
            self.initialized = False
            return False
