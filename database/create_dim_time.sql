-- Asegurar que el esquema final existe (ej. dw)
CREATE SCHEMA IF NOT EXISTS dw;

-- Crear la tabla dim_time
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

COMMENT ON TABLE dw.dim_time IS 'Tabla de dimensiones de tiempo para análisis temporal. Contiene información detallada sobre cada fecha.';

INSERT INTO dw.dim_time (
    time_key,
    datetime_utc,
    date_actual,
    year,
    quarter,
    month,
    month_name,
    day,
    hour,
    day_of_week,
    day_name,
    is_weekend
)
SELECT
    TO_CHAR(ts, 'YYYYMMDDHH24')::BIGINT AS time_key,
    ts::timestamp AS datetime_utc,
    ts::date AS date_actual,
    EXTRACT(YEAR FROM ts)::INT AS year,
    EXTRACT(QUARTER FROM ts)::INT AS quarter,
    EXTRACT(MONTH FROM ts)::INT AS month,
    TO_CHAR(ts, 'TMMonth') AS month_name,
    EXTRACT(DAY FROM ts)::INT AS day,
    EXTRACT(HOUR FROM ts)::INT AS hour,
    EXTRACT(ISODOW FROM ts)::INT AS day_of_week,
    TO_CHAR(ts, 'TMDay') AS day_name,
    CASE WHEN EXTRACT(ISODOW FROM ts) IN (6, 7) THEN TRUE ELSE FALSE END AS is_weekend
FROM generate_series(
    '2026-01-01 00:00:00'::timestamp,
    '2030-12-31 23:00:00'::timestamp,
    INTERVAL '1 hour'
) AS g(ts)
ON CONFLICT (time_key) DO NOTHING; -- Evita duplicados si corres el script varias veces

SELECT * FROM dw.dim_time ORDER BY time_key LIMIT 10; -- Verificar los primeros registros insertados