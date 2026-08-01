from pathlib import Path
from pipeline.transform import Transformer

transformer = Transformer()

folder = Path(r"data\raw\esios\2026\08\01\demand")

demand_df = transformer.build_demand_dataset(folder=folder)


print(demand_df.describe())
print(demand_df.info())  
print(demand_df.head())
print(demand_df.tail())