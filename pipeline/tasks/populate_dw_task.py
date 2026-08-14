from prefect import task, get_run_logger
from pipeline.populate_dw import run_populate_dw

@task(name="populate-dw-task", retries=1, retry_delay_seconds=60)
def populate_dw_task():
    logger = get_run_logger()
    logger.info("Starting populate DW task")
    run_populate_dw()
    logger.info("populate DW task completed successfully")