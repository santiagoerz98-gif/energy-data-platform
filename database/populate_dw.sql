-- =====================================================
-- Energy Data Platform
-- Populate DW from staging (idempotente + validaciones)
-- =====================================================

BEGIN;

-- -----------------------------------------------------
-- 0) Validaciones de precondición
-- -----------------------------------------------------
DO $$
DECLARE
    v_demand_count BIGINT;
    v_generation_count BIGINT;
    v_missing_time_demand BIGINT;
    v_missing_time_generation BIGINT;
    v_invalid_demand BIGINT;
    v_invalid_generation BIGINT;
BEGIN
    -- Verificar que haya datos de entrada
    SELECT COUNT(*) INTO v_demand_count FROM staging.demand;
    SELECT COUNT(*) INTO v_generation_count FROM staging.generation;

    IF v_demand_count = 0 AND v_generation_count = 0 THEN
        RAISE EXCEPTION 'No hay datos en staging.demand ni staging.generation';
    END IF;

    -- Validar columnas críticas demand
    SELECT COUNT(*) INTO v_invalid_demand
    FROM staging.demand
    WHERE datetime_utc IS NULL
       OR geo_id IS NULL
       OR value IS NULL
       OR value < 0
       OR measurement_type IS NULL;

    IF v_invalid_demand > 0 THEN
        RAISE EXCEPTION 'staging.demand contiene % filas inválidas (datetime_utc/geo_id/value/measurement_type)', v_invalid_demand;
    END IF;

    -- Validar columnas críticas generation
    SELECT COUNT(*) INTO v_invalid_generation
    FROM staging.generation
    WHERE datetime_utc IS NULL
       OR geo_id IS NULL
       OR value IS NULL
       OR value < 0
       OR short_name IS NULL;

    IF v_invalid_generation > 0 THEN
        RAISE EXCEPTION 'staging.generation contiene % filas inválidas (datetime_utc/geo_id/value/short_name)', v_invalid_generation;
    END IF;

    -- Validar cobertura de dim_time para demand
    SELECT COUNT(*) INTO v_missing_time_demand
    FROM (
        SELECT DISTINCT s.datetime_utc::date AS d
        FROM staging.demand s
    ) src
    LEFT JOIN dw.dim_time t
        ON t.date_actual = src.d
    WHERE t.time_key IS NULL;

    IF v_missing_time_demand > 0 THEN
        RAISE EXCEPTION 'Faltan % fechas en dw.dim_time para datos de demanda', v_missing_time_demand;
    END IF;

    -- Validar cobertura de dim_time para generation
    SELECT COUNT(*) INTO v_missing_time_generation
    FROM (
        SELECT DISTINCT s.datetime_utc::date AS d
        FROM staging.generation s
    ) src
    LEFT JOIN dw.dim_time t
        ON t.date_actual = src.d
    WHERE t.time_key IS NULL;

    IF v_missing_time_generation > 0 THEN
        RAISE EXCEPTION 'Faltan % fechas en dw.dim_time para datos de generación', v_missing_time_generation;
    END IF;
END $$;

-- -----------------------------------------------------
-- 1) Sincronización de dimensiones (idempotente)
-- -----------------------------------------------------

-- 1.1 dim_geography desde demand + generation
INSERT INTO dw.dim_geography (geo_id, geo_name)
SELECT DISTINCT geo_id, geo_name
FROM (
    SELECT geo_id, geo_name
    FROM staging.demand
    WHERE geo_id IS NOT NULL AND geo_name IS NOT NULL

    UNION

    SELECT geo_id, geo_name
    FROM staging.generation
    WHERE geo_id IS NOT NULL AND geo_name IS NOT NULL
) g
ON CONFLICT (geo_id) DO UPDATE
SET geo_name = EXCLUDED.geo_name
WHERE dw.dim_geography.geo_name IS DISTINCT FROM EXCLUDED.geo_name;

