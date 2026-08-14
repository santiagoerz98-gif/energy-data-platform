# Solution Architecture

## Proyecto: Energy Data Platform

**Version:** 1.1  
**Autor:** Santiago Rodriguez  
**Fecha:** Agosto 2026

---

# 1. Objetivo

Definir la arquitectura funcional y tecnica del estado actual del proyecto, separando claramente:

- componentes implementados en el MVP operativo;
- componentes planificados para fases posteriores.

---

# 2. Alcance actual

## Implementado

- Extraccion desde API ESIOS.
- Almacenamiento Raw en archivos JSON.
- Transformacion y limpieza con Pandas.
- Validacion de calidad.
- Carga a PostgreSQL schema `staging`.
- Esquema analitico `dw` definido en SQL.

## Planificado

- API REST (carpeta `api/`).
- Dashboard (carpeta `app/`).

---

# 3. Arquitectura general

## 3.1 Flujo implementado

```text
API ESIOS
       |
       v
Extract (pipeline/extract.py)
       |
       v
Raw Layer (data/raw/esios/...)
       |
       v
Transform (pipeline/transform.py)
       |
       v
Quality (pipeline/quality.py)
       |
       v
Load (pipeline/load.py)
       |
       v
PostgreSQL staging (schema staging)
       |
       v
Data Warehouse (schema dw)
```

## 3.2 Flujo planificado

```text
Data Warehouse (schema dw)
       |
       +--> FastAPI REST API (api/) [PLANIFICADO]
       |
       +--> Streamlit Dashboard (app/) [PLANIFICADO]
```

---

# 4. Componentes

## 4.1 Sistema fuente (ESIOS)

- Tipo: API REST (JSON sobre HTTPS)
- Funcion: fuente oficial de indicadores electricos

## 4.2 Extract Module

- Archivo: `pipeline/extract.py`
- Funcion: consumir API ESIOS y persistir JSON raw

## 4.3 Raw Layer

- Ruta: `data/raw/esios/`
- Funcion: conservar evidencia original para auditoria y reprocesado

## 4.4 Transform Module

- Archivo: `pipeline/transform.py`
- Funcion: normalizar, tipificar y limpiar datos

## 4.5 Quality Module

- Archivo: `pipeline/quality.py`
- Funcion: validar calidad y generar reportes

## 4.6 Load Module

- Archivo: `pipeline/load.py`
- Funcion: cargar dataframes a tablas del schema `staging`

## 4.7 Data Warehouse

- Scripts: `database/schema.sql`
- Funcion: modelo dimensional analitico en schema `dw`

## 4.8 API REST (Roadmap)

- Carpeta: `api/`
- Estado: no implementado
- Objetivo futuro: exponer datos de `dw` para consumo externo

## 4.9 Dashboard (Roadmap)

- Carpeta: `app/`
- Estado: no implementado
- Objetivo futuro: visualizacion de KPI y tendencias

---

# 5. Capas de datos

## Raw

- Datos JSON sin transformar.

## Processed

- Dataset transformado y validado para carga.

## Staging (PostgreSQL)

- Capa operativa de aterrizaje (`staging.demand`, `staging.generation`).

## DW (PostgreSQL)

- Capa analitica dimensional (`dw.fact_*`, `dw.dim_*`).

---

# 6. Comunicacion entre componentes

| Origen    | Destino            | Medio        |
| --------- | ------------------ | ------------ |
| ESIOS API | Extract            | HTTP         |
| Extract   | Raw Layer          | JSON         |
| Raw Layer | Transform          | archivo JSON |
| Transform | Quality            | DataFrame    |
| Quality   | Load               | DataFrame    |
| Load      | PostgreSQL staging | SQLAlchemy   |
| Staging   | DW                 | SQL          |

---

# 7. Punto de entrada del pipeline

- Archivo: `pipeline/run_pipeline.py`
- Funcion principal: `run_pipeline(...)`
- CLI:

```text
python -m pipeline.run_pipeline <indicator_id> [--start-date ...] [--end-date ...] [--time-trunc ...] [--geo-ids ...]
```

---

# 8. Gestion de errores

## Estado actual

- El pipeline registra eventos por modulo.
- La validacion de calidad puede detener la ejecucion cuando se incumplen reglas.

## Roadmap

- Reintentos automaticos para errores transitorios de API.
- Notificaciones operativas.

---

# 9. Decisiones de arquitectura

- Arquitectura modular para bajo acoplamiento.
- Persistencia raw para trazabilidad.
- Capa `staging` intermedia antes de `dw`.
- Separacion entre capacidades operativas (ETL) y de consumo (API/dashboard) para evolucion por fases.

---

# 10. Referencias

- `README.md`
- `docs/source_system_assesment.md`
- `docs/star_schema.md`
- `docs/implementation_status.md`
