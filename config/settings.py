from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("ESIOS_API_KEY")

BASE_URL = "https://api.esios.ree.es"

API_DEMAND_URL = "http://127.0.0.1:8000/demand"

TIMEOUT = 30

ESIOS_RETRY_TOTAL = 5
ESIOS_BACKOFF_FACTOR = 1.0
ESIOS_CONNECT_TIMEOUT = 5
ESIOS_READ_TIMEOUT = 30
ESIOS_RETRY_STATUS_FORCELIST = [429, 500, 502, 503, 504]

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "logs/pipeline.log")
LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"