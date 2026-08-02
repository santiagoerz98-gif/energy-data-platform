-- Poblar dim_geography
INSERT INTO dw.dim_geography(
    geo_id,
    geo_name,
)
SELECT DISTINCT
    geo_id,
    geo_name
FROM staging.staging_demand
ON CONFLICT (geo_id) DO NOTHING; -- Evita duplicados si corres el script varias veces   

-- Poblar dim_energy_source
INSERT INTO dw.dim_energy_source(
    technology_name,
    renewable
)
SELECT DISTINCT
    short_name,
    CASE 
        WHEN short_name IN ('Hidráulica', 'Eólica', 'Solar', 'Solar térmica', 'Solar fotovoltaica', 'Térmica renovable', 'Renovable') THEN TRUE
        ELSE FALSE 
    END
FROM staging.staging_generation
ON CONFLICT (technology_name) DO NOTHING; -- Evita duplicados si corres el script varias veces

-- fact_demand
INSERT INTO dw.fact_demand (
    time_key, 
    geography_key, 
    demand_mwh, 
    measurement_type
)
SELECT 
    t.date_key,             -- Viene de dim_time (ej: 20260601)
    g.geography_key,        -- La clave subrogada obtenida mediante el JOIN
    s.value,       -- La métrica numérica de staging
    s.measurement_type  -- Atributo descriptivo de la demanda
FROM staging.demand s
-- JOIN con la dimensión de tiempo usando la fecha para mapear el date_key
JOIN dw.dim_time t ON s.datetime_utc::DATE = t.date_actual
-- JOIN con la dimensión de geografía usando el ID natural
JOIN dw.dim_geography g ON s.geo_id = g.geo_id;

--- fact_generation
INSERT INTO dw.fact_generation (
    time_key, 
    geography_key, 
    energy_source_key, 
    generation_mwh
)
SELECT 
    t.date_key,
    g.geography_key,
    e.energy_source_key,    -- Clave subrogada de la fuente de energía
    s.value
FROM staging.generation s
-- JOIN con Tiempo
JOIN dw.dim_time t ON s.datetime_utc::DATE = t.date_actual
-- JOIN con Geografía
JOIN dw.dim_geography g ON s.geo_id = g.geo_id
-- JOIN con Fuente de Energía
JOIN dw.dim_energy_source e ON s.short_name = e.technology_name;