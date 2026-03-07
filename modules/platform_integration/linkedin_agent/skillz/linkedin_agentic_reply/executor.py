#!/usr/bin/env python3
"""
LinkedIn agentic reply skill executor.

Provides a WSP/WRE-aligned runtime wrapper around LinkedIn agentic reply actions.
"""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any, Dict, Optional


def _truthy(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


def _safe_int(value: str, default: int = 0) -> int:
    try:
        return int(str(value).strip())
    except Exception:
        return default


def _to_jsonable(value: Any) -> Any:
    if value is None:
        return None
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, list):
        return [_to_jsonable(v) for v in value]
    if isinstance(value, dict):
        return {k: _to_jsonable(v) for k, v in value.items()}
    return value


def _build_scam_callout_reply(params: Dict[str, str]) -> str:
    risk_reason = params.get("risk_reason", "").strip()
    suspicious_link = params.get("suspicious_link", params.get("link", "")).strip()
    opening = params.get("opening", "Potentially risky pattern here").strip()

    parts = [
        f"{opening}: third-party setup offer + external link.",
        "Please verify official OpenClaw/IronClaw channels before granting access.",
        "Avoid shortened links and unverified remote setup services.",
    ]
    if risk_reason:
        parts.append(f"Risk signal: {risk_reason}.")
    if suspicious_link:
        parts.append(f"Link to review: {suspicious_link}")
    return " ".join(parts).strip()


async def _draft_agentic_reply(linkedin: Any, params: Dict[str, str]) -> Dict[str, Any]:
    post_index = _safe_int(params.get("post_index", "0"), default=0)
    return await linkedin.draft_agentic_reply(
        post_index=post_index,
        post_context=params.get("post_context", params.get("content", "")).strip(),
        author=params.get("author", "").strip(),
        engagement_reason=params.get("engagement_reason", "").strip(),
        agent_identity=params.get("agent_identity", "0102").strip() or "0102",
        use_selected_post=_truthy(params.get("use_selected_post", "false")),
        read_first=_truthy(params.get("read_first", "false")),
    )


