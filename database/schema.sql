-- =====================================================
-- Energy Data Platform
-- Data Warehouse Schema
-- PostgreSQL
-- =====================================================

CREATE SCHEMA IF NOT EXISTS dw;

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

    time_key INTEGER NOT NULL,

    geography_key INTEGER NOT NULL,

    energy_source_key INTEGER NOT NULL,

    generation_mwh NUMERIC(12,3) NOT NULL CHECK (generation_mwh >= 0),

    CONSTRAINT fk_generation_time
        FOREIGN KEY(time_key)
        REFERENCES dim_time(time_key),

    CONSTRAINT fk_generation_geography
        FOREIGN KEY(geography_key)
        REFERENCES dim_geography(geography_key),

    CONSTRAINT fk_generation_energy
        FOREIGN KEY(energy_source_key)
        REFERENCES dim_energy_source(energy_source_key)

);

CREATE TABLE dw.fact_demand (

    demand_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    time_key INTEGER NOT NULL,

    geography_key INTEGER NOT NULL,

    demand_mwh NUMERIC(12,3) NOT NULL CHECK (demand_mwh >= 0),

    measurement_type VARCHAR(50) NOT NULL,

    CONSTRAINT fk_demand_time
        FOREIGN KEY(time_key)
        REFERENCES dim_time(time_key),

    CONSTRAINT fk_demand_geography
        FOREIGN KEY(geography_key)
        REFERENCES dim_geography(geography_key)

);

CREATE INDEX idx_fact_generation_time
ON fact_generation(time_key);

CREATE INDEX idx_fact_generation_geography
ON fact_generation(geography_key);

CREATE INDEX idx_fact_generation_energy
ON fact_generation(energy_source_key);

CREATE INDEX idx_fact_demand_time
ON fact_demand(time_key);

CREATE INDEX idx_fact_demand_geography
ON fact_demand(geography_key);