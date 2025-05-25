"""
02_Logs Reversal Utility

A utility script to reverse the order of lines in a log file,
placing the most recent entries at the top, with automatic backup creation.
"""

import os
import sys
import logging
import shutil
from datetime import datetime
from typing import List, Optional

# Initialize logger for this module
logger = logging.getLogger(__name__)

def setup_logging() -> None:
    """Configure basic logging for the script."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def create_backup(file_path: str) -> Optional[str]:
    """
    Create a timestamped backup of the log file.
    
    Args:
        file_path (str): Path to the original log file
        
    Returns:
        Optional[str]: Path to the backup file if successful, None otherwise
    """
    try:
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(os.path.dirname(file_path), "backups")
        backup_name = f"backup_{timestamp}_{os.path.basename(file_path)}"
        backup_path = os.path.join(backup_dir, backup_name)
        
        # Ensure backup directory exists
        os.makedirs(backup_dir, exist_ok=True)
        
        # Copy the file
        shutil.copy2(file_path, backup_path)
        logger.info(f"Created backup: {backup_path}")
        return backup_path
        
    except Exception as e:
        logger.error(f"Failed to create backup: {e}")
        return None

def reverse_log_file(file_path: str) -> bool:
    """
    Reverse the order of lines in a log file and create a backup.
    
    Args:
        file_path (str): Path to the log file to reverse
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            logger.error(f"Log file not found: {file_path}")
            return False
            
        # Create backup first
        backup_path = create_backup(file_path)
        if not backup_path:
            logger.error("Failed to create backup, aborting reverse operation")
            return False
            
        # Read all lines from the file
        with open(file_path, 'r', encoding='utf-8') as f:
            lines: List[str] = f.readlines()
            
        # Reverse the lines
        reversed_lines = list(reversed(lines))
        
        # Write back to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(reversed_lines)
            
        logger.info(f"Successfully reversed log file: {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error reversing log file {file_path}: {e}")
        return False

def main() -> None:
    """Main entry point for the script."""
    setup_logging()
    
    # Check command line arguments
    if len(sys.argv) != 2:
        print("Usage: python reverse_log.py <path_to_log_file>")
        sys.exit(1)
        
    log_file = sys.argv[1]
    
    # Ensure the log file is within the O2_log directory
    if not log_file.startswith('O2_log/'):
        logger.error("Log file must be within the O2_log directory")
        sys.exit(1)
        
    if reverse_log_file(log_file):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main() 