-- 1.2 dim_energy_source desde generation
INSERT INTO dw.dim_energy_source (technology_name, renewable)
SELECT DISTINCT
    s.short_name AS technology_name,
    CASE
        WHEN s.short_name IN (
            'Hidráulica',
            'Eólica',
            'Solar',
            'Solar térmica',
            'Solar fotovoltaica',
            'Térmica renovable',
            'Renovable'
        ) THEN TRUE
        ELSE FALSE
    END AS renewable
FROM staging.generation s
WHERE s.short_name IS NOT NULL
ON CONFLICT (technology_name) DO UPDATE
SET renewable = EXCLUDED.renewable
WHERE dw.dim_energy_source.renewable IS DISTINCT FROM EXCLUDED.renewable;

-- -----------------------------------------------------
-- 2) Validación de mapeos dimensionales
-- -----------------------------------------------------
DO $$
DECLARE
    v_unmapped_geo_demand BIGINT;
    v_unmapped_geo_generation BIGINT;
    v_unmapped_energy BIGINT;
BEGIN
    SELECT COUNT(*) INTO v_unmapped_geo_demand
    FROM (
        SELECT DISTINCT s.geo_id
        FROM staging.demand s
    ) d
    LEFT JOIN dw.dim_geography g
        ON g.geo_id = d.geo_id
    WHERE g.geography_key IS NULL;

    IF v_unmapped_geo_demand > 0 THEN
        RAISE EXCEPTION 'Existen % geo_id de demanda sin mapeo en dim_geography', v_unmapped_geo_demand;
    END IF;

    SELECT COUNT(*) INTO v_unmapped_geo_generation
    FROM (
        SELECT DISTINCT s.geo_id
        FROM staging.generation s
    ) d
    LEFT JOIN dw.dim_geography g
        ON g.geo_id = d.geo_id
    WHERE g.geography_key IS NULL;

    IF v_unmapped_geo_generation > 0 THEN
        RAISE EXCEPTION 'Existen % geo_id de generación sin mapeo en dim_geography', v_unmapped_geo_generation;
    END IF;

    SELECT COUNT(*) INTO v_unmapped_energy
    FROM (
        SELECT DISTINCT s.short_name
        FROM staging.generation s
    ) d
    LEFT JOIN dw.dim_energy_source e
        ON e.technology_name = d.short_name
    WHERE e.energy_source_key IS NULL;

    IF v_unmapped_energy > 0 THEN
        RAISE EXCEPTION 'Existen % tecnologías sin mapeo en dim_energy_source', v_unmapped_energy;
    END IF;
END $$;

-- -----------------------------------------------------
-- 3) Carga idempotente de hechos
--    Estrategia: DELETE por clave natural entrante + INSERT
-- -----------------------------------------------------

-- 3.1 fact_demand
WITH demand_src AS (
    SELECT DISTINCT ON (t.time_key, g.geography_key, s.measurement_type, s.indicator_id)
        t.time_key,
        g.geography_key,
        s.value::numeric(12,3) AS demand_mwh,
        s.measurement_type,
        s.indicator_id
    FROM staging.demand s
    JOIN dw.dim_time t
      ON date_trunc('hour', s.datetime_utc::timestamp) = t.datetime_utc
    JOIN dw.dim_geography g
      ON s.geo_id = g.geo_id
    WHERE s.value >= 0
    ORDER BY
      t.time_key, g.geography_key, s.measurement_type, s.indicator_id, s.datetime_utc DESC
),
deleted AS (
    DELETE FROM dw.fact_demand f
    USING demand_src d
    WHERE f.time_key = d.time_key
      AND f.geography_key = d.geography_key
      AND f.measurement_type = d.measurement_type
      AND f.indicator_id = d.indicator_id
    RETURNING f.demand_key
)
INSERT INTO dw.fact_demand (
    time_key,
    geography_key,
    demand_mwh,
    measurement_type,
    indicator_id
)
SELECT
    d.time_key,
    d.geography_key,
    d.demand_mwh,
    d.measurement_type,
    d.indicator_id
FROM demand_src d;

