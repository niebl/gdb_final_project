-- Database: iip_db

CREATE TABLE test
(
    test_id int GENERATED ALWAYS AS IDENTITY,
    test_name text UNIQUE,
    UNIQUE(test_id)
);

CREATE TABLE osem_bikes
(
    internal_id int GENERATED ALWAYS AS IDENTITY,
    bike_id varchar UNIQUE,
    
    last_update timestamp,
    position geometry,
    to_delete boolean DEFAULT false
);

CREATE TABLE osem_bike_measurements
(
    internal_id int GENERATED ALWAYS AS IDENTITY,
    sensor_id varchar,
    bike_id varchar,

    measurement_type varchar,
    measurement_value varchar,
    measurement_unit varchar,
    measurement_time timestamp,

    position geometry,

    to_delete boolean DEFAULT false,

    CONSTRAINT bike_id
        FOREIGN KEY(bike_id)
        REFERENCES osem_bikes(bike_id)
        ON DELETE CASCADE
);