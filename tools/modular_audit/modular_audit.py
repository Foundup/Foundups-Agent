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
- NOW SUPPORTS: Enterprise Domain architecture (WSP 3)

Mode 2: Baseline comparison
- Performs all Mode 1 checks
- Additionally compares the module structure against a baseline
- Reports added, modified, and removed modules and files
- NOW SUPPORTS: Hierarchical domain structure comparison
"""

import argparse
import json
import logging
import os
import sys
import hashlib
from pathlib import Path

VERSION = "0.8.0"

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

# Define critical modules that should prompt warnings if modified
CRITICAL_MODULES = {"core", "security", "auth", "config"}

# Define recognized Enterprise Domains (WSP 3)
ENTERPRISE_DOMAINS = {
    "ai_intelligence",
    "communication", 
    "platform_integration",
    "infrastructure",
    "data_processing",
    "gamification",
    "foundups",
    "blockchain"
}

def is_module_directory(path):
    """
    Check if a directory is an actual module (has src/ and/or tests/ directories).
    
    Args:
        path: Path to check
        
    Returns:
        bool: True if this appears to be a module directory
    """
    if not path.is_dir():
        return False
        
    # A module should have at least src/ directory
    src_dir = path / "src"
    tests_dir = path / "tests"
    
    return src_dir.exists() or tests_dir.exists()

def discover_modules_recursive(modules_root):
    """
    Recursively discover all modules in the Enterprise Domain structure.
    
    Args:
        modules_root: Path to the modules directory
        
    Returns:
        list: List of tuples (module_path, module_name, domain_path)
    """
    if not modules_root.exists() or not modules_root.is_dir():
        return []
    
    modules = []
    
    def scan_directory(current_path, relative_path=""):
        """Recursively scan for modules."""
        for item in current_path.iterdir():
            if not item.is_dir() or item.name.startswith('.') or item.name == '__pycache__':
                continue
                
            item_relative = relative_path + "/" + item.name if relative_path else item.name
            
            # Check if this is a module
            if is_module_directory(item):
                modules.append((item, item.name, item_relative))
                logging.debug(f"Found module: {item_relative}")
            else:
                # Continue scanning deeper
                scan_directory(item, item_relative)
    
    scan_directory(modules_root)
    return modules

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
    Discover all source files in the modules directory using Enterprise Domain structure.
    
    Args:
        root_path: Path to the project root
        
    Returns:
        tuple: (
            dict: Dictionary of module paths to sets of file paths relative to the module directory,
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
    
    # Discover all modules using recursive search
    modules = discover_modules_recursive(modules_dir)
    
    for module_path, module_name, domain_path in modules:
        # Use domain_path as the key to maintain uniqueness
        module_key = domain_path
        module_files[module_key] = set()
        
        # Find all source files in the module directory (recursively)
        for file_path in module_path.glob('**/*'):
            if file_path.is_file() and not file_path.name.startswith('.') and '__pycache__' not in str(file_path):
                # Store the path relative to the module directory
                relative_path = file_path.relative_to(module_path)
                module_files[module_key].add(str(relative_path))  # Convert Path to string for consistent comparison
    
    return module_files, flat_files

def audit_all_modules(modules_root):
    """
    Audit all modules to ensure they follow the established structure.
    Now supports Enterprise Domain architecture (WSP 3).
    
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
    
    # Check for Enterprise Domain compliance
    domain_findings = audit_enterprise_domains(modules_dir)
    findings.extend(domain_findings)
    
    # Discover all modules recursively
    modules = discover_modules_recursive(modules_dir)
    
    for module_path, module_name, domain_path in modules:
        module_count += 1
        
        # Check for src directory
        src_dir = module_path / "src"
        if not src_dir.exists() or not src_dir.is_dir():
            findings.append(f"ERROR: Module '{domain_path}' is missing the src/ directory")
        
        # Check for tests directory
        tests_dir = module_path / "tests"
        if not tests_dir.exists() or not tests_dir.is_dir():
            findings.append(f"ERROR: Module '{domain_path}' is missing the tests/ directory")
        else:
            # Check for tests/README.md (WSP requirement)
            test_readme = tests_dir / "README.md"
            if not test_readme.exists():
                findings.append(f"WARNING: Module '{domain_path}' is missing tests/README.md file")
        
        # Check for interface file (more flexible naming)
        if src_dir.exists():
            interface_files = list(src_dir.glob("*.py"))
            if not interface_files:
                findings.append(f"WARNING: Module '{domain_path}' has no Python files in src/ directory")
        
        # Check for module.json or requirements.txt (dependency manifest)
        module_json = module_path / "module.json"
        requirements_txt = module_path / "requirements.txt"
        if not module_json.exists() and not requirements_txt.exists():
            findings.append(f"WARNING: Module '{domain_path}' is missing dependency manifest (module.json or requirements.txt)")
    
    return findings, module_count

