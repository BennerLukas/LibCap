import os
import random
from typing import List

import sqlalchemy
import psycopg2
import psycopg2.extras
import pandas as pd
from pandas import DataFrame
import logging
import time


class DatabaseConnector:
    """Class that deals with all SQL operations"""

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
        # repeat until connection was successful
        while self.b_connected is False:
            # tests if the database is already accessible
            try:
                # set the needed connections and engines
                self.alchemy_engine = sqlalchemy.create_engine(
                    f'postgresql+psycopg2://postgres:1234@{self.hostname}:{self.port}/postgres')
                self.alchemy_connection = self.alchemy_engine.connect()
                self.psycopg2_connection = psycopg2.connect(database="postgres", user="postgres", port=self.port,
                                                            password="1234", host=self.hostname)

                # if all connections were successful the connection status is set to true
                self.b_connected = True
                print("Database Connected")
                logging.info("Connected to DB")
            except Exception as an_exception:
                logging.error(an_exception)
                logging.error("Not connected to DB")
                # self.hostname = "localhost" # if flask deployed locally while running docker stack for db
                # wait for 5 seconds before trying to reestablish connection
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
            # tries to get content of cursor (result of query) - if empty fails with ProgrammingError
            try:
                result = db_cursor.fetchall()
            except psycopg2.errors.ProgrammingError:
                result = None

            # finishes transaction and closes session
            self.psycopg2_connection.commit()
            db_cursor.close()
            logging.info("Executed SQL query successfully")
            return True, result
        # if SQL statement was invalid it'll be caught and database connection reestablished
        except psycopg2.errors.InFailedSqlTransaction:
            self.b_connected = False
            self._connect()
            logging.error("Transaction Failed - Review given inputs! Reestablished connection to database backend")
            return False, None

    def example_init(self, build_floorplan: bool = True):
        """
        Helper function to create an example based on a grid or a sql file
        :param build_floorplan:
        :return:
        """
        # check if init is valid or if the database already has entries
        status = self._check_initialisation()
        if status is False:
            logging.error("Executing Example Init")
            # if init should be based on floor plan
            if build_floorplan is True:
                self.generate_floorplan_data()
            else:
                # find example.sql in container
                for root, dirs, files in os.walk("/src/"):
                    if "example.sql" in files:
                        path = os.path.join(root, "example.sql")
                        logging.info(f"Path für Example in Docker: {path}")
                # open file and read content
                with open(path) as file:
                    sql_string = file.read()
                # execute read content
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
        """
        Checks initialization by checking if objects table is empty
        :return:
        bool
            existence of workstations in object
        """
        # fetch all entities in objects
        objects = self.get_select("SELECT * FROM objects")
        # checks if amount of entities returned > 0
        if len(objects.index) > 0:
            self.initialized = True
            return True
        else:
            self.initialized = False
            return False

    def generate_floorplan_data(self, grid: List = None):
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

        # creates enumerate object of grid to have the index and value of each row
        for y, row in enumerate(grid):
            # get all entries in grid based on index and value
            for x, obj in enumerate(row):
                # objects with ID 2 are empty spots
                if obj == 2:
                    # call function to create a placeholder
                    self.insert_workstation([2, x + 1, y + 1, "NULL", [], 4])
                # objects with ID 1 are workstations
                elif obj == 1:
                    # get random amount of equipment up to max
                    random_equipment = random.sample(possible_equipment, k=random.randint(0, 3))
                    # sets status randomly to either free (90%) or maintenance (10%)
                    random_status = 1 if random.randint(1, 10) < 9 else 4
                    self.insert_workstation([1, x + 1, y + 1, "NULL", random_equipment, random_status])
                # objects with ID 0 are special workstations to be manually inserted
                elif obj == 0:
                    self.insert_workstation(
                        [1, 1, 1, "NULL", possible_equipment, 1])  # Default Workstation fully equipped
                else:
                    raise
        return True

    def insert_workstation(self, param_list):
        """
        Helper function to create a new workstation object in database.
        :param param_list:
        :return:
        """
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
        boolean, _ = self.execute_sql(sql_string)
        return boolean
