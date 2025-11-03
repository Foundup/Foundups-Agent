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

Test script to verify FMAS Mode 2 MISSING and EXTRA file detection
according to WSP 3.5 requirements.
"""

import os
import sys
import logging
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path to import the modular_audit module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import modular_audit

def main():
    """Set up a test environment and verify MISSING and EXTRA file detection."""
    # Setup test environment
    base_dir = tempfile.mkdtemp()
    baseline_dir = Path(base_dir) / "baseline"
    target_dir = Path(base_dir) / "target"
    
    # Create baseline structure
    baseline_modules_dir = baseline_dir / "modules"
    os.makedirs(baseline_modules_dir, exist_ok=True)
    
    # Create a module in the baseline
    baseline_module_dir = baseline_modules_dir / "testmod"
    baseline_src_dir = baseline_module_dir / "src"
    os.makedirs(baseline_src_dir, exist_ok=True)
    
    # Create a file that will be missing in the target
    with open(baseline_src_dir / "missing_file.py", 'w') as f:
        f.write("# This file will be missing in the target\n")
    
    # Create a common file
    with open(baseline_src_dir / "common_file.py", 'w') as f:
        f.write("# This file will exist in both\n")
    
    # Create target structure
    target_modules_dir = target_dir / "modules"
    target_module_dir = target_modules_dir / "testmod"
    target_src_dir = target_module_dir / "src"
    os.makedirs(target_src_dir, exist_ok=True)
    
    # Create the common file
    with open(target_src_dir / "common_file.py", 'w') as f:
        f.write("# This file will exist in both\n")
    
    # Create a file that will be extra in the target
    with open(target_src_dir / "extra_file.py", 'w') as f:
        f.write("# This file is only in the target\n")
    
    try:
        # Configure logging to show INFO and above messages
        logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
        
        print("\n--- Running FMAS Mode 2 testing for MISSING and EXTRA files ---")
        print(f"Baseline path: {baseline_dir}")
        print(f"Target path: {target_dir}")
        
        # Run the comparison
        result = modular_audit.audit_with_baseline_comparison(target_dir, baseline_dir)
        
        # Print detailed results
        if result["status"] == "success":
            print("\nComparison completed successfully")
            print(f"Missing files: {result['files']['deleted']}")
            print(f"Extra files: {result['files']['new']}")
            
            print("\nExpected WSP 3.5 compliant log messages:")
            print("[testmod] MISSING: File missing from target module. (Baseline path: src/missing_file.py)")
            print("[testmod] EXTRA: File not found anywhere in baseline. (File path: src/extra_file.py)")
            
            print(f"\nMISSING files detected: {result['files']['deleted'] > 0}")
            print(f"EXTRA files detected: {result['files']['new'] > 0}")
        else:
            print(f"Comparison failed: {result['reason']}")
    finally:
        # Clean up
        shutil.rmtree(base_dir)

if __name__ == "__main__":
    main() 