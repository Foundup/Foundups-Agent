"""
YouTube Live Stream Ingest URL Resolver

Fetches the correct RTMPS ingest URL from YouTube Data API for the active stream.

YouTube Live Streaming API provides stream-specific ingest URLs:
- rtmpsIngestionAddress (primary)
- rtmpsBackupIngestionAddress (backup)

Using generic URLs like rtmps://a.rtmps.youtube.com:443/live2 can cause
connection issues when YouTube assigns a different endpoint to the stream.

Reference:
- https://developers.google.com/youtube/v3/live/docs/liveStreams
- https://developers.google.com/youtube/v3/live/guides/rtmps-ingestion

WSP Compliance:
- WSP 27: Universal DAE Architecture (Phase 1: Protocol execution)
- WSP 64: Secure credential management (OAuth via youtube_auth)
"""

import logging
import os
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

try:
    from dotenv import load_dotenv
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
    load_dotenv(PROJECT_ROOT / ".env")
except Exception:
    pass

# antifaFM channel configuration - NOT using FOUNDUPS_CHANNEL_ID fallback
ANTIFAFM_BRAND_CHANNEL_ID = os.getenv("ANTIFAFM_CHANNEL_ID", "UCVSmg5aOhP4tnQ9KFUg97qA")
ANTIFAFM_CHANNEL_ID = os.getenv(
    "ANTIFAFM_BROADCAST_CHANNEL_ID",
    ANTIFAFM_BRAND_CHANNEL_ID,  # Use antifaFM channel, not FOUNDUPS_CHANNEL_ID
)


def get_antifafm_broadcast_channel_id() -> str:
    """Resolve the channel currently hosting the antifaFM livestream."""
    # For antifaFM broadcaster, use ANTIFAFM channel - NOT FOUNDUPS_CHANNEL_ID fallback
    return os.getenv(
        "ANTIFAFM_BROADCAST_CHANNEL_ID",
        os.getenv("ANTIFAFM_CHANNEL_ID", "UCVSmg5aOhP4tnQ9KFUg97qA"),
    )


def _get_authenticated_channel_info(youtube) -> Optional[Dict[str, str]]:
    """Return the authenticated channel identity for the provided service."""
    try:
        response = youtube.channels().list(part="id,snippet", mine=True).execute()
        items = response.get("items", [])
        if not items:
            return None
        item = items[0]
        return {
            "id": item.get("id", ""),
            "title": item.get("snippet", {}).get("title", ""),
        }
    except Exception as e:
        logger.warning(f"[INGEST] Could not determine authenticated channel identity: {e}")
        return None


@dataclass
class IngestEndpoints:
    """RTMPS ingest endpoints for a live stream."""
    primary_url: str
    backup_url: Optional[str] = None
    stream_name: str = ""  # Stream key portion
    stream_id: str = ""    # YouTube stream resource ID
    broadcast_id: str = "" # YouTube broadcast resource ID

    def __str__(self) -> str:
        return f"IngestEndpoints(primary={self.primary_url[:50]}..., backup={'yes' if self.backup_url else 'no'})"


def get_youtube_service(token_index: int = None):
    """
    Get authenticated YouTube Data API service.

    Uses youtube_auth module for OAuth credential management.
    """
    try:
        from modules.platform_integration.youtube_auth.src.youtube_auth import get_authenticated_service
        return get_authenticated_service(token_index=token_index)
    except ImportError as e:
        logger.error(f"[INGEST] youtube_auth module not available: {e}")
        return None
    except Exception as e:
        logger.error(f"[INGEST] Failed to get YouTube service: {e}")
        return None


