### 
# Modulo para definir la estructura en la base de datos usando SQLAlchemy. 
# Reflejamos el Star Schema uniendo las dimensiones a la tabla de hechos con ForeignKey y relacionando mediante relationship.

from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from config.database import Base

# dim_geography
class DimGeography(Base):
    __tablename__ = 'dim_geography'

    __table_args__ = {'schema': 'dw'}

    geography_key = Column(Integer, primary_key=True)
    geo_id = Column(Integer, nullable=False)
    geo_name = Column(String(100), nullable=False)

# dim_energy_source
class DimEnergySource(Base):
    __tablename__ = 'dim_energy_source'

    __table_args__ = {'schema': 'dw'}

    energy_source_key = Column(Integer, primary_key=True)
    technology_name = Column(String(100), nullable=False)
    renewable = Column(Boolean, nullable=False)

# dim_time
class DimTime(Base):
    __tablename__ = 'dim_time'

    __table_args__ = {'schema': 'dw'}

    time_key = Column(Integer, primary_key=True)
    datetime_utc = Column(DateTime, nullable=False)
    date_actual = Column(Date, nullable=False)
    year = Column(Integer, nullable=False)
    quarter = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    month_name = Column(String(50), nullable=False)
    day = Column(Integer, nullable=False)
    hour = Column(Integer, nullable=False)
    day_of_week = Column(Integer, nullable=False)
    day_name = Column(String(50), nullable=False)
    is_weekend = Column(Boolean, nullable=False)

# fact_demand
class FactDemand(Base):
    __tablename__ = 'fact_demand'

    __table_args__ = {'schema': 'dw'}

    demand_key = Column(Integer, primary_key=True)
    time_key = Column(Integer, ForeignKey('dw.dim_time.time_key'), nullable=False)
    geography_key = Column(Integer, ForeignKey('dw.dim_geography.geography_key'), nullable=False)
    demand_mwh = Column(Float, nullable=False)
    measurement_type = Column(String(50), nullable=False)
    indicator_id = Column(Integer, nullable=False)

    # Relaciones con las dimensiones
    geography = relationship("DimGeography", backref="fact_demands")
    time = relationship("DimTime", backref="fact_demands")

class FactGeneration(Base):
    __tablename__ = 'fact_generation'

    __table_args__ = {'schema': 'dw'}

    generation_key = Column(Integer, primary_key=True, autoincrement=True)
    time_key = Column(Integer, ForeignKey('dw.dim_time.time_key'), nullable=False)
    geography_key = Column(Integer, ForeignKey('dw.dim_geography.geography_key'), nullable=False)
    energy_source_key = Column(Integer, ForeignKey('dw.dim_energy_source.energy_source_key'), nullable=False)
    generation_mwh = Column(Float, nullable=False)
    indicator_id = Column(Integer, nullable=False)

    # Relaciones con las dimensiones
    geography = relationship("DimGeography", backref="fact_generations")
    time = relationship("DimTime", backref="fact_generations")
    energy_source = relationship("DimEnergySource", backref="fact_generations")
