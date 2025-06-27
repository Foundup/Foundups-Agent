"""
WRE Orchestrator Tests

Tests for the complete WSP-54 agent suite orchestration, including:
- Agent health monitoring and availability checks
- WSP_48 enhancement opportunity detection and classification
- WSP_47 violation tracking integration
- System health check coordination

Follows WSP 6 test coverage requirements and WSP_48 recursive improvement protocols.
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from modules.wre_core.src.components.orchestrator import (
    check_agent_health,
    detect_wsp48_enhancement_opportunities,
    classify_enhancement_opportunity,
    run_system_health_check,
    get_version
)

class TestOrchestratorAgentHealth(unittest.TestCase):
    """Test agent health monitoring functionality."""
    
    def test_check_agent_health_all_operational(self):
        """Test agent health check when all agents are operational."""
        with patch('modules.wre_core.src.components.orchestrator.JanitorAgent'), \
             patch('modules.wre_core.src.components.orchestrator.LoremasterAgent'), \
             patch('modules.wre_core.src.components.orchestrator.ChroniclerAgent'), \
             patch('modules.wre_core.src.components.orchestrator.ComplianceAgent'), \
             patch('modules.wre_core.src.components.orchestrator.TestingAgent'), \
             patch('modules.wre_core.src.components.orchestrator.ScoringAgent'), \
             patch('modules.wre_core.src.components.orchestrator.DocumentationAgent'):
            
            agent_status = check_agent_health()
            
            # All 7 WSP-54 agents should be operational
            self.assertEqual(len(agent_status), 7)
            self.assertTrue(all(agent_status.values()))
            self.assertIn("JanitorAgent", agent_status)
            self.assertIn("TestingAgent", agent_status)
            self.assertIn("ScoringAgent", agent_status)
    
    def test_check_agent_health_partial_failure(self):
        """Test agent health check when some agents fail to initialize."""
        with patch('modules.wre_core.src.components.orchestrator.JanitorAgent'), \
             patch('modules.wre_core.src.components.orchestrator.LoremasterAgent'), \
             patch('modules.wre_core.src.components.orchestrator.ChroniclerAgent'), \
             patch('modules.wre_core.src.components.orchestrator.ComplianceAgent'), \
             patch('modules.wre_core.src.components.orchestrator.TestingAgent', side_effect=Exception("Test failure")), \
             patch('modules.wre_core.src.components.orchestrator.ScoringAgent', side_effect=Exception("Score failure")), \
             patch('modules.wre_core.src.components.orchestrator.DocumentationAgent'):
            
            agent_status = check_agent_health()
            
            # Should handle failures gracefully
            self.assertEqual(len(agent_status), 7)
            self.assertTrue(agent_status["JanitorAgent"])
            self.assertFalse(agent_status["TestingAgent"])
            self.assertFalse(agent_status["ScoringAgent"])

class TestWSP48EnhancementDetection(unittest.TestCase):
    """Test WSP_48 enhancement opportunity detection and classification."""
    
    def test_detect_wsp48_enhancements_from_agent_results(self):
        """Test detection of enhancement opportunities from agent results."""
        agent_results = {
            "TestingAgent": {
                "wsp48_enhancements": [
                    {
                        "type": "missing_tests",
                        "trigger": "Coverage below 90% threshold",
                        "module": "ai_intelligence/banter_engine",
                        "priority": "high"
                    }
                ]
            },
            "ScoringAgent": {
                "wsp48_enhancement": "documentation_enhancement",
                "enhancement_trigger": "Missing interface documentation",
                "module": "wre_core"
            }
        }
        
        opportunities = detect_wsp48_enhancement_opportunities(agent_results)
        
        self.assertEqual(len(opportunities), 2)
        self.assertEqual(opportunities[0]["type"], "missing_tests")
        self.assertEqual(opportunities[0]["source_agent"], "TestingAgent")
        self.assertEqual(opportunities[1]["type"], "documentation_enhancement")
        self.assertEqual(opportunities[1]["source_agent"], "ScoringAgent")
    
    def test_classify_enhancement_opportunity_framework_issue(self):
        """Test classification of framework-level enhancement opportunities."""
        opportunity = {
            "type": "test_infrastructure_failure",
            "trigger": "pytest execution failure",
            "module": "wre_core"
        }
        
        classification = classify_enhancement_opportunity(opportunity)
        
        self.assertEqual(classification["wsp47_classification"], "framework_issue")
        self.assertEqual(classification["action_required"], "immediate_fix")
        self.assertEqual(classification["wsp48_level"], "level_1_protocol")
        self.assertTrue(classification["recursive_improvement_candidate"])
    
    def test_classify_enhancement_opportunity_module_violation(self):
        """Test classification of module-level enhancement opportunities."""
        opportunity = {
            "type": "missing_tests",
            "trigger": "Low test coverage",
            "module": "ai_intelligence/banter_engine"
        }
        
        classification = classify_enhancement_opportunity(opportunity)
        
        self.assertEqual(classification["wsp47_classification"], "module_violation")
        self.assertEqual(classification["action_required"], "log_and_defer")
        self.assertEqual(classification["wsp48_level"], "level_1_protocol")  # Default fallback
        self.assertFalse(classification["recursive_improvement_candidate"])

class TestSystemHealthCheck(unittest.TestCase):
    """Test comprehensive system health check functionality."""
    
    @patch('modules.wre_core.src.components.orchestrator.check_agent_health')
    @patch('modules.wre_core.src.components.orchestrator.JanitorAgent')
    @patch('modules.wre_core.src.components.orchestrator.LoremasterAgent')
    @patch('modules.wre_core.src.components.orchestrator.ComplianceAgent')
    @patch('modules.wre_core.src.components.orchestrator.TestingAgent')
    @patch('modules.wre_core.src.components.orchestrator.ScoringAgent')
    def test_run_system_health_check_success(self, mock_scoring, mock_testing, 
                                           mock_compliance, mock_loremaster, 
                                           mock_janitor, mock_agent_health):
        """Test successful system health check with all agents operational."""
        # Mock agent health check
        mock_agent_health.return_value = {
            "JanitorAgent": True,
            "LoremasterAgent": True,
            "ComplianceAgent": True,
            "TestingAgent": True,
            "ScoringAgent": True,
            "DocumentationAgent": True,
            "ChroniclerAgent": True
        }
        
        # Mock agent instances and their methods
        mock_janitor_instance = Mock()
        mock_janitor_instance.clean_workspace.return_value = {"files_deleted": 5}
        mock_janitor.return_value = mock_janitor_instance
        
        mock_loremaster_instance = Mock()
        mock_loremaster_instance.run_audit.return_value = {"docs_found": 10}
        mock_loremaster.return_value = mock_loremaster_instance
        
        mock_testing_instance = Mock()
        mock_testing_instance.check_coverage.return_value = {"coverage_percentage": 95}
        mock_testing.return_value = mock_testing_instance
        
        result = run_system_health_check(project_root)
        
        # Verify agents were called
        mock_janitor_instance.clean_workspace.assert_called_once()
        mock_loremaster_instance.run_audit.assert_called_once()
        mock_testing_instance.check_coverage.assert_called_once()
    
    def test_get_version_from_file(self):
        """Test version retrieval from version.json file."""
        with patch('builtins.open', unittest.mock.mock_open(read_data='{"version": "1.0.0"}')):
            version = get_version()
            self.assertEqual(version, "1.0.0")
    
    def test_get_version_file_not_found(self):
        """Test version retrieval when version.json is missing."""
        with patch('builtins.open', side_effect=FileNotFoundError):
            version = get_version()
            self.assertEqual(version, "dev")

class TestWSP48Integration(unittest.TestCase):
    """Test WSP_48 recursive self-improvement integration."""
    
    def test_wsp48_three_level_enhancement_classification(self):
        """Test that WSP_48 correctly classifies three levels of enhancement."""
        test_cases = [
            {
                "type": "test_infrastructure_failure",
                "expected_level": "level_1_protocol"
            },
            {
                "type": "missing_test_structure", 
                "expected_level": "level_2_engine"
            },
            {
                "type": "complexity_reduction",
                "expected_level": "level_3_quantum"
            }
        ]
        
        for case in test_cases:
            opportunity = {"type": case["type"], "module": "test_module"}
            classification = classify_enhancement_opportunity(opportunity)
            self.assertEqual(classification["wsp48_level"], case["expected_level"])
    
    def test_wsp47_framework_vs_module_classification(self):
        """Test WSP_47 framework vs module violation classification."""
        framework_issues = [
            "test_infrastructure_failure",
            "scoring_infrastructure_failure", 
            "coverage_infrastructure_failure"
        ]
        
        module_violations = [
            "missing_tests",
            "test_coverage_improvement",
            "documentation_enhancement"
        ]
        
        for issue_type in framework_issues:
            opportunity = {"type": issue_type, "module": "test_module"}
            classification = classify_enhancement_opportunity(opportunity)
            self.assertEqual(classification["wsp47_classification"], "framework_issue")
            self.assertEqual(classification["action_required"], "immediate_fix")
        
        for violation_type in module_violations:
            opportunity = {"type": violation_type, "module": "test_module"}
            classification = classify_enhancement_opportunity(opportunity)
            self.assertEqual(classification["wsp47_classification"], "module_violation")
            self.assertEqual(classification["action_required"], "log_and_defer")

if __name__ == '__main__':
    unittest.main() 