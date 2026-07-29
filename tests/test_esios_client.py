from services.esios_client import EsiosClient
import json

client = EsiosClient()

response_dict = client.get(f"indicators",{"taxonomy_terms":["Generacion","Demanda"]})

with open("./data/raw/list_of_indicators_by_taxonomy_terms_generacion.json","w",encoding="utf-8") as f:
    json.dump(response_dict,f,ensure_ascii=False, indent=4)