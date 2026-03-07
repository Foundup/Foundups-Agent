"""
Tests for standalone action CLI routing.
"""

import asyncio
from unittest.mock import AsyncMock, patch

from modules.communication.moltbot_bridge.src.action_cli import (
    _dispatch_adapter_command,
    run_action_command,
)


def test_dispatch_linkedin_command_routes_to_linkedin_adapter():
    with patch(
        "modules.communication.moltbot_bridge.src.linkedin_social_adapter.execute_linkedin_action",
        new=AsyncMock(return_value={"success": True, "action": "read_feed"}),
    ):
        result = asyncio.run(
            _dispatch_adapter_command(
                "linkedin action read_feed max_posts=1",
                sender="@UnDaoDu",
            )
        )
    assert result["success"] is True
    assert result["route"] == "linkedin"
    assert result["action"] == "read_feed"


def test_dispatch_youtube_command_routes_to_youtube_adapter():
    with patch(
        "modules.communication.moltbot_bridge.src.youtube_automation_adapter.execute_youtube_action",
        new=AsyncMock(return_value={"success": True, "action": "comments"}),
    ):
        result = asyncio.run(
            _dispatch_adapter_command(
                "youtube action comments channel=move2japan max_comments=1 dry_run=true",
                sender="@UnDaoDu",
            )
        )
    assert result["success"] is True
    assert result["route"] == "youtube"
    assert result["action"] == "comments"


def test_dispatch_social_campaign_routes_to_campaign_adapter():
    with patch(
        "modules.communication.moltbot_bridge.src.social_campaign_adapter.execute_social_campaign",
        new=AsyncMock(return_value={"success": True, "campaign": "research_x_to_ln_group"}),
    ):
        result = asyncio.run(
            _dispatch_adapter_command(
                'social campaign research_x_to_ln_group content="new research summary"',
                sender="@UnDaoDu",
            )
        )
    assert result["success"] is True
    assert result["route"] == "social_campaign"
    assert result["campaign"] == "research_x_to_ln_group"


def test_dispatch_unmatched_command_returns_helpful_hints():
    result = asyncio.run(_dispatch_adapter_command("do something random", sender="@UnDaoDu"))
    assert result["success"] is False
    assert result["route"] == "unmatched"
    assert "hints" in result


def test_run_action_command_repeat_executes_multiple_iterations():
    with patch(
        "modules.communication.moltbot_bridge.src.action_cli._dispatch_adapter_command",
        new=AsyncMock(return_value={"success": True, "route": "linkedin"}),
    ), patch(
        "modules.communication.moltbot_bridge.src.action_cli._run_adapter_skill_safety_gate",
        return_value=(True, "skills passed safety scan"),
    ):
        result = run_action_command(
            "linkedin action read_feed max_posts=1",
            repeat=2,
            interval_sec=0,
            via_dae=False,
        )
    assert result["success"] is True
    assert result["repeat"] == 2
    assert len(result["results"]) == 2
    assert result["results"][0]["iteration"] == 1
    assert result["results"][1]["iteration"] == 2


def test_run_action_command_invokes_memory_store_per_iteration():
    with patch(
        "modules.communication.moltbot_bridge.src.action_cli._dispatch_adapter_command",
        new=AsyncMock(return_value={"success": True, "route": "linkedin"}),
    ), patch(
        "modules.communication.moltbot_bridge.src.action_cli._run_adapter_skill_safety_gate",
        return_value=(True, "skills passed safety scan"),
    ), patch(
        "modules.communication.moltbot_bridge.src.action_cli._store_action_outcome",
        return_value=True,
    ) as store_mock:
        result = run_action_command(
            "linkedin action read_feed max_posts=1",
            repeat=3,
            interval_sec=0,
            via_dae=False,
        )
    assert result["success"] is True
    assert len(result["results"]) == 3
    assert store_mock.call_count == 3
    assert all(r.get("memory_stored") is True for r in result["results"])


def test_run_action_command_passes_model_target_to_dae():
    with patch(
        "modules.communication.moltbot_bridge.src.action_cli._dispatch_via_dae",
        new=AsyncMock(return_value={"success": True, "route": "dae"}),
    ) as dae_mock:
        result = run_action_command(
            "linkedin action scam_scan_reply dry_run=true",
            via_dae=True,
            backend="openclaw",
            model_target="opus",
        )
    assert result["success"] is True
    dae_mock.assert_awaited()
    assert dae_mock.await_args.kwargs["model_target"] == "opus"


def test_run_action_command_blocks_adapter_when_skill_gate_fails():
    with patch(
        "modules.communication.moltbot_bridge.src.action_cli._run_adapter_skill_safety_gate",
        return_value=(False, "skill scan failed"),
    ):
        result = run_action_command(
            "linkedin action read_feed max_posts=1",
            repeat=1,
            interval_sec=0,
            via_dae=False,
        )
    assert result["success"] is False
    assert result["results"][0]["error"] == "skill_safety_blocked"
