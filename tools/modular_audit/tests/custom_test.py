#!/usr/bin/env python3
"""
Custom test script for validating FMAS Mode 2 MISSING and EXTRA file detection
according to WSP 3.5 requirements
"""

import os
import sys
import logging
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path to import the modular_audit module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from modular_audit import discover_source_files, validate_baseline_path

# Configure logging to show all messages
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

def cleanup_temp_dirs(dirs):
    """Clean up temporary directories"""
    for d in dirs:
        if os.path.exists(d):
            shutil.rmtree(d)

def setup_test_scenario():
    """Set up test directories for MISSING and EXTRA file tests"""
    # Create temporary directories
    temp_dir = tempfile.mkdtemp()
    target_dir = os.path.join(temp_dir, "target")
    baseline_dir = os.path.join(temp_dir, "baseline")
    
    # Create module structure
    os.makedirs(os.path.join(target_dir, "modules", "testmod", "src"), exist_ok=True)
    os.makedirs(os.path.join(baseline_dir, "modules", "testmod", "src"), exist_ok=True)
    
    # Create files
    with open(os.path.join(baseline_dir, "modules", "testmod", "src", "original.py"), 'w') as f:
        f.write("# Original file")
    
    with open(os.path.join(baseline_dir, "modules", "testmod", "src", "missing.py"), 'w') as f:
        f.write("# File that will be missing in target")
    
    with open(os.path.join(target_dir, "modules", "testmod", "src", "original.py"), 'w') as f:
        f.write("# Original file")
    
    with open(os.path.join(target_dir, "modules", "testmod", "src", "extra.py"), 'w') as f:
        f.write("# Extra file in target")
    
    return temp_dir, target_dir, baseline_dir

def test_file_discovery():
    """Test that file discovery works properly"""
    temp_dir, target_dir, baseline_dir = setup_test_scenario()
    
    try:
        # Discover files
        target_modules, target_flat = discover_source_files(Path(target_dir))
        baseline_modules, baseline_flat = discover_source_files(Path(baseline_dir))
        
        # Print found files
        print("\nFiles found in target:")
        for module, files in target_modules.items():
            print(f"  Module: {module}")
            for f in files:
                print(f"    {f}")
        
        print("\nFiles found in baseline:")
        for module, files in baseline_modules.items():
            print(f"  Module: {module}")
            for f in files:
                print(f"    {f}")
        
        # Validate results
        assert 'testmod' in target_modules, "Target module not found"
        assert 'testmod' in baseline_modules, "Baseline module not found"
        
        target_module_files = target_modules['testmod']
        baseline_module_files = baseline_modules['testmod']
        
        # Calculate differences
        extra_files = target_module_files - baseline_module_files
        missing_files = baseline_module_files - target_module_files
        
        # Report EXTRA files (according to WSP 3.5)
        print("\nDetailed differences:")
        for extra_file in extra_files:
            print(f"[testmod] EXTRA: File not found anywhere in baseline. (File path: {extra_file})")
        
        # Report MISSING files (according to WSP 3.5)
        for missing_file in missing_files:
            print(f"[testmod] MISSING: File missing from target module. (Baseline path: {missing_file})")
        
        # Test results
        print("\nTest results:")
        print(f"  EXTRA files detected: {len(extra_files) > 0}")
        print(f"  MISSING files detected: {len(missing_files) > 0}")
        
        # Assert specific files were detected
        assert any(str(f).endswith('extra.py') for f in extra_files), "Extra file not detected"
        assert any(str(f).endswith('missing.py') for f in missing_files), "Missing file not detected"
        
        print("\nTest completed successfully!")
    finally:
        # Clean up
        cleanup_temp_dirs([temp_dir])

if __name__ == "__main__":
    test_file_discovery() 