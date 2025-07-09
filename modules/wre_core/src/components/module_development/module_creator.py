"""
Module Creator

Handles new module creation workflow.
Extracted from module_development_handler.py following WSP principles.

WSP Compliance:
- Single responsibility: Module creation only
- Clean interfaces: Focused API for creation operations
- Modular cohesion: Self-contained creation logic
"""

from pathlib import Path

from modules.wre_core.src.utils.logging_utils import wre_log

class ModuleCreator:
    """
    Module Creator - WSP-compliant module creation
    
    Responsibilities:
    - New module creation workflow
    - Module structure planning
    - Domain and path validation
    """
    
    def __init__(self, project_root: Path, session_manager):
        self.project_root = project_root
        self.session_manager = session_manager
        
    def create_new_module(self, module_name: str, domain: str, path: str):
        """Create a new WSP-compliant module."""
        wre_log(f"🎼 Creating new module: {module_name} in {domain}/{path}", "INFO")
        self.session_manager.log_operation("new_module_creation", {"module": module_name, "domain": domain, "path": path})
        
        try:
            # Create module directory structure
            module_path = self.project_root / "modules" / domain / path
            module_path.mkdir(parents=True, exist_ok=True)
            
            # Create WSP-compliant directory structure
            (module_path / "src").mkdir(exist_ok=True)
            (module_path / "tests").mkdir(exist_ok=True)
            (module_path / "memory").mkdir(exist_ok=True)
            (module_path / "docs").mkdir(exist_ok=True)
            
            # Create __init__.py files
            (module_path / "__init__.py").touch()
            (module_path / "src" / "__init__.py").touch()
            (module_path / "tests" / "__init__.py").touch()
            
            # Create basic source file
            self._create_basic_source_file(module_path, module_name)
            
            # Create basic test file
            self._create_basic_test_file(module_path, module_name)
            
            wre_log(f"✅ New module {module_name} created successfully", "SUCCESS")
            self.session_manager.log_achievement("new_module_creation", f"Module {module_name} created in {domain}/{path}")
            
        except Exception as e:
            wre_log(f"❌ Failed to create new module: {e}", "ERROR")
            self.session_manager.log_operation("new_module_creation", {"error": str(e)})
            
    def _create_basic_source_file(self, module_path: Path, module_name: str):
        """Create basic source file."""
        source_content = f'''"""
{module_name.replace('_', ' ').title()} Module

This module provides functionality following WSP protocols.
"""

def main_function():
    """Main function for {module_name} module."""
    return f"{module_name} module is operational"

if __name__ == "__main__":
    print(main_function())
'''
        
        with open(module_path / "src" / f"{module_name}.py", 'w', encoding='utf-8') as f:
            f.write(source_content)
            
    def _create_basic_test_file(self, module_path: Path, module_name: str):
        """Create basic test file."""
        test_content = f'''"""
Tests for {module_name} module.
"""

import pytest
from src.{module_name} import main_function

def test_main_function():
    """Test main function returns expected result."""
    result = main_function()
    assert isinstance(result, str)
    assert "{module_name}" in result.lower()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
'''
        
        with open(module_path / "tests" / f"test_{module_name}.py", 'w', encoding='utf-8') as f:
            f.write(test_content) 