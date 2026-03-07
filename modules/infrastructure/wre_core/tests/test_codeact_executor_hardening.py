#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hardening tests for CodeAct executor safety policy."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from modules.infrastructure.wre_core.src.codeact_executor import (
    CodeActExecutor,
    SafetyGates,
)


def test_require_allowlist_blocks_when_empty():
    gates = SafetyGates(
        allowed_commands=[],
        blocked_patterns=[],
        require_allowlist=True,
    )
    assert gates.is_command_allowed("git status") is False


def test_shell_execution_uses_shell_false():
    executor = CodeActExecutor(repo_root=Path("."))
    skill = {
        "format": "codeact",
        "code_section": {
            "main_action": {"type": "shell", "command": "python --version", "capture": "out"}
        },
        "safety_gates": {
            "allowed_commands": ["python *"],
            "require_allowlist": True,
            "forbid_shell_metacharacters": True,
        },
    }

    with patch("modules.infrastructure.wre_core.src.codeact_executor.subprocess.run") as mock_run:
        class _Result:
            returncode = 0
            stdout = "Python 3.x"
            stderr = ""

        mock_run.return_value = _Result()
        result = executor.execute(skill, {})

    assert result.success is True
    assert mock_run.call_count == 1
    _, kwargs = mock_run.call_args
    assert kwargs.get("shell") is False


def test_metacharacter_policy_blocks_command():
    executor = CodeActExecutor(repo_root=Path("."))
    skill = {
        "format": "codeact",
        "code_section": {
            "main_action": {"type": "shell", "command": "python --version && whoami", "capture": "out"}
        },
        "safety_gates": {
            "allowed_commands": ["python *"],
            "require_allowlist": True,
            "forbid_shell_metacharacters": True,
        },
    }

    result = executor.execute(skill, {})
    assert result.success is False
    assert "metacharacter policy" in (result.error or "").lower()

