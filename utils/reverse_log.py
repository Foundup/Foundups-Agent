#!/usr/bin/env python3
"""
Reverse Log Combiner
-------------------
Combines and reverses multiple log files into a single markdown document.
Follows Windsurf protocol for logging, error handling, and file operations.

Usage:
    python utils/reverse_log.py
"""

import os
import sys
import logging
from pathlib import Path
import argparse
from typing import List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_logging() -> None:
    """Configure logging with appropriate level and format."""
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    logging.getLogger().setLevel(getattr(logging, log_level.upper()))

def read_log_file(file_path: Path) -> List[str]:
    """
    Read a log file and return its lines.
    
    Args:
        file_path: Path to the log file
        
    Returns:
        List of lines from the file
        
    Raises:
        FileNotFoundError: If file doesn't exist
        IOError: If file can't be read
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.readlines()
    except FileNotFoundError:
        logger.error(f"Log file not found: {file_path}")
        raise
    except IOError as e:
        logger.error(f"Error reading log file {file_path}: {e}")
        raise

def write_reversed_log(output_path: Path, content: str) -> None:
    """
    Write the reversed log content to a file.
    
    Args:
        output_path: Path to write the reversed log file
        content: Content to write
        
    Raises:
        IOError: If file can't be written
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"Successfully wrote reversed log to {output_path}")
    except IOError as e:
        logger.error(f"Error writing reversed log file {output_path}: {e}")
        raise

def process_single_log(file_path: Path, output_path: Path) -> bool:
    """
    Process a single log file and write its reversed content.
    
    Args:
        file_path: Path to the log file
        output_path: Path to write the reversed log
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info(f"Processing {file_path}")
        lines = read_log_file(file_path)
        reversed_lines = list(reversed(lines))
        content = "".join(reversed_lines)
        write_reversed_log(output_path, content)
        return True
    except Exception as e:
        logger.error(f"Error processing log {file_path}: {e}")
        return False

def main() -> int:
    """Main entry point for the script."""
    try:
        # Setup paths
        backup_dir = Path('02_logs/backup')
        output_dir = Path('02_logs')
        
        # Process each log file
        for i in range(1, 4):
            input_file = backup_dir / f'02_{i:03d}log.txt'
            output_file = output_dir / f'r_{i:03d}log.txt'
            
            if not input_file.exists():
                logger.error(f"Input file not found: {input_file}")
                continue
                
            logger.info(f"Processing {input_file} -> {output_file}")
            if process_single_log(input_file, output_file):
                logger.info(f"Successfully reversed {input_file}")
            else:
                logger.error(f"Failed to reverse {input_file}")
                
        return 0
        
    except Exception as e:
        logger.error(f"Script failed: {e}")
        return 1

if __name__ == "__main__":
    setup_logging()
    sys.exit(main()) 