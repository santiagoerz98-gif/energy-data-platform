BEGIN;

-- 1) Quitar FKs temporales hacia dim_time
ALTER TABLE dw.fact_demand DROP CONSTRAINT IF EXISTS fk_demand_time;
ALTER TABLE dw.fact_generation DROP CONSTRAINT IF EXISTS fk_generation_time;

-- 2) Cambiar tipo de time_key en hechos a BIGINT (YYYYMMDDHH)
ALTER TABLE dw.fact_demand
    ALTER COLUMN time_key TYPE BIGINT USING time_key::BIGINT;

ALTER TABLE dw.fact_generation
    ALTER COLUMN time_key TYPE BIGINT USING time_key::BIGINT;

-- 3) Agregar indicator_id a hechos para evitar mezclar series
ALTER TABLE dw.fact_demand
    ADD COLUMN IF NOT EXISTS indicator_id INTEGER;

ALTER TABLE dw.fact_generation
    ADD COLUMN IF NOT EXISTS indicator_id INTEGER;

-- 4) Reemplazar dim_time diaria por dim_time horaria
DROP TABLE IF EXISTS dw.dim_time;

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

COMMIT;

TRUNCATE TABLE dw.fact_demand;
TRUNCATE TABLE dw.fact_generation;

BEGIN;

-- FKs a dim_time horaria
ALTER TABLE dw.fact_demand
    ADD CONSTRAINT fk_demand_time
    FOREIGN KEY (time_key)
    REFERENCES dw.dim_time(time_key);

ALTER TABLE dw.fact_generation
    ADD CONSTRAINT fk_generation_time
    FOREIGN KEY (time_key)
    REFERENCES dw.dim_time(time_key);

-- Índices de unicidad natural para evitar duplicados por rerun
CREATE UNIQUE INDEX IF NOT EXISTS uq_fact_demand_natural
ON dw.fact_demand (time_key, geography_key, measurement_type, indicator_id);

CREATE UNIQUE INDEX IF NOT EXISTS uq_fact_generation_natural
ON dw.fact_generation (time_key, geography_key, energy_source_key, indicator_id);

COMMIT;

ROLLBACK;

