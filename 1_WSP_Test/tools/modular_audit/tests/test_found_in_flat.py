#!/usr/bin/env python3
"""
Test script to verify WSP 3.5 FOUND_IN_FLAT log messages for FMAS Mode 2.
"""

import os
import sys
import logging
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path to import the modular_audit module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from modular_audit import audit_with_baseline_comparison

def setup_test_environment():
    """Set up a test environment with baseline and target directories."""
    base_dir = tempfile.mkdtemp()
    baseline_dir = Path(base_dir) / "baseline"
    target_dir = Path(base_dir) / "target"
    
    # Create baseline structure with flat file
    baseline_modules_dir = baseline_dir / "modules"
    os.makedirs(baseline_modules_dir, exist_ok=True)
    
    # Create a flat file in the baseline modules directory
    with open(baseline_modules_dir / "flat_file.py", 'w') as f:
        f.write("# This is a flat file in the baseline modules directory\n")
    
    # Create target structure with the file in a module
    target_modules_dir = target_dir / "modules"
    target_module_dir = target_modules_dir / "newmod"
    target_src_dir = target_module_dir / "src"
    os.makedirs(target_src_dir, exist_ok=True)
    
    # Move the flat file into a module in the target
    with open(target_src_dir / "flat_file.py", 'w') as f:
        f.write("# This file was moved from the flat structure to a module\n")
    
    # Also add a truly new file to the target for comparison
    with open(target_src_dir / "extra_file.py", 'w') as f:
        f.write("# This is a completely new file\n")
    
    return base_dir, baseline_dir, target_dir

def main():
    """Run a test to validate FOUND_IN_FLAT file logging."""
    # Configure logging to show DEBUG and above messages
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
    
    base_dir, baseline_path, target_path = setup_test_environment()
    
    try:
        print("\n--- Running FMAS Mode 2 testing for FOUND_IN_FLAT files ---")
        print(f"Baseline path: {baseline_path}")
        print(f"Target path: {target_path}")
        
        # Run the comparison
        result = audit_with_baseline_comparison(target_path, baseline_path)
        
        # Print detailed results
        if result["status"] == "success":
            print("\nComparison completed successfully")
            print(f"New modules: {result['modules']['new']}")
            print(f"Modified modules: {result['modules']['modified']}")
            print(f"Deleted modules: {result['modules']['deleted']}")
            print(f"New files: {result['files']['new']}")
            print(f"Modified files: {result['files']['modified']}")
            print(f"Deleted files: {result['files']['deleted']}")
            print(f"Found in flat structure: {result['files']['found_in_flat']}")
            
            print("\nExpected WSP 3.5 compliant log message for FOUND_IN_FLAT files:")
            print("[newmod] FOUND_IN_FLAT: Found only in baseline flat modules/, needs proper placement. (File path: src/flat_file.py)")
            
            # Conclusion
            if result['files']['found_in_flat'] > 0:
                print("\nCONCLUSION: The modular_audit.py implementation successfully detects FOUND_IN_FLAT files.")
                print("Files moved from the flat baseline structure to organized modules in the target are correctly identified.")
            else:
                print("\nCONCLUSION: The modular_audit.py implementation does NOT detect FOUND_IN_FLAT files.")
        else:
            print(f"Comparison failed: {result['reason']}")
    finally:
        # Clean up
        shutil.rmtree(base_dir)

if __name__ == "__main__":
    main() 