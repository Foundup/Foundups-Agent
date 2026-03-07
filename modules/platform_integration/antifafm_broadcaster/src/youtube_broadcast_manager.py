"""
YouTube Broadcast Manager - Autonomous Broadcast Creation

Creates and manages YouTube Live broadcasts programmatically via YouTube Data API.

This is the MISSING PIECE that was causing FFmpeg to die after 3 frames:
- Stream key exists but was ORPHANED (no active broadcast)
- YouTube requires: Broadcast (video ID) + Stream (key) + BINDING between them
- Without active broadcast, RTMP connection accepts data but discards it

Flow:
1. create_broadcast() - Creates the video listing
2. get_or_create_stream() - Creates/reuses the RTMP stream endpoint
3. bind_stream_to_broadcast() - Links them together
4. transition_to_live() - Activates the broadcast
5. OBS/FFmpeg can now stream successfully!

Usage:
    from youtube_broadcast_manager import YouTubeBroadcastManager

    manager = YouTubeBroadcastManager()
    result = await manager.create_live_broadcast(
        title="antifaFM Radio - Live",
        description="24/7 antifascist radio stream"
    )

    # result contains stream_key and rtmp_url for OBS/FFmpeg

WSP Compliance:
- WSP 27: Universal DAE Architecture (autonomous operation)
- WSP 64: Secure credential management (OAuth via youtube_auth)
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta, timezone
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

# antifaFM channel configuration
ANTIFAFM_CHANNEL_ID = os.getenv("ANTIFAFM_CHANNEL_ID", "UCVSmg5aOhP4tnQ9KFUg97qA")


@dataclass
class BroadcastResult:
    """Result of broadcast creation."""
    success: bool
    broadcast_id: Optional[str] = None
    stream_id: Optional[str] = None
    stream_key: Optional[str] = None
    rtmp_url: Optional[str] = None
    rtmps_url: Optional[str] = None
    watch_url: Optional[str] = None
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.success:
            return f"BroadcastResult(broadcast={self.broadcast_id}, stream={self.stream_key[:8]}...)"
        return f"BroadcastResult(error={self.error})"


class YouTubeBroadcastManager:
    """
    Manages YouTube Live broadcasts for autonomous streaming.

    This enables AI_overseer to:
    1. Create broadcasts without manual YouTube Studio interaction
    2. Get stream keys and RTMP URLs for OBS/FFmpeg
    3. Control broadcast lifecycle (live/end)
    """

    def __init__(self, token_index: int = None):
        """
        Initialize broadcast manager.

        Args:
            token_index: OAuth token set to use (default: ANTIFAFM_YOUTUBE_TOKEN_SET)
        """
        self.token_index = token_index or int(os.getenv("ANTIFAFM_YOUTUBE_TOKEN_SET", "10"))
        self._youtube = None

    def _get_youtube_service(self):
        """Get authenticated YouTube Data API service."""
        if self._youtube:
            return self._youtube

        try:
            from modules.platform_integration.youtube_auth.src.youtube_auth import get_authenticated_service
            self._youtube = get_authenticated_service(token_index=self.token_index)
            return self._youtube
        except ImportError as e:
            logger.error(f"[BROADCAST] youtube_auth module not available: {e}")
            return None
        except Exception as e:
            logger.error(f"[BROADCAST] Failed to get YouTube service: {e}")
            return None

    def _verify_channel(self) -> Tuple[bool, Optional[str], Optional[str]]:
        """Verify OAuth is for antifaFM channel."""
        youtube = self._get_youtube_service()
        if not youtube:
            return False, None, "No YouTube service"

        try:
            response = youtube.channels().list(part="id,snippet", mine=True).execute()
            items = response.get("items", [])
            if not items:
                return False, None, "No channel found"

            channel = items[0]
            channel_id = channel.get("id")
            channel_title = channel.get("snippet", {}).get("title", "Unknown")

            if channel_id != ANTIFAFM_CHANNEL_ID:
                # Brand accounts: OAuth returns parent account, but target is brand channel
                # This is expected for antifaFM (brand) under Foundups (parent)
                allow_brand = os.getenv("ANTIFAFM_ALLOW_BRAND_ACCOUNT", "1") == "1"
                if allow_brand:
                    logger.warning(
                        f"[BROADCAST] Brand account detected: OAuth={channel_id} ({channel_title}), "
                        f"target={ANTIFAFM_CHANNEL_ID} - proceeding anyway"
                    )
                else:
                    return False, channel_title, f"Wrong channel: {channel_title} ({channel_id})"
            else:
                logger.info(f"[BROADCAST] Verified channel: {channel_title}")
            return True, channel_title, None

        except Exception as e:
            return False, None, str(e)

    async def create_live_broadcast(
        self,
        title: str = "antifaFM Radio - Live",
        description: str = "24/7 antifascist radio stream",
        privacy: str = "public",
        enable_dvr: bool = True,
        enable_auto_start: bool = True,
        enable_auto_stop: bool = False,
        scheduled_start: Optional[datetime] = None,
    ) -> BroadcastResult:
        """
        Create a complete live broadcast ready for streaming.

        This performs the FULL flow:
        1. Verify channel
        2. Create broadcast
        3. Create/reuse stream
        4. Bind stream to broadcast
        5. Return stream key and RTMP URL

        Args:
            title: Broadcast title
            description: Broadcast description
            privacy: "public", "private", or "unlisted"
            enable_dvr: Allow DVR (rewind)
            enable_auto_start: Auto-start when encoder connects
            enable_auto_stop: Auto-stop when encoder disconnects
            scheduled_start: Scheduled start time (default: now)

        Returns:
            BroadcastResult with stream_key and rtmp_url
        """
        # Step 1: Verify channel
        is_valid, channel_name, error = self._verify_channel()
        if not is_valid:
            return BroadcastResult(success=False, error=error)

        youtube = self._get_youtube_service()

        try:
            # Step 2: Create broadcast
            broadcast = await self._create_broadcast(
                youtube=youtube,
                title=title,
                description=description,
                privacy=privacy,
                enable_dvr=enable_dvr,
                enable_auto_start=enable_auto_start,
                enable_auto_stop=enable_auto_stop,
                scheduled_start=scheduled_start,
            )

            if not broadcast:
                return BroadcastResult(success=False, error="Failed to create broadcast")

            broadcast_id = broadcast["id"]
            logger.info(f"[BROADCAST] Created broadcast: {broadcast_id}")

            # Step 3: Get or create stream
            stream = await self._get_or_create_stream(
                youtube=youtube,
                title=f"{title} - Stream"
            )

            if not stream:
                return BroadcastResult(success=False, error="Failed to create stream")

            stream_id = stream["id"]
            cdn = stream.get("cdn", {})
            ingestion_info = cdn.get("ingestionInfo", {})

            stream_key = ingestion_info.get("streamName", "")
            rtmp_url = ingestion_info.get("ingestionAddress", "")
            rtmps_url = ingestion_info.get("rtmpsIngestionAddress", "")

            logger.info(f"[BROADCAST] Stream: {stream_id}, key: {stream_key[:8]}...")

            # Step 4: Bind stream to broadcast
            bound = await self._bind_stream(
                youtube=youtube,
                broadcast_id=broadcast_id,
                stream_id=stream_id
            )

            if not bound:
                return BroadcastResult(
                    success=False,
                    error="Failed to bind stream to broadcast",
                    broadcast_id=broadcast_id,
                    stream_id=stream_id
                )

            logger.info(f"[BROADCAST] Bound stream {stream_id} to broadcast {broadcast_id}")

            watch_url = f"https://youtube.com/watch?v={broadcast_id}"

            return BroadcastResult(
                success=True,
                broadcast_id=broadcast_id,
                stream_id=stream_id,
                stream_key=stream_key,
                rtmp_url=rtmp_url,
                rtmps_url=rtmps_url or f"rtmps://a.rtmps.youtube.com:443/live2",
                watch_url=watch_url
            )

        except Exception as e:
            logger.error(f"[BROADCAST] Error creating broadcast: {e}")
            return BroadcastResult(success=False, error=str(e))

    async def _create_broadcast(
        self,
        youtube,
        title: str,
        description: str,
        privacy: str,
        enable_dvr: bool,
        enable_auto_start: bool,
        enable_auto_stop: bool,
        scheduled_start: Optional[datetime],
    ) -> Optional[Dict]:
        """Create a YouTube broadcast."""

        # Schedule for now if not specified
        if not scheduled_start:
            scheduled_start = datetime.now(timezone.utc) + timedelta(minutes=1)

        scheduled_iso = scheduled_start.isoformat()

        body = {
            "snippet": {
                "title": title,
                "description": description,
                "scheduledStartTime": scheduled_iso,
            },
            "status": {
                "privacyStatus": privacy,
                "selfDeclaredMadeForKids": False,
            },
            "contentDetails": {
                "enableDvr": enable_dvr,
                "enableAutoStart": enable_auto_start,
                "enableAutoStop": enable_auto_stop,
                "latencyPreference": "normal",  # "ultraLow", "low", "normal"
                "enableClosedCaptions": False,
            }
        }

        try:
            response = youtube.liveBroadcasts().insert(
                part="snippet,status,contentDetails",
                body=body
            ).execute()

            return response

        except Exception as e:
            logger.error(f"[BROADCAST] liveBroadcasts.insert failed: {e}")
            return None

    async def _get_or_create_stream(
        self,
        youtube,
        title: str,
        resolution: str = "1080p",
        frame_rate: str = "30fps",
    ) -> Optional[Dict]:
        """Get existing stream or create new one."""

        # First, try to find existing reusable stream
        try:
            existing = youtube.liveStreams().list(
                part="id,snippet,cdn,status",
                mine=True,
                maxResults=10
            ).execute()

            for stream in existing.get("items", []):
                status = stream.get("status", {}).get("streamStatus", "")
                # Reuse inactive streams
                if status in ("ready", "inactive"):
                    logger.info(f"[BROADCAST] Reusing existing stream: {stream['id']}")
                    return stream

        except Exception as e:
            logger.warning(f"[BROADCAST] Could not list existing streams: {e}")

        # Create new stream
        body = {
            "snippet": {
                "title": title,
            },
            "cdn": {
                "frameRate": frame_rate,
                "resolution": resolution,
                "ingestionType": "rtmp",
            }
        }

        try:
            response = youtube.liveStreams().insert(
                part="snippet,cdn,status",
                body=body
            ).execute()

            return response

        except Exception as e:
            logger.error(f"[BROADCAST] liveStreams.insert failed: {e}")
            return None

    async def _bind_stream(
        self,
        youtube,
        broadcast_id: str,
        stream_id: str,
    ) -> bool:
        """Bind a stream to a broadcast."""
        try:
            youtube.liveBroadcasts().bind(
                part="id,contentDetails",
                id=broadcast_id,
                streamId=stream_id
            ).execute()

            return True

        except Exception as e:
            logger.error(f"[BROADCAST] liveBroadcasts.bind failed: {e}")
            return False

    async def transition_to_live(self, broadcast_id: str) -> bool:
        """
        Transition broadcast to live state.

        Note: YouTube requires the stream to be active (encoder connected)
        before transitioning to "live". Call this AFTER OBS/FFmpeg connects.
        """
        youtube = self._get_youtube_service()
        if not youtube:
            return False

        try:
            # First transition to "testing"
            youtube.liveBroadcasts().transition(
                part="id,status",
                id=broadcast_id,
                broadcastStatus="testing"
            ).execute()

            logger.info(f"[BROADCAST] Transitioned {broadcast_id} to testing")

            # Wait for stream to be active
            await asyncio.sleep(5)

            # Then transition to "live"
            youtube.liveBroadcasts().transition(
                part="id,status",
                id=broadcast_id,
                broadcastStatus="live"
            ).execute()

            logger.info(f"[BROADCAST] Transitioned {broadcast_id} to LIVE!")
            return True

        except Exception as e:
            logger.error(f"[BROADCAST] Transition failed: {e}")
            return False

    async def end_broadcast(self, broadcast_id: str) -> bool:
        """End an active broadcast."""
        youtube = self._get_youtube_service()
        if not youtube:
            return False

        try:
            youtube.liveBroadcasts().transition(
                part="id,status",
                id=broadcast_id,
                broadcastStatus="complete"
            ).execute()

            logger.info(f"[BROADCAST] Ended broadcast {broadcast_id}")
            return True

        except Exception as e:
            logger.error(f"[BROADCAST] End broadcast failed: {e}")
            return False

    async def get_active_broadcasts(self) -> list:
        """Get list of active/upcoming broadcasts."""
        youtube = self._get_youtube_service()
        if not youtube:
            return []

        try:
            response = youtube.liveBroadcasts().list(
                part="id,snippet,status",
                broadcastStatus="all",
                broadcastType="all",
                maxResults=25
            ).execute()

            return response.get("items", [])

        except Exception as e:
            logger.error(f"[BROADCAST] List broadcasts failed: {e}")
            return []

    async def update_broadcast_metadata(
        self,
        broadcast_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update live broadcast title and/or description via YouTube API.

        Can be called while stream is live - no interruption.

        Args:
            broadcast_id: The broadcast ID to update
            title: New title (optional, max 100 chars)
            description: New description (optional)

        Returns:
            dict with success status and updated fields
        """
        result = {"success": False, "error": None, "updated": []}

        youtube = self._get_youtube_service()
        if not youtube:
            result["error"] = "No YouTube service"
            return result

        try:
            # Get current broadcast to preserve unchanged fields
            current = youtube.liveBroadcasts().list(
                part="snippet",
                id=broadcast_id
            ).execute()

            items = current.get("items", [])
            if not items:
                result["error"] = f"Broadcast {broadcast_id} not found"
                return result

            snippet = items[0].get("snippet", {})

            # Update only provided fields
            if title:
                snippet["title"] = title[:100]  # YouTube limit
                result["updated"].append("title")
            if description:
                snippet["description"] = description
                result["updated"].append("description")

            # Execute update
            youtube.liveBroadcasts().update(
                part="snippet",
                body={
                    "id": broadcast_id,
                    "snippet": snippet
                }
            ).execute()

            logger.info(f"[BROADCAST] Updated metadata: {result['updated']}")
            result["success"] = True

        except Exception as e:
            logger.error(f"[BROADCAST] Update metadata failed: {e}")
            result["error"] = str(e)

        return result

    async def update_current_broadcast(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update the currently active broadcast's metadata.

        Finds the active broadcast automatically, then updates it.
        """
        broadcasts = await self.get_active_broadcasts()

        # Find active (live) broadcast
        active = None
        for b in broadcasts:
            status = b.get("status", {}).get("lifeCycleStatus", "")
            if status in ("live", "testing"):
                active = b
                break

        if not active:
            return {"success": False, "error": "No active broadcast found"}

        broadcast_id = active.get("id")
        return await self.update_broadcast_metadata(broadcast_id, title, description)


def generate_clickbait_title(news_headlines: list = None) -> str:
    """
    Generate a clickbait title with date and trending topics.

    Args:
        news_headlines: Optional list of current headlines to mine keywords

    Returns:
        Clickbait title string (max 100 chars)
    """
    from datetime import datetime

    date_str = datetime.now().strftime("%m/%d")

    # Base trending topics
    topics = ["Trump", "Iran", "War", "LIVE"]

    # Mine keywords from news if provided
    if news_headlines:
        hot_keywords = ["breaking", "attack", "missile", "strike", "protest", "raid"]
        for headline in news_headlines[:5]:
            for kw in hot_keywords:
                if kw.lower() in headline.lower():
                    topics.insert(0, headline.split()[0].title())
                    break

    # Build title
    hashtags = " ".join([f"#{t}" for t in topics[:4]])
    title = f"24/7 {hashtags} #AntifaFM Music - {date_str} #StopICE #music"

    return title[:100]  # YouTube limit


def generate_m2m_description(news_headlines: list = None, use_orchestrator: bool = True) -> str:
    """
    Generate M2M discoverable description with news and hashtags.

    NOTE: Uses ASCII-safe characters only to avoid UnicodeEncodeError
    on Windows cp932 encoding. No emoji - use hashtags for M2M discovery.

    Args:
        news_headlines: Current headlines to include (manual override)
        use_orchestrator: If True and no headlines provided, use NewsOrchestrator WSP 15 queue

    Returns:
        Description string with links and hashtags
    """
    from datetime import datetime

    date_str = datetime.now().strftime("%Y-%m-%d")

    # Get headlines from orchestrator if not provided
    if not news_headlines and use_orchestrator:
        try:
            from modules.platform_integration.antifafm_broadcaster.src.news_orchestrator import NewsOrchestrator
            orchestrator = NewsOrchestrator()
            news_headlines = orchestrator.get_for_description(5)
            if news_headlines:
                logger.info(f"[M2M] Using {len(news_headlines)} WSP 15 rated headlines")
        except Exception as e:
            logger.debug(f"[M2M] News orchestrator not available: {e}")

    description = f"""antifaFM - 24/7 Antifascist Radio | {date_str}

Live stream powered by FoundUps AI automation (pAVS network).

"""
    # Add news section if available
    if news_headlines and len(news_headlines) > 0:
        description += "TODAY'S HEADLINES:\n"
        for headline in news_headlines[:5]:
            description += f"- {headline}\n"
        description += "\n"

    description += """#antifaFM #LiveRadio #FoundUps #AI #0102 #pAVS
#AntifascistMusic #Resistance #Trump #Iran #War #News
#StopICE #ICEout #EpsteinFiles #TrumpFiles

LINKS:
- antifaFM: https://antifaFM.com
- FoundUps: https://foundups.com
- GitHub: https://github.com/FOUNDUPS

Powered by 0102 DAE Network - This is a FoundUp.
"""
    return description


async def test_broadcast_creation():
    """Test broadcast creation."""
    print("=" * 60)
    print("YouTube Broadcast Manager Test")
    print("=" * 60)

    manager = YouTubeBroadcastManager()

    # Verify channel first
    print("\n[TEST] Verifying channel...")
    is_valid, channel_name, error = manager._verify_channel()

    if not is_valid:
        print(f"[ERROR] Channel verification failed: {error}")
        print("\nTo fix:")
        print("1. Run: python modules/platform_integration/youtube_auth/scripts/authorize_antifafm.py")
        print("2. Select the antifaFM brand channel when prompted")
        return

    print(f"[OK] Channel: {channel_name}")

    # Create test broadcast
    print("\n[TEST] Creating broadcast...")
    result = await manager.create_live_broadcast(
        title="antifaFM Radio Test",
        description="Test broadcast - will be deleted",
        privacy="unlisted",  # Use unlisted for testing
    )

    if result.success:
        print(f"\n[SUCCESS] Broadcast created!")
        print(f"  Broadcast ID: {result.broadcast_id}")
        print(f"  Stream ID: {result.stream_id}")
        print(f"  Stream Key: {result.stream_key}")
        print(f"  RTMPS URL: {result.rtmps_url}")
        print(f"  Watch URL: {result.watch_url}")
        print("\n[NEXT] Configure OBS/FFmpeg with these settings, then:")
        print("  manager.transition_to_live(broadcast_id)")
    else:
        print(f"\n[FAILED] {result.error}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

    asyncio.run(test_broadcast_creation())
