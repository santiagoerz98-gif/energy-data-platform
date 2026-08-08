from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("ESIOS_API_KEY")

BASE_URL = "https://api.esios.ree.es"

TIMEOUT = 30

ESIOS_RETRY_TOTAL = 5
ESIOS_BACKOFF_FACTOR = 1.0
ESIOS_CONNECT_TIMEOUT = 5
ESIOS_READ_TIMEOUT = 30
ESIOS_RETRY_STATUS_FORCELIST = [429, 500, 502, 503, 504]