def audit_enterprise_domains(modules_dir):
    """
    Audit Enterprise Domain structure compliance (WSP 3).
    
    Args:
        modules_dir: Path to the modules directory
        
    Returns:
        list: List of domain-related findings
    """
    findings = []
    
    # Check for recognized Enterprise Domains
    found_domains = set()
    unknown_domains = set()
    
    for item in modules_dir.iterdir():
        if not item.is_dir() or item.name.startswith('.') or item.name == '__pycache__':
            continue
            
        # Skip non-domain files
        if item.is_file():
            continue
            
        if item.name in ENTERPRISE_DOMAINS:
            found_domains.add(item.name)
        else:
            # Check if this might be a legacy flat module
            if is_module_directory(item):
                findings.append(f"WARNING: Found potential flat module '{item.name}' - should be moved to appropriate Enterprise Domain")
            else:
                unknown_domains.add(item.name)
    
    # Report unknown domains
    for domain in unknown_domains:
        findings.append(f"WARNING: Unknown Enterprise Domain '{domain}' - not in recognized domains: {', '.join(sorted(ENTERPRISE_DOMAINS))}")
    
    # Report on domain coverage
    if found_domains:
        logging.debug(f"Found Enterprise Domains: {', '.join(sorted(found_domains))}")
    
    return findings

