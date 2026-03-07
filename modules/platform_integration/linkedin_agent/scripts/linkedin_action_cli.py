#!/usr/bin/env python3
"""
LinkedIn action CLI runner.

Runs individual LinkedIn actions independently (outside menu flows),
and can be invoked by IronClaw/OpenClaw command execution paths.

Examples:
  python -m modules.platform_integration.linkedin_agent.scripts.linkedin_action_cli --action read_feed --max-posts 5
  python -m modules.platform_integration.linkedin_agent.scripts.linkedin_action_cli --action connect --profile-url https://www.linkedin.com/in/name --dry-run
  python -m modules.platform_integration.linkedin_agent.scripts.linkedin_action_cli --action scam_reply --post-index 0 --dry-run true
"""

from __future__ import annotations

import argparse
import asyncio
import json
from typing import Any


def _bool_arg(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


async def _run_action(args: argparse.Namespace) -> dict[str, Any]:
    from modules.infrastructure.browser_actions.src.linkedin_actions import LinkedInActions

    linkedin = LinkedInActions(profile=args.profile)
    try:
        action = args.action

        if action == "navigate_feed":
            result = await linkedin.navigate_to_feed()
            return {"success": bool(result.success), "action": action, "result": result.to_dict()}

        if action == "navigate_profile":
            result = await linkedin.navigate_to_profile(args.profile_url)
            return {"success": bool(result.success), "action": action, "result": result.to_dict()}

        if action == "read_feed":
            posts = await linkedin.read_feed(max_posts=args.max_posts)
            return {
                "success": True,
                "action": action,
                "posts_count": len(posts),
                "posts": [p.to_dict() for p in posts],
            }

        if action == "like_post":
            post_id = args.post_id or f"index_{args.post_index}"
            result = await linkedin.like_post(post_id=post_id, post_index=args.post_index)
            return {"success": bool(result.success), "action": action, "result": result.to_dict()}

        if action == "reply_post":
            post_id = args.post_id or f"index_{args.post_index}"
            if args.dry_run:
                return {
                    "success": True,
                    "action": action,
                    "dry_run": True,
                    "post_id": post_id,
                    "post_index": args.post_index,
                    "reply_text": args.reply_text,
                }
            result = await linkedin.reply_to_post(
                post_id=post_id,
                reply_text=args.reply_text,
                post_index=args.post_index,
            )
            return {"success": bool(result.success), "action": action, "result": result.to_dict()}

        if action == "like_reply":
            post_id = args.post_id or f"index_{args.post_index}"
            result = await linkedin.like_and_reply(
                post_id=post_id,
                reply_text=args.reply_text,
                post_index=args.post_index,
            )
            return {"success": bool(result.success), "action": action, "result": result.to_dict()}

        if action == "scam_reply":
            post_id = args.post_id or f"index_{args.post_index}"
            reply_text = (
                args.reply_text.strip()
                or (
                    "Potentially risky pattern here: third-party setup offer + external link. "
                    "Please verify official OpenClaw/IronClaw channels before granting access. "
                    "Avoid shortened links and unverified remote setup services."
                )
            )
            if args.dry_run:
                return {
                    "success": True,
                    "action": action,
                    "dry_run": True,
                    "post_id": post_id,
                    "post_index": args.post_index,
                    "reply_text": reply_text,
                }
            result = await linkedin.reply_to_post(
                post_id=post_id,
                reply_text=reply_text,
                post_index=args.post_index,
            )
            return {"success": bool(result.success), "action": action, "result": result.to_dict()}

        if action == "engagement_session":
            result = await linkedin.run_engagement_session(
                duration_minutes=args.duration_minutes,
                max_engagements=args.max_engagements,
            )
            return {"success": bool(result.success), "action": action, "result": result.to_dict()}

        if action == "connect":
            result = await linkedin.send_connection_request(
                profile_url=args.profile_url,
                message=args.message,
                profile_name=args.profile_name,
                headline=args.headline,
                company=args.company,
                industry=args.industry,
                dry_run=args.dry_run,
            )
            return {"success": bool(result.success), "action": action, "result": result.to_dict()}

        if action == "digital_twin":
            result = await linkedin.run_digital_twin_flow(
                comment_text=args.comment_text,
                repost_text=args.repost_text,
                schedule_date=args.schedule_date,
                schedule_time=args.schedule_time,
                mentions=[m.strip() for m in (args.mentions or "").split(",") if m.strip()],
                identity_cycle=[i.strip() for i in (args.identity_cycle or "").split(",") if i.strip()],
                dry_run=args.dry_run,
            )
            return {"success": bool(result.success), "action": action, "result": result.to_dict()}

        return {"success": False, "action": action, "error": "unsupported_action"}

    finally:
        linkedin.close()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run individual LinkedIn actions.")
    parser.add_argument(
        "--action",
        required=True,
        choices=[
            "navigate_feed",
            "navigate_profile",
            "read_feed",
            "like_post",
            "reply_post",
            "like_reply",
            "scam_reply",
            "engagement_session",
            "connect",
            "digital_twin",
        ],
    )
    parser.add_argument("--profile", default="linkedin_foundups")
    parser.add_argument("--profile-url", default="")
    parser.add_argument("--post-id", default="")
    parser.add_argument("--post-index", type=int, default=0)
    parser.add_argument("--reply-text", default="")
    parser.add_argument("--max-posts", type=int, default=10)
    parser.add_argument("--duration-minutes", type=int, default=10)
    parser.add_argument("--max-engagements", type=int, default=5)
    parser.add_argument("--message", default=None)
    parser.add_argument("--profile-name", default=None)
    parser.add_argument("--headline", default=None)
    parser.add_argument("--company", default=None)
    parser.add_argument("--industry", default=None)
    parser.add_argument("--dry-run", type=_bool_arg, default=False)
    parser.add_argument("--comment-text", default="")
    parser.add_argument("--repost-text", default="")
    parser.add_argument("--schedule-date", default="")
    parser.add_argument("--schedule-time", default="")
    parser.add_argument("--mentions", default="@foundups")
    parser.add_argument("--identity-cycle", default="")
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    if args.action in {"navigate_profile", "connect"} and not args.profile_url:
        parser.error("--profile-url is required for this action")
    if args.action in {"reply_post", "like_reply"} and not args.reply_text and not args.dry_run:
        parser.error("--reply-text is required for this action")
    if args.action == "digital_twin":
        missing = []
        if not args.comment_text:
            missing.append("--comment-text")
        if not args.repost_text:
            missing.append("--repost-text")
        if not args.schedule_date:
            missing.append("--schedule-date")
        if not args.schedule_time:
            missing.append("--schedule-time")
        if missing:
            parser.error(f"missing required args for digital_twin: {', '.join(missing)}")

    result = asyncio.run(_run_action(args))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result.get("success") else 2


if __name__ == "__main__":
    raise SystemExit(main())
