# API Analysis

## Proyecto: Energy Data Platform

**Versión:** 1.0

**Autor:** Santiago Rodríguez

**Fecha:** Julio 2026

---

# 1. Objetivo

Este documento analiza la API pública de ESIOS (Sistema de Información del Operador del Sistema) con el objetivo de determinar si constituye una fuente adecuada para alimentar el pipeline de datos del proyecto **Energy Data Platform**.

El análisis incluye:

- descripción de la fuente de datos;
- autenticación;
- recursos disponibles;
- estructura de los datos;
- indicadores seleccionados;
- riesgos identificados;
- decisiones de diseño para el MVP.

---

# 2. Contexto del negocio

La empresa Red Eléctrica de España (REE) publica información del sistema eléctrico español a través de la plataforma ESIOS.

Estos datos permiten conocer:

- producción eléctrica
- demanda
- precios
- emisiones
- intercambios internacionales
- energías renovables
- tecnologías de generación

El objetivo del proyecto consiste en construir una plataforma de datos que permita almacenar esta información y ofrecer consultas rápidas para analistas energéticos.

---

# 3. Descripción de la API

Nombre:

ESIOS API

Proveedor:

Red Eléctrica de España (REE)

Tipo:

REST API

Formato:

JSON

Protocolo:

HTTPS

Frecuencia de actualización:

Depende del indicador.

Existen indicadores horarios, diarios y mensuales.

---

# 4. Autenticación

La API requiere autenticación mediante un API Key.

El token debe enviarse en los encabezados HTTP de cada petición.

Ejemplo conceptual:

Headers

- Accept
- Content-Type
- x-api-key

Las credenciales nunca deberán almacenarse directamente en el código fuente.

Durante el desarrollo se utilizará un archivo

.env

para guardar la clave.

---

# 5. Recursos disponibles

La API ofrece numerosos recursos.

Los más relevantes para este proyecto son:

## Indicadores

Permiten consultar series temporales de datos energéticos.

Será el recurso principal del MVP.

---

## Catálogo de indicadores

Permite conocer:

- identificador
- nombre
- descripción
- unidad
- frecuencia

---

## Valores históricos

Permite obtener los datos correspondientes a un indicador para un intervalo temporal.

---

# 6. Indicadores seleccionados

El catalogo tecnico del proyecto ya contempla indicadores de demanda y generacion en `config/ids_catalog.py`.

Para la operacion inicial del MVP se prioriza demanda, manteniendo generacion disponible para ejecuciones progresivas por lotes.

## Estado actual por dominio

| Dominio        | Estado                                    | Detalle                                        |
| -------------- | ----------------------------------------- | ---------------------------------------------- |
| Demanda        | Implementado y operativo                  | Multiples IDs activos en catalogo              |
| Generacion     | Implementado a nivel de catalogo/pipeline | Activacion gradual por indicador               |
| Precio mercado | Planificado                               | No integrado en catalogo actual                |
| Mix energetico | Derivable                                 | Se obtiene agregando indicadores de generacion |

## Indicadores de demanda actualmente catalogados

- 1293: Demanda real
- 1740: Demanda Real SNP
- 2037: Demanda real nacional
- 544: Demanda prevista
- 2052: Demanda real prevista nacional
- 545: Demanda programada
- 2053: Demanda real programada nacional

## Indicadores de generacion (catalogo disponible)

El archivo `config/ids_catalog.py` incluye un conjunto amplio de indicadores de generacion (reales, programados y previstos), entre ellos los IDs base 546-555 y otros asociados por tecnologia.

Se recomienda consultar siempre ese archivo como fuente de verdad operativa antes de planificar nuevas extracciones.

---

# 7. Parámetros de consulta

Los principales parámetros que utilizará el proyecto son:

| Parámetro  | Descripción                  |
| ---------- | ---------------------------- |
| start_date | Fecha inicial                |
| end_date   | Fecha final                  |
| time_trunc | Nivel de agregación temporal |
| geo_ids    | Área geográfica              |
| geo_trunc  | Nivel geográfico             |

