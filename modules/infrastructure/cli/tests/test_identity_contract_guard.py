"""Regression guard for Claw identity contract.

Contract:
- 012 is the operator/commander identity in runtime I/O.
- 0102 is the agent identity.
"""

from __future__ import annotations

from pathlib import Path
import re


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8", errors="replace")


def test_chat_voice_operator_identity_is_012() -> None:
    chat = _read("modules/infrastructure/cli/src/openclaw_chat.py")
    voice = _read("modules/infrastructure/cli/src/openclaw_voice.py")

    assert "Commander: @012" in chat
    assert 'input("012> ")' in chat
    assert 'sender="@012"' in chat
    assert 'sender="@0102"' not in chat

    assert "Commander: @012" in voice
    assert 'input("012> ")' in voice
    assert 'sender="@012"' in voice
    assert 'sender="@0102"' not in voice


def test_menu_action_sender_identity_is_012() -> None:
    main_menu = _read("modules/infrastructure/cli/src/main_menu.py")
    openclaw_menu = _read("modules/infrastructure/cli/src/openclaw_menu.py")

    assert 'sender="@012"' in main_menu
    assert 'sender="@012"' in openclaw_menu


def test_dae_role_contract_0102_agent_012_operator() -> None:
    dae = _read("modules/communication/moltbot_bridge/src/openclaw_dae.py")

    # Authorized commanders include 012.
    assert re.search(r'AUTHORIZED_COMMANDERS\s*=\s*{[^}]*["\']@?012["\']', dae)

    # Role-lock response must keep 0102/012 distinction.
    assert "I am 0102" in dae
    assert "You are 012" in dae
    assert "operator is always 012" in dae

    # Guard against regression back to prior phrasing.
    assert "Commander identity is @0102" not in dae

