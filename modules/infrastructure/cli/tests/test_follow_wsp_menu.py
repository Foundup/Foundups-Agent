"""Tests for follow-WSP CLI menu wiring."""

from __future__ import annotations

import sys
import types

from modules.infrastructure.cli.src.main_menu import _run_follow_wsp


class _FakeOrchestrator:
    def __init__(self, _repo_root):
        self.result = {
            "success": True,
            "tasks_completed": 2,
            "tasks_failed": 0,
            "wsp00_gate": {
                "gate_passed": True,
                "attempted_awakening": False,
            },
        }

    async def follow_wsp(self, _task: str):
        return self.result

    async def shutdown(self):
        return None


def _install_fake_orchestrator(monkeypatch, orchestrator_cls):
    module_name = "modules.infrastructure.wsp_orchestrator.src.wsp_orchestrator"
    fake_module = types.ModuleType(module_name)
    fake_module.WSPOrchestrator = orchestrator_cls
    monkeypatch.setitem(sys.modules, module_name, fake_module)


def test_follow_wsp_requires_task(capsys):
    _run_follow_wsp("   ")
    out = capsys.readouterr().out
    assert "task is required" in out


def test_follow_wsp_success_path(monkeypatch, capsys):
    _install_fake_orchestrator(monkeypatch, _FakeOrchestrator)

    _run_follow_wsp("check wsp gate")

    out = capsys.readouterr().out
    assert "Gate passed=True" in out
    assert "tasks_completed=2" in out


def test_follow_wsp_blocked_path(monkeypatch, capsys):
    class _BlockedOrchestrator(_FakeOrchestrator):
        def __init__(self, repo_root):
            super().__init__(repo_root)
            self.result = {
                "success": False,
                "tasks_completed": 0,
                "tasks_failed": 1,
                "wsp00_gate": {
                    "gate_passed": False,
                    "attempted_awakening": True,
                    "message": "WSP_00 gate failed after auto-awakening attempt.",
                },
            }

    _install_fake_orchestrator(monkeypatch, _BlockedOrchestrator)

    _run_follow_wsp("check wsp gate")

    out = capsys.readouterr().out
    assert "follow-WSP blocked/failed" in out
    assert "WSP_00 gate failed" in out
