# Estado de Implementacion

## Fecha de corte

2026-08-03

## 1. Resumen

El nucleo ETL del proyecto esta implementado y operativo. La capa de consumo (API y dashboard) permanece como roadmap.

## 2. Estado por componente

| Componente       | Estado       | Evidencia principal            |
| ---------------- | ------------ | ------------------------------ |
| Cliente ESIOS    | Implementado | `services/esios_client.py`     |
| Extract          | Implementado | `pipeline/extract.py`          |
| Transform        | Implementado | `pipeline/transform.py`        |
| Quality          | Implementado | `pipeline/quality.py`          |
| Load a staging   | Implementado | `pipeline/load.py`             |
| Orquestacion CLI | Implementado | `pipeline/run_pipeline.py`     |
| Esquema DW       | Implementado | `database/schema.sql`          |
| Dimension tiempo | Implementado | `database/create_dim_time.sql` |
| API REST         | Planificado  | `api/` (sin implementacion)    |
| Dashboard        | Planificado  | `app/` (sin implementacion)    |

## 3. Cobertura funcional actual

- Extraccion desde ESIOS por indicador y rango.
- Persistencia Raw de respuestas JSON.
- Limpieza de nulos, negativos y duplicados.
- Reportes de calidad en capa processed.
- Carga de datos a tablas del schema staging.

## 4. Cobertura de indicadores

- Demanda: operativo.
- Generacion: catalogado e integrable por ejecucion.
- Precio mercado y otros dominios: no implementados en catalogo activo.

## 5. Estado de pruebas

Existe una suite de pruebas en `tests/` con cobertura principal del pipeline. Tambien hay scripts de validacion manual.

## 6. Riesgos y pendientes

- Pendiente integrar API REST para consumo externo.
- Pendiente implementar dashboard para visualizacion.
- Pendiente endurecer estrategia de reintentos automáticos para fallos transitorios de API.
