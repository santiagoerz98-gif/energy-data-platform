import os
import json
from pathlib import Path
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class DataQualityValidator:
    """
    Clase para validar la calidad de los datos en un DataFrame y generar reportes de calidad.
    """

    def __init__(self, report_dir: Path = Path(r"data\raw\processed\reports")):
        self.report_dir = report_dir
        os.makedirs(self.report_dir, exist_ok=True) # Asegura que el directorio de reportes exista

        self.logger = logger
    def validate(self, df: pd.DataFrame,indicator_name:str, metricas_limpieza:dict) -> dict:
        """
        Valida la calidad de los datos en el DataFrame y genera un reporte de calidad.

        Args:
            df (pd.DataFrame): DataFrame a validar.
            indicator_name (str): Nombre del indicador para el que se está validando la calidad.
            metricas_limpieza (dict): Diccionario con métricas de limpieza de datos.

        Returns:
            dict: Diccionario con las métricas de calidad de los datos.
        """
        #Estructura del reporte de calidad
        reporte = {
            "timestamp": pd.Timestamp.now().isoformat(),
            "indicator_name": indicator_name,
            "metricas": metricas_limpieza,
            "estado": "EXITOSO"
        }
        # Reglas criticas de calidad de datos (Si fallan el pipeline se detiene)
        if metricas_limpieza["filas_finales"] == 0:
            reporte["estado"] = "FALLIDO"
            reporte["mensaje"] = "El DataFrame resultante está vacío después de la limpieza de datos."
            self._guardar_reporte(reporte, indicator_name)
            raise ValueError(f"Data Quality Error: {reporte['mensaje']}")
        
        if df["value"].isnull().any():
            reporte["estado"] = "FALLIDO"
            reporte["mensaje"] = "Existen valores nulos en la columna 'value' después de la limpieza."
            self._guardar_reporte(reporte, indicator_name)
            raise ValueError(f"Data Quality Error: {reporte['mensaje']}")

        if (df["value"] < 0).any():
            reporte["estado"] = "FALLIDO"
            reporte["mensaje"] = "Existen valores negativos en la columna 'value' después de la limpieza."
            self._guardar_reporte(reporte, indicator_name)
            raise ValueError(f"Data Quality Error: {reporte['mensaje']}")

        

        # Guardar el reporte de calidad en un archivo JSON
        self._guardar_reporte(reporte, indicator_name)

        return reporte

    def _guardar_reporte(self, reporte: dict, indicator_name: str):
        """
        Guarda el reporte de calidad en un archivo JSON.

        Args:
            reporte (dict): Diccionario con el reporte de calidad.
            indicator_name (str): Nombre del indicador para el que se está generando el reporte.
        """
        fecha = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        filename = f"quality_report_indicator_{indicator_name}_{fecha}.json"
        filepath = os.path.join(self.report_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(reporte, f, ensure_ascii=False, indent=4)

        self.logger.info(f"Reporte de calidad guardado en: {filepath}")