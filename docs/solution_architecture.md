# Solution Architecture

## Proyecto: Energy Data Platform

**Versión:** 1.0

**Autor:** Santiago Rodríguez

**Fecha:** Julio 2026

---

# 1. Objetivo

Este documento describe la arquitectura funcional y técnica del proyecto **Energy Data Platform**.

Su propósito es definir cómo fluyen los datos desde el sistema fuente hasta la aplicación utilizada por el usuario final, identificando los componentes, responsabilidades e interacciones del sistema.

Este documento servirá como guía para el desarrollo del MVP y facilitará la evolución futura de la plataforma.

---

# 2. Contexto

La empresa desea disponer de una plataforma que permita consultar información histórica y actual del sistema eléctrico español sin depender directamente de la API pública de ESIOS.

Actualmente cada aplicación consume la API de forma independiente, lo que genera varios problemas:

- llamadas repetidas a la API;
- ausencia de almacenamiento histórico;
- lógica duplicada en diferentes aplicaciones;
- tiempos de respuesta elevados;
- dificultad para realizar análisis históricos.

La solución propuesta consiste en construir una plataforma centralizada de datos.

---

# 3. Objetivos de arquitectura

La arquitectura deberá cumplir los siguientes objetivos.

### Funcionales

- Extraer información desde ESIOS.
- Almacenar datos históricos.
- Transformar los datos para análisis.
- Validar la calidad antes de almacenarlos.
- Exponer la información mediante una API.
- Permitir la visualización mediante un dashboard.

---

### No funcionales

- Modularidad.
- Bajo acoplamiento.
- Escalabilidad.
- Mantenibilidad.
- Reutilización.
- Facilidad para añadir nuevos indicadores.

---

# 4. Arquitectura general

```
                    +----------------------+
                    |     API ESIOS        |
                    +----------+-----------+
                               |
                               |
                     HTTP Requests (JSON)
                               |
                               ▼
                    +----------------------+
                    |  Extract Module      |
                    |   extract.py         |
                    +----------+-----------+
                               |
                               |
                     Raw JSON Storage
                               |
                               ▼
                    +----------------------+
                    |   Raw Layer          |
                    | data/raw/            |
                    +----------+-----------+
                               |
                               |
                               ▼
                    +----------------------+
                    | Transform Module     |
                    | transform.py         |
                    +----------+-----------+
                               |
                               |
                               ▼
                    +----------------------+
                    | Quality Module       |
                    | quality.py           |
                    +----------+-----------+
                               |
                     Validated Data
                               |
                               ▼
                    +----------------------+
                    | Load Module          |
                    | load.py              |
                    +----------+-----------+
                               |
                               |
                               ▼
                    +----------------------+
                    | PostgreSQL           |
                    | Data Warehouse       |
                    +----------+-----------+
                               |
                               |
                    SQL Queries
                               |
                 +-------------+--------------+
                 |                            |
                 ▼                            ▼
       +-------------------+       +------------------+
       | FastAPI           |       | Streamlit        |
       | REST API          |       | Dashboard        |
       +-------------------+       +------------------+
```

---

# 5. Componentes de la solución

La plataforma estará formada por siete componentes principales.

## 5.1 Sistema fuente

Responsabilidad

Proporcionar los datos oficiales del sistema eléctrico español.

Tecnología

- API REST
- JSON

Entrada

Ninguna.

Salida

JSON.

---

## 5.2 Extract Module

Responsabilidad

Consumir la API.

Funciones

- autenticación;
- llamadas HTTP;
- control de errores;
- almacenamiento Raw.

Entradas

API ESIOS.

Salidas

Archivos JSON.

---

## 5.3 Raw Layer

Responsabilidad

Conservar una copia exacta de la información recibida.

Beneficios

- auditoría;
- trazabilidad;
- reprocesamiento;
- recuperación.

Formato

JSON.

---

## 5.4 Transformation Module

Responsabilidad

Convertir los datos Raw en información estructurada.

Funciones

- limpieza;
- renombrado;
- conversión de tipos;
- cálculo de métricas;
- separación de dimensiones.

Salida

DataFrames preparados para carga.

---

## 5.5 Quality Module

Responsabilidad

Verificar la calidad antes de almacenar.

Reglas

- sin duplicados;
- sin fechas vacías;
- sin valores negativos;
- tipos correctos;
- tecnologías válidas.

Salida

Informe de calidad.

---

## 5.6 Load Module

Responsabilidad

Persistir la información.

Funciones

- insertar dimensiones;
- insertar hechos;
- UPSERT;
- transacciones.

Destino

PostgreSQL.

---

## 5.7 Data Warehouse

Responsabilidad

Almacenar los datos históricos.

Modelo

Esquema en estrella.

Tablas

- fact_generation
- fact_demand
- dim_time
- dim_energy_source

---

## 5.8 API REST

Responsabilidad

Proporcionar acceso a los datos.

Beneficios

- desacoplamiento;
- reutilización;
- integración.

Tecnología

FastAPI.

---

## 5.9 Dashboard

Responsabilidad

Presentar información al usuario.

Tecnología

Streamlit.

Funciones

- KPIs;
- gráficos;
- filtros;
- tablas.

---

# 6. Flujo de datos

El pipeline seguirá el siguiente flujo.

```
API

↓

Extracción

↓

JSON

↓

Raw Layer

↓

Transformación

↓

Validación

↓

Carga

↓

Data Warehouse

↓

FastAPI

↓

Dashboard
```

---

# 7. Arquitectura por capas

La solución sigue una arquitectura por capas.

## Capa 1

### Fuente

ESIOS.

---

## Capa 2

### Ingestión

Responsable de obtener los datos.

---

## Capa 3

### Almacenamiento Raw

