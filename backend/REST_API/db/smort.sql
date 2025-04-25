CREATE TABLE region (
    ID SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    region VARCHAR(50) NOT NULL,
    latitude DECIMAL(8,6) NOT NULL,
    longitude DECIMAL(9,6) NOT NULL
);

CREATE TABLE sensor (
    ID SERIAL PRIMARY KEY,
    latitude DECIMAL(8,6) NOT NULL,
    longitude DECIMAL(9,6) NOT NULL,
    name VARCHAR(50) NOT NULL
);

CREATE TABLE region_sensor (
    region_ID INTEGER NOT NULL,
    sensor_ID INTEGER NOT NULL,
    PRIMARY KEY (region_ID, sensor_ID),
    FOREIGN KEY (region_ID) REFERENCES region(ID) ON DELETE CASCADE,
    FOREIGN KEY (sensor_ID) REFERENCES sensor(ID) ON DELETE CASCADE
);

CREATE TABLE sensor_record (
    smort_ID INTEGER NOT NULL,
    time_stamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    trash_level DECIMAL(5,2),
    image TEXT NOT NULL,
    PRIMARY KEY (smort_ID, time_stamp),
    FOREIGN KEY (smort_ID) REFERENCES sensor(ID)
);