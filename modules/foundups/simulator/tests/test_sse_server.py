"""Unit tests for SSE server components.

Tests event format, sequence IDs, queue bounds, and simulated event generation.
Does NOT require running server - tests class internals directly.

WSP References:
    - WSP 50: Pre-action verification (event deduplication)
    - WSP 5: Test coverage for new code
"""

from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


def test_format_sse_event_structure():
    """SSE event format must include event, id, retry, and data fields."""
    from modules.foundups.simulator.sse_server import format_sse_event

    result = format_sse_event(
        event_type="sim_event",
        data={"event_type": "test", "payload": {}},
        sequence_id=42,
    )

    lines = result.strip().split("\n")
    assert lines[0] == "event: sim_event"
    assert lines[1] == "id: 42"
    assert lines[2].startswith("retry:")
    assert lines[3].startswith("data:")

    # Verify data is valid JSON
    data_line = lines[3].replace("data: ", "")
    parsed = json.loads(data_line)
    assert parsed["event_type"] == "test"


def test_format_sse_event_json_escaping():
    """SSE data field must properly escape special characters."""
    from modules.foundups.simulator.sse_server import format_sse_event

    result = format_sse_event(
        event_type="test",
        data={"message": 'Hello "world"\nwith newline'},
        sequence_id=1,
    )

    data_line = [l for l in result.split("\n") if l.startswith("data:")][0]
    data_json = data_line.replace("data: ", "")
    parsed = json.loads(data_json)
    assert parsed["message"] == 'Hello "world"\nwith newline'


def test_simulated_event_source_sequence_monotonic():
    """SimulatedEventSource must generate monotonically increasing sequence IDs."""
    from modules.foundups.simulator.sse_server import SimulatedEventSource

    source = SimulatedEventSource()
    source._last_event_time = 0  # Force immediate generation

    sequences = []
    for _ in range(10):
        source._last_event_time = 0  # Reset timer each iteration
        event = source.generate_event()
        if event:
            sequences.append(event["sequence_id"])

    # All sequences should be monotonically increasing
    assert sequences == sorted(sequences)
    assert len(set(sequences)) == len(sequences)  # All unique


def test_simulated_event_source_event_types():
    """SimulatedEventSource must generate only allowed event types."""
    from modules.foundups.simulator.sse_server import (
        SimulatedEventSource,
        STREAMABLE_EVENT_TYPES,
    )

    source = SimulatedEventSource()

    event_types_seen = set()
    for _ in range(100):
        source._last_event_time = 0  # Force generation
        event = source.generate_event()
        if event:
            event_types_seen.add(event["event_type"])

    # All generated types must be in STREAMABLE_EVENT_TYPES
    for etype in event_types_seen:
        assert etype in STREAMABLE_EVENT_TYPES, f"Unexpected event type: {etype}"


def test_simulated_event_source_task_state_uses_new_status():
    """task_state_changed events must use 'new_status' key (not 'new_state')."""
    from modules.foundups.simulator.sse_server import SimulatedEventSource

    source = SimulatedEventSource()

    # Generate until we get a task_state_changed
    for _ in range(200):
        source._last_event_time = 0
        event = source.generate_event()
        if event and event["event_type"] == "task_state_changed":
            assert "new_status" in event["payload"], "Missing 'new_status' key"
            assert "new_state" not in event["payload"], "Should not use 'new_state'"
            break
    else:
        pytest.skip("No task_state_changed generated in 200 attempts")


def test_simulated_event_source_required_fields():
    """All simulated events must include required fields."""
    from modules.foundups.simulator.sse_server import SimulatedEventSource

    source = SimulatedEventSource()
    source._last_event_time = 0
    event = source.generate_event()

    assert event is not None
    required_fields = ["event_id", "sequence_id", "event_type", "actor_id", "payload", "timestamp"]
    for field in required_fields:
        assert field in event, f"Missing required field: {field}"


def test_fam_event_source_queue_bounded():
    """FAMEventSource queue must be bounded to prevent memory growth."""
    from modules.foundups.simulator.sse_server import FAMEventSource

    source = FAMEventSource()

    # Queue should have maxsize set
    assert source._event_queue.maxsize == 1000, "Queue must have maxsize=1000"


def test_fam_event_source_filters_non_streamable_events():
    """FAMEventSource must filter out non-streamable event types."""
    from modules.foundups.simulator.sse_server import FAMEventSource, STREAMABLE_EVENT_TYPES

    source = FAMEventSource()

    # Create mock FAMEvent with non-streamable type
    mock_event = MagicMock()
    mock_event.event_type = "heartbeat"  # Not in STREAMABLE_EVENT_TYPES
    mock_event.event_id = "test_123"

    source._on_fam_event(mock_event)

    # Queue should be empty (event was filtered)
    assert source._event_queue.empty()