Responsable de conservar la información original.

---

## Capa 4

### Procesamiento

Transformación y calidad.

---

## Capa 5

### Persistencia

Data Warehouse.

---

## Capa 6

### Servicio

API REST.

---

## Capa 7

### Presentación

Dashboard.

---

# 8. Justificación tecnológica

## Python

Lenguaje principal.

Razones

- ecosistema Data.
- facilidad de mantenimiento.
- amplia adopción.

---

## Requests

Cliente HTTP sencillo.

---

## Pandas

Procesamiento tabular.

Ideal para el volumen del MVP.

---

## PostgreSQL

Base de datos robusta.

Permite evolucionar fácilmente.

---

## FastAPI

API REST moderna.

Documentación automática.

Excelente rendimiento.

---

## Streamlit

Permite construir dashboards rápidamente.

Ideal para MVP.

---

# 9. Comunicación entre componentes

| Origen    | Destino    | Medio      |
| --------- | ---------- | ---------- |
| API       | Extract    | HTTP       |
| Extract   | Raw Layer  | JSON       |
| Raw Layer | Transform  | Pandas     |
| Transform | Quality    | DataFrame  |
| Quality   | Load       | DataFrame  |
| Load      | PostgreSQL | SQL        |
| FastAPI   | PostgreSQL | SQLAlchemy |
| Streamlit | FastAPI    | HTTP       |

---

# 10. Gestión de errores

Cada módulo será responsable de gestionar sus propios errores.

## Extract

- Timeout.
- API no disponible.
- Error de autenticación.

---

## Transform

- JSON inválido.
- Columnas inexistentes.

---

## Quality

- Valores fuera de rango.
- Duplicados.
- Registros vacíos.

---

## Load

- Error de conexión.
- Violación de claves.

---

## API

- Recursos inexistentes.
- Errores internos.

---

# 11. Logging

Cada ejecución generará un registro.

Información mínima.

- fecha;
- hora;
- duración;
- módulo;
- registros procesados;
- estado;
- mensaje.

Ejemplo.

```
2026-07-27 09:00:15

MODULE: Extract

STATUS: SUCCESS

ROWS: 420
```

---

# 12. Seguridad

Las credenciales se almacenarán en un archivo `.env`.

Nunca deberán incluirse en:

- Git;
- GitHub;
- notebooks;
- scripts.

Toda comunicación con la API utilizará HTTPS.

---

# 13. Escalabilidad

La arquitectura ha sido diseñada para evolucionar sin modificar la lógica principal.

En futuras versiones podrán añadirse:

- nuevos indicadores;
- nuevos países;
- nuevas APIs;
- nuevos dashboards.

---

# 14. Evolución prevista

La arquitectura evolucionará de forma incremental.

## MVP

```
Python

↓

PostgreSQL

↓

FastAPI

↓

Streamlit
```

---

## Versión 2

```
Docker

↓

Docker Compose
```

---

## Versión 3

```
Airflow

↓

dbt

↓

Great Expectations
```

---

## Versión 4

```
Kafka

↓

Streaming
```

---

## Versión 5

```
Google Cloud

↓

Cloud Storage

↓

BigQuery

↓

Cloud Run
```

---

# 15. Decisiones arquitectónicas (Architecture Decision Records)

| ID      | Decisión                                        | Justificación                                                                  |
| ------- | ----------------------------------------------- | ------------------------------------------------------------------------------ |
| ADR-001 | Conservar una Raw Layer                         | Permite auditoría y reprocesamiento sin volver a consultar la API.             |
| ADR-002 | Utilizar PostgreSQL en el MVP                   | El volumen de datos es reducido y simplifica el desarrollo local.              |
| ADR-003 | Separar la API REST del dashboard               | Facilita que otros consumidores utilicen los datos sin depender de Streamlit.  |
| ADR-004 | Organizar el pipeline en módulos independientes | Mejora la mantenibilidad y permite sustituir componentes en futuras versiones. |
| ADR-005 | Utilizar un modelo dimensional                  | Optimiza las consultas analíticas y facilita la ampliación del Data Warehouse. |

---

# 16. Diagrama de despliegue (MVP)

```
┌──────────────────────────────────────────────┐
│                Equipo del desarrollador      │
│                                              │
│  ┌────────────────────────────────────────┐  │
│  │ Python Pipeline                        │  │
│  │ - extract.py                           │  │
│  │ - transform.py                         │  │
│  │ - quality.py                           │  │
│  │ - load.py                              │  │
│  └────────────────────────────────────────┘  │
│                     │                        │
│                     ▼                        │
│           PostgreSQL Local                  │
│                     │                        │
│        ┌────────────┴────────────┐           │
│        ▼                         ▼           │
│    FastAPI                 Streamlit         │
└──────────────────────────────────────────────┘
                    ▲
                    │ HTTPS
                    ▼
          API pública ESIOS (REE)
```

---

# 17. Conclusión

La arquitectura propuesta responde a las necesidades del MVP manteniendo una separación clara entre las distintas responsabilidades del sistema:

- **Ingestión**, encargada de obtener los datos desde la API oficial.
- **Almacenamiento Raw**, que garantiza trazabilidad y capacidad de reprocesamiento.
- **Transformación y calidad**, donde los datos se preparan para el análisis.
- **Persistencia**, mediante un modelo dimensional en PostgreSQL.
- **Servicio**, a través de una API REST desacoplada.
- **Presentación**, mediante un dashboard orientado a usuarios de negocio.

Esta arquitectura es sencilla de implementar, pero sigue principios utilizados en plataformas de datos empresariales y permite evolucionar progresivamente hacia soluciones con Docker, Airflow, dbt, Kafka y servicios en la nube sin necesidad de rediseñar el núcleo del sistema.
