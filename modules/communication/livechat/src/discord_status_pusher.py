#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Discord Status Pusher - Push automation status to 012 via Discord webhook.

Simple singleton that AutoModeratorDAE and other systems can use to push
status updates without importing AI Overseer directly.

Usage:
    from .discord_status_pusher import push_status
    push_status("✅ Finished Move2Japan comments (47 processed)")
"""

import os
import logging
from typing import Optional

logger = logging.getLogger("discord_status_pusher")

# Cache for AI Overseer (lazy-loaded)
_ai_overseer_cache = None


def _get_ai_overseer():
    """Lazy-load AI Overseer singleton."""
    global _ai_overseer_cache
    if _ai_overseer_cache is None:
        try:
            from modules.ai_intelligence.ai_overseer.src.ai_overseer import AIIntelligenceOverseer
            from pathlib import Path
            repo_root = Path("O:/Foundups-Agent")
            _ai_overseer_cache = AIIntelligenceOverseer(repo_root)
            logger.debug("[DISCORD-PUSH] AI Overseer loaded")
        except Exception as e:
            logger.warning(f"[DISCORD-PUSH] AI Overseer unavailable: {e}")
            _ai_overseer_cache = False  # Mark as failed, don't retry
    return _ai_overseer_cache if _ai_overseer_cache else None


def push_status(message: str, to_discord: bool = True, to_log: bool = True) -> bool:
    """
    Push status update to Discord and/or log.

    This is the main entry point for AutoModeratorDAE milestones.

    Args:
        message: Status message (supports emoji)
        to_discord: Push to Discord webhook (default True)
        to_log: Log to console (default True)

    Returns:
        True if push succeeded (or no webhook configured)
    """
    if to_log:
        logger.info(f"[STATUS] {message}")

    if not to_discord:
        return True

    # Try AI Overseer first (has push_status method)
    overseer = _get_ai_overseer()
    if overseer and hasattr(overseer, "push_status"):
        try:
            result = overseer.push_status(message, to_discord=True, to_chat=False)
            return result.get("discord", False)
        except Exception as e:
            logger.debug(f"[DISCORD-PUSH] AI Overseer push failed: {e}")

    # Fallback: direct webhook push
    return _direct_discord_push(message)


def _direct_discord_push(message: str) -> bool:
    """Direct Discord webhook push (fallback if AI Overseer unavailable)."""
    webhook_url = os.getenv("DISCORD_STATUS_WEBHOOK")
    if not webhook_url:
        logger.debug("[DISCORD-PUSH] No DISCORD_STATUS_WEBHOOK configured")
        return True  # Not an error, just not configured

    try:
        import requests
        response = requests.post(
            webhook_url,
            json={"content": message},
            timeout=5
        )
        if response.status_code in (200, 204):
            logger.debug(f"[DISCORD-PUSH] Sent: {message[:50]}...")
            return True
        else:
            logger.warning(f"[DISCORD-PUSH] Failed: HTTP {response.status_code}")
            return False
    except ImportError:
        logger.warning("[DISCORD-PUSH] requests library not available")
        return False
    except Exception as e:
        logger.warning(f"[DISCORD-PUSH] Error: {e}")
        return False


# Convenience aliases
def push_comment_complete(channel_name: str, count: int):
    """Push comment processing completion status."""
    emoji = "✅" if count > 0 else "💤"
    push_status(f"{emoji} Finished {channel_name} comments ({count} processed)")


def push_scheduling_complete(channel_name: str, scheduled: int, errors: int = 0):
    """Push shorts scheduling completion status."""
    if errors > 0:
        push_status(f"📊 {channel_name} scheduling: {scheduled} scheduled, {errors} errors")
    elif scheduled > 0:
        push_status(f"📊 {channel_name} shorts: {scheduled} scheduled")
    else:
        push_status(f"💤 {channel_name} shorts: nothing to schedule")


def push_cycle_complete(browser: str, cycle: int, comments: int, scheduled: int):
    """Push browser cycle completion summary."""
    push_status(f"🔄 {browser.upper()} cycle #{cycle}: {comments} comments, {scheduled} scheduled")


def push_oops_page(channel_name: str, fallback: Optional[str] = None):
    """Push OOPS page detection alert."""
    if fallback:
        push_status(f"🚨 OOPS page on {channel_name} → falling back to {fallback}")
    else:
        push_status(f"🚨 OOPS page detected on {channel_name}")


def push_idle(browser: str):
    """Push idle status when browser has no work."""
    push_status(f"💤 {browser.upper()} idle — all channels processed")
