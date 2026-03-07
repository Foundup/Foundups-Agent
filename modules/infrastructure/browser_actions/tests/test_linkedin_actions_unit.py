"""
Unit tests for individual LinkedInActions behaviors with fake router.
"""

import asyncio
import unittest
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from unittest.mock import patch

from modules.infrastructure.browser_actions.src.linkedin_actions import LinkedInActions


@dataclass
class _FakeRoutingResult:
    success: bool
    driver_used: str = "vision"
    action: str = ""
    duration_ms: int = 1
    fallback_used: bool = False
    error: Optional[str] = None
    result_data: Dict[str, Any] = field(default_factory=dict)


async def _no_sleep(_seconds: float) -> None:
    return None


class _FakeDriver:
    def __init__(self, router: "_FakeRouter") -> None:
        self.router = router

    def execute_script(self, script: str, *args):
        if "Reaction button" in script or "Like button not found in post" in script:
            return {"ok": True, "index": args[0] if args else 0, "already_liked": False, "selector": "Reaction"}

        if "Comment button not found in target post" in script:
            return {"ok": True, "method": "dom", "selector": "button[aria-label*=Comment]", "index": args[0] if args else 0}

        if "Comment input not found" in script:
            return {"ok": True, "method": "contenteditable", "tag": "DIV"}

        if "No active input element" in script:
            return {"ok": True, "method": "execCommand"}

        if "Submit button not found" in script:
            return {"ok": True, "method": "button", "text": "Post"}

        if "const textBoxes = document.querySelectorAll('span[data-testid=\"expandable-text-box\"]');" in script and "engagement_reason" in script:
            index = int(args[0]) if args else 0
            if index >= len(self.router.feed_posts):
                return {"ok": False, "error": "Post not found", "index": index, "found": len(self.router.feed_posts)}
            post = self.router.feed_posts[index]
            content_lower = post["content"].lower()
            is_ai_post = "ai" in content_lower or "autonomous" in content_lower
            return {
                "ok": True,
                "index": index,
                "author": post["author"],
                "author_url": f"https://www.linkedin.com/in/{post['author'].lower().replace(' ', '-')}/",
                "content": post["content"],
                "content_length": len(post["content"]),
                "is_repost": False,
                "repost_info": None,
                "is_ai_post": is_ai_post,
                "is_capital_post": False,
                "is_target_author": False,
                "should_engage": is_ai_post,
                "engagement_reason": "ai_topic" if is_ai_post else "none",
                "matched_keywords": {"ai": ["ai"] if is_ai_post else [], "capital": []},
                "likes": post["likes"],
                "comments": post["comments"],
                "position": {"top": 0, "left": 0, "width": 400, "height": 100},
                "timestamp": "today",
            }

        return {"ok": True}


class _FakeRouter:
    def __init__(self) -> None:
        self.calls: List[Dict[str, Any]] = []
        self.feed_posts = [
            {
                "id": "p1",
                "author": "Founder A",
                "content": "startup ai blockchain update",
                "timestamp": "today",
                "likes": 12,
                "comments": 3,
            },
            {
                "id": "p2",
                "author": "Engineer B",
                "content": "general update",
                "timestamp": "today",
                "likes": 1,
                "comments": 0,
            },
        ]
        self._fake_driver = _FakeDriver(self)

    async def _ensure_selenium(self):
        return self._fake_driver

    async def execute(self, action: str, payload: Dict[str, Any], driver: Any = None):
        self.calls.append({"action": action, "payload": payload, "driver": driver})

        if action == "navigate":
            return _FakeRoutingResult(success=True, action=action)
        if action == "find_by_description":
            desc = str(payload.get("description", "")).lower()
            if "feed posts" in desc:
                return _FakeRoutingResult(
                    success=True,
                    action=action,
                    result_data={"extracted_posts": self.feed_posts},
                )
            if "profile header fields" in desc:
                return _FakeRoutingResult(
                    success=True,
                    action=action,
                    result_data={
                        "name": "Gary Phillips",
                        "headline": "Founder Architect Blockchain",
                        "company": "ELOSIA",
                        "industry": "Blockchain",
                    },
                )
            return _FakeRoutingResult(success=True, action=action, result_data={})
        if action in {"click_by_description", "scroll_to_element"}:
            return _FakeRoutingResult(success=True, action=action)
        return _FakeRoutingResult(success=True, action=action)

    def close(self) -> None:
        return None


