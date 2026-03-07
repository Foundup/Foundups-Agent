#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for AI Overseer IronClaw runtime monitoring."""

from __future__ import annotations

import asyncio

from modules.ai_intelligence.ai_overseer.src.ai_overseer import AIIntelligenceOverseer


class _StubConfig:
    base_url = "http://127.0.0.1:3000"
    model = "local/qwen-coder-7b"
    auth_token = "token"
    no_api_keys = True


class _StubClientHealthy:
    config = _StubConfig()

    def health(self):
        return True, "healthy"

    def list_models(self):
        return ["local/qwen-coder-7b", "local/qwen3-4b"]


class _StubClientUnhealthy:
    config = _StubConfig()

    def health(self):
        return False, "connection refused"

    def list_models(self):
        return []


def _make_overseer_stub() -> AIIntelligenceOverseer:
    overseer = object.__new__(AIIntelligenceOverseer)
    overseer.ironclaw_runtime_last_status = None
    return overseer


def test_monitor_ironclaw_runtime_success():
    overseer = _make_overseer_stub()
    overseer._create_ironclaw_gateway_client = lambda: _StubClientHealthy()

    status = overseer.monitor_ironclaw_runtime(force=True)

    assert status["success"] is True
    assert status["available"] is True
    assert status["healthy"] is True
    assert status["models_count"] == 2
    assert overseer.get_ironclaw_runtime_status()["healthy"] is True


def test_monitor_ironclaw_runtime_unhealthy():
    overseer = _make_overseer_stub()
    overseer._create_ironclaw_gateway_client = lambda: _StubClientUnhealthy()

    status = overseer.monitor_ironclaw_runtime(force=False)

    assert status["success"] is False
    assert status["available"] is True
    assert status["healthy"] is False


def test_monitor_ironclaw_runtime_client_unavailable():
    overseer = _make_overseer_stub()

    def _raise():
        raise RuntimeError("missing dependency")

    overseer._create_ironclaw_gateway_client = _raise

    status = overseer.monitor_ironclaw_runtime(force=False)

    assert status["success"] is False
    assert status["available"] is False
    assert "unavailable" in status["message"].lower()


def test_handle_telemetry_event_routes_ironclaw_runtime_request():
    overseer = _make_overseer_stub()
    calls = {"count": 0}

    def _monitor(force: bool = False):
        calls["count"] += 1
        return {"success": True, "healthy": True, "force": force}

    overseer.monitor_ironclaw_runtime = _monitor

    async def _run():
        await AIIntelligenceOverseer._handle_telemetry_event(
            overseer,
            {"event": "ironclaw_runtime_status_request", "force": True},
        )

    asyncio.run(_run())
    assert calls["count"] == 1
