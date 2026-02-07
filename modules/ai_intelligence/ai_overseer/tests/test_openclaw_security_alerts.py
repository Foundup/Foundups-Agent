#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for OpenClaw security alert emission and dedupe."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from modules.ai_intelligence.ai_overseer.src.ai_overseer import AIIntelligenceOverseer


def _make_overseer_stub() -> AIIntelligenceOverseer:
    overseer = object.__new__(AIIntelligenceOverseer)
    overseer.openclaw_security_alert_dedupe_sec = 900
    overseer.openclaw_security_alert_history = {}
    overseer.openclaw_incident_alert_dedupe_sec = 900
    overseer.openclaw_incident_alert_history = {}
    overseer.openclaw_security_chat_sender = None
    overseer.openclaw_security_alert_log = None  # Added for correlator integration
    overseer.openclaw_incident_alert_log = None
    overseer.security_correlator = None  # Added for correlator integration
    overseer.push_status = MagicMock(return_value={"discord": True})
    overseer.mcp = None
    return overseer


def _status_fail():
    return {
        "required": True,
        "enforced": True,
        "max_severity": "medium",
        "exit_code": 1,
        "message": "scan failed",
        "checked_at": 123.0,
        "report_path": "report.json",
        "skills_dir": "skills",
    }


def _incident_event():
    return {
        "event": "openclaw_incident_alert",
        "incident_id": "INC-1234ABCD",
        "severity": "high",
        "event_counts": {"permission_denied": 3},
        "first_seen": 100.0,
        "last_seen": 123.0,
        "policy_trigger": "sender_threshold:tester",
        "containment": "mute_sender",
    }


def test_emit_openclaw_security_alert_dedupes_queue_events():
    overseer = _make_overseer_stub()
    overseer.mcp = type("MCP", (), {"event_queue": asyncio.Queue()})()
    overseer._dispatch_openclaw_security_alert = AsyncMock()

    async def _run():
        with patch("modules.ai_intelligence.ai_overseer.src.ai_overseer.MCP_AVAILABLE", True):
            await overseer._emit_openclaw_security_alert(_status_fail(), source="monitor")
            await overseer._emit_openclaw_security_alert(_status_fail(), source="monitor")
        assert overseer.mcp.event_queue.qsize() == 1
        event = await overseer.mcp.event_queue.get()
        assert event["event"] == "openclaw_security_alert"
        assert event["severity"] == "critical"

    asyncio.run(_run())


def test_emit_openclaw_security_alert_fallback_dispatch():
    overseer = _make_overseer_stub()
    overseer.mcp = None
    overseer._dispatch_openclaw_security_alert = AsyncMock()

    async def _run():
        with patch("modules.ai_intelligence.ai_overseer.src.ai_overseer.MCP_AVAILABLE", False):
            await overseer._emit_openclaw_security_alert(_status_fail(), source="monitor")
        overseer._dispatch_openclaw_security_alert.assert_awaited_once()

    asyncio.run(_run())


def test_handle_telemetry_event_routes_openclaw_security_event():
    overseer = _make_overseer_stub()
    overseer._dispatch_openclaw_security_alert = AsyncMock()

    async def _run():
        await overseer._handle_telemetry_event(
            {"event": "openclaw_security_alert", "message": "blocked"}
        )
        overseer._dispatch_openclaw_security_alert.assert_awaited_once()

    asyncio.run(_run())


def test_emit_openclaw_incident_alert_dedupes_queue_events():
    overseer = _make_overseer_stub()
    overseer.mcp = type("MCP", (), {"event_queue": asyncio.Queue()})()
    overseer._dispatch_openclaw_incident_alert = AsyncMock()

    async def _run():
        with patch("modules.ai_intelligence.ai_overseer.src.ai_overseer.MCP_AVAILABLE", True):
            await overseer._emit_openclaw_incident_alert(_incident_event())
            await overseer._emit_openclaw_incident_alert(_incident_event())

        assert overseer.mcp.event_queue.qsize() == 1
        queued = await overseer.mcp.event_queue.get()
        assert queued["event"] == "openclaw_incident_alert"
        assert queued["incident_id"] == "INC-1234ABCD"
        assert queued.get("_dedupe_checked") is True

    asyncio.run(_run())


def test_handle_telemetry_event_routes_openclaw_incident_event():
    overseer = _make_overseer_stub()
    overseer._dispatch_openclaw_incident_alert = AsyncMock()

    async def _run():
        await overseer._handle_telemetry_event(_incident_event())
        overseer._dispatch_openclaw_incident_alert.assert_awaited_once()

    asyncio.run(_run())


def test_handle_telemetry_event_dedupes_external_incident_duplicates():
    overseer = _make_overseer_stub()
    overseer._dispatch_openclaw_incident_alert = AsyncMock()

    async def _run():
        await overseer._handle_telemetry_event(_incident_event())
        await overseer._handle_telemetry_event(_incident_event())
        overseer._dispatch_openclaw_incident_alert.assert_awaited_once()

    asyncio.run(_run())


def test_handle_telemetry_event_correlates_openclaw_security_signals():
    overseer = _make_overseer_stub()
    overseer.ingest_security_event = MagicMock(return_value=None)

    async def _run():
        await overseer._handle_telemetry_event(
            {
                "event": "permission_denied",
                "sender": "agent_01",
                "channel": "discord_live",
                "reason": "source tier denied",
            }
        )

    asyncio.run(_run())
    overseer.ingest_security_event.assert_called_once()
    assert overseer.ingest_security_event.call_args.kwargs["event_type"] == "permission_denied"
    assert overseer.ingest_security_event.call_args.kwargs["sender"] == "agent_01"
    assert overseer.ingest_security_event.call_args.kwargs["channel"] == "discord_live"


def test_release_openclaw_containment_calls_correlator():
    overseer = _make_overseer_stub()
    correlator = MagicMock()
    correlator.release_containment.return_value = True
    overseer.security_correlator = correlator

    result = overseer.release_openclaw_containment(
        target_type="sender",
        target_id="agent_01",
        requested_by="ops",
        reason="manual_clear",
    )
    correlator.release_containment.assert_called_once_with("sender", "agent_01")
    assert result["success"] is True
    assert result["released"] is True


def test_handle_telemetry_event_routes_containment_release():
    overseer = _make_overseer_stub()
    overseer.release_openclaw_containment = MagicMock(return_value={"released": True})

    async def _run():
        await overseer._handle_telemetry_event(
            {
                "event": "openclaw_containment_release",
                "target_type": "sender",
                "target_id": "agent_01",
                "requested_by": "security_admin",
                "reason": "manual_override",
            }
        )

    asyncio.run(_run())
    overseer.release_openclaw_containment.assert_called_once()
    kwargs = overseer.release_openclaw_containment.call_args.kwargs
    assert kwargs["target_type"] == "sender"
    assert kwargs["target_id"] == "agent_01"
