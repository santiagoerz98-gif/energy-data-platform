# Source System Assessment

## Proyecto: Energy Data Platform

**Versión:** 1.0

**Autor:** Santiago Rodríguez

**Fecha:** Julio 2026

---

# 1. Objetivo

Este documento evalúa la API pública de ESIOS como sistema fuente para el proyecto **Energy Data Platform**.

El objetivo es determinar:

- Si la fuente es adecuada para alimentar el Data Warehouse.
- Qué riesgos presenta.
- Qué estrategia de ingestión debe utilizarse.
- Qué controles de calidad son necesarios.
- Qué limitaciones deben considerarse durante el desarrollo del MVP.

---

# 2. Descripción del sistema fuente

## Nombre

ESIOS API

## Organización responsable

Red Eléctrica de España (REE)

## Tipo de sistema

REST API

## Dominio

Sistema eléctrico español

## Formato de intercambio

JSON

## Transporte

HTTPS

## Método de acceso

API autenticada mediante API Key.

---

# 3. Objetivo de negocio de la fuente

ESIOS proporciona información oficial sobre el funcionamiento del sistema eléctrico español.

Entre los principales conjuntos de datos disponibles se encuentran:

- Demanda eléctrica.
- Generación por tecnología.
- Precio del mercado eléctrico.
- Emisiones.
- Intensidad de carbono.
- Intercambios internacionales.
- Energías renovables.
- Producción por comunidades autónomas.

La información es utilizada por:

- Operadores del sistema.
- Comercializadoras.
- Analistas energéticos.
- Investigadores.
- Empresas del sector energético.

---

# 4. Evaluación de la fuente

| Aspecto          | Evaluación |
| ---------------- | ---------- |
| Fiabilidad       | Alta       |
| Disponibilidad   | Alta       |
| Calidad esperada | Alta       |
| Fuente oficial   | Sí         |
| Documentación    | Completa   |
| API pública      | Sí         |
| Autenticación    | API Key    |
| Formato estándar | JSON       |

### Conclusión

La API es una fuente adecuada para un proyecto de ingeniería de datos debido a su carácter oficial, estabilidad y estructura consistente.

---

# 5. Datos que consumirá el MVP

El MVP trabajará únicamente con los siguientes dominios de información.

## Demanda eléctrica

Frecuencia:

Horaria.

Uso:

Análisis histórico.

Dashboard.

KPIs.

---

## Generación eléctrica

Información disponible:

Producción por tecnología.

Uso:

Mix energético.

Porcentaje renovable.

Producción total.

---

## Precio del mercado

Uso:

Indicador económico.

---

## Tecnologías de generación

Ejemplos:

- Solar
- Eólica
- Nuclear
- Hidráulica
- Ciclo combinado
- Cogeneración

---

# 6. Volumen esperado

Durante el MVP el volumen de información será reducido.

Estimación.

| Concepto             | Estimación |
| -------------------- | ---------- |
| Extracciones diarias | 1          |
| Registros diarios    | < 1000     |
| Registros mensuales  | < 30000    |
| Tamaño JSON          | Bajo       |
| Crecimiento esperado | Lineal     |

### Impacto

No será necesario utilizar herramientas Big Data durante el MVP.

PostgreSQL es suficiente.

---

# 7. Frecuencia de actualización

La frecuencia depende del indicador.

Para el MVP se realizará:

Una extracción diaria.

En futuras versiones podrá ejecutarse:

- cada hora;
- cada 15 minutos;
- mediante un orquestador como Airflow.

---

# 8. Estrategia de ingestión

La ingestión seguirá un patrón ELT simplificado.

```text
API

↓

Extracción

↓

Raw JSON

↓

Transformación

↓

PostgreSQL
```

### Justificación

Guardar los datos originales permite:

- auditoría;
- reprocesamiento;
- depuración;
- recuperación ante errores.

---

# 9. Estrategia de almacenamiento

Se utilizarán tres niveles.

## Raw Layer

Contendrá el JSON exactamente como fue recibido.

No se modificarán los datos.

Ejemplo.

```
data/raw/

2026/

07/

generation/

generation_20260727_120000.json
```

---

## Processed Layer

Contendrá DataFrames limpios.

Se eliminarán:

- columnas innecesarias;
- registros inválidos;
- duplicados.

---

## Data Warehouse

PostgreSQL almacenará:

- dimensiones;
- tablas de hechos;
- métricas.

