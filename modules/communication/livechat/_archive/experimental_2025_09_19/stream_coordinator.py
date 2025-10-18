"""
Stream Coordinator - WSP-Compliant Module
WSP 40: Architectural Coherence Protocol
WSP 62: File Size Compliance (<500 lines)

Extracted from auto_moderator_dae.py for stream management.
Handles stream discovery, lifecycle, and transitions.
"""

import asyncio
import logging
import os
import time
from typing import Optional, Tuple
from modules.platform_integration.stream_resolver.src.stream_resolver import StreamResolver

logger = logging.getLogger(__name__)


class StreamCoordinator:
    """
    WSP-Compliant Stream Coordinator
    
    Extracted responsibilities:
    - Stream discovery and monitoring
    - Stream lifecycle management
    - Seamless stream transitions
    - Stream verification
    """
    
    def __init__(self, youtube_service):
        """Initialize stream coordinator."""
        logger.info("[U+1F3AC] Initializing Stream Coordinator (WSP-Compliant)")
        
        self.service = youtube_service
        self.stream_resolver = None
        self._last_stream_id = None
        self.transition_start = None
        
        # WRE Monitor integration
        self.wre_monitor = None
        try:
            from modules.infrastructure.wre_core.wre_monitor import get_monitor
            self.wre_monitor = get_monitor()
            logger.info("[0102] WRE Monitor attached to Stream Coordinator")
        except Exception as e:
            logger.debug(f"WRE Monitor not available: {e}")
            self.wre_monitor = None
        
        logger.info("[OK] Stream Coordinator initialized")
    
    def find_livestream(self) -> Optional[Tuple[str, str]]:
        """
        Find active livestream on the channel.
        Can check multiple channels if configured.
        
        Returns:
            Tuple of (video_id, live_chat_id) or None
        """
        logger.info("[SEARCH] Looking for livestream...")
        
        if not self.stream_resolver:
            self.stream_resolver = StreamResolver(self.service)
        
        # List of channels to check - monitoring both channels on same YouTube account
        channels_to_check = [
            os.getenv('CHANNEL_ID', 'UC-LSSlOZwpGIRIYihaz8zCw'),  # Move2Japan/UnDaoDu main
            os.getenv('CHANNEL_ID2', 'UCSNTUXjAgpd4sgWYP0xoJgw'),  # FoundUps channel
            # Add more channels here if needed:
            # os.getenv('BACKUP_CHANNEL_ID'),  # Additional backup channel
        ]
        
        # Filter out None values
        channels_to_check = [ch for ch in channels_to_check if ch]
        
        # Try each channel
        for channel_id in channels_to_check:
            logger.info(f"[U+1F50E] Checking channel: {channel_id[:12]}...")
            result = self.stream_resolver.resolve_stream(channel_id)
            
            if result and result[0] and result[1]:
                video_id, live_chat_id = result
                logger.info(f"[OK] Found stream on channel {channel_id[:12]}... with video ID: {video_id}")
                return video_id, live_chat_id
        
        logger.info(f"[FAIL] No active livestream found on {len(channels_to_check)} channel(s)")
        return None
    
    async def verify_stream_is_live(self, video_id: str) -> bool:
        """
        [ALERT] CRITICAL VERIFICATION: Check if YouTube stream is ACTUALLY LIVE
        This method performs multiple checks to ensure the stream is genuinely live.
        
        Args:
            video_id: YouTube video ID to verify
            
        Returns:
            True if stream is confirmed live, False otherwise
        """
        try:
            logger.info(f"[SEARCH] [LIVE VERIFICATION] Checking video ID: {video_id}")

            # Check 1: Get video details from YouTube API
            logger.info("[SEARCH] [LIVE VERIFICATION] Step 1: Getting video details...")
            response = self.service.videos().list(
                part="liveStreamingDetails,snippet,status",
                id=video_id
            ).execute()

            if not response.get("items"):
                logger.warning(f"[FORBIDDEN] [LIVE VERIFICATION] Video {video_id} not found")
                return False

            video_item = response["items"][0]
            live_details = video_item.get("liveStreamingDetails", {})
            status = video_item.get("status", {})
            snippet = video_item.get("snippet", {})

            logger.info(f"[SEARCH] [LIVE VERIFICATION] Video title: {snippet.get('title', 'Unknown')}")

            # Check 2: Verify it's actually live (has start time, no end time)
            logger.info("[SEARCH] [LIVE VERIFICATION] Step 2: Checking live status...")
            actual_start_time = live_details.get("actualStartTime")
            actual_end_time = live_details.get("actualEndTime")

            if not actual_start_time:
                logger.warning("[FORBIDDEN] [LIVE VERIFICATION] No actual start time - not live")
                return False

            if actual_end_time:
                logger.warning("[FORBIDDEN] [LIVE VERIFICATION] Has end time - stream completed")
                return False

            # Check 3: Verify privacy status (should be public for live streams)
            privacy_status = status.get("privacyStatus", "private")
            if privacy_status == "private":
                logger.warning("[FORBIDDEN] [LIVE VERIFICATION] Stream is private - cannot verify live status")
                return False

            # Check 4: Verify concurrent viewers (live streams should have viewers)
            concurrent_viewers = live_details.get("concurrentViewers", 0)
            logger.info(f"[SEARCH] [LIVE VERIFICATION] Concurrent viewers: {concurrent_viewers}")

            # All checks passed
            logger.info("[OK] [LIVE VERIFICATION] ALL CHECKS PASSED - STREAM IS LIVE!")
            logger.info(f"[OK] [LIVE VERIFICATION] Start time: {actual_start_time}")
            logger.info(f"[OK] [LIVE VERIFICATION] Privacy: {privacy_status}")
            logger.info(f"[OK] [LIVE VERIFICATION] Viewers: {concurrent_viewers}")

            return True

        except Exception as e:
            logger.error(f"[FAIL] [LIVE VERIFICATION] Error during verification: {e}")
            # On error, assume not live for safety
            return False
    
    def track_stream_transition(self, old_stream_id: str, new_stream_id: str):
        """
        Track stream transitions for WRE monitoring.
        
        Args:
            old_stream_id: Previous stream ID
            new_stream_id: New stream ID
        """
        if self.wre_monitor and self.transition_start:
            transition_time = time.time() - self.transition_start
            self.wre_monitor.track_stream_transition(old_stream_id, new_stream_id, transition_time)
            logger.info(f"[DATA] Stream transition tracked: {old_stream_id} -> {new_stream_id} ({transition_time:.1f}s)")
        
        self._last_stream_id = new_stream_id
        self.transition_start = time.time()
    
    def mark_transition_start(self):
        """Mark the start of a stream transition."""
        self.transition_start = time.time()
        logger.info("[REFRESH] Stream transition started")
    
    def clear_cache(self):
        """Clear stream resolver cache for fresh search."""
        if self.stream_resolver:
            self.stream_resolver.clear_cache()
            logger.info("[REFRESH] Stream resolver cache cleared")
    
    def get_last_stream_id(self) -> Optional[str]:
        """Get the last monitored stream ID."""
        return self._last_stream_id
    
    def is_in_transition(self) -> bool:
        """Check if currently in stream transition."""
        return self.transition_start is not None
    
    def get_transition_duration(self) -> Optional[float]:
        """Get current transition duration in seconds."""
        if self.transition_start:
            return time.time() - self.transition_start
        return None
