"""
Unit tests for OpenClaw chat backend switch command parsing.
"""

from modules.infrastructure.cli.src.openclaw_chat import _parse_backend_switch_command


def test_parse_backend_switch_command_recognizes_direct_backend_form():
    assert _parse_backend_switch_command("backend ironclaw") == "ironclaw"
    assert _parse_backend_switch_command("backend openclaw") == "openclaw"


def test_parse_backend_switch_command_recognizes_switch_phrase():
    assert _parse_backend_switch_command("switch backend to ironclaw") == "ironclaw"
    assert _parse_backend_switch_command("change to openclaw mode") == "openclaw"


def test_parse_backend_switch_command_ignores_non_backend_queries():
    assert _parse_backend_switch_command("switch model to qwen3") is None
    assert _parse_backend_switch_command("what model are you using") is None
