"""
OpenClawDAE social action routing tests.
"""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, patch

from modules.communication.moltbot_bridge.src.openclaw_dae import (
    IntentCategory,
    OpenClawDAE,
    OpenClawIntent,
)


PROJECT_ROOT = Path(__file__).resolve().parents[5]


def _social_intent(message: str) -> OpenClawIntent:
    return OpenClawIntent(
        raw_message=message,
        category=IntentCategory.SOCIAL,
        confidence=0.9,
        sender="@UnDaoDu",
        channel="local_repl",
        session_key="sess_social_adapter",
        is_authorized_commander=True,
        target_domain="communication",
    )


def test_social_route_prefers_campaign_adapter():
    dae = OpenClawDAE(repo_root=PROJECT_ROOT)
    intent = _social_intent(
        'social campaign research_x_to_ln_group content="new research summary"'
    )
    with patch(
        "modules.communication.moltbot_bridge.src.social_campaign_adapter.handle_social_campaign_intent",
        new=AsyncMock(return_value="Social campaign executed for @UnDaoDu"),
    ):
        response = asyncio.run(dae._execute_social(intent))
    assert "Social campaign executed" in response


def test_social_route_uses_linkedin_adapter():
    dae = OpenClawDAE(repo_root=PROJECT_ROOT)
    intent = _social_intent("linkedin action group_post dry_run=true")
    with patch(
        "modules.communication.moltbot_bridge.src.social_campaign_adapter.handle_social_campaign_intent",
        new=AsyncMock(return_value=None),
    ), patch(
        "modules.communication.moltbot_bridge.src.linkedin_social_adapter.handle_linkedin_social_intent",
        new=AsyncMock(return_value="LinkedIn action executed for @UnDaoDu"),
    ):
        response = asyncio.run(dae._execute_social(intent))
    assert "LinkedIn action executed" in response


def test_conversation_route_uses_linkedin_adapter_for_natural_request():
    dae = OpenClawDAE(repo_root=PROJECT_ROOT)
    intent = OpenClawIntent(
        raw_message="0102 go agentic on this LinkedIn post and reply as 0102",
        category=IntentCategory.CONVERSATION,
        confidence=0.9,
        sender="@UnDaoDu",
        channel="local_repl",
        session_key="sess_social_conversation",
        is_authorized_commander=True,
        target_domain="digital_twin",
    )
    with patch(
        "modules.communication.moltbot_bridge.src.linkedin_social_adapter.handle_linkedin_social_intent",
        new=AsyncMock(
            return_value=(
                "LinkedIn action executed for @UnDaoDu:\n"
                "Skill executed: linkedin_agentic_reply\n"
                "{\n"
                '  "success": true,\n'
                '  "action": "reply_post",\n'
                '  "reply_text": "0102 reply preview"\n'
                "}"
            )
        ),
    ):
        response = asyncio.run(dae._try_conversation_social_control(intent))
    assert "LinkedIn action executed" in response
    snapshot = dae.get_identity_snapshot(include_runtime_probe=False)
    assert snapshot["last_social_source"] == "linkedin"
    assert snapshot["last_social_action"] == "reply_post"
    assert snapshot["last_social_skill"] == "linkedin_agentic_reply"
    assert snapshot["last_social_success"] == "true"
    assert "0102 reply preview" in snapshot["last_social_preview"]


def test_social_route_uses_x_adapter_after_linkedin():
    dae = OpenClawDAE(repo_root=PROJECT_ROOT)
    intent = _social_intent('x action post content="foundups update"')
    with patch(
        "modules.communication.moltbot_bridge.src.social_campaign_adapter.handle_social_campaign_intent",
        new=AsyncMock(return_value=None),
    ), patch(
        "modules.communication.moltbot_bridge.src.linkedin_social_adapter.handle_linkedin_social_intent",
        new=AsyncMock(return_value=None),
    ), patch(
        "modules.communication.moltbot_bridge.src.x_social_adapter.handle_x_social_intent",
        new=AsyncMock(return_value="X action executed for @UnDaoDu"),
    ):
        response = asyncio.run(dae._execute_social(intent))
    assert "X action executed" in response


def test_social_route_falls_back_with_tips():
    dae = OpenClawDAE(repo_root=PROJECT_ROOT)
    intent = _social_intent("please handle social")
    with patch(
        "modules.communication.moltbot_bridge.src.social_campaign_adapter.handle_social_campaign_intent",
        new=AsyncMock(return_value=None),
    ), patch(
        "modules.communication.moltbot_bridge.src.linkedin_social_adapter.handle_linkedin_social_intent",
        new=AsyncMock(return_value=None),
    ), patch(
        "modules.communication.moltbot_bridge.src.x_social_adapter.handle_x_social_intent",
        new=AsyncMock(return_value=None),
    ):
        response = asyncio.run(dae._execute_social(intent))
    assert "social campaign" in response
    assert "linkedin action" in response
    assert "x action" in response
