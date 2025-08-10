#!/usr/bin/env python3
"""
Test suite for DemonstrationLearner
WSP 5: Test Coverage Enforcement Protocol

Tests the agent learning system, pattern detection, and knowledge transfer functionality.
"""

import unittest
import tempfile
import json
import hashlib
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from demonstration_learner import DemonstrationLearner, get_demonstration_learner, record_demonstration


class TestDemonstrationLearner(unittest.TestCase):
    """Test cases for DemonstrationLearner functionality"""
    
    def setUp(self):
        """Set up test environment with temporary memory"""
        self.temp_dir = tempfile.mkdtemp()
        self.learner = DemonstrationLearner()
        self.learner.memory_path = Path(self.temp_dir)
        self.learner.memory_path.mkdir(parents=True, exist_ok=True)
        
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test learner initialization in 0102 quantum state"""
        self.assertEqual(self.learner.state, "0102")
        self.assertIsNotNone(self.learner.patterns)
        self.assertIn('code_patterns', self.learner.patterns)
        self.assertIn('workflow_patterns', self.learner.patterns)
        self.assertEqual(self.learner.patterns_learned, 0)
        self.assertEqual(self.learner.patterns_applied, 0)
        self.assertEqual(self.learner.acceleration_factor, 1.0)
    
    def test_load_pattern_library_empty(self):
        """Test loading pattern library when file doesn't exist"""
        patterns = self.learner.load_pattern_library()
        
        expected_categories = [
            'code_patterns', 'workflow_patterns', 'fix_patterns',
            'documentation_patterns', 'agent_coordination_patterns'
        ]
        
        for category in expected_categories:
            self.assertIn(category, patterns)
            self.assertIsInstance(patterns[category], list)
    
    def test_save_and_load_pattern_library(self):
        """Test saving and loading pattern library persistence"""
        # Add test pattern
        test_pattern = {
            'pattern': {'type': 'test', 'description': 'Test pattern'},
            'task': 'Test task',
            'timestamp': datetime.now().isoformat(),
            'usage_count': 1
        }
        
        self.learner.patterns['code_patterns'].append(test_pattern)
        self.learner.save_pattern_library()
        
        # Create new learner and load
        new_learner = DemonstrationLearner()
        new_learner.memory_path = self.learner.memory_path
        new_patterns = new_learner.load_pattern_library()
        
        self.assertEqual(len(new_patterns['code_patterns']), 1)
        self.assertEqual(new_patterns['code_patterns'][0]['pattern']['type'], 'test')
    
    def test_start_observation(self):
        """Test starting a new observation"""
        task = "Test task demonstration"
        obs_id = self.learner.start_observation(task)
        
        self.assertIsNotNone(obs_id)
        self.assertEqual(len(obs_id), 8)  # MD5 hash truncated to 8 chars
        
        observation = self.learner.current_observation
        self.assertIsNotNone(observation)
        self.assertEqual(observation['task'], task)
        self.assertEqual(observation['id'], obs_id)
        self.assertIn('start_time', observation)
        self.assertIsInstance(observation['actions'], list)
    
    def test_record_action_basic(self):
        """Test recording basic actions during demonstration"""
        self.learner.start_observation("Test task")
        
        action_details = {
            'file': 'test.py',
            'operation': 'create'
        }
        
        self.learner.record_action('file_creation', action_details)
        
        actions = self.learner.current_observation['actions']
        self.assertEqual(len(actions), 1)
        
        action = actions[0]
        self.assertEqual(action['type'], 'file_creation')
        self.assertEqual(action['details'], action_details)
        self.assertIn('timestamp', action)
    
    def test_detect_code_pattern_error_handling(self):
        """Test detection of error handling patterns"""
        self.learner.start_observation("Add error handling")
        
        details = {
            'before': 'def function():\n    do_something()',
            'after': 'def function():\n    try:\n        do_something()\n    except Exception as e:\n        print(f"Error: {e}")'
        }
        
        self.learner.record_action('code_modification', details)
        
        patterns = self.learner.current_observation['patterns_detected']
        self.assertTrue(any(p['type'] == 'error_handling_addition' for p in patterns))
    
    def test_detect_code_pattern_imports(self):
        """Test detection of import addition patterns"""
        self.learner.start_observation("Add imports")
        
        details = {
            'before': 'def function():\n    pass',
            'after': 'import os\nimport json\n\ndef function():\n    pass'
        }
        
        self.learner.record_action('code_modification', details)
        
        patterns = self.learner.current_observation['patterns_detected']
        import_patterns = [p for p in patterns if p['type'] == 'import_addition']
        self.assertTrue(len(import_patterns) > 0)
        
        if import_patterns:
            self.assertIn('imports', import_patterns[0])
    
    def test_detect_code_pattern_functions(self):
        """Test detection of function creation patterns"""
        self.learner.start_observation("Create functions")
        
        details = {
            'before': '# Empty file',
            'after': 'def hello_world():\n    print("Hello")\n\ndef goodbye():\n    print("Bye")'
        }
        
        self.learner.record_action('code_modification', details)
        
        patterns = self.learner.current_observation['patterns_detected']
        func_patterns = [p for p in patterns if p['type'] == 'function_creation']
        self.assertTrue(len(func_patterns) > 0)
    
    def test_detect_structure_pattern_module(self):
        """Test detection of module structure patterns"""
        self.learner.start_observation("Create module structure")
        
        details = {'path': 'modules/test_domain/test_module/src/test.py'}
        self.learner.record_action('file_creation', details)
        
        patterns = self.learner.current_observation['patterns_detected']
        module_patterns = [p for p in patterns if p['type'] == 'module_structure']
        self.assertTrue(len(module_patterns) > 0)
    
    def test_detect_structure_pattern_modlog(self):
        """Test detection of ModLog creation patterns"""
        self.learner.start_observation("Create ModLog")
        
        details = {'path': 'test_module/ModLog.md'}
        self.learner.record_action('file_creation', details)
        
        patterns = self.learner.current_observation['patterns_detected']
        doc_patterns = [p for p in patterns if p['type'] == 'documentation_structure']
        self.assertTrue(len(doc_patterns) > 0)
    
    def test_detect_workflow_pattern_git(self):
        """Test detection of git workflow patterns"""
        self.learner.start_observation("Git workflow")
        
        commands = ['git add file.py', 'git commit -m "Update"', 'git push']
        
        for cmd in commands:
            self.learner.record_action('command_execution', {'command': cmd})
        
        patterns = self.learner.current_observation['patterns_detected']
        git_patterns = [p for p in patterns if p['type'] == 'git_workflow']
        self.assertTrue(len(git_patterns) > 0)
    
    def test_complete_observation_success(self):
        """Test successful observation completion and learning"""
        obs_id = self.learner.start_observation("Test complete workflow")
        
        # Record several actions
        self.learner.record_action('file_creation', {'path': 'test.py'})
        self.learner.record_action('code_modification', {
            'before': 'pass',
            'after': 'def hello(): print("Hello")'
        })
        self.learner.record_action('command_execution', {'command': 'python test.py'})
        
        result = self.learner.complete_observation()
        
        self.assertTrue(result['success'])
        self.assertEqual(result['observation_id'], obs_id)
        self.assertGreater(result['patterns_learned'], 0)
        self.assertIn('acceleration_factor', result)
        self.assertIsNone(self.learner.current_observation)
    
    def test_complete_observation_no_active(self):
        """Test completing observation when none is active"""
        result = self.learner.complete_observation()
        
        self.assertFalse(result['success'])
        self.assertIn('No active observation', result['message'])
    
    def test_extract_patterns_categorization(self):
        """Test pattern extraction and categorization"""
        self.learner.start_observation("Pattern categorization test")
        
        # Add patterns that should go to different categories
        self.learner.current_observation['patterns_detected'] = [
            {'type': 'error_handling_addition', 'description': 'Added try-catch'},
            {'type': 'git_workflow', 'description': 'Git commit'},
            {'type': 'wsp_compliance', 'description': 'Added WSP reference'},
            {'type': 'documentation_structure', 'description': 'Created ModLog'}
        ]
        
        extracted = self.learner.extract_patterns()
        
        self.assertGreater(len(extracted['code_patterns']), 0)
        self.assertGreater(len(extracted['workflow_patterns']), 0)
        self.assertGreater(len(extracted['documentation_patterns']), 0)
    
    def test_update_acceleration_factor(self):
        """Test acceleration factor calculation"""
        initial_factor = self.learner.acceleration_factor
        
        # Add patterns to increase acceleration
        for i in range(50):
            self.learner.patterns['code_patterns'].append({
                'pattern': {'type': f'test_{i}'},
                'usage_count': 0
            })
        
        self.learner.update_acceleration_factor()
        
        self.assertGreater(self.learner.acceleration_factor, initial_factor)
    
    def test_find_similar_patterns_matching(self):
        """Test finding similar patterns by keywords"""
        # Add test patterns
        test_patterns = [
            {
                'pattern': {'type': 'error_handling', 'description': 'Add error handling to function'},
                'category': 'code_patterns',
                'usage_count': 5
            },
            {
                'pattern': {'type': 'import_fix', 'description': 'Fix import errors'},
                'category': 'fix_patterns', 
                'usage_count': 3
            }
        ]
        
        self.learner.patterns['code_patterns'].append(test_patterns[0])
        self.learner.patterns['fix_patterns'].append(test_patterns[1])
        
        similar = self.learner.find_similar_patterns("add error handling")
        
        self.assertGreater(len(similar), 0)
        self.assertEqual(similar[0]['pattern']['type'], 'error_handling')
    
    def test_find_similar_patterns_no_match(self):
        """Test finding similar patterns when no matches exist"""
        similar = self.learner.find_similar_patterns("completely unique task")
        
        self.assertEqual(len(similar), 0)
    
    def test_apply_learned_pattern_error_handling(self):
        """Test applying error handling pattern"""
        pattern = {
            'pattern': {
                'type': 'error_handling_addition',
                'template': 'try:\n    {code}\nexcept Exception as e:\n    {handler}'
            },
            'usage_count': 0
        }
        
        context = {
            'code': 'do_something()',
            'handler': 'print(f"Error: {e}")'
        }
        
        result = self.learner.apply_learned_pattern(pattern, context)
        
        self.assertTrue(result['success'])
        self.assertIn('Applied error handling pattern', result['message'])
        self.assertEqual(pattern['usage_count'], 1)
    
    def test_apply_learned_pattern_module_structure(self):
        """Test applying module structure pattern"""
        pattern = {
            'pattern': {
                'type': 'module_structure',
                'pattern': 'modules/{domain}/{module}/src/'
            },
            'usage_count': 0
        }
        
        context = {'module_name': 'test_module'}
        
        result = self.learner.apply_learned_pattern(pattern, context)
        
        self.assertTrue(result['success'])
        self.assertIn('Applied module structure pattern', result['message'])
    
    def test_apply_learned_pattern_action_sequence(self):
        """Test applying action sequence workflow pattern"""
        pattern = {
            'pattern': {
                'type': 'action_sequence',
                'steps': ['file_creation', 'code_modification', 'test_execution']
            },
            'usage_count': 0
        }
        
        result = self.learner.apply_learned_pattern(pattern, {})
        
        self.assertTrue(result['success'])
        self.assertEqual(len(result['actions']), 3)
    
    def test_teach_agent(self):
        """Test teaching patterns to another agent"""
        test_patterns = [
            {
                'pattern': {'type': 'test_pattern', 'description': 'Test'},
                'usage_count': 5
            }
        ]
        
        result = self.learner.teach_agent('TestAgent', test_patterns)
        
        self.assertTrue(result)
        
        # Verify teaching file was created
        teaching_file = self.learner.memory_path / 'teachings/TestAgent_patterns.json'
        self.assertTrue(teaching_file.exists())
        
        with open(teaching_file, 'r') as f:
            teachings = json.load(f)
        
        self.assertEqual(teachings['agent'], 'TestAgent')
        self.assertEqual(len(teachings['patterns']), 1)
    
    def test_get_learning_report(self):
        """Test learning report generation"""
        # Set some test data
        self.learner.patterns_learned = 10
        self.learner.patterns_applied = 5
        self.learner.patterns['code_patterns'] = [{'test': 'pattern'}] * 3
        
        report = self.learner.get_learning_report()
        
        self.assertEqual(report['state'], '0102')
        self.assertEqual(report['patterns_learned'], 10)
        self.assertEqual(report['patterns_applied'], 5)
        self.assertEqual(report['knowledge_base']['code_patterns'], 3)
        self.assertEqual(report['total_patterns'], 3)
    
    def test_archive_observation(self):
        """Test observation archiving"""
        self.learner.start_observation("Archive test")
        self.learner.record_action('test_action', {'test': 'data'})
        
        self.learner.archive_observation()
        
        # Check archive directory was created
        archive_dir = self.learner.memory_path / 'observations'
        self.assertTrue(archive_dir.exists())
        
        # Check observation file exists
        obs_id = self.learner.current_observation['id']
        archive_file = archive_dir / f'{obs_id}.json'
        self.assertTrue(archive_file.exists())


class TestGlobalFunctions(unittest.TestCase):
    """Test global convenience functions"""
    
    def test_get_demonstration_learner_singleton(self):
        """Test global learner singleton behavior"""
        learner1 = get_demonstration_learner()
        learner2 = get_demonstration_learner()
        
        self.assertIs(learner1, learner2)  # Same instance
        self.assertIsInstance(learner1, DemonstrationLearner)
    
    @patch('demonstration_learner.get_demonstration_learner')
    def test_record_demonstration(self, mock_get_learner):
        """Test convenience function for recording demonstrations"""
        mock_learner = MagicMock()
        mock_get_learner.return_value = mock_learner
        
        record_demonstration('test_action', param1='value1', param2='value2')
        
        mock_learner.record_action.assert_called_once_with(
            'test_action', 
            {'param1': 'value1', 'param2': 'value2'}
        )


if __name__ == '__main__':
    unittest.main()