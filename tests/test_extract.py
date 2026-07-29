
from pipeline.extract import Extractor
from services.esios_client import EsiosClient

# Instancia del cliente de ESIOS
client = EsiosClient()

# Instancia del extractor con el cliente de ESIOS
extractor = Extractor(client)

data = extractor.extract_indicator(indicator_id=548, start_date="2023-01-01", end_date="2023-01-31")

print(data)

