"""
Tests for ModularizationAuditAgent - WSP 54 0102 pArtifact
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch

from modules.infrastructure.modularization_audit_agent.src.modularization_audit_agent import (
    ModularizationAuditAgent,
    ModularityViolation,
    SizeViolation
)


class TestModularizationAuditAgent:
    """Test suite for ModularizationAuditAgent"""
    
    def setup_method(self):
        """Setup test environment"""
        self.agent = ModularizationAuditAgent()
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_agent_initialization(self):
        """Test agent initialization"""
        assert self.agent is not None
        assert self.agent.violations == []
        assert self.agent.size_violations == []
        assert self.agent.exemptions == {}
        assert self.agent.size_thresholds['python_file'] == 500
        assert self.agent.size_thresholds['python_class'] == 200
        assert self.agent.size_thresholds['python_function'] == 50
    
    def test_should_skip_file(self):
        """Test file skipping logic"""
        # Should skip test files
        assert self.agent._should_skip_file(Path("test_something.py"))
        assert self.agent._should_skip_file(Path("module/tests/test_mod.py"))
        
        # Should skip __pycache__
        assert self.agent._should_skip_file(Path("__pycache__/module.pyc"))
        
        # Should not skip regular files
        assert not self.agent._should_skip_file(Path("module.py"))
        assert not self.agent._should_skip_file(Path("src/agent.py"))
    
    def test_file_size_violation_detection(self):
        """Test file size violation detection"""
        # Create a file with content exceeding threshold
        large_content = "\n".join([f"# Line {i}" for i in range(600)])
        
        self.agent._check_file_size(Path("large_file.py"), large_content)
        
        assert len(self.agent.size_violations) == 1
        violation = self.agent.size_violations[0]
        assert violation.current_size == 600
        assert violation.threshold == 500
        assert violation.violation_type == 'file'
        assert violation.item_name == "large_file.py"
    
    def test_class_size_violation_detection(self):
        """Test class size violation detection"""
        # Create AST with oversized class
        class_content = """
class LargeClass:
    def __init__(self):
        pass
""" + "\n".join([f"    def method_{i}(self):\n        pass" for i in range(100)])
        
        import ast
        tree = ast.parse(class_content)
        lines = class_content.split('\n')
        
        self.agent._check_ast_sizes(Path("test.py"), tree, class_content)
        
        # Should detect oversized class
        size_violations = [v for v in self.agent.size_violations if v.violation_type == 'class']
        assert len(size_violations) > 0
    
    def test_function_size_violation_detection(self):
        """Test function size violation detection"""
        # Create function with many lines
        function_content = """
