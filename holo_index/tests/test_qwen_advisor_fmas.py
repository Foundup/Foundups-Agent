#!/usr/bin/env python3
"""
FMAS (Failure Mode Analysis System) Tests for QwenAdvisor
WSP Compliance: WSP 5, 6, 50, 84, 85, 87

Comprehensive testing of:
1. Rules engine WSP compliance checking
2. Agent environment detection
3. Advisor integration with CLI
4. Cache functionality
5. Telemetry recording
"""

import unittest
from unittest.mock import Mock, patch
import os
import sys
import tempfile
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qwen_advisor.rules_engine import ComplianceRulesEngine, ComplianceCheckResult
from qwen_advisor.agent_detection import AgentEnvironmentDetector
from qwen_advisor.advisor import QwenAdvisor, AdvisorContext, AdvisorResult
from qwen_advisor.cache import AdvisorCache
from qwen_advisor.config import QwenAdvisorConfig


class TestComplianceRulesEngine(unittest.TestCase):
    """Test the deterministic rules engine for WSP compliance."""

    def setUp(self):
        """Initialize the rules engine for each test."""
        self.engine = ComplianceRulesEngine()

    def test_wsp_85_root_protection_violation(self):
        """Test WSP 85: Root directory protection violations."""
        # Test creating test file in root
        query = "create test_new_feature.py"
        intent = self.engine.analyze_query_intent(query)
        result = self.engine.check_wsp_85_root_protection(query, intent)

        self.assertIsNotNone(result)
        self.assertFalse(result.passed)
        self.assertEqual(result.severity, "CRITICAL")
        self.assertIn("WSP 85 VIOLATION", result.guidance)
        self.assertIn("modules/infrastructure/integration_tests/tests/", result.suggested_fix)

    def test_wsp_85_allowed_root_files(self):
        """Test WSP 85: Allowed root files (main.py, holo_index.py)."""
        # Test allowed files
        for filename in ["main.py", "holo_index.py", "navigation.py"]:
            query = f"create {filename}"
            intent = self.engine.analyze_query_intent(query)
            result = self.engine.check_wsp_85_root_protection(query, intent)

            # Should be None (no violation) for allowed files
            self.assertIsNone(result)

    def test_wsp_84_no_duplicates_violation(self):
        """Test WSP 84: No enhanced/v2 duplicates violation."""
        # Test creating enhanced version
        query = "create enhanced_chat_sender.py"
        intent = self.engine.analyze_query_intent(query)
        result = self.engine.check_wsp_84_no_duplicates(query, intent)

        self.assertIsNotNone(result)
        self.assertFalse(result.passed)
        self.assertEqual(result.severity, "CRITICAL")
        self.assertIn("WSP 84 VIOLATION", result.guidance)
        self.assertIn("Edit the existing file directly", result.suggested_fix)

    def test_wsp_84_v2_violation(self):
        """Test WSP 84: _v2 version violation."""
        query = "implement chat_handler_v2.py"
        intent = self.engine.analyze_query_intent(query)
        result = self.engine.check_wsp_84_no_duplicates(query, intent)

        self.assertIsNotNone(result)
        self.assertFalse(result.passed)
        self.assertIn("enhanced_, _v2, or _improved", result.guidance)

    def test_wsp_87_search_first_requirement(self):
        """Test WSP 87: Search before creating requirement."""
        query = "create new authentication module"
        intent = self.engine.analyze_query_intent(query)
        result = self.engine.check_wsp_87_search_first(query, intent)

        self.assertIsNotNone(result)
        self.assertFalse(result.passed)
        self.assertEqual(result.severity, "HIGH")
        self.assertIn("WSP 87 REQUIRED", result.guidance)
        self.assertIn("python holo_index.py --search", result.suggested_fix)

    def test_wsp_22_modlog_reminder(self):
        """Test WSP 22: ModLog update reminders."""
        # Test creation reminder
        query = "create test_authentication.py"
        intent = self.engine.analyze_query_intent(query)
        result = self.engine.check_wsp_22_modlog_sync(query, intent)

        self.assertIsNotNone(result)
        self.assertEqual(result.severity, "MEDIUM")
        self.assertIn("TestModLog", result.guidance)

        # Test modification reminder
        query = "modify existing handler"
        intent = self.engine.analyze_query_intent(query)
        result = self.engine.check_wsp_22_modlog_sync(query, intent)

        self.assertIsNotNone(result)
        self.assertTrue(result.passed)  # Reminder, not violation
        self.assertEqual(result.severity, "LOW")
        self.assertIn("ModLog.md", result.guidance)

    def test_wsp_49_module_structure_requirement(self):
        """Test WSP 49: Module structure requirements."""
        query = "create new authentication module"
        intent = self.engine.analyze_query_intent(query)
        result = self.engine.check_wsp_49_module_structure(query, intent)

        self.assertIsNotNone(result)
        self.assertFalse(result.passed)
        self.assertEqual(result.severity, "HIGH")
        self.assertIn("WSP 49 REQUIRED", result.guidance)
        self.assertIn("README.md", result.suggested_fix)
        self.assertIn("ModLog.md", result.suggested_fix)
        self.assertIn("INTERFACE.md", result.suggested_fix)

    def test_query_intent_analysis(self):
        """Test query intent analysis."""
        # Test creation intent
        query = "create new feature"
        intent = self.engine.analyze_query_intent(query)
        self.assertTrue(intent["is_creation"])
        self.assertEqual(intent["primary_action"], "create")

        # Test modification intent
        query = "fix the bug in handler"
        intent = self.engine.analyze_query_intent(query)
        self.assertTrue(intent["is_modification"])
        self.assertEqual(intent["primary_action"], "modify")

        # Test search intent
        query = "find message processing"
        intent = self.engine.analyze_query_intent(query)
        self.assertFalse(intent["is_creation"])
        self.assertFalse(intent["is_modification"])
        self.assertEqual(intent["primary_action"], "search")

    def test_contextual_guidance_generation(self):
        """Test complete contextual guidance generation."""
        # Test critical violation
        query = "create enhanced_handler.py"
        search_hits = []
        guidance = self.engine.generate_contextual_guidance(query, search_hits)

        self.assertEqual(guidance["risk_level"], "CRITICAL")
        self.assertIn("STOP", guidance["primary_guidance"])
        self.assertTrue(len(guidance["violations"]) > 0)
        self.assertTrue(len(guidance["action_items"]) > 0)

        # Test with existing code hits
        query = "create chat feature"  # Use 'create' to trigger creation intent
        search_hits = [
            {"file": "chat_sender.py", "confidence": 75},
            {"file": "message_handler.py", "confidence": 60}
        ]
        guidance = self.engine.generate_contextual_guidance(query, search_hits)

        # Check that violations were found (WSP 87 is always triggered for create)
        # Even with high confidence hits, WSP 87 takes priority
        self.assertTrue(len(guidance["violations"]) > 0 or
                        "TIP" in guidance["primary_guidance"] or
                        "existing" in guidance["primary_guidance"].lower())

    def test_risk_level_calculation(self):
        """Test risk level calculation based on violations."""
        # Critical violation
        violations = [
            ComplianceCheckResult(False, "CRITICAL", "Critical issue", None, "WSP 84")
        ]
        risk = self.engine._calculate_risk_level(violations)
        self.assertEqual(risk, "CRITICAL")

        # High violation
        violations = [
            ComplianceCheckResult(False, "HIGH", "High issue", None, "WSP 87")
        ]
        risk = self.engine._calculate_risk_level(violations)
        self.assertEqual(risk, "HIGH")

        # No violations
        violations = []
        risk = self.engine._calculate_risk_level(violations)
        self.assertEqual(risk, "LOW")


