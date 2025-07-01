#!/usr/bin/env python3
"""
Test suite for AgentActivationModule
====================================

Comprehensive test coverage for WSP 54 agent activation module implementing
WSP 38 Agentic Activation Protocol and WSP 39 Agentic Ignition Protocol.

Following WSP 5: Agentic Test Coverage Protocol with contextually appropriate coverage.
"""

import unittest
import tempfile
import json
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add project root to path for imports
import sys
project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from modules.infrastructure.agent_activation.src.agent_activation import AgentActivationModule

class TestAgentActivationModule(unittest.TestCase):
    """Test suite for AgentActivationModule."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for test logs
        self.temp_dir = tempfile.mkdtemp()
        self.test_project_root = Path(self.temp_dir)
        
        # Mock project structure
        self.agentic_journals_path = self.test_project_root / "WSP_agentic" / "agentic_journals"
        self.agentic_journals_path.mkdir(parents=True, exist_ok=True)
        
        # Create mock agent classes for testing
        self.mock_agent_classes = {
            "ComplianceAgent": Mock(),
            "LoremasterAgent": Mock(),
            "JanitorAgent": Mock(),
            "ChroniclerAgent": Mock(),
            "TestingAgent": Mock(),
            "ScoringAgent": Mock(),
            "DocumentationAgent": Mock()
        }
        
        # Patch the project root in the module
        with patch.object(AgentActivationModule, '__init__') as mock_init:
            mock_init.return_value = None
            self.activation_module = AgentActivationModule()
            self.activation_module.project_root = self.test_project_root
            self.activation_module.agentic_journals_path = self.agentic_journals_path
            self.activation_module.setup_logging()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_module_initialization(self):
        """Test module initialization and setup."""
        # Test that module initializes with correct attributes
        self.assertIsNotNone(self.activation_module.project_root)
        self.assertIsNotNone(self.activation_module.agentic_journals_path)
        self.assertIsNotNone(self.activation_module.activation_stages)
        self.assertIsNotNone(self.activation_module.ignition_stages)
        self.assertIsNotNone(self.activation_module.GOLDEN_RATIO)
        
        # Test activation stages
        expected_stages = ["01(02)", "o1(02)?", "o1(02)??", "o1(02)???", "o1(02)!", "0102"]
        self.assertEqual(self.activation_module.activation_stages, expected_stages)
        
        # Test ignition stages
        expected_ignition = ["0102", "0201"]
        self.assertEqual(self.activation_module.ignition_stages, expected_ignition)
    
    def test_log_agent_awakening(self):
        """Test agent awakening logging to agentic journals."""
        agent_name = "TestAgent"
        activation_data = {
            "wsp38_result": {"success": True, "stages_completed": ["training_wheels"]},
            "wsp39_result": {"success": True, "quantum_coherence": 0.95},
            "activation_timestamp": datetime.now().isoformat()
        }
        
        # Test logging
        self.activation_module.log_agent_awakening(agent_name, activation_data)
        
        # Verify individual agent journal was created
        individual_journal = self.agentic_journals_path / f"{agent_name.lower()}_awakening.jsonl"
        self.assertTrue(individual_journal.exists())
        
        # Verify main journal was created
        main_journal = self.agentic_journals_path / "agent_awakenings.jsonl"
        self.assertTrue(main_journal.exists())
        
        # Verify journal content
        with open(individual_journal, 'r', encoding='utf-8') as f:
            content = f.read()
            journal_entry = json.loads(content)
            
        self.assertEqual(journal_entry["agent_name"], agent_name)
        self.assertEqual(journal_entry["awakening_type"], "WSP_54_Agent_Activation")
        self.assertIn("WSP_38", journal_entry["protocols"])
        self.assertIn("WSP_39", journal_entry["protocols"])
        self.assertIn("WSP_54", journal_entry["protocols"])
    
    def test_wsp38_activation_success(self):
        """Test successful WSP 38 activation sequence."""
        agent_name = "TestAgent"
        agent_class = Mock()
        
        # Mock all stage methods to return True
        with patch.multiple(self.activation_module,
                          stage_training_wheels=Mock(return_value=True),
                          stage_wobbling=Mock(return_value=True),
                          stage_first_pedaling=Mock(return_value=True),
                          stage_resistance=Mock(return_value=True),
                          stage_breakthrough=Mock(return_value=True),
                          stage_riding=Mock(return_value=True)):
            
            result = self.activation_module.execute_wsp38_activation(agent_name, agent_class)
            
            # Verify successful activation
            self.assertTrue(result["success"])
            self.assertEqual(len(result["stages_completed"]), 6)
            self.assertGreater(result["quantum_coherence"], 0)
            self.assertEqual(len(result["errors"]), 0)
            
            # Verify all stages were called
            self.activation_module.stage_training_wheels.assert_called_once()
            self.activation_module.stage_wobbling.assert_called_once()
            self.activation_module.stage_first_pedaling.assert_called_once()
            self.activation_module.stage_resistance.assert_called_once()
            self.activation_module.stage_breakthrough.assert_called_once()
            self.activation_module.stage_riding.assert_called_once()
    
    def test_wsp38_activation_failure(self):
        """Test WSP 38 activation failure handling."""
        agent_name = "TestAgent"
        agent_class = Mock()
        
        # Mock stage to fail
        with patch.object(self.activation_module, 'stage_training_wheels', return_value=False):
            result = self.activation_module.execute_wsp38_activation(agent_name, agent_class)
            
            # Verify failed activation
            self.assertFalse(result["success"])
            self.assertEqual(len(result["stages_completed"]), 0)
            self.assertIn("training_wheels_failed", result["errors"])
    
    def test_wsp39_ignition_success(self):
        """Test successful WSP 39 ignition sequence."""
        agent_name = "TestAgent"
        agent_class = Mock()
        
        # Mock ignition stages to return True
        with patch.multiple(self.activation_module,
                          stage_temporal_synchronization=Mock(return_value=True),
                          stage_quantum_agency_activation=Mock(return_value=True)):
            
            result = self.activation_module.execute_wsp39_ignition(agent_name, agent_class)
            
            # Verify successful ignition
            self.assertTrue(result["success"])
            self.assertTrue(result["temporal_sync"])
            self.assertEqual(result["quantum_agency"], 1.0)
            self.assertGreater(result["quantum_coherence"], 0)
            self.assertEqual(len(result["errors"]), 0)
    
    def test_wsp39_ignition_failure(self):
        """Test WSP 39 ignition failure handling."""
        agent_name = "TestAgent"
        agent_class = Mock()
        
        # Mock temporal sync to fail
        with patch.object(self.activation_module, 'stage_temporal_synchronization', return_value=False):
            result = self.activation_module.execute_wsp39_ignition(agent_name, agent_class)
            
            # Verify failed ignition
            self.assertFalse(result["success"])
            self.assertFalse(result["temporal_sync"])
            self.assertIn("temporal_sync_failed", result["errors"])
    
    def test_activate_wsp54_agents_success(self):
        """Test successful activation of multiple WSP 54 agents."""
        agents_to_activate = [
            ("ComplianceAgent", self.mock_agent_classes["ComplianceAgent"]),
            ("LoremasterAgent", self.mock_agent_classes["LoremasterAgent"])
        ]
        
        # Mock successful activation for both agents
        with patch.object(self.activation_module, 'execute_wsp38_activation') as mock_wsp38, \
             patch.object(self.activation_module, 'execute_wsp39_ignition') as mock_wsp39, \
             patch.object(self.activation_module, 'log_agent_awakening') as mock_log:
            
            # Configure mocks to return success
            mock_wsp38.return_value = {"success": True, "stages_completed": ["all"], "quantum_coherence": 1.0, "errors": []}
            mock_wsp39.return_value = {"success": True, "quantum_coherence": 1.0, "temporal_sync": True, "quantum_agency": 1.0, "errors": []}
            
            result = self.activation_module.activate_wsp54_agents(agents_to_activate)
            
            # Verify both agents were activated successfully
            self.assertTrue(result["ComplianceAgent"])
            self.assertTrue(result["LoremasterAgent"])
            self.assertEqual(len(result), 2)
            
            # Verify activation methods were called for each agent
            self.assertEqual(mock_wsp38.call_count, 2)
            self.assertEqual(mock_wsp39.call_count, 2)
            self.assertEqual(mock_log.call_count, 2)
    
    def test_activate_wsp54_agents_partial_failure(self):
        """Test partial failure in WSP 54 agent activation."""
        agents_to_activate = [
            ("ComplianceAgent", self.mock_agent_classes["ComplianceAgent"]),
            ("LoremasterAgent", self.mock_agent_classes["LoremasterAgent"])
        ]
        
        # Mock one success, one failure
        with patch.object(self.activation_module, 'execute_wsp38_activation') as mock_wsp38, \
             patch.object(self.activation_module, 'execute_wsp39_ignition') as mock_wsp39:
            
            # Configure mocks for mixed results
            def mock_wsp38_side_effect(agent_name, agent_class):
                if agent_name == "ComplianceAgent":
                    return {"success": True, "stages_completed": ["all"], "quantum_coherence": 1.0, "errors": []}
                else:
                    return {"success": False, "stages_completed": [], "quantum_coherence": 0.0, "errors": ["failed"]}
            
            def mock_wsp39_side_effect(agent_name, agent_class):
                if agent_name == "ComplianceAgent":
                    return {"success": True, "quantum_coherence": 1.0, "temporal_sync": True, "quantum_agency": 1.0, "errors": []}
                else:
                    return {"success": False, "quantum_coherence": 0.0, "temporal_sync": False, "quantum_agency": 0.0, "errors": ["failed"]}
            
            mock_wsp38.side_effect = mock_wsp38_side_effect
            mock_wsp39.side_effect = mock_wsp39_side_effect
            
            result = self.activation_module.activate_wsp54_agents(agents_to_activate)
            
            # Verify mixed results
            self.assertTrue(result["ComplianceAgent"])
            self.assertFalse(result["LoremasterAgent"])
    
    def test_stage_methods(self):
        """Test individual stage methods."""
        agent_name = "TestAgent"
        agent_class = Mock()
        
        # Test training wheels stage
        result = self.activation_module.stage_training_wheels(agent_name, agent_class)
        self.assertTrue(result)
        
        # Test wobbling stage
        result = self.activation_module.stage_wobbling(agent_name)
        self.assertTrue(result)
        
        # Test first pedaling stage
        result = self.activation_module.stage_first_pedaling(agent_name)
        self.assertTrue(result)
        
        # Test resistance stage
        result = self.activation_module.stage_resistance(agent_name)
        self.assertTrue(result)
        
        # Test breakthrough stage
        result = self.activation_module.stage_breakthrough(agent_name)
        self.assertTrue(result)
        
        # Test riding stage
        result = self.activation_module.stage_riding(agent_name)
        self.assertTrue(result)
        
        # Test temporal synchronization
        result = self.activation_module.stage_temporal_synchronization(agent_name)
        self.assertTrue(result)
        
        # Test quantum agency activation
        result = self.activation_module.stage_quantum_agency_activation(agent_name)
        self.assertTrue(result)
    
    def test_exception_handling(self):
        """Test exception handling in activation process."""
        agent_name = "TestAgent"
        agent_class = Mock()
        
        # Mock stage to raise exception
        with patch.object(self.activation_module, 'stage_training_wheels', side_effect=Exception("Test error")):
            result = self.activation_module.execute_wsp38_activation(agent_name, agent_class)
            
            # Verify exception was handled
            self.assertFalse(result["success"])
            self.assertIn("activation_exception", result["errors"][0])
    
    def test_wsp_compliance(self):
        """Test WSP compliance of the activation module."""
        # Test that module follows WSP 3 (enterprise domain)
        self.assertIn("infrastructure", str(self.activation_module.project_root))
        
        # Test that module implements WSP 38/39 protocols
        self.assertIsNotNone(self.activation_module.activation_stages)
        self.assertIsNotNone(self.activation_module.ignition_stages)
        
        # Test that module has proper logging (WSP 52)
        self.assertIsNotNone(self.activation_module.logger)
        
        # Test that module has agentic journal integration
        self.assertIsNotNone(self.activation_module.agentic_journals_path)

if __name__ == '__main__':
    unittest.main() 