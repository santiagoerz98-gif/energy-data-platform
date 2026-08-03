import argparse
import logging

from config.database import engine
from services.esios_client import EsiosClient
from pipeline.extract import Extractor
from pipeline.transform import Transformer
from pipeline.quality import DataQualityValidator
from pipeline.load import Loader

logger = logging.getLogger(__name__)

def run_pipeline(
        indicator_id: int,
        start_date: str | None = None,
        end_date: str | None = None,
        time_trunc: str | None = None,
        geo_ids: list[int] | None = None
)-> dict:
    """
    Run the ETL pipeline for a given indicator and date range.

    Args:
        indicator_id: ID of the indicator to process.
        start_date: Start date for the data extraction (optional).
        end_date: End date for the data extraction (optional).
        time_trunc: Time truncation for the data (optional).
        geo_ids: List of geographic IDs to filter the data (optional).

    Returns:
        dict: A dictionary containing the results of the pipeline execution.
    """

    client = EsiosClient()
    extractor = Extractor(client)
    transformer = Transformer()
    validator = DataQualityValidator()
    loader = Loader(engine)

    # 1. Extract data
    logger.info(f"Starting data extraction for indicator {indicator_id}...")

    extraction = extractor.extract_indicator(indicator_id, start_date, end_date, time_trunc, geo_ids)

    filepath = extraction['filepath']

    # 2. Transform data
    logger.info(f"Starting data transformation for indicator {indicator_id}...")

    transformation = transformer.build_dataframe(filepath)
    df, metadata, metricas_limpieza = transformation['df'], transformation['metadata'], transformation['metricas_limpieza']

    # 3. Validate data quality (Raise valueError and stop the pipeline if validation fails)
    logger.info(f"Starting data quality validation for indicator {indicator_id}...")

    reporte = validator.validate(df, metadata["name"],metricas_limpieza)

    # 4. Load data into the staging schema
    logger.info(f"Starting data loading for indicator {indicator_id}...")
    table_name = metadata["dataset"]
    loader.load_staging(
        df, 
        table_name=table_name,
        indicator_id=indicator_id,
        start_date=start_date,
        end_date=end_date
    )

    return {
        "indicator_id": indicator_id,
        "quality_report": reporte,
        "loaded_rows": len(df)
    }


def main(): 
    parser = argparse.ArgumentParser(description="Ejecuta el pipeline ESIOS para un indicador") 
    parser.add_argument("indicator_id", type=int)
    parser.add_argument("--start-date")
    parser.add_argument("--end-date")
    parser.add_argument("--time-trunc")
    parser.add_argument("--geo-ids", type=int, nargs="*")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    run_pipeline(
        args.indicator_id, args.start_date, args.end_date, args.time_trunc, args.geo_ids
    )


if __name__ == "__main__":
    main()