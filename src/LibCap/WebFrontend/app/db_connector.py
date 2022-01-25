import os
import random

import sqlalchemy
import psycopg2
import psycopg2.extras
import pandas as pd
from pandas import DataFrame
import logging
import time


class DatabaseConnector:
    def __init__(self):
        # self.hostname = "localhost"
        self.hostname = "database"
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
                self.hostname = "localhost"
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

    def example_init(self, build_floorplan=True):
        status = self._check_initialisation()
        if status is False:
            logging.error("Executing Example Init")
            if build_floorplan is True:
                self.generate_floorplan_data()
            else:
                for root, dirs, files in os.walk("/src/"):
                    if "example.sql" in files:
                        path = os.path.join(root, "example.sql")
                        logging.info(f"Path für Example in Docker: {path}")
                with open(path) as file:
                    sql_string = file.read()
                self.execute_sql(sql_string)
        else:
            logging.error("Already initialized.")

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
        usernames = self.get_select("SELECT * FROM objects")
        if len(usernames.index) > 0:
            self.initialized = True
            return True
        else:
            self.initialized = False
            return False

    def generate_floorplan_data(self, grid=None):
        """
        n_object_type -> 1: workstation / 2: placeholder
        arr_equipment -> ["PC", "Plug"]
        n_status_id -> 1: free / 4: maintenance
        :return:
        """
        if grid is None:
            grid = [
                [0, 2, 1, 2, 1, 1, 2],
                [1, 2, 1, 2, 1, 1, 2],
                [1, 2, 1, 2, 1, 1, 2],
                [2, 2, 2, 2, 2, 2, 2],
                [2, 2, 2, 2, 2, 2, 2],
                [1, 2, 1, 2, 1, 1, 2],
                [1, 2, 1, 2, 1, 1, 2],
                [2, 2, 2, 2, 2, 2, 2],
                [2, 2, 2, 2, 2, 2, 2],
                [1, 2, 1, 2, 1, 1, 2],
                [1, 2, 1, 2, 1, 1, 2],
                [1, 2, 1, 2, 1, 1, 2],

            ]
        possible_equipment = ["Ethernet", "Lamp", "Plug", "PC"]

        for y, row in enumerate(grid):
            for x, obj in enumerate(row):
                if obj == 2:
                    # placeholder
                    self.insert_workstation([2, x+1, y+1, "NULL", [], 4])
                elif obj == 1:
                    # random_equipment = list(set([random.choice(possible_equipment) for _ in range(random.randint(0, 3))]))
                    random_equipment = random.sample(possible_equipment, k=random.randint(0, 3))
                    random_status = 1 if random.randint(1, 10) < 9 else 4
                    self.insert_workstation([1, x+1, y+1, "NULL", random_equipment, random_status])
                elif obj == 0:
                    self.insert_workstation(
                        [1, 1, 1, "NULL", possible_equipment, 1])  # Default Workstation fully equipped
                else:
                    raise
        return True

    def insert_workstation(self, param_list):
        sql_string = f"""
        INSERT INTO objects (n_object_type, n_grid_coordinate_x, n_grid_coordinate_y, n_grid_coordinate_z, arr_equipment,n_status_id) 
        VALUES (
        {param_list[0]}, 
        {param_list[1]}, 
        {param_list[2]}, 
        {param_list[3]}, 
        ARRAY {param_list[4]}::varchar[], 
        {param_list[5]}
        );"""
        print(sql_string)
        bool, result = self.execute_sql(sql_string)
        return bool
