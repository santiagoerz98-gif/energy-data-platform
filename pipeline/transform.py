from pathlib import Path
import json
import logging

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