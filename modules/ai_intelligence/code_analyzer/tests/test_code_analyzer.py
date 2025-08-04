"""
Test suite for Code Analyzer module.

WSP Compliance:
- WSP 34 (Testing Protocol): Comprehensive test coverage for code analysis functionality
- WSP 54 (Agent Duties): Test agent coordination and analysis capabilities
- WSP 22 (ModLog): Test change tracking and analysis history
- WSP 50 (Pre-Action Verification): Test verification before code analysis
"""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the module to test
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from code_analyzer import CodeAnalyzer, CodeAnalysisResult, analyze_code, analyze_module


class TestCodeAnalyzer(unittest.TestCase):
    """Test cases for CodeAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = CodeAnalyzer()
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_analyzer_initialization(self):
        """Test CodeAnalyzer initialization."""
        self.assertIsNotNone(self.analyzer)
        self.assertIsInstance(self.analyzer.wsp_standards, dict)
        self.assertIn('modlog_present', self.analyzer.wsp_standards)
        self.assertIn('readme_present', self.analyzer.wsp_standards)
        self.assertIn('interface_documented', self.analyzer.wsp_standards)
        self.assertIn('tests_present', self.analyzer.wsp_standards)
        self.assertIn('proper_structure', self.analyzer.wsp_standards)
    
    def test_analyze_file_with_valid_python(self):
        """Test analyzing a valid Python file."""
        # Create a test Python file
        test_file = os.path.join(self.temp_dir, "test_file.py")
        with open(test_file, 'w') as f:
            f.write('''"""
Test module docstring.
"""

def test_function():
    """Test function docstring."""
    return "Hello, World!"

class TestClass:
    """Test class docstring."""
    
    def __init__(self):
        """Constructor docstring."""
        self.value = 42
''')
        
        result = self.analyzer.analyze_file(test_file)
        
        self.assertIsInstance(result, CodeAnalysisResult)
        self.assertEqual(result.file_path, test_file)
        self.assertGreater(result.quality_score, 0)
        self.assertGreater(result.compliance_score, 0)
        self.assertIsInstance(result.issues, list)
        self.assertIsInstance(result.recommendations, list)
        self.assertIsInstance(result.wsp_compliance, dict)
    
    def test_analyze_file_with_invalid_python(self):
        """Test analyzing an invalid Python file."""
        # Create an invalid Python file
        test_file = os.path.join(self.temp_dir, "invalid_file.py")
        with open(test_file, 'w') as f:
            f.write('def test_function(:  # Invalid syntax\n    pass')
        
        result = self.analyzer.analyze_file(test_file)
        
        self.assertIsInstance(result, CodeAnalysisResult)
        self.assertEqual(result.file_path, test_file)
        self.assertEqual(result.complexity_score, 0.0)
        self.assertEqual(result.quality_score, 0.0)
        self.assertEqual(result.compliance_score, 0.0)
        self.assertIn("Analysis failed", result.issues[0])
    
    def test_analyze_file_with_missing_file(self):
        """Test analyzing a non-existent file."""
        non_existent_file = os.path.join(self.temp_dir, "non_existent.py")
        
        result = self.analyzer.analyze_file(non_existent_file)
        
        self.assertIsInstance(result, CodeAnalysisResult)
        self.assertEqual(result.file_path, non_existent_file)
        self.assertEqual(result.complexity_score, 0.0)
        self.assertEqual(result.quality_score, 0.0)
        self.assertEqual(result.compliance_score, 0.0)
        self.assertIn("Analysis failed", result.issues[0])
    
    def test_analyze_directory(self):
        """Test analyzing a directory with Python files."""
        # Create test Python files
        test_files = [
            "file1.py",
            "file2.py",
            "subdir/file3.py"
        ]
        
        for file_path in test_files:
            full_path = os.path.join(self.temp_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write('def test_function():\n    return "test"')
        
        results = self.analyzer.analyze_directory(self.temp_dir)
        
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 3)  # Should find 3 Python files
        
        for result in results:
            self.assertIsInstance(result, CodeAnalysisResult)
            self.assertGreater(result.quality_score, 0)
    
    def test_calculate_complexity(self):
        """Test complexity calculation."""
        import ast
        
        # Simple code with low complexity
        simple_code = "def simple():\n    return 1"
        tree = ast.parse(simple_code)
        complexity = self.analyzer._calculate_complexity(tree)
        self.assertEqual(complexity, 1)  # Base complexity only
        
        # Code with higher complexity
        complex_code = """
def complex_function():
    if True:
        for i in range(10):
            if i % 2 == 0:
                while i > 0:
                    i -= 1
