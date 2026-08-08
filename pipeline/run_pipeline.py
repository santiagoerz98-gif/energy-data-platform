import argparse
import logging
import time
import uuid

from config.database import engine
from config.logging_config import setup_logging
from pipeline.errors import (
    ExtractStageError,
    TransformStageError,
    QualityStageError,
    LoadStageError,
    PipelineError,
)
from pipeline.extract import Extractor
from pipeline.load import Loader
from pipeline.quality import DataQualityValidator
from pipeline.transform import Transformer
from services.esios_client import EsiosClient

logger = logging.getLogger(__name__)

def _log_event(level: str, event: str, **ctx):
    payload = {"event": event, **ctx}
    getattr(logger, level)(payload)

def run_pipeline(indicator_id, start_date=None, end_date=None, time_trunc=None, geo_ids=None):
    run_id = str(uuid.uuid4())
    t0 = time.perf_counter()

    _log_event(
        "info",
        "pipeline.started",
        run_id=run_id,
        indicator_id=indicator_id,
        start_date=start_date,
        end_date=end_date,
        time_trunc=time_trunc,
        geo_ids=geo_ids,
    )

    client = EsiosClient()
    extractor = Extractor(client)
    transformer = Transformer()
    validator = DataQualityValidator()
    loader = Loader(engine)

    try:
        s = time.perf_counter()
        _log_event("info", "stage.started", run_id=run_id, stage="extract")
        extraction = extractor.extract_indicator(indicator_id, start_date, end_date, time_trunc, geo_ids)
        filepath = extraction["filepath"]
        _log_event(
            "info",
            "stage.success",
            run_id=run_id,
            stage="extract",
            duration_ms=round((time.perf_counter() - s) * 1000),
            filepath=str(filepath),
        )
    except Exception as e:
        _log_event("error", "stage.failed", run_id=run_id, stage="extract", error=str(e))
        raise ExtractStageError(f"extract failed for indicator {indicator_id}") from e

    try:
        s = time.perf_counter()
        _log_event("info", "stage.started", run_id=run_id, stage="transform")
        transformation = transformer.build_dataframe(filepath)
        df = transformation["df"]
        metadata = transformation["metadata"]
        metricas_limpieza = transformation["metricas_limpieza"]
        _log_event(
            "info",
            "stage.success",
            run_id=run_id,
            stage="transform",
            duration_ms=round((time.perf_counter() - s) * 1000),
            rows_out=len(df),
            retention=metricas_limpieza.get("retencion"),
        )
    except Exception as e:
        _log_event("error", "stage.failed", run_id=run_id, stage="transform", error=str(e))
        raise TransformStageError(f"transform failed for indicator {indicator_id}") from e

    try:
        s = time.perf_counter()
        _log_event("info", "stage.started", run_id=run_id, stage="quality")
        reporte = validator.validate(df, metadata["name"], metricas_limpieza)
        _log_event(
            "info",
            "stage.success",
            run_id=run_id,
            stage="quality",
            duration_ms=round((time.perf_counter() - s) * 1000),
            quality_status=reporte.get("estado"),
        )
    except Exception as e:
        _log_event("error", "stage.failed", run_id=run_id, stage="quality", error=str(e))
        raise QualityStageError(f"quality failed for indicator {indicator_id}") from e

    try:
        s = time.perf_counter()
        _log_event("info", "stage.started", run_id=run_id, stage="load")
        loader.load_staging(
            df,
            table_name=metadata["dataset"],
            indicator_id=indicator_id,
            start_date=start_date,
            end_date=end_date,
        )
        _log_event(
            "info",
            "stage.success",
            run_id=run_id,
            stage="load",
            duration_ms=round((time.perf_counter() - s) * 1000),
            rows_loaded=len(df),
            table_name=metadata["dataset"],
        )
    except Exception as e:
        _log_event("error", "stage.failed", run_id=run_id, stage="load", error=str(e))
        raise LoadStageError(f"load failed for indicator {indicator_id}") from e

    total_ms = round((time.perf_counter() - t0) * 1000)
    _log_event(
        "info",
        "pipeline.success",
        run_id=run_id,
        indicator_id=indicator_id,
        total_duration_ms=total_ms,
        loaded_rows=len(df),
    )

    return {
        "run_id": run_id,
        "indicator_id": indicator_id,
        "quality_report": reporte,
        "loaded_rows": len(df),
        "duration_ms": total_ms,
    }

def main():
    parser = argparse.ArgumentParser(description="Ejecuta el pipeline ESIOS para un indicador")
    parser.add_argument("indicator_id", type=int)
    parser.add_argument("--start-date")
    parser.add_argument("--end-date")
    parser.add_argument("--time-trunc")
    parser.add_argument("--geo-ids", type=int, nargs="*")
    args = parser.parse_args()

    setup_logging()

    try:
        run_pipeline(args.indicator_id, args.start_date, args.end_date, args.time_trunc, args.geo_ids)
    except PipelineError:
        logger.exception("pipeline.failed")
        raise

if __name__ == "__main__":
    main()