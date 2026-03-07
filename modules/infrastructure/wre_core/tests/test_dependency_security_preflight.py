#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for dependency/CVE startup preflight."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from modules.infrastructure.wre_core.src.dependency_security_preflight import (
    run_dependency_security_preflight,
)


def test_dependency_preflight_passes_with_clean_results(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("OPENCLAW_DEP_SECURITY_MAX_CRITICAL", "0")
    monkeypatch.setenv("OPENCLAW_DEP_SECURITY_MAX_HIGH", "0")
    monkeypatch.setenv("OPENCLAW_DEP_SECURITY_REQUIRE_TOOLS", "1")

    def _fake_run(cmd, timeout_sec=180, cwd=None):
        if "pip_audit" in " ".join(cmd):
            return {"ok": True, "code": 0, "stdout": "[]", "stderr": "", "cmd": cmd}
        return {"ok": True, "code": 0, "stdout": "{}", "stderr": "", "cmd": cmd}

    with patch("modules.infrastructure.wre_core.src.dependency_security_preflight._run", side_effect=_fake_run):
        status = run_dependency_security_preflight(tmp_path, force=True)

    assert status["passed"] is True
    assert status["totals"]["critical"] == 0
    assert status["totals"]["high"] == 0


def test_dependency_preflight_fails_on_high_threshold_breach(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("OPENCLAW_DEP_SECURITY_MAX_CRITICAL", "0")
    monkeypatch.setenv("OPENCLAW_DEP_SECURITY_MAX_HIGH", "0")
    monkeypatch.setenv("OPENCLAW_DEP_SECURITY_REQUIRE_TOOLS", "1")
    # Trigger node check path.
    (tmp_path / "package-lock.json").write_text("{}", encoding="utf-8")

    def _fake_run(cmd, timeout_sec=180, cwd=None):
        cmd_str = " ".join(cmd)
        if "pip_audit" in cmd_str:
            return {"ok": True, "code": 0, "stdout": "[]", "stderr": "", "cmd": cmd}
        if cmd and Path(cmd[0]).name.startswith("npm"):
            stdout = '{"metadata":{"vulnerabilities":{"critical":0,"high":2,"moderate":0,"low":0}}}'
            return {"ok": True, "code": 1, "stdout": stdout, "stderr": "", "cmd": cmd}
        return {"ok": True, "code": 0, "stdout": "{}", "stderr": "", "cmd": cmd}

    with patch("modules.infrastructure.wre_core.src.dependency_security_preflight._run", side_effect=_fake_run):
        status = run_dependency_security_preflight(tmp_path, force=True)

    assert status["passed"] is False
    assert status["totals"]["high"] == 2


def test_dependency_preflight_fails_when_tools_required_and_unavailable(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("OPENCLAW_DEP_SECURITY_REQUIRE_TOOLS", "1")

    with patch(
        "modules.infrastructure.wre_core.src.dependency_security_preflight._run",
        return_value={"ok": False, "code": 127, "stdout": "", "stderr": "missing", "cmd": []},
    ):
        status = run_dependency_security_preflight(tmp_path, force=True)

    assert status["passed"] is False
    assert status["tool_failures"] >= 1


def test_dependency_preflight_scans_all_node_lockfiles(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("OPENCLAW_DEP_SECURITY_MAX_CRITICAL", "0")
    monkeypatch.setenv("OPENCLAW_DEP_SECURITY_MAX_HIGH", "5")
    monkeypatch.setenv("OPENCLAW_DEP_SECURITY_REQUIRE_TOOLS", "1")
    monkeypatch.setenv("OPENCLAW_DEP_SECURITY_NODE_LOCK_SCOPE", "all")

    (tmp_path / "package-lock.json").write_text("{}", encoding="utf-8")
    app = tmp_path / "apps" / "web"
    app.mkdir(parents=True, exist_ok=True)
    (app / "package-lock.json").write_text("{}", encoding="utf-8")

    def _fake_run(cmd, timeout_sec=180, cwd=None):
        cmd_str = " ".join(cmd)
        if "pip_audit" in cmd_str:
            return {"ok": True, "code": 0, "stdout": "[]", "stderr": "", "cmd": cmd}
        if cmd and Path(cmd[0]).name.startswith("npm"):
            if cwd and str(cwd).endswith("apps\\web"):
                stdout = '{"metadata":{"vulnerabilities":{"critical":0,"high":3,"moderate":0,"low":0}}}'
            else:
                stdout = '{"metadata":{"vulnerabilities":{"critical":0,"high":2,"moderate":0,"low":0}}}'
            return {"ok": True, "code": 1, "stdout": stdout, "stderr": "", "cmd": cmd}
        return {"ok": True, "code": 0, "stdout": "{}", "stderr": "", "cmd": cmd}

    with patch("modules.infrastructure.wre_core.src.dependency_security_preflight._run", side_effect=_fake_run):
        status = run_dependency_security_preflight(tmp_path, force=True)

    assert status["node_lock_scope"] == "all"
    assert status["node_lock_count"] == 2
    assert status["totals"]["high"] == 5
    assert status["passed"] is True


def test_dependency_preflight_ignores_hidden_nested_worktree_lockfiles(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("OPENCLAW_DEP_SECURITY_MAX_CRITICAL", "0")
    monkeypatch.setenv("OPENCLAW_DEP_SECURITY_MAX_HIGH", "0")
    monkeypatch.setenv("OPENCLAW_DEP_SECURITY_REQUIRE_TOOLS", "1")
    monkeypatch.setenv("OPENCLAW_DEP_SECURITY_NODE_LOCK_SCOPE", "all")

    (tmp_path / "package-lock.json").write_text("{}", encoding="utf-8")
    hidden = tmp_path / ".feature_clean"
    hidden.mkdir(parents=True, exist_ok=True)
    (hidden / ".git").write_text("gitdir: /tmp/fake\n", encoding="utf-8")
    (hidden / "package-lock.json").write_text("{}", encoding="utf-8")

    def _fake_run(cmd, timeout_sec=180, cwd=None):
        cmd_str = " ".join(cmd)
        if "pip_audit" in cmd_str:
            return {"ok": True, "code": 0, "stdout": "[]", "stderr": "", "cmd": cmd}
        if cmd and Path(cmd[0]).name.startswith("npm"):
            stdout = '{"metadata":{"vulnerabilities":{"critical":0,"high":0,"moderate":0,"low":0}}}'
            return {"ok": True, "code": 0, "stdout": stdout, "stderr": "", "cmd": cmd}
        return {"ok": True, "code": 0, "stdout": "{}", "stderr": "", "cmd": cmd}

    with patch("modules.infrastructure.wre_core.src.dependency_security_preflight._run", side_effect=_fake_run):
        status = run_dependency_security_preflight(tmp_path, force=True)

    assert status["node_lock_scope"] == "all"
    assert status["node_lock_count"] == 1


def test_dependency_preflight_counts_pip_audit_dict_payload_and_unknown_threshold(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("OPENCLAW_DEP_SECURITY_MAX_CRITICAL", "0")
    monkeypatch.setenv("OPENCLAW_DEP_SECURITY_MAX_HIGH", "0")
    monkeypatch.setenv("OPENCLAW_DEP_SECURITY_MAX_UNKNOWN", "0")
    monkeypatch.setenv("OPENCLAW_DEP_SECURITY_REQUIRE_TOOLS", "1")

    def _fake_run(cmd, timeout_sec=180, cwd=None):
        cmd_str = " ".join(cmd)
        if "pip_audit" in cmd_str:
            stdout = (
                '{"dependencies":[{"name":"pkg","version":"1","vulns":[{"id":"CVE-0000-0000"}]}],'
                '"fixes":[]}'
            )
            return {"ok": True, "code": 1, "stdout": stdout, "stderr": "", "cmd": cmd}
        return {"ok": True, "code": 0, "stdout": "{}", "stderr": "", "cmd": cmd}

    with patch("modules.infrastructure.wre_core.src.dependency_security_preflight._run", side_effect=_fake_run):
        status = run_dependency_security_preflight(tmp_path, force=True)

    assert status["totals"]["unknown"] == 1
    assert status["max_unknown"] == 0
    assert status["passed"] is False