-- 3.2 fact_generation
WITH generation_src AS (
    SELECT DISTINCT ON (t.time_key, g.geography_key, e.energy_source_key, s.indicator_id)
        t.time_key,
        g.geography_key,
        e.energy_source_key,
        s.value::numeric(12,3) AS generation_mwh,
        s.indicator_id
    FROM staging.generation s
    JOIN dw.dim_time t
      ON date_trunc('hour', s.datetime_utc::timestamp) = t.datetime_utc
    JOIN dw.dim_geography g
      ON s.geo_id = g.geo_id
    JOIN dw.dim_energy_source e
      ON s.short_name = e.technology_name
    WHERE s.value >= 0
    ORDER BY
      t.time_key, g.geography_key, e.energy_source_key, s.indicator_id, s.datetime_utc DESC
),
deleted AS (
    DELETE FROM dw.fact_generation f
    USING generation_src gsrc
    WHERE f.time_key = gsrc.time_key
      AND f.geography_key = gsrc.geography_key
      AND f.energy_source_key = gsrc.energy_source_key
      AND f.indicator_id = gsrc.indicator_id
    RETURNING f.generation_key
)
INSERT INTO dw.fact_generation (
    time_key,
    geography_key,
    energy_source_key,
    generation_mwh,
    indicator_id
)
SELECT
    gsrc.time_key,
    gsrc.geography_key,
    gsrc.energy_source_key,
    gsrc.generation_mwh,
    gsrc.indicator_id
FROM generation_src gsrc;

-- -----------------------------------------------------
-- 4) Validaciones post-carga
-- -----------------------------------------------------
DO $$
DECLARE
    v_dup_demand BIGINT;
    v_dup_generation BIGINT;
    v_neg_demand BIGINT;
    v_neg_generation BIGINT;
BEGIN
    -- Duplicados por clave natural
    SELECT COUNT(*) INTO v_dup_demand
    FROM (
        SELECT time_key, geography_key, measurement_type, indicator_id, COUNT(*)
        FROM dw.fact_demand
        GROUP BY 1,2,3,4
        HAVING COUNT(*) > 1
    ) x;

    IF v_dup_demand > 0 THEN
        RAISE EXCEPTION 'Se detectaron % grupos duplicados en dw.fact_demand', v_dup_demand;
    END IF;

    SELECT COUNT(*) INTO v_dup_generation
    FROM (
        SELECT time_key, geography_key, energy_source_key, COUNT(*)
        FROM dw.fact_generation
        GROUP BY 1,2,3
        HAVING COUNT(*) > 1
    ) x;

    IF v_dup_generation > 0 THEN
        RAISE EXCEPTION 'Se detectaron % grupos duplicados en dw.fact_generation', v_dup_generation;
    END IF;

    -- No negativos
    SELECT COUNT(*) INTO v_neg_demand
    FROM dw.fact_demand
    WHERE demand_mwh < 0;

    IF v_neg_demand > 0 THEN
        RAISE EXCEPTION 'Se detectaron % filas negativas en dw.fact_demand', v_neg_demand;
    END IF;

    SELECT COUNT(*) INTO v_neg_generation
    FROM dw.fact_generation
    WHERE generation_mwh < 0;

    IF v_neg_generation > 0 THEN
        RAISE EXCEPTION 'Se detectaron % filas negativas en dw.fact_generation', v_neg_generation;
    END IF;
END $$;

-- -----------------------------------------------------
-- 5) Limpiar staging despues de carga exitosa al Data Warehouse
-- -----------------------------------------------------

TRUNCATE TABLE staging.demand;
TRUNCATE TABLE staging.generation;

COMMIT;


-- SELECT COUNT(*) AS dim_geo_rows FROM dw.dim_geography;
-- SELECT COUNT(*) AS dim_energy_rows FROM dw.dim_energy_source;
-- SELECT COUNT(*) AS fact_demand_rows FROM dw.fact_demand;
-- SELECT COUNT(*) AS fact_generation_rows FROM dw.fact_generation;