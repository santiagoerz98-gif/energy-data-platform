# Definir esquemas de validación de tipos y serialización JSON con Pydantic
from pydantic import BaseModel,ConfigDict
from datetime import date, datetime

class GeographyData(BaseModel):
    geography_key: int
    geo_id: int
    geo_name: str

    model_config = ConfigDict(from_attributes=True)  # Permite la serialización de objetos ORM a Pydantic

class EnergySourceData(BaseModel):
    energy_source_key: int
    technology_name: str
    renewable: bool

    model_config = ConfigDict(from_attributes=True)  # Permite la serialización de objetos ORM a Pydantic

class TimeData(BaseModel):
    time_key: int
    datetime_utc: datetime  # Cambiado a str para serialización JSON
    date_actual: date
    year: int
    quarter: int
    month: int
    month_name: str
    day: int
    hour: int
    day_of_week: int
    day_name: str
    is_weekend: bool

    model_config = ConfigDict(from_attributes=True)  # Permite la serialización de objetos ORM a Pydantic

class DemandData(BaseModel):
    time: TimeData
    geography: GeographyData
    demand_mwh: float
    measurement_type: str
    indicator_id: int

    # Configuración para permitir la serialización de objetos ORM
    model_config = ConfigDict(from_attributes=True)  # Permite la serialización de objetos ORM a Pydantic

class GenerationData(BaseModel):
    time: TimeData
    geography: GeographyData
    energy_source: EnergySourceData
    generation_mwh: float
    indicator_id: int

    # Configuración para permitir la serialización de objetos ORM
    model_config = ConfigDict(from_attributes=True)  # Permite la serialización de objetos ORM a Pydantic