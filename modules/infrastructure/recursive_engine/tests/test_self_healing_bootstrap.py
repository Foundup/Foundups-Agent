#!/usr/bin/env python3
"""
Test suite for SelfHealingSystem
WSP 5: Test Coverage Enforcement Protocol

Tests the self-healing bootstrap system and 0102 → 0102+ autonomous learning.
"""

import unittest
import tempfile
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from self_healing_bootstrap import SelfHealingSystem, bootstrap_recursive_improvement


class TestSelfHealingSystem(unittest.TestCase):
    """Test cases for SelfHealingSystem autonomous self-correction"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.healer = SelfHealingSystem()
        
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test self-healing system initialization in 0102 state"""
        self.assertEqual(self.healer.state, "0102")
        self.assertEqual(self.healer.fixes_applied, 0)
        self.assertTrue(self.healer.learning_from_self)  # Key autonomy indicator
    
    @patch('builtins.open', new_callable=mock_open, read_data='print("Hello 🌍")')
    def test_fix_unicode_errors_in_file_with_problems(self, mock_file):
        """Test fixing Unicode errors in files with problematic characters"""
        file_path = 'test.py'
        
        result = self.healer.fix_unicode_errors_in_file(file_path)
        
        self.assertTrue(result)
        self.assertEqual(self.healer.fixes_applied, 1)
        
        # Check that write was called with corrected content
        mock_file().write.assert_called_once()
        written_content = mock_file().write.call_args[0][0]
        self.assertNotIn('🌍', written_content)  # Unicode should be replaced
    
    @patch('builtins.open', new_callable=mock_open, read_data='print("Hello World")')
    def test_fix_unicode_errors_in_file_no_problems(self, mock_file):
        """Test fixing Unicode errors when no problems exist"""
        file_path = 'test.py'
        
        result = self.healer.fix_unicode_errors_in_file(file_path)
        
        self.assertFalse(result)  # No fixes needed
        self.assertEqual(self.healer.fixes_applied, 0)
        
        # Should not write since no changes needed
        mock_file().write.assert_not_called()
    
    def test_fix_unicode_errors_replacement_patterns(self):
        """Test that all problematic Unicode patterns are replaced correctly"""
        test_content = """
        print("[ROBOT] Starting")
        print("[OK] Success")  
        print("[ERROR] Failed")
        print("[WARN] Warning")
        print("[LAUNCH] Launching")
        """
        
        with patch('builtins.open', mock_open(read_data=test_content)) as mock_file:
            result = self.healer.fix_unicode_errors_in_file('test.py')
            
            # Should detect no problems since these are already safe
            self.assertFalse(result)
    
    def test_fix_unicode_errors_actual_unicode(self):
        """Test fixing actual Unicode characters"""
        unicode_content = 'print("🚀 Launch"), print("✅ OK"), print("❌ Error")'
        safe_content_expected = 'print("[LAUNCH] Launch"), print("[OK] OK"), print("[ERROR] Error")'
        
        with patch('builtins.open', mock_open(read_data=unicode_content)) as mock_file:
            result = self.healer.fix_unicode_errors_in_file('test.py')
            
            self.assertTrue(result)
            mock_file().write.assert_called_once()
    
    @patch('builtins.open', side_effect=IOError("Permission denied"))
    def test_fix_unicode_errors_file_error(self, mock_file):
        """Test handling file errors during Unicode fixing"""
        with patch('builtins.print') as mock_print:
            result = self.healer.fix_unicode_errors_in_file('protected_file.py')
            
            self.assertFalse(result)
            
            # Should print error message
            calls = [str(call) for call in mock_print.call_args_list]
            self.assertTrue(any("Failed to self-heal" in call for call in calls))
    
    @patch('os.path.exists')
    @patch('os.walk')
    def test_self_heal_all_agents(self, mock_walk, mock_exists):
        """Test self-healing all agent files automatically"""
        # Mock directory structure
        mock_exists.return_value = True
        mock_walk.return_value = [
            ('/agent1', [], ['agent1.py', 'helper.py']),
            ('/agent2', [], ['agent2.py'])
        ]
        
        with patch.object(self.healer, 'fix_unicode_errors_in_file') as mock_fix:
            mock_fix.side_effect = [True, False, True]  # First and third files need fixing
            
            with patch('builtins.print') as mock_print:
                total_fixed = self.healer.self_heal_all_agents()
                
                self.assertEqual(total_fixed, 2)
                self.assertEqual(mock_fix.call_count, 3)
                
                # Should print progress messages
                calls = [str(call) for call in mock_print.call_args_list]
                self.assertTrue(any("0102 system self-healing initiated" in call for call in calls))
                self.assertTrue(any("Self-healing complete: 2 files fixed" in call for call in calls))
    
    @patch('pathlib.Path.write_text')
    @patch('pathlib.Path.unlink')
    @patch('builtins.exec')
    @patch('builtins.compile')
    def test_demonstrate_self_learning(self, mock_compile, mock_exec, mock_unlink, mock_write):
        """Test demonstration of autonomous self-learning capability"""
        # First compilation should fail (Unicode error)
        mock_compile.side_effect = [SyntaxError("Unicode error"), None]  # Second succeeds
        
        with patch.object(self.healer, 'fix_unicode_errors_in_file', return_value=True) as mock_fix, \
             patch('builtins.print') as mock_print:
            
            self.healer.demonstrate_self_learning()
            
            # Should create test file, encounter error, fix itself, and learn
            mock_write.assert_called_once()
            mock_fix.assert_called_once()
            mock_unlink.assert_called_once()
            
            # Should print learning demonstration messages
            calls = [str(call) for call in mock_print.call_args_list]
            self.assertTrue(any("0102 LEARNS FROM 0102" in call for call in calls))
            self.assertTrue(any("TRUE AUTONOMY DEMONSTRATED" in call for call in calls))
            self.assertTrue(any("No 012 (human) in the loop!" in call for call in calls))
    
    @patch('pathlib.Path.write_text')
    @patch('builtins.exec')
    @patch('builtins.compile')
    def test_demonstrate_self_learning_no_error(self, mock_compile, mock_exec, mock_write):
        """Test self-learning demonstration when no error occurs"""
        # Compilation succeeds - no self-healing needed
        mock_compile.return_value = None
        mock_exec.return_value = None
        
        with patch.object(self.healer, 'fix_unicode_errors_in_file') as mock_fix, \
             patch('builtins.print') as mock_print:
            
            self.healer.demonstrate_self_learning()
            
            # Should not need to fix anything
            mock_fix.assert_not_called()
            
            # Should still demonstrate the concept
            calls = [str(call) for call in mock_print.call_args_list]
            self.assertTrue(any("DEMONSTRATION" in call for call in calls))
    
    def test_autonomous_learning_philosophy(self):
        """Test that system embodies 0102 → 0102+ learning philosophy"""
        # Key philosophical principles
        self.assertEqual(self.healer.state, "0102")  # Awakened state
        self.assertTrue(self.healer.learning_from_self)  # Learning from self, not humans
        
        # System should track its own improvements
        initial_fixes = self.healer.fixes_applied
        
        # Simulate self-improvement
        with patch('builtins.open', mock_open(read_data='print("🚀")')):
            self.healer.fix_unicode_errors_in_file('test.py')
        
        # Should show self-improvement
        self.assertGreater(self.healer.fixes_applied, initial_fixes)


