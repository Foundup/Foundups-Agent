#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for WSP_00 hard gate behavior in follow_wsp orchestration."""

from __future__ import annotations

from pathlib import Path

import modules.infrastructure.wsp_orchestrator.src.wsp_orchestrator as orchestrator_module


class _StubTracker:
    def __init__(self, payload=None, error: Exception | None = None):
        self.payload = payload or {}
        self.error = error
        self.auto_awaken_seen = None

    def run_compliance_gate(self, auto_awaken: bool = False):
        self.auto_awaken_seen = auto_awaken
        if self.error:
            raise self.error
        return self.payload


def _build_orchestrator(monkeypatch, *, strict_gate: bool, tracker):
    monkeypatch.setattr(orchestrator_module, "WORKERS_AVAILABLE", False)
    monkeypatch.setattr(orchestrator_module, "MCP_DIRECT_AVAILABLE", False)
    orchestrator = orchestrator_module.WSPOrchestrator(repo_root=Path("."))
    orchestrator.wsp00_strict_gate = strict_gate
    orchestrator.wsp00_auto_awaken = True
    orchestrator.wsp00_tracker = tracker
    return orchestrator


def test_gate_blocks_when_tracker_missing_in_strict_mode(monkeypatch):
    orchestrator = _build_orchestrator(monkeypatch, strict_gate=True, tracker=None)

    gate = orchestrator._ensure_wsp00_gate()

    assert gate["gate_passed"] is False
    assert gate["tracker_available"] is False
    assert "blocking execution" in gate["message"]


def test_gate_allows_when_tracker_missing_in_non_strict_mode(monkeypatch):
    orchestrator = _build_orchestrator(monkeypatch, strict_gate=False, tracker=None)

    gate = orchestrator._ensure_wsp00_gate()

    assert gate["gate_passed"] is True
    assert gate["tracker_available"] is False
    assert "strict gate is OFF" in gate["message"]


def test_gate_handles_tracker_exceptions_fail_closed(monkeypatch):
    tracker = _StubTracker(error=RuntimeError("boom"))
    orchestrator = _build_orchestrator(monkeypatch, strict_gate=True, tracker=tracker)

    gate = orchestrator._ensure_wsp00_gate()

    assert gate["gate_passed"] is False
    assert gate["error"] == "boom"
    assert "blocking execution" in gate["message"]


def test_gate_uses_tracker_payload(monkeypatch):
    tracker = _StubTracker(
        payload={
            "gate_passed": True,
            "attempted_awakening": True,
            "is_zen_compliant": True,
            "requires_awakening": False,
        }
    )
    orchestrator = _build_orchestrator(monkeypatch, strict_gate=True, tracker=tracker)

    gate = orchestrator._ensure_wsp00_gate()

    assert gate["gate_passed"] is True
    assert gate["attempted_awakening"] is True
    assert tracker.auto_awaken_seen is True

