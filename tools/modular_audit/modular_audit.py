#!/usr/bin/env python3
"""
Foundups Modular Audit System (FMAS)

This tool performs an audit of the module structure and test existence.
This helps ensure that all modules follow the established standards.

Mode 1: Structure check only
- Validates that each module has a src/ directory
- Validates that each module has a tests/ directory
- Checks for the presence of the module interface file
- Checks for the presence of the module.json dependency manifest
- Reports any missing components as findings

Mode 2: Baseline comparison
- Performs all Mode 1 checks
- Additionally compares the module structure against a baseline
- Reports added, modified, and removed modules and files
"""

import argparse
import json
import logging
import os
import sys
import hashlib
from pathlib import Path

VERSION = "0.7.0"

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

# Define critical modules that should prompt warnings if modified
CRITICAL_MODULES = {"core", "security", "auth", "config"}

def validate_baseline_path(baseline_path):
    """
    Validate that the baseline path exists and contains a modules directory.
    
    Args:
        baseline_path: Path to the baseline directory
        
    Returns:
        bool: True if the baseline path is valid, False otherwise
    """
    if not baseline_path.exists():
        logging.error(f"Baseline path {baseline_path} does not exist")
        return False
        
    if not baseline_path.is_dir():
        logging.error(f"Baseline path {baseline_path} is not a directory")
        return False
        
    modules_dir = baseline_path / "modules"
    if not modules_dir.exists() or not modules_dir.is_dir():
        logging.error(f"Baseline directory {baseline_path} does not contain a modules directory")
        return False
        
    return True

def discover_source_files(root_path):
    """
    Discover all source files in the modules directory.
    
    Args:
        root_path: Path to the project root
        
    Returns:
        tuple: (
            dict: Dictionary of module names to sets of file paths relative to the module directory,
            set: Set of flat files in the modules directory (not in a module subdirectory)
        )
    """
    modules_dir = root_path / "modules"
    if not modules_dir.exists() or not modules_dir.is_dir():
        logging.error(f"Modules directory {modules_dir} does not exist or is not a directory")
        return {}, set()
        
    module_files = {}
    flat_files = set()
    
    # First, scan for flat files directly in the modules directory
    for file_path in modules_dir.glob('*'):
        if file_path.is_file() and not file_path.name.startswith('.'):
            # Store relative to modules directory
            flat_files.add(file_path.name)
    
    # Then scan module directories as before
    for module_dir in modules_dir.iterdir():
        if module_dir.is_dir() and not module_dir.name.startswith('.'):
            module_name = module_dir.name
            module_files[module_name] = set()
            
            # Find all source files in the module directory (recursively)
            for file_path in module_dir.glob('**/*'):
                if file_path.is_file() and not file_path.name.startswith('.'):
                    # Store the path relative to the module directory
                    relative_path = file_path.relative_to(module_dir)
                    module_files[module_name].add(relative_path)
    
    return module_files, flat_files

def audit_all_modules(modules_root):
    """
    Audit all modules to ensure they follow the established structure.
    
    Args:
        modules_root: Path to the root directory containing the modules
        
    Returns:
        tuple: (list of findings, count of modules audited)
    """
    if not modules_root.exists():
        logging.error(f"Modules root {modules_root} does not exist")
        return ["CRITICAL: Modules root directory does not exist"], 0
    
    modules_dir = modules_root if modules_root.name == "modules" else modules_root / "modules"
    
    if not modules_dir.exists():
        logging.error(f"Modules directory {modules_dir} does not exist")
        return ["CRITICAL: Modules directory does not exist"], 0
    
    findings = []
    module_count = 0
    
    for module_dir in modules_dir.iterdir():
        if not module_dir.is_dir() or module_dir.name.startswith('.'):
            continue
        
        module_count += 1
        module_name = module_dir.name
        
        # Check for src directory
        src_dir = module_dir / "src"
        if not src_dir.exists() or not src_dir.is_dir():
            findings.append(f"ERROR: Module '{module_name}' is missing the src/ directory")
        
        # Check for tests directory
        tests_dir = module_dir / "tests"
        if not tests_dir.exists() or not tests_dir.is_dir():
            findings.append(f"ERROR: Module '{module_name}' is missing the tests/ directory")
        
        # Check for interface file
        interface_file = src_dir / f"{module_name}.py"
        if not interface_file.exists():
            findings.append(f"WARNING: Module '{module_name}' is missing the interface file {module_name}.py")
        
        # Check for module.json
        module_json = module_dir / "module.json"
        if not module_json.exists():
            findings.append(f"WARNING: Module '{module_name}' is missing the module.json dependency manifest")
    
    return findings, module_count

