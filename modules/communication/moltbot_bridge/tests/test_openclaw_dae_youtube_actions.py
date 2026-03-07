"""
OpenClawDAE YouTube action routing tests.
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


def _intent(message: str, category: IntentCategory) -> OpenClawIntent:
    return OpenClawIntent(
        raw_message=message,
        category=category,
        confidence=0.9,
        sender="@UnDaoDu",
        channel="local_repl",
        session_key="sess_yt_adapter",
        is_authorized_commander=True,
        target_domain="youtube_shorts_scheduler"
        if category == IntentCategory.SCHEDULE
        else "auto_moderator_bridge",
    )


def test_schedule_route_prefers_youtube_adapter():
    dae = OpenClawDAE(repo_root=PROJECT_ROOT)
    intent = _intent(
        "youtube action scheduling channel=move2japan max_videos=2 dry_run=true",
        IntentCategory.SCHEDULE,
    )
    with patch(
        "modules.communication.moltbot_bridge.src.youtube_automation_adapter.handle_youtube_automation_intent",
        new=AsyncMock(return_value="YouTube action executed for @UnDaoDu"),
    ):
        response = asyncio.run(dae._execute_schedule(intent))
    assert "YouTube action executed" in response


def test_automation_route_prefers_youtube_adapter():
    dae = OpenClawDAE(repo_root=PROJECT_ROOT)
    intent = _intent(
        "youtube action indexing channel=undaodu batch_size=3",
        IntentCategory.AUTOMATION,
    )
    with patch(
        "modules.communication.moltbot_bridge.src.youtube_automation_adapter.handle_youtube_automation_intent",
        new=AsyncMock(return_value="YouTube action executed for @UnDaoDu"),
    ):
        response = asyncio.run(dae._execute_automation(intent))
    assert "YouTube action executed" in response


def test_automation_falls_back_to_auto_moderator_bridge():
    dae = OpenClawDAE(repo_root=PROJECT_ROOT)
    intent = _intent("show automation status", IntentCategory.AUTOMATION)

    with patch(
        "modules.communication.moltbot_bridge.src.youtube_automation_adapter.handle_youtube_automation_intent",
        new=AsyncMock(return_value=None),
    ), patch(
        "modules.communication.moltbot_bridge.src.auto_moderator_bridge.handle_automation_intent",
        return_value="bridge_status_ok",
    ):
        response = asyncio.run(dae._execute_automation(intent))

    assert response == "bridge_status_ok"

