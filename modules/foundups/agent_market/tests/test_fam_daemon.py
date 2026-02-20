"""Tests for FAM DAEmon observability backbone.

Coverage:
1. Schema validation (FAMEvent, FAMEventType)
2. Ordering/sequence guarantees
3. Dedupe/replay protection
4. JSONL+SQLite parity
5. Heartbeat + health endpoint
6. Failure-path coverage

WSP References:
- WSP 91: Observability standards
- WSP 5: Testing standards
"""

import json
import sqlite3
import tempfile
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List
from unittest.mock import MagicMock, patch

import pytest

from modules.foundups.agent_market.src.fam_daemon import (
    FAMDaemon,
    FAMDaemonHealth,
    FAMEvent,
    FAMEventStore,
    FAMEventType,
    _generate_dedupe_key,
    _generate_event_id,
    get_fam_daemon,
)


# ============================================================================
# Schema Validation Tests
# ============================================================================


class TestFAMEventType:
    """Tests for FAMEventType enum."""

    def test_event_types_are_strings(self):
        """All event types have string values."""
        for event_type in FAMEventType:
            assert isinstance(event_type.value, str)
            assert len(event_type.value) > 0

    def test_required_event_types_exist(self):
        """Required event types from spec exist."""
        required = [
            "FOUNDUP_CREATED",
            "TASK_STATE_CHANGED",
            "PROOF_SUBMITTED",
            "VERIFICATION_RECORDED",
            "PAYOUT_TRIGGERED",
            "MILESTONE_PUBLISHED",
            "SECURITY_ALERT_FORWARDED",
            "INCIDENT_ALERT_FORWARDED",
            "HEARTBEAT",
            "DAEMON_STARTED",
            "DAEMON_STOPPED",
        ]
        for name in required:
            assert hasattr(FAMEventType, name), f"Missing event type: {name}"

    def test_event_type_values_are_snake_case(self):
        """Event type values use snake_case convention."""
        for event_type in FAMEventType:
            assert event_type.value.islower()
            assert "_" in event_type.value or event_type.value.isalpha()


class TestFAMEvent:
    """Tests for FAMEvent dataclass."""

    def test_event_creation_with_required_fields(self):
        """FAMEvent can be created with required fields."""
        event = FAMEvent(
            event_id="fam_ev_test123",
            sequence_id=1,
            dedupe_key="test:key",
            event_type="task_state_changed",
            payload={"task_id": "t1", "new_status": "claimed"},
        )

        assert event.event_id == "fam_ev_test123"
        assert event.sequence_id == 1
        assert event.dedupe_key == "test:key"
        assert event.event_type == "task_state_changed"
        assert event.schema_version == "fam_event_v1"
        assert event.actor_id == "system"  # Default

    def test_event_to_dict_serialization(self):
        """FAMEvent serializes to dict correctly."""
        now = datetime.now(timezone.utc)
        event = FAMEvent(
            event_id="fam_ev_test",
            sequence_id=42,
            dedupe_key="test:key",
            event_type="heartbeat",
            actor_id="daemon",
            foundup_id="f1",
            task_id="t1",
            payload={"uptime": 100},
            timestamp=now,
            recorded_at=now,
        )

        result = event.to_dict()

        assert result["event_id"] == "fam_ev_test"
        assert result["sequence_id"] == 42
        assert result["dedupe_key"] == "test:key"
        assert result["event_type"] == "heartbeat"
        assert result["schema_version"] == "fam_event_v1"
        assert result["actor_id"] == "daemon"
        assert result["foundup_id"] == "f1"
        assert result["task_id"] == "t1"
        assert result["payload"]["uptime"] == 100
        assert isinstance(result["timestamp"], str)
        assert isinstance(result["recorded_at"], str)

    def test_event_to_json_roundtrip(self):
        """FAMEvent JSON roundtrip preserves data."""
        event = FAMEvent(
            event_id="fam_ev_test",
            sequence_id=1,
            dedupe_key="test:key",
            event_type="foundup_created",
            payload={"name": "Test Foundup"},
        )

        json_str = event.to_json()
        data = json.loads(json_str)
        restored = FAMEvent.from_dict(data)

        assert restored.event_id == event.event_id
        assert restored.sequence_id == event.sequence_id
        assert restored.dedupe_key == event.dedupe_key
        assert restored.event_type == event.event_type
        assert restored.payload == event.payload

    def test_event_from_dict_with_defaults(self):
        """FAMEvent.from_dict handles missing optional fields."""
        data = {
            "event_id": "fam_ev_test",
            "sequence_id": 1,
            "dedupe_key": "test:key",
            "event_type": "heartbeat",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "recorded_at": datetime.now(timezone.utc).isoformat(),
        }

        event = FAMEvent.from_dict(data)

        assert event.schema_version == "fam_event_v1"
        assert event.actor_id == "system"
        assert event.foundup_id is None
        assert event.task_id is None
        assert event.payload == {}


