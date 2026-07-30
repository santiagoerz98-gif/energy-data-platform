from pathlib import Path
from pipeline.transform import Transformer

transformer = Transformer()

filepath = Path("./data/raw/esios/2026/07/29/Demanda prevista/indicator_544_20230101_20230131_20260729_131359.json")

data = transformer.read_raw(filepath=filepath)

print(type(data))