def resolve_ingest_endpoints(
    stream_key: str = None,
    channel_id: Optional[str] = None,
    prefer_backup: bool = False,
    token_index: int = None
) -> Optional[IngestEndpoints]:
    """
    Resolve the correct RTMPS ingest endpoints for the active live stream.

    Flow:
    1. List active live broadcasts for the channel
    2. Get the bound stream ID from the broadcast
    3. Fetch stream details to get ingest URLs

    Args:
        stream_key: Optional stream key to match (if known)
        channel_id: YouTube channel ID (defaults to antifaFM)
        prefer_backup: If True, swap primary/backup order
        token_index: OAuth token set to use (None = auto-rotate)

    Returns:
        IngestEndpoints with primary and backup URLs, or None if not found
    """
    channel_id = channel_id or get_antifafm_broadcast_channel_id()
    logger.info(f"[INGEST] Resolving ingest endpoints for channel {channel_id[:12]}...")

    youtube = get_youtube_service(token_index)
    if not youtube:
        logger.error("[INGEST] Could not get YouTube service")
        return None

    try:
        identity = _get_authenticated_channel_info(youtube)
        if identity:
            logger.info(f"[INGEST] OAuth channel: {identity['title']} ({identity['id']})")
            if channel_id and identity["id"] != channel_id:
                # Brand accounts: OAuth returns parent account, but target is brand channel
                # This is expected for antifaFM (brand) under Foundups (parent)
                # Only warn, don't fail - the stream key determines actual destination
                allow_brand = os.getenv("ANTIFAFM_ALLOW_BRAND_ACCOUNT", "1") == "1"
                if allow_brand:
                    logger.warning(
                        f"[INGEST] OAuth channel differs from target (brand account): "
                        f"OAuth={identity['id']} ({identity['title']}), target={channel_id}"
                    )
                else:
                    logger.error(
                        f"[INGEST] OAuth channel mismatch: expected {channel_id}, got {identity['id']} ({identity['title']})"
                    )
                    return None

        # Step 1: Find active/upcoming broadcasts
        broadcasts = youtube.liveBroadcasts().list(
            part="id,snippet,contentDetails,status",
            broadcastStatus="all",  # active, upcoming, complete
            broadcastType="all",
            maxResults=10
        ).execute()

        if not broadcasts.get("items"):
            logger.warning("[INGEST] No broadcasts found for channel")
            return None

        # Find the most relevant broadcast (active > upcoming > recent)
        target_broadcast = None
        for broadcast in broadcasts.get("items", []):
            status = broadcast.get("status", {}).get("lifeCycleStatus", "")
            logger.debug(f"[INGEST] Broadcast {broadcast['id']}: {status}")

            if status == "live":
                target_broadcast = broadcast
                break
            elif status in ("ready", "testing") and not target_broadcast:
                target_broadcast = broadcast
            elif status == "created" and not target_broadcast:
                target_broadcast = broadcast

        if not target_broadcast:
            # Use most recent
            target_broadcast = broadcasts["items"][0]

        broadcast_id = target_broadcast["id"]
        broadcast_title = target_broadcast.get("snippet", {}).get("title", "Untitled")
        bound_stream_id = target_broadcast.get("contentDetails", {}).get("boundStreamId")

        logger.info(f"[INGEST] Found broadcast: {broadcast_title} (ID: {broadcast_id})")
        logger.info(f"[INGEST] Bound stream ID: {bound_stream_id}")

        if not bound_stream_id:
            logger.error("[INGEST] Broadcast has no bound stream - cannot get ingest URL")
            return None

        # Step 2: Get stream details with ingest info
        streams = youtube.liveStreams().list(
            part="id,snippet,cdn,status",
            id=bound_stream_id
        ).execute()

        if not streams.get("items"):
            logger.error(f"[INGEST] Stream {bound_stream_id} not found")
            return None

        stream = streams["items"][0]
        cdn = stream.get("cdn", {})
        ingestion_info = cdn.get("ingestionInfo", {})

        # Extract ingest URLs
        primary_url = ingestion_info.get("rtmpsIngestionAddress")
        backup_url = ingestion_info.get("rtmpsBackupIngestionAddress")
        stream_name = ingestion_info.get("streamName", "")  # This is the stream key

        # Fallback to non-RTMPS if RTMPS not available
        if not primary_url:
            primary_url = ingestion_info.get("ingestionAddress")
            backup_url = ingestion_info.get("backupIngestionAddress")
            logger.warning("[INGEST] RTMPS URLs not available, using RTMP")

        if not primary_url:
            logger.error("[INGEST] No ingest URL found in stream data")
            logger.debug(f"[INGEST] CDN data: {cdn}")
            return None

        # Validate stream key matches if provided
        if stream_key and stream_name and stream_key != stream_name:
            logger.warning(f"[INGEST] Stream key mismatch: env={stream_key[:8]}... api={stream_name[:8]}...")

        # Swap if backup preferred
        if prefer_backup and backup_url:
            primary_url, backup_url = backup_url, primary_url
            logger.info("[INGEST] Using backup endpoint as primary (prefer_backup=True)")

        endpoints = IngestEndpoints(
            primary_url=primary_url,
            backup_url=backup_url,
            stream_name=stream_name,
            stream_id=bound_stream_id,
            broadcast_id=broadcast_id
        )

        logger.info(f"[INGEST] Resolved: {endpoints}")
        logger.info(f"[INGEST] Primary URL: {primary_url}")
        if backup_url:
            logger.info(f"[INGEST] Backup URL: {backup_url}")

        return endpoints

    except Exception as e:
        logger.error(f"[INGEST] API error: {e}")
        return None


