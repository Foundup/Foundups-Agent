# File: modular_audit.py
# Purpose: FMAS Phase 1 - Test Existence & Structure Validator (Windsurf Protocol)
# Version: 0.4.0 (Enhanced implementation for WSP 11 & 12)

import os
import argparse
import logging
from pathlib import Path # Use pathlib for better path handling
import sys # Add sys import

# --- Configuration ---
# Default file types in src/ to check for corresponding tests
DEFAULT_SRC_EXTENSIONS = {'.py'}
# Default prefix for test files
DEFAULT_TEST_PREFIX = 'test_'
# Interface file name
INTERFACE_FILE = 'INTERFACE.md'
# Dependency manifest file name
DEPENDENCY_MANIFEST_FILE = 'requirements.txt'
# --- End Configuration ---

# --- Logging Setup ---
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
log = logging.getLogger(__name__)
# --- End Logging Setup ---

def check_structure_and_test_existence(module_path: Path) -> list[str]:
    """
    Audits a single module directory for structure and test file existence.

    Args:
        module_path: Path object for the module directory (e.g., ./modules/module_name).

    Returns:
        A list of error/warning strings found for this module.
    """
    module_name = module_path.name
    errors = []
    
    log.debug(f"Checking module structure: {module_name} at path {module_path}")

    src_path = module_path / 'src'
    tests_path = module_path / 'tests'

    # 1. Check for src/ directory
    if not src_path.is_dir():
        log.debug(f"Module {module_name}: src/ directory not found")
        errors.append(f"[{module_name}] STRUCTURE_ERROR: 'src/' directory not found or is not a directory.")
        # Cannot proceed without src/, so return early for this module
        return errors
    
    log.debug(f"Module {module_name}: src/ directory exists")

    # 2. Check for tests/ directory
    if not tests_path.is_dir():
        # Log as warning, but continue checking src files (they *should* have tests)
        log.warning(f"[{module_name}] STRUCTURE_WARN: 'tests/' directory not found or is not a directory. Cannot verify test files.")
        # We can still check if src files exist, but cannot check *for* tests.
        # Depending on strictness, you might add an error here instead/as well.
        # errors.append(f"[{module_name}] STRUCTURE_ERROR: 'tests/' directory not found.")
    else:
        log.debug(f"Module {module_name}: tests/ directory exists")
        # 3. Check for corresponding test files if tests/ exists
        for src_file in src_path.rglob('*'): # rglob finds files recursively
            if src_file.is_file() and src_file.suffix in DEFAULT_SRC_EXTENSIONS and not src_file.name.startswith('__init__'):
                relative_src_path = src_file.relative_to(src_path)
                expected_test_filename = f"{DEFAULT_TEST_PREFIX}{src_file.name}"
                # Construct expected path: tests/relative/path/test_filename.py
                expected_test_path = tests_path / relative_src_path.parent / expected_test_filename
                
                log.debug(f"Module {module_name}: Checking for test file: {expected_test_path}")

                if not expected_test_path.is_file():
                    log.debug(f"Module {module_name}: Test file not found: {expected_test_path}")
                    src_file_rel_str = str(relative_src_path).replace('\\', '/') # Use double backslash for escape in f-string
                    errors.append(f"[{module_name}] NO_TEST: Missing test file for src/{src_file_rel_str}. Expected: {expected_test_path.relative_to(module_path).as_posix()}")

    # 4. Check for interface definition file (WSP 11)
    interface_file_path = module_path / INTERFACE_FILE
    log.debug(f"Module {module_name}: Checking for interface file: {interface_file_path}")
    if not interface_file_path.is_file():
        log.debug(f"Module {module_name}: Interface file not found: {interface_file_path}")
        errors.append(f"[{module_name}] INTERFACE_MISSING: Required interface definition file '{INTERFACE_FILE}' not found.")
    else:
        log.debug(f"Module {module_name}: Interface file exists")

    # 5. Check for dependency manifest file (WSP 12)
    dependency_manifest_path = module_path / DEPENDENCY_MANIFEST_FILE
    log.debug(f"Module {module_name}: Checking for dependency manifest: {dependency_manifest_path}")
    if not dependency_manifest_path.is_file():
        log.debug(f"Module {module_name}: Dependency manifest not found: {dependency_manifest_path}")
        errors.append(f"[{module_name}] DEPENDENCY_MANIFEST_MISSING: Required dependency manifest file '{DEPENDENCY_MANIFEST_FILE}' not found.")
    elif dependency_manifest_path.stat().st_size == 0:
        log.debug(f"Module {module_name}: Dependency manifest exists but is empty")
        errors.append(f"[{module_name}] DEPENDENCY_MANIFEST_MISSING: Dependency manifest file '{DEPENDENCY_MANIFEST_FILE}' exists but is empty.")
    else:
        log.debug(f"Module {module_name}: Dependency manifest exists")

    log.debug(f"Module {module_name}: Found {len(errors)} errors")
    return errors

