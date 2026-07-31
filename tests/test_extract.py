
from pipeline.extract import Extractor
from services.esios_client import EsiosClient

# Instancia del cliente de ESIOS
client = EsiosClient()

# Instancia del extractor con el cliente de ESIOS
extractor = Extractor(client)

data = extractor.extract_indicator(indicator_id=2053, start_date="2026-07-01", end_date="2026-07-30")

print(data)

