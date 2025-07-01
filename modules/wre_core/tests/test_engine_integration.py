"""
WRE Engine Integration Tests

Tests for the complete WRE (Windsurf Recursive Engine) including:
- System initialization and component loading
- Module priority calculation and MPS scoring
- WSP compliance validation and testing
- Component manager functionality

Follows WSP 6 test coverage requirements and WSP_48 enhancement detection protocols.
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from modules.wre_core.src.components.engine_core import WRECore

class TestWREInitialization(unittest.TestCase):
    """Test WRE system initialization and component loading."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Use a unique project root for each test to avoid conflicts
        self.test_project_root = Path(__file__).resolve().parent.parent.parent.parent / "test_wre_temp"
        self.test_project_root.mkdir(exist_ok=True)
        self.wre = WRECore(str(self.test_project_root))
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up the test WRE instance
        if hasattr(self.wre, 'shutdown'):
            try:
                self.wre.shutdown()
            except:
                pass
        # Remove test directory
        import shutil
        if self.test_project_root.exists():
            shutil.rmtree(self.test_project_root, ignore_errors=True)
    
    def test_wre_initialization_simulation_mode(self):
        """Test WRE initializes correctly."""
        self.assertIsNotNone(self.wre.project_root)
        self.assertIsNotNone(self.wre.component_manager)
        self.assertIsNotNone(self.wre.module_prioritizer)
    
    def test_initialize_board_component(self):
        """Test board (Cursor interface) initialization via component manager."""
        with patch('modules.infrastructure.module_scaffolding_agent.src.module_scaffolding_agent.ModuleScaffoldingAgent') as mock_agent:
            mock_instance = Mock()
            mock_agent.return_value = mock_instance
            
            self.wre.component_manager.initialize_all_components()
            components = self.wre.component_manager.get_components()
            
            # Check that components were initialized
            self.assertIsNotNone(components)
            mock_agent.assert_called_once()
    
    def test_initialize_mast_component(self):
        """Test mast (LoreMaster) initialization via component manager."""
        with patch('modules.infrastructure.loremaster_agent.src.loremaster_agent.LoremasterAgent') as mock_agent:
            mock_instance = Mock()
            mock_agent.return_value = mock_instance
            
            self.wre.component_manager.initialize_all_components()
            components = self.wre.component_manager.get_components()
            
            # Check that components were initialized
            self.assertIsNotNone(components)
            mock_agent.assert_called_once()
    
    def test_session_manager_initialization(self):
        """Test session manager initialization."""
        self.assertIsNotNone(self.wre.session_manager)
        self.assertIsNone(self.wre.current_session_id)