class TestDeterministicIds:
    """Tests for deterministic ID generation."""

    def test_event_id_is_deterministic(self):
        """Same inputs produce same event ID."""
        id1 = _generate_event_id("heartbeat", "abc123", "2026-02-08T12:00:00")
        id2 = _generate_event_id("heartbeat", "abc123", "2026-02-08T12:00:00")

        assert id1 == id2
        assert id1.startswith("fam_ev_")

    def test_event_id_differs_on_input_change(self):
        """Different inputs produce different event IDs."""
        id1 = _generate_event_id("heartbeat", "abc123", "2026-02-08T12:00:00")
        id2 = _generate_event_id("heartbeat", "abc456", "2026-02-08T12:00:00")
        id3 = _generate_event_id("payout", "abc123", "2026-02-08T12:00:00")

        assert id1 != id2
        assert id1 != id3
        assert id2 != id3

    def test_dedupe_key_task_state_changed(self):
        """Dedupe key for task_state_changed includes task_id and new_status."""
        key = _generate_dedupe_key(
            "task_state_changed",
            {"task_id": "t1", "new_status": "claimed"},
        )

        assert key == "task:t1:claimed"

    def test_dedupe_key_proof_submitted(self):
        """Dedupe key for proof_submitted includes proof_id."""
        key = _generate_dedupe_key(
            "proof_submitted",
            {"proof_id": "p1"},
        )

        assert key == "proof:p1"

    def test_dedupe_key_heartbeat(self):
        """Dedupe key for heartbeat includes timestamp truncated to second."""
        key = _generate_dedupe_key(
            "heartbeat",
            {"timestamp": "2026-02-08T12:00:00.123456"},
        )

        assert key == "heartbeat:2026-02-08T12:00:00"

    def test_dedupe_key_default_uses_hash(self):
        """Dedupe key for unknown types uses payload hash."""
        key = _generate_dedupe_key(
            "custom_event",
            {"data": "test"},
        )

        assert key.startswith("custom_event:")
        assert len(key) > len("custom_event:")


# ============================================================================
# Event Store Tests
# ============================================================================


