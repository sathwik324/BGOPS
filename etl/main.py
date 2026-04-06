import os
import sys
import logging
import time

# Ensure imports work from the project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from etl import fetch_data
from etl import transform_data
from etl import load_data

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("etl_main")

def main():
    logger.info("=====================================================")
    logger.info("🏀 STARTING DAILY BGOPS DAILY DATA REFRESH 🏀")
    logger.info("=====================================================")
    start_time = time.time()

    try:
        # STEP 1: FETCH
        logger.info(">>> STEP 1/3: Fetching latest from NBA API...")
        fetch_data.main()

        # STEP 2: TRANSFORM
        logger.info(">>> STEP 2/3: Transforming and cleaning new data...")
        transform_data.main()

        # STEP 3: LOAD
        logger.info(">>> STEP 3/3: Upserting fresh data into MySQL Database...")
        load_data.main()

        duration = time.time() - start_time
        logger.info("=====================================================")
        logger.info(f"✅ DATA REFRESH COMPLETE IN {duration:.2f} SECONDS ✅")
        logger.info("=====================================================")

    except Exception as e:
        logger.error("❌ ETL PIPELINE FAILED: %s", e, exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
