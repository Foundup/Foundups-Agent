"""
Module Status Manager Component

Handles module status display and information gathering.
Extracted from module_development_handler.py per WSP 62 refactoring requirements.

WSP Compliance:
- WSP 62: Large File and Refactoring Enforcement Protocol (refactoring)
- WSP 1: Single responsibility principle (status display only)
- WSP 49: Module directory structure standardization
"""

from pathlib import Path
from typing import Dict, Any, Optional

from modules.wre_core.src.utils.logging_utils import wre_log


class ModuleStatusManager:
    """
    Module Status Manager - Handles module status display and information gathering
    
    Responsibilities:
    - Module status information collection
    - Module path discovery
    - Status display formatting
    - Documentation status checking
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        
    def display_module_status(self, module_name: str, session_manager):
        """Display status for a specific module."""
        wre_log(f"📊 Displaying status for: {module_name}", "INFO")
        session_manager.log_operation("module_status", {"module": module_name})
        
        try:
            # Find module path
            module_path = self.find_module_path(module_name)
            if not module_path:
                wre_log(f"❌ Module not found: {module_name}", "ERROR")
                return
                
            # Get module status information
            status_info = self.get_module_status_info(module_path, module_name)
            
            # Display status
            wre_log(f"📋 Status for {module_name}:", "INFO")
            wre_log(f"  Path: {status_info['path']}", "INFO")
            wre_log(f"  Domain: {status_info['domain']}", "INFO")
            wre_log(f"  Status: {status_info['status']}", "INFO")
            wre_log(f"  Test files: {status_info['test_count']}", "INFO")
            wre_log(f"  Source files: {status_info['source_count']}", "INFO")
            wre_log(f"  Documentation: {status_info['docs_status']}", "INFO")
            
            # WSP 62 size compliance check
            if status_info.get('size_violations'):
                wre_log(f"  ⚠️ WSP 62 Size Violations: {len(status_info['size_violations'])}", "WARNING")
                for violation in status_info['size_violations']:
                    wre_log(f"    - {violation}", "WARNING")
            
            session_manager.log_achievement("module_status", f"Displayed status for {module_name}")
            
        except Exception as e:
            wre_log(f"❌ Module status display failed: {e}", "ERROR")
            session_manager.log_operation("module_status", {"error": str(e)})
            
    def find_module_path(self, module_name: str) -> Optional[Path]:
        """Find the path to a module by name or full path."""
        try:
            # Clean up the module name - handle full paths
            if module_name.startswith("modules/"):
                # Extract just the module name from full path like "modules/platform_integration/remote_builder"
                parts = module_name.split("/")
                if len(parts) >= 3:
                    domain = parts[1]  # e.g., "platform_integration"
                    actual_module_name = parts[2]  # e.g., "remote_builder"
                    
                    # Try direct path first
                    direct_path = self.project_root / "modules" / domain / actual_module_name
                    if direct_path.exists() and direct_path.is_dir():
                        return direct_path
                        
                    # FIXED: Silent handling of missing modules - don't error
                    return None
            else:
                # Simple module name - search across all domains
                modules_dir = self.project_root / "modules"
                if not modules_dir.exists():
                    return None
                    
                # Search all domain directories
                for domain_dir in modules_dir.iterdir():
                    if domain_dir.is_dir() and not domain_dir.name.startswith('.'):
                        module_path = domain_dir / module_name
                        if module_path.exists() and module_path.is_dir():
                            return module_path
                            
                # FIXED: Return None instead of raising error for missing modules
                return None
                
        except Exception as e:
            # AUTONOMOUS: Silent error handling - don't log module search failures
            return None
        
    def get_module_status_info(self, module_path: Path, module_name: str) -> Dict[str, Any]:
        """Get comprehensive status information for a module."""
        status_info = {
            "path": str(module_path),
            "domain": module_path.parent.name,
            "status": "Unknown",
            "test_count": 0,
            "source_count": 0,
            "docs_status": "Incomplete",
            "size_violations": []
        }
        
        # Count test files
        tests_dir = module_path / "tests"
        if tests_dir.exists():
            test_files = list(tests_dir.rglob("test_*.py"))
            status_info["test_count"] = len(test_files)
            
        # Count source files and check WSP 62 compliance
        src_dir = module_path / "src"
        if src_dir.exists():
            source_files = list(src_dir.rglob("*.py"))
            status_info["source_count"] = len(source_files)
            
            # WSP 62 size checking
            status_info["size_violations"] = self._check_file_sizes(source_files)
            
        # Check documentation
        readme_file = module_path / "README.md"
        roadmap_file = module_path / "ROADMAP.md"
        
        if readme_file.exists() and roadmap_file.exists():
            status_info["docs_status"] = "Complete"
        elif readme_file.exists() or roadmap_file.exists():
            status_info["docs_status"] = "Partial"
        else:
            status_info["docs_status"] = "Missing"
            
        # Determine module status
        if status_info["source_count"] > 0 and status_info["test_count"] > 0:
            status_info["status"] = "Active"
        elif status_info["source_count"] > 0:
            status_info["status"] = "In Development"
        else:
            status_info["status"] = "Planned"
            
        return status_info
        
    def _check_file_sizes(self, source_files) -> list:
        """Check files for WSP 62 size violations."""
        violations = []
        python_threshold = 500  # WSP 62 threshold for Python files
        
        for file_path in source_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    line_count = sum(1 for line in f)
                    
                if line_count > python_threshold:
                    severity = "CRITICAL" if line_count > python_threshold * 1.5 else "WARNING"
                    violations.append(f"{severity}: {file_path.name} ({line_count} lines > {python_threshold})")
                elif line_count > python_threshold * 0.9:  # 90% threshold
                    violations.append(f"APPROACHING: {file_path.name} ({line_count} lines)")
                    
            except Exception:
                # Skip files that can't be read
                continue
                
        return violations 