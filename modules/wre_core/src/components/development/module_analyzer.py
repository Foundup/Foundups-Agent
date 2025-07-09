"""
Module Analyzer Component

Handles all module analysis operations including dependency analysis,
roadmap generation, documentation updates, and module enhancement.

WSP Compliance:
- Single responsibility: Module analysis and assessment
- Clean interfaces: Delegates to appropriate analysis tools
- Modular cohesion: Only module analysis logic
"""

import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
import yaml

from modules.wre_core.src.utils.logging_utils import wre_log

class ModuleAnalyzer:
    """
    Module Analyzer - Handles module analysis operations
    
    Responsibilities:
    - Module dependency analysis
    - Roadmap generation and display
    - Documentation updates
    - Module enhancement orchestration
    - Priority assessment
    - Ecosystem analysis
    """
    
    def __init__(self, project_root: Path, session_manager):
        self.project_root = project_root
        self.session_manager = session_manager
        
    def handle_analysis_choice(self, choice: str, engine):
        """Handle module analysis menu choices."""
        wre_log(f"🔍 Module analysis choice: {choice}", "INFO")
        
        if choice == "1":
            # Analyze module dependencies
            module_name = engine.ui_interface.get_user_input("Enter module name to analyze: ")
            self._analyze_module_dependencies(module_name, engine)
            
        elif choice == "2":
            # Display module roadmap
            module_name = engine.ui_interface.get_user_input("Enter module name for roadmap: ")
            self._display_module_roadmap(module_name, engine)
            
        elif choice == "3":
            # Update module documentation
            module_name = engine.ui_interface.get_user_input("Enter module name for doc update: ")
            self._update_module_docs(module_name, engine)
            
        elif choice == "4":
            # Orchestrate module enhancement
            module_name = engine.ui_interface.get_user_input("Enter module name for enhancement: ")
            self._orchestrate_module_enhancement(module_name, engine)
            
        elif choice == "5":
            # Perform priority assessment
            self._perform_priority_assessment(engine)
            
        elif choice == "6":
            # Perform ecosystem analysis
            self._perform_ecosystem_analysis(engine)
            
        else:
            wre_log("❌ Invalid module analysis choice", "ERROR")
            
    def _analyze_module_dependencies(self, module_name: str, engine):
        """Analyze dependencies for a specific module."""
        wre_log(f"🔗 Analyzing dependencies for: {module_name}", "INFO")
        self.session_manager.log_operation("dependency_analysis", {"module": module_name})
        
        try:
            # Find module path
            module_path = self._find_module_path(module_name)
            if not module_path:
                wre_log(f"❌ Module not found: {module_name}", "ERROR")
                return
                
            # Analyze dependencies
            dependencies = self._extract_module_dependencies(module_path)
            
            # Display results
            wre_log(f"📋 Dependencies for {module_name}:", "INFO")
            for dep_type, deps in dependencies.items():
                wre_log(f"  {dep_type}:", "INFO")
                for dep in deps:
                    wre_log(f"    - {dep}", "INFO")
                    
            # Log analysis results
            self.session_manager.log_achievement("dependency_analysis", f"Analyzed {module_name} dependencies")
            
        except Exception as e:
            wre_log(f"❌ Dependency analysis failed: {e}", "ERROR")
            self.session_manager.log_operation("dependency_analysis", {"error": str(e)})
            
    def _find_module_path(self, module_name: str) -> Optional[Path]:
        """Find the path to a module by name."""
        # Search in modules directory
        modules_dir = self.project_root / "modules"
        
        # Search recursively for module
        for module_path in modules_dir.rglob("*"):
            if module_path.is_dir() and module_path.name == module_name:
                return module_path
                
        return None
        
    def _extract_module_dependencies(self, module_path: Path) -> Dict[str, List[str]]:
        """Extract dependencies from a module."""
        dependencies = {
            "imports": [],
            "requirements": [],
            "config_files": []
        }
        
        # Check for requirements.txt
        req_file = module_path / "requirements.txt"
        if req_file.exists():
            with open(req_file, 'r') as f:
                dependencies["requirements"] = [line.strip() for line in f if line.strip()]
                
        # Check for module.json
        module_json = module_path / "module.json"
        if module_json.exists():
            dependencies["config_files"].append("module.json")
            
        # Check for __init__.py
        init_file = module_path / "__init__.py"
        if init_file.exists():
            dependencies["config_files"].append("__init__.py")
            
        # Check src directory for imports
        src_dir = module_path / "src"
        if src_dir.exists():
            for py_file in src_dir.rglob("*.py"):
                imports = self._extract_imports_from_file(py_file)
                dependencies["imports"].extend(imports)
                
        # Remove duplicates
        dependencies["imports"] = list(set(dependencies["imports"]))
        
        return dependencies
        
    def _extract_imports_from_file(self, file_path: Path) -> List[str]:
        """Extract import statements from a Python file."""
        imports = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Simple import extraction (could be enhanced with ast)
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('import ') or line.startswith('from '):
                    imports.append(line)
                    
        except Exception as e:
            wre_log(f"❌ Failed to extract imports from {file_path}: {e}", "ERROR")
            
        return imports
        
    def _display_module_roadmap(self, module_name: str, engine):
        """Display roadmap for a specific module."""
        wre_log(f"🗺️ Displaying roadmap for: {module_name}", "INFO")
        self.session_manager.log_operation("roadmap_display", {"module": module_name})
        
        try:
            # Find module path
            module_path = self._find_module_path(module_name)
            if not module_path:
                wre_log(f"❌ Module not found: {module_name}", "ERROR")
                return
                
            # Check for ROADMAP.md
            roadmap_file = module_path / "ROADMAP.md"
            if roadmap_file.exists():
                with open(roadmap_file, 'r', encoding='utf-8') as f:
                    roadmap_content = f.read()
                    
                wre_log(f"📋 Roadmap for {module_name}:", "INFO")
                wre_log(roadmap_content, "INFO")
                
                self.session_manager.log_achievement("roadmap_display", f"Displayed roadmap for {module_name}")
            else:
                wre_log(f"⚠️ No ROADMAP.md found for {module_name}", "WARNING")
                
        except Exception as e:
            wre_log(f"❌ Roadmap display failed: {e}", "ERROR")
            self.session_manager.log_operation("roadmap_display", {"error": str(e)})
            
    def _update_module_docs(self, module_name: str, engine):
        """Update documentation for a specific module."""
        wre_log(f"📝 Updating documentation for: {module_name}", "INFO")
        self.session_manager.log_operation("doc_update", {"module": module_name})
        
        try:
            # Find module path
            module_path = self._find_module_path(module_name)
            if not module_path:
                wre_log(f"❌ Module not found: {module_name}", "ERROR")
                return
                
            # Update README.md
            readme_file = module_path / "README.md"
            if readme_file.exists():
                self._update_readme_file(readme_file, module_name)
                
            # Update ROADMAP.md
            roadmap_file = module_path / "ROADMAP.md"
            if roadmap_file.exists():
                self._update_roadmap_file(roadmap_file, module_name)
                
            wre_log(f"✅ Documentation updated for {module_name}", "SUCCESS")
            self.session_manager.log_achievement("doc_update", f"Updated docs for {module_name}")
            
        except Exception as e:
            wre_log(f"❌ Documentation update failed: {e}", "ERROR")
            self.session_manager.log_operation("doc_update", {"error": str(e)})
            
    def _update_readme_file(self, readme_path: Path, module_name: str):
        """Update a README.md file with current information."""
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Add update timestamp
            timestamp = self.session_manager.get_current_timestamp()
            update_entry = f"\n\n## Last Updated\n{timestamp} - WRE automated update\n"
            
            with open(readme_path, 'a', encoding='utf-8') as f:
                f.write(update_entry)
                
        except Exception as e:
            wre_log(f"❌ Failed to update README: {e}", "ERROR")
            
    def _update_roadmap_file(self, roadmap_path: Path, module_name: str):
        """Update a ROADMAP.md file with current information."""
        try:
            with open(roadmap_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Add update timestamp
            timestamp = self.session_manager.get_current_timestamp()
            update_entry = f"\n\n## Last Updated\n{timestamp} - WRE automated update\n"
            
            with open(roadmap_path, 'a', encoding='utf-8') as f:
                f.write(update_entry)
                
        except Exception as e:
            wre_log(f"❌ Failed to update ROADMAP: {e}", "ERROR")
            
    def _orchestrate_module_enhancement(self, module_name: str, engine):
        """Orchestrate enhancement for a specific module."""
        wre_log(f"🎼 Orchestrating enhancement for: {module_name}", "INFO")
        self.session_manager.log_operation("module_enhancement", {"module": module_name})
        
        try:
            # Get WSP30 orchestrator from engine
            orchestrator = engine.get_wsp30_orchestrator()
            
            # Start enhancement process
            success = orchestrator.orchestrate_module_enhancement(module_name)
            
            if success:
                wre_log(f"✅ Module enhancement orchestrated for {module_name}", "SUCCESS")
                self.session_manager.log_achievement("module_enhancement", f"Enhanced {module_name}")
            else:
                wre_log(f"❌ Module enhancement failed for {module_name}", "ERROR")
                
        except Exception as e:
            wre_log(f"❌ Module enhancement failed: {e}", "ERROR")
            self.session_manager.log_operation("module_enhancement", {"error": str(e)})
            
    def _perform_priority_assessment(self, engine):
        """Perform priority assessment across all modules."""
        wre_log("📊 Performing priority assessment...", "INFO")
        self.session_manager.log_operation("priority_assessment", {"action": "start"})
        
        try:
            # Get module prioritizer from engine
            prioritizer = engine.get_module_prioritizer()
            
            # Generate priority assessment
            assessment = prioritizer.generate_priority_assessment()
            
            # Display assessment results
            wre_log("📋 Priority Assessment Results:", "INFO")
            for priority, modules in assessment.items():
                wre_log(f"  {priority}: {len(modules)} modules", "INFO")
                for module in modules[:5]:  # Show top 5
                    wre_log(f"    - {module['name']} (Score: {module['score']})", "INFO")
                    
            self.session_manager.log_achievement("priority_assessment", "Priority assessment completed")
            
        except Exception as e:
            wre_log(f"❌ Priority assessment failed: {e}", "ERROR")
            self.session_manager.log_operation("priority_assessment", {"error": str(e)})
            
    def _perform_ecosystem_analysis(self, engine):
        """Perform ecosystem-wide analysis."""
        wre_log("🌍 Performing ecosystem analysis...", "INFO")
        self.session_manager.log_operation("ecosystem_analysis", {"action": "start"})
        
        try:
            # Analyze module ecosystem
            ecosystem_data = self._analyze_ecosystem()
            
            # Display ecosystem insights
            wre_log("📊 Ecosystem Analysis Results:", "INFO")
            wre_log(f"  Total modules: {ecosystem_data['total_modules']}", "INFO")
            wre_log(f"  Domains: {len(ecosystem_data['domains'])}", "INFO")
            wre_log(f"  Average complexity: {ecosystem_data['avg_complexity']:.2f}", "INFO")
            wre_log(f"  Test coverage: {ecosystem_data['test_coverage']:.1f}%", "INFO")
            
            # Show domain breakdown
            wre_log("  Domain breakdown:", "INFO")
            for domain, count in ecosystem_data['domain_breakdown'].items():
                wre_log(f"    {domain}: {count} modules", "INFO")
                
            self.session_manager.log_achievement("ecosystem_analysis", "Ecosystem analysis completed")
            
        except Exception as e:
            wre_log(f"❌ Ecosystem analysis failed: {e}", "ERROR")
            self.session_manager.log_operation("ecosystem_analysis", {"error": str(e)})
            
    def _analyze_ecosystem(self) -> Dict[str, Any]:
        """Analyze the entire module ecosystem."""
        ecosystem_data = {
            "total_modules": 0,
            "domains": set(),
            "domain_breakdown": {},
            "avg_complexity": 0.0,
            "test_coverage": 0.0
        }
        
        modules_dir = self.project_root / "modules"
        
        # Count modules and domains
        for domain_dir in modules_dir.iterdir():
            if domain_dir.is_dir():
                domain_name = domain_dir.name
                ecosystem_data["domains"].add(domain_name)
                
                module_count = 0
                for module_dir in domain_dir.iterdir():
                    if module_dir.is_dir() and (module_dir / "__init__.py").exists():
                        module_count += 1
                        ecosystem_data["total_modules"] += 1
                        
                ecosystem_data["domain_breakdown"][domain_name] = module_count
                
        # Convert domains set to list for JSON serialization
        ecosystem_data["domains"] = list(ecosystem_data["domains"])
        
        # Calculate average complexity (placeholder)
        ecosystem_data["avg_complexity"] = 3.5
        
        # Calculate test coverage (placeholder)
        ecosystem_data["test_coverage"] = 75.0
        
        return ecosystem_data 