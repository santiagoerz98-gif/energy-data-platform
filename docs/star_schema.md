````markdown
# Diseño del Modelo Estrella

**Proyecto:** Energy Data Platform MVP  
**Empresa:** IberGrid Analytics (empresa ficticia)  
**Fase:** 3 - Modelado de Datos  
**Documento:** Diseño del Modelo Estrella  
**Versión:** 1.0

---

# 1. Objetivo

El objetivo de este documento es definir el modelo dimensional que servirá como base para el Data Warehouse del proyecto.

El modelo permitirá almacenar información histórica sobre la generación y la demanda eléctrica procedente de la API de ESIOS, optimizando las consultas analíticas mediante un esquema estrella (_Star Schema_).

---

# 2. Objetivos del modelo

El modelo ha sido diseñado para responder preguntas de negocio como:

- ¿Cuánta energía se produjo durante un período determinado?
- ¿Cuál fue la demanda eléctrica por región?
- ¿Qué tecnologías generan mayor cantidad de energía?
- ¿Qué porcentaje de la generación corresponde a energías renovables?
- ¿Cómo evoluciona la producción y la demanda a lo largo del tiempo?

---

# 3. Granularidad

Antes de definir las tablas es necesario establecer el nivel de detalle (grano) que tendrá cada una de ellas.

## Fact Generation

Cada registro representa:

> La producción de una tecnología de generación para una ubicación geográfica en un instante de tiempo determinado.

Granularidad:

- Fecha y hora
- Tecnología de generación
- Ubicación geográfica

---

## Fact Demand

Cada registro representa:

> La demanda eléctrica registrada para una ubicación geográfica en un instante de tiempo determinado.

Granularidad:

- Fecha y hora
- Ubicación geográfica

---

# 4. Dimensiones

## 4.1 Dimensión Tiempo

**Tabla:** `dim_time`

### Propósito

Permite realizar análisis temporales sin necesidad de calcular atributos derivados durante las consultas.

### Atributos

| Campo       | Tipo        | Descripción                                        |
| ----------- | ----------- | -------------------------------------------------- |
| time_key    | INT         | Clave primaria con formato YYYYMMDD (ej: 20260803) |
| date_actual | DATE        | Fecha calendario                                   |
| year        | INT         | Año                                                |
| quarter     | INT         | Trimestre                                          |
| month       | INT         | Mes numerico (1-12)                                |
| month_name  | VARCHAR(20) | Nombre del mes                                     |
| day         | INT         | Dia del mes                                        |
| day_of_week | INT         | Dia ISO de la semana (1-7)                         |
| day_name    | VARCHAR(20) | Nombre del dia                                     |
| is_weekend  | BOOLEAN     | Verdadero si la fecha cae en fin de semana         |

Nota: la definicion fisica y su carga inicial estan en `database/create_dim_time.sql`.

---

## 4.2 Dimensión Tecnología

**Tabla:** `dim_energy_source`

### Propósito

Almacena las tecnologías de generación eléctrica.

### Atributos

| Campo             | Tipo         | Descripción                          |
| ----------------- | ------------ | ------------------------------------ |
| energy_source_key | SERIAL       | Clave primaria sustituta             |
| technology_name   | VARCHAR(100) | Nombre de la tecnología              |
| renewable         | BOOLEAN      | Indica si la tecnología es renovable |

---

## 4.3 Dimensión Geografía

**Tabla:** `dim_geography`

### Propósito

Representa la ubicación geográfica asociada a cada medición.

### Atributos

| Campo         | Tipo         | Descripción                           |
| ------------- | ------------ | ------------------------------------- |
| geography_key | SERIAL       | Clave primaria sustituta              |
| geo_id        | INTEGER      | Identificador proporcionado por ESIOS |
| geo_name      | VARCHAR(100) | Nombre de la ubicación                |

---

# 5. Tablas de hechos

## 5.1 Fact Generation

**Tabla:** `fact_generation`

### Propósito

Almacena la producción eléctrica registrada para cada tecnología, ubicación y momento.

### Medida

- `generation_mwh`

### Campos

| Campo             | Tipo          | Descripción            |
| ----------------- | ------------- | ---------------------- |
| generation_key    | BIGSERIAL     | Clave primaria         |
| time_key          | INTEGER       | FK → dim_time          |
| geography_key     | INTEGER       | FK → dim_geography     |
| energy_source_key | INTEGER       | FK → dim_energy_source |
| generation_mwh    | NUMERIC(12,3) | Energía generada (MWh) |

---

## 5.2 Fact Demand

**Tabla:** `fact_demand`

### Propósito

