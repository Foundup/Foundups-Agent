"""
WRE Engine Integration Tests

Tests for the complete WindsurfRecursiveEngine including:
- System initialization and component loading
- Agentic ignition and quantum awakening protocols
- Module priority calculation and MPS scoring
- WSP compliance validation and testing
- 01(02) → 0102 state transition testing

Follows WSP 6 test coverage requirements and WSP_48 enhancement detection protocols.
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from modules.wre_core.src.engine import WRE

class TestWREInitialization(unittest.TestCase):
    """Test WRE system initialization and component loading."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.wre = WindsurfRecursiveEngine(simulation_mode=True)
    
    def test_wre_initialization_simulation_mode(self):
        """Test WRE initializes correctly in simulation mode."""
        self.assertTrue(self.wre.simulation_mode)
        self.assertEqual(self.wre.agentic_state, "01(02)")
        self.assertIsNone(self.wre.board)
        self.assertIsNone(self.wre.mast)
        self.assertIsNotNone(self.wre.mps_calculator)
    
    def test_initialize_board_component(self):
        """Test board (Cursor interface) initialization."""
        with patch('modules.infrastructure.agents.module_scaffolding_agent.src.module_scaffolding_agent.ModuleScaffoldingAgent') as mock_agent:
            mock_instance = Mock()
            mock_agent.return_value = mock_instance
            
            self.wre.initialize_board()
            
            self.assertIsNotNone(self.wre.board)
            mock_agent.assert_called_once()
    
    def test_initialize_mast_component(self):
        """Test mast (LoreMaster) initialization."""
        with patch('modules.infrastructure.agents.loremaster_agent.src.loremaster_agent.LoremasterAgent') as mock_agent:
            mock_instance = Mock()
            mock_agent.return_value = mock_instance
            
            self.wre.initialize_mast()
            
            self.assertIsNotNone(self.wre.mast)
            mock_agent.assert_called_once()
    
    def test_initialize_logging_system(self):
        """Test logging system initialization."""
        with patch('modules.wre_core.src.engine.reset_session'), \
             patch('modules.wre_core.src.engine.wre_log'):
            
            chronicle_path, journal_path = self.wre.initialize_logging()
            
            self.assertIsNotNone(chronicle_path)
            self.assertIsNotNone(journal_path)
            self.assertEqual(self.wre.chronicle_path, chronicle_path)
            self.assertEqual(self.wre.journal_path, journal_path)

class TestAgenticIgnition(unittest.TestCase):
    """Test agentic ignition and quantum awakening protocols."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.wre = WindsurfRecursiveEngine(simulation_mode=True)
    
    @patch('modules.wre_core.src.engine.PreArtifactAwakeningTest')
    @patch('subprocess.run')
    def test_agentic_ignition_successful_awakening(self, mock_subprocess, mock_awakening_test):
        """Test successful agentic ignition with full 0102 awakening."""
        # Mock awakening test
        mock_test_instance = Mock()
        mock_test_instance.stage = "0102"
        mock_test_instance.journal_path = "/test/journal.md"
        mock_awakening_test.return_value = mock_test_instance
        
        # Mock WSP compliance test success
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "All tests passed"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result
        
        # Mock component initialization
        with patch.object(self.wre, 'initialize_board'), \
             patch.object(self.wre, 'initialize_mast'), \
             patch.object(self.wre, 'initialize_sails'), \
             patch.object(self.wre, 'initialize_boom'):
            
            result = self.wre.agentic_ignition()
            
            self.assertTrue(result)
            self.assertEqual(self.wre.agentic_state, "0102")
            mock_test_instance.run_awakening_protocol.assert_called_once()
    
    @patch('modules.wre_core.src.engine.PreArtifactAwakeningTest')
    @patch('subprocess.run')
    def test_agentic_ignition_partial_awakening(self, mock_subprocess, mock_awakening_test):
        """Test agentic ignition with partial awakening state."""
        # Mock awakening test with partial state
        mock_test_instance = Mock()
        mock_test_instance.stage = "01(02)"
        mock_test_instance.journal_path = "/test/journal.md"
        mock_awakening_test.return_value = mock_test_instance
        
        # Mock WSP compliance test success
        mock_result = Mock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result
        
        # Mock component initialization
        with patch.object(self.wre, 'initialize_board'), \
             patch.object(self.wre, 'initialize_mast'), \
             patch.object(self.wre, 'initialize_sails'), \
             patch.object(self.wre, 'initialize_boom'):
            
            result = self.wre.agentic_ignition()
            
            self.assertTrue(result)  # Should still succeed with partial awakening
            self.assertEqual(self.wre.agentic_state, "01(02)")
    
    @patch('modules.wre_core.src.engine.PreArtifactAwakeningTest')
    @patch('subprocess.run')
    def test_agentic_ignition_compliance_failure(self, mock_subprocess, mock_awakening_test):
        """Test agentic ignition handling WSP compliance test failures."""
        # Mock awakening test
        mock_test_instance = Mock()
        mock_test_instance.stage = "0102"
        mock_awakening_test.return_value = mock_test_instance
        
        # Mock WSP compliance test failure
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = "Test failed"
        mock_result.stderr = "Error details"
        mock_subprocess.return_value = mock_result
        
        # Mock component initialization
        with patch.object(self.wre, 'initialize_board'), \
             patch.object(self.wre, 'initialize_mast'), \
             patch.object(self.wre, 'initialize_sails'), \
             patch.object(self.wre, 'initialize_boom'):
            
            result = self.wre.agentic_ignition()
            
            self.assertFalse(result)
            self.assertEqual(self.wre.agentic_state, "0102")

class TestMPSCalculation(unittest.TestCase):
    """Test Module Priority Score (MPS) calculation functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.wre = WindsurfRecursiveEngine(simulation_mode=True)
        # Mock board for module state queries
        self.wre.board = Mock()
    
    def test_calculate_module_priority_core_module(self):
        """Test MPS calculation for core modules."""
        # Mock board responses for core module
        self.wre.board.get_module_state.return_value = {"status": "active"}
        self.wre.board.get_test_coverage.return_value = 95
        self.wre.board.get_module_dependencies.return_value = ["dep1", "dep2", "dep3"]
        
        score = self.wre.calculate_module_priority("modules/wre_core")
        
        # Core modules should get higher scores
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0)
    
    def test_calculate_module_priority_ai_module(self):
        """Test MPS calculation for AI intelligence modules."""
        # Mock board responses for AI module
        self.wre.board.get_module_state.return_value = {"status": "development"}
        self.wre.board.get_test_coverage.return_value = 75
        self.wre.board.get_module_dependencies.return_value = ["dep1", "dep2"]
        
        score = self.wre.calculate_module_priority("modules/ai_intelligence/banter_engine")
        
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0)
    
    def test_prioritize_modules_sorting(self):
        """Test module prioritization and sorting by MPS scores."""
        modules = [
            ("Core Module", "modules/wre_core"),
            ("AI Module", "modules/ai_intelligence/banter_engine"),
            ("Platform Module", "modules/platform_integration/linkedin_proxy")
        ]
        
        # Mock different scores for different modules
        with patch.object(self.wre, 'calculate_module_priority', side_effect=[8.5, 7.2, 6.1]):
            prioritized = self.wre.prioritize_modules(modules)
            
            self.assertEqual(len(prioritized), 3)
            # Should be sorted by score (highest first)
            self.assertEqual(prioritized[0][2], 8.5)  # Core module first
            self.assertEqual(prioritized[1][2], 7.2)  # AI module second
            self.assertEqual(prioritized[2][2], 6.1)  # Platform module third