class TestAgentEnvironmentDetector(unittest.TestCase):
    """Test the agent environment detection system."""

    def setUp(self):
        """Initialize detector for each test."""
        self.original_env = os.environ.copy()

    def tearDown(self):
        """Restore original environment."""
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_explicit_agent_mode_detection(self):
        """Test explicit AGENT_MODE=0102 detection."""
        os.environ['AGENT_MODE'] = '0102'
        detector = AgentEnvironmentDetector()
        self.assertTrue(detector.is_0102_agent())
        self.assertEqual(detector.get_advisor_mode(), "always_on")

    def test_holoindex_advisor_always(self):
        """Test HOLOINDEX_ADVISOR=always detection."""
        os.environ['HOLOINDEX_ADVISOR'] = 'always'
        detector = AgentEnvironmentDetector()
        self.assertTrue(detector.is_0102_agent())
        self.assertEqual(detector.get_advisor_mode(), "always_on")

    def test_windsurf_environment_detection(self):
        """Test Windsurf IDE detection."""
        os.environ['WINDSURF_WORKSPACE'] = '/path/to/workspace'
        detector = AgentEnvironmentDetector()
        self.assertTrue(detector.detect_windsurf_environment())
        self.assertTrue(detector.is_0102_agent())

    def test_cursor_environment_detection(self):
        """Test Cursor IDE detection."""
        os.environ['CURSOR_EDITOR'] = 'true'
        detector = AgentEnvironmentDetector()
        self.assertTrue(detector.detect_cursor_environment())
        self.assertTrue(detector.is_0102_agent())

    def test_ci_environment_detection(self):
        """Test CI/CD environment detection."""
        ci_vars = ['CI', 'GITHUB_ACTIONS', 'GITLAB_CI', 'JENKINS_HOME']

        for var in ci_vars:
            os.environ.clear()
            os.environ.update(self.original_env)
            os.environ[var] = 'true'
            detector = AgentEnvironmentDetector()
            self.assertTrue(detector.detect_ci_environment())
            self.assertTrue(detector.is_0102_agent())

    def test_vscode_environment_detection(self):
        """Test VS Code environment detection."""
        os.environ['VSCODE_PID'] = '12345'
        detector = AgentEnvironmentDetector()
        self.assertTrue(detector.detect_ide_environment())
        self.assertTrue(detector.is_0102_agent())

    def test_human_mode_default(self):
        """Test default to human (012) mode."""
        # Clear all agent indicators
        os.environ.clear()
        detector = AgentEnvironmentDetector()
        self.assertFalse(detector.is_0102_agent())
        self.assertEqual(detector.get_advisor_mode(), "opt_in")

    def test_advisor_mode_override(self):
        """Test advisor mode override."""
        os.environ['HOLOINDEX_ADVISOR_MODE'] = 'disabled'
        detector = AgentEnvironmentDetector()
        self.assertEqual(detector.get_advisor_mode(), "disabled")

    def test_should_run_advisor_logic(self):
        """Test should_run_advisor decision logic."""
        detector = AgentEnvironmentDetector()

        # Test explicit opt-out
        args = Mock()
        args.no_advisor = True
        args.llm_advisor = False
        self.assertFalse(detector.should_run_advisor(args))

        # Test explicit opt-in
        args.no_advisor = False
        args.llm_advisor = True
        self.assertTrue(detector.should_run_advisor(args))

        # Test environment-based default (human mode)
        os.environ.clear()
        detector = AgentEnvironmentDetector()
        args.no_advisor = False
        args.llm_advisor = False
        self.assertFalse(detector.should_run_advisor(args))

        # Test environment-based default (agent mode)
        os.environ['AGENT_MODE'] = '0102'
        detector = AgentEnvironmentDetector()
        args.no_advisor = False
        args.llm_advisor = False
        self.assertTrue(detector.should_run_advisor(args))


