# Consultas sobre el esquema estrella (Star Schema) para obtener información de la tabla de hechos y sus dimensiones relacionadas.
from sqlalchemy.orm import Session
from api.models import FactDemand, DimTime, DimGeography, DimEnergySource, FactGeneration
from typing import Optional
from datetime import date

def get_demand_data(
        db: Session,
        *,
        start_date: Optional[date] = None, 
        end_date: Optional[date] = None,
        measurement_type: Optional[str] = None,
        geo_name: Optional[str] = None
    ):
    """
    Obtiene datos de demanda desde la tabla de hechos fact_demand, 
    filtrando por fechas, tipo de medición y geografía.
    """
    query = (
        db.query(
            FactDemand.demand_mwh,
            FactDemand.measurement_type,
            FactDemand.indicator_id,
            DimTime.datetime_utc,
            DimGeography.geo_name
        )
        .join(DimTime, FactDemand.time_key == DimTime.time_key)
        .join(DimGeography, FactDemand.geography_key == DimGeography.geography_key)
    )

    if start_date:
        query = query.filter(DimTime.date_actual >= start_date)

    if end_date:
        query = query.filter(DimTime.date_actual <= end_date)

    if measurement_type:
        query = query.filter(FactDemand.measurement_type == measurement_type)

    if geo_name:
        query = query.filter(DimGeography.geo_name == geo_name)

    rows = query.order_by(DimTime.datetime_utc).all()

    return [
        {
            "datetime_utc": row.datetime_utc.isoformat(),
            "demand_mwh": float(row.demand_mwh),
            "measurement_type": row.measurement_type,
            "indicator_id": row.indicator_id,
            "geo_name": row.geo_name
        }
        for row in rows
    ]

def get_generation_data(
        db: Session,
        *, 
        start_date: Optional[date] = None, 
        end_date: Optional[date] = None,
        energy_source_name: Optional[str] = None,
        geo_name: Optional[str] = None
    ):
    """
    Obtiene datos de generación desde la tabla de hechos fact_generation, 
    filtrando por fechas, fuente de energía y geografía.
    """
    query = (
        db.query(
            FactGeneration.generation_mwh,
            FactGeneration.indicator_id,
            DimTime.datetime_utc,
            DimGeography.geo_name,
            DimEnergySource.technology_name
        )
        .join(DimTime, FactGeneration.time_key == DimTime.time_key)
        .join(DimGeography, FactGeneration.geography_key == DimGeography.geography_key)
        .join(DimEnergySource, FactGeneration.energy_source_key == DimEnergySource.energy_source_key)
    )

    if start_date:
        query = query.filter(DimTime.date_actual >= start_date)

    if end_date:
        query = query.filter(DimTime.date_actual <= end_date)

    if energy_source_name:
        query = query.filter(DimEnergySource.technology_name == energy_source_name)

    if geo_name:
        query = query.filter(DimGeography.geo_name == geo_name)

    rows = query.order_by(DimTime.datetime_utc).all()

    return [
        {
            "datetime_utc": row.datetime_utc.isoformat(),
            "generation_mwh": float(row.generation_mwh),
            "indicator_id": row.indicator_id,
            "geo_name": row.geo_name,
            "technology_name": row.technology_name
        }
        for row in rows
    ]


    