---

# 8. Formato esperado de la respuesta

Las respuestas se reciben en formato JSON.

De manera simplificada contienen:

```json
{
  "indicator": {
    "id": 1001,
    "name": "Demanda eléctrica"
  },
  "values": [
    {
      "datetime": "...",
      "value": 25340,
      "geo_id": 8741
    }
  ]
}
```

El campo más importante es

values

ya que contiene la serie temporal.

---

# 9. Diccionario preliminar de datos

| Campo          | Tipo      | Descripción                 | Destino                       |
| -------------- | --------- | --------------------------- | ----------------------------- |
| indicator_id   | INTEGER   | Identificador del indicador | metadata                      |
| indicator_name | VARCHAR   | Nombre del indicador        | metadata                      |
| datetime_utc   | TIMESTAMP | Fecha de la medición        | dim_time                      |
| value          | FLOAT     | Valor medido                | fact_generation / fact_demand |
| geo_id         | INTEGER   | Identificador geográfico    | dim_geo                       |
| geo_name       | VARCHAR   | Nombre del área             | dim_geo                       |
| unit           | VARCHAR   | Unidad de medida            | metadata                      |

---

# 10. Datos necesarios para el MVP

El pipeline únicamente almacenará los campos necesarios.

Se descartarán:

- textos descriptivos
- notas
- información HTML
- enlaces
- metadatos no utilizados

Esto reducirá el tamaño de almacenamiento y simplificará las transformaciones.

---

# 11. Frecuencia de extracción

Durante el MVP la extracción será manual.

En versiones posteriores podrá ejecutarse:

- cada hora
- diariamente
- mediante Airflow

---

# 12. Riesgos identificados

## Cambios en el esquema JSON

La API podría añadir nuevos campos.

Mitigación

Seleccionar únicamente las columnas necesarias.

---

## Valores nulos

Algunos indicadores pueden contener datos incompletos.

Mitigación

Implementar reglas de calidad.

---

## Registros duplicados

Podrían aparecer al repetir una extracción.

Mitigación

Implementar UPSERT durante la carga.

---

## Errores de conexión

La API puede no responder temporalmente.

Mitigación

Implementar reintentos automáticos.

---

## Cambios en los indicadores

REE puede modificar identificadores.

Mitigación

Consultar periódicamente el catálogo.

---

# 13. Decisiones de diseño

Para el MVP se ha decidido:

✓ trabajar únicamente con indicadores nacionales

✓ almacenar los JSON originales

✓ transformar los datos con Pandas

✓ utilizar PostgreSQL como Data Warehouse

✓ preparar la salida para consumo por API o dashboard en fases posteriores

Nota de estado:

- `api/` existe como carpeta de roadmap, sin implementacion funcional.
- `app/` existe como carpeta de roadmap, sin implementacion funcional.

---

# 14. Datos que almacenará el proyecto

El Data Warehouse contendrá dos tablas de hechos.

## Fact Generation

Producción eléctrica por tecnología.

---

## Fact Demand

Demanda eléctrica.

---

Y las siguientes dimensiones.

- Tiempo
- Tecnología
- Área geográfica

---

# 15. Calidad de datos

Durante la transformación se verificarán las siguientes reglas.

## Regla 1

No permitir valores nulos en

datetime

---

## Regla 2

No permitir producción negativa.

---

## Regla 3

No permitir demanda negativa.

---

## Regla 4

Eliminar registros duplicados.

---

## Regla 5

Validar tipos de datos.

---

# 16. Limitaciones del MVP

No se implementará:

- streaming
- Kafka
- Airflow
- Docker
- dbt
- Great Expectations
- CI/CD

Estas funcionalidades se incorporarán en versiones posteriores.

---

# 17. Próximos pasos

Finalizado este análisis se desarrollarán los siguientes módulos:

1. Cliente de la API

2. Ingestión

3. Transformación

4. Calidad

5. Carga

6. Consolidacion de carga analitica en `dw`

7. API REST (fase posterior)

8. Dashboard (fase posterior)
