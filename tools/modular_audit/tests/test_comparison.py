#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io

"""
# === UTF-8 ENFORCEMENT (WSP 90) ===
# Prevent UnicodeEncodeError on Windows systems
# Only apply when running as main script, not during import
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===

Temporary script to test the FMAS Mode 2 baseline comparison functionality
"""

import sys
import logging
from pathlib import Path
from tools.modular_audit.modular_audit import audit_with_baseline_comparison, discover_source_files

# Configure logging to show all messages
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

def main():
    """Test the baseline comparison with our temp directories"""
    target_path = Path("./temp_target")
    baseline_path = Path("./temp_baseline")
    
    # Show all discovered files
    target_files = discover_source_files(target_path)
    baseline_files = discover_source_files(baseline_path)
    
    print("Target files:")
    for module, files in target_files.items():
        print(f"  {module}:")
        for file in files:
            print(f"    {file}")
            
    print("\nBaseline files:")
    for module, files in baseline_files.items():
        print(f"  {module}:")
        for file in files:
            print(f"    {file}")
    
    # Run the comparison
    result = audit_with_baseline_comparison(target_path, baseline_path)
    
    # Print detailed results
    if result["status"] == "success":
        print(f"\nComparison completed successfully")
        print(f"New modules: {result['modules']['new']}")
        print(f"Modified modules: {result['modules']['modified']}")
        print(f"Deleted modules: {result['modules']['deleted']}")
        print(f"New files: {result['files']['new']}")
        print(f"Deleted files: {result['files']['deleted']}")
        
        # Look at the modified module in detail
        if 'testmod' in target_files and 'testmod' in baseline_files:
            new_files = target_files['testmod'] - baseline_files['testmod'] 
            deleted_files = baseline_files['testmod'] - target_files['testmod']
            
            print("\nDetailed file changes for testmod:")
            print(f"  New files: {new_files}")
            print(f"  Deleted files: {deleted_files}")
    else:
        print(f"Comparison failed: {result['reason']}")

if __name__ == "__main__":
    main() 