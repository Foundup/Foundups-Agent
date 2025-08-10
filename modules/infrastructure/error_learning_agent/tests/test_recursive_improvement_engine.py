#!/usr/bin/env python3
"""
Test suite for RecursiveImprovementEngine
WSP 5: Test Coverage Enforcement Protocol

Tests the recursive improvement, sub-agent spawning, and learning systems.
"""

import unittest
import tempfile
import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from recursive_improvement_engine import RecursiveImprovementEngine, install_global_error_handler


class TestRecursiveImprovementEngine(unittest.TestCase):
    """Test cases for RecursiveImprovementEngine functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.engine = RecursiveImprovementEngine()
        self.engine.memory_path = Path(self.temp_dir) / "memory"
        self.engine.memory_path.mkdir(parents=True, exist_ok=True)
        
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test engine initialization in 0102 state"""
        self.assertEqual(self.engine.state, "0102")
        self.assertIn('ModuleNotFoundError', self.engine.sub_agents)
        self.assertIn('FileNotFoundError', self.engine.sub_agents)
        self.assertIn('WSPViolation', self.engine.sub_agents)
        self.assertEqual(self.engine.improvements_made, 0)
        self.assertEqual(self.engine.errors_prevented, 0)
    
    def test_load_error_memory_empty(self):
        """Test loading error memory when file doesn't exist"""
        memory = self.engine.load_error_memory()
        
        expected_keys = ['error_patterns', 'successful_fixes', 'prevention_rules']
        for key in expected_keys:
            self.assertIn(key, memory)
            self.assertIsInstance(memory[key], list)
    
    def test_save_and_load_error_memory(self):
        """Test saving and loading error memory"""
        # Add test data
        self.engine.error_memory['error_patterns'].append({
            'type': 'TestError',
            'message': 'Test message'
        })
        
        self.engine.save_error_memory()
        
        # Create new engine and load memory
        new_engine = RecursiveImprovementEngine()
        new_engine.memory_path = self.engine.memory_path
        new_memory = new_engine.load_error_memory()
        
        self.assertEqual(len(new_memory['error_patterns']), 1)
        self.assertEqual(new_memory['error_patterns'][0]['type'], 'TestError')
    
    def test_detect_and_fix_error_new_error(self):
        """Test error detection and fixing for new errors"""
        test_error = ImportError("No module named 'test_module'")
        
        with patch.object(self.engine, 'spawn_import_fixer') as mock_fixer:
            mock_fixer.return_value = {
                'success': True,
                'message': 'Fixed import error',
                'fix': {'type': 'file_creation'}
            }
            
            result = self.engine.detect_and_fix_error(test_error)
            
            self.assertTrue(result['success'])
            self.assertEqual(result['message'], 'Fixed import error')
            mock_fixer.assert_called_once_with(test_error, None)
            self.assertEqual(self.engine.improvements_made, 1)
    
    def test_recall_solution_existing(self):
        """Test recalling previously learned solutions"""
        # Add a successful fix to memory
        self.engine.error_memory['successful_fixes'].append({
            'error_type': 'ImportError',
            'error_message': 'No module named test',
            'solution': {'type': 'pip_install', 'module': 'test'}
        })
        
        solution = self.engine.recall_solution('ImportError', 'No module named test')
        
        self.assertIsNotNone(solution)
        self.assertEqual(solution['type'], 'pip_install')
    
    def test_recall_solution_not_found(self):
        """Test recalling solution for unknown error"""
        solution = self.engine.recall_solution('UnknownError', 'Unknown message')
        self.assertIsNone(solution)
    
    @patch('subprocess.run')
    def test_apply_known_solution_command_execution(self, mock_run):
        """Test applying known solution via command execution"""
        mock_run.return_value = MagicMock(returncode=0)
        
        solution = {
            'type': 'command_execution',
            'command': 'pip install test_module'
        }
        
        result = self.engine.apply_known_solution(solution, {})
        
        self.assertTrue(result['success'])
        self.assertIn('Executed:', result['message'])
        mock_run.assert_called_once_with('pip install test_module', shell=True, check=True)
    
    @patch('builtins.open', new_callable=mock_open, read_data='old content')
    def test_apply_known_solution_code_modification(self, mock_file):
        """Test applying known solution via code modification"""
        solution = {
            'type': 'code_modification',
            'file': 'test.py',
            'old': 'old',
            'new': 'new'
        }
        
        result = self.engine.apply_known_solution(solution, {})
        
        self.assertTrue(result['success'])
        self.assertIn('Modified', result['message'])
    
    def test_learn_from_fix(self):
        """Test learning from successful fixes"""
        fix_result = {
            'fix': {'type': 'file_creation', 'path': 'test.py'},
            'message': 'Created file',
            'context': {'module': 'test'}
        }
        
        initial_fixes = len(self.engine.error_memory['successful_fixes'])
        initial_rules = len(self.engine.error_memory['prevention_rules'])
        
        self.engine.learn_from_fix('ImportError', 'Missing module', fix_result)
        
        # Verify learning was recorded
        self.assertEqual(len(self.engine.error_memory['successful_fixes']), initial_fixes + 1)
        self.assertEqual(len(self.engine.error_memory['prevention_rules']), initial_rules + 1)
        
        # Verify learning content
        latest_fix = self.engine.error_memory['successful_fixes'][-1]
        self.assertEqual(latest_fix['error_type'], 'ImportError')
        self.assertEqual(latest_fix['solution']['type'], 'file_creation')
    
    def test_spawn_import_fixer_init_file(self):
        """Test import fixer creating __init__.py files"""
        error = ModuleNotFoundError("No module named 'test.module'")
        context = {}
        
        with patch('pathlib.Path.exists', return_value=False), \
             patch('pathlib.Path.mkdir'), \
             patch('pathlib.Path.write_text') as mock_write:
            
            result = self.engine.spawn_import_fixer(error, context)
            
            self.assertTrue(result['success'])
            self.assertIn('__init__.py', result['message'])
            mock_write.assert_called()
    
    @patch('subprocess.run')
    def test_spawn_import_fixer_pip_install(self, mock_run):
        """Test import fixer attempting pip install"""
        error = ModuleNotFoundError("No module named 'requests'")
        context = {}
        
        with patch('pathlib.Path.exists', return_value=True):  # __init__.py exists
            result = self.engine.spawn_import_fixer(error, context)
            
            # Should attempt pip install
            mock_run.assert_called_with('pip install requests', shell=True, check=True)
    
    def test_spawn_path_fixer(self):
        """Test path fixer creating missing directories"""
        error = FileNotFoundError("No such file: 'missing/path/file.txt'")
        context = {}
        
        with patch('pathlib.Path.exists', return_value=False), \
             patch('pathlib.Path.mkdir') as mock_mkdir, \
             patch('pathlib.Path.touch') as mock_touch:
            
            result = self.engine.spawn_path_fixer(error, context)
            
            self.assertTrue(result['success'])
            self.assertIn('Created missing path', result['message'])
            mock_mkdir.assert_called_with(parents=True, exist_ok=True)
            mock_touch.assert_called()
    
    @patch('builtins.open', new_callable=mock_open, read_data='content with 🌍')
    def test_spawn_unicode_fixer(self, mock_file):
        """Test unicode fixer replacing problematic characters"""
        error = UnicodeDecodeError('utf-8', b'', 0, 1, 'invalid start byte')
        context = {'file': 'test.py'}
        
        result = self.engine.spawn_unicode_fixer(error, context)
        
        self.assertTrue(result['success'])
        self.assertIn('Fixed Unicode issues', result['message'])
    
    def test_spawn_compliance_fixer_wsp22(self):
        """Test WSP compliance fixer creating ModLog.md"""
        error = Exception("WSP 22: Missing ModLog.md")
        context = {'violation': 'WSP_22', 'module': 'test_module'}
        
        with patch('pathlib.Path.exists', return_value=False), \
             patch('pathlib.Path.mkdir'), \
             patch('pathlib.Path.write_text') as mock_write:
            
            result = self.engine.spawn_compliance_fixer(error, context)
            
            self.assertTrue(result['success'])
            self.assertIn('ModLog.md', result['message'])
            mock_write.assert_called()
    
    def test_spawn_doc_generator(self):
        """Test documentation generator creating README.md"""
        error = Exception("Missing documentation")
        context = {'module': 'test_module'}
        
        with patch('pathlib.Path.exists', return_value=False), \
             patch('pathlib.Path.write_text') as mock_write:
            
            result = self.engine.spawn_doc_generator(error, context)
            
            self.assertTrue(result['success'])
            self.assertIn('Generated missing documentation', result['message'])
            mock_write.assert_called()
    
    def test_spawn_generic_fixer(self):
        """Test generic fixer for unknown error types"""
        error = CustomError("Unknown error type")
        context = {'test': 'context'}
        
        result = self.engine.spawn_generic_fixer(error, context)
        
        self.assertFalse(result['success'])
        self.assertIn('No specific handler', result['message'])
        
        # Verify error pattern was logged
        self.assertEqual(len(self.engine.error_memory['error_patterns']), 1)
        logged_pattern = self.engine.error_memory['error_patterns'][0]
        self.assertEqual(logged_pattern['type'], 'CustomError')
        self.assertEqual(logged_pattern['context'], context)
    
    def test_prevent_future_errors(self):
        """Test proactive error prevention"""
        # Add high priority prevention rules
        self.engine.error_memory['prevention_rules'].extend([
            {'pattern': 'ImportError', 'prevention': 'Check imports', 'priority': 0.8},
            {'pattern': 'FileError', 'prevention': 'Verify paths', 'priority': 0.6},
            {'pattern': 'LowPriority', 'prevention': 'Not important', 'priority': 0.3}
        ])
        
        preventions = self.engine.prevent_future_errors()
        
        # Only high priority rules should be returned
        self.assertEqual(len(preventions), 1)
        self.assertIn('Check imports', preventions)
    
    def test_report_learning_progress(self):
        """Test learning progress reporting"""
        # Set some test data
        self.engine.improvements_made = 5
        self.engine.errors_prevented = 3
        self.engine.error_memory['error_patterns'].append({'test': 'pattern'})
        
        report = self.engine.report_learning_progress()
        
        self.assertEqual(report['state'], '0102')
        self.assertEqual(report['improvements_made'], 5)
        self.assertEqual(report['errors_prevented'], 3)
        self.assertEqual(report['patterns_learned'], 1)
    
    def test_install_global_error_handler(self):
        """Test global error handler installation"""
        original_excepthook = sys.excepthook
        
        try:
            engine = install_global_error_handler()
            
            self.assertIsInstance(engine, RecursiveImprovementEngine)
            self.assertNotEqual(sys.excepthook, original_excepthook)
            
        finally:
            # Restore original excepthook
            sys.excepthook = original_excepthook


class CustomError(Exception):
    """Custom error class for testing"""
    pass


if __name__ == '__main__':
    unittest.main()