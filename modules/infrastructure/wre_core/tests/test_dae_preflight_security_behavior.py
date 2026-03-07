#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Behavior tests for shared DAE security preflight."""

from __future__ import annotations

from unittest.mock import patch

from modules.infrastructure.wre_core.src.dae_preflight import run_dae_preflight


def test_dae_preflight_blocks_on_security_failure_when_enforced(monkeypatch):
    monkeypatch.setenv("OPENCLAW_SECURITY_PREFLIGHT", "1")
    monkeypatch.setenv("OPENCLAW_SECURITY_PREFLIGHT_ENFORCED", "1")
    monkeypatch.setenv("WRE_DASHBOARD_PREFLIGHT", "0")

    class _Sentinel:
        def __init__(self, repo_root):
            self.repo_root = repo_root

        def check(self, force: bool = False):
            return {"passed": False, "cached": False, "message": "blocked"}

    with patch(
        "modules.ai_intelligence.ai_overseer.src.openclaw_security_sentinel.OpenClawSecuritySentinel",
        _Sentinel,
    ):
        assert run_dae_preflight("unit_test_dae", quiet=True) is False


def test_dae_preflight_allows_security_failure_when_not_enforced(monkeypatch):
    monkeypatch.setenv("OPENCLAW_SECURITY_PREFLIGHT", "1")
    monkeypatch.setenv("OPENCLAW_SECURITY_PREFLIGHT_ENFORCED", "0")
    monkeypatch.setenv("WRE_DASHBOARD_PREFLIGHT", "0")

    class _Sentinel:
        def __init__(self, repo_root):
            self.repo_root = repo_root

        def check(self, force: bool = False):
            return {"passed": False, "cached": True, "message": "warn-only"}

    with patch(
        "modules.ai_intelligence.ai_overseer.src.openclaw_security_sentinel.OpenClawSecuritySentinel",
        _Sentinel,
    ):
        assert run_dae_preflight("unit_test_dae", quiet=True) is True


def test_dae_preflight_24x7_defaults_force_security_rescan(monkeypatch):
    monkeypatch.setenv("OPENCLAW_SECURITY_PREFLIGHT", "1")
    monkeypatch.setenv("OPENCLAW_24X7", "1")
    monkeypatch.delenv("OPENCLAW_SECURITY_PREFLIGHT_FORCE", raising=False)
    monkeypatch.delenv("OPENCLAW_SECURITY_PREFLIGHT_ENFORCED", raising=False)
    monkeypatch.setenv("WRE_DASHBOARD_PREFLIGHT", "0")

    observed = {"force": None}

    class _Sentinel:
        def __init__(self, repo_root):
            self.repo_root = repo_root

        def check(self, force: bool = False):
            observed["force"] = force
            return {"passed": True, "cached": False, "message": "ok"}

    with patch(
        "modules.ai_intelligence.ai_overseer.src.openclaw_security_sentinel.OpenClawSecuritySentinel",
        _Sentinel,
    ):
        assert run_dae_preflight("unit_test_dae", quiet=True) is True
        assert observed["force"] is True

