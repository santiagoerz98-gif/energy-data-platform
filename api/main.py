import logging
from sqlalchemy.exc import SQLAlchemyError
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from api.schemas import DemandData, GenerationData
from api.crud import get_demand_data, get_generation_data
from config.database import get_db
from datetime import date

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI(title = "Energy Data Platform API", description = "API for serving energy data", version = "1.0.0")

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/demand", response_model=List[DemandData])
def get_demand(db: Session = Depends(get_db), 
               start_date: Optional[date] = None, 
               end_date: Optional[date] = None,
               measurement_type: Optional[str] = None,
               geo_name: Optional[str] = None):
    """Endpoint para obtener datos de demanda desde la tabla de hechos fact_demand, filtrando por fechas, tipo de medición y geografía."""
    try:
        return get_demand_data(
            db, 
            start_date=start_date, 
            end_date=end_date, 
            measurement_type=measurement_type, 
            geo_name=geo_name
        )
    except SQLAlchemyError as e:
        logger.error(f"Error consultando la base de datos: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/generation", response_model=List[GenerationData])
def get_generation(db: Session = Depends(get_db), 
                   start_date: Optional[date] = None, 
                   end_date: Optional[date] = None,
                   energy_source_name: Optional[str] = None,
                   geo_name: Optional[str] = None):
    """Endpoint para obtener datos de generación desde la tabla de hechos fact_generation, filtrando por fechas, fuente de energía y geografía."""
    try:
        return get_generation_data(
            db, 
            start_date=start_date, 
            end_date=end_date,
            energy_source_name=energy_source_name, 
            geo_name=geo_name
        )
    except SQLAlchemyError as e:
        logger.error(f"Error consultando la base de datos: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")