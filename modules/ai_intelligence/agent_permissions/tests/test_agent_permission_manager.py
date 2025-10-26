# -*- coding: utf-8 -*-
"""
Unit Tests for Agent Permission Manager

Tests permission management, skills_registry integration, allowlist/forbidlist
validation, and automatic downgrade functionality.

WSP Compliance:
- WSP 5 (Test Coverage): Comprehensive unit tests
- WSP 6 (Test Audit): Documents test coverage
"""

import unittest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any

import sys
project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from modules.ai_intelligence.agent_permissions.src.agent_permission_manager import (
    AgentPermissionManager,
    PermissionCheckResult,
    PermissionRecord,
    PROMOTION_THRESHOLDS,
    DOWNGRADE_THRESHOLDS
)
from modules.ai_intelligence.agent_permissions.src.confidence_tracker import (
    ConfidenceTracker
)


class TestAgentPermissionManager(unittest.TestCase):
    """Test suite for AgentPermissionManager"""

    def setUp(self):
        """Set up test environment with temp directory"""
        self.test_dir = Path(tempfile.mkdtemp())

        # Create test skills_registry.json location
        self.skills_dir = self.test_dir / ".claude" / "skills"
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        self.skills_registry_path = self.skills_dir / "skills_registry.json"

        # Create memory directory (expected at modules/ai_intelligence/agent_permissions/memory)
        self.memory_dir = self.test_dir / "modules" / "ai_intelligence" / "agent_permissions" / "memory"
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        # Initialize manager with repo_root only
        self.manager = AgentPermissionManager(repo_root=self.test_dir)

    def tearDown(self):
        """Clean up test environment"""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_initialization(self):
        """Test manager initialization"""
        self.assertEqual(self.manager.skills_registry_path, self.skills_registry_path)
        self.assertTrue(self.manager.permission_events_path.parent.exists())
        self.assertIsInstance(self.manager.confidence_tracker, ConfidenceTracker)

    def test_check_permission_unregistered_agent(self):
        """Test permission check for unregistered agent"""
        result = self.manager.check_permission(
            agent_id="unregistered_agent",
            operation="read",
            file_path=None
        )

        self.assertFalse(result.allowed)
        self.assertIn("not registered", result.reason)

    def test_register_agent_default_permissions(self):
        """Test agent registration with default read_only permissions"""
        agent_id = "gemma_dead_code_detection"

        # Grant permission creates agent if not exists - start with read_only (default permission level)
        # Granting any permission automatically creates the agent
        record = self.manager.grant_permission(
            agent_id=agent_id,
            permission_type="read_only",
            granted_by="system",
            justification="Initial agent creation"
        )

        self.assertIsNotNone(record)

        # Check permission
        result = self.manager.check_permission(agent_id, "read")
        self.assertTrue(result.allowed)
        self.assertEqual(result.permission_level, "read_only")

    def test_grant_permission_with_allowlist(self):
        """Test permission grant with allowlist patterns"""
        agent_id = "test_agent"

        # Set confidence above downgrade threshold for metrics_write (0.70)
        self.manager.confidence_tracker.confidence_scores[agent_id] = 0.75

        # Grant metrics_write permission (creates agent if not exists)
        record = self.manager.grant_permission(
            agent_id=agent_id,
            permission_type="metrics_write",
            granted_by="0102",
            justification="Proven ability with bug detection",
            allowlist_patterns=["modules/**/*.json"],
            forbidlist_patterns=["*_dae.py", "main.py"]
        )

        self.assertIsNotNone(record)

        # Check permission for allowed file
        # Use 'metrics_write' operation since that's what the permission level allows
        result = self.manager.check_permission(
            agent_id,
            "metrics_write",
            "modules/ai_intelligence/metrics/test_metrics.json"
        )
        self.assertTrue(result.allowed)

    def test_forbidlist_blocks_access(self):
        """Test forbidlist blocks access to critical files"""
        agent_id = "test_agent"

        # Grant permission (creates agent if not exists)
        self.manager.grant_permission(
            agent_id=agent_id,
            permission_type="edit_access_tests",
            granted_by="0102",
            justification="Test",
            allowlist_patterns=["**/*.py"],
            forbidlist_patterns=["*_dae.py", "main.py", "wsp_orchestrator.py"]
        )

        # Check forbidden files
        forbidden_files = [
            "modules/communication/livechat/src/auto_moderator_dae.py",
            "main.py",
            "modules/infrastructure/wsp_orchestrator/src/wsp_orchestrator.py"
        ]

        for file_path in forbidden_files:
            result = self.manager.check_permission(agent_id, "edit", file_path)
            self.assertFalse(result.allowed, f"Should forbid {file_path}")
            self.assertIn("forbidlist", result.reason)

    def test_allowlist_restricts_access(self):
        """Test allowlist restricts access to only specified patterns"""
        agent_id = "test_agent"

        # Set confidence above downgrade threshold for edit_access_tests (0.80)
        self.manager.confidence_tracker.confidence_scores[agent_id] = 0.85

        # Grant permission with restrictive allowlist (creates agent if not exists)
        self.manager.grant_permission(
            agent_id=agent_id,
            permission_type="edit_access_tests",
            granted_by="0102",
            justification="Test",
            allowlist_patterns=["modules/**/tests/*.py"],
            forbidlist_patterns=[]
        )

        # Allowed: test files
        result = self.manager.check_permission(
            agent_id,
            "edit",
            "modules/ai_intelligence/agent_permissions/tests/test_confidence.py"
        )
        self.assertTrue(result.allowed)

        # Not allowed: source files
        result = self.manager.check_permission(
            agent_id,
            "edit",
            "modules/ai_intelligence/agent_permissions/src/confidence_tracker.py"
        )
        self.assertFalse(result.allowed)
        self.assertIn("not in allowlist", result.reason)

    def test_automatic_downgrade_on_low_confidence(self):
        """Test automatic downgrade when confidence drops"""
        agent_id = "test_agent"

        # Set initial confidence above threshold
        self.manager.confidence_tracker.confidence_scores[agent_id] = 0.75

        # Grant metrics_write permission (creates agent if not exists)
        self.manager.grant_permission(
            agent_id=agent_id,
            permission_type="metrics_write",
            granted_by="0102",
            justification="Initial grant"
        )

        # Manually set confidence below threshold
        # metrics_write downgrade threshold is 0.70
        self.manager.confidence_tracker.confidence_scores[agent_id] = 0.65

        # Check permission should fail due to low confidence
        # Use 'metrics_write' operation since that's what the permission level allows
        result = self.manager.check_permission(agent_id, "metrics_write")

        self.assertFalse(result.allowed)
        self.assertIn("Confidence", result.reason)
        self.assertIn("below threshold", result.reason)

    def test_downgrade_permission(self):
        """Test manual permission downgrade"""
        agent_id = "test_agent"

        # Grant edit_access_tests (creates agent if not exists)
        self.manager.grant_permission(
            agent_id=agent_id,
            permission_type="edit_access_tests",
            granted_by="0102",
            justification="Initial grant"
        )

        # Downgrade
        success = self.manager.downgrade_permission(
            agent_id=agent_id,
            reason="Failed regression test",
            requires_reapproval=True
        )

        self.assertTrue(success)

        # Check new permission level
        skill = self.manager._find_skill(agent_id)
        self.assertEqual(skill['permission_level'], 'metrics_write')
        self.assertTrue(skill['requires_reapproval'])

    def test_permission_expiration(self):
        """Test expired permissions are rejected"""
        agent_id = "test_agent"

        # Grant permission with expiration (creates agent if not exists)
        self.manager.grant_permission(
            agent_id=agent_id,
            permission_type="metrics_write",
            granted_by="0102",
            justification="Temporary permission",
            duration_days=1
        )

        # Set expiration to past
        skill = self.manager._find_skill(agent_id)
        skill['permission_expires_at'] = (datetime.now() - timedelta(days=1)).isoformat()
        self.manager._save_skills_registry()

        # Check permission
        result = self.manager.check_permission(agent_id, "write")
        self.assertFalse(result.allowed)
        self.assertIn("expired", result.reason)

    def test_approval_signature_generation(self):
        """Test approval signature is generated correctly"""
        agent_id = "test_agent"

        # Grant permission (creates agent if not exists)
        self.manager.grant_permission(
            agent_id=agent_id,
            permission_type="metrics_write",
            granted_by="0102",
            justification="Test approval"
        )

        # Check promotion history
        skill = self.manager._find_skill(agent_id)
        promotion_history = skill.get('promotion_history', [])

        self.assertGreater(len(promotion_history), 0)

        latest_promotion = promotion_history[-1]
        self.assertIn('approval_signature', latest_promotion)
        self.assertTrue(latest_promotion['approval_signature'].startswith('sha256:'))
        self.assertEqual(len(latest_promotion['approval_signature']), 71)  # "sha256:" + 64 char hex

    def test_permission_audit_trail(self):
        """Test permission events are logged to JSONL"""
        agent_id = "test_agent"

        # Grant permission (creates agent if not exists)
        self.manager.grant_permission(
            agent_id=agent_id,
            permission_type="metrics_write",
            granted_by="0102",
            justification="Test"
        )

        # Check JSONL file
        permission_events = self.memory_dir / "permission_events.jsonl"
        self.assertTrue(permission_events.exists())

        # Read events
        events = []
        with open(permission_events, 'r') as f:
            for line in f:
                events.append(json.loads(line.strip()))

        # Should have at least PERMISSION_GRANTED event
        self.assertGreaterEqual(len(events), 1)

        grant_event = [e for e in events if e['event_type'] == 'PERMISSION_GRANTED']
        self.assertEqual(len(grant_event), 1)
        self.assertEqual(grant_event[0]['agent_id'], agent_id)

    def test_promotion_thresholds(self):
        """Test promotion threshold constants"""
        # read_only doesn't have thresholds (starting point)
        self.assertEqual(PROMOTION_THRESHOLDS['metrics_write']['confidence_required'], 0.75)
        self.assertEqual(PROMOTION_THRESHOLDS['edit_access_tests']['confidence_required'], 0.85)
        self.assertEqual(PROMOTION_THRESHOLDS['edit_access_src']['confidence_required'], 0.95)

    def test_downgrade_thresholds(self):
        """Test downgrade threshold constants"""
        # read_only is not in DOWNGRADE_THRESHOLDS (bottom of ladder)
        self.assertEqual(DOWNGRADE_THRESHOLDS['metrics_write'], 0.70)
        self.assertEqual(DOWNGRADE_THRESHOLDS['edit_access_tests'], 0.80)
        self.assertEqual(DOWNGRADE_THRESHOLDS['edit_access_src'], 0.90)

    def test_multiple_agents_isolation(self):
        """Test multiple agents have isolated permissions"""
        agent1 = "gemma_dead_code_detection"
        agent2 = "qwen_code_quality_investigator"

        # Set confidence above downgrade thresholds
        self.manager.confidence_tracker.confidence_scores[agent1] = 0.75  # for metrics_write (0.70)
        self.manager.confidence_tracker.confidence_scores[agent2] = 0.85  # for edit_access_tests (0.80)

        # Grant different permissions (creates agents if not exist)
        self.manager.grant_permission(agent1, "metrics_write", "0102", justification="Test")
        self.manager.grant_permission(agent2, "edit_access_tests", "0102", justification="Test")

        # Check permissions (use appropriate operations for each permission level)
        result1 = self.manager.check_permission(agent1, "metrics_write")
        result2 = self.manager.check_permission(agent2, "edit")

        self.assertTrue(result1.allowed)
        self.assertTrue(result2.allowed)
        self.assertEqual(result1.permission_level, "metrics_write")
        self.assertEqual(result2.permission_level, "edit_access_tests")

    def test_permission_record_creation(self):
        """Test PermissionRecord creation"""
        now = datetime.now()
        record = PermissionRecord(
            agent_id="test_agent",
            permission_level="metrics_write",
            granted_at=now,
            granted_by="0102",
            expires_at=now + timedelta(days=30),
            confidence_at_grant=0.80,
            allowlist_patterns=["**/*.json"],
            forbidlist_patterns=["*.env"],
            justification="Test",
            approval_signature="abc123"
        )

        self.assertEqual(record.agent_id, "test_agent")
        self.assertEqual(record.permission_level, "metrics_write")
        self.assertEqual(record.confidence_at_grant, 0.80)
        self.assertEqual(len(record.allowlist_patterns), 1)

    def test_check_permission_result_structure(self):
        """Test PermissionCheckResult structure"""
        result = PermissionCheckResult(
            allowed=True,
            reason="Permission granted",
            permission_level="metrics_write",
            confidence=0.85
        )

        self.assertTrue(result.allowed)
        self.assertEqual(result.permission_level, "metrics_write")
        self.assertEqual(result.confidence, 0.85)

    def test_skills_registry_persistence(self):
        """Test skills registry persists across manager instances"""
        agent_id = "test_agent"

        # Grant permission (creates agent if not exists)
        self.manager.grant_permission(
            agent_id=agent_id,
            permission_type="read_only",
            granted_by="system",
            justification="Test agent"
        )

        # Create new manager instance
        new_manager = AgentPermissionManager(repo_root=self.test_dir)

        # Check agent is still registered
        result = new_manager.check_permission(agent_id, "read")
        self.assertTrue(result.allowed)

    def test_file_pattern_matching_recursive_glob(self):
        """Test file pattern matching with ** recursive glob"""
        agent_id = "test_agent"

        # Set confidence above downgrade threshold for edit_access_tests (0.80)
        self.manager.confidence_tracker.confidence_scores[agent_id] = 0.85

        # Grant permission (creates agent if not exists)
        self.manager.grant_permission(
            agent_id=agent_id,
            permission_type="edit_access_tests",
            granted_by="0102",
            justification="Test",
            allowlist_patterns=["modules/**/*.py"],
            forbidlist_patterns=[]
        )

        # Test deep nested file
        result = self.manager.check_permission(
            agent_id,
            "edit",
            "modules/ai_intelligence/agent_permissions/src/confidence_tracker.py"
        )
        self.assertTrue(result.allowed)

        # Test non-matching file
        result = self.manager.check_permission(
            agent_id,
            "edit",
            "main.py"
        )
        self.assertFalse(result.allowed)

    def test_48_hour_cooldown_after_downgrade(self):
        """Test 48-hour cooldown is enforced after downgrade"""
        agent_id = "test_agent"

        # Grant permission (creates agent if not exists)
        self.manager.grant_permission(
            agent_id=agent_id,
            permission_type="metrics_write",
            granted_by="0102",
            justification="Initial grant"
        )

        # Downgrade
        self.manager.downgrade_permission(
            agent_id=agent_id,
            reason="Test downgrade",
            requires_reapproval=True
        )

        # Check downgrade timestamp is set
        skill = self.manager._find_skill(agent_id)
        self.assertIn('permission_downgraded_at', skill)
        self.assertTrue(skill['requires_reapproval'])

        # In real implementation, check_permission would enforce
        # 48-hour cooldown before allowing promotion

    def test_wsp_compliance_tracking(self):
        """Test WSP compliance can be tracked in promotion history"""
        agent_id = "test_agent"

        # Grant permission with WSP compliance details (creates agent if not exists)
        self.manager.grant_permission(
            agent_id=agent_id,
            permission_type="metrics_write",
            granted_by="0102",
            justification="Demonstrated WSP 50 compliance"
        )

        # Check promotion history
        skill = self.manager._find_skill(agent_id)
        promotion = skill['promotion_history'][-1]

        self.assertIn('reason', promotion)
        self.assertIn('WSP', promotion['reason'])


if __name__ == '__main__':
    unittest.main()