class TestLinkedInActionsUnit(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.router = _FakeRouter()
        self.actions = LinkedInActions(router=self.router)

    async def asyncTearDown(self):
        self.actions.close()

    async def test_navigate_to_feed(self):
        with patch(
            "modules.infrastructure.browser_actions.src.linkedin_actions.asyncio.sleep",
            new=_no_sleep,
        ):
            result = await self.actions.navigate_to_feed()
        self.assertTrue(result.success)

    async def test_navigate_to_profile(self):
        result = await self.actions.navigate_to_profile("https://www.linkedin.com/in/test/")
        self.assertTrue(result.success)

    async def test_read_feed(self):
        with patch(
            "modules.infrastructure.browser_actions.src.linkedin_actions.asyncio.sleep",
            new=_no_sleep,
        ):
            posts = await self.actions.read_feed(max_posts=2)
        self.assertEqual(len(posts), 2)
        self.assertTrue(posts[0].is_relevant)

    async def test_like_post(self):
        result = await self.actions.like_post("p1")
        self.assertTrue(result.success)

    async def test_reply_to_post(self):
        with patch(
            "modules.infrastructure.browser_actions.src.linkedin_actions.asyncio.sleep",
            new=_no_sleep,
        ):
            result = await self.actions.reply_to_post("p1", "great post")
        self.assertTrue(result.success)

    async def test_like_and_reply(self):
        with patch(
            "modules.infrastructure.browser_actions.src.linkedin_actions.asyncio.sleep",
            new=_no_sleep,
        ):
            result = await self.actions.like_and_reply("p1", "nice work")
        self.assertTrue(result.success)

    async def test_draft_agentic_reply_fallback_generates_substantive_text(self):
        with patch.object(self.actions, "_ensure_linkedin_comment_drafter", return_value=False):
            draft = await self.actions.draft_agentic_reply(
                post_context=(
                    "I asked Brett Adcock how Helix 02 is different, and it starts with a new "
                    "paradigm: no code learning through experience with full bodily autonomy. "
                    "One robot learns a task and that knowledge propagates across the fleet."
                ),
                author="Dave Blundin",
                engagement_reason="ai_topic",
                agent_identity="0102",
            )

        self.assertTrue(draft["success"])
        self.assertEqual(draft["method"], "wardrobe_fallback")
        self.assertIn("fleet", draft["reply_text"].lower())
        self.assertIn("0102", draft["reply_text"])

    async def test_draft_agentic_reply_prefers_external_model_when_selected(self):
        with patch.object(
            self.actions,
            "_try_external_model_agentic_reply",
            return_value={
                "reply_text": "Useful framing. Fleet learning only compounds when the memory layer survives deployment boundaries.",
                "provider": "anthropic",
                "model": "claude-opus-4-6",
            },
        ), patch.object(self.actions, "_get_preferred_external_target", return_value=("anthropic", "claude-opus-4-6")):
            draft = await self.actions.draft_agentic_reply(
                post_context="One robot learns a task and that knowledge propagates across the fleet.",
                author="Dave Blundin",
                engagement_reason="ai_topic",
                agent_identity="0102",
            )

        self.assertTrue(draft["success"])
        self.assertEqual(draft["method"], "external_model")
        self.assertEqual(draft["external_target"]["provider"], "anthropic")
        self.assertIn("memory layer", draft["reply_text"].lower())

    async def test_draft_agentic_reply_can_read_selected_post(self):
        with patch.object(
            self.actions,
            "read_selected_post_content_dom",
            return_value={
                "content": "Helix 02 learns through real-world embodied loops.",
                "author": "Dave Blundin",
                "engagement_reason": "ai_topic",
            },
        ), patch.object(self.actions, "_ensure_linkedin_comment_drafter", return_value=False):
            draft = await self.actions.draft_agentic_reply(
                use_selected_post=True,
                agent_identity="0102",
            )

        self.assertTrue(draft["success"])
        self.assertTrue(draft["use_selected_post"])
        self.assertEqual(draft["author"], "Dave Blundin")

    async def test_draft_agentic_reply_read_first_prefers_live_dom_over_passed_context(self):
        with patch.object(
            self.actions,
            "read_post_content_dom",
            return_value={
                "content": "Live DOM post about embodied fleet learning.",
                "author": "Live Author",
                "engagement_reason": "ai_topic",
            },
        ), patch.object(self.actions, "_ensure_linkedin_comment_drafter", return_value=False):
            draft = await self.actions.draft_agentic_reply(
                post_index=0,
                post_context="Stale provided context that should be ignored.",
                author="Stale Author",
                read_first=True,
                agent_identity="0102",
            )

        self.assertTrue(draft["success"])
        self.assertTrue(draft["read_first"])
        self.assertEqual(draft["author"], "Live Author")
        self.assertIn("fleet", draft["content_preview"].lower())

    async def test_run_engagement_session(self):
        with patch(
            "modules.infrastructure.browser_actions.src.linkedin_actions.asyncio.sleep",
            new=_no_sleep,
        ):
            result = await self.actions.run_engagement_session(duration_minutes=1, max_engagements=1)
        self.assertTrue(result.success)
        self.assertGreaterEqual(result.engagements, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
