import logging
from pathlib import Path
from config.database import engine

logger = logging.getLogger(__name__)

SQL_PATH = Path(__file__).resolve().parent.parent / "database" / "populate_dw.sql"

def run_populate_dw():
    logger.info("Running populate DW task")
    sql = SQL_PATH.read_text(encoding="utf-8")
    raw_connection = engine.raw_connection()
    try:
        raw_connection.autocommit = True
        with raw_connection.cursor() as cursor:
            cursor.execute(sql)
        logger.info("populate DW task completed successfully")
    finally:
        raw_connection.close()