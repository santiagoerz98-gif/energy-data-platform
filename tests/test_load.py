from pathlib import Path
from pipeline.quality import DataQualityValidator
from pipeline.transform import Transformer
from pipeline.load import Loader
from config.database import engine

transformer = Transformer()
validator = DataQualityValidator(report_dir=Path(r"data\raw\processed\reports"))
loader = Loader(engine)

filepath = Path(r"data\raw\esios\2026\08\01\demand\indicator_1293_Demandareal_20260701_20260730_20260801_152252.json")

results = transformer.build_dataframe(filepath=filepath)

indicator_name = results["metadata"]["name"]

quality_report = validator.validate(df=results["df"], indicator_name=indicator_name, metricas_limpieza=results["metricas_limpieza"])

loader.load_staging(df=results["df"], table_name=f"staging_{results['metadata']['dataset']}", schema="staging")

