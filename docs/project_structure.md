# Estructura del Proyecto

## 1. Vision general

Este documento describe la organizacion del repositorio y la responsabilidad de cada carpeta.

## 2. Carpetas principales

## `api/`

- Estado actual: carpeta reservada para roadmap.
- Objetivo futuro: servicios FastAPI para exposicion de datos.

## `app/`

- Estado actual: carpeta reservada para roadmap.
- Objetivo futuro: dashboard de analitica.

## `config/`

- `database.py`: engine/conexion de SQLAlchemy.
- `ids_catalog.py`: catalogo maestro de indicadores.
- `settings.py`: configuraciones generales.

## `data/`

- `raw/`: respuestas originales de ESIOS.
- `raw/processed/reports/`: reportes de calidad.

## `database/`

- `schema.sql`: DDL del esquema `dw` y `staging`, incluye creacion/carga de `dw.dim_time`.
- `populate_dw.sql`: script de carga analitica desde staging.
- `docker-compose.yml`: soporte local para PostgreSQL.

## `docs/`

Documentacion funcional, tecnica y operativa del proyecto.

## `notebooks/`

Exploracion y analisis ad hoc.

## `pipeline/`

- `run_pipeline.py`: punto de entrada CLI.
- `extract.py`: extraccion de API ESIOS.
- `transform.py`: transformaciones y limpieza.
- `quality.py`: validaciones de calidad.
- `load.py`: carga en base de datos.

## `services/`

- `esios_client.py`: cliente HTTP de ESIOS.
- `catalog_generator.py`: utilidades para catalogos.
- `id_selector.py`: soporte para seleccion de indicadores.

## `tests/`

Pruebas unitarias y scripts de validacion para pipeline y servicios.

## 3. Flujo entre carpetas

1. `services/` consume API.
2. `pipeline/` ejecuta ETL.
3. `data/` guarda raw y reportes.
4. `database/` define modelo SQL.
5. `docs/` describe operacion y arquitectura.

## 4. Convenciones operativas

- Ejecucion principal por CLI: `python -m pipeline.run_pipeline ...`
- Carga operativa en schema `staging`.
- Capa analitica final en schema `dw`.