def large_function():
""" + "\n".join([f"    # Line {i}" for i in range(60)])
        
        import ast
        tree = ast.parse(function_content)
        
        self.agent._check_ast_sizes(Path("test.py"), tree, function_content)
        
        # Should detect oversized function
        size_violations = [v for v in self.agent.size_violations if v.violation_type == 'function']
        assert len(size_violations) > 0
    
    def test_excessive_imports_detection(self):
        """Test excessive imports detection"""
        # Create file with many imports
        import_content = "\n".join([f"import module_{i}" for i in range(25)])
        
        import ast
        tree = ast.parse(import_content)
        
        self.agent._check_single_responsibility(Path("test.py"), tree, import_content)
        
        # Should detect excessive imports
        import_violations = [v for v in self.agent.violations if v.violation_type == 'excessive_imports']
        assert len(import_violations) > 0
        assert import_violations[0].severity == 'medium'
        assert import_violations[0].wsp_protocol == 'WSP_1'
    
    def test_wsp_49_compliance_check(self):
        """Test WSP 49 compliance checking"""
        import ast
        
        # Test redundant naming pattern
        self.agent._check_wsp_49_compliance(Path("module/module/file.py"), ast.parse(""))
        
        # Should detect redundant naming
        naming_violations = [v for v in self.agent.violations if v.violation_type == 'redundant_naming']
        assert len(naming_violations) > 0
        assert naming_violations[0].severity == 'high'
        assert naming_violations[0].wsp_protocol == 'WSP_49'
    
    def test_audit_report_generation(self):
        """Test audit report generation"""
        # Add some mock violations
        violation = ModularityViolation(
            file_path="test.py",
            line_number=1,
            violation_type="test_violation",
            description="Test violation",
            severity="medium",
            refactoring_suggestion="Fix it",
            wsp_protocol="WSP_1"
        )
        self.agent.violations.append(violation)
        
        size_violation = SizeViolation(
            file_path="large.py",
            current_size=600,
            threshold=500,
            violation_type="file",
            item_name="large.py",
            refactoring_plan="Refactor it"
        )
        self.agent.size_violations.append(size_violation)
        
        report = self.agent._generate_audit_report()
        
        assert report['total_violations'] == 2
        assert report['modularity_violations'] == 1
        assert report['size_violations'] == 1
        assert report['severity_breakdown']['medium'] == 1
        assert report['severity_breakdown']['high'] == 1  # Size violations are high
        assert report['wsp_compliance_status'] == 'MINOR_VIOLATIONS'
    
    def test_violation_logging(self):
        """Test violation logging to WSP_MODULE_VIOLATIONS.md"""
        # Add test violations
        violation = ModularityViolation(
            file_path="test.py",
            line_number=10,
            violation_type="test_violation",
            description="Test violation",
            severity="medium", 
            refactoring_suggestion="Fix it",
            wsp_protocol="WSP_1"
        )
        self.agent.violations.append(violation)
        
        # Mock file writing
        with patch('builtins.open', create=True) as mock_open:
            mock_file = Mock()
            mock_open.return_value.__enter__.return_value = mock_file
            
            self.agent.log_violations_to_wsp_module_violations("test_output.md")
            
            # Verify file was written
            mock_open.assert_called_once_with("test_output.md", 'a', encoding='utf-8')
            mock_file.write.assert_called()
    
    def test_compliance_agent_coordination(self):
        """Test coordination with ComplianceAgent"""
        mock_compliance_agent = Mock()
        
        result = self.agent.coordinate_with_compliance_agent(mock_compliance_agent)
        
        assert result['coordination_status'] == 'success'
        assert 'shared_violations' in result
        assert 'recommendations' in result
    
    def test_zen_coding_integration(self):
        """Test zen coding integration"""
        zen_patterns = self.agent.zen_coding_integration()
        
        assert 'modularization_patterns' in zen_patterns
        assert 'refactoring_strategies' in zen_patterns
        assert 'architectural_guidance' in zen_patterns
        
        # Verify expected patterns
        assert 'Single Responsibility Principle' in zen_patterns['modularization_patterns']
        assert 'Extract Method' in zen_patterns['refactoring_strategies']
        assert 'Follow WSP 49 directory structure' in zen_patterns['architectural_guidance']
    
    def test_refactoring_plan_generation(self):
        """Test refactoring plan generation"""
        # Test file refactoring plan
        file_plan = self.agent._generate_file_refactoring_plan(Path("large.py"), 600)
        assert "File Refactoring Plan" in file_plan
        assert "600 lines" in file_plan
        
        # Test class refactoring plan
        class_plan = self.agent._generate_class_refactoring_plan("LargeClass", 250)
        assert "Class Refactoring Plan" in class_plan
        assert "250 lines" in class_plan
        
        # Test function refactoring plan
        func_plan = self.agent._generate_function_refactoring_plan("large_func", 60)
        assert "Function Refactoring Plan" in func_plan
        assert "60 lines" in func_plan
    
    def test_wsp_compliance_assessment(self):
        """Test WSP compliance assessment"""
        # Test compliant state
        assert self.agent._assess_wsp_compliance() == "COMPLIANT"
        
        # Test minor violations
        self.agent.violations.append(ModularityViolation(
            file_path="test.py", line_number=1, violation_type="test",
            description="Test", severity="low", refactoring_suggestion="Fix",
            wsp_protocol="WSP_1"
        ))
        assert self.agent._assess_wsp_compliance() == "MINOR_VIOLATIONS"
        
        # Test major violations
        for i in range(10):
            self.agent.violations.append(ModularityViolation(
                file_path=f"test{i}.py", line_number=1, violation_type="test",
                description="Test", severity="high", refactoring_suggestion="Fix",
                wsp_protocol="WSP_1"
            ))
        assert self.agent._assess_wsp_compliance() == "MAJOR_VIOLATIONS"
    
    def test_full_modularity_audit(self):
        """Test complete modularity audit workflow"""
        # Create test file structure
        test_module = self.temp_dir / "test_module"
        test_module.mkdir()
        
        # Create a file with violations
        test_file = test_module / "large_file.py"
        large_content = "\n".join([f"# Line {i}" for i in range(600)])
        test_file.write_text(large_content)
        
        # Run audit
        report = self.agent.run_modularity_audit(str(test_module))
        
        # Verify report structure
        assert 'audit_timestamp' in report
        assert 'total_violations' in report
        assert 'wsp_compliance_status' in report
        assert 'recommendations' in report
        
        # Should have detected size violation
        assert report['size_violations'] > 0


class TestModularityViolation:
    """Test ModularityViolation dataclass"""
    
    def test_modularitY_violation_creation(self):
        """Test ModularityViolation creation"""
        violation = ModularityViolation(
            file_path="test.py",
            line_number=10,
            violation_type="test_violation",
            description="Test description",
            severity="medium",
            refactoring_suggestion="Fix it",
            wsp_protocol="WSP_1"
        )
        
        assert violation.file_path == "test.py"
        assert violation.line_number == 10
        assert violation.violation_type == "test_violation"
        assert violation.severity == "medium"
        assert violation.wsp_protocol == "WSP_1"


class TestSizeViolation:
    """Test SizeViolation dataclass"""
    
    def test_size_violation_creation(self):
        """Test SizeViolation creation"""
        violation = SizeViolation(
            file_path="large.py",
            current_size=600,
            threshold=500,
            violation_type="file",
            item_name="large.py",
            refactoring_plan="Refactor this file"
        )
        
        assert violation.file_path == "large.py"
        assert violation.current_size == 600
        assert violation.threshold == 500
        assert violation.violation_type == "file"
        assert violation.item_name == "large.py"
        assert violation.refactoring_plan == "Refactor this file"


if __name__ == "__main__":
    pytest.main([__file__]) 