def get_ingest_url_with_fallback(
    stream_key: str = None,
    channel_id: Optional[str] = None,
    fallback_url: str = "rtmps://a.rtmps.youtube.com:443/live2",
    try_backup_on_failure: bool = True,
    token_index: int = None,
) -> Tuple[str, bool]:
    """
    Get ingest URL with fallback to generic URL.

    Attempts API resolution first, falls back to generic URL if API fails.

    Args:
        stream_key: Stream key from environment
        channel_id: YouTube channel ID
        fallback_url: Generic URL to use if API fails
        try_backup_on_failure: If primary fails, try backup URL
        token_index: OAuth token set to use for API lookup

    Returns:
        Tuple of (rtmp_url, is_api_resolved)
        - rtmp_url: The RTMPS ingest URL to use
        - is_api_resolved: True if URL came from API, False if fallback
    """
    # Try API resolution
    endpoints = resolve_ingest_endpoints(
        stream_key=stream_key,
        channel_id=channel_id or get_antifafm_broadcast_channel_id(),
        token_index=token_index,
    )

    if endpoints and endpoints.primary_url:
        logger.info("[INGEST] Using API-resolved ingest URL")
        return endpoints.primary_url, True

    # API failed - use fallback
    logger.warning(f"[INGEST] API resolution failed, using fallback: {fallback_url}")
    return fallback_url, False


def diagnose_ingest_config(
    stream_key: str = None,
    channel_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Diagnostic function to check ingest configuration.

    Useful for debugging streaming issues.

    Returns:
        Dict with diagnostic information
    """
    result = {
        "channel_id": channel_id,
        "stream_key_configured": bool(stream_key),
        "api_available": False,
        "endpoints": None,
        "error": None
    }

    try:
        endpoints = resolve_ingest_endpoints(
            stream_key=stream_key,
            channel_id=channel_id or get_antifafm_broadcast_channel_id()
        )

        if endpoints:
            result["api_available"] = True
            result["endpoints"] = {
                "primary_url": endpoints.primary_url,
                "backup_url": endpoints.backup_url,
                "stream_name": endpoints.stream_name[:8] + "..." if endpoints.stream_name else None,
                "stream_id": endpoints.stream_id,
                "broadcast_id": endpoints.broadcast_id
            }
        else:
            result["error"] = "No endpoints resolved"

    except Exception as e:
        result["error"] = str(e)

    return result


# CLI for testing
if __name__ == "__main__":
    import sys
    import json

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

    stream_key = os.getenv("ANTIFAFM_YOUTUBE_STREAM_KEY", "")

    print("\n[TEST] YouTube Ingest URL Resolver")
    print("=" * 50)

    if "--diagnose" in sys.argv:
        result = diagnose_ingest_config(stream_key=stream_key)
        print(json.dumps(result, indent=2))
    else:
        endpoints = resolve_ingest_endpoints(stream_key=stream_key)
        if endpoints:
            print(f"Primary: {endpoints.primary_url}")
            print(f"Backup:  {endpoints.backup_url or 'N/A'}")
            print(f"Stream:  {endpoints.stream_name[:12]}..." if endpoints.stream_name else "N/A")
        else:
            print("[ERROR] Could not resolve ingest endpoints")

            # Show fallback
            url, is_api = get_ingest_url_with_fallback(stream_key=stream_key)
            print(f"\nFallback URL: {url}")
            print(f"From API: {is_api}")
