#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for OpenClaw/IronClaw capability drift audit."""

from pathlib import Path
from unittest.mock import patch

from modules.communication.moltbot_bridge.src import openclaw_capability_audit as audit


PROJECT_ROOT = Path(__file__).resolve().parents[4]


def test_run_daily_audit_returns_expected_sections_without_writing_files():
    fake_runtime = {
        "ok": True,
        "healthy": True,
        "detail": "test_ok",
        "configured_model": "local/qwen-coder-7b",
        "visible_models": ["local/qwen-coder-7b"],
        "configured_model_visible": True,
    }

    with patch.object(audit, "_audit_ironclaw_runtime", return_value=fake_runtime):
        report = audit.run_daily_audit(repo_root=PROJECT_ROOT, write_files=False)

    assert "cli_coverage" in report
    assert "switch_model_drift" in report
    assert "ironclaw_runtime" in report
    assert report["ironclaw_runtime"]["detail"] == "test_ok"
    assert report["artifacts"] == {}


def test_cli_coverage_marks_openclaw_menu_option_as_direct():
    fake_runtime = {
        "ok": True,
        "healthy": True,
        "detail": "test_ok",
        "configured_model": "local/qwen-coder-7b",
        "visible_models": ["local/qwen-coder-7b"],
        "configured_model_visible": True,
    }

    with patch.object(audit, "_audit_ironclaw_runtime", return_value=fake_runtime):
        report = audit.run_daily_audit(repo_root=PROJECT_ROOT, write_files=False)

    entries = report["cli_coverage"]["entries"]
    by_option = {entry["option"]: entry for entry in entries}
    assert "16" in by_option
    assert by_option["16"]["status"] == "direct"
