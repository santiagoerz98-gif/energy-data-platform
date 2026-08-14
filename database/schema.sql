-- =====================================================
-- Energy Data Platform
-- Data Warehouse Schema
-- PostgreSQL
-- =====================================================

CREATE SCHEMA IF NOT EXISTS dw;

CREATE SCHEMA IF NOT EXISTS staging;

-- -----------------------------------------------------
-- dim_time (grano horario, YYYYMMDDHH)
-- -----------------------------------------------------
CREATE TABLE dw.dim_time (

    time_key BIGINT PRIMARY KEY,          -- YYYYMMDDHH, ej: 2026080814

    datetime_utc TIMESTAMP NOT NULL UNIQUE,

    date_actual DATE NOT NULL,

    year INT NOT NULL,

    quarter INT NOT NULL,

    month INT NOT NULL,

    month_name VARCHAR(20) NOT NULL,

    day INT NOT NULL,

    hour INT NOT NULL,

    day_of_week INT NOT NULL,             -- ISO: 1..7

    day_name VARCHAR(20) NOT NULL,

    is_weekend BOOLEAN NOT NULL

);

COMMENT ON TABLE dw.dim_time IS 'Dimension de tiempo a grano horario para analisis temporal.';

INSERT INTO dw.dim_time (
    time_key, datetime_utc, date_actual, year, quarter, month, month_name,
    day, hour, day_of_week, day_name, is_weekend
)
SELECT
    TO_CHAR(ts, 'YYYYMMDDHH24')::BIGINT,
    ts::timestamp,
    ts::date,
    EXTRACT(YEAR FROM ts)::INT,
    EXTRACT(QUARTER FROM ts)::INT,
    EXTRACT(MONTH FROM ts)::INT,
    TO_CHAR(ts, 'TMMonth'),
    EXTRACT(DAY FROM ts)::INT,
    EXTRACT(HOUR FROM ts)::INT,
    EXTRACT(ISODOW FROM ts)::INT,
    TO_CHAR(ts, 'TMDay'),
    CASE WHEN EXTRACT(ISODOW FROM ts) IN (6, 7) THEN TRUE ELSE FALSE END
FROM generate_series(
    '2026-01-01 00:00:00'::timestamp,
    '2030-12-31 23:00:00'::timestamp,
    INTERVAL '1 hour'
) AS g(ts)
ON CONFLICT (time_key) DO NOTHING;

CREATE TABLE dw.dim_geography (

    geography_key INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    geo_id INTEGER NOT NULL UNIQUE,

    geo_name VARCHAR(100) NOT NULL

);

CREATE TABLE dw.dim_energy_source (

    energy_source_key INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    technology_name VARCHAR(100) NOT NULL UNIQUE,

    renewable BOOLEAN NOT NULL

);

CREATE TABLE dw.fact_generation (

    generation_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    time_key BIGINT NOT NULL,

    geography_key INTEGER NOT NULL,

    energy_source_key INTEGER NOT NULL,

    indicator_id INTEGER,

    generation_mwh NUMERIC(12,3) NOT NULL CHECK (generation_mwh >= 0),

    CONSTRAINT fk_generation_time
        FOREIGN KEY(time_key)
        REFERENCES dw.dim_time(time_key),

    CONSTRAINT fk_generation_geography
        FOREIGN KEY(geography_key)
        REFERENCES dw.dim_geography(geography_key),

    CONSTRAINT fk_generation_energy
        FOREIGN KEY(energy_source_key)
        REFERENCES dw.dim_energy_source(energy_source_key)

);

CREATE TABLE dw.fact_demand (

    demand_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    time_key BIGINT NOT NULL,

    geography_key INTEGER NOT NULL,

    indicator_id INTEGER,

    demand_mwh NUMERIC(12,3) NOT NULL CHECK (demand_mwh >= 0),

    measurement_type VARCHAR(50) NOT NULL,

    CONSTRAINT fk_demand_time
        FOREIGN KEY(time_key)
        REFERENCES dw.dim_time(time_key),

    CONSTRAINT fk_demand_geography
        FOREIGN KEY(geography_key)
        REFERENCES dw.dim_geography(geography_key)

);

CREATE INDEX idx_fact_generation_time
ON dw.fact_generation(time_key);

CREATE INDEX idx_fact_generation_geography
ON dw.fact_generation(geography_key);

CREATE INDEX idx_fact_generation_energy
ON dw.fact_generation(energy_source_key);

CREATE INDEX idx_fact_demand_time
ON dw.fact_demand(time_key);

CREATE INDEX idx_fact_demand_geography
ON dw.fact_demand(geography_key);

-- Claves naturales unicas: soportan la carga idempotente (delete+insert) de populate_dw.sql
CREATE UNIQUE INDEX uq_fact_demand_natural
ON dw.fact_demand (time_key, geography_key, measurement_type, indicator_id);

CREATE UNIQUE INDEX uq_fact_generation_natural
ON dw.fact_generation (time_key, geography_key, energy_source_key, indicator_id);