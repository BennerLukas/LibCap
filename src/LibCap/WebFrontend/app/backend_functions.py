# imports
from app.db_connector import *
from typing import List, Dict


class Backend:
    def __init__(self, database_connector: DatabaseConnector):
        self.dbc = database_connector
        self.user = None

    def _prep_param_list(self, param_list):
        print(param_list)
        equipment_list = ["Ethernet", "Lamp", "Plug", "PC"]
        bool_conversion = {"on": True, "off": False}
        equipment_list_bool = [bool_conversion.get(param_list.get("Ethernet")),
                               bool_conversion.get(param_list.get("Lamp")),
                               bool_conversion.get(param_list.get("Plug")), bool_conversion.get(param_list.get("PC"))]
        equipment_list_decoded = ["'" + str(equipment) + "'" for index, equipment in enumerate(equipment_list) if
                                  equipment_list_bool[index]]
        equipment_list_str = ",".join(equipment_list_decoded)
        return equipment_list_str

    def add_controller_to_database(self, param_list) -> int:

        equipment_list_str = self._prep_param_list(param_list)

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
        bool, result = self.dbc.execute_sql(sql_string)
        return result

    def get_auslastung(self) -> List[int]:
        anzahl_frei = self.dbc.get_select(f"SELECT COUNT(n_object_id) FROM OBJECTS WHERE n_status_id = 1").iat[0, 0]
        anzahl_belegt = self.dbc.get_select(f"SELECT COUNT(n_object_id) FROM OBJECTS WHERE n_status_id = 2").iat[0, 0]
        anzahl_reserviert = self.dbc.get_select(f"SELECT COUNT(n_object_id) FROM OBJECTS WHERE n_status_id = 3").iat[
            0, 0]
        return [anzahl_frei, anzahl_belegt, anzahl_reserviert]

    def get_sitzplaetze(self) -> List[Dict]:
        df = self.dbc.get_select('SELECT DISTINCT * FROM objects')
        df["n_grid_coordinate_x"] = df["n_grid_coordinate_x"].astype(int)
        df["n_grid_coordinate_y"] = df["n_grid_coordinate_y"].astype(int)
        # transpose dataframe to be usable as dictionary
        data_transposed_as_dict = df.transpose().to_dict()
        # create a list with each object
        ergebnis = [data_transposed_as_dict.get(i) for i in data_transposed_as_dict.keys()]

        # fetch amount of rows and seats in each row
        ys = int(max(df.n_grid_coordinate_y.unique()))
        xs = int(max(df.n_grid_coordinate_x.unique()))

        endergebnis = []
        for y in range(1, ys + 1):
            # print("Reihe:",y)
            subliste = []
            for x in range(1, xs + 1):
                vorhanden = False
                # print("Platz", x)
                for o in ergebnis:
                    if o.get('n_grid_coordinate_y') == y and o.get('n_grid_coordinate_x') == x:
                        # print("Found", o)
                        vorhanden = True
                        subliste.append(o)
                if vorhanden is False:
                    # print(f"{x} war nicht vorhanden")
                    filler_dict = {'n_object_id': f"filler_object_{x}_{y}", 'n_object_type': 2,
                                   'n_grid_coordinate_x': x, 'n_grid_coordinate_y': y, 'n_grid_coordinate_z': 1.0,
                                   'arr_equipment': [], 'n_status_id': 4,
                                   'ts_last_change': 'now'}
                    subliste.append(filler_dict)

            endergebnis.append(subliste)

        return endergebnis

    def get_counter(self):
        ctr_occupied_workstations = self.dbc.get_select(
            f"SELECT COUNT(n_object_id) FROM OBJECTS WHERE n_status_id = 2 OR n_status_id = 3 AND n_object_type = 1").iat[
            0, 0]
        ctr_available_workstations = \
        self.dbc.get_select(f"SELECT COUNT(n_object_id) FROM OBJECTS WHERE n_status_id = 1 AND n_object_type = 1").iat[
            0, 0]
        ctr_maintenance_workstations = \
        self.dbc.get_select(f"SELECT COUNT(n_object_id) FROM OBJECTS WHERE n_status_id = 4 AND n_object_type = 1").iat[
            0, 0]
        ctr_total_workstations = \
        self.dbc.get_select(f"SELECT COUNT(n_object_id) FROM OBJECTS WHERE n_object_type = 1").iat[0, 0]
        return ctr_occupied_workstations, ctr_available_workstations, ctr_maintenance_workstations, ctr_total_workstations

    def get_workstations(self):
        # id, label

        df = self.dbc.get_select(
            f"SELECT n_object_id, n_grid_coordinate_x, n_grid_coordinate_y FROM OBJECTS WHERE n_object_type = 1;")
        df = df.sort_values("n_object_id")
        workstations = [{"id": df.iloc[i, 0], "label": f"{df.iloc[i,0]} (X: {int(df.iloc[i,1])} Y: {int(df.iloc[i,2])})"} for i in range(len(df.index))]
        return workstations

    def update_status(self, workstation_id, state):
        sql_string = f"UPDATE OBJECTS SET n_status_id = {state} WHERE n_object_id = {workstation_id};"
        _, result = self.dbc.execute_sql(sql_string)
        return bool

    def update_equipment(self, workstation_id, equipment):

        equipment_list_str = self._prep_param_list(equipment)
        print(equipment_list_str)

        sql_string = f"UPDATE OBJECTS SET arr_equipment = ARRAY [{equipment_list_str}]::varchar[] WHERE n_object_id = {workstation_id};"
        _, result = self.dbc.execute_sql(sql_string)
        return bool

    def delete(self, workstation_id):
        sql_string = f"DELETE FROM objects WHERE n_object_id = {workstation_id};"
        _, result = self.dbc.execute_sql(sql_string)
        return bool
