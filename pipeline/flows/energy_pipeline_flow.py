from prefect import flow, get_run_logger, unmapped
from pipeline.tasks.run_pipeline_task import run_pipeline_task
from pipeline.tasks.populate_dw_task import populate_dw_task

@flow(name="energy-pipeline-flow")
def energy_pipeline_flow(indicator_ids:list[int], start_date=None, end_date=None, time_trunc=None, geo_ids=None):
    logger = get_run_logger()
    logger.info(f"Starting energy pipeline flow for indicator_ids: {indicator_ids}")
    future_results = run_pipeline_task.map(
        indicator_id=indicator_ids,
        start_date=unmapped(start_date),
        end_date=unmapped(end_date),
        time_trunc=unmapped(time_trunc),
        geo_ids=unmapped(geo_ids)
    )
    results = future_results.result()

    populate_dw_task.submit(wait_for=future_results).result()

    logger.info(f"Energy pipeline flow completed for indicator_ids: {indicator_ids} with results: {results}")
    return results

if __name__ == "__main__":
    import argparse
    from config.logging_config import setup_logging

    parser = argparse.ArgumentParser(description="Run the energy pipeline flow.")
    parser.add_argument("--indicator_ids", nargs="*", type=int, required=True, help="List of indicator IDs to process.")
    parser.add_argument("--start_date", type=str, help="Start date for the data extraction.")
    parser.add_argument("--end_date", type=str, help="End date for the data extraction.")
    parser.add_argument("--time_trunc", type=str, help="Time truncation for the data.")
    parser.add_argument("--geo_ids", nargs="*", type=int, help="List of geographic IDs to process.")

    args = parser.parse_args()
    setup_logging()

    energy_pipeline_flow(
        indicator_ids=args.indicator_ids,
        start_date=args.start_date,
        end_date=args.end_date,
        time_trunc=args.time_trunc,
        geo_ids=args.geo_ids
    )