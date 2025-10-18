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

Test script to verify FMAS Mode 2 MODIFIED file detection according to WSP 3.5.
"""

import os
import sys
import logging
import tempfile
import shutil
import hashlib
from pathlib import Path

# Add parent directory to path to import the modular_audit module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from modular_audit import audit_with_baseline_comparison, compute_file_hash

def calculate_hash(file_path):
    """Calculate MD5 hash of a file."""
    with open(file_path, 'rb') as f:
        file_hash = hashlib.md5()
        chunk = f.read(8192)
        while chunk:
            file_hash.update(chunk)
            chunk = f.read(8192)
    return file_hash.hexdigest()

def setup_test_environment():
    """Create a test environment with baseline and target directories."""
    base_dir = tempfile.mkdtemp()
    baseline_dir = Path(base_dir) / "baseline"
    target_dir = Path(base_dir) / "target"
    
    # Create directory structure
    baseline_modules_dir = baseline_dir / "modules"
    baseline_module_dir = baseline_modules_dir / "testmod"
    baseline_src_dir = baseline_module_dir / "src"
    os.makedirs(baseline_src_dir, exist_ok=True)
    
    target_modules_dir = target_dir / "modules"
    target_module_dir = target_modules_dir / "testmod"
    target_src_dir = target_module_dir / "src"
    os.makedirs(target_src_dir, exist_ok=True)
    
    # Create modified file
    with open(baseline_src_dir / "modified.py", 'w') as f:
        f.write("# This is the baseline version\n")
    
    with open(target_src_dir / "modified.py", 'w') as f:
        f.write("# This is the modified version\n")
    
    # Create identical file
    with open(baseline_src_dir / "identical.py", 'w') as f:
        f.write("# This file is identical in both\n")
    
    with open(target_src_dir / "identical.py", 'w') as f:
        f.write("# This file is identical in both\n")
        
    return base_dir, baseline_dir, target_dir

def main():
    """Run test to validate MODIFIED file detection."""
    # Set up logging
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
    
    # Create test environment
    base_dir, baseline_dir, target_dir = setup_test_environment()
    
    try:
        # Verify file hashes
        baseline_modified = baseline_dir / "modules" / "testmod" / "src" / "modified.py"
        target_modified = target_dir / "modules" / "testmod" / "src" / "modified.py"
        baseline_identical = baseline_dir / "modules" / "testmod" / "src" / "identical.py"
        target_identical = target_dir / "modules" / "testmod" / "src" / "identical.py"
        
        baseline_modified_hash = calculate_hash(baseline_modified)
        target_modified_hash = calculate_hash(target_modified)
        baseline_identical_hash = calculate_hash(baseline_identical)
        target_identical_hash = calculate_hash(target_identical)
        
        print("\n--- File Hash Verification ---")
        print(f"Baseline modified.py hash: {baseline_modified_hash}")
        print(f"Target modified.py hash: {target_modified_hash}")
        print(f"Hashes different: {baseline_modified_hash != target_modified_hash}")
        
        print(f"Baseline identical.py hash: {baseline_identical_hash}")
        print(f"Target identical.py hash: {target_identical_hash}")
        print(f"Hashes same: {baseline_identical_hash == target_identical_hash}")
        
        # Verify our compute_file_hash function works as expected
        print("\n--- Testing compute_file_hash function ---")
        computed_baseline_hash = compute_file_hash(baseline_modified)
        computed_target_hash = compute_file_hash(target_modified)
        print(f"Computed baseline hash: {computed_baseline_hash}")
        print(f"Computed target hash: {computed_target_hash}")
        print(f"Hashes different: {computed_baseline_hash != computed_target_hash}")
        
        # Run the comparison
        print("\n--- Running FMAS Mode 2 testing for MODIFIED files ---")
        print(f"Baseline path: {baseline_dir}")
        print(f"Target path: {target_dir}")
        
        result = audit_with_baseline_comparison(target_dir, baseline_dir)
        
        # Print detailed results
        if result["status"] == "success":
            print("\nComparison completed successfully")
            print(f"Modified files: {result['files']['modified']}")
            
            print("\nExpected WSP 3.5 compliant log message for MODIFIED files:")
            print("[testmod] MODIFIED: Content differs from baseline. (File path: src/modified.py)")
            
            # Conclusion
            if result['files']['modified'] > 0:
                print("\nCONCLUSION: The modular_audit.py implementation successfully detects MODIFIED files.")
                print("Files with different content between baseline and target are correctly identified.")
            else:
                print("\nCONCLUSION: The modular_audit.py implementation does NOT detect MODIFIED files.")
        else:
            print(f"Comparison failed: {result['reason']}")
    finally:
        # Clean up
        shutil.rmtree(base_dir)

if __name__ == "__main__":
    main() 