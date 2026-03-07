"""
LinkedInActions connection policy tests.

Validates pre-click role gating for live Connect actions.
"""

import asyncio
import os
import sys
import unittest
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

from modules.infrastructure.browser_actions.src.linkedin_actions import LinkedInActions  # noqa: E402


@dataclass
class _FakeRoutingResult:
    success: bool
    driver_used: str = "vision"
    action: str = ""
    duration_ms: int = 1
    fallback_used: bool = False
    error: Optional[str] = None
    result_data: Dict[str, Any] = field(default_factory=dict)


class _FakeRouter:
    def __init__(
        self,
        profile_extract: Optional[Dict[str, Any]] = None,
        profile_extract_success: bool = True,
        connect_success: bool = True,
        add_note_success: bool = True,
        send_success: bool = True,
        type_success: bool = True,
    ) -> None:
        self.profile_extract = profile_extract or {}
        self.profile_extract_success = profile_extract_success
        self.connect_success = connect_success
        self.add_note_success = add_note_success
        self.send_success = send_success
        self.type_success = type_success
        self.calls: List[Dict[str, Any]] = []

    async def execute(self, action: str, payload: Dict[str, Any], driver: Any = None):
        self.calls.append({"action": action, "payload": payload, "driver": driver})

        if action == "navigate":
            return _FakeRoutingResult(success=True, action=action, result_data={})

        if action == "find_by_description":
            return _FakeRoutingResult(
                success=self.profile_extract_success,
                action=action,
                result_data=self.profile_extract if self.profile_extract_success else {},
                error=None if self.profile_extract_success else "extract_failed",
            )

        if action == "click_by_description":
            desc = str(payload.get("description", "")).lower()
            if "connect button" in desc:
                return _FakeRoutingResult(success=self.connect_success, action=action)
            if "add a note" in desc:
                return _FakeRoutingResult(success=self.add_note_success, action=action)
            if "invitation note text input field" in desc:
                return _FakeRoutingResult(success=self.type_success, action=action)
            if "send invitation button" in desc:
                return _FakeRoutingResult(success=self.send_success, action=action)
            return _FakeRoutingResult(success=True, action=action)

        return _FakeRoutingResult(success=True, action=action)

    def close(self) -> None:
        return None


class TestLinkedInActionsConnectionPolicy(unittest.TestCase):
    def _run(self, coro):
        return asyncio.run(coro)

    def test_blocks_disallowed_role_before_connect_click(self):
        router = _FakeRouter(
            profile_extract={
                "name": "Jane Doe",
                "headline": "Business Development Director",
                "company": "Acme",
                "industry": "Technology",
            }
        )
        actions = LinkedInActions(router=router)

        result = self._run(
            actions.send_connection_request(
                "https://www.linkedin.com/in/jane-doe/"
            )
        )
        self.assertFalse(result.success)
        self.assertIn("policy_blocked", result.error or "")
        connect_clicks = [
            c
            for c in router.calls
            if c["action"] == "click_by_description"
            and "connect button" in str(c["payload"].get("description", "")).lower()
        ]
        self.assertEqual(len(connect_clicks), 0)

    def test_allows_founder_and_clicks_connect(self):
        router = _FakeRouter()
        actions = LinkedInActions(router=router)

        result = self._run(
            actions.send_connection_request(
                "https://www.linkedin.com/in/gary-phillips/",
                profile_name="Gary Phillips",
                headline="Founder | Architect | Blockchain",
                company="ELOSIA",
                industry="Blockchain",
            )
        )
        self.assertTrue(result.success)
        self.assertEqual(actions.get_session_stats()["connections_sent"], 1)
        connect_clicks = [
            c
            for c in router.calls
            if c["action"] == "click_by_description"
            and "connect button" in str(c["payload"].get("description", "")).lower()
        ]
        self.assertGreaterEqual(len(connect_clicks), 1)

    def test_dry_run_allows_without_clicking_connect(self):
        router = _FakeRouter()
        actions = LinkedInActions(router=router)

        result = self._run(
            actions.send_connection_request(
                "https://www.linkedin.com/in/gary-phillips/",
                profile_name="Gary Phillips",
                headline="Chief Technology Officer",
                dry_run=True,
            )
        )
        self.assertTrue(result.success)
        self.assertTrue(result.details.get("dry_run"))
        connect_clicks = [
            c
            for c in router.calls
            if c["action"] == "click_by_description"
            and "connect button" in str(c["payload"].get("description", "")).lower()
        ]
        self.assertEqual(len(connect_clicks), 0)

    def test_blocks_when_metadata_missing(self):
        router = _FakeRouter(profile_extract_success=False)
        actions = LinkedInActions(router=router)

        result = self._run(
            actions.send_connection_request(
                "https://www.linkedin.com/in/unknown-profile/"
            )
        )
        self.assertFalse(result.success)
        self.assertIn("missing_profile_metadata", result.error or "")


if __name__ == "__main__":
    unittest.main(verbosity=2)
