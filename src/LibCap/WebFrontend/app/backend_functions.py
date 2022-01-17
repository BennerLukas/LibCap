# imports
from app.db_connector import *
from typing import List, Dict


class Backend:
    def __init__(self, database_connector: DatabaseConnector):
        self.dbc = database_connector
        self.user = None

    def add_controller_to_database(self, param_list) -> int:
        equipment_list = ["LAN", "Lampe", "Steckdose", "Drehstuhl"]
        equipment_list_bool = [param_list.get("LAN"), param_list.get("Lampe"),
                               param_list.get("Steckdose"), param_list.get("Drehstuhl")]
        equipment_list_decoded = [equipment for index, equipment in enumerate(equipment_list) if
                                  equipment_list_bool[index]]
        equipment_list_str = ",".join(equipment_list_decoded)

        sql_string = f"""
        INSERT INTO OBJECTS(
            n_object_type, 
            n_grid_coordinate_x, 
            n_grid_coordinate_y, 
            n_grid_coordinate_z, 
            arr_equipment, 
            n_status_id)
        VALUES (
            {param_list.get("object_type", 1)},
            {param_list.get("x")},
            {param_list.get("y")},
            {param_list.get("z")},
            ARRAY ({equipment_list_str}),
            {param_list.get("status")});
        
        """
        self.dbc.execute_sql(sql_string)
        pass

    def set_user(self, username: str, password: str) -> str:
        sql_string = f"SELECT * FROM LB_USER WHERE username = {username} AND password = {password}"
        user = self.dbc.get_select(sql_string)
        if user is False:
            return False
        else:
            self.user = username
            return True

    def get_auslastung(self) ->List[int]:
        anzahl_frei = self.dbc.get_select(f"SELECT COUNT(n_object_id) FROM OBJECTS WHERE n_status_id = 1").iat[0, 0]
        anzahl_belegt = self.dbc.get_select(f"SELECT COUNT(n_object_id) FROM OBJECTS WHERE n_status_id = 2").iat[0, 0]
        anzahl_reserviert = self.dbc.get_select(f"SELECT COUNT(n_object_id) FROM OBJECTS WHERE n_status_id = 3").iat[0, 0]
        return [anzahl_frei, anzahl_belegt, anzahl_reserviert]
