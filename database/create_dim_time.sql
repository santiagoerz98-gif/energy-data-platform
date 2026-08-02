-- Asegurar que el esquema final existe (ej. dw)
CREATE SCHEMA IF NOT EXISTS dw;

-- Crear la tabla dim_time
CREATE TABLE IF NOT EXISTS dw.dim_time (
    date_key INT PRIMARY KEY,         -- Formato YYYYMMDD (Ej: 20260601)
    date_actual DATE NOT NULL,        -- Fecha real (Ej: 2026-06-01)
    year INT NOT NULL,                -- Año (Ej: 2026)
    quarter INT NOT NULL,             -- Trimestre (1 a 4)
    month INT NOT NULL,               -- Mes numérico (1 a 12)
    month_name VARCHAR(20) NOT NULL,    -- Nombre del mes (Ej: June / Junio)
    day INT NOT NULL,                 -- Día del mes (1 a 31)
    day_of_week INT NOT NULL,         -- Día de la semana (0 o 1 hasta 6/7)
    day_name VARCHAR(20) NOT NULL,    -- Nombre del día (Ej: Monday / Lunes)
    is_weekend BOOLEAN NOT NULL       -- Si es fin de semana (True/False)
);

COMMENT ON TABLE dw.dim_time IS 'Tabla de dimensiones de tiempo para análisis temporal. Contiene información detallada sobre cada fecha.'

INSERT INTO dw.dim_time (
    date_key, 
    date_actual, 
    year, 
    quarter, 
    month, 
    month_name, 
    day, 
    day_of_week, 
    day_name, 
    is_weekend
)
SELECT 
    TO_CHAR(d, 'YYYYMMDD')::INT AS date_key,
    d::DATE AS date_actual,
    EXTRACT(YEAR FROM d)::INT AS year,
    EXTRACT(QUARTER FROM d)::INT AS quarter,
    EXTRACT(MONTH FROM d)::INT AS month,
    TO_CHAR(d, 'TMMonth') AS month_name, -- Nombre del mes
    EXTRACT(DAY FROM d)::INT AS day,
    EXTRACT(ISODOW FROM d)::INT AS day_of_week, -- 1 (Lunes) al 7 (Domingo)
    TO_CHAR(d, 'TMDay') AS day_name,     -- Nombre del día
    CASE 
        WHEN EXTRACT(ISODOW FROM d) IN (6, 7) THEN TRUE 
        ELSE FALSE 
    END AS is_weekend
FROM 
    generate_series('2026-01-01'::DATE, '2030-12-31'::DATE, INTERVAL '1 day') t(d)
ON CONFLICT (date_key) DO NOTHING; -- Evita duplicados si corres el script varias veces

SELECT * FROM dw.dim_time ORDER BY date_key LIMIT 10; -- Verificar los primeros registros insertados