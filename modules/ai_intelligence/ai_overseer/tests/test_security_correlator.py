#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for security event correlator.

WSP 71/95: Incident detection, containment, and forensics.
"""

import json
import os
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

import pytest


# ---------------------------------------------------------------------------
# Correlator Tests
# ---------------------------------------------------------------------------

class TestSecurityEventCorrelator:
    """Tests for SecurityEventCorrelator."""

    def test_ingest_event_below_threshold(self):
        """Events below threshold do not trigger incident."""
        from modules.ai_intelligence.ai_overseer.src.security_event_correlator import (
            SecurityEventCorrelator, SecurityEvent, EventType,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            correlator = SecurityEventCorrelator(Path(tmpdir))
            correlator.incident_threshold = 5

            # Ingest 4 events (below threshold)
            for i in range(4):
                event = SecurityEvent(
                    event_type=EventType.PERMISSION_DENIED,
                    timestamp=time.time(),
                    sender="user1",
                    channel="test",
                    details={"idx": i},
                )
                incident = correlator.ingest_event(event)
                assert incident is None

    def test_ingest_event_at_threshold_creates_incident(self):
        """Threshold crossing creates incident."""
        from modules.ai_intelligence.ai_overseer.src.security_event_correlator import (
            SecurityEventCorrelator, SecurityEvent, EventType, IncidentSeverity,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            correlator = SecurityEventCorrelator(Path(tmpdir))
            correlator.incident_threshold = 3

            # Ingest 3 events (at threshold)
            for i in range(2):
                event = SecurityEvent(
                    event_type=EventType.RATE_LIMITED,
                    timestamp=time.time(),
                    sender="attacker",
                    channel="spam",
                    details={},
                )
                correlator.ingest_event(event)

            # Third event crosses threshold
            event = SecurityEvent(
                event_type=EventType.RATE_LIMITED,
                timestamp=time.time(),
                sender="attacker",
                channel="spam",
                details={},
            )
            incident = correlator.ingest_event(event)

            assert incident is not None
            assert incident.incident_id.startswith("INC-")
            assert incident.policy_trigger.startswith("sender_threshold:")
            assert incident.event_counts.get("rate_limited") == 3

    def test_incident_dedupe_suppresses_duplicates(self):
        """Dedupe window suppresses repeated incidents."""
        from modules.ai_intelligence.ai_overseer.src.security_event_correlator import (
            SecurityEventCorrelator, SecurityEvent, EventType,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            correlator = SecurityEventCorrelator(Path(tmpdir))
            correlator.incident_threshold = 2
            correlator.alert_dedupe_window_sec = 60

            # First batch triggers incident
            for _ in range(2):
                correlator.ingest_event(SecurityEvent(
                    event_type=EventType.PERMISSION_DENIED,
                    timestamp=time.time(),
                    sender="user1",
                    channel="test",
                    details={},
                ))

            # Clear events but not dedupe cache
            correlator._events.clear()
            correlator._events_by_sender.clear()

            # Second batch should be deduped
            for _ in range(2):
                incident = correlator.ingest_event(SecurityEvent(
                    event_type=EventType.PERMISSION_DENIED,
                    timestamp=time.time(),
                    sender="user1",
                    channel="test",
                    details={},
                ))

            # Should have suppressed the second incident
            assert correlator._dedupe_suppressions >= 1

    def test_severity_calculation(self):
        """Severity scales with event composition."""
        from modules.ai_intelligence.ai_overseer.src.security_event_correlator import (
            SecurityEventCorrelator, SecurityEvent, EventType, IncidentSeverity,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            correlator = SecurityEventCorrelator(Path(tmpdir))

            # Security alert events = HIGH severity
            events_with_alert = [
                SecurityEvent(EventType.SECURITY_ALERT, time.time(), "s", "c", {}),
                SecurityEvent(EventType.PERMISSION_DENIED, time.time(), "s", "c", {}),
            ]
            assert correlator._calculate_severity(events_with_alert) == IncidentSeverity.HIGH

            # Many events without security alert = MEDIUM
            many_events = [
                SecurityEvent(EventType.RATE_LIMITED, time.time(), "s", "c", {})
                for _ in range(10)
            ]
            assert correlator._calculate_severity(many_events) == IncidentSeverity.MEDIUM


class TestContainmentLifecycle:
    """Tests for containment apply/release lifecycle."""

    def test_containment_applied_on_incident(self):
        """Containment is applied when HIGH severity incident is created."""
        from modules.ai_intelligence.ai_overseer.src.security_event_correlator import (
            SecurityEventCorrelator, SecurityEvent, EventType, ContainmentAction,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            correlator = SecurityEventCorrelator(Path(tmpdir))
            correlator.incident_threshold = 2
            correlator.containment_enabled = True
            correlator.containment_duration_sec = 60

            # Trigger HIGH severity incident (SECURITY_ALERT = HIGH)
            correlator.ingest_event(SecurityEvent(
                event_type=EventType.SECURITY_ALERT,
                timestamp=time.time(),
                sender="bad_user",
                channel="test",
                details={},
            ))
            correlator.ingest_event(SecurityEvent(
                event_type=EventType.PERMISSION_DENIED,
                timestamp=time.time(),
                sender="bad_user",
                channel="test",
                details={},
            ))

            # Check containment applied
            state = correlator.check_containment("bad_user", "test")
            assert state is not None
            assert state.action in (ContainmentAction.MUTE_SENDER, ContainmentAction.MUTE_CHANNEL)

    def test_containment_expires_after_duration(self):
        """Containment expires after configured duration."""
        from modules.ai_intelligence.ai_overseer.src.security_event_correlator import (
            SecurityEventCorrelator, SecurityEvent, EventType,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            correlator = SecurityEventCorrelator(Path(tmpdir))
            correlator.incident_threshold = 2
            correlator.containment_enabled = True
            correlator.containment_duration_sec = 1  # 1 second

            # Trigger incident
            for _ in range(2):
                correlator.ingest_event(SecurityEvent(
                    event_type=EventType.RATE_LIMITED,
                    timestamp=time.time(),
                    sender="temp_user",
                    channel="test",
                    details={},
                ))

            # Wait for expiry
            time.sleep(1.1)

            # Should be expired now
            state = correlator.check_containment("temp_user", "test")
            assert state is None

    def test_explicit_containment_release(self):
        """Containment can be explicitly released."""
        from modules.ai_intelligence.ai_overseer.src.security_event_correlator import (
            SecurityEventCorrelator, SecurityEvent, EventType,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            correlator = SecurityEventCorrelator(Path(tmpdir))
            correlator.incident_threshold = 2
            correlator.containment_enabled = True
            correlator.containment_duration_sec = 3600  # 1 hour

            # Trigger HIGH severity incident
            correlator.ingest_event(SecurityEvent(
                event_type=EventType.SECURITY_ALERT,
                timestamp=time.time(),
                sender="release_me",
                channel="test",
                details={},
            ))
            correlator.ingest_event(SecurityEvent(
                event_type=EventType.PERMISSION_DENIED,
                timestamp=time.time(),
                sender="release_me",
                channel="test",
                details={},
            ))

            # Verify containment active
            assert correlator.check_containment("release_me", "test") is not None

            # Release containment
            released = correlator.release_containment("sender", "release_me")
            assert released is True

            # Verify released
            assert correlator.check_containment("release_me", "test") is None

    def test_containment_disabled(self):
        """No containment when disabled."""
        from modules.ai_intelligence.ai_overseer.src.security_event_correlator import (
            SecurityEventCorrelator, SecurityEvent, EventType,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            correlator = SecurityEventCorrelator(Path(tmpdir))
            correlator.incident_threshold = 2
            correlator.containment_enabled = False

            # Trigger incident
            for _ in range(2):
                correlator.ingest_event(SecurityEvent(
                    event_type=EventType.RATE_LIMITED,
                    timestamp=time.time(),
                    sender="free_user",
                    channel="test",
                    details={},
                ))

            # No containment should be applied
            assert correlator.check_containment("free_user", "test") is None


class TestContainmentPersistence:
    """Tests for persistent containment state."""

    def test_containment_restores_across_correlator_instances(self):
        """Active containment should survive correlator restart."""
        from modules.ai_intelligence.ai_overseer.src.security_event_correlator import (
            SecurityEventCorrelator, SecurityEvent, EventType,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            correlator = SecurityEventCorrelator(Path(tmpdir))
            correlator.incident_threshold = 2
            correlator.containment_enabled = True
            correlator.containment_duration_sec = 3600

            correlator.ingest_event(SecurityEvent(
                event_type=EventType.SECURITY_ALERT,
                timestamp=time.time(),
                sender="persist_user",
                channel="persist_channel",
                details={},
            ))
            correlator.ingest_event(SecurityEvent(
                event_type=EventType.PERMISSION_DENIED,
                timestamp=time.time(),
                sender="persist_user",
                channel="persist_channel",
                details={},
            ))

            restored = SecurityEventCorrelator(Path(tmpdir))
            state = restored.check_containment("persist_user", "persist_channel")
            assert state is not None

    def test_containment_release_removes_persisted_state(self):
        """Manual release should remove state from persistent store."""
        from modules.ai_intelligence.ai_overseer.src.security_event_correlator import (
            SecurityEventCorrelator, SecurityEvent, EventType,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            correlator = SecurityEventCorrelator(Path(tmpdir))
            correlator.incident_threshold = 2
            correlator.containment_enabled = True
            correlator.containment_duration_sec = 3600

            correlator.ingest_event(SecurityEvent(
                event_type=EventType.SECURITY_ALERT,
                timestamp=time.time(),
                sender="release_persist",
                channel="persist_channel",
                details={},
            ))
            correlator.ingest_event(SecurityEvent(
                event_type=EventType.PERMISSION_DENIED,
                timestamp=time.time(),
                sender="release_persist",
                channel="persist_channel",
                details={},
            ))

            assert correlator.release_containment("sender", "release_persist") is True
            restored = SecurityEventCorrelator(Path(tmpdir))
            state = restored.check_containment("release_persist", "persist_channel")
            assert state is None


class TestForensicBundle:
    """Tests for forensic bundle export."""

    def test_bundle_export_creates_file(self):
        """Bundle export creates JSON file."""
        from modules.ai_intelligence.ai_overseer.src.security_event_correlator import (
            SecurityEventCorrelator, SecurityEvent, EventType,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            correlator = SecurityEventCorrelator(Path(tmpdir))
            correlator.incident_threshold = 2

            # Trigger incident
            incident = None
            for _ in range(2):
                incident = correlator.ingest_event(SecurityEvent(
                    event_type=EventType.SECURITY_ALERT,
                    timestamp=time.time(),
                    sender="bundle_test",
                    channel="export",
                    details={"test": True},
                ))

            assert incident is not None

            # Export bundle
            bundle_path = correlator.export_bundle(incident.incident_id)
            assert bundle_path is not None
            assert bundle_path.exists()

            # Verify bundle content
            with open(bundle_path) as f:
                bundle = json.load(f)

            assert bundle["bundle_version"] == "1.0"
            assert bundle["incident"]["incident_id"] == incident.incident_id
            assert len(bundle["incident"]["events"]) == 2

    def test_bundle_no_secrets(self):
        """Bundle does not contain actual secret values."""
        from modules.ai_intelligence.ai_overseer.src.security_event_correlator import (
            SecurityEventCorrelator, SecurityEvent, EventType,
        )
        # Only check for actual API key patterns, not generic words
        secret_patterns = ["AIza", "sk-ant-", "sk-proj-", "oauth_token="]

        with tempfile.TemporaryDirectory() as tmpdir:
            correlator = SecurityEventCorrelator(Path(tmpdir))
            correlator.incident_threshold = 2

            # Trigger incident with potentially sensitive details
            for _ in range(2):
                correlator.ingest_event(SecurityEvent(
                    event_type=EventType.PERMISSION_DENIED,
                    timestamp=time.time(),
                    sender="test_user",
                    channel="secure",
                    details={"message": "sensitive data here"},
                ))

            incident_id = list(correlator._incidents.keys())[0]
            bundle_path = correlator.export_bundle(incident_id)

            # Check bundle content for actual secret patterns
            bundle_text = bundle_path.read_text()
            for pattern in secret_patterns:
                assert pattern not in bundle_text, f"Found secret pattern: {pattern}"

    def test_bundle_includes_containment_actions(self):
        """Bundle includes containment actions taken for HIGH severity."""
        from modules.ai_intelligence.ai_overseer.src.security_event_correlator import (
            SecurityEventCorrelator, SecurityEvent, EventType,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            correlator = SecurityEventCorrelator(Path(tmpdir))
            correlator.incident_threshold = 2
            correlator.containment_enabled = True

            # Trigger HIGH severity incident (SECURITY_ALERT = HIGH)
            correlator.ingest_event(SecurityEvent(
                event_type=EventType.SECURITY_ALERT,
                timestamp=time.time(),
                sender="contained_user",
                channel="test",
                details={},
            ))
            correlator.ingest_event(SecurityEvent(
                event_type=EventType.PERMISSION_DENIED,
                timestamp=time.time(),
                sender="contained_user",
                channel="test",
                details={},
            ))

            incident_id = list(correlator._incidents.keys())[0]
            bundle_path = correlator.export_bundle(incident_id)

            with open(bundle_path) as f:
                bundle = json.load(f)

            # Should have containment actions
            assert "containment_actions" in bundle
            assert len(bundle["containment_actions"]) > 0


class TestCorrelatorStats:
    """Tests for correlator statistics."""

    def test_stats_include_all_fields(self):
        """Stats include all required fields."""
        from modules.ai_intelligence.ai_overseer.src.security_event_correlator import (
            SecurityEventCorrelator,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            correlator = SecurityEventCorrelator(Path(tmpdir))
            stats = correlator.get_stats()

            required_fields = [
                "events_in_window",
                "correlation_window_sec",
                "incident_threshold",
                "open_incidents",
                "total_incidents",
                "active_sender_containments",
                "active_channel_containments",
                "dedupe_suppressions",
                "containment_enabled",
            ]

            for field in required_fields:
                assert field in stats, f"Missing field: {field}"


class TestEventPruning:
    """Tests for event correlation window pruning."""

    def test_events_outside_window_pruned(self):
        """Events older than correlation window are pruned."""
        from modules.ai_intelligence.ai_overseer.src.security_event_correlator import (
            SecurityEventCorrelator, SecurityEvent, EventType,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            correlator = SecurityEventCorrelator(Path(tmpdir))
            correlator.correlation_window_sec = 1  # 1 second window

            # Add old event
            old_event = SecurityEvent(
                event_type=EventType.RATE_LIMITED,
                timestamp=time.time() - 2,  # 2 seconds ago
                sender="old_user",
                channel="test",
                details={},
            )
            correlator._events.append(old_event)
            correlator._events_by_sender["old_user"] = [old_event]

            # Trigger prune via new event
            correlator.ingest_event(SecurityEvent(
                event_type=EventType.RATE_LIMITED,
                timestamp=time.time(),
                sender="new_user",
                channel="test",
                details={},
            ))

            # Old event should be pruned
            assert "old_user" not in correlator._events_by_sender
            assert len(correlator._events) == 1


# ---------------------------------------------------------------------------
# Tranche 5: Authenticated Release, Audit, Consistency, Notifications
# ---------------------------------------------------------------------------

class TestAuthenticatedRelease:
    """Tests for authenticated containment release (Tranche 5 Step 1)."""

    def test_release_fails_without_token_configured(self):
        """Release fails when no operator token is configured."""
        from modules.ai_intelligence.ai_overseer.src.security_event_correlator import (
            SecurityEventCorrelator,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            correlator = SecurityEventCorrelator(Path(tmpdir))
            correlator.operator_token = ""  # No token configured

            result = correlator.release_containment_authenticated(
                target_type="sender",
                target_id="test_user",
                token="any_token",
                nonce="nonce123",
                requested_by="operator1",
                reason="test release",
            )

            assert result["success"] is False
            assert result["error"] == "authentication_failed"

    def test_release_fails_with_invalid_token(self):
        """Release fails when provided token doesn't match."""
        from modules.ai_intelligence.ai_overseer.src.security_event_correlator import (
            SecurityEventCorrelator,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            correlator = SecurityEventCorrelator(Path(tmpdir))
            correlator.operator_token = "correct_token_12345"

            result = correlator.release_containment_authenticated(
                target_type="sender",
                target_id="test_user",
                token="wrong_token",
                nonce="nonce456",
                requested_by="operator1",
                reason="test release",
            )

            assert result["success"] is False
            assert result["error"] == "authentication_failed"

    def test_release_succeeds_with_valid_token(self):
        """Release succeeds when token matches and containment exists."""
        from modules.ai_intelligence.ai_overseer.src.security_event_correlator import (
            SecurityEventCorrelator, SecurityEvent, EventType,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            correlator = SecurityEventCorrelator(Path(tmpdir))
            correlator.operator_token = "valid_operator_token_789"
            correlator.incident_threshold = 2
            correlator.containment_enabled = True
            correlator.containment_duration_sec = 3600

            # Trigger containment first (HIGH severity)
            correlator.ingest_event(SecurityEvent(
                event_type=EventType.SECURITY_ALERT,
                timestamp=time.time(),
                sender="auth_test_user",
                channel="test",
                details={},
            ))
            correlator.ingest_event(SecurityEvent(
                event_type=EventType.PERMISSION_DENIED,
                timestamp=time.time(),
                sender="auth_test_user",
                channel="test",
                details={},
            ))

            # Verify containment active
            assert correlator.check_containment("auth_test_user", "test") is not None

            # Authenticated release
            result = correlator.release_containment_authenticated(
                target_type="sender",
                target_id="auth_test_user",
                token="valid_operator_token_789",
                nonce="unique_nonce_abc123",
                requested_by="admin@example.com",
                reason="Verified false positive",
                source_ip="192.168.1.100",
                session_id="sess_xyz",
            )

            assert result["success"] is True
            assert result["release_id"].startswith("REL-")
            assert correlator.check_containment("auth_test_user", "test") is None


class TestReplayPrevention:
    """Tests for nonce-based replay prevention (Tranche 5 Step 1)."""

    def test_replay_detected_same_nonce(self):
        """Replay is detected when same nonce is reused."""
        from modules.ai_intelligence.ai_overseer.src.security_event_correlator import (
            SecurityEventCorrelator,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            correlator = SecurityEventCorrelator(Path(tmpdir))
            correlator.operator_token = "replay_test_token"
            correlator.replay_window_sec = 300

            # First request succeeds
            result1 = correlator.release_containment_authenticated(
                target_type="sender",
                target_id="user1",
                token="replay_test_token",
                nonce="nonce_replay_test",
                requested_by="op1",
                reason="first request",
            )
            assert result1.get("error") != "authentication_failed"
            assert result1.get("error") != "replay_detected"

            # Second request with same nonce fails
            result2 = correlator.release_containment_authenticated(
                target_type="sender",
                target_id="user2",
                token="replay_test_token",
                nonce="nonce_replay_test",  # Same nonce
                requested_by="op1",
                reason="replayed request",
            )
            assert result2["success"] is False
            assert result2["error"] == "replay_detected"

    def test_different_nonces_both_succeed(self):
        """Different nonces allow multiple requests."""
        from modules.ai_intelligence.ai_overseer.src.security_event_correlator import (
            SecurityEventCorrelator,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            correlator = SecurityEventCorrelator(Path(tmpdir))
            correlator.operator_token = "multi_nonce_token"

            result1 = correlator.release_containment_authenticated(
                target_type="sender",
                target_id="user1",
                token="multi_nonce_token",
                nonce="nonce_first",
                requested_by="op1",
                reason="request 1",
            )
            result2 = correlator.release_containment_authenticated(
                target_type="sender",
                target_id="user1",
                token="multi_nonce_token",
                nonce="nonce_second",
                requested_by="op1",
                reason="request 2",
            )

            # Both should not fail on replay (may fail on no containment but not replay)
            assert result1.get("error") != "replay_detected"
            assert result2.get("error") != "replay_detected"

    def test_missing_nonce_rejected(self):
        """Request without nonce is rejected."""
        from modules.ai_intelligence.ai_overseer.src.security_event_correlator import (
            SecurityEventCorrelator,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            correlator = SecurityEventCorrelator(Path(tmpdir))
            correlator.operator_token = "nonce_required_token"

            result = correlator.release_containment_authenticated(
                target_type="sender",
                target_id="user1",
                token="nonce_required_token",
                nonce="",  # Empty nonce
                requested_by="op1",
                reason="missing nonce test",
            )

            assert result["success"] is False
            assert result["error"] == "replay_detected"


class TestAuditPersistence:
    """Tests for audit trail persistence (Tranche 5 Step 2)."""

    def test_audit_record_persisted_to_jsonl(self):
        """Audit records are written to JSONL file."""
        from modules.ai_intelligence.ai_overseer.src.security_event_correlator import (
            SecurityEventCorrelator,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            correlator = SecurityEventCorrelator(Path(tmpdir))
            correlator.operator_token = "audit_jsonl_token"

            correlator.release_containment_authenticated(
                target_type="sender",
                target_id="audit_user",
                token="audit_jsonl_token",
                nonce="audit_nonce_1",
                requested_by="auditor@example.com",
                reason="JSONL audit test",
                source_ip="10.0.0.1",
                session_id="audit_sess",
            )

            # Check JSONL file
            assert correlator.audit_log.exists()
            with open(correlator.audit_log) as f:
                lines = f.readlines()
            assert len(lines) >= 1

            record = json.loads(lines[-1])
            assert record["target_id"] == "audit_user"
            assert record["requested_by"] == "auditor@example.com"
            assert record["source_ip"] == "10.0.0.1"

    def test_audit_record_persisted_to_sqlite(self):
        """Audit records are written to SQLite."""
        from modules.ai_intelligence.ai_overseer.src.security_event_correlator import (
            SecurityEventCorrelator,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            correlator = SecurityEventCorrelator(Path(tmpdir))
            correlator.operator_token = "audit_sqlite_token"

            correlator.release_containment_authenticated(
                target_type="channel",
                target_id="audit_channel",
                token="audit_sqlite_token",
                nonce="audit_nonce_2",
                requested_by="admin",
                reason="SQLite audit test",
            )

            # Retrieve from SQLite
            records = correlator.get_audit_records(limit=10, target_id="audit_channel")
            assert len(records) >= 1
            assert records[0]["target_id"] == "audit_channel"
            assert records[0]["requested_by"] == "admin"

    def test_failed_auth_creates_audit_record(self):
        """Failed authentication attempts are also audited."""
        from modules.ai_intelligence.ai_overseer.src.security_event_correlator import (
            SecurityEventCorrelator,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            correlator = SecurityEventCorrelator(Path(tmpdir))
            correlator.operator_token = "real_token"

            correlator.release_containment_authenticated(
                target_type="sender",
                target_id="hacker_target",
                token="wrong_token",
                nonce="attacker_nonce",
                requested_by="attacker",
                reason="unauthorized attempt",
                source_ip="1.2.3.4",
            )

            records = correlator.get_audit_records(limit=10, target_id="hacker_target")
            assert len(records) >= 1
            assert records[0]["success"] == 0  # False
            assert records[0]["auth_method"] == "token_failed"
            assert records[0]["source_ip"] == "1.2.3.4"


class TestConsistencyCheck:
    """Tests for cross-process consistency check (Tranche 5 Step 3)."""

    def test_consistency_check_detects_stale_entries(self):
        """Consistency check detects expired entries in DB."""
        from modules.ai_intelligence.ai_overseer.src.security_event_correlator import (
            SecurityEventCorrelator, ContainmentState, ContainmentAction,
        )
        import sqlite3

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create correlator and add stale entry directly to DB
            correlator = SecurityEventCorrelator(Path(tmpdir))

            # Insert stale entry directly
            with correlator._containment_conn() as conn:
                conn.execute(
                    """
                    INSERT INTO containment_state
                        (target_type, target_id, action, applied_at, expires_at, reason, incident_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        "sender",
                        "stale_user",
                        "mute_sender",
                        time.time() - 1000,
                        time.time() - 500,  # Already expired
                        "old incident",
                        "INC-STALE",
                    ),
                )
                conn.commit()

            # Create new correlator to trigger consistency check
            correlator2 = SecurityEventCorrelator(Path(tmpdir))

            # Should have detected the stale entry
            assert len(correlator2._consistency_errors) >= 1
            assert any("stale_db_entry" in e for e in correlator2._consistency_errors)

    def test_stats_include_consistency_errors(self):
        """Stats include consistency error count."""
        from modules.ai_intelligence.ai_overseer.src.security_event_correlator import (
            SecurityEventCorrelator,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            correlator = SecurityEventCorrelator(Path(tmpdir))
            stats = correlator.get_stats()

            assert "consistency_errors" in stats
            assert stats["consistency_errors"] == 0  # Fresh DB should be clean


class TestNotificationDedupe:
    """Tests for notification deduplication (Tranche 5 Step 4)."""

    def test_duplicate_notifications_suppressed(self):
        """Duplicate notifications within window are suppressed."""
        from modules.ai_intelligence.ai_overseer.src.security_event_correlator import (
            SecurityEventCorrelator, IncidentSeverity,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            correlator = SecurityEventCorrelator(Path(tmpdir))
            correlator.notification_dedupe_sec = 300

            # First notification sent
            result1 = correlator._dispatch_notification(
                event_type="test_event",
                severity=IncidentSeverity.MEDIUM,
                details={"target_type": "sender", "target_id": "dedupe_test"},
            )
            assert result1 is True

            # Second notification deduped
            result2 = correlator._dispatch_notification(
                event_type="test_event",
                severity=IncidentSeverity.MEDIUM,
                details={"target_type": "sender", "target_id": "dedupe_test"},
            )
            assert result2 is False

    def test_different_targets_not_deduped(self):
        """Notifications for different targets are not deduped."""
        from modules.ai_intelligence.ai_overseer.src.security_event_correlator import (
            SecurityEventCorrelator, IncidentSeverity,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            correlator = SecurityEventCorrelator(Path(tmpdir))
            correlator.notification_dedupe_sec = 300

            result1 = correlator._dispatch_notification(
                event_type="test_event",
                severity=IncidentSeverity.HIGH,
                details={"target_type": "sender", "target_id": "user_a"},
            )
            result2 = correlator._dispatch_notification(
                event_type="test_event",
                severity=IncidentSeverity.HIGH,
                details={"target_type": "sender", "target_id": "user_b"},
            )

            assert result1 is True
            assert result2 is True  # Different target, not deduped

    def test_incident_notification_dispatch(self):
        """Incident notification can be dispatched."""
        from modules.ai_intelligence.ai_overseer.src.security_event_correlator import (
            SecurityEventCorrelator, Incident, IncidentSeverity, ContainmentAction,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            correlator = SecurityEventCorrelator(Path(tmpdir))

            incident = Incident(
                incident_id="INC-NOTIFY01",
                severity=IncidentSeverity.HIGH,
                first_seen=time.time(),
                last_seen=time.time(),
                event_counts={"rate_limited": 5},
                events=[],
                containment=ContainmentAction.MUTE_SENDER,
                policy_trigger="sender_threshold:test",
            )

            result = correlator.dispatch_incident_notification(incident)
            assert result is True


# ---------------------------------------------------------------------------
# Tranche 6: Retention, Token Rotation, Retry Metrics, Abuse Controls
# ---------------------------------------------------------------------------

class TestTokenRotation:
    """Tests for token rotation support."""

    def test_previous_token_is_accepted(self):
        """Previous token can authenticate during rotation window."""
        from modules.ai_intelligence.ai_overseer.src.security_event_correlator import (
            SecurityEventCorrelator, ContainmentAction,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            correlator = SecurityEventCorrelator(Path(tmpdir))
            correlator.operator_token = "token_new"
            correlator.operator_token_previous = "token_old"
            correlator._apply_containment(
                target_type="sender",
                target_id="rot_user",
                action=ContainmentAction.MUTE_SENDER,
                incident_id="INC-ROTATE1",
                now=time.time(),
            )

            result = correlator.release_containment_authenticated(
                target_type="sender",
                target_id="rot_user",
                token="token_old",
                nonce="nonce_rotation_1",
                requested_by="rotator",
                reason="token rotation validation",
            )

            assert result["success"] is True
            records = correlator.get_audit_records(limit=1, target_id="rot_user")
            assert records[0]["auth_method"] == "token_previous"

    def test_warn_when_only_previous_token_set(self, caplog):
        """Startup emits warning if only previous token is configured."""
        from modules.ai_intelligence.ai_overseer.src.security_event_correlator import (
            SecurityEventCorrelator,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict(
                os.environ,
                {
                    "OPENCLAW_OPERATOR_TOKEN": "",
                    "OPENCLAW_OPERATOR_TOKEN_PREVIOUS": "legacy_only",
                },
                clear=False,
            ):
                SecurityEventCorrelator(Path(tmpdir))
            assert "primary_missing_using_previous_only" in caplog.text


class TestRetentionAndPruning:
    """Tests for retention and pruning behavior."""

    def test_prune_old_audit_rows(self):
        """SQLite audit rows older than retention are pruned."""
        from modules.ai_intelligence.ai_overseer.src.security_event_correlator import (
            SecurityEventCorrelator,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            correlator = SecurityEventCorrelator(Path(tmpdir))
            now = time.time()
            correlator.audit_retention_days = 1

            with correlator._containment_conn() as conn:
                conn.execute(
                    """
                    INSERT INTO release_audit
                        (release_id, target_type, target_id, requested_by, reason,
                         source_ip, session_id, timestamp, success, auth_method)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        "REL-OLD0001",
                        "sender",
                        "old_target",
                        "old_op",
                        "old reason",
                        "127.0.0.1",
                        "sess-old",
                        now - 3 * 86400,
                        1,
                        "token",
                    ),
                )
                conn.commit()

            correlator._prune_audit_records(now)
            rows = correlator.get_audit_records(limit=10, target_id="old_target")
            assert rows == []

    def test_prune_used_nonces(self):
        """Old used nonces are pruned from memory and DB."""
        from modules.ai_intelligence.ai_overseer.src.security_event_correlator import (
            SecurityEventCorrelator,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            correlator = SecurityEventCorrelator(Path(tmpdir))
            now = time.time()
            correlator.replay_window_sec = 10
            correlator._used_nonces["old_nonce"] = now - 100

            with correlator._containment_conn() as conn:
                conn.execute(
                    "INSERT INTO used_nonces (nonce, used_at) VALUES (?, ?)",
                    ("old_nonce", now - 100),
                )
                conn.commit()

            correlator._prune_used_nonces(now)
            assert "old_nonce" not in correlator._used_nonces
            with correlator._containment_conn() as conn:
                row = conn.execute(
                    "SELECT nonce FROM used_nonces WHERE nonce = ?",
                    ("old_nonce",),
                ).fetchone()
            assert row is None

    def test_rotate_audit_jsonl(self):
        """JSONL audit file rotates when max size threshold is exceeded."""
        from modules.ai_intelligence.ai_overseer.src.security_event_correlator import (
            SecurityEventCorrelator,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            correlator = SecurityEventCorrelator(Path(tmpdir))
            correlator.audit_jsonl_max_mb = 1
            correlator.audit_jsonl_keep_files = 2

            correlator.audit_log.parent.mkdir(parents=True, exist_ok=True)
            with open(correlator.audit_log, "w", encoding="utf-8") as f:
                f.write("x" * (1024 * 1024 + 16))

            correlator._rotate_audit_jsonl_if_needed()
            rotated = list(correlator.audit_log.parent.glob("openclaw_release_audit_*.jsonl"))
            assert len(rotated) >= 1


class TestNotificationReliability:
    """Tests for Discord retry/backoff and notification metrics."""

    def test_notification_retry_success_updates_metrics(self):
        """Retries should be counted and success metric updated."""
        from modules.ai_intelligence.ai_overseer.src.security_event_correlator import (
            SecurityEventCorrelator, IncidentSeverity,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            correlator = SecurityEventCorrelator(Path(tmpdir))
            correlator.discord_webhook_url = "https://example.invalid/webhook"
            correlator.notification_retry_max = 3
            correlator.notification_retry_backoff_sec = 0

            attempts = {"n": 0}

            def _flaky(*_args, **_kwargs):
                attempts["n"] += 1
                return attempts["n"] >= 3

            with patch.object(correlator, "_send_discord_notification", side_effect=_flaky):
                sent = correlator._dispatch_notification(
                    event_type="retry_test",
                    severity=IncidentSeverity.HIGH,
                    details={"target_type": "sender", "target_id": "retry_user"},
                )

            assert sent is True
            assert correlator._notification_attempts == 1
            assert correlator._notification_retries == 2
            assert correlator._notification_successes == 1
            assert correlator._notification_failures == 0

    def test_notification_retry_failure_updates_metrics(self):
        """Failure after retries should increment failure metrics."""
        from modules.ai_intelligence.ai_overseer.src.security_event_correlator import (
            SecurityEventCorrelator, IncidentSeverity,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            correlator = SecurityEventCorrelator(Path(tmpdir))
            correlator.discord_webhook_url = "https://example.invalid/webhook"
            correlator.notification_retry_max = 2
            correlator.notification_retry_backoff_sec = 0

            with patch.object(correlator, "_send_discord_notification", return_value=False):
                sent = correlator._dispatch_notification(
                    event_type="retry_fail_test",
                    severity=IncidentSeverity.HIGH,
                    details={"target_type": "sender", "target_id": "retry_fail_user"},
                )

            assert sent is False
            assert correlator._notification_attempts == 1
            assert correlator._notification_retries == 1
            assert correlator._notification_successes == 0
            assert correlator._notification_failures == 1


class TestReleaseAbuseControls:
    """Tests for release rate limit and lockout controls."""

    def test_release_rate_limit_blocks_excess_requests(self):
        """Requests above per-operator/session limit are blocked."""
        from modules.ai_intelligence.ai_overseer.src.security_event_correlator import (
            SecurityEventCorrelator,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            correlator = SecurityEventCorrelator(Path(tmpdir))
            correlator.operator_token = "limit_token"
            correlator.release_rate_limit_count = 1
            correlator.release_rate_limit_window_sec = 60
            correlator.auth_failure_threshold = 99

            first = correlator.release_containment_authenticated(
                target_type="sender",
                target_id="user_a",
                token="limit_token",
                nonce="nonce_limit_1",
                requested_by="ops",
                reason="request one",
                session_id="sess-limit",
            )
            second = correlator.release_containment_authenticated(
                target_type="sender",
                target_id="user_b",
                token="limit_token",
                nonce="nonce_limit_2",
                requested_by="ops",
                reason="request two",
                session_id="sess-limit",
            )

            assert first.get("error") != "rate_limited"
            assert second["success"] is False
            assert second["error"] == "rate_limited"

    def test_lockout_after_repeated_auth_failures(self):
        """Repeated auth failures trigger temporary lockout."""
        from modules.ai_intelligence.ai_overseer.src.security_event_correlator import (
            SecurityEventCorrelator,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            correlator = SecurityEventCorrelator(Path(tmpdir))
            correlator.operator_token = "real_token_lockout"
            correlator.auth_failure_threshold = 2
            correlator.auth_lockout_sec = 120
            correlator.release_rate_limit_count = 50

            correlator.release_containment_authenticated(
                target_type="sender",
                target_id="user1",
                token="wrong1",
                nonce="nonce_lock_1",
                requested_by="operator_lock",
                reason="bad token 1",
                session_id="lock-session",
            )
            correlator.release_containment_authenticated(
                target_type="sender",
                target_id="user1",
                token="wrong2",
                nonce="nonce_lock_2",
                requested_by="operator_lock",
                reason="bad token 2",
                session_id="lock-session",
            )

            blocked = correlator.release_containment_authenticated(
                target_type="sender",
                target_id="user1",
                token="real_token_lockout",
                nonce="nonce_lock_3",
                requested_by="operator_lock",
                reason="post-fail attempt",
                session_id="lock-session",
            )

            assert blocked["success"] is False
            assert blocked["error"] == "locked_out"
