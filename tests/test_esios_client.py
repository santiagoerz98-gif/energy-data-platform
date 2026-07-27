from services.esios_client import EsiosClient

client = EsiosClient()

response_dict = client.get_indicator(indicator_id=1293, start_date="2023-01-01", end_date="2023-01-31", time_trunc="day", geo_ids=8741)

print(response_dict)