def audit_with_baseline_comparison(target_root, baseline_root):
    """
    Audit modules and compare with a baseline version, reporting changes.
    
    Args:
        target_root: Path to the target directory
        baseline_root: Path to the baseline directory
        
    Returns:
        dict: Summary of changes including new, modified, and deleted modules and files
    """
    # Validate the baseline path
    if not validate_baseline_path(baseline_root):
        return {
            "status": "failed",
            "reason": "Invalid baseline path"
        }
    
    # Initialize summary structure
    summary = {
        "status": "success",
        "modules": {
            "new": [],
            "modified": [],
            "deleted": []
        },
        "files": {
            "new": 0,
            "modified": 0,
            "deleted": 0,
            "found_in_flat": 0
        }
    }
    
    # Discover files in target and baseline
    target_modules, target_flat_files = discover_source_files(target_root)
    baseline_modules, baseline_flat_files = discover_source_files(baseline_root)
    
    logging.info(f"Found {len(target_modules)} modules in target and {len(baseline_modules)} modules in baseline")
    if baseline_flat_files:
        logging.info(f"Found {len(baseline_flat_files)} flat files in baseline modules/ directory")
    
    # Find new and modified modules
    for module_name, target_files in target_modules.items():
        if module_name not in baseline_modules:
            # New module, but check if any files were moved from flat structure
            found_in_flat_files = []
            extra_files = []
            
            # Check each file in the target module
            for file_path in target_files:
                # Check if this is a file that was moved from the flat structure
                if file_path.name in baseline_flat_files:
                    found_in_flat_files.append(file_path)
                    # WSP 3.5 detailed FOUND_IN_FLAT file logging
                    logging.warning(f"[{module_name}] FOUND_IN_FLAT: Found only in baseline flat modules/, needs proper placement. (File path: {file_path})")
                else:
                    extra_files.append(file_path)
                    # WSP 3.5 detailed EXTRA file logging for new modules
                    logging.warning(f"[{module_name}] EXTRA: File not found anywhere in baseline. (File path: {file_path})")
            
            # Update counts for new module
            summary["modules"]["new"].append(module_name)
            summary["files"]["new"] += len(extra_files)
            summary["files"]["found_in_flat"] += len(found_in_flat_files)
            
            if found_in_flat_files:
                logging.debug(f"New module {module_name} has {len(found_in_flat_files)} files that were moved from flat structure")
            
            logging.info(f"New module found: {module_name} with {len(target_files)} files")
            
            # Check if this is a critical module
            module_path = target_root / "modules" / module_name
            interface_path = module_path / "src" / f"{module_name}.py"
            if interface_path.exists():
                logging.warning(f"New critical module found: {module_name}")
        else:
            # Existing module, check for file changes
            baseline_files = baseline_modules[module_name]
            
            # New files (EXTRA) or potentially FOUND_IN_FLAT
            found_in_flat_files = []
            new_files = target_files - baseline_files
            
            # Check if any "new" files actually exist in the baseline's flat files
            for file_path in list(new_files):
                # Check if this is a file that was moved from the flat structure
                if file_path.name in baseline_flat_files:
                    found_in_flat_files.append(file_path)
                    new_files.remove(file_path)
                    # WSP 3.5 detailed FOUND_IN_FLAT file logging
                    logging.warning(f"[{module_name}] FOUND_IN_FLAT: Found only in baseline flat modules/, needs proper placement. (File path: {file_path})")
            
            # Update counts for FOUND_IN_FLAT
            if found_in_flat_files:
                if module_name not in summary["modules"]["modified"]:
                    summary["modules"]["modified"].append(module_name)
                summary["files"]["found_in_flat"] += len(found_in_flat_files)
                logging.debug(f"Module {module_name} has {len(found_in_flat_files)} files that were moved from flat structure")
            
            # Report remaining new files as EXTRA
            if new_files:
                if module_name not in summary["modules"]["modified"]:
                    summary["modules"]["modified"].append(module_name)
                summary["files"]["new"] += len(new_files)
                logging.debug(f"Module {module_name} has {len(new_files)} new files")
                
                # WSP 3.5 detailed EXTRA file logging
                for extra_file in new_files:
                    logging.warning(f"[{module_name}] EXTRA: File not found anywhere in baseline. (File path: {extra_file})")
                
            # Deleted files (MISSING)
            deleted_files = baseline_files - target_files
            if deleted_files:
                if module_name not in summary["modules"]["modified"]:
                    summary["modules"]["modified"].append(module_name)
                summary["files"]["deleted"] += len(deleted_files)
                logging.debug(f"Module {module_name} has {len(deleted_files)} deleted files")
                
                # WSP 3.5 detailed MISSING file logging
                for missing_file in deleted_files:
                    logging.warning(f"[{module_name}] MISSING: File missing from target module. (Baseline path: {missing_file})")
                
            # Modified files - compare file contents
            common_files = target_files & baseline_files
            modified_files = []
            
            for common_file in common_files:
                target_file_path = target_root / "modules" / module_name / common_file
                baseline_file_path = baseline_root / "modules" / module_name / common_file
                
                # Compare file contents using hash
                target_hash = compute_file_hash(target_file_path)
                baseline_hash = compute_file_hash(baseline_file_path)
                
                if target_hash != baseline_hash:
                    modified_files.append(common_file)
                    # WSP 3.5 detailed MODIFIED file logging
                    logging.warning(f"[{module_name}] MODIFIED: Content differs from baseline. (File path: {common_file})")
            
            if modified_files:
                if module_name not in summary["modules"]["modified"]:
                    summary["modules"]["modified"].append(module_name)
                summary["files"]["modified"] += len(modified_files)
                logging.debug(f"Module {module_name} has {len(modified_files)} modified files")
    
    # Find deleted modules
    for module_name, baseline_files in baseline_modules.items():
        if module_name not in target_modules:
            summary["modules"]["deleted"].append(module_name)
            summary["files"]["deleted"] += len(baseline_files)
            logging.info(f"Deleted module found: {module_name} with {len(baseline_files)} files")
            
            # Check if this was a critical module
            module_path = baseline_root / "modules" / module_name
            interface_path = module_path / "src" / f"{module_name}.py"
            if interface_path.exists():
                logging.warning(f"Critical module deleted: {module_name}")
    
    return summary