def audit_all_modules(modules_root_dir: Path) -> tuple[list[str], int]:
    """
    Audits all subdirectories in the modules_root_dir.

    Args:
        modules_root_dir: Path object for the main /modules directory.

    Returns:
        A tuple containing:
            - A list of all error/warning strings found across all modules.
            - The total number of modules scanned.
    """
    all_results = []
    module_count = 0

    if not modules_root_dir.is_dir():
        log.critical(f"Modules root directory not found or is invalid: {modules_root_dir}")
        return ["CRITICAL: Modules root directory not found."], 0
    
    log.debug(f"Starting audit of modules in: {modules_root_dir}")
    
    # List all items to be scanned
    items = list(modules_root_dir.iterdir())
    log.debug(f"Found {len(items)} items in modules directory")

    for item in items:
        # Only check immediate subdirectories
        if item.is_dir():
            # Skip common non-module dirs or baseline dirs if needed
            if item.name.startswith('.') or item.name == '__pycache__' or 'clean' in item.name.lower():
                 log.debug(f"Skipping directory: {item.name}")
                 continue

            log.info(f"--- Auditing Module: {item.name} ---")
            module_count += 1
            log.debug(f"Checking module {item.name}...")
            module_results = check_structure_and_test_existence(item)
            log.debug(f"Finished checking module {item.name}. Found {len(module_results)} issues.")
            all_results.extend(module_results)

    log.debug(f"Finished audit. Scanned {module_count} modules, found {len(all_results)} total issues.")
    return all_results, module_count


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="FoundUps Modular Audit Tool (Phase 1) - Structure & Test Existence Check",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter # Show defaults in help
    )
    parser.add_argument(
        "modules_root",
        type=Path, # Use Path directly for type checking
        help="Path to the root /modules directory (e.g., ./modules)"
    )
    # Example of adding configurability later:
    # parser.add_argument("--test-prefix", default=DEFAULT_TEST_PREFIX, help="Prefix for test files")
    # parser.add_argument("--src-ext", nargs='+', default=list(DEFAULT_SRC_EXTENSIONS), help="Source file extensions to check")
    parser.add_argument("--lang", help="Specify language context to apply appropriate structural rules")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")

    args = parser.parse_args()
    
    if args.verbose:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)
    
    log.info(f"Starting FMAS Phase 1 Audit on: {args.modules_root.resolve()}")

    audit_findings, scanned_count = audit_all_modules(args.modules_root)

    log.debug("Generating audit summary...")
    print("\n--- Audit Summary ---")
    log.info(f"Scanned {scanned_count} potential modules.")

    if not audit_findings:
        log.info("✅ PASSED: All audited modules meet Phase 1 structure and test existence requirements.")
        exit(0)
    else:
        print("ERROR: ❌ FAILED: Issues found during audit:", file=sys.stderr) # Use print to stderr
        for finding in audit_findings:
            print(f"- {finding}", file=sys.stderr) # Use print to stderr

        # Exit with a non-zero code to indicate failure for scripting
        exit(1) 