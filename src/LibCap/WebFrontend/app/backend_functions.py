# imports
from app.db_connector import *
from typing import List, Dict, Tuple


class Backend:
    """
    Class of helper functions used in the frontend.
    """
    def __init__(self, database_connector: DatabaseConnector):
        self.dbc = database_connector

    @staticmethod
    def _prep_param_list(param_list: Dict) -> str:
        """
        Converts a dictionary based on a key value pair of equipment string and status string to a string used for SQL.
        :param param_list:
        :return:
        str
            usable string for SQL operations pertaining to the equipment ARRAY in the objects table
        """
        print(param_list)
        # helper variables
        equipment_list = ["Ethernet", "Lamp", "Plug", "PC"]
        bool_conversion = {"on": True, "off": False}

        # converts the dictionary to a list of bools
        equipment_list_bool = [bool_conversion.get(param_list.get("Ethernet")),
                               bool_conversion.get(param_list.get("Lamp")),
                               bool_conversion.get(param_list.get("Plug")), bool_conversion.get(param_list.get("PC"))]

        # list comprehension to create string of all selected equipment options
        equipment_list_decoded = ["'" + str(equipment) + "'"
                                  for index, equipment in enumerate(equipment_list)
                                  if equipment_list_bool[index]]

        # joins the list with commas to create a viable string for sql operations
        equipment_list_str = ",".join(equipment_list_decoded)
        return equipment_list_str

    def add_controller_to_database(self, param_list: Dict) -> int:
        """
        Adds a controller given a equipment dictionary to the database.
        :param param_list:
        :return:
        int
            ID of new controller
        """
        # converts Dictionary to string used in SQL statement
        equipment_list_str = self._prep_param_list(param_list)

        # test if object already exists
        result = self.dbc.get_select(
            f"""SELECT COUNT(n_object_id) FROM OBJECTS 
                WHERE n_grid_coordinate_x = {param_list.get('x')} AND n_grid_coordinate_y = {param_list.get('y')}""") \
            .iat[0, 0]
        # result is the number of objects found -- should never exceed one to not violate table constraints
        if result == 1:
            # already in use
            return None

        # Insert statement for SQL
        sql_string = f"""
        INSERT INTO OBJECTS(
            n_object_type, 
            n_grid_coordinate_x, 
            n_grid_coordinate_y, 
            arr_equipment, 
            n_status_id)
        VALUES (
            {param_list.get("object_type", 1)},
            {param_list.get("x")},
            {param_list.get("y")},
            ARRAY [{equipment_list_str}]::varchar[],
            {param_list.get("status")})
        RETURNING n_object_id;
        
        """

        # Executes the SQL statement
        _, result = self.dbc.execute_sql(sql_string)
        return result

    def get_occupancy(self) -> List[int]:
        """
        Helper function for occupancy chart
        :return:
        """
        # fetches the number of free workstations
        number_available = self.dbc.get_select(f"SELECT COUNT(n_object_id) FROM OBJECTS WHERE n_status_id = 1").iat[
            0, 0]
        # fetches the number of occupied workstations and the ones currently in their grace period
        number_occupied = self.dbc.get_select(f"""SELECT COUNT(n_object_id) FROM OBJECTS 
                                                  WHERE n_status_id = 2 OR n_status_id = 3""").iat[0, 0]
        # fetches the number of reserved workstations
        number_reserved = self.dbc.get_select(f"SELECT COUNT(n_object_id) FROM OBJECTS WHERE n_status_id = 5").iat[0, 0]
        return [number_available, number_occupied, number_reserved]

    def get_dashboard_infos(self) -> List[Dict]:
        """
        Gets all objects for the frontend dashboard and returns them as a list of dictionaries.
        :return:
        List
            Dictionaries with column names as keys and their respective values
        """
        # Fetch all objects in objects table
        df = self.dbc.get_select('SELECT DISTINCT * FROM objects')

        # convert column datatypes to int for formatting
        df["n_grid_coordinate_x"] = df["n_grid_coordinate_x"].astype(int)
        df["n_grid_coordinate_y"] = df["n_grid_coordinate_y"].astype(int)

        # transpose dataframe to be usable as dictionary
        data_transposed_as_dict = df.transpose().to_dict()

        # create a list with each object
        tmp_result = [data_transposed_as_dict.get(i) for i in data_transposed_as_dict.keys()]

        # fetch amount of rows and seats in each row
        ys = int(max(df.n_grid_coordinate_y.unique()))
        xs = int(max(df.n_grid_coordinate_x.unique()))

        # prep result list
        result = []
        # create n rows based on the max value of n_grid_coordinate_y
        for y in range(1, ys + 1):
            # print("Reihe:",y)
            # sublist represents one row of objects
            sublist = []
            # create n column based on the max value of n_grid_coordinate_x
            for x in range(1, xs + 1):
                # base assumption that on that specific coordinate is no workstation
                exist = False
                # print("Platz", x)
                # iterate over all objects
                for o in tmp_result:
                    # if an object has the current grid coordinates it'll be appended to sublist and existence is
                    # remembered
                    if o.get('n_grid_coordinate_y') == y and o.get('n_grid_coordinate_x') == x:
                        # print("Found", o)
                        exist = True
                        sublist.append(o)
                # if no object was found that has the grid coordinate
                if exist is False:
                    # print(f"{x} war nicht vorhanden")
                    # create a base object that is not a workstation (object_type != 1) and
                    # have its status set to maintenance (status_id = 4)
                    filler_dict = {'n_object_id': f"filler_object_{x}_{y}", 'n_object_type': 2,
                                   'n_grid_coordinate_x': x, 'n_grid_coordinate_y': y, 'n_grid_coordinate_z': 1.0,
                                   'arr_equipment': [], 'n_status_id': 4,
                                   'ts_last_change': 'now'}
                    # append to row list
                    sublist.append(filler_dict)
            # append row to final list
            result.append(sublist)

        return result

    def get_counter(self) -> Tuple:
        """
        Helper function to fetch multiple KPIs pertaining to the occupational status of all workstations.
        :return:
        Tuple counter of occupied, available, maintenance and total workstations
        """
        ctr_occupied_workstations = self.dbc.get_select(
            f"SELECT COUNT(n_object_id) FROM OBJECTS WHERE n_status_id = 2 OR n_status_id = 3 OR n_status_id = 5 AND n_object_type = 1").iat[
            0, 0]
        ctr_available_workstations = \
            self.dbc.get_select(
                f"SELECT COUNT(n_object_id) FROM OBJECTS WHERE n_status_id = 1 AND n_object_type = 1").iat[0, 0]
        ctr_maintenance_workstations = \
            self.dbc.get_select(
                f"SELECT COUNT(n_object_id) FROM OBJECTS WHERE n_status_id = 4 AND n_object_type = 1").iat[0, 0]
        ctr_total_workstations = \
            self.dbc.get_select(f"SELECT COUNT(n_object_id) FROM OBJECTS WHERE n_object_type = 1").iat[0, 0]
        return (ctr_occupied_workstations, ctr_available_workstations, ctr_maintenance_workstations,
                ctr_total_workstations)

    def get_workstations(self) -> List:
        """
        Preparatory function to fetch all active workstations with id and location for webpage.
        :return:
        List
            Dictionaries with key-value-pair of "id" and "label"
        """
        # id, label
        # Fetches all objects and their coordinates if they are workstations (i.e. n_object_type = 1)
        df = self.dbc.get_select(
            f"SELECT n_object_id, n_grid_coordinate_x, n_grid_coordinate_y FROM OBJECTS WHERE n_object_type = 1;")
        # Sort dataframe by id to have a more visually pleasing experience in front end
        df = df.sort_values("n_object_id")
        # List comprehension to get dictionaries for all rows in dataframe
        # Values of cells are fetched with iloc - row, column syntax
        workstations = [
            {"id": df.iloc[i, 0], "label": f"{df.iloc[i, 0]} (X: {int(df.iloc[i, 1])} Y: {int(df.iloc[i, 2])})"} for i
            in range(len(df.index))]
        return workstations

    def update_status(self, workstation_id: int, state: int):
        """
        Sets the status of a workstation to the passed state.
        :param workstation_id:
        :param state:
        :return:
        bool
            success status of update operation
        """
        sql_string = f"UPDATE OBJECTS SET n_status_id = {state} WHERE n_object_id = {workstation_id};"
        _, result = self.dbc.execute_sql(sql_string)
        return bool

    def update_equipment(self, workstation_id: int, equipment: Dict) -> bool:
        """
        Updates a workstation to have the passed equipment.
        :param workstation_id: integer representing the index of a workstation
        :param equipment: list containing all equipment
        :return:
        bool
            success status of update operation
        """
        # Converts Param Dictionary to
        equipment_list_str = self._prep_param_list(equipment)
        print(equipment_list_str)

        sql_string = f"UPDATE OBJECTS SET arr_equipment = ARRAY [{equipment_list_str}]::varchar[] WHERE n_object_id = {workstation_id};"
        _, result = self.dbc.execute_sql(sql_string)
        return bool

    def delete(self, workstation_id: int) -> bool:
        """
        Executes a delete operation in the database for a given workstation id.
        :param workstation_id:
        :return:
        bool
            success status of delete operation
        """
        sql_string = f"DELETE FROM objects WHERE n_object_id = {workstation_id};"
        _, result = self.dbc.execute_sql(sql_string)
        return bool

    def get_timeseries_forecast(self):
        # SELECT COUNT(n_object_id) FROM OBJECTS WHERE n_object_type = 1
        ts_available_workstations = self.get_counter()[3]
        _, ts_status_history = self.dbc.execute_sql(f'''
                                                    SELECT (AVG(n_occupied_objects)/{ts_available_workstations}::float)*100 as n_occupancy_rate, date_part('isodow', ts_weekday)
                                                    FROM
                                                    (SELECT (COUNT(DISTINCT n_object_id)) as n_occupied_objects, ts_timestamp::date as ts_weekday
                                                    FROM "status_history"
                                                    WHERE n_status_id in (2,3,5)
                                                    GROUP BY ts_timestamp::date
                                                    ORDER BY ts_weekday) Dayview
                                                    GROUP BY  date_part('isodow', ts_weekday)
                                                    ORDER BY  date_part('isodow', ts_weekday)
                                                    ''')
        print(ts_status_history)
        weekly_list = [0, 0, 0, 0, 0, 0, 0]

        if ts_status_history is not None:

            for i in ts_status_history:
                weekly_list[int(i[1]) - 1] = i[0]

        print(weekly_list)
        return weekly_list
