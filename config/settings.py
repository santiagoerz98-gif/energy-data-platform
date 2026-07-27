from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("ESIOS_API_KEY")

BASE_URL = "https://api.esios.ree.es"

TIMEOUT = 30