def test_fam_event_source_accepts_streamable_events():
    """FAMEventSource must accept streamable event types."""
    from modules.foundups.simulator.sse_server import FAMEventSource

    source = FAMEventSource()

    # Create mock FAMEvent with streamable type
    mock_event = MagicMock()
    mock_event.event_type = "task_state_changed"
    mock_event.event_id = "test_456"
    mock_event.actor_id = "agent_001"
    mock_event.foundup_id = "F_1"
    mock_event.task_id = "task_001"
    mock_event.payload = {"new_status": "claimed"}
    mock_event.timestamp = datetime.now(UTC)

    source._on_fam_event(mock_event)

    # Queue should have one event
    assert not source._event_queue.empty()
    queued = source._event_queue.get_nowait()
    assert queued["event_type"] == "task_state_changed"
    assert queued["sequence_id"] == 1


def test_fam_event_source_queue_full_handling():
    """FAMEventSource must drop events when queue is full (no exception)."""
    from modules.foundups.simulator.sse_server import FAMEventSource

    source = FAMEventSource()

    # Create mock FAMEvent
    mock_event = MagicMock()
    mock_event.event_type = "task_state_changed"
    mock_event.event_id = "test_789"
    mock_event.actor_id = "agent_001"
    mock_event.foundup_id = "F_1"
    mock_event.task_id = "task_001"
    mock_event.payload = {"new_status": "claimed"}
    mock_event.timestamp = datetime.now(UTC)

    # Fill queue to capacity
    for i in range(1000):
        mock_event.event_id = f"test_{i}"
        source._on_fam_event(mock_event)

    # One more should NOT raise exception (graceful drop)
    mock_event.event_id = "overflow_event"
    source._on_fam_event(mock_event)  # Should not raise

    # Queue should still be at max
    assert source._event_queue.qsize() == 1000


def test_streamable_event_types_includes_economic_events():
    """STREAMABLE_EVENT_TYPES must include all economic events for earning pulses."""
    from modules.foundups.simulator.sse_server import STREAMABLE_EVENT_TYPES

    economic_events = [
        "payout_triggered",
        "fi_trade_executed",
        "investor_funding_received",
        "mvp_offering_resolved",
        "mvp_bid_submitted",
        "mvp_subscription_accrued",
    ]

    for event in economic_events:
        assert event in STREAMABLE_EVENT_TYPES, f"Missing economic event: {event}"


def test_fam_event_source_observability_properties():
    """FAMEventSource must expose dropped_event_count and queue_size for monitoring."""
    from modules.foundups.simulator.sse_server import FAMEventSource

    source = FAMEventSource()

    # Initial state
    assert source.dropped_event_count == 0
    assert source.queue_size == 0

    # Add some events
    mock_event = MagicMock()
    mock_event.event_type = "task_state_changed"
    mock_event.event_id = "test_obs_1"
    mock_event.actor_id = "agent_001"
    mock_event.foundup_id = "F_1"
    mock_event.task_id = "task_001"
    mock_event.payload = {"new_status": "claimed"}
    mock_event.timestamp = datetime.now(UTC)

    source._on_fam_event(mock_event)
    assert source.queue_size == 1
    assert source.dropped_event_count == 0

    # Fill queue and overflow
    for i in range(1000):
        mock_event.event_id = f"test_obs_{i}"
        source._on_fam_event(mock_event)

    # Should have dropped at least 1 event (queue was at 1, added 1000)
    assert source.dropped_event_count >= 1
    assert source.queue_size == 1000


def _dummy_request(
    host: str = "198.51.100.5",
    headers: dict | None = None,
    query_params: dict | None = None,
):
    return SimpleNamespace(
        headers=headers or {},
        query_params=query_params or {},
        client=SimpleNamespace(host=host),
    )


def test_member_gate_disabled_allows_request(monkeypatch):
    """Member gate disabled should always allow."""
    from modules.foundups.simulator.sse_server import _authorize_member_request

    monkeypatch.setenv("FAM_MEMBER_GATE_ENABLED", "0")
    allowed, reason, role = _authorize_member_request(_dummy_request())

    assert allowed is True
    assert reason == "gate_disabled"
    assert role == "observer_012"


def test_member_gate_denies_without_invite_key(monkeypatch):
    """Member gate enabled should deny when invite key is missing."""
    from modules.foundups.simulator.sse_server import _authorize_member_request

    monkeypatch.setenv("FAM_MEMBER_GATE_ENABLED", "1")
    monkeypatch.setenv("FAM_MEMBER_GATE_ALLOW_LOCAL_BYPASS", "0")
    monkeypatch.setenv("FAM_MEMBER_INVITE_KEY", "secret123")

    allowed, reason, _ = _authorize_member_request(_dummy_request())
    assert allowed is False
    assert reason == "invalid_invite_key"


def test_member_gate_denies_when_misconfigured(monkeypatch):
    """Enabled member gate without configured key must fail closed."""
    from modules.foundups.simulator.sse_server import _authorize_member_request

    monkeypatch.setenv("FAM_MEMBER_GATE_ENABLED", "1")
    monkeypatch.setenv("FAM_MEMBER_GATE_ALLOW_LOCAL_BYPASS", "0")
    monkeypatch.delenv("FAM_MEMBER_INVITE_KEY", raising=False)

    allowed, reason, _ = _authorize_member_request(_dummy_request())
    assert allowed is False
    assert reason == "member_gate_misconfigured"


