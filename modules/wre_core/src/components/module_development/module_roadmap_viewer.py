"""
Module Roadmap Viewer

Handles roadmap file reading, display, and generation coordination.
Extracted from module_development_handler.py following WSP principles.

WSP Compliance:
- Single responsibility: Roadmap viewing and generation only
- Clean interfaces: Focused API for roadmap operations
- Modular cohesion: Self-contained roadmap logic
"""

from pathlib import Path
from typing import Dict, List, Any

from modules.wre_core.src.utils.logging_utils import wre_log

class ModuleRoadmapViewer:
    """
    Module Roadmap Viewer - WSP-compliant roadmap handling
    
    Responsibilities:
    - Roadmap file reading and display
    - Roadmap generation coordination
    - Roadmap template management
    """
    
    def __init__(self, project_root: Path, session_manager):
        self.project_root = project_root
        self.session_manager = session_manager
        
    def view_roadmap(self, module_name: str, engine):
        """View existing roadmap for a module."""
        wre_log(f"🗺️ Viewing roadmap for: {module_name}", "INFO")
        self.session_manager.log_operation("roadmap_view", {"module": module_name})
        
        try:
            # Find module path
            module_path = self._find_module_path(module_name)
            if not module_path:
                wre_log(f"❌ Module not found: {module_name}", "ERROR")
                return
                
            # Check if ROADMAP.md exists
            roadmap_file = module_path / "ROADMAP.md"
            if roadmap_file.exists():
                self._display_roadmap_content(module_name, roadmap_file)
            else:
                wre_log(f"⚠️ No ROADMAP.md found for {module_name}", "WARNING")
                # Offer to generate one
                generate_choice = engine.ui_interface.prompt_yes_no("Generate a roadmap?")
                if generate_choice:
                    self._generate_intelligent_roadmap(module_name, module_path)
                    
        except Exception as e:
            wre_log(f"❌ Roadmap view failed: {e}", "ERROR")
            self.session_manager.log_operation("roadmap_view", {"error": str(e)})
            
    def _display_roadmap_content(self, module_name: str, roadmap_file: Path):
        """Display roadmap file content."""
        wre_log(f"📋 Roadmap for {module_name}:", "INFO")
        try:
            with open(roadmap_file, 'r', encoding='utf-8') as f:
                content = f.read()
                print(content)
                
            self.session_manager.log_achievement("roadmap_view", f"Displayed roadmap for {module_name}")
            
        except Exception as e:
            wre_log(f"❌ Failed to read roadmap file: {e}", "ERROR")
            
    def _generate_intelligent_roadmap(self, module_name: str, module_path: Path):
        """Generate an intelligent roadmap based on module status."""
        wre_log(f"🎯 Generating roadmap for: {module_name}", "INFO")
        
        try:
            # Get module status for roadmap generation
            status_info = self._get_basic_module_status(module_path)
            
            # Create intelligent roadmap
            roadmap = self._create_intelligent_roadmap(module_name, status_info)
            
            # Save roadmap to file
            self._save_roadmap_to_file(module_path, roadmap, module_name)
            
            # Display generated roadmap
            wre_log(f"📋 Generated Roadmap for {module_name}:", "INFO")
            self._display_roadmap_phases(roadmap)
            
            self.session_manager.log_achievement("roadmap_generation", f"Generated roadmap for {module_name}")
            
        except Exception as e:
            wre_log(f"❌ Roadmap generation failed: {e}", "ERROR")
            
    def _create_intelligent_roadmap(self, module_name: str, status_info: Dict[str, Any]) -> Dict[str, List[str]]:
        """Create an intelligent roadmap based on module status."""
        roadmap = {
            "Phase 1 - Foundation": [],
            "Phase 2 - Development": [],
            "Phase 3 - Testing": [],
            "Phase 4 - Documentation": [],
            "Phase 5 - Integration": []
        }
        
        # Phase 1 - Foundation
        if status_info["source_count"] == 0:
            roadmap["Phase 1 - Foundation"].extend([
                "Create src/ directory structure",
                "Add __init__.py files",
                "Define core module interface",
                "Set up basic module structure"
            ])
            
        # Phase 2 - Development
        if status_info["source_count"] < 3:
            roadmap["Phase 2 - Development"].extend([
                "Implement core functionality",
                "Add error handling",
                "Create utility functions",
                "Add configuration management"
            ])
            
        # Phase 3 - Testing
        if status_info["test_count"] == 0:
            roadmap["Phase 3 - Testing"].extend([
                "Create tests/ directory",
                "Add unit tests for core functions",
                "Add integration tests",
                "Set up test coverage reporting"
            ])
            
        # Phase 4 - Documentation
        if status_info["docs_status"] != "Complete":
            roadmap["Phase 4 - Documentation"].extend([
                "Create comprehensive README.md",
                "Add API documentation",
                "Create usage examples",
                "Update ROADMAP.md with progress"
            ])
            
        # Phase 5 - Integration
        roadmap["Phase 5 - Integration"].extend([
            "Integrate with WSP framework",
            "Add WSP compliance checks",
            "Test with other modules",
            "Prepare for deployment"
        ])
        
        return roadmap
        
    def _save_roadmap_to_file(self, module_path: Path, roadmap: Dict[str, List[str]], module_name: str):
        """Save roadmap to ROADMAP.md file."""
        try:
            roadmap_file = module_path / "ROADMAP.md"
            
            # Create roadmap content
            content = f"""# {module_name} Development Roadmap

## Overview
Intelligent development roadmap generated by WRE system.

## Development Phases

"""
            
            for phase, tasks in roadmap.items():
                content += f"### {phase}\n"
                for task in tasks:
                    content += f"- [ ] {task}\n"
                content += "\n"
                
            # Add metadata
            content += f"""
## Metadata
- **Generated**: {self.session_manager.get_current_timestamp()}
- **Generated by**: WRE Module Roadmap Viewer
- **Status**: Active Development

## Notes
This roadmap was automatically generated based on current module status.
Update this file as development progresses.
"""
            
            # Write to file
            with open(roadmap_file, 'w', encoding='utf-8') as f:
                f.write(content)
                
            wre_log(f"✅ Roadmap saved to {roadmap_file}", "SUCCESS")
            
        except Exception as e:
            wre_log(f"❌ Failed to save roadmap: {e}", "ERROR")
            
    def _display_roadmap_phases(self, roadmap: Dict[str, List[str]]):
        """Display roadmap phases."""
        for phase, tasks in roadmap.items():
            wre_log(f"  {phase}:", "INFO")
            for task in tasks:
                wre_log(f"    - {task}", "INFO")
                
    def _find_module_path(self, module_name: str) -> Path:
        """Find the path to a module by name."""
        modules_dir = self.project_root / "modules"
        
        for module_path in modules_dir.rglob("*"):
            if module_path.is_dir() and module_path.name == module_name:
                return module_path
                
        return None
        
    def _get_basic_module_status(self, module_path: Path) -> Dict[str, Any]:
        """Get basic module status for roadmap generation."""
        status_info = {
            "test_count": 0,
            "source_count": 0,
            "docs_status": "Incomplete"
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
            
        # Check documentation
        required_docs = ["README.md", "ROADMAP.md", "ModLog.md", "INTERFACE.md"]
        existing_docs = sum(1 for doc in required_docs if (module_path / doc).exists())
        
        if existing_docs == len(required_docs):
            status_info["docs_status"] = "Complete"
        elif existing_docs > 0:
            status_info["docs_status"] = "Partial"
        else:
            status_info["docs_status"] = "Missing"
            
        return status_info 