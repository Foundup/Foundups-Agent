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

def write_markdown_log(output_path: Path, content: str) -> None:
    """
    Write the combined log content to a markdown file.
    
    Args:
        output_path: Path to write the markdown file
        content: Content to write
        
    Raises:
        IOError: If file can't be written
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"Successfully wrote combined log to {output_path}")
    except IOError as e:
        logger.error(f"Error writing markdown file {output_path}: {e}")
        raise

def update_gitignore(gitignore_path: Path, target_path: Path) -> None:
    """
    Add the target file to .gitignore if not already present.
    
    Args:
        gitignore_path: Path to .gitignore file
        target_path: Path to add to .gitignore
    """
    try:
        # Create .gitignore if it doesn't exist
        if not gitignore_path.exists():
            gitignore_path.touch()
            logger.info(f"Created {gitignore_path}")
        
        # Read current content
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add target if not present
        target_str = str(target_path)
        if target_str not in content:
            with open(gitignore_path, 'a', encoding='utf-8') as f:
                f.write(f"\n{target_str}")
            logger.info(f"Added {target_str} to .gitignore")
    except IOError as e:
        logger.error(f"Error updating .gitignore: {e}")

def combine_reversed_logs(log_dir: Path) -> Optional[str]:
    """
    Combine and reverse multiple log files.
    
    Args:
        log_dir: Directory containing log files
        
    Returns:
        Combined and reversed log content as markdown string
    """
    try:
        # Get log files
        log_files = sorted(log_dir.glob('02_log_*.txt'))
        if not log_files:
            logger.error(f"No log files found in {log_dir}")
            return None
            
        # Read and combine logs
        all_lines = []
        for log_file in reversed(log_files):  # Process newer files first
            logger.info(f"Processing {log_file}")
            lines = read_log_file(log_file)
            all_lines.extend(lines)
            
        # Reverse all lines
        reversed_lines = list(reversed(all_lines))
        
        # Create markdown content
        content = "## Combined Reversed Log (Most Recent First)\n\n"
        content += "```log\n"
        content += "".join(reversed_lines)
        content += "\n```"
        
        return content
        
    except Exception as e:
        logger.error(f"Error combining logs: {e}")
        return None

def main() -> int:
    """Main entry point for the script."""
    try:
        # Parse arguments
        parser = argparse.ArgumentParser(description='Combine and reverse log files')
        parser.add_argument('--log-dir', default='02_log',
                          help='Directory containing log files')
        args = parser.parse_args()
        
        # Setup paths
        log_dir = Path(args.log_dir)
        output_path = log_dir / 'DevLog.md'
        gitignore_path = Path('.gitignore')
        
        # Create log directory if it doesn't exist
        if not log_dir.exists():
            log_dir.mkdir(parents=True)
            logger.info(f"Created log directory: {log_dir}")
            
        # Create test log files if they don't exist
        test_files = ['02_log_001.txt', '02_log_002.txt']
        for file_name in test_files:
            file_path = log_dir / file_name
            if not file_path.exists():
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"Test log entry for {file_name}\n")
                logger.info(f"Created test log file: {file_path}")
            
        # Combine and reverse logs
        content = combine_reversed_logs(log_dir)
        if not content:
            return 1
            
        # Write markdown file
        write_markdown_log(output_path, content)
        
        # Update .gitignore
        update_gitignore(gitignore_path, output_path)
        
        return 0
        
    except Exception as e:
        logger.error(f"Script failed: {e}")
        return 1

if __name__ == "__main__":
    setup_logging()
    sys.exit(main()) 