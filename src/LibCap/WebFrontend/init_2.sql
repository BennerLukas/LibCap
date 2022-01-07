DROP TABLE IF EXISTS LB_USER;
DROP TABLE IF EXISTS STATUS_HISTORY;
DROP TABLE IF EXISTS OBJECTS;
DROP TABLE IF EXISTS CURRENT_STATUS;


CREATE TABLE LB_USER (
  username  varchar(45)     NOT NULL,
  password  varchar(450)    NOT NULL,
  PRIMARY KEY (username)
);

CREATE TABLE CURRENT_STATUS (
    n_status_id     SERIAL,
    s_status_name   VARCHAR(20),
    PRIMARY KEY (n_status_id)
);

CREATE TABLE OBJECTS (
    n_object_id SERIAL              NOT NULL,
    n_object_type           INT     NOT NULL    DEFAULT 1,
    n_grid_coordinate_x     FLOAT,
    n_grid_coordinate_y     FLOAT,
    n_grid_coordinate_z     FLOAT,
    arr_equipment           VARCHAR [],
    n_status_id             INT     NOT NULL    DEFAULT 0,
    PRIMARY KEY (n_object_id),
    FOREIGN KEY (n_status_id) REFERENCES CURRENT_STATUS (n_status_id)
);

CREATE TABLE STATUS_HISTORY (
    n_id            SERIAL      NOT NULL,
    n_object_id     INT         NOT NULL,
    n_status_id     INT         NOT NULL,
    ts_timestamp    TIMESTAMP   NOT NULL    DEFAULT current_timestamp,
    PRIMARY KEY (n_id),
    FOREIGN KEY (n_object_id) REFERENCES OBJECTS (n_object_id),
    FOREIGN KEY (n_status_id) REFERENCES CURRENT_STATUS (n_status_id)
);

CREATE OR REPLACE PROCEDURE change_status(
    object_id INT,
    status INT,
    change_time TIMESTAMP
)
    language plpgsql
AS '
BEGIN
    UPDATE OBJECTS
    SET n_status_id = status
    WHERE n_object_id = object_id;

    INSERT INTO STATUS_HISTORY (n_object_id, n_status_id, ts_timestamp)
    VALUES (object_id, status, change_time);
END;
';

/* 
Trigger + Function?

- Trigger after update on status

- Function Updates objects

Benefits: No need for executing Procedure manually, every update triggers DB
*/