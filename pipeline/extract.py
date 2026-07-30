from datetime import datetime
import json
from pathlib import Path
from services.esios_client import EsiosClient
import logging

logger = logging.getLogger(__name__)


class Extractor():
    def __init__(self, client:EsiosClient):
        """
        Inicializa el extractor con un cliente de ESIOS.
        :param client: Instancia del cliente de ESIOS para realizar las solicitudes a la API.
        """
        self.client = client

    def extract_indicator(
            self,
            indicator_id: int,
            start_date: str | None = None,
            end_date: str | None = None,
            time_trunc: str | None = None,
            geo_ids: list[int] | None = None)-> dict:
        """
        Extrae los datos de un indicador desde la API de ESIOS y almacena
        la respuesta original en la capa Raw.

        Args:
            indicator_id: Identificador del indicador.
            start_date: Fecha inicial (ISO-8601).
            end_date: Fecha final (ISO-8601).
            time_trunc: Nivel de agregación temporal.
            geo_ids: Lista de identificadores geográficos.

        Returns:
            dict: Respuesta JSON completa obtenida de la API.
        """
        # Llamada al cliente para obtener los datos del indicador
        data = self.client.get_indicator(
            indicator_id, 
            start_date=start_date, 
            end_date=end_date, 
            time_trunc=time_trunc,
            geo_ids=geo_ids)

        indicator_name = data["indicator"]['name']
        indicator_short_name = data["indicator"]["short_name"]

        # Obtener la fecha y hora actual para el timestamp del archivo
        extraction_date = datetime.now()
        timestamp = extraction_date.strftime("%Y%m%d_%H%M%S")

        # Crear la ruta del directorio para almacenar los datos extraídos
        raw_dir = self._build_raw_directory(extraction_date,indicator_name)
        
        # Asegurarse de que el directorio exista
        raw_dir.mkdir(parents=True, exist_ok=True)

        # Crear el nombre del archivo basado en el indicador, fechas y timestamp
        filename = self._build_filename(
            indicator_id=indicator_id,
            indicator_short_name=indicator_short_name,
            start_date=start_date,
            end_date=end_date,
            timestamp=timestamp
        )

        # Crear la ruta completa del archivo
        filepath = raw_dir / filename
        
        # Guardar los datos extraídos en un archivo JSON
        try:
            with filepath.open("w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            logger.info(f"Datos almacenados correctamente en '{filepath}'.")

        except OSError as e:
            logger.exception(f"No se pudo guardar el archivo '{filepath}'.")
            raise

        return {
             "name":indicator_name,
             "data":data,
             "filepath":filepath
        }

    def _build_raw_directory(self,extraction_date:datetime,indicator_name:str)-> Path:
        """
            Construye el Path al directorio para guardar los datos extraidos
        """
        raw_dir = (
            Path("data")
            / "raw"
            / "esios"
            / str(extraction_date.year)
            / f"{extraction_date.month:02d}"
            / f"{extraction_date.day:02d}"
            / f"{indicator_name}"
        )
        return raw_dir

    def _format_date_for_filename(self, date_str: str | None) -> str: 
            """
            Formatea una fecha en formato YYYY-MM-DD a un formato adecuado para nombres de archivo.
            :param date_str: Fecha en formato YYYY-MM-DD.
            :return: Fecha formateada como YYYYMMDD.
            """
            if date_str is None:
                return "all"
            return date_str.replace("-", "").replace(":", "")

    def _build_filename(
            self,
            indicator_id:int,
            indicator_short_name:str,
            start_date:str | None, 
            end_date:str | None,
            timestamp:str
        )->str:
        """
            Construye el nombre del archivo JSON de la capa RAW
        """
        filename =  f"indicator_{indicator_id}_{indicator_short_name.replace(' ','')}_{self._format_date_for_filename(start_date)}_{self._format_date_for_filename(end_date)}_{timestamp}.json"
        return filename
        
         

    