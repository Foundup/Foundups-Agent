"""
Channel Configuration for YouTube Shorts Scheduler

Multi-channel support for Move2Japan, UnDaoDu, FoundUps, and RavingANTIFA.

Browser Port Routing:
- Chrome (9222): Move2Japan, UnDaoDu
- Edge (9223): FoundUps, RavingANTIFA
"""

from typing import Dict, Any, Optional
from urllib.parse import quote
import json

# Channel configurations
CHANNELS: Dict[str, Dict[str, Any]] = {
    "move2japan": {
        "id": "UC-LSSlOZwpGIRIYihaz8zCw",
        "name": "Move2Japan",
        "handle": "@MOVE2JAPAN",
        "timezone": "Asia/Tokyo",
        "time_slots": ["5:00 AM", "11:00 AM", "5:00 PM"],
        "max_per_day": 3,
        "chrome_port": 9222,  # Shared with UnDaoDu
        "description_template": "ffcpln",
    },
    "undaodu": {
        "id": "UCfHM9Fw9HD-NwiS0seD_oIA",
        "name": "UnDaoDu",
        "handle": "@UnDaoDu",
        "timezone": "Asia/Tokyo",
        "time_slots": ["5:00 AM", "11:00 AM", "5:00 PM"],
        "max_per_day": 3,
        "chrome_port": 9222,  # Shared with Move2Japan
        "description_template": "ffcpln",
    },
    "foundups": {
        "id": "UCSNTUXjAgpd4sgWYP0xoJgw",
        "name": "FoundUps",
        "handle": "@FoundUps",
        "timezone": "America/New_York",
        "time_slots": ["9:00 AM", "3:00 PM", "9:00 PM"],
        "max_per_day": 3,
        "chrome_port": 9223,  # Edge browser
        "description_template": "ffcpln",
    },
    "ravingantifa": {
        "id": "UCVSmg5aOhP4tnQ9KFUg97qA",
        "name": "RavingANTIFA",
        "handle": "@ravingANTIFA",
        "timezone": "America/New_York",
        "time_slots": ["9:00 AM", "3:00 PM", "9:00 PM"],
        "max_per_day": 3,
        "chrome_port": 9223,  # Edge browser - shared with FoundUps
        "description_template": "ffcpln",
    },
}


def get_channel_config(channel_key: str) -> Optional[Dict[str, Any]]:
    """
    Get configuration for a channel.

    Args:
        channel_key: "move2japan", "undaodu", "foundups", or "ravingantifa"

    Returns:
        Channel config dict or None
    """
    return CHANNELS.get(channel_key.lower())


def build_studio_url(
    channel_id: str,
    content_type: str = "short",
    visibility: Optional[str] = None,
    sort_by: str = "date",
    sort_order: str = "DESCENDING"
) -> str:
    """
    Build YouTube Studio URL with filters.

    Args:
        channel_id: YouTube channel ID
        content_type: "short", "upload", "live"
        visibility: "UNLISTED", "SCHEDULED", "PUBLIC", "PRIVATE", or None
        sort_by: "date", "views", etc.
        sort_order: "DESCENDING" or "ASCENDING"

    Returns:
        Full YouTube Studio URL with encoded parameters
    """
    base_url = f"https://studio.youtube.com/channel/{channel_id}/videos/{content_type}"

    # Build filter
    if visibility:
        filter_obj = [{"name": "VISIBILITY", "value": [visibility]}]
    else:
        filter_obj = []

    # Build sort
    sort_obj = {"columnType": sort_by, "sortOrder": sort_order}

    # Encode parameters
    filter_param = quote(json.dumps(filter_obj))
    sort_param = quote(json.dumps(sort_obj))

    return f"{base_url}?filter={filter_param}&sort={sort_param}"


def get_studio_urls(channel_key: str) -> Dict[str, str]:
    """
    Get all pre-built Studio URLs for a channel.

    Args:
        channel_key: "move2japan", "undaodu", "foundups", or "ravingantifa"

    Returns:
        Dict with URL keys: unlisted_shorts, scheduled_shorts, all_shorts
    """
    config = get_channel_config(channel_key)
    if not config:
        raise ValueError(f"Unknown channel: {channel_key}")

    channel_id = config["id"]

    return {
        "unlisted_shorts": build_studio_url(channel_id, "short", "UNLISTED"),
        "scheduled_shorts": build_studio_url(channel_id, "short", "SCHEDULED"),
        "public_shorts": build_studio_url(channel_id, "short", "PUBLIC"),
        "all_shorts": build_studio_url(channel_id, "short"),
        "base": f"https://studio.youtube.com/channel/{channel_id}",
    }
