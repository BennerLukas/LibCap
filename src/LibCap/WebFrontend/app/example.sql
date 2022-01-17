INSERT INTO LB_USER(username, password)
VALUES ('admin', 'admin');
INSERT INTO CURRENT_STATUS(s_status_name)
VALUES ('frei');
INSERT INTO CURRENT_STATUS(s_status_name)
VALUES ('belegt');
INSERT INTO CURRENT_STATUS(s_status_name)
VALUES ('reserviert');
INSERT INTO CURRENT_STATUS(s_status_name)
VALUES ('anderes');
INSERT INTO objects (n_object_type, n_grid_coordinate_x, n_grid_coordinate_y, n_grid_coordinate_z, arr_equipment, n_status_id)
VALUES (1, 1, 1, 1, ARRAY['LAN', 'Steckdose', 'Leselampe'], 1);
INSERT INTO objects (n_object_type, n_grid_coordinate_x, n_grid_coordinate_y, n_grid_coordinate_z, arr_equipment, n_status_id)
VALUES (1, 2, 1, 1, ARRAY['LAN', 'Steckdose', 'Leselampe'], 2);
INSERT INTO objects (n_object_type, n_grid_coordinate_x, n_grid_coordinate_y, n_grid_coordinate_z, arr_equipment, n_status_id)
VALUES (1, 3, 1, 1, ARRAY['LAN', 'Steckdose', 'Leselampe'],1);
INSERT INTO objects (n_object_type, n_grid_coordinate_x, n_grid_coordinate_y, n_grid_coordinate_z, arr_equipment, n_status_id)
VALUES (1, 4, 1, 1, ARRAY['LAN', 'Steckdose', 'Leselampe'],1);
INSERT INTO objects (n_object_type, n_grid_coordinate_x, n_grid_coordinate_y, n_grid_coordinate_z, arr_equipment, n_status_id)
VALUES (1, 1, 2, 1, ARRAY['LAN', 'Steckdose', 'Leselampe'],3);
INSERT INTO objects (n_object_type, n_grid_coordinate_x, n_grid_coordinate_y, n_grid_coordinate_z, arr_equipment, n_status_id)
VALUES (1, 2, 2, 1, ARRAY['LAN', 'Steckdose', 'Leselampe'],3);
INSERT INTO objects (n_object_type, n_grid_coordinate_x, n_grid_coordinate_y, n_grid_coordinate_z, arr_equipment, n_status_id)
VALUES (1, 3, 2, 1, ARRAY['LAN', 'Steckdose'], 1);
INSERT INTO objects (n_object_type, n_grid_coordinate_x, n_grid_coordinate_y, n_grid_coordinate_z, arr_equipment, n_status_id)
VALUES (1, 4, 2, 1, ARRAY['LAN', 'Steckdose', 'Leselampe'], 2);
INSERT INTO objects (n_object_type, n_grid_coordinate_x, n_grid_coordinate_y, n_grid_coordinate_z, arr_equipment, n_status_id)
VALUES (1, 1, 3, 1, ARRAY['LAN', 'Steckdose', 'Leselampe'], 4);
INSERT INTO objects (n_object_type, n_grid_coordinate_x, n_grid_coordinate_y, n_grid_coordinate_z, arr_equipment, n_status_id)
VALUES (1, 2, 3, 1, ARRAY['Steckdose', 'Leselampe'], 1);
INSERT INTO objects (n_object_type, n_grid_coordinate_x, n_grid_coordinate_y, n_grid_coordinate_z, arr_equipment, n_status_id)
VALUES (1, 3, 3, 1, ARRAY['LAN', 'Steckdose', 'Leselampe'], 1);
INSERT INTO objects (n_object_type, n_grid_coordinate_x, n_grid_coordinate_y, n_grid_coordinate_z, arr_equipment, n_status_id)
VALUES (1, 4, 3, 1, ARRAY['Steckdose', 'Leselampe'], 1);
INSERT INTO objects (n_object_type, n_grid_coordinate_x, n_grid_coordinate_y, n_grid_coordinate_z, arr_equipment, n_status_id)
VALUES (1, 1, 4, 1, ARRAY['Steckdose', 'Leselampe'], 1);
INSERT INTO objects (n_object_type, n_grid_coordinate_x, n_grid_coordinate_y, n_grid_coordinate_z, arr_equipment, n_status_id)
VALUES (1, 2, 4, 1, ARRAY['Steckdose', 'Leselampe'], 1);