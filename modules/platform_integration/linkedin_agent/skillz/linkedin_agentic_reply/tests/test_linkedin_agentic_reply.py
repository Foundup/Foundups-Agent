#!/usr/bin/env python3
"""Tests for LinkedIn agentic reply skill wrapper."""

import asyncio
from unittest.mock import patch


def test_execute_skill_reply_post_dry_run():
    class _DummyLinkedIn:
        def __init__(self, *args, **kwargs):
            pass

        async def draft_agentic_reply(
            self,
            post_index=0,
            post_context="",
            author="",
            engagement_reason="",
            agent_identity="0102",
            use_selected_post=False,
            read_first=False,
        ):
            return {
                "success": True,
                "reply_text": "0102: embodied loops only compound when memory survives deployment.",
                "post_index": post_index,
                "method": "external_model",
                "use_selected_post": use_selected_post,
                "read_first": read_first,
            }

        def close(self):
            return None

    with patch(
        "modules.infrastructure.browser_actions.src.linkedin_actions.LinkedInActions",
        new=_DummyLinkedIn,
    ):
        from modules.platform_integration.linkedin_agent.skillz.linkedin_agentic_reply import execute_skill

        result = asyncio.run(
            execute_skill(
                action="reply_post",
                params={
                    "post_index": "1",
                    "dry_run": "true",
                    "use_selected_post": "true",
                    "read_first": "true",
                },
            )
        )

    assert result["success"] is True
    assert result["skill"] == "linkedin_agentic_reply"
    assert result["draft"]["use_selected_post"] is True
    assert result["draft"]["read_first"] is True
