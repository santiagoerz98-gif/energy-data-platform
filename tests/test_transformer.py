from pathlib import Path
from pipeline.transform import Transformer

transformer = Transformer()

filepath = Path("data/raw/esios/2026/07/30/Generación T.Real nuclear/indicator_549_20260701_20260730_20260730_151108.json")

data = transformer.read_raw(filepath=filepath)

normalize_data = transformer.normalize(data)

normalize_data = transformer.convert_types(normalize_data)

clean_data = transformer.clean_data(normalize_data)

enriched_data = transformer.create_derived_columns(clean_data)

print(enriched_data.head())