"""
        tree = ast.parse(complex_code)
        complexity = self.analyzer._calculate_complexity(tree)
        self.assertGreater(complexity, 1)  # Should have higher complexity
    
    def test_assess_quality(self):
        """Test quality assessment."""
        import ast
        
        # High quality code
        good_code = '''"""
Module docstring.
"""

def good_function():
    """Function docstring."""
    # Good comment
    return "good"
'''
        tree = ast.parse(good_code)
        quality = self.analyzer._assess_quality(good_code, tree)
        self.assertGreater(quality, 80)  # Should have high quality
        
        # Low quality code
        bad_code = "def badFunction():\n    return 'bad'"
        tree = ast.parse(bad_code)
        quality = self.analyzer._assess_quality(bad_code, tree)
        self.assertLess(quality, 80)  # Should have lower quality
    
    def test_check_wsp_compliance(self):
        """Test WSP compliance checking."""
        # Create a test file in a proper module structure
        module_dir = os.path.join(self.temp_dir, "test_module")
        src_dir = os.path.join(module_dir, "src")
        tests_dir = os.path.join(module_dir, "tests")
        
        os.makedirs(src_dir)
        os.makedirs(tests_dir)
        
        # Create required WSP files
        with open(os.path.join(module_dir, "ModLog.md"), 'w') as f:
            f.write("# ModLog")
        with open(os.path.join(module_dir, "README.md"), 'w') as f:
            f.write("# README")
        with open(os.path.join(module_dir, "INTERFACE.md"), 'w') as f:
            f.write("# INTERFACE")
        with open(os.path.join(tests_dir, "test.py"), 'w') as f:
            f.write("def test(): pass")
        
        test_file = os.path.join(src_dir, "test.py")
        with open(test_file, 'w') as f:
            f.write("def test(): pass")
        
        compliance = self.analyzer._check_wsp_compliance(test_file, "test content")
        self.assertGreater(compliance, 80)  # Should have high compliance
    
    def test_identify_issues(self):
        """Test issue identification."""
        import ast
        
        # Code with issues
        problematic_code = "def BadFunction():\n    return 'bad'"
        tree = ast.parse(problematic_code)
        issues = self.analyzer._identify_issues(problematic_code, tree)
        
        self.assertIsInstance(issues, list)
        self.assertGreater(len(issues), 0)  # Should identify issues
    
    def test_generate_recommendations(self):
        """Test recommendation generation."""
        issues = ["Missing module or function docstrings", "Naming conventions not followed"]
        compliance_score = 60
        
        recommendations = self.analyzer._generate_recommendations(issues, compliance_score)
        
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
        self.assertIn("docstrings", recommendations[0])


class TestCodeAnalysisResult(unittest.TestCase):
    """Test cases for CodeAnalysisResult dataclass."""
    
    def test_result_creation(self):
        """Test creating a CodeAnalysisResult."""
        result = CodeAnalysisResult(
            file_path="test.py",
            complexity_score=5.0,
            quality_score=85.0,
            compliance_score=90.0,
            issues=["Missing docstring"],
            recommendations=["Add docstring"],
            wsp_compliance={"modlog_present": True}
        )
        
        self.assertEqual(result.file_path, "test.py")
        self.assertEqual(result.complexity_score, 5.0)
        self.assertEqual(result.quality_score, 85.0)
        self.assertEqual(result.compliance_score, 90.0)
        self.assertEqual(result.issues, ["Missing docstring"])
        self.assertEqual(result.recommendations, ["Add docstring"])
        self.assertEqual(result.wsp_compliance, {"modlog_present": True})


class TestConvenienceFunctions(unittest.TestCase):
    """Test cases for convenience functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_analyze_code_function(self):
        """Test analyze_code convenience function."""
        # Create a test file
        test_file = os.path.join(self.temp_dir, "test.py")
        with open(test_file, 'w') as f:
            f.write('def test(): return "test"')
        
        result = analyze_code(test_file)
        
        self.assertIsInstance(result, CodeAnalysisResult)
        self.assertEqual(result.file_path, test_file)
    
    def test_analyze_module_function(self):
        """Test analyze_module convenience function."""
        # Create test files
        test_files = ["file1.py", "file2.py"]
        for file_path in test_files:
            full_path = os.path.join(self.temp_dir, file_path)
            with open(full_path, 'w') as f:
                f.write('def test(): return "test"')
        
        results = analyze_module(self.temp_dir)
        
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 2)


if __name__ == '__main__':
    unittest.main() 