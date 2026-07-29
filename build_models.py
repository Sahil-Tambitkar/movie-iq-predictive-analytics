import logging

from src.pipeline import run_pipeline

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting analysis pipeline")
    run_pipeline()
    logger.info("Analysis pipeline completed")
