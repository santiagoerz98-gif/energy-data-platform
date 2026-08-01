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
        df = self.clean_data(df)
        

        return {
            "df": df,
            "metadata": metadata
        }

    def build_demand_dataframe(self,filepath:Path)->pd.DataFrame:
        """
        Construye un DataFrame específico para la demanda a partir de un archivo JSON de la capa Raw.

        Args:
            filepath: Ruta del archivo JSON.

        Returns:
            pd.DataFrame: DataFrame final listo para el Data Warehouse.
        """
        df = self.build_dataframe(filepath)["df"]
        metadata = self.build_dataframe(filepath)["metadata"]

        # Crea columna "measurment_type" basada en el metadata del indicador
        df["measurement_type"] = metadata.get("measurement_type")

        
        return df

    def build_generation_dataframe(self,filepath:Path)->pd.DataFrame:
        """
        Construye un DataFrame específico para la generación a partir de un archivo JSON de la capa Raw.

        Args:
            filepath: Ruta del archivo JSON.

        Returns:
            pd.DataFrame: DataFrame final listo para el Data Warehouse.
        """
        df = self.build_dataframe(filepath)["df"]
        metadata = self.build_dataframe(filepath)["metadata"]

        # Crea columna "energy_source" basada en el metadata del indicador
        df["energy_source"] = metadata.get("short_name")

        
        return df
    
    def build_demand_dataset(self,folder:Path)->pd.DataFrame:
        """
        Crea el dataset "demand" final a partir de los archivos JSON en una carpeta.

        Args:
            folder: Ruta de la carpeta con los archivos JSON.

        Returns:
            pd.DataFrame: DataFrame resultante de la concatenación.
        """

        df_list = []

        # Itera sobre todos los archivos JSON en la carpeta y construye un DataFrame para cada uno
        for file in folder.iterdir():
            if file.suffix == ".json":
                df = self.build_demand_dataframe(file)
                df_list.append(df)

        return pd.concat(df_list,ignore_index=True)

    def build_generation_dataset(self,folder:Path)->pd.DataFrame:
        """
        Crea el dataset "generation" final a partir de los archivos JSON en una carpeta.

        Args:
            folder: Ruta de la carpeta con los archivos JSON.

        Returns:
            pd.DataFrame: DataFrame resultante de la concatenación.
        """

        df_list = []

        # Itera sobre todos los archivos JSON en la carpeta y construye un DataFrame para cada uno
        for file in folder.iterdir():
            if file.suffix == ".json":
                df = self.build_generation_dataframe(file)
                df_list.append(df)

        return pd.concat(df_list,ignore_index=True)
    