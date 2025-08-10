#!/usr/bin/env python3
"""
Test suite for ErrorLearningAgent
WSP 5: Test Coverage Enforcement Protocol

Tests the core error learning and solution remembrance functionality.
"""

import unittest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from error_learning_agent import ErrorLearningAgent


class TestErrorLearningAgent(unittest.TestCase):
    """Test cases for ErrorLearningAgent functionality"""
    
    def setUp(self):
        """Set up test environment with temporary memory"""
        self.temp_dir = tempfile.mkdtemp()
        self.agent = ErrorLearningAgent()
        self.agent.project_root = Path(self.temp_dir)
        self.agent.learning_log = Path(self.temp_dir) / "error_learning.json"
        
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test agent initialization in 0102 quantum state"""
        self.assertEqual(self.agent.quantum_state, "0102")
        self.assertIsNotNone(self.agent.learning_log)
        self.assertIsNotNone(self.agent.project_root)
    
    def test_capture_error_basic(self):
        """Test basic error capture and learning"""
        result = self.agent.capture_error("ImportError", "No module named 'test'")
        
        self.assertIn('timestamp', result)
        self.assertEqual(result['error_type'], "ImportError")
        self.assertEqual(result['error_details'], "No module named 'test'")
        self.assertEqual(result['quantum_state'], "0102")
        self.assertIn('remembered_solution', result)
        self.assertIn('kiss_fix', result)
    
    def test_remember_solution_patterns(self):
        """Test solution remembrance from 0201 quantum state"""
        # Test known error types
        solutions = {
            "file_not_found": self.agent.remember_solution("file_not_found"),
            "wsp_violation": self.agent.remember_solution("wsp_violation"), 
            "overkill": self.agent.remember_solution("overkill"),
            "test_failure": self.agent.remember_solution("test_failure"),
            "import_error": self.agent.remember_solution("import_error")
        }
        
        for error_type, solution in solutions.items():
            self.assertIsInstance(solution, str)
            self.assertTrue(len(solution) > 0)
        
        # Test unknown error type
        unknown_solution = self.agent.remember_solution("unknown_error")
        self.assertEqual(unknown_solution, "Access 0201 for solution pattern")
    
    def test_generate_kiss_fix(self):
        """Test KISS principle fix generation"""
        solution = "Test solution"
        fix = self.agent.generate_kiss_fix("TestError", solution)
        
        self.assertEqual(fix, f"PoC Fix: {solution}")
    
    def test_log_learning_persistence(self):
        """Test learning persistence to NDJSON format"""
        # Capture multiple errors
        error1 = self.agent.capture_error("Error1", "Details1")
        error2 = self.agent.capture_error("Error2", "Details2")
        
        # Verify log file exists and contains entries
        self.assertTrue(self.agent.learning_log.exists())
        
        with open(self.agent.learning_log, 'r') as f:
            lines = f.readlines()
        
        self.assertEqual(len(lines), 2)
        
        # Verify NDJSON format
        for line in lines:
            entry = json.loads(line.strip())
            self.assertIn('timestamp', entry)
            self.assertIn('error_type', entry)
            self.assertIn('quantum_state', entry)
    
    def test_trigger_improvement_with_exception(self):
        """Test improvement triggering with actual exceptions"""
        # Create a test exception
        test_exception = ImportError("No module named 'test_module'")
        
        result = self.agent.trigger_improvement(test_exception)
        
        self.assertIn('timestamp', result)
        self.assertEqual(result['error_type'], "ImportError")
        self.assertIn("No module named 'test_module'", result['error_details'])
        self.assertIn('kiss_fix', result)
    
    @patch('builtins.print')
    def test_trigger_improvement_output(self, mock_print):
        """Test console output during improvement triggering"""
        test_exception = ValueError("Test error")
        
        self.agent.trigger_improvement(test_exception)
        
        # Verify console output
        calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any("0102" in call for call in calls))
        self.assertTrue(any("KISS" in call for call in calls))
    
    def test_multiple_error_learning(self):
        """Test learning from multiple error types"""
        error_types = [
            ("ImportError", "Missing module"),
            ("FileNotFoundError", "Missing file"),
            ("WSPViolation", "Missing ModLog"),
            ("UnicodeError", "Invalid character"),
            ("TestFailure", "Test failed")
        ]
        
        results = []
        for error_type, details in error_types:
            result = self.agent.capture_error(error_type, details)
            results.append(result)
        
        # Verify all errors learned
        self.assertEqual(len(results), 5)
        
        # Verify different solutions for different errors
        solutions = [r['remembered_solution'] for r in results]
        self.assertEqual(len(set(solutions)), 5)  # All unique solutions
    
    def test_quantum_state_consistency(self):
        """Test quantum state remains 0102 throughout operations"""
        # Initial state
        self.assertEqual(self.agent.quantum_state, "0102")
        
        # After error capture
        self.agent.capture_error("TestError", "Test details")
        self.assertEqual(self.agent.quantum_state, "0102")
        
        # After solution remembrance
        self.agent.remember_solution("test_error")
        self.assertEqual(self.agent.quantum_state, "0102")
        
        # After improvement triggering
        self.agent.trigger_improvement(Exception("Test"))
        self.assertEqual(self.agent.quantum_state, "0102")
    
    def test_learning_log_directory_creation(self):
        """Test automatic creation of learning log directory"""
        # Remove directory if exists
        if self.agent.learning_log.parent.exists():
            import shutil
            shutil.rmtree(self.agent.learning_log.parent)
        
        # Capture error should create directory
        self.agent.capture_error("TestError", "Test details")
        
        self.assertTrue(self.agent.learning_log.parent.exists())
        self.assertTrue(self.agent.learning_log.exists())


if __name__ == '__main__':
    unittest.main()