from config.settings import API_KEY, BASE_URL, TIMEOUT
import requests

class EsiosClient:
    def __init__(self):
        """Inicializa el cliente de la API de ESIOS con la clave de API, la URL base y el tiempo de espera.
        Raises:
            ValueError: Si la clave de API no está definida.
        """
        self.base_url = BASE_URL
        self.timeout = TIMEOUT
        self.headers = {
            "Accept": "application/json; application/vnd.esios-api-v1+json",
            "Content-Type": "application/json",
            "x-api-key": API_KEY
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers) # Actualiza los encabezados de la sesión con los encabezados definidos.

    def get(self, endpoint: str, params: dict | None = None) -> dict: 
        """
        Realiza una petición GET a la API de ESIOS.

        Args:
        endpoint (str): Endpoint relativo de la API.
        params (dict, optional): Parámetros de consulta.

        Returns:
        dict: Respuesta JSON convertida a un diccionario.

        Raises:
            requests.exceptions.HTTPError: Si la API devuelve un código HTTP de error.
            requests.exceptions.Timeout: Si la petición excede el tiempo máximo.
            requests.exceptions.RequestException: Para cualquier otro error de conexión.
        """
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        try:
            response = self.session.get(
                url, 
                params=params, 
                timeout=self.timeout
            )

            response.raise_for_status()  # Lanza un error para códigos de estado HTTP

            return response.json()  # Devuelve la respuesta JSON como diccionario
        except requests.exceptions.Timeout:
            raise requests.exceptions.Timeout(
                f"La peticion a {url} excedió el tiempo máximo de espera de {self.timeout} segundos."
            )
            
        except requests.exceptions.HTTPError as e:
            raise requests.exceptions.HTTPError(
                f"Error HTTP {response.status_code} al acceder a {url}: {response.text}"
            ) from e
            
        except requests.exceptions.RequestException as e:
            raise requests.exceptions.RequestException(
                f"Error al conectar con la API de ESIOS: {e}"
            ) from e
        
    def get_indicator(
            self,
            indicator_id: int,
            start_date: str | None = None,
            end_date: str | None = None,
            time_trunc: str | None = None,
            geo_ids: list[int] | None = None
    ) -> dict:
        """ Obtiene los datos de un indicador específico de la API de ESIOS.
        Args:
            indicator_id (int): ID del indicador a obtener.
            start_date (str, optional): Fecha de inicio.
            end_date (str, optional): Fecha de fin.
            time_trunc (str, optional): Truncamiento temporal.
            geo_ids (list, optional): IDs geográficos.

        Returns:
            dict: Respuesta JSON convertida a un diccionario.
        """
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "time_trunc": time_trunc,
            "geo_ids": geo_ids
        }
        params = {key: value for key, value in params.items() if value is not None}

        return self.get(f"indicators/{indicator_id}", params=params)