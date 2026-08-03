import logging
import pandas as pd
from pathlib import Path

from sqlalchemy import inspect, text

logger = logging.getLogger(__name__)

class Loader:
    def __init__(self, engine):
        """
        Inicializa el cargador con un motor de base de datos.
        :param engine: Instancia del motor de SQLAlchemy para conectarse a la base de datos.
        """
        self.engine = engine

    def load_staging(self, df: pd.DataFrame, table_name: str, schema: str = "staging", indicator_id: int | None = None, start_date: str | None = None, end_date: str | None = None):
        """
        Carga un DataFrame en la tabla de staging de la base de datos.

        Args:
            df (pd.DataFrame): DataFrame a cargar.
            table_name (str): Nombre de la tabla de staging.
            schema (str): Nombre del esquema donde se cargará la tabla.
        """
        try:
            table_exists = inspect(self.engine).has_table(table_name, schema=schema)
            
            if indicator_id is not None and table_exists:
                # Elimina filas existentes para el indicador y rango de fechas especificados antes de cargar nuevos datos
                self.delete_existing_rows(schema, table_name, indicator_id, start_date, end_date)

            df.to_sql(
                table_name, 
                self.engine, # Utiliza el motor de SQLAlchemy para la conexión
                schema=schema, # Esquema donde se cargará la tabla
                if_exists='append', # Si la tabla existe, se agregan los datos; si no, se crea la tabla
                index=False, 
                method="multi" # Utiliza inserciones múltiples para mejorar el rendimiento
            )
            logger.info(f"-> [Load] Datos cargados exitosamente en la tabla de staging: '{table_name}'")
        except Exception as e:
            logger.exception(f"-> [Load Error] Falló la carga a la tabla '{table_name}': {e}")
            raise e

    def delete_existing_rows(self, schema: str, table_name: str, indicator_id: int, start_date: str, end_date: str):
        """
        Elimina filas existentes en la tabla de staging para un indicador y rango de fechas específicos.

        Args:
            schema (str): Nombre del esquema donde se encuentra la tabla.
            table_name (str): Nombre de la tabla de staging.
            indicator_id (int): ID del indicador.
            start_date (str): Fecha de inicio del rango.
            end_date (str): Fecha de fin del rango.
        """
        conditions = ["indicator_id = :indicator_id"]
        params = {"indicator_id": indicator_id}

        if start_date and end_date:
            conditions.append("datetime_utc BETWEEN :start_date AND :end_date")
            params.update(start_date=start_date, end_date=end_date)

        query = text(f"DELETE FROM {schema}.{table_name} WHERE {' AND '.join(conditions)}")

        with self.engine.begin() as conn:
            result = conn.execute(query, params)
            logger.info(f"-> [Load] {result.rowcount} filas previas eliminadas antes del append")