def test_member_gate_allows_with_valid_key_and_role(monkeypatch):
    """Valid invite key and role should pass gate."""
    from modules.foundups.simulator.sse_server import _authorize_member_request

    monkeypatch.setenv("FAM_MEMBER_GATE_ENABLED", "1")
    monkeypatch.setenv("FAM_MEMBER_GATE_ALLOW_LOCAL_BYPASS", "0")
    monkeypatch.setenv("FAM_MEMBER_INVITE_KEY", "secret123")

    req = _dummy_request(
        headers={"x-invite-key": "secret123", "x-member-role": "agent_trader"},
    )
    allowed, reason, role = _authorize_member_request(req, required_role="member")
    assert allowed is True
    assert reason == "ok"
    assert role == "agent_trader"


def test_member_gate_denies_insufficient_role(monkeypatch):
    """Observer role should be denied for trader-only endpoint."""
    from modules.foundups.simulator.sse_server import _authorize_member_request

    monkeypatch.setenv("FAM_MEMBER_GATE_ENABLED", "1")
    monkeypatch.setenv("FAM_MEMBER_GATE_ALLOW_LOCAL_BYPASS", "0")
    monkeypatch.setenv("FAM_MEMBER_INVITE_KEY", "secret123")

    req = _dummy_request(
        headers={"x-invite-key": "secret123", "x-member-role": "observer_012"},
    )
    allowed, reason, _ = _authorize_member_request(req, required_role="agent_trader")
    assert allowed is False
    assert reason == "insufficient_role"


def test_member_gate_local_bypass(monkeypatch):
    """Localhost can bypass gate when configured."""
    from modules.foundups.simulator.sse_server import _authorize_member_request

    monkeypatch.setenv("FAM_MEMBER_GATE_ENABLED", "1")
    monkeypatch.setenv("FAM_MEMBER_GATE_ALLOW_LOCAL_BYPASS", "1")
    monkeypatch.setenv("FAM_MEMBER_INVITE_KEY", "secret123")

    allowed, reason, role = _authorize_member_request(_dummy_request(host="127.0.0.1"))
    assert allowed is True
    assert reason == "local_bypass"
    assert role == "admin"


def test_streamable_event_types_include_dex_contract_events():
    """DEX contract event types must be streamable to frontend."""
    from modules.foundups.simulator.sse_server import STREAMABLE_EVENT_TYPES

    expected = {
        "order_placed",
        "order_cancelled",
        "order_matched",
        "price_tick",
        "orderbook_snapshot",
        "portfolio_updated",
    }
    assert expected.issubset(STREAMABLE_EVENT_TYPES)


def test_sim_events_endpoint_denies_without_invite_key(monkeypatch):
    """API must return 403 when member gate is enabled and key is missing."""
    from modules.foundups.simulator import sse_server

    monkeypatch.setenv("FAM_MEMBER_GATE_ENABLED", "1")
    monkeypatch.setenv("FAM_MEMBER_GATE_ALLOW_LOCAL_BYPASS", "0")
    monkeypatch.setenv("FAM_MEMBER_INVITE_KEY", "gate-secret")

    client = TestClient(sse_server.app)
    response = client.get("/api/sim-events")
    assert response.status_code == 403
    body = response.json()
    assert body["detail"]["error"] == "member_access_denied"
    assert body["detail"]["reason"] == "invalid_invite_key"


def test_health_endpoint_denies_when_protected(monkeypatch):
    """Health endpoint must be gated when protect_health is enabled."""
    from modules.foundups.simulator import sse_server

    monkeypatch.setenv("FAM_MEMBER_GATE_ENABLED", "1")
    monkeypatch.setenv("FAM_MEMBER_GATE_PROTECT_HEALTH", "1")
    monkeypatch.setenv("FAM_MEMBER_GATE_ALLOW_LOCAL_BYPASS", "0")
    monkeypatch.setenv("FAM_MEMBER_INVITE_KEY", "gate-secret")

    client = TestClient(sse_server.app)
    response = client.get("/api/health")
    assert response.status_code == 403


def test_health_endpoint_allows_with_valid_invite(monkeypatch):
    """Health endpoint should allow valid invite key when protected."""
    from modules.foundups.simulator import sse_server

    monkeypatch.setenv("FAM_MEMBER_GATE_ENABLED", "1")
    monkeypatch.setenv("FAM_MEMBER_GATE_PROTECT_HEALTH", "1")
    monkeypatch.setenv("FAM_MEMBER_GATE_ALLOW_LOCAL_BYPASS", "0")
    monkeypatch.setenv("FAM_MEMBER_INVITE_KEY", "gate-secret")

    client = TestClient(sse_server.app)
    response = client.get("/api/health", headers={"x-invite-key": "gate-secret"})
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