async def execute_skill(
    action: str,
    params: Dict[str, str],
    dom_action_observer: Optional[Any] = None,
) -> Dict[str, Any]:
    from modules.infrastructure.browser_actions.src.linkedin_actions import LinkedInActions

    profile = params.get("profile", "linkedin_foundups")
    browser_port = int(params.get("browser_port", "9222"))
    linkedin = LinkedInActions(
        profile=profile,
        browser_port=browser_port,
        dom_action_observer=dom_action_observer,
    )
    skill_name = "linkedin_agentic_reply"

    try:
        if action == "reply_post":
            reply_text = params.get("reply_text", "").strip()
            drafted = None
            if not reply_text:
                drafted = await _draft_agentic_reply(linkedin, params)
                if drafted.get("success"):
                    reply_text = str(drafted.get("reply_text", "")).strip()
            if not reply_text:
                return {
                    "success": False,
                    "action": action,
                    "skill": skill_name,
                    "error": "missing reply_text",
                    "draft": _to_jsonable(drafted),
                }

            post_index = _safe_int(params.get("post_index", "0"), default=0)
            post_id = params.get("post_id", "").strip() or f"index_{post_index}"
            dry_run = _truthy(params.get("dry_run", "true"))
            if dry_run:
                return {
                    "success": True,
                    "action": action,
                    "skill": skill_name,
                    "dry_run": True,
                    "post_id": post_id,
                    "post_index": post_index,
                    "reply_text": reply_text,
                    "draft": _to_jsonable(drafted),
                }
            result = await linkedin.reply_to_post(
                post_id=post_id,
                reply_text=reply_text,
                post_index=post_index,
            )
            return {
                "success": bool(result.success),
                "action": action,
                "skill": skill_name,
                "reply_text": reply_text,
                "draft": _to_jsonable(drafted),
                "result": _to_jsonable(result),
            }

        if action == "like_reply":
            reply_text = params.get("reply_text", "").strip()
            drafted = None
            if not reply_text:
                drafted = await _draft_agentic_reply(linkedin, params)
                if drafted.get("success"):
                    reply_text = str(drafted.get("reply_text", "")).strip()
            if not reply_text:
                return {
                    "success": False,
                    "action": action,
                    "skill": skill_name,
                    "error": "missing reply_text",
                    "draft": _to_jsonable(drafted),
                }

            post_index = _safe_int(params.get("post_index", "0"), default=0)
            post_id = params.get("post_id", "").strip() or f"index_{post_index}"
            dry_run = _truthy(params.get("dry_run", "true"))
            if dry_run:
                return {
                    "success": True,
                    "action": action,
                    "skill": skill_name,
                    "dry_run": True,
                    "post_id": post_id,
                    "post_index": post_index,
                    "reply_text": reply_text,
                    "draft": _to_jsonable(drafted),
                }
            result = await linkedin.like_and_reply(
                post_id=post_id,
                reply_text=reply_text,
                post_index=post_index,
            )
            return {
                "success": bool(result.success),
                "action": action,
                "skill": skill_name,
                "reply_text": reply_text,
                "draft": _to_jsonable(drafted),
                "result": _to_jsonable(result),
            }

        if action == "scam_reply":
            post_index = _safe_int(params.get("post_index", "0"), default=0)
            post_id = params.get("post_id", "").strip() or f"index_{post_index}"
            reply_text = params.get("reply_text", "").strip()
            drafted = None
            if not reply_text:
                drafted = await _draft_agentic_reply(linkedin, params)
                if drafted.get("success"):
                    reply_text = str(drafted.get("reply_text", "")).strip()
            if not reply_text:
                reply_text = _build_scam_callout_reply(params)

            dry_run = _truthy(params.get("dry_run", "true"))
            if dry_run:
                return {
                    "success": True,
                    "action": action,
                    "skill": skill_name,
                    "dry_run": True,
                    "post_id": post_id,
                    "post_index": post_index,
                    "reply_text": reply_text,
                    "draft": _to_jsonable(drafted),
                }
            result = await linkedin.reply_to_post(
                post_id=post_id,
                reply_text=reply_text,
                post_index=post_index,
            )
            return {
                "success": bool(result.success),
                "action": action,
                "skill": skill_name,
                "reply_text": reply_text,
                "draft": _to_jsonable(drafted),
                "result": _to_jsonable(result),
            }

        if action == "scam_scan_reply":
            max_posts = _safe_int(params.get("max_posts", "10"), default=10)
            min_score = _safe_int(params.get("min_score", "4"), default=4)
            max_replies = _safe_int(params.get("max_replies", "1"), default=1)
            dry_run = _truthy(params.get("dry_run", "true"))

            flagged = await linkedin.scan_feed_for_scam(
                max_posts=max_posts,
                min_score=min_score,
            )
            selected = flagged[: max(0, max_replies)]
            plans = []

            for item in selected:
                reply_text = params.get("reply_text", "").strip() or item.get("suggested_reply", "")
                drafted = None
                if not reply_text:
                    drafted = await linkedin.draft_agentic_reply(
                        post_index=int(item.get("post_index", 0)),
                        post_context=str(item.get("content", "")),
                        author=str(item.get("author", "")),
                        engagement_reason="scam_warning",
                        agent_identity=params.get("agent_identity", "0102").strip() or "0102",
                        use_selected_post=_truthy(params.get("use_selected_post", "false")),
                        read_first=_truthy(params.get("read_first", "false")),
                    )
                    if drafted.get("success"):
                        reply_text = str(drafted.get("reply_text", "")).strip()

                plans.append(
                    {
                        "post_id": item.get("post_id"),
                        "post_index": item.get("post_index"),
                        "author": item.get("author"),
                        "risk_score": item.get("risk_score"),
                        "risk_signals": item.get("risk_signals"),
                        "reply_text": reply_text,
                        "agentic_requested": True,
                        "draft": _to_jsonable(drafted),
                    }
                )

            if dry_run:
                return {
                    "success": True,
                    "action": action,
                    "skill": skill_name,
                    "dry_run": True,
                    "flagged_count": len(flagged),
                    "planned_replies": plans,
                }

            posted = []
            for plan in plans:
                if not plan.get("reply_text"):
                    continue
                result = await linkedin.reply_to_post(
                    post_id=str(plan.get("post_id") or f"index_{int(plan.get('post_index', 0))}"),
                    reply_text=str(plan.get("reply_text")),
                    post_index=int(plan.get("post_index", 0)),
                )
                posted.append(
                    {
                        **plan,
                        "result": _to_jsonable(result),
                        "success": bool(getattr(result, "success", False)),
                    }
                )

            return {
                "success": any(item.get("success") for item in posted) if posted else False,
                "action": action,
                "skill": skill_name,
                "flagged_count": len(flagged),
                "posted_replies": posted,
            }

        return {
            "success": False,
            "action": action,
            "skill": skill_name,
            "error": "unsupported agentic skill action",
        }
    finally:
        close_method = getattr(linkedin, "close", None)
        if callable(close_method):
            close_method()
