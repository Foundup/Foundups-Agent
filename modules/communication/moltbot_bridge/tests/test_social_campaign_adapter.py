"""
Tests for social campaign adapter command parsing and routing.
"""

import unittest
from unittest.mock import AsyncMock, patch

from modules.communication.moltbot_bridge.src.social_campaign_adapter import (
    _parse_campaign_command,
    handle_social_campaign_intent,
)


class TestSocialCampaignAdapter(unittest.IsolatedAsyncioTestCase):
    def test_parse_valid_campaign_command(self):
        parsed = _parse_campaign_command(
            'social campaign research_x_to_ln_group content="new research summary"'
        )
        self.assertIsNotNone(parsed)
        campaign, params = parsed  # type: ignore[misc]
        self.assertEqual(campaign, "research_x_to_ln_group")
        self.assertEqual(params.get("content"), "new research summary")

    def test_parse_alias_campaign_command(self):
        parsed = _parse_campaign_command(
            'social campaign research_to_ln content="new research summary"'
        )
        self.assertIsNotNone(parsed)
        campaign, params = parsed  # type: ignore[misc]
        self.assertEqual(campaign, "research_x_to_ln_group")
        self.assertEqual(params.get("content"), "new research summary")

    def test_parse_non_campaign(self):
        parsed = _parse_campaign_command("social action post now")
        self.assertIsNone(parsed)

    async def test_handle_campaign_success(self):
        mock_result = {
            "success": True,
            "campaign": "research_x_to_ln_group",
            "steps": {
                "x_post": {"success": True},
                "linkedin_group_post": {"success": True},
            },
        }
        with patch(
            "modules.communication.moltbot_bridge.src.social_campaign_adapter.execute_social_campaign",
            new=AsyncMock(return_value=mock_result),
        ):
            response = await handle_social_campaign_intent(
                'social campaign research_x_to_ln_group content="new research summary"',
                sender="@UnDaoDu",
            )
        self.assertIsNotNone(response)
        self.assertIn("Social campaign executed", response or "")
        self.assertIn('"success": true', (response or "").lower())

    async def test_handle_unsupported_campaign(self):
        response = await handle_social_campaign_intent(
            "social campaign unknown_campaign content=test",
            sender="@UnDaoDu",
        )
        self.assertIsNotNone(response)
        self.assertIn("not recognized", response or "")


if __name__ == "__main__":
    unittest.main(verbosity=2)
