"""
Log Reversal Utility

A utility script to reverse the order of lines in a log file,
placing the most recent entries at the top, with versioned output.
"""

import os
import sys
import logging
import shutil
from datetime import datetime
from typing import List, Optional, Tuple

# Initialize logger for this module
logger = logging.getLogger(__name__)

def setup_logging() -> None:
    """Configure basic logging for the script."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def ensure_directory(path: str) -> None:
    """
    Ensure directory exists, create if it doesn't.
    
    Args:
        path (str): Directory path to ensure exists
    """
    try:
        os.makedirs(path, exist_ok=True)
        logger.info(f"Ensured directory exists: {path}")
    except Exception as e:
        logger.error(f"Failed to create directory {path}: {e}")
        raise

def get_next_version() -> str:
    """
    Get the next available version number for the log file.
    
    Returns:
        str: Next version number (e.g., '001')
    """
    # Look for existing versioned files in 02_logs directory
    logs_dir = "02_logs"
    ensure_directory(logs_dir)
    
    try:
        existing_files = [f for f in os.listdir(logs_dir) if f.startswith('02_log_')]
        if not existing_files:
            logger.info("No existing versioned files found, starting with version 001")
            return '001'
            
        # Extract version numbers and find the highest
        versions = [int(f.split('_')[2].split('.')[0]) for f in existing_files]
        next_version = max(versions) + 1
        logger.info(f"Found existing versions: {versions}, using next version: {next_version:03d}")
        return f'{next_version:03d}'
    except Exception as e:
        logger.error(f"Error getting next version: {e}")
        return '001'

def parse_conversation_entries(lines: List[str]) -> List[List[str]]:
    """
    Parse conversation history into logical entries.
    
    Args:
        lines (List[str]): Raw lines from log file
        
    Returns:
        List[List[str]]: List of conversation entries
    """
    entries = []
    current_entry = []
    in_conversation = False
    
    for line in lines:
        stripped = line.strip()
        
        # Skip empty lines at the start of entries
        if not stripped and not current_entry:
            continue
            
        # Start new entry on speaker change
        if stripped.startswith(('You said:', 'ChatGPT said:')):
            if current_entry:
                entries.append(current_entry)
            current_entry = [line]
            in_conversation = True
        elif in_conversation and current_entry:
            current_entry.append(line)
            
    # Add last entry if exists
    if current_entry:
        entries.append(current_entry)
        
    return entries

def reverse_log_file(file_path: str) -> bool:
    """
    Reverse the order of lines in a log file and create a versioned output.
    
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
            
        logger.info(f"Reading log file: {file_path}")
        # Read all lines from the file
        with open(file_path, 'r', encoding='utf-8') as f:
            lines: List[str] = f.readlines()
            
        # Parse into conversation entries
        entries = parse_conversation_entries(lines)
        logger.info(f"Found {len(entries)} conversation entries to reverse")
        
        # Reverse entries while keeping each entry's internal order
        entries.reverse()
        
        # Get next version number and create output path in 02_logs directory
        version = get_next_version()
        output_file = os.path.join("02_logs", f'02_log_{version}.txt')
        
        # Write to versioned output file
        logger.info(f"Writing reversed content to: {output_file}")
        with open(output_file, 'w', encoding='utf-8') as f:
            # Write header
            f.write("# === O2 SESSION LOG ===\n")
            f.write("# This log tracks the full development history of the FoundUps Agent project.\n")
            f.write("# Lines are ordered with the most recent events at the top.\n")
            f.write("# Use this file to prime O2 with complete build context.\n")
            f.write("# Format: Human-Agent interactions, task decisions, architectural changes.\n")
            f.write("# Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M") + "\n\n")
            f.write("--------------------------------------------\n\n")
            
            # Write reversed entries with spacing
            for entry in entries:
                f.writelines(entry)
                f.write('\n')  # Add spacing between entries
            
        logger.info(f"Successfully created reversed log file: {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"Error processing log file {file_path}: {e}")
        return False

def main() -> None:
    """Main entry point for the script."""
    setup_logging()
    
    # Check command line arguments
    if len(sys.argv) != 2:
        print("Usage: python reverse_log.py <path_to_log_file>")
        sys.exit(1)
        
    log_file = sys.argv[1]
    
    # Ensure the log file is within the 02_logs/backup directory
    if not log_file.startswith('02_logs/backup/'):
        logger.error("Log file must be within the 02_logs/backup directory")
        sys.exit(1)
        
    if reverse_log_file(log_file):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main() 