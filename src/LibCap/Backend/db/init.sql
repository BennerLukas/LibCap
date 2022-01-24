DROP TABLE IF EXISTS LB_USER;

DROP TABLE IF EXISTS STATUS_HISTORY;

DROP TABLE IF EXISTS OBJECTS;

DROP TABLE IF EXISTS CURRENT_STATUS;


/*WebFrontend*/
CREATE TABLE LB_USER (
    username varchar(45) NOT NULL,
    password varchar(450) NOT NULL,
    PRIMARY KEY (username)
);


/*Static status lookup*/
CREATE TABLE CURRENT_STATUS (
    n_status_id serial NOT NULL,
    s_status_name varchar(20),
    /*Occupied, Free, etc.*/
    PRIMARY KEY (n_status_id)
);

CREATE TABLE OBJECTS (
    n_object_id serial NOT NULL,
    n_object_type int NOT NULL DEFAULT 1,
    n_grid_coordinate_x float,
    n_grid_coordinate_y float,
    n_grid_coordinate_z float,
    arr_equipment varchar[],
    n_status_id int NOT NULL DEFAULT 0,
    ts_last_change timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (n_object_id),
    FOREIGN KEY (n_status_id) REFERENCES CURRENT_STATUS (n_status_id)
    /*Lookup status in CURRENT_STATUS*/
);

CREATE TABLE STATUS_HISTORY (
    n_id serial NOT NULL,
    n_object_id int NOT NULL,
    n_status_id int NOT NULL,
    ts_timestamp timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (n_id),
    FOREIGN KEY (n_object_id) REFERENCES OBJECTS (n_object_id),
    FOREIGN KEY (n_status_id) REFERENCES CURRENT_STATUS (n_status_id)
);

-- FUNCTIONS
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
   NEW.ts_last_change = CURRENT_TIMESTAMP; 
   RETURN NEW;
END;
$$ language 'plpgsql';

CREATE OR REPLACE FUNCTION track_changes()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO STATUS_HISTORY (n_object_id, n_status_id, ts_timestamp)
        Values (NEW.n_object_id, NEW.n_status_id, NEW.ts_last_change);
    RETURN NEW;
END;
$$ language 'plpgsql';

-- TRIGGERS
CREATE TRIGGER status_update BEFORE UPDATE
    ON OBJECTS FOR EACH ROW EXECUTE PROCEDURE 
    update_timestamp();

CREATE TRIGGER change_tracker AFTER UPDATE
    ON OBJECTS FOR EACH ROW EXECUTE PROCEDURE 
    track_changes();


-- INSERTS
INSERT INTO CURRENT_STATUS (s_status_name)
    VALUES ('Free'), ('Occupied'), ('Grace Period'), ('Unavailable');

--INSERT INTO OBJECTS (n_grid_coordinate_x, n_grid_coordinate_y, n_grid_coordinate_z, arr_equipment, n_status_id)
--    VALUES (1, 1, 1, '{plug}', 1);