class TestFAMEventStore:
    """Tests for FAMEventStore persistence layer."""

    @pytest.fixture
    def temp_store(self, tmp_path):
        """Create a temporary event store."""
        return FAMEventStore(tmp_path)

    def test_store_initialization(self, temp_store):
        """Event store initializes with empty state."""
        stats = temp_store.get_stats()

        assert stats["total_events"] == 0
        assert stats["max_sequence_id"] == 0
        assert stats["events_by_type"] == {}

    def test_write_event_success(self, temp_store):
        """Write event to store succeeds."""
        event = FAMEvent(
            event_id="fam_ev_test1",
            sequence_id=0,  # Will be assigned
            dedupe_key="test:1",
            event_type="heartbeat",
            payload={"heartbeat_number": 1},
        )

        success, message = temp_store.write(event)

        assert success is True
        assert message == "ok"
        assert event.sequence_id == 1  # Assigned

    def test_sequence_ids_are_monotonic(self, temp_store):
        """Sequence IDs are monotonically increasing."""
        sequence_ids = []

        for i in range(10):
            event = FAMEvent(
                event_id=f"fam_ev_test{i}",
                sequence_id=0,
                dedupe_key=f"test:{i}",
                event_type="heartbeat",
                payload={"n": i},
            )
            temp_store.write(event)
            sequence_ids.append(event.sequence_id)

        # Verify monotonic
        for i in range(1, len(sequence_ids)):
            assert sequence_ids[i] > sequence_ids[i - 1]

        # Verify no gaps
        assert sequence_ids == list(range(1, 11))

    def test_dedupe_rejects_duplicate(self, temp_store):
        """Duplicate dedupe key is rejected."""
        event1 = FAMEvent(
            event_id="fam_ev_test1",
            sequence_id=0,
            dedupe_key="unique:key",
            event_type="heartbeat",
            payload={},
        )
        event2 = FAMEvent(
            event_id="fam_ev_test2",
            sequence_id=0,
            dedupe_key="unique:key",  # Same dedupe key
            event_type="heartbeat",
            payload={},
        )

        success1, _ = temp_store.write(event1)
        success2, message2 = temp_store.write(event2)

        assert success1 is True
        assert success2 is False
        assert "duplicate" in message2

    def test_replay_protection(self, temp_store):
        """Replaying same events does not create duplicates."""
        events = [
            FAMEvent(
                event_id=f"fam_ev_test{i}",
                sequence_id=0,
                dedupe_key=f"key:{i}",
                event_type="heartbeat",
                payload={"n": i},
            )
            for i in range(5)
        ]

        # First write
        for event in events:
            temp_store.write(event)

        # Attempt replay
        for event in events:
            success, message = temp_store.write(event)
            assert success is False
            assert "duplicate" in message

        # Count should still be 5
        stats = temp_store.get_stats()
        assert stats["total_events"] == 5

    def test_query_by_event_type(self, temp_store):
        """Query filters by event type."""
        # Write mixed events
        for i in range(3):
            temp_store.write(FAMEvent(
                event_id=f"hb_{i}",
                sequence_id=0,
                dedupe_key=f"hb:{i}",
                event_type="heartbeat",
                payload={},
            ))
        for i in range(2):
            temp_store.write(FAMEvent(
                event_id=f"ts_{i}",
                sequence_id=0,
                dedupe_key=f"ts:{i}",
                event_type="task_state_changed",
                payload={},
            ))

        heartbeats = temp_store.query(event_type="heartbeat")
        task_changes = temp_store.query(event_type="task_state_changed")

        assert len(heartbeats) == 3
        assert len(task_changes) == 2

    def test_query_by_foundup_id(self, temp_store):
        """Query filters by foundup_id."""
        temp_store.write(FAMEvent(
            event_id="ev1",
            sequence_id=0,
            dedupe_key="f1:1",
            event_type="task_state_changed",
            foundup_id="f_alpha",
            payload={},
        ))
        temp_store.write(FAMEvent(
            event_id="ev2",
            sequence_id=0,
            dedupe_key="f2:1",
            event_type="task_state_changed",
            foundup_id="f_beta",
            payload={},
        ))
        temp_store.write(FAMEvent(
            event_id="ev3",
            sequence_id=0,
            dedupe_key="f1:2",
            event_type="payout_triggered",
            foundup_id="f_alpha",
            payload={},
        ))

        alpha_events = temp_store.query(foundup_id="f_alpha")

        assert len(alpha_events) == 2
        assert all(e.foundup_id == "f_alpha" for e in alpha_events)

    def test_query_since_sequence(self, temp_store):
        """Query returns events after sequence ID."""
        for i in range(10):
            temp_store.write(FAMEvent(
                event_id=f"ev{i}",
                sequence_id=0,
                dedupe_key=f"key:{i}",
                event_type="heartbeat",
                payload={},
            ))

        events = temp_store.query(since_sequence=5)

        assert len(events) == 5
        assert events[0].sequence_id == 6
        assert events[-1].sequence_id == 10

    def test_query_limit(self, temp_store):
        """Query respects limit parameter."""
        for i in range(20):
            temp_store.write(FAMEvent(
                event_id=f"ev{i}",
                sequence_id=0,
                dedupe_key=f"key:{i}",
                event_type="heartbeat",
                payload={},
            ))

        events = temp_store.query(limit=5)

        assert len(events) == 5


class TestJSONLSQLiteParity:
    """Tests for JSONL+SQLite parity verification."""

    @pytest.fixture
    def temp_store(self, tmp_path):
        """Create a temporary event store."""
        return FAMEventStore(tmp_path)

    def test_parity_ok_on_empty_store(self, temp_store):
        """Parity check passes on empty store."""
        ok, message = temp_store.verify_parity()

        assert ok is True
        assert "0 events" in message

    def test_parity_ok_after_writes(self, temp_store):
        """Parity check passes after normal writes."""
        for i in range(10):
            temp_store.write(FAMEvent(
                event_id=f"ev{i}",
                sequence_id=0,
                dedupe_key=f"key:{i}",
                event_type="heartbeat",
                payload={},
            ))

        ok, message = temp_store.verify_parity()

        assert ok is True
        assert "10 events" in message

    def test_parity_detects_jsonl_extra(self, tmp_path):
        """Parity check detects extra lines in JSONL."""
        store = FAMEventStore(tmp_path)

        # Write one event
        store.write(FAMEvent(
            event_id="ev1",
            sequence_id=0,
            dedupe_key="key:1",
            event_type="heartbeat",
            payload={},
        ))

        # Manually append to JSONL (simulating corruption)
        jsonl_path = tmp_path / "fam_events.jsonl"
        with open(jsonl_path, "a") as f:
            f.write('{"extra": "line"}\n')

        ok, message = store.verify_parity()

        assert ok is False
        assert "mismatch" in message

    def test_dual_write_creates_both_files(self, tmp_path):
        """Writing events creates both JSONL and SQLite files."""
        store = FAMEventStore(tmp_path)

        store.write(FAMEvent(
            event_id="ev1",
            sequence_id=0,
            dedupe_key="key:1",
            event_type="heartbeat",
            payload={},
        ))

        assert (tmp_path / "fam_events.jsonl").exists()
        assert (tmp_path / "fam_audit.db").exists()


