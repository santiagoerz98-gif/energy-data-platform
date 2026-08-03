# Guia de Ejecucion del Pipeline

## 1. Punto de entrada

El pipeline se ejecuta desde:

- `pipeline/run_pipeline.py`

Comando recomendado:

```bash
python -m pipeline.run_pipeline <indicator_id> [opciones]
```

## 2. Parametros CLI

- `indicator_id` (obligatorio): ID del indicador ESIOS.
- `--start-date`: fecha inicial (`YYYY-MM-DD`).
- `--end-date`: fecha final (`YYYY-MM-DD`).
- `--time-trunc`: granularidad temporal solicitada a ESIOS.
- `--geo-ids`: lista de identificadores geograficos.

## 3. Ejemplos

### Demanda real mensual

```bash
python -m pipeline.run_pipeline 1293 --start-date 2026-07-01 --end-date 2026-07-31
```

### Demanda prevista para rango corto

```bash
python -m pipeline.run_pipeline 544 --start-date 2026-08-01 --end-date 2026-08-03
```

### Generacion con truncamiento diario

```bash
python -m pipeline.run_pipeline 546 --start-date 2026-08-01 --end-date 2026-08-03 --time-trunc day
```

## 4. Flujo operativo

1. Extract: descarga JSON desde ESIOS.
2. Transform: normaliza y limpia datos.
3. Quality: valida y genera reporte.
4. Load: inserta en `staging.<dataset>`.

## 5. Salidas esperadas

- Raw JSON: `data/raw/esios/YYYY/MM/DD/...`
- Reportes de calidad: `data/raw/processed/reports/`
- Datos operativos: `staging.demand` o `staging.generation`

## 6. Validacion post-ejecucion

Ejemplos SQL:

```sql
SELECT COUNT(*) FROM staging.demand;
SELECT COUNT(*) FROM staging.generation;
```

## 7. Manejo de fallos

- Si falla calidad, el pipeline detiene la ejecucion.
- Si falla API o DB, revisar logs y volver a ejecutar.
- El proceso elimina filas previas por indicador/rango antes de insertar cuando aplica.

## 8. Buenas practicas operativas

- Ejecutar por ventanas de fecha acotadas.
- Validar reportes de calidad en cada corrida.
- Mantener catalogo de indicadores actualizado en `config/ids_catalog.py`.