Almacena la demanda eléctrica registrada para una ubicación geográfica y un instante determinado.

### Medida

- `demand_mwh`

### Campos

| Campo            | Tipo          | Descripción                                  |
| ---------------- | ------------- | -------------------------------------------- |
| demand_key       | BIGSERIAL     | Clave primaria                               |
| time_key         | INTEGER       | FK → dim_time                                |
| geography_key    | INTEGER       | FK → dim_geography                           |
| demand_mwh       | NUMERIC(12,3) | Demanda eléctrica (MWh)                      |
| measurement_type | VARCHAR(50)   | Tipo de medicion (Real, Forecast, Scheduled) |

---

# 6. Relaciones

## Fact Generation

| Tabla relacionada | Clave             |
| ----------------- | ----------------- |
| dim_time          | time_key          |
| dim_geography     | geography_key     |
| dim_energy_source | energy_source_key |

---

## Fact Demand

| Tabla relacionada | Clave         |
| ----------------- | ------------- |
| dim_time          | time_key      |
| dim_geography     | geography_key |

---

# 7. Diagrama del modelo estrella

## Producción eléctrica

```text
                        dim_time
                    ┌───────────────┐
                    │   time_key PK │
                    │ date_actual   │
                    │ day           │
                    │ month         │
                    │ quarter       │
                    │ year          │
                    │ month_name    │
                    │ day_of_week   │
                    │ day_name      │
                    │ is_weekend    │
                    └───────┬───────┘
                            │
                            │
                            │
┌──────────────────┐         │        ┌────────────────────────┐
│ dim_geography    │         │        │ dim_energy_source      │
│──────────────────│         │        │────────────────────────│
│ geography_key PK │◄────────┼────────► energy_source_key PK   │
│ geo_id           │         │        │ technology_name        │
│ geo_name         │         │        │ renewable              │
└──────────────────┘         │        └────────────────────────┘
                             │
                             │
                     ┌───────▼────────────────┐
                     │    fact_generation     │
                     │────────────────────────│
                     │ generation_key PK      │
                     │ time_key FK            │
                     │ geography_key FK       │
                     │ energy_source_key FK   │
                     │ generation_mwh         │
                     └────────────────────────┘
```

---

## Demanda eléctrica

```text
                 dim_time
             ┌───────────────┐
             │  time_key PK  │
             └───────┬───────┘
                     │
                     │
                     │
            ┌────────▼─────────┐
            │   fact_demand    │
            │──────────────────│
            │ demand_key PK    │
            │ time_key FK      │
            │ geography_key FK │
            │ demand_mwh       │
            └────────┬─────────┘
                     │
                     │
             ┌───────▼──────────┐
             │ dim_geography    │
             │──────────────────│
             │ geography_key PK │
             │ geo_id           │
             │ geo_name         │
             └──────────────────┘
```

---

# 8. Decisiones de diseño

## Modelo estrella

Se ha seleccionado un esquema estrella por su simplicidad y porque está optimizado para consultas analíticas (OLAP), reduciendo el número de uniones necesarias entre tablas.

---

## Dos tablas de hechos

La generación y la demanda representan procesos de negocio distintos y evolucionan de forma independiente, por lo que se modelan en tablas separadas.

---

## Claves sustitutas

Todas las dimensiones utilizan claves sustitutas (`SERIAL`) para desacoplar el modelo dimensional de los identificadores del sistema origen.

---

## Dimensión Tiempo compartida

La dimensión tiempo será utilizada por todas las tablas de hechos, permitiendo realizar análisis temporales consistentes.

---

## Alineacion con implementacion

Este documento refleja el esquema actual definido en:

- `database/schema.sql`
- `database/create_dim_time.sql`

---

## Dimensión Tecnología

Solo la tabla `fact_generation` referencia la dimensión de tecnologías, ya que la demanda eléctrica no depende de una fuente de generación específica.

---

# 9. Ventajas del modelo

- Separación clara entre hechos y dimensiones.
- Consultas analíticas simples y eficientes.
- Modelo fácilmente extensible para incorporar nuevos indicadores energéticos.
- Facilita la construcción de cuadros de mando y herramientas de Business Intelligence.
- Compatible con herramientas como Power BI, Tableau o Looker.

---

# 10. Próximos pasos

Una vez validado este diseño se procederá a:

1. Crear el esquema físico en PostgreSQL.
2. Implementar el archivo `schema.sql`.
3. Definir las claves primarias y foráneas.
4. Crear los índices necesarios para optimizar las consultas.
5. Preparar el proceso de transformación y carga (ETL) hacia el Data Warehouse.

---
````