def compute_file_hash(file_path):
    """
    Compute a SHA256 hash of a file's contents.
    
    Args:
        file_path: Path to the file
        
    Returns:
        str: Hexadecimal digest of the file hash
    """
    hash_obj = hashlib.sha256()
    
    try:
        with open(file_path, 'rb') as f:
            # Read in chunks to handle large files efficiently
            for chunk in iter(lambda: f.read(4096), b''):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except Exception as e:
        logging.error(f"Error computing hash for {file_path}: {e}")
        return None

def main():
    """Main entry point for the modular audit tool."""
    parser = argparse.ArgumentParser(description="Foundups Modular Audit Script (FMAS)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug level logging")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress most output")
    parser.add_argument("--mode", type=int, choices=[1, 2], default=1, 
                      help="Audit mode: 1=Structure audit, 2=Baseline comparison")
    parser.add_argument("--baseline", type=str, help="Path to the baseline directory for comparison (required for Mode 2)")
    
    args = parser.parse_args()
    
    # Configure logging based on verbosity flags
    log_level = logging.INFO  # Default
    if args.debug:
        log_level = logging.DEBUG
    elif args.quiet:
        log_level = logging.WARNING
    
    logging.basicConfig(
        level=log_level,
        format="%(levelname)s: %(message)s"
    )
    
    # Get the path to the project root (parent of the tools directory)
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent
    
    logging.info(f"Project root: {project_root}")
    
    if args.mode == 1:
        # Mode 1: Structure audit
        logging.info("Running FMAS Mode 1: Structure Audit")
        audit_results = audit_all_modules(project_root)
        
        # Count the issues
        error_count = 0
        warning_count = 0
        
        for finding in audit_results[0]:
            if "ERROR" in finding:
                error_count += 1
            elif "WARNING" in finding:
                warning_count += 1
        
        # Print summary
        logging.info("\nAudit Summary:")
        logging.info(f"  Modules audited: {audit_results[1]}")
        logging.info(f"  Errors found: {error_count}")
        logging.info(f"  Warnings found: {warning_count}")
        
        # Exit with non-zero status if there were errors
        if error_count > 0:
            logging.error("Audit completed with errors.")
            sys.exit(1)
        else:
            logging.info("Audit completed successfully.")
            sys.exit(0)
    
    elif args.mode == 2:
        # Mode 2: Baseline comparison
        logging.info("Running FMAS Mode 2: Baseline Comparison")
        
        # Check if baseline path is provided
        if not args.baseline:
            logging.error("Baseline path is required for Mode 2. Use --baseline to specify the path.")
            sys.exit(1)
        
        baseline_path = Path(args.baseline).resolve()
        logging.info(f"Baseline path: {baseline_path}")
        
        # Run the baseline comparison
        comparison_results = audit_with_baseline_comparison(project_root, baseline_path)
        
        if comparison_results["status"] == "failed":
            logging.error(f"Baseline comparison failed: {comparison_results.get('reason', 'Unknown error')}")
            sys.exit(1)
        
        # Print summary
        logging.info("\nBaseline Comparison Summary:")
        logging.info(f"  New modules: {len(comparison_results['modules']['new'])}")
        logging.info(f"  Modified modules: {len(comparison_results['modules']['modified'])}")
        logging.info(f"  Deleted modules: {len(comparison_results['modules']['deleted'])}")
        logging.info(f"  New files: {comparison_results['files']['new']}")
        logging.info(f"  Modified files: {comparison_results['files']['modified']}")
        logging.info(f"  Deleted files: {comparison_results['files']['deleted']}")
        logging.info(f"  Files moved from flat structure: {comparison_results['files']['found_in_flat']}")
        
        # List the specific modules affected
        if comparison_results['modules']['new'] and not args.quiet:
            logging.info("\nNew modules:")
            for module in comparison_results['modules']['new']:
                logging.info(f"  + {module}")
        
        if comparison_results['modules']['modified'] and not args.quiet:
            logging.info("\nModified modules:")
            for module in comparison_results['modules']['modified']:
                logging.info(f"  ~ {module}")
        
        if comparison_results['modules']['deleted'] and not args.quiet:
            logging.info("\nDeleted modules:")
            for module in comparison_results['modules']['deleted']:
                logging.info(f"  - {module}")
        
        # Exit with status based on whether changes were detected
        has_changes = (len(comparison_results['modules']['new']) > 0 or 
                       len(comparison_results['modules']['modified']) > 0 or 
                       len(comparison_results['modules']['deleted']) > 0)
        
        if has_changes:
            logging.warning("Changes detected between target and baseline.")
            sys.exit(2)  # Use a different exit code to indicate changes found
        else:
            logging.info("No changes detected between target and baseline.")
            sys.exit(0)
    
if __name__ == "__main__":
    main() 