# ============================================================================
# FAMDaemon Tests
# ============================================================================


class TestFAMDaemon:
    """Tests for FAMDaemon runtime."""

    @pytest.fixture
    def daemon(self, tmp_path):
        """Create a daemon with temp storage."""
        d = FAMDaemon(
            data_dir=tmp_path,
            heartbeat_interval_sec=0.1,  # Fast for testing
            auto_start=False,
        )
        yield d
        # Cleanup
        if d._running:
            d.stop()

    def test_daemon_start_emits_event(self, daemon):
        """Starting daemon emits DAEMON_STARTED event."""
        daemon.start()

        events = daemon.query_events(event_type="daemon_started")

        assert len(events) == 1
        assert events[0].event_type == "daemon_started"
        assert "heartbeat_interval_sec" in events[0].payload

    def test_daemon_stop_emits_event(self, daemon):
        """Stopping daemon emits DAEMON_STOPPED event."""
        daemon.start()
        time.sleep(0.05)
        daemon.stop()

        events = daemon.query_events(event_type="daemon_stopped")

        assert len(events) == 1
        assert events[0].event_type == "daemon_stopped"
        assert "uptime_seconds" in events[0].payload

    def test_heartbeat_loop(self, daemon):
        """Heartbeat loop emits heartbeat events."""
        daemon.start()

        # Wait for a few heartbeats
        time.sleep(0.35)

        daemon.stop()

        events = daemon.query_events(event_type="heartbeat")

        # Should have at least 2 heartbeats in 0.35s with 0.1s interval
        assert len(events) >= 2

    def test_emit_custom_event(self, daemon):
        """emit() writes custom events."""
        success, message = daemon.emit(
            event_type=FAMEventType.TASK_STATE_CHANGED,
            payload={"task_id": "t1", "new_status": "claimed"},
            actor_id="agent_1",
            foundup_id="f_test",
            task_id="t1",
        )

        assert success is True

        events = daemon.query_events(event_type="task_state_changed")
        assert len(events) == 1
        assert events[0].actor_id == "agent_1"
        assert events[0].foundup_id == "f_test"
        assert events[0].task_id == "t1"

    def test_emit_with_string_event_type(self, daemon):
        """emit() accepts string event type."""
        success, _ = daemon.emit(
            event_type="custom_type",
            payload={"key": "value"},
        )

        assert success is True
        events = daemon.query_events(event_type="custom_type")
        assert len(events) == 1

    def test_event_listeners(self, daemon):
        """Event listeners are notified on emit."""
        received_events: List[FAMEvent] = []

        def listener(event: FAMEvent):
            received_events.append(event)

        daemon.add_listener(listener)
        daemon.emit(FAMEventType.HEARTBEAT, {"n": 1})
        daemon.emit(FAMEventType.HEARTBEAT, {"n": 2})

        assert len(received_events) == 2

        daemon.remove_listener(listener)
        daemon.emit(FAMEventType.HEARTBEAT, {"n": 3})

        assert len(received_events) == 2  # Listener removed

    def test_listener_error_does_not_block(self, daemon):
        """Listener errors do not block event emission."""
        def bad_listener(event: FAMEvent):
            raise ValueError("Listener error")

        daemon.add_listener(bad_listener)

        # Should not raise
        success, _ = daemon.emit(FAMEventType.HEARTBEAT, {"n": 1})

        assert success is True


