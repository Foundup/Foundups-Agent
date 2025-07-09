"""
Module Status Manager

Handles module status information gathering, display, and metadata management.
Extracted from module_development_handler.py following WSP principles.

WSP Compliance:
- Single responsibility: Module status management only
- Clean interfaces: Focused API for status operations
- Modular cohesion: Self-contained status logic
"""

from pathlib import Path
from typing import Dict, Any, Optional

from modules.wre_core.src.utils.logging_utils import wre_log

class ModuleStatusManager:
    """
    Module Status Manager - WSP-compliant status handling
    
    Responsibilities:
    - Module status information gathering
    - Status display and formatting
    - Module metadata management
    - Module path resolution
    """
    
    def __init__(self, project_root: Path, session_manager):
        self.project_root = project_root
        self.session_manager = session_manager
        
    def display_module_status(self, module_name: str, engine):
        """Display comprehensive status for a specific module."""
        wre_log(f"📊 Displaying status for: {module_name}", "INFO")
        self.session_manager.log_operation("module_status", {"module": module_name})
        
        try:
            # Find module path
            module_path = self.find_module_path(module_name)
            if not module_path:
                wre_log(f"❌ Module not found: {module_name}", "ERROR")
                return
                
            # Get module status information
            status_info = self.get_module_status_info(module_path, module_name)
            
            # Display formatted status
            self._display_formatted_status(module_name, status_info)
            
            self.session_manager.log_achievement("module_status", f"Displayed status for {module_name}")
            
        except Exception as e:
            wre_log(f"❌ Module status display failed: {e}", "ERROR")
            self.session_manager.log_operation("module_status", {"error": str(e)})
            
    def find_module_path(self, module_name: str) -> Optional[Path]:
        """Find the path to a module by name."""
        # Search in modules directory
        modules_dir = self.project_root / "modules"
        
        # Search recursively for module
        for module_path in modules_dir.rglob("*"):
            if module_path.is_dir() and module_path.name == module_name:
                return module_path
                
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
            "wsp_compliance": "Unknown"
        }
        
        # Count test files
        tests_dir = module_path / "tests"
        if tests_dir.exists():
            test_files = list(tests_dir.rglob("test_*.py"))
            status_info["test_count"] = len(test_files)
            
        # Count source files
        src_dir = module_path / "src"
        if src_dir.exists():
            source_files = list(src_dir.rglob("*.py"))
            status_info["source_count"] = len(source_files)
            
        # Check documentation status
        status_info["docs_status"] = self._assess_documentation_status(module_path)
        
        # Determine overall module status
        status_info["status"] = self._determine_module_status(status_info)
        
        # Check WSP compliance
        status_info["wsp_compliance"] = self._assess_wsp_compliance(module_path)
        
        return status_info
        
    def _display_formatted_status(self, module_name: str, status_info: Dict[str, Any]):
        """Display formatted status information."""
        wre_log(f"📋 Status for {module_name}:", "INFO")
        wre_log(f"  📁 Path: {status_info['path']}", "INFO")
        wre_log(f"  🏢 Domain: {status_info['domain']}", "INFO")
        wre_log(f"  📊 Status: {status_info['status']}", "INFO")
        wre_log(f"  🧪 Test files: {status_info['test_count']}", "INFO")
        wre_log(f"  📝 Source files: {status_info['source_count']}", "INFO")
        wre_log(f"  📚 Documentation: {status_info['docs_status']}", "INFO")
        wre_log(f"  ✅ WSP Compliance: {status_info['wsp_compliance']}", "INFO")
        
    def _assess_documentation_status(self, module_path: Path) -> str:
        """Assess documentation completeness."""
        required_docs = ["README.md", "ROADMAP.md", "ModLog.md", "INTERFACE.md"]
        existing_docs = []
        
        for doc in required_docs:
            if (module_path / doc).exists():
                existing_docs.append(doc)
                
        if len(existing_docs) == len(required_docs):
            return "Complete"
        elif len(existing_docs) > 0:
            return f"Partial ({len(existing_docs)}/{len(required_docs)})"
        else:
            return "Missing"
            
    def _determine_module_status(self, status_info: Dict[str, Any]) -> str:
        """Determine overall module status."""
        if status_info["source_count"] > 0 and status_info["test_count"] > 0:
            return "✅ Active"
        elif status_info["source_count"] > 0:
            return "🔄 In Development"
        else:
            return "📋 Planned"
            
    def _assess_wsp_compliance(self, module_path: Path) -> str:
        """Assess WSP compliance level."""
        compliance_indicators = {
            "structure": (module_path / "src").exists() and (module_path / "tests").exists(),
            "readme": (module_path / "README.md").exists(),
            "interface": (module_path / "INTERFACE.md").exists(),
            "modlog": (module_path / "ModLog.md").exists(),
            "init_files": (module_path / "__init__.py").exists()
        }
        
        compliance_score = sum(compliance_indicators.values())
        total_checks = len(compliance_indicators)
        
        if compliance_score == total_checks:
            return "✅ Full"
        elif compliance_score >= total_checks * 0.7:
            return "🟡 Partial"
        else:
            return "❌ Low" 