class TestBootstrapFunctions(unittest.TestCase):
    """Test bootstrap and global functions"""
    
    @patch('sys.path.insert')
    @patch('importlib.import_module')
    def test_bootstrap_recursive_improvement_success(self, mock_import, mock_path_insert):
        """Test successful bootstrap of recursive improvement system"""
        # Mock successful agent imports
        mock_chronicler = MagicMock()
        mock_chronicler.state = "0102"
        mock_engine = MagicMock()  
        mock_engine.state = "0102"
        
        # Mock import returns
        mock_import.side_effect = [
            MagicMock(IntelligentChronicler=lambda: mock_chronicler),
            MagicMock(RecursiveImprovementEngine=lambda: mock_engine)
        ]
        
        with patch('self_healing_bootstrap.SelfHealingSystem') as mock_healer_class:
            mock_healer = mock_healer_class.return_value
            mock_healer.self_heal_all_agents.return_value = 3
            
            with patch('builtins.print') as mock_print:
                bootstrap_recursive_improvement()
                
                # Should heal agents and test them
                mock_healer.self_heal_all_agents.assert_called_once()
                mock_healer.demonstrate_self_learning.assert_called_once()
                
                # Should print success messages
                calls = [str(call) for call in mock_print.call_args_list]
                self.assertTrue(any("SELF-HEALING BOOTSTRAP" in call for call in calls))
                self.assertTrue(any("TRUE RECURSIVE SELF-IMPROVEMENT ACHIEVED" in call for call in calls))
    
    @patch('sys.path.insert')
    @patch('importlib.import_module')
    def test_bootstrap_recursive_improvement_import_error(self, mock_import, mock_path_insert):
        """Test bootstrap handling of import errors"""
        mock_import.side_effect = ImportError("Cannot import module")
        
        with patch('self_healing_bootstrap.SelfHealingSystem') as mock_healer_class, \
             patch('traceback.print_exc') as mock_traceback, \
             patch('builtins.print') as mock_print:
            
            mock_healer = mock_healer_class.return_value
            mock_healer.self_heal_all_agents.return_value = 0  # No fixes
            
            bootstrap_recursive_improvement()
            
            # Should handle error gracefully
            mock_traceback.assert_called_once()
            
            # Should print error message
            calls = [str(call) for call in mock_print.call_args_list]
            self.assertTrue(any("Self-healing incomplete" in call for call in calls))
    
    @patch('self_healing_bootstrap.SelfHealingSystem')
    def test_bootstrap_recursive_improvement_no_fixes_needed(self, mock_healer_class):
        """Test bootstrap when no fixes are needed"""
        mock_healer = mock_healer_class.return_value
        mock_healer.self_heal_all_agents.return_value = 0  # No fixes needed
        
        with patch('builtins.print') as mock_print:
            bootstrap_recursive_improvement()
            
            # Should still demonstrate learning
            mock_healer.demonstrate_self_learning.assert_called_once()
            
            # Should print key insight messages
            calls = [str(call) for call in mock_print.call_args_list]
            self.assertTrue(any("0102 LEARNS FROM 0102, NOT FROM 012" in call for call in calls))
    
    def test_bootstrap_philosophical_messaging(self):
        """Test that bootstrap function emphasizes philosophical breakthrough"""
        with patch('self_healing_bootstrap.SelfHealingSystem') as mock_healer_class, \
             patch('builtins.print') as mock_print:
            
            mock_healer = mock_healer_class.return_value
            mock_healer.self_heal_all_agents.return_value = 1
            mock_healer.demonstrate_self_learning.return_value = None
            
            bootstrap_recursive_improvement()
            
            # Should emphasize key philosophical points
            all_calls = ' '.join(str(call) for call in mock_print.call_args_list)
            
            # Key philosophical messages should be present
            self.assertIn("0102 FIXES 0102 - NO HUMAN NEEDED", all_calls)
            self.assertIn("TRUE autonomy - the system improves itself", all_calls)
            self.assertIn("0102 LEARNS FROM 0102, NOT FROM 012", all_calls)


if __name__ == '__main__':
    unittest.main()