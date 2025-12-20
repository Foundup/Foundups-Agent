"""
YouTube Automation Gates (WSP 77/91)
===================================

Centralizes "can we act?" checks for YouTube automation surfaces.

Design goals:
- Single STOP file to immediately halt automation without code edits.
- Small, dependency-free helpers callable from multiple modules.
- Telemetry-friendly snapshot for heartbeat + gate-lab correlation.

Non-goals:
- This module does not attempt to bypass platform enforcement.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict


def _env_truthy(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in ("1", "true", "yes", "y", "on")


def stop_file_path() -> Path:
    return Path(os.getenv("YT_AUTOMATION_STOP_FILE", "memory/STOP_YT_AUTOMATION"))


def stop_active() -> bool:
    try:
        return stop_file_path().exists()
    except OSError:
        return False


def gate_snapshot() -> Dict[str, object]:
    """
    Snapshot current automation gates for observability (WSP 91).

    Keep this stable/compact; it is emitted frequently (heartbeat).
    """
    return {
        "stop_file": str(stop_file_path()),
        "stop_active": stop_active(),
        "yt_automation": _env_truthy("YT_AUTOMATION_ENABLED", "true"),
        "livechat_send": _env_truthy("YT_LIVECHAT_SEND_ENABLED", "true"),
        "livechat_dry_run": _env_truthy("YT_LIVECHAT_DRY_RUN", "false"),
        "comment_engagement": _env_truthy("YT_COMMENT_ENGAGEMENT_ENABLED", "true"),
        "livechat_ui_actions": _env_truthy("YT_LIVECHAT_UI_ACTIONS_ENABLED", "true"),
        "party_reactions": _env_truthy("YT_PARTY_REACTIONS_ENABLED", "true"),
        "announcements": _env_truthy("YT_LIVECHAT_ANNOUNCEMENTS_ENABLED", "true"),
        "stream_scraping": _env_truthy("YT_STREAM_SCRAPING_ENABLED", "true"),
        "stream_vision_disabled": os.getenv("STREAM_VISION_DISABLED", "true"),
    }