---

# 10. Calidad de datos esperada

Aunque la fuente es oficial, se implementarán controles.

## Regla 1

No aceptar registros duplicados.

---

## Regla 2

No aceptar fechas vacías.

---

## Regla 3

No aceptar valores negativos.

---

## Regla 4

No aceptar tecnologías desconocidas.

---

## Regla 5

No aceptar registros fuera del rango solicitado.

---

# 11. Riesgos identificados

## Riesgo 1

La API no responde.

### Impacto

Alto.

### Probabilidad

Media.

### Mitigación

Reintentos automáticos.

Timeout.

Registro de errores.

---

## Riesgo 2

Cambios en el esquema JSON.

### Impacto

Medio.

### Mitigación

Seleccionar únicamente las columnas utilizadas.

Validar el esquema antes de transformar.

---

## Riesgo 3

Cambios en indicadores.

### Impacto

Medio.

### Mitigación

Consultar el catálogo de indicadores antes de grandes actualizaciones del pipeline.

---

## Riesgo 4

API Key inválida.

### Impacto

Alto.

### Mitigación

Variables de entorno.

Nunca almacenar credenciales en GitHub.

---

## Riesgo 5

Datos incompletos.

### Impacto

Bajo.

### Mitigación

Validaciones de calidad.

Registro de incidencias.

---

# 12. Estrategia de recuperación

Si una extracción falla.

El pipeline deberá:

1. Registrar el error.
2. Mantener el histórico.
3. No sobrescribir datos anteriores.
4. Finalizar de forma controlada.

En futuras versiones se añadirán:

- reintentos automáticos;
- notificaciones;
- monitorización.

---

# 13. Requisitos funcionales

El sistema deberá ser capaz de:

- consumir la API;
- almacenar datos crudos;
- transformar la información;
- validar la calidad;
- cargar PostgreSQL;
- exponer los datos mediante FastAPI.

---

# 14. Requisitos no funcionales

## Mantenibilidad

Código modular.

---

## Escalabilidad

Preparado para añadir nuevos indicadores.

---

## Reutilización

El cliente de la API será independiente del resto del pipeline.

---

## Trazabilidad

Cada extracción quedará almacenada.

---

## Seguridad

Las credenciales estarán en variables de entorno.

---

# 15. Dependencias externas

El funcionamiento del pipeline depende de:

- Disponibilidad de la API.
- Conectividad a Internet.
- PostgreSQL.
- Espacio de almacenamiento.

---

# 16. Decisiones arquitectónicas

| Decisión                | Justificación                                |
| ----------------------- | -------------------------------------------- |
| Guardar JSON original   | Permite auditoría y reprocesamiento          |
| Utilizar PostgreSQL     | Suficiente para el volumen del MVP           |
| Transformar con Pandas  | Simplicidad y amplia adopción                |
| Separar API y Dashboard | Desacoplamiento entre consumo y presentación |
| Modelo dimensional      | Facilita consultas analíticas                |

---

# 17. Evolución prevista

Una vez finalizado el MVP, la arquitectura evolucionará incorporando:

## Infraestructura

- Docker
- Docker Compose

---

## Orquestación

- Apache Airflow

---

## Transformaciones

- dbt

---

## Calidad

- Great Expectations

---

## Cloud

- BigQuery
- Cloud Storage
- Cloud Run

---

## Streaming

- Apache Kafka

---

## Observabilidad

- Logging centralizado
- Métricas del pipeline
- Alertas

---

## CI/CD

- GitHub Actions

---

# 18. Conclusión

La API de ESIOS cumple los requisitos para actuar como sistema fuente del proyecto.

Su carácter oficial, la disponibilidad de documentación, el formato JSON y la existencia de mecanismos de autenticación permiten construir un pipeline robusto y fácilmente escalable.

La estrategia adoptada para el MVP prioriza la simplicidad sin renunciar a buenas prácticas de ingeniería de datos:

- conservación de los datos originales (Raw Layer);
- separación entre extracción, transformación y carga;
- validaciones de calidad antes de persistir la información;
- almacenamiento en un modelo dimensional;
- exposición mediante una API REST desacoplada del sistema de almacenamiento.

Esta base permitirá evolucionar el proyecto hacia una arquitectura de nivel profesional incorporando orquestación, procesamiento en tiempo real, despliegue en la nube y monitorización sin necesidad de rediseñar el pipeline.
