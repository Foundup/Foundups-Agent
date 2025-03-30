#!/usr/bin/env python3
"""
Backup script for Foundups-Agent repository.
Creates a clean backup and performs Git operations.
"""

import os
import sys
import logging
import argparse
from pathlib import Path
import shutil
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s'
)
logger = logging.getLogger(__name__)

def clean_backup(dest_path):
    """Remove existing backup if it exists."""
    try:
        if os.path.exists(dest_path):
            logger.info(f"Removing existing backup at {dest_path}")
            shutil.rmtree(dest_path)
    except Exception as e:
        logger.error(f"Failed to remove existing backup: {e}")
        raise

def create_backup(src_path, dest_path):
    """Create a clean backup of the repository."""
    try:
        logger.info(f"Creating backup from {src_path} to {dest_path}")
        
        # Use PowerShell's Copy-Item for better path handling
        cmd = f'Copy-Item -Path "{src_path}" -Destination "{dest_path}" -Recurse -Force'
        result = subprocess.run(['powershell', '-Command', cmd], capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"Backup failed: {result.stderr}")
            return False
            
        logger.info("Backup created successfully")
        return True
        
    except Exception as e:
        logger.error(f"Backup failed: {e}")
        return False

def git_operations(dest_path):
    """Perform Git operations in the backup directory."""
    try:
        # Change to backup directory
        os.chdir(dest_path)
        
        # Initialize git if not already initialized
        if not os.path.exists('.git'):
            subprocess.run(['git', 'init'], check=True)
            logger.info("Git repository initialized")
        
        # Add all files
        subprocess.run(['git', 'add', '.'], check=True)
        logger.info("Files added to git")
        
        # Commit changes
        subprocess.run(['git', 'commit', '-m', 'Initial backup commit'], check=True)
        logger.info("Changes committed")
        
        return True
        
    except Exception as e:
        logger.error(f"Git operations failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Backup Foundups-Agent repository')
    parser.add_argument('--src', default='.', help='Source directory (default: current directory)')
    parser.add_argument('--dest', default='o:/foundups-agent-backup', help='Destination directory')
    args = parser.parse_args()
    
    try:
        # Clean existing backup
        clean_backup(args.dest)
        
        # Create new backup
        if not create_backup(args.src, args.dest):
            logger.error("Backup creation failed")
            sys.exit(1)
            
        # Perform Git operations
        if not git_operations(args.dest):
            logger.error("Git operations failed")
            sys.exit(1)
            
        logger.info("Backup process completed successfully")
        
    except Exception as e:
        logger.error(f"Backup process failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 