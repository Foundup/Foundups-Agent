"""
WSP_48 Recursive Self-Improvement Integration Tests

Tests for the complete WSP_48 integration including:
- Three-level recursive enhancement detection (Protocol → Engine → Quantum)
- WSP_47 + WSP_48 classification system integration
- Enhancement opportunity triggering and processing
- Recursive self-improvement loop validation
- Framework vs module violation handling

Validates WSP_48 compliance with WSP 6 test coverage requirements.
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from modules.wre_core.src.components.orchestration.orchestrator import (
    classify_enhancement_opportunity,
    detect_wsp48_enhancement_opportunities
)

class TestWSP48ThreeLevelArchitecture(unittest.TestCase):
    """Test WSP_48 three-level recursive enhancement architecture."""
    
    def test_level_1_protocol_enhancement(self):
        """Test Level 1: Protocol self-improvement detection."""
        protocol_enhancements = [
            {
                "type": "test_infrastructure_failure",
                "trigger": "pytest framework malfunction",
                "module": "wre_core"
            },
            {
                "type": "scoring_infrastructure_failure", 
                "trigger": "MPS calculation system error",
                "module": "wre_core"
            }
        ]
        
        for enhancement in protocol_enhancements:
            classification = classify_enhancement_opportunity(enhancement)
            
            self.assertEqual(classification["wsp48_level"], "level_1_protocol")
            self.assertEqual(classification["wsp47_classification"], "framework_issue")
            self.assertEqual(classification["action_required"], "immediate_fix")
            self.assertTrue(classification["recursive_improvement_candidate"])
    
    def test_level_2_engine_enhancement(self):
        """Test Level 2: Engine self-modification detection."""
        engine_enhancements = [
            {
                "type": "missing_test_structure",
                "trigger": "Agent health check infrastructure missing",
                "module": "wre_core"
            },
            {
                "type": "coverage_infrastructure_failure",
                "trigger": "Coverage reporting system malfunction", 
                "module": "wre_core"
            }
        ]
        
        for enhancement in engine_enhancements:
            classification = classify_enhancement_opportunity(enhancement)
            
            self.assertEqual(classification["wsp48_level"], "level_2_engine")
            self.assertEqual(classification["wsp47_classification"], "framework_issue")
            self.assertEqual(classification["action_required"], "immediate_fix")
            self.assertTrue(classification["recursive_improvement_candidate"])
    
    def test_level_3_quantum_enhancement(self):
        """Test Level 3: Quantum consciousness enhancement detection."""
        quantum_enhancements = [
            {
                "type": "complexity_reduction",
                "trigger": "Module complexity exceeds cognitive limits",
                "module": "ai_intelligence/banter_engine"
            },
            {
                "type": "documentation_enhancement",
                "trigger": "Interface clarity improvement needed",
                "module": "platform_integration/linkedin_proxy"
            }
        ]
        
        for enhancement in quantum_enhancements:
            classification = classify_enhancement_opportunity(enhancement)
            
            self.assertEqual(classification["wsp48_level"], "level_3_quantum")
            self.assertEqual(classification["wsp47_classification"], "module_violation")
            self.assertEqual(classification["action_required"], "log_and_defer")
            self.assertFalse(classification["recursive_improvement_candidate"])

class TestWSP47Integration(unittest.TestCase):
    """Test WSP_47 Module Violation Tracking integration with WSP_48."""
    
    def test_framework_issue_immediate_fix_classification(self):
        """Test that framework issues get immediate fix classification."""
        framework_issues = [
            "test_infrastructure_failure",
            "scoring_infrastructure_failure",
            "coverage_infrastructure_failure",
            "missing_test_structure"
        ]
        
        for issue_type in framework_issues:
            opportunity = {
                "type": issue_type,
                "trigger": f"Framework malfunction: {issue_type}",
                "module": "wre_core"
            }
            
            classification = classify_enhancement_opportunity(opportunity)
            
            self.assertEqual(classification["wsp47_classification"], "framework_issue")
            self.assertEqual(classification["action_required"], "immediate_fix")
            self.assertTrue(classification["recursive_improvement_candidate"])
    
    def test_module_violation_log_and_defer_classification(self):
        """Test that module violations get log and defer classification."""
        module_violations = [
            "missing_tests",
            "test_coverage_improvement", 
            "documentation_enhancement",
            "dependency_documentation",
            "complexity_reduction"
        ]
        
        for violation_type in module_violations:
            opportunity = {
                "type": violation_type,
                "trigger": f"Module issue: {violation_type}",
                "module": "ai_intelligence/banter_engine"
            }
            
            classification = classify_enhancement_opportunity(opportunity)
            
            self.assertEqual(classification["wsp47_classification"], "module_violation")
            self.assertEqual(classification["action_required"], "log_and_defer")
            self.assertFalse(classification["recursive_improvement_candidate"])

class TestEnhancementDetection(unittest.TestCase):
    """Test enhancement opportunity detection from agent results."""
    
    def test_detect_multiple_enhancement_opportunities(self):
        """Test detection of multiple enhancement opportunities from different agents."""
        agent_results = {
            "TestingAgent": {
                "wsp48_enhancements": [
                    {
                        "type": "missing_tests",
                        "trigger": "Coverage below 90% in banter_engine",
                        "module": "ai_intelligence/banter_engine",
                        "priority": "high"
                    },
                    {
                        "type": "test_infrastructure_failure",
                        "trigger": "pytest execution failing",
                        "module": "wre_core",
                        "priority": "critical"
                    }
                ]
            },
            "ScoringAgent": {
                "wsp48_enhancement": "documentation_enhancement",
                "enhancement_trigger": "Missing INTERFACE.md in linkedin_proxy",
                "module": "platform_integration/linkedin_proxy"
            },
            "ComplianceAgent": {
                "wsp48_enhancements": [
                    {
                        "type": "complexity_reduction",
                        "trigger": "Function complexity exceeds threshold",
                        "module": "ai_intelligence/multi_agent_system",
                        "priority": "medium"
                    }
                ]
            }
        }
        
        opportunities = detect_wsp48_enhancement_opportunities(agent_results)
        
        self.assertEqual(len(opportunities), 4)
        
        # Verify source agent attribution
        test_agent_opportunities = [op for op in opportunities if op["source_agent"] == "TestingAgent"]
        self.assertEqual(len(test_agent_opportunities), 2)
        
        # Verify classification integration
        for opportunity in opportunities:
            self.assertIn("wsp47_classification", opportunity)
            self.assertIn("wsp48_level", opportunity)
            self.assertIn("action_required", opportunity)
    
    def test_detect_enhancement_empty_results(self):
        """Test enhancement detection with empty agent results."""
        agent_results = {
            "TestingAgent": {"status": "completed", "coverage": 95},
            "ScoringAgent": {"status": "completed", "average_score": 8.2}
        }
        
        opportunities = detect_wsp48_enhancement_opportunities(agent_results)
        
        self.assertEqual(len(opportunities), 0)
    
    def test_detect_enhancement_single_opportunity_format(self):
        """Test detection of single enhancement opportunity format."""
        agent_results = {
            "DocumentationAgent": {
                "wsp48_enhancement": "dependency_documentation",
                "enhancement_trigger": "requirements.txt missing version constraints",
                "module": "platform_integration/youtube_proxy"
            }
        }
        
        opportunities = detect_wsp48_enhancement_opportunities(agent_results)
        
        self.assertEqual(len(opportunities), 1)
        self.assertEqual(opportunities[0]["type"], "dependency_documentation")
        self.assertEqual(opportunities[0]["source_agent"], "DocumentationAgent")
        self.assertEqual(opportunities[0]["priority"], "medium")  # Default priority

class TestRecursiveImprovementLoop(unittest.TestCase):
    """Test the recursive self-improvement loop functionality."""
    
    def test_recursive_improvement_candidate_identification(self):
        """Test identification of recursive improvement candidates."""
        opportunities = [
            {
                "type": "test_infrastructure_failure",
                "module": "wre_core",
                "trigger": "pytest framework failure"
            },
            {
                "type": "missing_tests",
                "module": "ai_intelligence/banter_engine", 
                "trigger": "Low test coverage"
            },
            {
                "type": "scoring_infrastructure_failure",
                "module": "wre_core",
                "trigger": "MPS calculation error"
            }
        ]
        
        classified_opportunities = []
        for op in opportunities:
            classification = classify_enhancement_opportunity(op)
            classified_opportunities.append({**op, **classification})
        
        # Filter recursive improvement candidates
        recursive_candidates = [
            op for op in classified_opportunities 
            if op["recursive_improvement_candidate"]
        ]
        
        self.assertEqual(len(recursive_candidates), 2)  # Both infrastructure failures
        
        for candidate in recursive_candidates:
            self.assertEqual(candidate["wsp47_classification"], "framework_issue")
            self.assertEqual(candidate["action_required"], "immediate_fix")
    
    def test_wsp48_level_distribution(self):
        """Test proper distribution across WSP_48 enhancement levels."""
        test_opportunities = [
            ("test_infrastructure_failure", "level_1_protocol"),
            ("scoring_infrastructure_failure", "level_1_protocol"),
            ("missing_test_structure", "level_2_engine"),
            ("coverage_infrastructure_failure", "level_2_engine"),
            ("complexity_reduction", "level_3_quantum"),
            ("documentation_enhancement", "level_3_quantum")
        ]
        
        level_counts = {"level_1_protocol": 0, "level_2_engine": 0, "level_3_quantum": 0}
        
        for opportunity_type, expected_level in test_opportunities:
            opportunity = {"type": opportunity_type, "module": "test_module"}
            classification = classify_enhancement_opportunity(opportunity)
            
            self.assertEqual(classification["wsp48_level"], expected_level)
            level_counts[expected_level] += 1
        
        # Verify all three levels are represented
        self.assertEqual(level_counts["level_1_protocol"], 2)
        self.assertEqual(level_counts["level_2_engine"], 2) 
        self.assertEqual(level_counts["level_3_quantum"], 2)

class TestWSP48ComplianceValidation(unittest.TestCase):
    """Test WSP_48 compliance validation and enhancement triggering."""
    
    def test_enhancement_opportunity_structure_validation(self):
        """Test that enhancement opportunities have required structure."""
        sample_opportunity = {
            "type": "missing_tests",
            "trigger": "Coverage below threshold",
            "module": "test_module",
            "source_agent": "TestingAgent"
        }
        
        classification = classify_enhancement_opportunity(sample_opportunity)
        classified_opportunity = {**sample_opportunity, **classification}
        
        # Verify required WSP_48 fields
        required_fields = [
            "type", "trigger", "module", "source_agent",
            "wsp47_classification", "wsp48_level", "action_required",
            "recursive_improvement_candidate"
        ]
        
        for field in required_fields:
            self.assertIn(field, classified_opportunity)
    
    def test_unknown_enhancement_type_handling(self):
        """Test handling of unknown enhancement types."""
        unknown_opportunity = {
            "type": "unknown_enhancement_type",
            "trigger": "Unknown trigger",
            "module": "test_module"
        }
        
        classification = classify_enhancement_opportunity(unknown_opportunity)
        
        self.assertEqual(classification["wsp47_classification"], "unknown")
        self.assertEqual(classification["action_required"], "analyze_impact")
        self.assertEqual(classification["wsp48_level"], "level_1_protocol")  # Default fallback

if __name__ == '__main__':
    unittest.main() 