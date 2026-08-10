from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from api import schemas
from api.models import (
    DimEnergySource,
    DimGeography,
    DimTime,
    FactDemand,
    FactGeneration,
)


def get_demand_data(
    db: Session,
    *,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    measurement_type: Optional[str] = None,
    geo_name: Optional[str] = None,
):
    query = (
        db.query(FactDemand, DimTime, DimGeography)
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
        schemas.DemandData(
            time=schemas.TimeData.model_validate(time_obj),
            geography=schemas.GeographyData.model_validate(geo_obj),
            demand_mwh=float(fact_obj.demand_mwh),
            measurement_type=fact_obj.measurement_type,
            indicator_id=fact_obj.indicator_id,
        )
        for fact_obj, time_obj, geo_obj in rows
    ]


def get_generation_data(
    db: Session,
    *,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    energy_source_name: Optional[str] = None,
    geo_name: Optional[str] = None,
):
    query = (
        db.query(FactGeneration, DimTime, DimGeography, DimEnergySource)
        .join(DimTime, FactGeneration.time_key == DimTime.time_key)
        .join(DimGeography, FactGeneration.geography_key == DimGeography.geography_key)
        .join(
            DimEnergySource,
            FactGeneration.energy_source_key == DimEnergySource.energy_source_key,
        )
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
        schemas.GenerationData(
            time=schemas.TimeData.model_validate(time_obj),
            geography=schemas.GeographyData.model_validate(geo_obj),
            energy_source=schemas.EnergySourceData.model_validate(energy_source_obj),
            generation_mwh=float(fact_obj.generation_mwh),
            indicator_id=fact_obj.indicator_id,
        )
        for fact_obj, time_obj, geo_obj, energy_source_obj in rows
    ]


