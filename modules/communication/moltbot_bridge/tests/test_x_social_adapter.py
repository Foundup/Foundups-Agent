"""
Tests for X social adapter command parsing and routing.
"""

import unittest
from unittest.mock import AsyncMock, patch

from modules.communication.moltbot_bridge.src.x_social_adapter import (
    _parse_action_command,
    handle_x_social_intent,
)


class TestXSocialAdapter(unittest.IsolatedAsyncioTestCase):
    def test_parse_valid_command(self):
        parsed = _parse_action_command(
            'x action post content="foundups: roi -> roc" profile=x_foundups'
        )
        self.assertIsNotNone(parsed)
        action, params = parsed  # type: ignore[misc]
        self.assertEqual(action, "post")
        self.assertEqual(params.get("profile"), "x_foundups")

    def test_parse_alias_command(self):
        parsed = _parse_action_command(
            'twitter action post_tweet content="hello world"'
        )
        self.assertIsNotNone(parsed)
        action, params = parsed  # type: ignore[misc]
        self.assertEqual(action, "post")
        self.assertEqual(params.get("content"), "hello world")

    def test_parse_non_command(self):
        parsed = _parse_action_command("please post this on x")
        self.assertIsNone(parsed)

    async def test_handle_command_success(self):
        mock_result = {"success": True, "action": "post"}
        with patch(
            "modules.communication.moltbot_bridge.src.x_social_adapter.execute_x_action",
            new=AsyncMock(return_value=mock_result),
        ):
            response = await handle_x_social_intent(
                'x action post content="foundups update"',
                sender="@UnDaoDu",
            )
        self.assertIsNotNone(response)
        self.assertIn("X action executed", response or "")
        self.assertIn('"success": true', (response or "").lower())

    async def test_handle_unsupported_action(self):
        response = await handle_x_social_intent(
            "x action unknown_action",
            sender="@UnDaoDu",
        )
        self.assertIsNotNone(response)
        self.assertIn("not recognized", response or "")


if __name__ == "__main__":
    unittest.main(verbosity=2)
