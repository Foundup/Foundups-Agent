#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for AI Overseer OpenClaw security wiring."""

from __future__ import annotations

import asyncio

from modules.ai_intelligence.ai_overseer.src.ai_overseer import AIIntelligenceOverseer


class _SentinelPass:
    def check(self, force: bool = False):
        return {
            "available": True,
            "passed": True,
            "cached": not force,
            "message": "ok",
        }


class _SentinelFail:
    def check(self, force: bool = False):
        return {
            "available": True,
            "passed": False,
            "cached": not force,
            "message": "blocked",
        }


def _make_overseer_stub() -> AIIntelligenceOverseer:
    """Create a minimal overseer instance for unit-level method tests."""
    overseer = object.__new__(AIIntelligenceOverseer)
    overseer.openclaw_security_sentinel = None
    overseer.openclaw_security_monitor_task = None
    overseer.openclaw_security_last_status = None
    return overseer


def test_monitor_openclaw_security_success_sets_last_status():
    overseer = _make_overseer_stub()
    overseer.openclaw_security_sentinel = _SentinelPass()

    result = overseer.monitor_openclaw_security(force=True)

    assert result["success"] is True
    assert result["passed"] is True
    assert overseer.get_openclaw_security_status()["passed"] is True


def test_monitor_openclaw_security_failure_sets_last_status():
    overseer = _make_overseer_stub()
    overseer.openclaw_security_sentinel = _SentinelFail()

    result = overseer.monitor_openclaw_security(force=False)

    assert result["success"] is False
    assert result["passed"] is False
    assert overseer.get_openclaw_security_status()["passed"] is False


def test_monitor_openclaw_security_unavailable():
    overseer = _make_overseer_stub()

    result = overseer.monitor_openclaw_security(force=False)

    assert result["success"] is False
    assert result["available"] is False
    assert "unavailable" in result["message"].lower()


def test_start_and_stop_openclaw_security_monitoring():
    overseer = _make_overseer_stub()
    overseer.openclaw_security_sentinel = _SentinelPass()

    async def _one_shot_loop(interval_sec: float, force_first: bool):
        _ = interval_sec
        _ = force_first
        await asyncio.sleep(0.01)

    overseer._run_openclaw_security_monitor_loop = _one_shot_loop

    async def _run():
        await overseer.start_openclaw_security_monitoring(interval_sec=5, force_first=True)
        assert overseer.openclaw_security_monitor_task is not None
        await asyncio.sleep(0.02)
        await overseer.stop_openclaw_security_monitoring()
        assert overseer.openclaw_security_monitor_task is None

    asyncio.run(_run())

