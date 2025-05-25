#!/usr/bin/env python3
"""
Test script to verify WSP 3.5 compliant log message formatting for FMAS Mode 2.
"""

import os
import sys
import logging
import tempfile
import shutil
from pathlib import Path
from io import StringIO

# Add parent directory to path to import the modular_audit module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import modular_audit

def setup_test_environment():
    """Create a test environment with various file scenarios."""
    base_dir = tempfile.mkdtemp()
    baseline_dir = Path(base_dir) / "baseline"
    target_dir = Path(base_dir) / "target"
    
    # Create directory structure
    baseline_modules_dir = baseline_dir / "modules"
    target_modules_dir = target_dir / "modules"
    
    # Create module directories
    os.makedirs(baseline_modules_dir, exist_ok=True)
    os.makedirs(target_modules_dir, exist_ok=True)
    
    # 1. Create a module with modified files
    modified_module_baseline = baseline_modules_dir / "modified_module"
    modified_module_baseline_src = modified_module_baseline / "src"
    os.makedirs(modified_module_baseline_src, exist_ok=True)
    
    with open(modified_module_baseline_src / "common.py", 'w') as f:
        f.write("# Baseline version\n")
    
    modified_module_target = target_modules_dir / "modified_module"
    modified_module_target_src = modified_module_target / "src"
    os.makedirs(modified_module_target_src, exist_ok=True)
    
    with open(modified_module_target_src / "common.py", 'w') as f:
        f.write("# Target version - modified\n")
    
    # 2. Create a module with missing and extra files
    missing_extra_module_baseline = baseline_modules_dir / "missing_extra_module"
    missing_extra_module_baseline_src = missing_extra_module_baseline / "src"
    os.makedirs(missing_extra_module_baseline_src, exist_ok=True)
    
    with open(missing_extra_module_baseline_src / "common.py", 'w') as f:
        f.write("# Common file\n")
    
    with open(missing_extra_module_baseline_src / "missing.py", 'w') as f:
        f.write("# Will be missing in target\n")
    
    missing_extra_module_target = target_modules_dir / "missing_extra_module"
    missing_extra_module_target_src = missing_extra_module_target / "src"
    os.makedirs(missing_extra_module_target_src, exist_ok=True)
    
    with open(missing_extra_module_target_src / "common.py", 'w') as f:
        f.write("# Common file\n")
    
    with open(missing_extra_module_target_src / "extra.py", 'w') as f:
        f.write("# Extra file in target\n")
    
    # 3. Create a flat file in baseline
    with open(baseline_modules_dir / "flat_file.py", 'w') as f:
        f.write("# Flat file in baseline\n")
    
    # Create a module in target that uses the flat file
    flat_module_target = target_modules_dir / "flat_module"
    flat_module_target_src = flat_module_target / "src"
    os.makedirs(flat_module_target_src, exist_ok=True)
    
    with open(flat_module_target_src / "flat_file.py", 'w') as f:
        f.write("# Flat file moved to module\n")
    
    return base_dir, baseline_dir, target_dir

def capture_log_output(level=logging.WARNING):
    """Capture log messages to a string buffer."""
    log_capture = StringIO()
    handler = logging.StreamHandler(log_capture)
    handler.setLevel(level)
    formatter = logging.Formatter('%(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    
    # Remove any existing handlers and add our capture handler
    root_logger = logging.getLogger()
    for hdlr in root_logger.handlers[:]:
        root_logger.removeHandler(hdlr)
    root_logger.addHandler(handler)
    root_logger.setLevel(level)
    
    return log_capture

def main():
    """Run test to validate WSP 3.5 log message formatting."""
    # Setup test environment
    base_dir, baseline_dir, target_dir = setup_test_environment()
    
    try:
        # Capture logging output
        log_capture = capture_log_output()
        
        print("\n--- Running FMAS Mode 2 testing for log message formatting ---")
        print(f"Baseline path: {baseline_dir}")
        print(f"Target path: {target_dir}")
        
        # Run the comparison
        result = modular_audit.audit_with_baseline_comparison(target_dir, baseline_dir)
        
        # Print results from the comparison
        if result["status"] == "success":
            print("\nComparison completed successfully")
            print(f"Modified modules: {result['modules']['modified']}")
            print(f"New modules: {result['modules']['new']}")
            print(f"Deleted modules: {result['modules']['deleted']}")
            
            print(f"Modified files: {result['files']['modified']}")
            print(f"New files: {result['files']['new']}")
            print(f"Deleted files: {result['files']['deleted']}")
            print(f"Found in flat: {result['files']['found_in_flat']}")
            
            # Print captured logs and verify format
            log_output = log_capture.getvalue()
            print("\n--- Captured Log Messages ---")
            print(log_output)
            
            # Check for expected log message formats
            expected_formats = [
                "[modified_module] MODIFIED: Content differs from baseline",
                "[missing_extra_module] MISSING: File missing from target module",
                "[missing_extra_module] EXTRA: File not found anywhere in baseline",
                "[flat_module] FOUND_IN_FLAT: Found only in baseline flat modules/"
            ]
            
            print("\n--- WSP 3.5 Format Validation ---")
            for expected in expected_formats:
                if expected in log_output:
                    print(f"✅ Found expected format: {expected}")
                else:
                    print(f"❌ Missing expected format: {expected}")
            
            print("\nOVERALL CONCLUSION:")
            if all(expected in log_output for expected in expected_formats):
                print("✅ All WSP 3.5 log formats were correctly implemented.")
            else:
                print("❌ Some expected WSP 3.5 log formats were not found.")
        else:
            print(f"Comparison failed: {result['reason']}")
    finally:
        # Clean up
        shutil.rmtree(base_dir)

if __name__ == "__main__":
    main() 