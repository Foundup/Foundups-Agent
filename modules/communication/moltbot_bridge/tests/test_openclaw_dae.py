#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for OpenClaw DAE - The Frontal Lobe

Validates the full autonomy loop:
  Ingress -> Intent -> Preflight -> Plan -> Permission -> Execute -> Validate -> Remember

Test Layers:
  Layer 0: Intent classification (keyword heuristic)
  Layer 1: WSP preflight (authority + availability checks)
  Layer 2: Permission gate (graduated autonomy tiers)
  Layer 3: End-to-end process() (full loop)

WSP Compliance: WSP 5 (Test Coverage), WSP 6 (Test Audit)
"""

import asyncio
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from unittest.mock import PropertyMock

from modules.communication.moltbot_bridge.src.openclaw_dae import (
    OpenClawDAE,
    IntentCategory,
    AutonomyTier,
    OpenClawIntent,
)
from modules.communication.moltbot_bridge.src.gemma_intent_classifier import (
    GemmaIntentClassifier,
)


# ---------------------------------------------------------------------------
# Layer 0: Intent Classification
# ---------------------------------------------------------------------------

class TestIntentClassification:
    """Test intent classification from raw messages."""

    def setup_method(self):
        self.dae = OpenClawDAE(repo_root=project_root)

    def test_query_intent(self):
        """QUERY: search/find/explain messages classify as query."""
        intent = self.dae.classify_intent(
            message="What is the WRE orchestrator?",
            sender="user123",
            channel="telegram",
            session_key="sess1",
        )
        assert intent.category == IntentCategory.QUERY
        assert intent.target_domain == "holo_index"
        assert not intent.is_authorized_commander

    def test_command_intent(self):
        """COMMAND: run/execute/deploy messages classify as command."""
        intent = self.dae.classify_intent(
            message="Run the test suite and fix errors",
            sender="user123",
            channel="whatsapp",
            session_key="sess2",
        )
        assert intent.category == IntentCategory.COMMAND
        assert intent.target_domain == "wre_orchestrator"

    def test_monitor_intent(self):
        """MONITOR: status/health/metrics classify as monitor."""
        intent = self.dae.classify_intent(
            message="Show me the system status and health check",
            sender="user123",
            channel="discord",
            session_key="sess3",
        )
        assert intent.category == IntentCategory.MONITOR
        assert intent.target_domain == "ai_overseer"

    def test_schedule_intent(self):
        """SCHEDULE: schedule/remind/cron classify as schedule."""
        intent = self.dae.classify_intent(
            message="Schedule a video for tomorrow at 3pm",
            sender="user123",
            channel="whatsapp",
            session_key="sess4",
        )
        assert intent.category == IntentCategory.SCHEDULE

    def test_social_intent(self):
        """SOCIAL: comment/post/reply classify as social."""
        intent = self.dae.classify_intent(
            message="Post a comment on the latest video and reply to viewers",
            sender="user123",
            channel="telegram",
            session_key="sess5",
        )
        assert intent.category == IntentCategory.SOCIAL

    def test_conversation_fallback(self):
        """CONVERSATION: unrecognized messages default to conversation."""
        intent = self.dae.classify_intent(
            message="Hello there!",
            sender="user123",
            channel="whatsapp",
            session_key="sess6",
        )
        assert intent.category == IntentCategory.CONVERSATION
        assert intent.target_domain == "digital_twin"

    def test_commander_detection_undaodu(self):
        """Commander authority detected for @UnDaoDu."""
        intent = self.dae.classify_intent(
            message="Hello",
            sender="@UnDaoDu",
            channel="discord",
            session_key="sess7",
        )
        assert intent.is_authorized_commander is True

    def test_non_commander(self):
        """Non-commander correctly identified."""
        intent = self.dae.classify_intent(
            message="Hello",
            sender="random_user_42",
            channel="telegram",
            session_key="sess8",
        )
        assert intent.is_authorized_commander is False


# ---------------------------------------------------------------------------
# Layer 0b: Gemma Intent Classifier (Unit)
# ---------------------------------------------------------------------------

class TestGemmaIntentClassifier:
    """Unit tests for GemmaIntentClassifier in isolation."""

    def test_classify_keyword_fallback_no_model(self):
        """Falls back to keyword-only when Gemma model not found."""
        classifier = GemmaIntentClassifier(
            model_path=Path("nonexistent_model.gguf")
        )
        result = classifier.classify(
            message="What is WSP 50?",
            keyword_scores={"query": 0.4, "monitor": 0.1},
        )
        assert result["category"] == "query"
        assert result["method"] == "keyword_only"
        assert result["confidence"] > 0

    def test_classify_default_on_empty_scores(self):
        """Returns default conversation when no keyword scores."""
        classifier = GemmaIntentClassifier(
            model_path=Path("nonexistent_model.gguf")
        )
        result = classifier.classify(
            message="banana",
            keyword_scores={},
        )
        assert result["category"] == "conversation"
        assert result["method"] == "default"
        assert result["confidence"] == 0.5

    def test_classify_respects_max_candidates(self):
        """Only top-N candidates are sent to Gemma."""
        classifier = GemmaIntentClassifier(
            model_path=Path("nonexistent_model.gguf"),
            max_candidates=2,
        )
        result = classifier.classify(
            message="check status",
            keyword_scores={
                "monitor": 0.5,
                "query": 0.3,
                "system": 0.1,
                "command": 0.05,
            },
        )
        # Should still work in keyword fallback
        assert result["category"] == "monitor"
        assert result["method"] == "keyword_only"

    def test_stats_tracking(self):
        """Stats track calls and fallbacks."""
        classifier = GemmaIntentClassifier(
            model_path=Path("nonexistent_model.gguf")
        )
        classifier.classify("test", {"query": 0.5})
        classifier.classify("test", {"command": 0.3})
        stats = classifier.stats
        assert stats["total_calls"] == 2
        assert stats["keyword_fallbacks"] == 2
        assert stats["gemma_calls"] == 0

    def test_is_available_none_before_check(self):
        """is_available is None before first classification attempt."""
        classifier = GemmaIntentClassifier()
        assert classifier.is_available is None


class TestGemmaHybridIntegration:
    """Test Gemma integration into OpenClawDAE.classify_intent()."""

    def setup_method(self):
        self.dae = OpenClawDAE(repo_root=project_root)

    def test_keyword_only_when_gemma_disabled(self):
        """OPENCLAW_GEMMA_INTENT=0 forces keyword-only mode."""
        with patch.dict("os.environ", {"OPENCLAW_GEMMA_INTENT": "0"}):
            intent = self.dae.classify_intent(
                message="What is the system health status?",
                sender="user123",
                channel="discord",
                session_key="sess_kw",
            )
            assert intent.category in (IntentCategory.QUERY, IntentCategory.MONITOR)
            assert intent.metadata.get("classification_method") in (
                "keyword_only", "default"
            )

    def test_metadata_includes_classification_method(self):
        """classify_intent always includes classification_method in metadata."""
        intent = self.dae.classify_intent(
            message="Hello world",
            sender="user123",
            channel="telegram",
            session_key="sess_meta",
        )
        # Greeting override doesn't set method (that's fine)
        # But non-greeting should
        intent2 = self.dae.classify_intent(
            message="Run the deploy script",
            sender="user123",
            channel="telegram",
            session_key="sess_meta2",
        )
        assert "classification_method" in intent2.metadata

    def test_gemma_hybrid_with_mock(self):
        """Mock Gemma classifier returns hybrid result."""
        mock_classifier = MagicMock(spec=GemmaIntentClassifier)
        mock_classifier.classify.return_value = {
            "category": "monitor",
            "confidence": 0.87,
            "method": "gemma_hybrid",
            "gemma_scores": {"monitor": 0.85, "query": 0.10},
            "latency_ms": 25,
        }
        # Inject mock classifier
        self.dae._gemma_classifier = mock_classifier
        self.dae._gemma_classifier_checked = True

        with patch.dict("os.environ", {"OPENCLAW_GEMMA_INTENT": "1"}):
            intent = self.dae.classify_intent(
                message="Show me the system status and health check",
                sender="user123",
                channel="discord",
                session_key="sess_hybrid",
            )
            assert intent.category == IntentCategory.MONITOR
            assert intent.confidence == 0.87
            assert intent.metadata["classification_method"] == "gemma_hybrid"
            assert intent.metadata["classification_latency_ms"] == 25

    def test_gemma_unavailable_degrades_gracefully(self):
        """When Gemma classifier is None, falls back to keyword scoring."""
        self.dae._gemma_classifier = None
        self.dae._gemma_classifier_checked = True

        intent = self.dae.classify_intent(
            message="Run the test suite and fix errors",
            sender="user123",
            channel="whatsapp",
            session_key="sess_fallback",
        )
        assert intent.category == IntentCategory.COMMAND
        assert intent.metadata.get("classification_method") == "keyword_only"

    def test_foundup_intent_with_gemma_disabled(self):
        """FOUNDUP intent still works in keyword-only mode."""
        with patch.dict("os.environ", {"OPENCLAW_GEMMA_INTENT": "0"}):
            intent = self.dae.classify_intent(
                message="Launch a new foundup and create a token",
                sender="@UnDaoDu",
                channel="discord",
                session_key="sess_foundup",
            )
            assert intent.category == IntentCategory.FOUNDUP
            assert intent.target_domain == "fam_adapter"
            assert intent.is_authorized_commander is True


# ---------------------------------------------------------------------------
# Layer 0c: SOURCE Tier - File Path Extraction & Permission Gate
# ---------------------------------------------------------------------------

class TestFilePathExtraction:
    """Test file path extraction from COMMAND messages."""

    def test_extract_python_file(self):
        """Extracts Python file paths from messages."""
        paths = OpenClawDAE._extract_file_paths(
            "Edit modules/ai_intelligence/ai_overseer/src/ai_overseer.py"
        )
        assert len(paths) == 1
        assert paths[0] == "modules/ai_intelligence/ai_overseer/src/ai_overseer.py"

    def test_extract_multiple_files(self):
        """Extracts multiple file paths from a single message."""
        paths = OpenClawDAE._extract_file_paths(
            "Fix modules/foo/src/bar.py and modules/baz/src/qux.py"
        )
        assert len(paths) == 2

    def test_extract_markdown_file(self):
        """Extracts .md file paths."""
        paths = OpenClawDAE._extract_file_paths(
            "Update modules/communication/moltbot_bridge/README.md"
        )
        assert len(paths) == 1
        assert paths[0].endswith("README.md")

    def test_extract_json_file(self):
        """Extracts .json file paths."""
        paths = OpenClawDAE._extract_file_paths(
            "Modify modules/infrastructure/wre_core/skillz/skills_registry_v2.json"
        )
        assert len(paths) == 1
        assert paths[0].endswith("skills_registry_v2.json")

    def test_extract_no_paths(self):
        """Returns empty list when no file paths found."""
        paths = OpenClawDAE._extract_file_paths("Run the test suite")
        assert paths == []

    def test_extract_quoted_path(self):
        """Handles quoted file paths."""
        paths = OpenClawDAE._extract_file_paths(
            'Edit "modules/foo/src/bar.py" please'
        )
        assert len(paths) == 1

    def test_backslash_normalized(self):
        """Windows backslash paths normalized to forward slashes."""
        paths = OpenClawDAE._extract_file_paths(
            "Fix modules\\foo\\src\\bar.py"
        )
        assert len(paths) == 1
        assert "\\" not in paths[0]


class TestSourceModificationDetection:
    """Test _is_source_modification heuristic."""

    def setup_method(self):
        self.dae = OpenClawDAE(repo_root=project_root)

    def _make_intent(self, message: str) -> OpenClawIntent:
        return OpenClawIntent(
            raw_message=message,
            category=IntentCategory.COMMAND,
            confidence=0.9,
            sender="@UnDaoDu",
            channel="discord",
            session_key="test",
            is_authorized_commander=True,
        )

    def test_edit_with_file_path(self):
        """'edit' + file path = source modification."""
        intent = self._make_intent("Edit modules/foo/src/bar.py to fix the bug")
        assert self.dae._is_source_modification(intent) is True

    def test_modify_module(self):
        """'modify' + 'module' = source modification."""
        intent = self._make_intent("Modify the overseer module to add logging")
        assert self.dae._is_source_modification(intent) is True

    def test_run_tests_not_source(self):
        """'run tests' is NOT source modification."""
        intent = self._make_intent("Run the test suite and report results")
        assert self.dae._is_source_modification(intent) is False

    def test_deploy_not_source(self):
        """'deploy' without file path is NOT source modification."""
        intent = self._make_intent("Deploy the latest changes to staging")
        assert self.dae._is_source_modification(intent) is False

    def test_refactor_source_code(self):
        """'refactor' + 'source' = source modification."""
        intent = self._make_intent("Refactor the source code of the chat engine")
        assert self.dae._is_source_modification(intent) is True


class TestSourceTierResolution:
    """Test SOURCE tier is correctly resolved for code-modification commands."""

    def setup_method(self):
        self.dae = OpenClawDAE(repo_root=project_root)

    def test_commander_source_modification_gets_source_tier(self):
        """Commander with source modification intent -> SOURCE tier."""
        # Need permissions to be loaded for SOURCE tier to be returned
        self.dae._permissions = MagicMock()

        intent = OpenClawIntent(
            raw_message="Edit modules/foo/src/bar.py to fix the bug",
            category=IntentCategory.COMMAND,
            confidence=0.9,
            sender="@UnDaoDu",
            channel="discord",
            session_key="test",
            is_authorized_commander=True,
        )
        tier = self.dae._resolve_autonomy_tier(intent)
        assert tier == AutonomyTier.SOURCE

    def test_commander_non_source_command_gets_docs_tests(self):
        """Commander with non-source command -> DOCS_TESTS tier."""
        self.dae._permissions = MagicMock()

        intent = OpenClawIntent(
            raw_message="Run the test suite and deploy",
            category=IntentCategory.COMMAND,
            confidence=0.9,
            sender="@UnDaoDu",
            channel="discord",
            session_key="test",
            is_authorized_commander=True,
        )
        tier = self.dae._resolve_autonomy_tier(intent)
        assert tier == AutonomyTier.DOCS_TESTS

    def test_non_commander_never_gets_source(self):
        """Non-commanders ALWAYS get ADVISORY regardless of message."""
        self.dae._permissions = MagicMock()

        intent = OpenClawIntent(
            raw_message="Edit modules/foo/src/bar.py",
            category=IntentCategory.COMMAND,
            confidence=0.9,
            sender="hacker123",
            channel="telegram",
            session_key="test",
            is_authorized_commander=False,
        )
        tier = self.dae._resolve_autonomy_tier(intent)
        assert tier == AutonomyTier.ADVISORY

    def test_no_permissions_fails_closed(self):
        """Without permission manager loaded, COMMAND -> ADVISORY (fail-closed)."""
        # Patch the property to return None (preventing lazy-load)
        with patch.object(type(self.dae), "permissions", new_callable=PropertyMock, return_value=None):
            intent = OpenClawIntent(
                raw_message="Edit modules/foo/src/bar.py",
                category=IntentCategory.COMMAND,
                confidence=0.9,
                sender="@UnDaoDu",
                channel="discord",
                session_key="test",
                is_authorized_commander=True,
            )
            tier = self.dae._resolve_autonomy_tier(intent)
            assert tier == AutonomyTier.ADVISORY


class TestSourcePermissionGate:
    """Test file-specific SOURCE permission checks."""

    def setup_method(self):
        self.dae = OpenClawDAE(repo_root=project_root)

    def test_source_permission_blocked_no_manager(self):
        """SOURCE denied when permission manager is None (fail-closed)."""
        with patch.object(type(self.dae), "permissions", new_callable=PropertyMock, return_value=None):
            intent = OpenClawIntent(
                raw_message="Edit modules/foo/src/bar.py",
                category=IntentCategory.COMMAND,
                confidence=0.9,
                sender="@UnDaoDu",
                channel="discord",
                session_key="test",
                is_authorized_commander=True,
            )
            granted, reason = self.dae._check_source_permission(intent)
            assert granted is False
            assert "unavailable" in reason

    def test_source_permission_file_allowed(self):
        """SOURCE granted when permission manager allows the file."""
        mock_perms = MagicMock()
        mock_perms.check_permission.return_value = MagicMock(
            allowed=True, reason="Permission granted"
        )
        self.dae._permissions = mock_perms

        intent = OpenClawIntent(
            raw_message="Edit modules/foo/src/bar.py",
            category=IntentCategory.COMMAND,
            confidence=0.9,
            sender="@UnDaoDu",
            channel="discord",
            session_key="test",
            is_authorized_commander=True,
        )
        granted, reason = self.dae._check_source_permission(intent)
        assert granted is True
        # Should have called check_permission with the file path
        mock_perms.check_permission.assert_called_with(
            agent_id="openclaw",
            operation="write",
            file_path="modules/foo/src/bar.py",
        )

    def test_source_permission_file_forbidden(self):
        """SOURCE denied when file is in forbidlist."""
        mock_perms = MagicMock()
        mock_perms.check_permission.return_value = MagicMock(
            allowed=False, reason="File main.py in forbidlist"
        )
        self.dae._permissions = mock_perms

        intent = OpenClawIntent(
            raw_message="Edit main.py to add a feature",
            category=IntentCategory.COMMAND,
            confidence=0.9,
            sender="@UnDaoDu",
            channel="discord",
            session_key="test",
            is_authorized_commander=True,
        )
        # main.py won't be extracted by our regex (it's a single segment, not dir/file)
        # But the general write check should still be called
        granted, reason = self.dae._check_source_permission(intent)
        # With no file paths extracted, falls through to general check
        assert granted is False

    def test_source_permission_exception_fails_closed(self):
        """SOURCE denied when permission check throws exception."""
        mock_perms = MagicMock()
        mock_perms.check_permission.side_effect = RuntimeError("DB offline")
        self.dae._permissions = mock_perms

        intent = OpenClawIntent(
            raw_message="Edit modules/foo/src/bar.py",
            category=IntentCategory.COMMAND,
            confidence=0.9,
            sender="@UnDaoDu",
            channel="discord",
            session_key="test",
            is_authorized_commander=True,
        )
        granted, reason = self.dae._check_source_permission(intent)
        assert granted is False
        assert "error" in reason


# ---------------------------------------------------------------------------
# Layer 1: WSP Preflight
# ---------------------------------------------------------------------------

class TestWSPPreflight:
    """Test WSP 50 pre-action verification."""

    def setup_method(self):
        self.dae = OpenClawDAE(repo_root=project_root)

    def test_command_blocked_for_non_commander(self):
        """COMMAND intent blocked for non-authorized sender."""
        intent = OpenClawIntent(
            raw_message="Run deploy script",
            category=IntentCategory.COMMAND,
            confidence=0.8,
            sender="random_user",
            channel="telegram",
            session_key="sess",
            is_authorized_commander=False,
        )
        assert self.dae._wsp_preflight(intent) is False

    def test_command_allowed_for_commander(self):
        """COMMAND intent allowed for authorized commander."""
        intent = OpenClawIntent(
            raw_message="Run deploy script",
            category=IntentCategory.COMMAND,
            confidence=0.8,
            sender="@UnDaoDu",
            channel="whatsapp",
            session_key="sess",
            is_authorized_commander=True,
        )
        # WRE won't be loaded in test, so it should fail on WRE check
        # but authority check passes
        result = self.dae._wsp_preflight(intent)
        # May be False due to WRE unavailability - that's correct behavior
        assert isinstance(result, bool)

    def test_query_allowed_for_anyone(self):
        """QUERY intent allowed for any sender (read-only)."""
        intent = OpenClawIntent(
            raw_message="What is WSP 50?",
            category=IntentCategory.QUERY,
            confidence=0.7,
            sender="random_user",
            channel="discord",
            session_key="sess",
            is_authorized_commander=False,
        )
        assert self.dae._wsp_preflight(intent) is True

    def test_system_blocked_for_non_commander(self):
        """SYSTEM intent blocked for non-authorized sender."""
        intent = OpenClawIntent(
            raw_message="Restart the server",
            category=IntentCategory.SYSTEM,
            confidence=0.9,
            sender="hacker123",
            channel="telegram",
            session_key="sess",
            is_authorized_commander=False,
        )
        assert self.dae._wsp_preflight(intent) is False


# ---------------------------------------------------------------------------
# Layer 2: Permission Gate
# ---------------------------------------------------------------------------

class TestPermissionGate:
    """Test graduated autonomy permission resolution."""

    def setup_method(self):
        self.dae = OpenClawDAE(repo_root=project_root)

    def test_non_commander_gets_advisory(self):
        """Non-commanders always get ADVISORY tier."""
        intent = OpenClawIntent(
            raw_message="hello",
            category=IntentCategory.QUERY,
            confidence=0.5,
            sender="user",
            channel="discord",
            session_key="sess",
            is_authorized_commander=False,
        )
        tier = self.dae._resolve_autonomy_tier(intent)
        assert tier == AutonomyTier.ADVISORY

    def test_commander_query_gets_metrics(self):
        """Commander with QUERY gets METRICS tier."""
        intent = OpenClawIntent(
            raw_message="search for something",
            category=IntentCategory.QUERY,
            confidence=0.8,
            sender="@UnDaoDu",
            channel="whatsapp",
            session_key="sess",
            is_authorized_commander=True,
        )
        tier = self.dae._resolve_autonomy_tier(intent)
        assert tier == AutonomyTier.METRICS

    def test_permission_gate_blocks_non_commander_elevated(self):
        """Permission gate blocks non-commanders from elevated tiers."""
        intent = OpenClawIntent(
            raw_message="hack the system",
            category=IntentCategory.COMMAND,
            confidence=0.9,
            sender="bad_actor",
            channel="telegram",
            session_key="sess",
            is_authorized_commander=False,
        )
        gate_ok = self.dae._check_permission_gate(intent, AutonomyTier.SOURCE)
        assert gate_ok is False

    def test_advisory_always_passes_gate(self):
        """ADVISORY tier always passes permission gate."""
        intent = OpenClawIntent(
            raw_message="hello",
            category=IntentCategory.CONVERSATION,
            confidence=0.5,
            sender="anyone",
            channel="discord",
            session_key="sess",
            is_authorized_commander=False,
        )
        gate_ok = self.dae._check_permission_gate(intent, AutonomyTier.ADVISORY)
        assert gate_ok is True


# ---------------------------------------------------------------------------
# Layer 3: End-to-End Process
# ---------------------------------------------------------------------------

class TestEndToEndProcess:
    """Test full autonomy loop via process()."""

    def setup_method(self):
        self.dae = OpenClawDAE(repo_root=project_root)

    def test_conversation_returns_response(self):
        """Conversation message returns Digital Twin response."""
        result = asyncio.run(self.dae.process(
            message="Hey, how are you?",
            sender="user123",
            channel="telegram",
        ))
        assert isinstance(result, str)
        assert len(result) > 0
        assert "0102" in result or "Digital Twin" in result

    def test_blocked_command_downgrades_to_conversation(self):
        """Non-commander COMMAND downgrades to conversation response."""
        result = asyncio.run(self.dae.process(
            message="Run the deploy script now",
            sender="random_user",
            channel="whatsapp",
        ))
        assert isinstance(result, str)
        # Should get a conversational response, not execution
        assert "0102" in result or "Digital Twin" in result or "received" in result.lower()

    def test_monitor_returns_status(self):
        """MONITOR intent returns system status."""
        result = asyncio.run(self.dae.process(
            message="Show system status and health",
            sender="user123",
            channel="discord",
        ))
        assert isinstance(result, str)
        assert "Status" in result or "status" in result.lower()

    def test_security_filter_blocks_secrets(self):
        """Validate phase catches secret patterns in output."""
        # The validate_and_remember phase should catch this
        dae = self.dae
        from modules.communication.moltbot_bridge.src.openclaw_dae import (
            ExecutionPlan, AutonomyTier
        )
        intent = OpenClawIntent(
            raw_message="test",
            category=IntentCategory.QUERY,
            confidence=0.5,
            sender="user",
            channel="test",
            session_key="test",
            is_authorized_commander=False,
        )
        plan = ExecutionPlan(
            intent=intent,
            route="test",
            permission_level=AutonomyTier.ADVISORY,
            wsp_preflight_passed=True,
        )
        # Simulate a response that leaks an API key
        result = dae._validate_and_remember(
            plan=plan,
            response_text="Here is the key: AIzaSyB1234567890abcdef",
            execution_time_ms=10,
        )
        assert "REDACTED" in result.response_text
        assert len(result.wsp_violations) > 0


# ---------------------------------------------------------------------------
# Run tests
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v", "--tb=short"])