class TestFAMDaemonHealth:
    """Tests for FAMDaemon health/status API."""

    @pytest.fixture
    def daemon(self, tmp_path):
        """Create a daemon with temp storage."""
        d = FAMDaemon(
            data_dir=tmp_path,
            heartbeat_interval_sec=0.1,
            auto_start=False,
        )
        yield d
        if d._running:
            d.stop()

    def test_health_before_start(self, daemon):
        """get_health() returns valid status before start."""
        health = daemon.get_health()

        assert health.running is False
        assert health.uptime_seconds == 0.0
        assert health.heartbeat_count == 0
        assert health.last_heartbeat is None
        assert health.parity_ok is True

    def test_health_after_start(self, daemon):
        """get_health() returns running status after start."""
        daemon.start()
        time.sleep(0.15)

        health = daemon.get_health()

        assert health.running is True
        assert health.uptime_seconds > 0
        assert health.heartbeat_count >= 1
        assert health.last_heartbeat is not None

    def test_health_includes_event_stats(self, daemon):
        """Health includes event store statistics."""
        daemon.emit(FAMEventType.TASK_STATE_CHANGED, {"task_id": "t1", "new_status": "open"})
        daemon.emit(FAMEventType.TASK_STATE_CHANGED, {"task_id": "t2", "new_status": "claimed"})

        health = daemon.get_health()

        assert health.event_store_stats["total_events"] == 2
        assert "task_state_changed" in health.event_store_stats["events_by_type"]

    def test_health_to_dict(self, daemon):
        """FAMDaemonHealth serializes to dict."""
        health = daemon.get_health()
        data = health.to_dict()

        assert isinstance(data, dict)
        assert "running" in data
        assert "uptime_seconds" in data
        assert "heartbeat_count" in data
        assert "event_store_stats" in data
        assert "parity_ok" in data

    def test_get_status_alias(self, daemon):
        """get_status() is an alias for get_health().to_dict()."""
        status = daemon.get_status()

        assert isinstance(status, dict)
        assert "running" in status


class TestFAMDaemonErrors:
    """Tests for FAMDaemon error handling."""

    @pytest.fixture
    def daemon(self, tmp_path):
        """Create a daemon with temp storage."""
        d = FAMDaemon(
            data_dir=tmp_path,
            heartbeat_interval_sec=0.5,
            auto_start=False,
        )
        yield d
        if d._running:
            d.stop()

    def test_double_start_is_idempotent(self, daemon):
        """Calling start() twice does not create duplicate threads."""
        daemon.start()
        thread1 = daemon._heartbeat_thread

        daemon.start()  # Second call
        thread2 = daemon._heartbeat_thread

        assert thread1 is thread2

    def test_double_stop_is_idempotent(self, daemon):
        """Calling stop() twice is safe."""
        daemon.start()
        daemon.stop()
        daemon.stop()  # Should not raise

        assert daemon._running is False

    def test_emit_duplicate_returns_false(self, daemon):
        """Emitting duplicate event returns False."""
        # Same dedupe key
        daemon.emit(
            FAMEventType.TASK_STATE_CHANGED,
            {"task_id": "t1", "new_status": "claimed"},
        )

        success, message = daemon.emit(
            FAMEventType.TASK_STATE_CHANGED,
            {"task_id": "t1", "new_status": "claimed"},  # Same
        )

        assert success is False
        assert "duplicate" in message


class TestModuleSingleton:
    """Tests for module-level singleton."""

    def test_get_fam_daemon_returns_singleton(self, tmp_path):
        """get_fam_daemon returns the same instance."""
        # Reset global
        import modules.foundups.agent_market.src.fam_daemon as fam_module
        fam_module._daemon = None

        daemon1 = get_fam_daemon(data_dir=tmp_path, auto_start=False)
        daemon2 = get_fam_daemon(data_dir=tmp_path, auto_start=False)

        assert daemon1 is daemon2

        # Cleanup
        if daemon1._running:
            daemon1.stop()
        fam_module._daemon = None


# ============================================================================
# Thread Safety Tests
# ============================================================================


class TestThreadSafety:
    """Tests for thread safety of event store."""

    def test_concurrent_writes(self, tmp_path):
        """Concurrent writes do not corrupt sequence IDs."""
        store = FAMEventStore(tmp_path)
        errors = []
        written_ids = []
        lock = threading.Lock()

        def writer(start_id: int, count: int):
            for i in range(count):
                event = FAMEvent(
                    event_id=f"ev_{start_id}_{i}",
                    sequence_id=0,
                    dedupe_key=f"key:{start_id}:{i}",
                    event_type="heartbeat",
                    payload={},
                )
                try:
                    success, _ = store.write(event)
                    if success:
                        with lock:
                            written_ids.append(event.sequence_id)
                except Exception as e:
                    with lock:
                        errors.append(str(e))

        threads = [
            threading.Thread(target=writer, args=(i * 100, 50))
            for i in range(4)
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(written_ids) == 200

        # All sequence IDs should be unique
        assert len(set(written_ids)) == 200

        # Sequence IDs should be 1-200 (no gaps)
        assert sorted(written_ids) == list(range(1, 201))
