#!/usr/bin/env python3
"""
Test Extension Activation

WSP Compliance: WSP 34 (Test Documentation), WSP 49 (Mandatory Module Structure)

Tests for WRE Interface Extension activation, command registration, and
status bar integration functionality.
"""

import unittest
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

class TestExtensionActivation(unittest.TestCase):
    """Test WRE Interface Extension activation functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.extension_path = Path(__file__).resolve().parent.parent
        self.project_root = project_root
        
    def test_extension_structure(self):
        """Test that extension has required structure"""
        required_files = [
            'package.json',
            'src/extension.js',
            'tests/README.md',
            'tests/__init__.py'
        ]
        
        for file_path in required_files:
            full_path = self.extension_path / file_path
            self.assertTrue(full_path.exists(), f"Required file missing: {file_path}")
    
    def test_package_json_structure(self):
        """Test package.json has required fields"""
        package_json_path = self.extension_path / 'package.json'
        self.assertTrue(package_json_path.exists(), "package.json missing")
        
        # Basic validation - in real test would parse JSON
        with open(package_json_path, 'r') as f:
            content = f.read()
            self.assertIn('"name": "wre-interface-extension"', content)
            self.assertIn('"main": "./src/extension.js"', content)
    
    def test_extension_js_exists(self):
        """Test main extension file exists"""
        extension_js_path = self.extension_path / 'src' / 'extension.js'
        self.assertTrue(extension_js_path.exists(), "extension.js missing")
    
    def test_sub_agent_coordinator_exists(self):
        """Test sub-agent coordinator exists"""
        coordinator_path = self.extension_path / 'src' / 'sub_agent_coordinator.py'
        self.assertTrue(coordinator_path.exists(), "sub_agent_coordinator.py missing")
    
    def test_wsp_compliance(self):
        """Test WSP compliance requirements"""
        # Test README.md exists
        readme_path = self.extension_path / 'README.md'
        self.assertTrue(readme_path.exists(), "README.md missing")
        
        # Test ModLog.md exists
        modlog_path = self.extension_path / 'ModLog.md'
        self.assertTrue(modlog_path.exists(), "ModLog.md missing")
        
        # Test tests/README.md exists
        tests_readme_path = self.extension_path / 'tests' / 'README.md'
        self.assertTrue(tests_readme_path.exists(), "tests/README.md missing")

class TestCommandRegistration(unittest.TestCase):
    """Test command registration functionality"""
    
    def test_command_structure(self):
        """Test that commands are properly defined"""
        package_json_path = Path(__file__).resolve().parent.parent / 'package.json'
        
        with open(package_json_path, 'r') as f:
            content = f.read()
            
        # Check for required commands
        required_commands = [
            'wre.activate',
            'wre.createModule',
            'wre.analyzeCode',
            'wre.runTests',
            'wre.validateCompliance'
        ]
        
        for command in required_commands:
            self.assertIn(command, content, f"Command {command} not found in package.json")

class TestStatusBarIntegration(unittest.TestCase):
    """Test status bar integration"""
    
    def test_status_bar_configuration(self):
        """Test status bar configuration in package.json"""
        package_json_path = Path(__file__).resolve().parent.parent / 'package.json'
        
        with open(package_json_path, 'r') as f:
            content = f.read()
            
        # Check for status bar configuration
        self.assertIn('"statusBar"', content, "Status bar configuration missing")
        self.assertIn('"wre.status"', content, "WRE status bar item missing")

if __name__ == '__main__':
    unittest.main() 