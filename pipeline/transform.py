from pathlib import Path
import json
import logging
import pandas as pd

logger = logging.getLogger(__name__)

class Transformer:
    """
    Responsable de transformar los datos de la capa Raw
    en estructuras preparadas para el Data Warehouse.
    """
    def __init__(self):
        pass

    def read_raw(self,filepath:Path)->dict:
        """
        Lee un archivo JSON almacenado en la capa Raw.

        Args:
            filepath: Ruta del archivo JSON.

        Returns:
            dict: Contenido del archivo.

        Raises:
            FileNotFoundError: Si el archivo no existe.
            json.JSONDecodeError: Si el contenido no es un JSON válido.
            OSError: Si ocurre un error durante la lectura.
        """

        logger.info("Reading raw file: %s",filepath)

        try:
            with filepath.open("r",encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError:
            logger.exception("Raw file not found: %s",filepath)
            raise

        except json.JSONDecodeError:
            logger.exception("invalid JSON file:%s",filepath)
            raise

        except OSError:
            logger.exception("Error reading file: %s", filepath)
            raise

        logger.info("Raw successfully loaded")

        return data

    def normalize(self,data:dict)-> pd.DataFrame:
        """
        Convierte la lista 'values' del JSON de ESIOS en un DataFrame,
        preservando todas las columnas presentes.
        """
        values = data["indicator"]["values"]
        return pd.DataFrame(values)

    def convert_types(self,df:pd.DataFrame)->pd.DataFrame:
        """
        Convierte las columnas del DataFrame a los tipos de datos esperados.

        Args:
            df: DataFrame normalizado.

        Returns:
            pd.DataFrame: DataFrame con los tipos convertidos.
        """

        df = df.copy()

        DTYPE_MAPPING = {
            "value":float,
            "geo_id":"int64",
            "geo_name":"string",
        }

        for column,dtype in DTYPE_MAPPING.items():
            if column in df.columns:
                df[column] = df[column].astype(dtype=dtype)

        if "datetime_utc" in df.columns:
            df["datetime_utc"] = pd.to_datetime(
                df["datetime_utc"],
                utc=True
            )

        return df

    def clean_data(self,df:pd.DataFrame)->pd.DataFrame:
        """
        Realiza la limpieza básica de los datos.

        Args:
            df: DataFrame con los tipos ya convertidos.

        Returns:
            pd.DataFrame: DataFrame limpio.
        """
        df = df.copy()

        # Eliminar columnas que no se utilizaran
        columns_to_drop =[
            "datetime",
            "tz_time"
        ]

        df = df.drop(
            columns=columns_to_drop,
            errors="ignore"
        )

        # Eliminar las filas completamente vacias
        df = df.dropna(how="all")

        # Eliminar duplicados exactos
        df = df.drop_duplicates()

        # Reiniciar el indice
        df.reset_index(drop=True)

        return df

    def create_derived_columns(self,df:pd.DataFrame)->pd.DataFrame:
        """
        Crea columnas derivadas a partir de la fecha y hora UTC.

        Args:
            df: DataFrame limpio.

        Returns:
            pd.DataFrame: DataFrame enriquecido.
        """
        df =df.copy()

        timestamp = df["datetime_utc"]

        df["year"] = timestamp.dt.year
        df["month"] = timestamp.dt.month
        df["day"] = timestamp.dt.day
        df["hour"] = timestamp.dt.hour
        df["weekday"] = timestamp.dt.day_name()

        return df


    