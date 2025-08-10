#!/usr/bin/env python3
"""
Test suite for AutonomousIntegration
WSP 5: Test Coverage Enforcement Protocol

Tests the master autonomous orchestrator and true recursive self-improvement functionality.
"""

import unittest
import tempfile
import json
import time
from pathlib import Path
from unittest.mock import patch, MagicMock, call
from datetime import datetime

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from autonomous_integration import AutonomousIntegration, run_autonomous_system


class TestAutonomousIntegration(unittest.TestCase):
    """Test cases for AutonomousIntegration autonomous orchestrator"""
    
    def setUp(self):
        """Set up test environment with mocked dependencies"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock the agent dependencies
        with patch('autonomous_integration.IntelligentChronicler') as mock_chronicler, \
             patch('autonomous_integration.RecursiveImprovementEngine') as mock_engine, \
             patch('autonomous_integration.get_demonstration_learner') as mock_learner, \
             patch('autonomous_integration.install_global_error_handler'):
            
            self.integration = AutonomousIntegration()
            self.mock_chronicler = mock_chronicler.return_value
            self.mock_engine = mock_engine.return_value  
            self.mock_learner = mock_learner.return_value
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
        # Stop monitoring if started
        try:
            self.integration.stop_monitoring()
        except:
            pass
    
    def test_initialization(self):
        """Test autonomous integration initialization in 0102 state"""
        self.assertEqual(self.integration.state, "0102")
        self.assertIsNotNone(self.integration.chronicler)
        self.assertIsNotNone(self.integration.improvement_engine)
        self.assertIsNotNone(self.integration.demonstration_learner)
        self.assertEqual(self.integration.events_processed, 0)
        self.assertEqual(self.integration.improvements_triggered, 0)
    
    def test_queue_event(self):
        """Test event queuing and processing trigger"""
        event = {
            'type': 'file_modified',
            'path': 'test.py',
            'timestamp': datetime.now().isoformat()
        }
        
        with patch('threading.Thread') as mock_thread:
            self.integration.queue_event(event)
            
            self.assertIn(event, self.integration.event_queue)
            mock_thread.assert_called_once()
    
    def test_is_significant_event_python_file(self):
        """Test significance detection for Python files"""
        event = {'path': 'modules/test/agent.py', 'type': 'file_modified'}
        
        self.assertTrue(self.integration.is_significant_event(event))
    
    def test_is_significant_event_modlog(self):
        """Test significance detection for ModLog files"""  
        event = {'path': 'modules/test/ModLog.md', 'type': 'file_modified'}
        
        self.assertTrue(self.integration.is_significant_event(event))
    
    def test_is_significant_event_wsp_file(self):
        """Test significance detection for WSP files"""
        event = {'path': 'WSP_framework/WSP_48.md', 'type': 'file_modified'}
        
        self.assertTrue(self.integration.is_significant_event(event))
    
    def test_is_significant_event_insignificant(self):
        """Test significance detection for insignificant files"""
        event = {'path': 'random_file.txt', 'type': 'file_modified'}
        
        # Should be False unless learning threshold is low
        with patch.object(self.integration.chronicler, 'significance_threshold', 0.8):
            self.assertFalse(self.integration.is_significant_event(event))
    
    @patch('builtins.open', create=True)
    @patch('builtins.compile')
    def test_check_for_errors_syntax_error(self, mock_compile, mock_open):
        """Test automatic syntax error detection and fixing"""
        mock_compile.side_effect = SyntaxError("invalid syntax")
        mock_open.return_value.__enter__.return_value.read.return_value = "invalid python code"
        
        self.mock_engine.detect_and_fix_error.return_value = {
            'success': True,
            'message': 'Fixed syntax error'
        }
        
        self.integration.check_for_errors('test.py')
        
        self.mock_engine.detect_and_fix_error.assert_called_once()
        self.assertEqual(self.integration.improvements_triggered, 1)
    
    @patch('builtins.open', create=True)
    def test_learn_from_modification(self, mock_open):
        """Test learning from file modifications"""
        mock_open.return_value.__enter__.return_value.read.return_value = "test content"
        
        self.integration.learn_from_modification('test.py')
        
        self.mock_learner.record_action.assert_called_once_with(
            'file_modification',
            {'file': 'test.py', 'content_preview': 'test content'}
        )
    
    def test_check_wsp_compliance_missing_modlog(self):
        """Test WSP compliance checking and auto-fixing"""
        with patch('pathlib.Path.exists', return_value=False):
            self.mock_engine.detect_and_fix_error.return_value = {
                'success': True,
                'message': 'Created ModLog.md'
            }
            
            self.integration.check_wsp_compliance('modules/test_module/src/test.py')
            
            # Should detect missing ModLog and trigger fix
            self.mock_engine.detect_and_fix_error.assert_called()
            args = self.mock_engine.detect_and_fix_error.call_args
            self.assertIn('WSP_22', args[1]['violation'])
    
    def test_trigger_documentation_update(self):
        """Test autonomous documentation triggering"""
        self.mock_chronicler.run_autonomous_cycle.return_value = 3
        
        self.integration.trigger_documentation_update()
        
        self.mock_chronicler.run_autonomous_cycle.assert_called_once()
        self.assertEqual(self.integration.documentations_created, 3)
    
    def test_run_autonomous_cycle_health_check(self):
        """Test autonomous cycle health checking"""
        # Mock time to trigger cycle
        with patch('time.time', return_value=time.time() + 100):
            self.integration.run_autonomous_cycle()
            
            # Should have called chronicler for documentation
            self.mock_chronicler.run_autonomous_cycle.assert_called()
    
    def test_check_system_health_healthy(self):
        """Test system health checking when all agents healthy"""
        self.mock_chronicler.file_states = {'file1': 'state1'}
        self.mock_engine.error_memory = {'patterns': [1, 2, 3]}
        self.mock_learner.patterns = {'code': [1, 2]}
        
        with patch('builtins.print') as mock_print:
            self.integration.check_system_health()
            
            # Should print OK status
            mock_print.assert_called_with("[OK] System health: OK")
    
    def test_check_system_health_issues(self):
        """Test system health checking when agents have issues"""
        self.mock_chronicler.file_states = {}  # Empty - indicates issue
        self.mock_engine.error_memory = {'patterns': [1, 2]}
        self.mock_learner.patterns = {'code': []}
        
        with patch('builtins.print') as mock_print:
            self.integration.check_system_health()
            
            # Should detect and report issues
            calls = [str(call) for call in mock_print.call_args_list]
            self.assertTrue(any("Health issues detected" in call for call in calls))
    
    def test_apply_learned_improvements(self):
        """Test applying learned patterns proactively"""
        # Mock prevention rules from improvement engine
        self.mock_engine.prevent_future_errors.return_value = [
            "Check imports before execution",
            "Verify file paths exist"
        ]
        
        # Mock similar patterns from learner
        self.mock_learner.find_similar_patterns.return_value = [
            {'pattern': 'test_pattern', 'similarity': 0.8}
        ]
        
        with patch('builtins.print') as mock_print:
            self.integration.apply_learned_improvements()
            
            # Should apply prevention rules and find patterns
            self.mock_engine.prevent_future_errors.assert_called_once()
            self.assertEqual(self.mock_learner.find_similar_patterns.call_count, 4)  # 4 common tasks
    
    @patch('pathlib.Path.write_text')
    @patch('pathlib.Path.mkdir')
    def test_generate_learning_report(self, mock_mkdir, mock_write):
        """Test comprehensive learning report generation"""
        # Set up mock data
        self.integration.events_processed = 100
        self.integration.improvements_triggered = 25
        self.integration.documentations_created = 15
        
        self.mock_chronicler.file_states = {'file1': 'state'}
        self.mock_chronicler.learned_patterns = {'significant_changes': [1, 2, 3]}
        self.mock_engine.report_learning_progress.return_value = {
            'improvements_made': 25, 'errors_prevented': 10
        }
        self.mock_learner.get_learning_report.return_value = {
            'total_patterns': 150, 'acceleration_factor': 2.5
        }
        
        with patch('builtins.print') as mock_print:
            self.integration.generate_learning_report()
            
            # Should create report file
            mock_mkdir.assert_called_once()
            mock_write.assert_called_once()
            
            # Should print summary
            calls = [str(call) for call in mock_print.call_args_list]
            self.assertTrue(any("LEARNING REPORT" in call for call in calls))
    
    def test_demonstrate_workflow_learning(self):
        """Test human demonstration recording and learning"""
        task = "Update ModLog when code changes"
        actions = [
            {
                'type': 'file_modification',
                'description': 'Modify Python file',
                'path': 'test.py',
                'content': 'new code'
            },
            {
                'type': 'documentation_update', 
                'description': 'Update ModLog',
                'file': 'ModLog.md'
            }
        ]
        
        self.mock_learner.start_observation.return_value = 'obs123'
        self.mock_learner.complete_observation.return_value = {
            'patterns_learned': 2,
            'acceleration_factor': 1.5
        }
        
        with patch('pathlib.Path.mkdir'), \
             patch('builtins.open', create=True) as mock_open, \
             patch('builtins.print') as mock_print:
            
            self.integration.demonstrate(task, actions)
            
            # Should record all actions
            self.assertEqual(self.mock_learner.record_action.call_count, 2)
            
            # Should complete observation and learn
            self.mock_learner.complete_observation.assert_called_once()
            
            # Should print learning results
            calls = [str(call) for call in mock_print.call_args_list]
            self.assertTrue(any("Learned 2 new patterns" in call for call in calls))
    
    def test_file_system_event_handlers(self):
        """Test file system event handlers"""
        # Test file modification
        mock_event = MagicMock()
        mock_event.is_directory = False
        mock_event.src_path = 'test.py'
        
        with patch.object(self.integration, 'queue_event') as mock_queue:
            self.integration.on_modified(mock_event)
            
            mock_queue.assert_called_once()
            event = mock_queue.call_args[0][0]
            self.assertEqual(event['type'], 'file_modified')
            self.assertEqual(event['path'], 'test.py')
        
        # Test file creation
        with patch.object(self.integration, 'queue_event') as mock_queue, \
             patch.object(self.mock_learner, 'record_action'):
            
            self.integration.on_created(mock_event)
            
            mock_queue.assert_called_once()
            event = mock_queue.call_args[0][0] 
            self.assertEqual(event['type'], 'file_created')
            
            # Should also record for learning
            self.mock_learner.record_action.assert_called_with(
                'file_creation', {'path': 'test.py'}
            )
    
    def test_process_events_queue(self):
        """Test event queue processing"""
        # Add test events
        events = [
            {'type': 'file_modified', 'path': 'test1.py', 'timestamp': '2025-01-01T12:00:00'},
            {'type': 'file_created', 'path': 'test2.py', 'timestamp': '2025-01-01T12:01:00'}
        ]
        
        for event in events:
            self.integration.event_queue.append(event)
        
        with patch.object(self.integration, 'is_significant_event', return_value=True), \
             patch.object(self.integration, 'handle_significant_event') as mock_handle:
            
            self.integration.process_events()
            
            # Should process both events
            self.assertEqual(mock_handle.call_count, 2)
            self.assertEqual(self.integration.events_processed, 2)
            self.assertEqual(len(self.integration.event_queue), 0)


class TestGlobalFunctions(unittest.TestCase):
    """Test global system functions"""
    
    @patch('autonomous_integration.AutonomousIntegration')
    @patch('time.sleep')
    def test_run_autonomous_system(self, mock_sleep, mock_integration_class):
        """Test launching the fully autonomous system"""
        mock_integration = mock_integration_class.return_value
        mock_sleep.side_effect = [None, KeyboardInterrupt()]  # Stop after one cycle
        
        with patch('builtins.print') as mock_print:
            run_autonomous_system()
            
            # Should create integration and start monitoring
            mock_integration_class.assert_called_once()
            mock_integration.start_monitoring.assert_called_once()
            
            # Should run at least one autonomous cycle
            mock_integration.run_autonomous_cycle.assert_called()
            
            # Should handle KeyboardInterrupt gracefully
            mock_integration.stop_monitoring.assert_called_once()
            mock_integration.generate_learning_report.assert_called_once()


if __name__ == '__main__':
    unittest.main()