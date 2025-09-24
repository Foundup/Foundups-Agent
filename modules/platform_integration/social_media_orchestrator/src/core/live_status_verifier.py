"""
Live Status Verifier
Handles YouTube live stream status verification
Extracted from simple_posting_orchestrator.py for better separation of concerns
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any


class LiveStatusVerifier:
    """Verifies if YouTube streams are actually live"""

    def __init__(self):
        """Initialize live status verifier"""
        self.logger = logging.getLogger(self.__class__.__name__)

        # Cache for live status to avoid repeated checks
        self._live_status_cache = {}
        self._cache_duration = timedelta(minutes=5)

    def verify_live_status(self, video_id: str, channel_name: str = None) -> bool:
        """
        Verify if a stream is actually live using the YouTube API

        Args:
            video_id: YouTube video ID
            channel_name: Optional channel name for logging

        Returns:
            True if stream is live, False otherwise
        """
        # Check cache first
        cached_result = self._get_cached_status(video_id)
        if cached_result is not None:
            self.logger.info(f"[CACHE] Using cached live status for {video_id}: {cached_result}")
            return cached_result

        # Import here to avoid circular dependencies
        try:
            from modules.platform_integration.youtube_auth.src.youtube_auth import get_authenticated_service

            youtube_service = get_authenticated_service()
            is_live = self._check_live_status_via_api(youtube_service, video_id, channel_name)

            # Cache the result
            self._cache_status(video_id, is_live)

            return is_live

        except ImportError as e:
            self.logger.error(f"[STATUS] Could not import YouTube auth: {e}")
            return self._fallback_verification(video_id, channel_name)

        except Exception as e:
            self.logger.error(f"[STATUS] Error verifying live status: {e}")
            return self._fallback_verification(video_id, channel_name)

    def _check_live_status_via_api(self, youtube_service, video_id: str, channel_name: str = None) -> bool:
        """
        Check live status using YouTube API

        Args:
            youtube_service: Authenticated YouTube service
            video_id: YouTube video ID
            channel_name: Optional channel name for logging

        Returns:
            True if stream is live
        """
        try:
            request = youtube_service.videos().list(
                part="snippet,liveStreamingDetails",
                id=video_id
            )
            response = request.execute()

            if not response.get('items'):
                self.logger.warning(f"[STATUS] Video {video_id} not found")
                return False

            video = response['items'][0]
            snippet = video.get('snippet', {})
            live_details = video.get('liveStreamingDetails', {})

            # Check live broadcast content
            live_broadcast = snippet.get('liveBroadcastContent', 'none')
            is_live = live_broadcast == 'live'

            # Additional checks
            actual_start = live_details.get('actualStartTime')
            actual_end = live_details.get('actualEndTime')
            scheduled_start = live_details.get('scheduledStartTime')

            self.logger.info(f"[STATUS] Video {video_id} status:")
            self.logger.info(f"  • Live broadcast content: {live_broadcast}")
            self.logger.info(f"  • Title: {snippet.get('title', 'Unknown')}")

            if channel_name:
                self.logger.info(f"  • Channel: {channel_name}")

            if actual_start:
                self.logger.info(f"  • Started at: {actual_start}")
            if actual_end:
                self.logger.info(f"  • Ended at: {actual_end}")
            elif scheduled_start and not actual_start:
                self.logger.info(f"  • Scheduled for: {scheduled_start}")

            if is_live:
                self.logger.info(f"✅ [STATUS] Stream {video_id} is LIVE")
            else:
                reason = self._get_not_live_reason(live_broadcast, actual_end, scheduled_start, actual_start)
                self.logger.info(f"❌ [STATUS] Stream {video_id} is NOT live: {reason}")

            return is_live

        except Exception as e:
            self.logger.error(f"[STATUS] API check failed for {video_id}: {e}")
            return False

    def _get_not_live_reason(self, broadcast_content: str, actual_end: str,
                             scheduled_start: str, actual_start: str) -> str:
        """Get human-readable reason why stream is not live"""
        if broadcast_content == 'completed' or actual_end:
            return "Stream has ended"
        elif broadcast_content == 'upcoming' or (scheduled_start and not actual_start):
            return "Stream is scheduled but not started"
        elif broadcast_content == 'none':
            return "Not a live stream"
        else:
            return f"Unknown status: {broadcast_content}"

    def _fallback_verification(self, video_id: str, channel_name: str = None) -> bool:
        """
        Fallback verification method when API is not available

        Args:
            video_id: YouTube video ID
            channel_name: Optional channel name

        Returns:
            True if we should assume stream is live (conservative approach)
        """
        self.logger.warning(f"[STATUS] Using fallback verification for {video_id}")

        # Try using stream resolver if available
        try:
            from modules.platform_integration.stream_resolver.src.no_quota_stream_checker import NoQuotaStreamChecker

            checker = NoQuotaStreamChecker()
            is_live = checker.check_if_live(f"https://www.youtube.com/watch?v={video_id}")

            self.logger.info(f"[STATUS] NoQuotaStreamChecker says {video_id} is {'LIVE' if is_live else 'NOT live'}")
            return is_live

        except ImportError:
            self.logger.warning("[STATUS] NoQuotaStreamChecker not available")
        except Exception as e:
            self.logger.error(f"[STATUS] NoQuotaStreamChecker failed: {e}")

        # Conservative approach: assume it's live if we can't verify
        self.logger.warning(f"[STATUS] Cannot verify status, assuming {video_id} is LIVE (conservative)")
        return True

    def verify_live_status_manually(self) -> bool:
        """
        Manual verification prompt for user

        Returns:
            True if user confirms stream is live
        """
        self.logger.info("="*50)
        self.logger.info("🔍 MANUAL LIVE STATUS VERIFICATION REQUIRED")
        self.logger.info("="*50)

        try:
            response = input("\n>>> Is the stream currently LIVE? (yes/no): ").strip().lower()
            is_live = response in ['yes', 'y', 'true', '1']

            if is_live:
                self.logger.info("✅ User confirmed: Stream is LIVE")
            else:
                self.logger.info("❌ User confirmed: Stream is NOT live")

            return is_live

        except KeyboardInterrupt:
            self.logger.info("\n⏹️ Manual verification cancelled")
            return False
        except Exception as e:
            self.logger.error(f"Error during manual verification: {e}")
            return False

    def _get_cached_status(self, video_id: str) -> Optional[bool]:
        """
        Get cached live status if available and not expired

        Args:
            video_id: YouTube video ID

        Returns:
            Cached status or None if not available/expired
        """
        if video_id in self._live_status_cache:
            cached_time, cached_status = self._live_status_cache[video_id]
            if datetime.now() - cached_time < self._cache_duration:
                return cached_status

        return None

    def _cache_status(self, video_id: str, is_live: bool) -> None:
        """
        Cache the live status for a video

        Args:
            video_id: YouTube video ID
            is_live: Live status to cache
        """
        self._live_status_cache[video_id] = (datetime.now(), is_live)
        self.logger.debug(f"[CACHE] Cached status for {video_id}: {is_live}")

    def clear_cache(self, video_id: str = None) -> None:
        """
        Clear cached status

        Args:
            video_id: Specific video to clear, or None to clear all
        """
        if video_id:
            self._live_status_cache.pop(video_id, None)
            self.logger.info(f"[CACHE] Cleared cache for {video_id}")
        else:
            self._live_status_cache.clear()
            self.logger.info("[CACHE] Cleared all cached statuses")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'cached_videos': len(self._live_status_cache),
            'cache_duration_minutes': self._cache_duration.total_seconds() / 60,
            'cached_ids': list(self._live_status_cache.keys())
        }