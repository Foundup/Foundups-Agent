#!/usr/bin/env python3
"""Unit tests for Holo system check report wiring."""

from __future__ import annotations

from pathlib import Path

import holo_index.reports.holo_system_check as system_check


def test_run_system_check_includes_wsp_framework_health(monkeypatch, tmp_path: Path) -> None:
    repo_root = tmp_path
    cli_dir = repo_root / "holo_index"
    cli_dir.mkdir(parents=True, exist_ok=True)
    (cli_dir / "cli.py").write_text(
        "parser.add_argument('--foo', action='store_true')\n"
        "if args.foo:\n"
        "    pass\n",
        encoding="utf-8",
    )

    expected_wsp = {
        "available": True,
        "severity": "warning",
        "message": "drift=2 framework_only=1 knowledge_only=0 index_issues=0",
        "drift_count": 2,
        "framework_count": 103,
        "knowledge_count": 101,
        "report_path": "memory/wsp_framework_audit_latest.json",
    }
    monkeypatch.setattr(system_check, "_collect_wsp_framework_health", lambda _repo: expected_wsp)

    report = system_check.run_system_check(
        repo_root,
        checks=[{"flag": "--foo", "arg": "foo", "label": "Foo"}],
    )

    assert report["summary"]["ok"] == 1
    assert report["wsp_framework_health"] == expected_wsp


def test_write_system_check_report_includes_wsp_section(tmp_path: Path) -> None:
    report = {
        "timestamp": "2026-02-11T10:00:00+00:00",
        "mode": "wiring",
        "summary": {"ok": 1, "in_dev": 0, "missing": 0, "unwired": 0},
        "skillz_inventory": {"total": 0, "by_root": {}, "samples": []},
        "wsp_framework_health": {
            "available": True,
            "severity": "warning",
            "message": "drift=1 framework_only=0 knowledge_only=0 index_issues=0",
            "drift_count": 1,
            "framework_count": 103,
            "knowledge_count": 102,
            "report_path": "modules/ai_intelligence/ai_overseer/memory/wsp_framework_audit_latest.json",
        },
        "checks": [],
    }

    out_path = system_check.write_system_check_report(report, tmp_path)
    text = out_path.read_text(encoding="utf-8")

    assert "## WSP Framework Health" in text
    assert "Severity: warning" in text
    assert "Drift Count: 1" in text
