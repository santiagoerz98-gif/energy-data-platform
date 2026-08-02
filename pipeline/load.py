import logging
import pandas as pd
from pathlib import Path

logger = logging.getLogger(__name__)

class Loader:
    def __init__(self, engine):
        """
        Inicializa el cargador con un motor de base de datos.
        :param engine: Instancia del motor de SQLAlchemy para conectarse a la base de datos.
        """
        self.engine = engine

    def load_staging(self, df: pd.DataFrame, table_name: str, schema: str = "staging"):
        """
        Carga un DataFrame en la tabla de staging de la base de datos.

        Args:
            df (pd.DataFrame): DataFrame a cargar.
            table_name (str): Nombre de la tabla de staging.
            schema (str): Nombre del esquema donde se cargará la tabla.
        """
        try:
            df.to_sql(
                table_name, 
                self.engine, # Utiliza el motor de SQLAlchemy para la conexión
                schema=schema, # Esquema donde se cargará la tabla
                if_exists='replace', # Reemplaza la tabla si ya existe
                index=False, 
                method="multi" # Utiliza inserciones múltiples para mejorar el rendimiento
            )
            logger.info(f"-> [Load] Datos cargados exitosamente en la tabla de staging: '{table_name}'")
        except Exception as e:
            logger.exception(f"-> [Load Error] Falló la carga a la tabla '{table_name}': {e}")
            raise e