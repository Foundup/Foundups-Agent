import logging
import os
from dotenv import load_dotenv

def setup_logging():
    """Configures logging for the application."""
    load_dotenv()
    log_level_name = os.getenv('LOG_LEVEL', 'INFO').upper()
    log_level = getattr(logging, log_level_name, logging.INFO)

    log_format = '%(asctime)s | %(levelname)-8s | %(module)-15s | %(funcName)-20s | %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'

    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler() # Log to console
            # TODO: Add FileHandler if needed, perhaps rotating logs
            # logging.FileHandler("agent.log")
        ]
    )

    # Suppress overly verbose logs from libraries if necessary
    logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)
    logging.getLogger('google.auth.transport.requests').setLevel(logging.WARNING)

    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured with level: {log_level_name}")

# Call setup_logging() when this module is imported?
# Or call it explicitly in main.py - let's do explicit for clarity.
# setup_logging()
