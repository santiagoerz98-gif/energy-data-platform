# Identificación de Entidades del Data Warehouse

**Proyecto:** Energy Data Platform MVP  
**Empresa:** IberGrid Analytics (empresa ficticia)  
**Fase:** 3 - Modelado de Datos  
**Documento:** Identificación de Entidades  
**Versión:** 1.0

---

# 1. Objetivo

El objetivo de este documento es identificar las principales entidades del dominio de negocio que formarán parte del Data Warehouse.

Esta identificación servirá como base para el diseño del modelo dimensional (esquema estrella) y permitirá definir posteriormente las tablas de hechos y dimensiones necesarias para el análisis de la producción y la demanda eléctrica en España.

---

# 2. Contexto de negocio

IberGrid Analytics desarrolla una plataforma interna para analizar información pública del sistema eléctrico español obtenida a través de la API de ESIOS.

El objetivo es proporcionar información histórica y facilitar el análisis de indicadores relacionados con:

- Producción eléctrica.
- Demanda eléctrica.
- Evolución temporal.
- Distribución geográfica.
- Participación de las distintas tecnologías de generación.

Los usuarios finales de la plataforma son analistas energéticos, responsables de planificación y equipos de inteligencia de negocio.

---

# 3. Procesos de negocio identificados

Tras analizar la API de ESIOS se han identificado dos procesos principales:

## 3.1 Producción eléctrica

Representa la energía generada por cada tecnología de generación durante un instante determinado.

Ejemplos de tecnologías:

- Solar fotovoltaica
- Eólica
- Hidráulica
- Nuclear
- Ciclo combinado
- Cogeneración

La producción constituye uno de los procesos principales que se desea analizar.

---

## 3.2 Demanda eléctrica

Representa la demanda de energía eléctrica registrada durante un instante determinado para una zona geográfica.

Este proceso permite analizar la evolución del consumo eléctrico y compararlo con la producción disponible.

---

# 4. Granularidad

Antes de diseñar el modelo dimensional es necesario definir el nivel de detalle (grano) de cada tabla de hechos.

## Fact Generation

Cada registro representa:

> La producción de una tecnología de generación para una ubicación geográfica en un instante de tiempo determinado.

Granularidad:

- Fecha y hora
- Tecnología
- Ubicación geográfica

---

## Fact Demand

Cada registro representa:

> La demanda eléctrica registrada para una ubicación geográfica en un instante de tiempo determinado.

Granularidad:

- Fecha y hora
- Ubicación geográfica

---

# 5. Entidades identificadas

A partir del análisis del dominio se identifican las siguientes entidades.

## 5.1 Tiempo

Representa la dimensión temporal utilizada para realizar análisis históricos.

### Atributos previstos

- Fecha
- Hora
- Día
- Mes
- Trimestre
- Año
- Día de la semana

### Justificación

Toda la información energética se analiza desde una perspectiva temporal.

Será una dimensión compartida por todas las tablas de hechos.

---

## 5.2 Tecnología de generación

Representa la tecnología utilizada para producir la energía.

### Ejemplos

- Solar fotovoltaica
- Solar térmica
- Eólica
- Hidráulica
- Nuclear
- Ciclo combinado

### Atributos previstos

- Identificador
- Nombre
- Tipo (Renovable / No renovable)

### Justificación

Permite analizar el mix energético y calcular indicadores como el porcentaje de generación renovable.

---

## 5.3 Geografía

Representa la zona geográfica asociada a la medición.

La API proporciona información mediante:

- geo_id
- geo_name

### Atributos previstos

- Identificador geográfico
- Nombre

### Justificación

Permite realizar comparaciones entre diferentes regiones y analizar la distribución territorial de la producción y la demanda.

---

# 6. Tablas de hechos identificadas

## Fact Generation

Contendrá las mediciones de producción eléctrica.

### Métrica principal

- Energía generada (MWh)

### Relaciones

- Dimensión Tiempo
- Dimensión Tecnología
- Dimensión Geografía

---

## Fact Demand

Contendrá las mediciones de demanda eléctrica.

### Métrica principal

- Demanda eléctrica (MWh)

### Atributo operativo adicional

- `measurement_type`: clasifica la medicion en `Real`, `Forecast` o `Scheduled`.

Este atributo facilita comparar demanda observada frente a demanda prevista o programada sin perder granularidad temporal.

### Relaciones

- Dimensión Tiempo
- Dimensión Geografía

---

# 7. Modelo conceptual

El modelo conceptual identificado es el siguiente.

```
                 dim_time
                     │
                     │
                     │
dim_energy_source ───┼──── fact_generation ───── dim_geography


                 dim_time
                     │
                     │
                     │
                fact_demand
                     │
                     │
               dim_geography
```

---

# 8. Justificación del modelo

Se ha optado por separar la información en dos tablas de hechos independientes debido a que representan procesos de negocio diferentes.

**Fact Generation**

- Analiza la producción energética.
- Incluye la tecnología utilizada para generar la energía.

**Fact Demand**

- Analiza el consumo eléctrico.
- No requiere una dimensión de tecnología de generación.

Esta separación facilita la evolución del modelo y evita introducir atributos o claves que no aportan valor analítico.

---

# 9. Próximos pasos

Una vez identificadas las entidades del dominio se procederá a:

1. Diseñar el modelo estrella.
2. Definir las claves primarias y foráneas.
3. Especificar las relaciones entre tablas.
4. Crear el diagrama entidad-relación.
5. Implementar el esquema físico en PostgreSQL.

---

# 10. Nota de alineacion con el modelo fisico

El modelo fisico actual en `database/schema.sql` incorpora `measurement_type` en `fact_demand`, por lo que este documento conceptual se actualiza para mantener consistencia entre diseño y operacion.

---