def compute_file_hash(file_path):
    """
    Compute a SHA256 hash of a file's contents.
    
    Args:
        file_path: Path to the file
        
    Returns:
        str: Hexadecimal digest of the file hash, or None if the file cannot be read
    """
    hash_obj = hashlib.sha256()
    
    try:
        with open(file_path, 'rb') as f:
            # Read in chunks to handle large files efficiently
            for chunk in iter(lambda: f.read(4096), b''):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except FileNotFoundError:
        logging.error(f"Error computing hash: File not found: {file_path}")
        return None
    except PermissionError:
        logging.error(f"Error computing hash: Permission denied for file: {file_path}")
        return None
    except Exception as e:
        logging.error(f"Error computing hash for {file_path}: {str(e)}")
        return None

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
                if isinstance(file_path, Path):
                    file_name = file_path.name
                else:
                    file_name = Path(file_path).name
                    
                if file_name in baseline_flat_files:
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
            if module_name in CRITICAL_MODULES:
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
                if isinstance(file_path, Path):
                    file_name = file_path.name
                else:
                    file_name = Path(file_path).name
                    
                if file_name in baseline_flat_files:
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
                # Handle hierarchical paths - module_name is now domain_path
                target_file_path = target_root / "modules" / Path(module_name) / Path(common_file)
                baseline_file_path = baseline_root / "modules" / Path(module_name) / Path(common_file)
                
                # Compare file contents using hash
                target_hash = compute_file_hash(target_file_path)
                baseline_hash = compute_file_hash(baseline_file_path)
                
                if target_hash is not None and baseline_hash is not None and target_hash != baseline_hash:
                    modified_files.append(common_file)
                    # WSP 3.5 detailed MODIFIED file logging
                    logging.warning(f"[{module_name}] MODIFIED: Content differs from baseline src/. (File path: {common_file})")
            
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
            if module_name in CRITICAL_MODULES:
                logging.warning(f"Critical module deleted: {module_name}")
            
            # WSP 3.5 detailed MISSING file logging for all files in the deleted module
            for missing_file in baseline_files:
                logging.warning(f"[{module_name}] MISSING: File missing from target module. (Baseline path: {missing_file})")
    
    # Determine overall status based on findings
    has_changes = (
        len(summary["modules"]["new"]) > 0 or 
        len(summary["modules"]["modified"]) > 0 or 
        len(summary["modules"]["deleted"]) > 0
    )
    
    if has_changes:
        summary["has_changes"] = True
    else:
        summary["has_changes"] = False
        
    return summary

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Foundups Modular Audit System (FMAS)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug level logging")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress most output")
    parser.add_argument("--mode", type=int, choices=[1, 2], default=1, help="Audit mode: 1=Structure audit, 2=Baseline comparison")
    parser.add_argument("--baseline", type=str, help="Path to the baseline directory for comparison (required for Mode 2)")
    
    args = parser.parse_args()

    # Set logging level based on arguments
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.verbose:
        logging.getLogger().setLevel(logging.INFO)
    elif args.quiet:
        logging.getLogger().setLevel(logging.ERROR)

    project_root = Path.cwd()
    logging.info(f"Project root: {project_root}")

    if args.mode == 1:
        logging.info("Running FMAS Mode 1: Structure Audit")
        
        # Run the audit and get the findings
        findings, module_count = audit_all_modules(project_root)
        
        # Print the findings if there are any
        if findings:
            logging.info("\nDetailed Findings:")
            for finding in findings:
                if "ERROR" in finding:
                    logging.error(f"- {finding}")
                elif "WARNING" in finding:
                    logging.warning(f"- {finding}")
                else:
                    logging.info(f"- {finding}")
            print() # Add a newline for readability

        # Prepare summary
        summary_findings = {
            "errors": len([f for f in findings if "ERROR" in f]),
            "warnings": len([f for f in findings if "WARNING" in f])
        }

        logging.info("Audit Summary:")
        logging.info(f"  Modules audited: {module_count}")
        logging.info(f"  Errors found: {summary_findings['errors']}")
        logging.info(f"  Warnings found: {summary_findings['warnings']}")

        if summary_findings["errors"] > 0:
            logging.error("Audit completed with errors.")
            sys.exit(1)
        elif summary_findings["warnings"] > 0:
            logging.warning("Audit completed with warnings.")
        else:
            logging.info("Audit completed with no findings.")
            
    elif args.mode == 2:
        if not args.baseline:
            logging.error("Baseline path is required for Mode 2")
            sys.exit(1)
            
        baseline_root = Path(args.baseline).resolve()
        if not validate_baseline_path(baseline_root):
            sys.exit(1)
            
        logging.info(f"Running FMAS Mode 2: Baseline Comparison against {baseline_root}")
        
        # Run the audit and get the findings
        audit_results = audit_with_baseline_comparison(project_root, baseline_root)
        
        # Prepare summary
        error_count = len(audit_results[0])
        warning_count = len(audit_results[1])
        
        logging.info("Audit Summary:")
        logging.info(f"  Errors found: {error_count}")
        logging.info(f"  Warnings found: {warning_count}")
        
        # Print the findings if there are any
        if audit_results[0]:
            logging.info("\nDetailed Findings:")
            for finding in audit_results[0]:
                if "ERROR" in finding:
                    logging.error(f"- {finding}")
                elif "WARNING" in finding:
                    logging.warning(f"- {finding}")
                else:
                    logging.info(f"- {finding}")
            print() # Add a newline for readability
        
        # Exit with non-zero status if there were errors
        if error_count > 0:
            logging.error("Audit completed with errors.")
            sys.exit(1)
        else:
            logging.info("Audit completed with no findings.")

if __name__ == "__main__":
    main() 