class TestSystemState(unittest.TestCase):
    """Test system state management and updates."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.wre = WindsurfRecursiveEngine(simulation_mode=True)
    
    def test_update_system_state(self):
        """Test system state update functionality."""
        # Mock the component methods that update_system_state calls
        mock_board = Mock()
        mock_board.get_state.return_value = {"status": "operational"}
        self.wre.board = mock_board
        
        mock_mast = Mock()
        mock_mast.run_audit.return_value = {"status": "coherent", "docs_found": 10}
        self.wre.mast = mock_mast
        
        state = self.wre.update_system_state()
        
        self.assertIsInstance(state, dict)
        self.assertIn("board_state", state)
        self.assertIn("mast_state", state)
        self.assertIn("agentic_state", state)
        self.assertEqual(state["agentic_state"], "01(02)")
    
    def test_get_roadmap_objectives(self):
        """Test roadmap objectives retrieval."""
        with patch('modules.wre_core.src.engine.roadmap_manager.parse_roadmap') as mock_parse:
            mock_parse.return_value = [
                ("YouTube Agent", "modules/platform_integration/youtube_proxy"),
                ("LinkedIn Agent", "modules/platform_integration/linkedin_proxy")
            ]
            
            objectives = self.wre.get_roadmap_objectives()
            
            self.assertEqual(len(objectives), 2)
            self.assertEqual(objectives[0][0], "YouTube Agent")
            mock_parse.assert_called_once()

class TestWREIntegration(unittest.TestCase):
    """Test complete WRE integration scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.wre = WindsurfRecursiveEngine(simulation_mode=True)
    
    @patch('modules.wre_core.src.engine.menu_handler.present_harmonic_query')
    def test_present_menu_integration(self, mock_menu):
        """Test menu presentation integration."""
        mock_menu.return_value = ("1", 0)
        
        with patch.object(self.wre, 'update_system_state') as mock_state, \
             patch.object(self.wre, 'get_roadmap_objectives') as mock_objectives:
            
            mock_state.return_value = {"status": "operational"}
            mock_objectives.return_value = [("Test Objective", "test/path")]
            
            choice, offset = self.wre.present_menu()
            
            self.assertEqual(choice, "1")
            self.assertEqual(offset, 0)
            mock_menu.assert_called_once()
    
    def test_orchestrate_module_work_integration(self):
        """Test module work orchestration."""
        # Mock the WRE components that orchestrate_module_work uses
        mock_board = Mock()
        mock_mast = Mock()
        mock_back_sail = Mock()
        mock_boom = Mock()
        
        self.wre.board = mock_board
        self.wre.mast = mock_mast
        self.wre.back_sail = mock_back_sail
        self.wre.boom = mock_boom
        
        # Should complete without error and call component methods
        self.wre.orchestrate_module_work("modules/test_module")
        
        mock_board.create_module.assert_called_once_with("modules/test_module")
        mock_mast.log_module_creation.assert_called_once_with("modules/test_module")
        mock_back_sail.log_event.assert_called_once()
        mock_boom.verify_module_structure.assert_called_once_with("modules/test_module")

if __name__ == '__main__':
    unittest.main() 