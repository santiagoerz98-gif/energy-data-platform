import logging
from config.settings import API_KEY, BASE_URL, ESIOS_RETRY_TOTAL, ESIOS_BACKOFF_FACTOR, ESIOS_CONNECT_TIMEOUT, ESIOS_READ_TIMEOUT, ESIOS_RETRY_STATUS_FORCELIST
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

class EsiosClient:
    def __init__(self):
        """Inicializa el cliente de la API de ESIOS con la clave de API, la URL base y el tiempo de espera.
        Raises:
            ValueError: Si la clave de API no está definida.
        """
        if not API_KEY:
            raise ValueError("La clave de API de ESIOS no está definida. Por favor, configure la variable de entorno 'ESIOS_API_KEY'.")
        
        self.base_url = BASE_URL
        self.connect_timeout = ESIOS_CONNECT_TIMEOUT
        self.read_timeout = ESIOS_READ_TIMEOUT
        self.timeout = (self.connect_timeout, self.read_timeout)

        self.headers = {
            "Accept": "application/json; application/vnd.esios-api-v1+json",
            "Content-Type": "application/json",
            "x-api-key": API_KEY
        }

        self.session = requests.Session()
        self.session.headers.update(self.headers) # Actualiza los encabezados de la sesión con los encabezados definidos.

        retry = Retry(
            total=ESIOS_RETRY_TOTAL, # Número total de reintentos permitidos.
            connect=ESIOS_RETRY_TOTAL, # Número de reintentos permitidos para errores de conexión.
            read=ESIOS_RETRY_TOTAL, # Número de reintentos permitidos para errores de lectura.
            status=ESIOS_RETRY_TOTAL, # Número de reintentos permitidos para errores de estado HTTP.
            backoff_factor=ESIOS_BACKOFF_FACTOR, # Factor de retroceso exponencial para el tiempo de espera entre reintentos.
            status_forcelist=ESIOS_RETRY_STATUS_FORCELIST, # Lista de códigos de estado HTTP que activan un reintento.
            allowed_methods=["GET"], # Métodos HTTP permitidos para reintentos.
            respect_retry_after_header=True, # Indica si se debe respetar el encabezado Retry-After en las respuestas HTTP.
            raise_on_status=False # Indica si se debe lanzar una excepción para códigos de estado HTTP.
        )

        self.adapter = HTTPAdapter(
            max_retries=retry, 
            pool_connections=10, 
            pool_maxsize=10, 
            pool_block=True
        ) # Configura un adaptador para reintentos de conexión.

        self.session.mount("https://", self.adapter) # Configura la sesión para reintentar hasta 5 veces en caso de fallos de conexión.
        self.session.mount("http://", self.adapter) # Configura la sesión para reintentar hasta 5 veces en caso de fallos de conexión.

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
            logger.info("ESIOS GET %s params=%s", url, params)
            response = self.session.get(
                url, 
                params=params, 
                timeout=self.timeout
            )

            response.raise_for_status()  # Lanza un error para códigos de estado HTTP
            try:
                return response.json()  # Devuelve la respuesta JSON como diccionario
            except ValueError as exc:
                raise requests.exceptions.RequestException(
                    f"Error al parsear la respuesta JSON de {url}: {exc}"
                ) from exc
            
        except requests.exceptions.Timeout as exc:
            logger.warning("Timeout al acceder a %s: %s", url, exc)
            raise requests.exceptions.Timeout(
                f"La peticion a {url} excedió el tiempo máximo de espera de {self.timeout} segundos."
                f"(connect={self.connect_timeout}s, read={self.read_timeout}s)."
            ) from exc
            
        except requests.exceptions.HTTPError as exc:
            status_code = getattr(exc.response, 'status_code', None)
            response_text = getattr(exc.response, 'text', "")
            logger.warning("Error HTTP %s al acceder a %s: %s", status_code, url, response_text)

            raise requests.exceptions.HTTPError(
                f"Error HTTP {status_code} al acceder a {url}: {response_text}"
            ) from exc
            
        except requests.exceptions.RequestException as exc:
            logger.exception("Error al conectar con la API de ESIOS: %s", exc)
            raise requests.exceptions.RequestException(
                f"Error al conectar con la API de ESIOS: {exc}"
            ) from exc
        
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