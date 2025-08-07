#!/usr/bin/env python3
"""
Test Cube/Block Building Functionality

WSP Compliance: WSP 34 (Test Documentation), WSP 49 (Mandatory Module Structure)

Tests for MLE-STAR Engine cube/block building capabilities, independent
block creation, and "snap together like Lego" integration with FoundUps ecosystem.
"""

import unittest
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

class TestCubeBlockBuilding(unittest.TestCase):
    """Test MLE-STAR Engine cube/block building functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.mlestar_path = Path(__file__).resolve().parent.parent
        self.project_root = project_root
        
    def test_cube_block_architecture_focus(self):
        """Test that MLE-STAR focuses on cube/block architecture"""
        readme_path = self.mlestar_path / 'README.md'
        self.assertTrue(readme_path.exists(), "README.md missing")
        
        with open(readme_path, 'r') as f:
            content = f.read()
            
        # Check for cube/block architecture focus
        cube_block_keywords = [
            'independent Cubes/Blocks',
            'snap into the FoundUps ecosystem',
            'snap together like Lego',
            'Cube/Block Architecture Focus',
            'Independent Block Building'
        ]
        
        for keyword in cube_block_keywords:
            self.assertIn(keyword, content, f"Missing cube/block focus: {keyword}")
    
    def test_wsp_3_compliance(self):
        """Test WSP 3 enterprise domain organization compliance"""
        # Check that MLE-STAR follows WSP 3 structure
        required_dirs = ['src', 'tests', 'validation', 'sessions']
        
        for dir_name in required_dirs:
            dir_path = self.mlestar_path / dir_name
            self.assertTrue(dir_path.exists(), f"Required directory missing: {dir_name}")
    
    def test_independent_block_capabilities(self):
        """Test independent block creation capabilities"""
        # This would test actual block creation functionality
        # For now, validate that the concept is properly documented
        
        readme_path = self.mlestar_path / 'README.md'
        with open(readme_path, 'r') as f:
            content = f.read()
            
        independent_block_concepts = [
            'Standalone Block Creation',
            'Block Independence',
            'Ecosystem Snap-In',
            'Modular Composition'
        ]
        
        for concept in independent_block_concepts:
            self.assertIn(concept, content, f"Missing independent block concept: {concept}")
    
    def test_foundups_ecosystem_integration(self):
        """Test FoundUps ecosystem integration capabilities"""
        readme_path = self.mlestar_path / 'README.md'
        with open(readme_path, 'content') as f:
            content = f.read()
            
        ecosystem_integration = [
            'FoundUps Ecosystem Integration',
            'snap together like Lego',
            'Ecosystem Compatibility',
            'Cross-Block Coordination'
        ]
        
        for integration in ecosystem_integration:
            self.assertIn(integration, content, f"Missing ecosystem integration: {integration}")

class TestWREIntegration(unittest.TestCase):
    """Test WRE integration for cube/block building"""
    
    def test_wre_mlestar_integration(self):
        """Test WRE-MLE-STAR integration for enhanced block building"""
        integration_path = self.mlestar_path / 'src' / 'wre_mlestar_integration.py'
        self.assertTrue(integration_path.exists(), "WRE-MLE-STAR integration file missing")
        
        with open(integration_path, 'r') as f:
            content = f.read()
            
        # Check for integration capabilities
        integration_features = [
            'WREMLESTARIntegration',
            'EnhancedModuleScore',
            'MLESTARFoundUpSpec',
            'create_mlestar_enhanced_foundup'
        ]
        
        for feature in integration_features:
            self.assertIn(feature, content, f"Missing WRE integration feature: {feature}")

class TestWSPCompliance(unittest.TestCase):
    """Test WSP compliance for cube/block building"""
    
    def test_wsp_49_structure(self):
        """Test WSP 49 mandatory module structure"""
        mlestar_path = Path(__file__).resolve().parent.parent
        
        # Check for required files per WSP 49
        required_files = [
            'README.md',
            'ModLog.md',
            'INTERFACE.md',
            'ROADMAP.md',
            'requirements.txt',
            'tests/README.md',
            'tests/__init__.py'
        ]
        
        for file_path in required_files:
            full_path = mlestar_path / file_path
            self.assertTrue(full_path.exists(), f"WSP 49 required file missing: {file_path}")
    
    def test_wsp_34_test_documentation(self):
        """Test WSP 34 test documentation compliance"""
        tests_readme_path = Path(__file__).resolve().parent / 'README.md'
        self.assertTrue(tests_readme_path.exists(), "WSP 34 test documentation missing")
        
        with open(tests_readme_path, 'r') as f:
            content = f.read()
            
        # Check for required test documentation sections
        required_sections = [
            'Test Strategy',
            'How to Run',
            'Test Categories',
            'Expected Behavior',
            'Integration Requirements'
        ]
        
        for section in required_sections:
            self.assertIn(section, content, f"WSP 34 missing test section: {section}")

if __name__ == '__main__':
    unittest.main() 