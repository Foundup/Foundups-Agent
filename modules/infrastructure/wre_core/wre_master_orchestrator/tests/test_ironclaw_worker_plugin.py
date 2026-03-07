#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for WRE IronClaw worker plugin."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from modules.infrastructure.wre_core.wre_master_orchestrator.src.plugins.ironclaw_worker import (
    IronClawWorkerPlugin,
)
from modules.infrastructure.wre_core.wre_master_orchestrator.src.wre_master_orchestrator import (
    WREMasterOrchestrator,
)


class _StubConfig:
    base_url = "http://127.0.0.1:3000"
    model = "local/qwen-coder-7b"
    no_api_keys = True


class _ClientOK:
    config = _StubConfig()

    def health(self):
        return True, "healthy"

    def list_models(self):
        return ["local/qwen-coder-7b"]

    def chat_completion(self, **kwargs):
        _ = kwargs
        return "worker response"


class _ClientUnhealthy:
    config = _StubConfig()

    def health(self):
        return False, "down"

    def list_models(self):
        return []

    def chat_completion(self, **kwargs):
        _ = kwargs
        return ""


def test_execute_success():
    plugin = IronClawWorkerPlugin(repo_root=Path.cwd())

    with patch(
        "modules.communication.moltbot_bridge.src.ironclaw_gateway_client.IronClawGatewayClient",
        _ClientOK,
    ):
        result = plugin.execute(
            {
                "work_type": "sim",
                "input_payload": {"prompt": "hello"},
                "max_tokens": 120,
                "temperature": 0.2,
            }
        )

    assert result["success"] is True
    assert result["plugin"] == "ironclaw_worker"
    assert result["work_type"] == "sim"
    assert "worker response" in result["response"]


def test_execute_respects_require_healthy():
    plugin = IronClawWorkerPlugin(repo_root=Path.cwd())

    with patch(
        "modules.communication.moltbot_bridge.src.ironclaw_gateway_client.IronClawGatewayClient",
        _ClientUnhealthy,
    ):
        result = plugin.execute(
            {
                "work_type": "builder",
                "input_payload": {"goal": "build patch"},
                "require_healthy": True,
            }
        )

    assert result["success"] is False
    assert "unhealthy" in result["error"].lower()


def test_execute_missing_payload_fails_fast():
    plugin = IronClawWorkerPlugin(repo_root=Path.cwd())
    result = plugin.execute({"work_type": "custom", "input_payload": None, "user_message": ""})
    assert result["success"] is False
    assert "missing" in result["error"].lower()


def test_wre_auto_registers_ironclaw_worker(monkeypatch):
    monkeypatch.setenv("WRE_ENABLE_IRONCLAW_WORKER", "1")
    orchestrator = WREMasterOrchestrator()
    assert "ironclaw_worker" in orchestrator.plugins


def test_wre_can_disable_ironclaw_worker_registration(monkeypatch):
    monkeypatch.setenv("WRE_ENABLE_IRONCLAW_WORKER", "0")
    orchestrator = WREMasterOrchestrator()
    assert "ironclaw_worker" not in orchestrator.plugins
