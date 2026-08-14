# Energy Data Platform

Plataforma de ingenieria de datos para extraer, transformar y cargar informacion del sistema electrico español desde la API de ESIOS hacia PostgreSQL, usando un pipeline ETL modular en Python.

## Estado del proyecto

- Implementado: pipeline ETL (extract, transform, quality, load), almacenamiento raw, carga a schema `staging`, esquema analitico `dw`.
- Planificado: API REST en `api/` y dashboard en `app/`.

## Stack tecnologico actual

- Python 3.11+
- Pandas
- Requests
- SQLAlchemy
- Psycopg
- PostgreSQL
- Pytest

## Estructura principal

- `pipeline/`: flujo ETL principal (`run_pipeline.py`, `extract.py`, `transform.py`, `quality.py`, `load.py`).
- `services/`: cliente ESIOS y utilidades de catalogo.
- `config/`: configuracion de DB y catalogo de IDs (`ids_catalog.py`).
- `database/`: scripts SQL para esquema DW y poblacion inicial de `dim_time`.
- `data/`: capas `raw` y `processed` con respuestas y reportes.
- `tests/`: pruebas unitarias y scripts de validacion.
- `docs/`: documentacion funcional y tecnica.

## Requisitos previos

- Python 3.11 o superior
- PostgreSQL operativo
- API key de ESIOS

## Instalacion rapida (Windows PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Configuracion

Crear archivo `.env` en la raiz del proyecto con:

```env
ESIOS_API_KEY=tu_api_key
DATABASE_URL=postgresql+psycopg://usuario:password@localhost:5432/energy_dw
```

## Inicializacion de base de datos

Ejecutar scripts SQL en este orden:

1. `database/schema.sql`

Opcional para carga analitica desde staging:

2. `database/populate_dw.sql`

## Ejecucion del pipeline

Ejemplo con indicador de demanda real:

```powershell
python -m pipeline.run_pipeline 1293 --start-date 2026-07-01 --end-date 2026-07-31
```

Parametros CLI disponibles:

- `indicator_id` (obligatorio)
- `--start-date`
- `--end-date`
- `--time-trunc`
- `--geo-ids`

## Pruebas

Ejecucion recomendada:

```powershell
pytest tests -v
```

Nota: en `tests/` conviven pruebas unitarias y algunos scripts de validacion manual.

## Documentacion

- `docs/solution_architecture.md`: arquitectura de solucion y estado implementado vs roadmap.
- `docs/source_system_assesment.md`: evaluacion del sistema fuente ESIOS.
- `docs/api_analysis.md`: analisis de API y estrategia de indicadores.
- `docs/dimensional_model.md`: entidades y modelo conceptual.
- `docs/star_schema.md`: modelo estrella y esquema fisico.
- `docs/setup_guide.md`: guia detallada de instalacion y configuracion.
- `docs/pipeline_execution_guide.md`: ejecucion operativa del pipeline.
- `docs/implementation_status.md`: estado de implementacion por componente.
- `docs/project_structure.md`: mapa detallado del repositorio.
