import logging
import os
import re

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    def load_dotenv():
        pass

class CleanLoggingFilter(logging.Filter):
    """Filter to remove Chinese characters from log messages"""
    
    def __init__(self):
        super().__init__()
        # Map Chinese characters to English equivalents
        self.chinese_replacements = {
            '逃': '[BUILD]',        # Package/Build
            '楳': '[MERGE]',        # Shuffle/Merge
            '圸': '[FLAG]',         # Feature flags
            'ｧｬ': '[DNA]',         # Semantic change
            '女・・': '[WIP]',      # Work in progress
            '竢ｪ': '[REVERT]',      # Rewind/Revert
            '卵・・': '[REMOVE]',   # Wastebasket/Remove
            '筮・ｸ・': '[UPDATE]',  # Arrow up/down for deps
        }
    
    def filter(self, record):
        """Clean Chinese characters from log messages"""
        if hasattr(record, 'msg') and record.msg:
            # Clean the message
            cleaned_msg = str(record.msg)
            for chinese_char, english_replacement in self.chinese_replacements.items():
                cleaned_msg = cleaned_msg.replace(chinese_char, english_replacement)
            
            # Update the record
            record.msg = cleaned_msg
        
        return True  # Always allow the log through (after cleaning)

def setup_logging():
    """Configures logging for the application."""
    load_dotenv()
    log_level_name = os.getenv('LOG_LEVEL', 'INFO').upper()
    log_level = getattr(logging, log_level_name, logging.INFO)

    log_format = '%(asctime)s | %(levelname)-8s | %(module)-15s | %(funcName)-20s | %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'

    # Create handlers with Chinese character filtering
    console_handler = logging.StreamHandler()
    console_handler.addFilter(CleanLoggingFilter())
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=[
            console_handler  # Log to console with Chinese character cleaning
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
