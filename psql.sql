CREATE TABLE multiple_predictions (
    product_id VARCHAR(255) PRIMARY KEY,
    air_temperature_k FLOAT,
    process_temperature_k FLOAT,
    rotational_speed_rpm INT,
    torque_nm FLOAT,
    tool_wear_min INT,
    type VARCHAR(255),
    prediction INT
);

CREATE TABLE prediction (
    id SERIAL PRIMARY KEY,
    product_id VARCHAR(255) ,
    air_temperature_k FLOAT,
    process_temperature_k FLOAT,
    rotational_speed_rpm INT,
    torque_nm FLOAT,
    tool_wear_min INT,
    type VARCHAR(255),
    prediction INT,
    date DATE,
    source VARCHAR(255)
);


ALTER TABLE single_prediction
ALTER COLUMN date_time TYPE DATE;

ALTER TABLE single_prediction
RENAME COLUMN date_time TO date;

ALTER TABLE multiple_predictions
ADD COLUMN date DATE,
ADD COLUMN source VARCHAR(255);

INSERT INTO single_prediction (
    product_id,
    air_temperature_k,
    process_temperature_k,
    rotational_speed_rpm,
    torque_nm,
    tool_wear_min,
    type,
    prediction,
    date,
    source
) VALUES (
    'L12345',
    1230,
    2342,
    9834,
    234,
    243,
    'L',
    1,
    '2024-04-02',  -- Assuming '2024-04-02' is the date to be inserted
    'webapp'
);