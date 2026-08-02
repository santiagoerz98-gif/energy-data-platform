from pathlib import Path
import json
import logging
import pandas as pd

from config.ids_catalog import INDICATORS

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
        filas_iniciales = len(df)

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
        filas_vacias = df.isnull().all(axis=1).sum()
        df = df.dropna(how="all")

        # Limpieza de valores nulos y negativos en la columna "value"
        nulos_en_value = df["value"].isnull().sum()
        df = df.dropna(subset=["value"])
        negativos_en_value = (df["value"] < 0).sum()
        df = df[df["value"] >= 0]

        # Eliminar duplicados exactos
        duplicados_eliminados = df.duplicated().sum()
        df = df.drop_duplicates()

        # Retencion
        retencion = len(df) / filas_iniciales * 100

        # Reiniciar el indice
        df.reset_index(drop=True)

        metricas_limpieza = {
            "filas_iniciales": filas_iniciales,
            "filas_vacias_eliminadas": filas_vacias,
            "nulos_en_value_eliminados": nulos_en_value,
            "negativos_en_value_eliminados": negativos_en_value,
            "duplicados_eliminados": duplicados_eliminados,
            "filas_finales": len(df),
            "retencion": retencion
        }

        return {"df": df, "metricas_limpieza": metricas_limpieza}

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

    def build_dataframe(self,filepath:Path)->pd.DataFrame:
        """
        Construye un DataFrame completo a partir de un archivo JSON de la capa Raw.

        Args:
            filepath: Ruta del archivo JSON.

        Returns:
            pd.DataFrame: DataFrame final listo para el Data Warehouse.
        """
        # Leer el archivo JSON 
        data = self.read_raw(filepath)
        filename = filepath.stem
        parts = filename.split("_")
        indicator_id = int(parts[1])
        metadata = INDICATORS.get(indicator_id)

        # Normaliza, convierte tipos y limpia los datos
        df = self.normalize(data)
        df = self.convert_types(df)
        df = self.clean_data(df)["df"]
        metricas_limpieza = self.clean_data(df)["metricas_limpieza"]

        # Crea columna "measurment_type" basada en el metadata del indicador
        df["measurement_type"] = metadata.get("measurement_type")

        # Crea columna "short_name" basada en el metadata del indicador
        df["short_name"] = metadata.get("short_name")

        return {
            "df": df,
            "metadata": metadata,
            "metricas_limpieza": metricas_limpieza
        }
    