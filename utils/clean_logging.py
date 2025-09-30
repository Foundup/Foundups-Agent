#!/usr/bin/env python3
"""
Clean Logging Utility - Ensures English-only log prefixes

Prevents Chinese characters from appearing in daemon logs.
"""

import re

def clean_log_message(message: str) -> str:
    """Clean Chinese characters from log messages"""
    replacements = {
        '逃': '[BUILD]',
        '楳': '[MERGE]', 
        '圸': '[FLAG]',
        'ｧｬ': '[DNA]',
        '女・・': '[WIP]',
        '竢ｪ': '[REVERT]',
        '卵・・': '[REMOVE]',
        '筮・ｸ・': '[UPDATE]',
    }
    
    cleaned = message
    for char, replacement in replacements.items():
        cleaned = cleaned.replace(char, replacement)
    
    return cleaned

def safe_log(level: str, message: str, **kwargs):
    """Log with guaranteed English-only prefixes"""
    clean_message = clean_log_message(message)
    
    # Use standard logging
    import logging
    logger = logging.getLogger(__name__)
    
    if level.upper() == 'INFO':
        logger.info(clean_message, **kwargs)
    elif level.upper() == 'WARNING':
        logger.warning(clean_message, **kwargs)
    elif level.upper() == 'ERROR':
        logger.error(clean_message, **kwargs)
    elif level.upper() == 'DEBUG':
        logger.debug(clean_message, **kwargs)
    else:
        logger.info(clean_message, **kwargs)

# Convenience functions
def log_info(message: str, **kwargs):
    safe_log('INFO', message, **kwargs)

def log_warning(message: str, **kwargs):
    safe_log('WARNING', message, **kwargs)
    
def log_error(message: str, **kwargs):
    safe_log('ERROR', message, **kwargs)
