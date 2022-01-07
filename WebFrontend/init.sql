CREATE TABLE IF NOT EXISTS user (
  username  varchar(45)     NOT NULL,
  password  varchar(450)    NOT NULL,
  PRIMARY KEY (username)
);

CREATE TABLE IF NOT EXISTS status(
    n_status_id     SERIAL,
    s_status_name   VARCHAR(20),
    PRIMARY KEY (n_status_id)
);

CREATE TABLE IF NOT EXISTS objects (
    n_object_id SERIAL              NOT NULL,
    n_object_type           INT     NOT NULL    DEFAULT 1,
    n_grid_coordinate_x     FLOAT,
    n_grid_coordinate_y     FLOAT,
    n_grid_coordinate_z     FLOAT,
    arr_equipment           VARCHAR []
    n_status_id             INT     NOT NULL    DEFAULT 0,
    PRIMARY KEY (n_object_id),
    FOREIGN KEY (n_status_id) REFERENCES status (n_status_id)
);

CREATE TABLE IF NOT EXISTS status_changes (
    n_id            SERIAL      NOT NULL,
    n_object_id     INT         NOT NULL,
    n_status_id     INT         NOT NULL,
    ts_timestamp    TIMESTAMP   NOT NULL    DEFAULT current_timestamp,
    PRIMARY KEY (n_id),
    FOREIGN KEY (n_object_id) REFERENCES objects (n_object_id),
    FOREIGN KEY (n_status_id) REFERENCES status (n_status_id)
);

create or replace procedure change_status(
    object_id INT,
    status INT,
    change_time TIMESTAMP
)
    language plpgsql
AS
$$
BEGIN
    UPDATE objects
    SET n_status_id = status
    WHERE n_object_id = object_id;

    INSERT INTO status_changes (n_object_id, n_status_id, ts_timestamp)
    VALUES (object_id, status, change_time)
END;
$$
;