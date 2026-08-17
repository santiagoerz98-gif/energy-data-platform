# Energy Data Platform

A data engineering project that ingests electricity data from the Spanish energy market API, transforms it, validates it, and loads it into a PostgreSQL analytical warehouse. The project is designed to demonstrate an end-to-end ETL workflow, data modeling, orchestration, API exposure, and dashboarding.

## Overview

This project extracts electricity market indicators from the ESIOS API managed by Red Eléctrica de España, stores raw responses, applies transformation and quality rules, and loads structured data into a star schema warehouse for analytical consumption.

The solution is built around a modular ETL pipeline with:

- Python-based extraction and transformation
- Data quality validation
- PostgreSQL warehouse and staging schemas
- Prefect orchestration
- FastAPI service for querying the warehouse
- Streamlit dashboard for exploration and visualization

## Business Problem

Energy consumption and generation data are highly time-dependent and require pipeline reliability, schema consistency, and quality checks. This project addresses that by automating data collection and organizing the data into a warehouse-ready structure for analytical queries and operational reporting.

## Architecture

```mermaid
flowchart LR
    A[ESIOS API] --> B[Extract]
    B --> C[Transform]
    C --> D[Quality Validation]
    D --> E[PostgreSQL Staging]
    E --> F[Warehouse / DW Schema]
    F --> G[FastAPI]
    F --> H[Streamlit Dashboard]
```

## Stack tecnologico actual

- Python 3.11+
- Prefect
- FastAPI
- Stremlit
- Pandas
- Requests
- SQLAlchemy
- PostgreSQL
- Docker Compose

## Features

- Extraction of energy indicators by date range and geography
- Raw data persistence for traceability
- Data cleaning and standardization
- Quality reporting and validation
- Staging load for operational data
- Analytical DW schema with star-model tables
- API endpoints for demand and generation data
- Dashboard to explore trends and compare indicators

## Project Structure

```text
energy-data-platform/
├── api/
│   ├── crud.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
├── app/
│   ├── app.py
│   ├── app_services/
│   └── components/
├── config/
│   ├── database.py
│   ├── ids_catalog.py
│   ├── logging_config.py
│   └── settings.py
├── database/
│   ├── populate_dw.sql
│   └── schema.sql
├── data/
│   ├── raw/
│   └── processed/
├── docs/
├── pipeline/
│   ├── flows/
│   ├── tasks/
│   ├── extract.py
│   ├── load.py
│   ├── quality.py
│   ├── run_pipeline.py
│   └── transform.py
├── services/
│   ├── catalog_generator.py
│   ├── esios_client.py
│   └── id_selector.py
├── tests/
├── .env.example
├── docker-compose.yaml
├── prefect.yaml
├── requirements.txt
├── README.md
└── LICENSE.txt
```

## Requisitos previos

Before running the project, ensure you have:

- Python 3.11 or newer
- PostgreSQL available locally or via Docker
- Access to the ESIOS API with a valid API key
- Git
- Docker Desktop for local database provisioning

## Quick Start (Windows PowerShell)

1. Clone repository

```powershell
git clone https://github.com/santiagoerz98-gif/energy-data-platform.git
cd energy-data-platform
```

2. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies

```powershell
pip install -r requirements.txt
```

4. Configure environment variables
   Create a .env file in the project root:

```text
ESIOS_API_KEY=your_esios_api_key
DATABASE_URL=postgresql+psycopg://energy_user:energy_password@localhost:5432/energy_dw
LOG_LEVEL=INFO
```

5. Start the full stack with Docker
   This command starts all required services in one shot:

```powershell
docker compose up -d --build
```

The stack includes:

- PostgreSQL
- Prefect Server
- Prefect Worker
- FastAPI service
- Streamlit dashboard

6.  Check that the services are running

```powershell
docker compose ps
```

You should be able to access:

- Prefect UI: http://localhost:4200
- FastAPI docs: http://localhost:8000/docs
- Streamlit app: http://localhost:8501

7. Populate the warehouse

Run the Prefect deployment to load data into the database:

```bash
prefect deployment run 'datos-peninsulares'
```

This is the recommended way to ingest the data into PostgreSQL. If no dates are given, the pipeline uses its default range automatically. For a specific month, pass the dates explicitly:
prefect deployment run 'datos-peninsulares' \
 --param start_date=2026-07-01 \
 --param end_date=2026-07-31

## Data Model

The warehouse follows a dimensional model with star-schema patterns:

- `code dw.dim_time`
- `dw.dim_geography`
- `dw.dim_energy_source`
- `dw.fact_demand`
- `dw.fact_generation`

## Quality and Reliability

The project includes:

- raw data storage
- transformation validation
- quality reports
- logging for ETL stages
- retry configuration for API requests
- idempotent staging loads based on indicator and date range

## Known Limitations

This project is a strong data engineering MVP, but it still has room for improvement:

- more complete CI/CD automation
- improved deployment orchestration and scheduling
- broader dataset coverage
- richer dashboard interactions
- production-ready environment variable management