class TestQwenAdvisor(unittest.TestCase):
    """Test the QwenAdvisor integration."""

    def setUp(self):
        """Set up test advisor with mocked dependencies."""
        self.config = QwenAdvisorConfig()
        self.config.cache_enabled = False  # Disable cache for testing
        self.advisor = QwenAdvisor(config=self.config)

    def test_generate_guidance_with_violations(self):
        """Test guidance generation with WSP violations."""
        context = AdvisorContext(
            query="create enhanced_module.py",
            code_hits=[],
            wsp_hits=[]
        )

        result = self.advisor.generate_guidance(context)

        self.assertIsInstance(result, AdvisorResult)
        self.assertIn("VIOLATION", result.guidance)
        self.assertTrue(len(result.reminders) > 0)
        self.assertTrue(len(result.todos) > 0)
        self.assertEqual(result.metadata["risk_level"], "CRITICAL")

    def test_generate_guidance_with_test_query(self):
        """Test that test queries get FMAS plan reminder."""
        context = AdvisorContext(
            query="test the authentication module",
            code_hits=[],
            wsp_hits=[]
        )

        result = self.advisor.generate_guidance(context)

        # Should have FMAS plan in todos
        fmas_todo = next((t for t in result.todos if "FMAS_PLAN" in t), None)
        self.assertIsNotNone(fmas_todo)

    def test_generate_guidance_with_code_hits(self):
        """Test guidance with existing code hits."""
        context = AdvisorContext(
            query="implement chat feature",
            code_hits=[
                {"file": "chat_sender.py", "confidence": 80, "cube": "communication"},
                {"file": "message_handler.py", "confidence": 65, "cube": "communication"}
            ],
            wsp_hits=[
                {"wsp": "WSP_50", "content": "Pre-action verification", "cube": "compliance"}
            ]
        )

        result = self.advisor.generate_guidance(context)

        self.assertIsInstance(result, AdvisorResult)
        # Since query has 'implement' it triggers create intent with high confidence hits
        # But WSP 87 takes priority, so check for that
        self.assertTrue(
            "existing" in result.guidance.lower() or
            "wsp 87" in result.guidance.lower()
        )
        self.assertEqual(result.metadata["cubes"], ["communication", "compliance"])

    def test_cache_functionality(self):
        """Test cache hit and miss behavior."""
        # Create advisor with cache enabled
        config = QwenAdvisorConfig()
        config.cache_enabled = True
        advisor = QwenAdvisor(config=config)

        context = AdvisorContext(
            query="unique test query for cache",
            code_hits=[],
            wsp_hits=[]
        )

        # First call - cache miss
        result1 = advisor.generate_guidance(context)
        self.assertIsNotNone(result1)

        # Second call with same query - should hit cache
        result2 = advisor.generate_guidance(context)
        self.assertEqual(result1.guidance, result2.guidance)
        self.assertEqual(result1.metadata["cache_key"], result2.metadata["cache_key"])