class TestMPSCalculation(unittest.TestCase):
    """Test Module Priority Score (MPS) calculation functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Use a unique project root for each test to avoid conflicts
        self.test_project_root = Path(__file__).resolve().parent.parent.parent.parent / "test_mps_temp"
        self.test_project_root.mkdir(exist_ok=True)
        self.wre = WRECore(str(self.test_project_root))
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up the test WRE instance
        if hasattr(self.wre, 'shutdown'):
            try:
                self.wre.shutdown()
            except:
                pass
        # Remove test directory
        import shutil
        if self.test_project_root.exists():
            shutil.rmtree(self.test_project_root, ignore_errors=True)
    
    def test_calculate_module_priority_core_module(self):
        """Test MPS calculation for core modules."""
        # Provide proper score dictionary for core module
        scores = {
            'IM': 5,  # Importance - Core modules are very important
            'IP': 5,  # Impact - Core modules have high impact
            'ADV': 4, # AI Data Value - High value for AI systems
            'ADF': 4, # AI Dev Feasibility - Feasible to develop
            'DF': 5,  # Dependency Factor - Many modules depend on core
            'RF': 2,  # Risk Factor - Low risk for core modules
            'CX': 3   # Complexity - Moderate complexity (weighted negatively)
        }
        score = self.wre.module_prioritizer.mps_calculator.calculate(scores)
        
        # Core modules should get higher scores
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0)
    
    def test_calculate_module_priority_ai_module(self):
        """Test MPS calculation for AI intelligence modules."""
        # Provide proper score dictionary for AI module
        scores = {
            'IM': 4,  # Importance - AI modules are important
            'IP': 4,  # Impact - AI modules have high impact
            'ADV': 5, # AI Data Value - Very high value for AI systems
            'ADF': 3, # AI Dev Feasibility - Moderate feasibility
            'DF': 3,  # Dependency Factor - Some dependencies
            'RF': 3,  # Risk Factor - Moderate risk
            'CX': 4   # Complexity - High complexity (weighted negatively)
        }
        score = self.wre.module_prioritizer.mps_calculator.calculate(scores)
        
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0)
    
    def test_module_prioritizer_initialization(self):
        """Test module prioritizer component."""
        self.assertIsNotNone(self.wre.module_prioritizer)
        self.assertIsNotNone(self.wre.module_prioritizer.mps_calculator)

class TestComponentIntegration(unittest.TestCase):
    """Test WRE component integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Use a unique project root for each test to avoid conflicts
        self.test_project_root = Path(__file__).resolve().parent.parent.parent.parent / "test_integration_temp"
        self.test_project_root.mkdir(exist_ok=True)
        self.wre = WRECore(str(self.test_project_root))
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up the test WRE instance
        if hasattr(self.wre, 'shutdown'):
            try:
                self.wre.shutdown()
            except:
                pass
        # Remove test directory
        import shutil
        if self.test_project_root.exists():
            shutil.rmtree(self.test_project_root, ignore_errors=True)
    
    def test_wsp30_orchestrator_integration(self):
        """Test WSP30 orchestrator integration."""
        self.assertIsNotNone(self.wre.wsp30_orchestrator)
        self.assertEqual(self.wre.wsp30_orchestrator.project_root, self.wre.project_root)
    
    def test_ui_interface_integration(self):
        """Test UI interface integration."""
        self.assertIsNotNone(self.wre.ui_interface)
    
    def test_component_manager_validation(self):
        """Test component manager validation functionality."""
        # Test that validation works without initialized components
        result = self.wre.component_manager.validate_components()
        # Should handle gracefully even if components aren't initialized
        self.assertIsInstance(result, bool)

class TestWRELifecycle(unittest.TestCase):
    """Test WRE lifecycle operations."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Use a unique project root for each test to avoid conflicts
        self.test_project_root = Path(__file__).resolve().parent.parent.parent.parent / "test_lifecycle_temp"
        self.test_project_root.mkdir(exist_ok=True)
        self.wre = WRECore(str(self.test_project_root))
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up the test WRE instance
        if hasattr(self.wre, 'shutdown'):
            try:
                self.wre.shutdown()
            except:
                pass
        # Remove test directory
        import shutil
        if self.test_project_root.exists():
            shutil.rmtree(self.test_project_root, ignore_errors=True)
    
    def test_session_lifecycle(self):
        """Test session start and management."""
        # Test session manager functionality
        session_id = self.wre.session_manager.start_session("test")
        self.assertIsNotNone(session_id)
        
        # Test logging functionality
        self.wre.session_manager.log_operation("test_op", {"test": "data"})
        self.wre.session_manager.log_achievement("test_achievement", "Test achievement logged")
    
    @patch('builtins.input', return_value='0')
    @unittest.skip("Temporarily skipped due to pagination recursion issue - needs refactoring")
    def test_main_loop_exit(self, mock_input):
        """Test main loop exit functionality."""
        # Create UI interface with test mode to bypass pagination
        from modules.wre_core.src.interfaces.ui_interface import UIInterface
        test_ui = UIInterface(test_mode=True)
        
        # Replace the UI interface with test version and patch _get_user_choice
        with patch.object(self.wre, 'ui_interface', test_ui):
            with patch.object(test_ui, '_get_user_choice', return_value='0'):
                with patch.object(self.wre, 'shutdown') as mock_shutdown:
                    self.wre.running = True
                    self.wre._main_loop()
                    mock_shutdown.assert_called_once()

if __name__ == '__main__':
    unittest.main() 