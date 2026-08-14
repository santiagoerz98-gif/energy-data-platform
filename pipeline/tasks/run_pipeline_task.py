from prefect import task, get_run_logger
from pipeline.errors import PipelineError
from pipeline.run_pipeline import run_pipeline

@task(retries=3, retry_delay_seconds=30, name="run-pipeline-task")
def run_pipeline_task(
    indicator_id,
    start_date = None,
    end_date = None,
    time_trunc = None,
    geo_ids=None,
):
    """
    Run a pipeline task for a given indicator and date range.

    Args:
        indicator_id (str): The ID of the indicator to run the pipeline for.
        start_date (str, optional): The start date for the data processing. Defaults to None.
        end_date (str, optional): The end date for the data processing. Defaults to None.
        time_trunc (str, optional): The time truncation level (e.g., 'day', 'month'). Defaults to None.
        geo_ids (list, optional): A list of geographic IDs to filter the data. Defaults to None.
    """
    logger = get_run_logger()
    try:
        result = run_pipeline(indicator_id, start_date, end_date, time_trunc, geo_ids)
        logger.info(f"Indicador {indicator_id} cargado: {result['loaded_rows']} filas")
        return result
    except PipelineError as e:
        logger.error(f"Fallo en indicador {indicator_id}: {e}")
        raise