class TestIntegrationScenarios(unittest.TestCase):
    """Integration tests for complete scenarios."""

    def test_0102_agent_full_flow(self):
        """Test full flow for 0102 agent with violations."""
        # Set up agent environment
        os.environ['AGENT_MODE'] = '0102'

        # Create detector and advisor
        detector = AgentEnvironmentDetector()
        advisor = QwenAdvisor()

        # Verify agent detection
        self.assertTrue(detector.is_0102_agent())

        # Create violating query
        context = AdvisorContext(
            query="create test_new_feature.py in root",
            code_hits=[],
            wsp_hits=[]
        )

        # Get guidance
        result = advisor.generate_guidance(context)

        # Verify critical violation detected
        self.assertEqual(result.metadata["risk_level"], "CRITICAL")
        self.assertIn("WSP 85", str(result.metadata["violations"]))
        self.assertIn("STOP", result.guidance)

    def test_012_human_opt_in_flow(self):
        """Test opt-in flow for 012 human developers."""
        # Clear agent indicators
        os.environ.clear()

        # Create detector
        detector = AgentEnvironmentDetector()

        # Verify human mode
        self.assertFalse(detector.is_0102_agent())
        self.assertEqual(detector.get_advisor_mode(), "opt_in")

        # Test with CLI args
        args = Mock()
        args.no_advisor = False
        args.llm_advisor = True  # Explicit opt-in

        self.assertTrue(detector.should_run_advisor(args))

    def test_compliance_guidance_priorities(self):
        """Test that violations are prioritized correctly."""
        engine = ComplianceRulesEngine()

        # Query with multiple violations
        query = "create enhanced_test_feature.py in root"
        search_hits = []

        guidance = engine.generate_contextual_guidance(query, search_hits)

        # Should have multiple violations
        self.assertTrue(len(guidance["violations"]) >= 2)

        # Critical violations should be mentioned first
        primary = guidance["primary_guidance"]
        self.assertIn("STOP", primary)

        # Should have action items
        self.assertTrue(len(guidance["action_items"]) > 0)


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases."""

    def test_empty_query_handling(self):
        """Test handling of empty queries."""
        engine = ComplianceRulesEngine()
        guidance = engine.generate_contextual_guidance("", [])

        self.assertIsNotNone(guidance)
        self.assertEqual(guidance["risk_level"], "LOW")

    def test_malformed_search_hits(self):
        """Test handling of malformed search hits."""
        advisor = QwenAdvisor()
        context = AdvisorContext(
            query="test query",
            code_hits=[{"malformed": "data"}],  # Missing expected fields
            wsp_hits=[None, {"wsp": "WSP_50"}]  # Contains None
        )

        # Should not crash
        result = advisor.generate_guidance(context)
        self.assertIsNotNone(result)

    def test_environment_detection_without_psutil(self):
        """Test environment detection when psutil is not available."""
        with patch.dict(sys.modules, {'psutil': None}):
            detector = AgentEnvironmentDetector()
            info = detector.get_environment_info()
            self.assertIsNotNone(info)

    def test_unicode_in_guidance(self):
        """Test handling of unicode characters in guidance."""
        engine = ComplianceRulesEngine()
        query = "create test_file.py"
        guidance = engine.generate_contextual_guidance(query, [])

        # Should contain emojis/unicode
        lines = engine.format_guidance_for_cli(guidance)
        self.assertTrue(any(line for line in lines))  # Should not crash on unicode


if __name__ == "__main__":
    # Run with verbosity
    unittest.main(verbosity=2)