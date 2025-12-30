"""
Live Stream Signal - Heartbeat Communication Between Stream Resolver and Comment DAE

This module provides a simple file-based signal system for communicating live stream status
between the stream resolver (producer) and comment engagement DAE (consumer).

Architecture (Occam's Razor):
- Stream Resolver WRITES signal when live stream detected/ended
- Comment DAE READS signal before each channel rotation cycle
- If live detected → pause comment rotation for that channel
- If no live → continue normal comment rotation

Signal File: memory/live_stream_signal.json
{
    "live": true,
    "channel_id": "UC-LSSlOZwpGIRIYihaz8zCw",
    "channel_name": "Move2Japan",
    "video_id": "dQw4w9WgXcQ",
    "timestamp": "2025-12-28T12:00:00",
    "source": "no_quota_stream_checker"
}

WSP Compliance:
- WSP 27: DAE Architecture (Signal → Knowledge → Protocol → Agentic)
- WSP 91: DAEMON Observability (file-based telemetry)
"""

import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Signal file path (relative to repo root)
SIGNAL_FILE = Path("memory/live_stream_signal.json")


def _get_signal_path() -> Path:
    """Get absolute path to signal file."""
    # Try to find repo root by looking for common markers
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "main.py").exists() or (parent / "CLAUDE.md").exists():
            signal_path = parent / SIGNAL_FILE
            signal_path.parent.mkdir(parents=True, exist_ok=True)
            return signal_path

    # Fallback: use current working directory
    signal_path = Path.cwd() / SIGNAL_FILE
    signal_path.parent.mkdir(parents=True, exist_ok=True)
    return signal_path


def write_live_signal(
    channel_id: str,
    channel_name: str,
    video_id: str,
    source: str = "stream_resolver"
) -> bool:
    """
    Write live stream detected signal.

    Called by stream_resolver when a live stream is detected.

    Args:
        channel_id: YouTube channel ID
        channel_name: Human-readable channel name (Move2Japan, UnDaoDu, FoundUps)
        video_id: YouTube video ID of the live stream
        source: Component that detected the stream

    Returns:
        True if signal written successfully
    """
    try:
        signal_path = _get_signal_path()

        signal = {
            "live": True,
            "channel_id": channel_id,
            "channel_name": channel_name,
            "video_id": video_id,
            "timestamp": datetime.now().isoformat(),
            "source": source,
            "written_at": time.time()
        }

        with open(signal_path, 'w', encoding='utf-8') as f:
            json.dump(signal, f, indent=2)

        logger.info(f"[SIGNAL] Live stream signal WRITTEN: {channel_name} ({video_id})")
        return True

    except Exception as e:
        logger.error(f"[SIGNAL] Failed to write live signal: {e}")
        return False


def clear_live_signal(channel_id: Optional[str] = None) -> bool:
    """
    Clear live stream signal (stream ended).

    Called by stream_resolver when a live stream ends.

    Args:
        channel_id: Optional channel ID to match (only clears if matches)

    Returns:
        True if signal cleared successfully
    """
    try:
        signal_path = _get_signal_path()

        if not signal_path.exists():
            return True  # Already cleared

        # Check if we should clear (optional channel_id filter)
        if channel_id:
            try:
                with open(signal_path, 'r', encoding='utf-8') as f:
                    current = json.load(f)
                if current.get("channel_id") != channel_id:
                    logger.debug(f"[SIGNAL] Signal not cleared - different channel")
                    return False
            except Exception:
                pass

        # Clear by writing non-live signal
        signal = {
            "live": False,
            "channel_id": None,
            "channel_name": None,
            "video_id": None,
            "timestamp": datetime.now().isoformat(),
            "source": "signal_cleared",
            "written_at": time.time()
        }

        with open(signal_path, 'w', encoding='utf-8') as f:
            json.dump(signal, f, indent=2)

        logger.info(f"[SIGNAL] Live stream signal CLEARED")
        return True

    except Exception as e:
        logger.error(f"[SIGNAL] Failed to clear signal: {e}")
        return False


def read_live_signal() -> Dict:
    """
    Read current live stream signal.

    Called by comment DAE before each channel rotation.

    Returns:
        Signal dict with 'live' key (False if no signal or error)
    """
    try:
        signal_path = _get_signal_path()

        if not signal_path.exists():
            return {"live": False, "reason": "no_signal_file"}

        with open(signal_path, 'r', encoding='utf-8') as f:
            signal = json.load(f)

        # Check if signal is stale (older than 5 minutes)
        written_at = signal.get("written_at", 0)
        age_seconds = time.time() - written_at

        if age_seconds > 300:  # 5 minutes
            logger.debug(f"[SIGNAL] Signal is stale ({age_seconds:.0f}s old)")
            signal["stale"] = True

        return signal

    except Exception as e:
        logger.error(f"[SIGNAL] Failed to read signal: {e}")
        return {"live": False, "reason": f"error: {e}"}


def is_channel_live(channel_id: str) -> bool:
    """
    Check if a specific channel has an active live stream.

    Quick helper for comment DAE rotation logic.

    Args:
        channel_id: YouTube channel ID to check

    Returns:
        True if channel has active (non-stale) live stream
    """
    signal = read_live_signal()

    if not signal.get("live"):
        return False

    if signal.get("stale"):
        return False

    return signal.get("channel_id") == channel_id


def get_live_channel() -> Optional[str]:
    """
    Get the channel ID that currently has a live stream.

    Returns:
        Channel ID if live stream active, None otherwise
    """
    signal = read_live_signal()

    if not signal.get("live"):
        return None

    if signal.get("stale"):
        return None

    return signal.get("channel_id")
