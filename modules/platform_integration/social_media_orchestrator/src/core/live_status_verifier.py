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

        # Stream age filtering - don't log noise about old streams
        self.max_stream_age_days = 7  # Don't log about streams older than 7 days

        # Track last status check results for orchestrator integration
        self._last_broadcast_content = None
        self._last_actual_end = None
        self._last_age_hours = None

        # Initialize Qwen intelligence for smart filtering
        self.qwen_intelligence = None
        try:
            from modules.communication.livechat.src.qwen_youtube_integration import get_qwen_youtube
            self.qwen_intelligence = get_qwen_youtube()
            self.logger.info("🤖🧠 [QWEN-STATUS] Qwen intelligence connected to LiveStatusVerifier")
        except Exception as e:
            self.logger.debug(f"🤖🧠 [QWEN-STATUS] Qwen not available: {e}")

        # Initialize duplicate prevention manager for checking posted videos
        self.duplicate_manager = None
        try:
            from .duplicate_prevention_manager import DuplicatePreventionManager
            self.duplicate_manager = DuplicatePreventionManager()
            self.logger.debug("[DB] Duplicate prevention manager connected for status filtering")
        except Exception as e:
            self.logger.debug(f"[DB] Duplicate prevention manager not available: {e}")

        # Initialize NO-QUOTA stream checker ONCE to avoid rapid re-initialization loop
        self.no_quota_checker = None
        try:
            from modules.platform_integration.stream_resolver.src.no_quota_stream_checker import NoQuotaStreamChecker
            self.no_quota_checker = NoQuotaStreamChecker()
            self.logger.debug("[NO-QUOTA] Stream checker initialized and ready for reuse")
        except Exception as e:
            self.logger.debug(f"[NO-QUOTA] Stream checker not available: {e}")

    def verify_live_status(self, video_id: str, channel_name: str = None) -> bool:
        """
        Verify if a stream is actually live using NO-QUOTA web scraping first, API as fallback

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

        # Try NO-QUOTA verification first to preserve API quota
        self.logger.info(f"[NO-QUOTA] Trying web-based verification for {video_id} to save API quota")
        no_quota_result = self._fallback_verification(video_id, channel_name)

        if no_quota_result is False:
            # NO-QUOTA says NOT live - no need to burn API quota
            self.logger.info(f"[NO-QUOTA] Confirmed {video_id} is NOT live - skipping API verification")
            self._cache_status(video_id, False)
            return False

        if no_quota_result is True:
            # NO-QUOTA says LIVE - use API for final confirmation before posting
            self.logger.info(f"[CONFIRM] {video_id} appears LIVE via web - confirming with API")
            # Continue to API verification below

        # Only reach here if NO-QUOTA said LIVE or was uncertain - use API for confirmation/verification
        try:
            from modules.platform_integration.youtube_auth.src.youtube_auth import get_authenticated_service

            youtube_service = get_authenticated_service()
            is_live = self._check_live_status_via_api(youtube_service, video_id, channel_name)

            # Cache the result
            self._cache_status(video_id, is_live)

            return is_live

        except ImportError as e:
            self.logger.error(f"[STATUS] Could not import YouTube auth: {e}")
            return False  # Can't verify without API

        except Exception as e:
            self.logger.error(f"[STATUS] Error verifying live status: {e}")
            return False  # Can't verify

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

            # Store results for orchestrator integration
            self._last_broadcast_content = live_broadcast
            self._last_actual_end = actual_end

            # Calculate age if stream has ended
            if actual_end and (live_broadcast == 'completed' or live_broadcast == 'none'):
                try:
                    end_time = datetime.fromisoformat(actual_end.replace('Z', '+00:00'))
                    self._last_age_hours = (datetime.now(end_time.tzinfo) - end_time).total_seconds() / 3600
                except Exception:
                    self._last_age_hours = None
            else:
                self._last_age_hours = None

            # FILTERING LOGIC: Check if we should skip detailed logging for old streams
            should_skip_logging = self._should_skip_detailed_logging(video_id, live_broadcast, actual_end, actual_start)

            # AUTO-MARK OLD STREAMS AS PROCESSED: Only for streams that would be posted about
            # Don't mark streams that are being filtered out (too old) - they're not worth tracking
            if not is_live and actual_end and not should_skip_logging:
                # Only auto-mark if this stream would have been considered for posting (recent enough)
                # Skip auto-marking for very old streams that are just noise
                self._conditional_auto_mark(video_id, snippet.get('title', 'Unknown'), actual_end, should_skip_logging)

            if should_skip_logging:
                if is_live:
                    self.logger.info(f"✅ [STATUS] Stream {video_id} is LIVE")
                else:
                    reason = self._get_not_live_reason(live_broadcast, actual_end, scheduled_start, actual_start)
                    self.logger.debug(f"❌ [STATUS] Stream {video_id} is NOT live (filtered): {reason}")
                return is_live

            # Detailed logging for recent/active streams only
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
            error_str = str(e).lower()
            self.logger.error(f"[STATUS] API check failed for {video_id}: {e}")

            # Check for quota exhaustion and trigger rotation
            if any(phrase in error_str for phrase in ['quota', 'limit exceeded', 'daily limit', 'rate limit']):
                self.logger.warning(f"[QUOTA] Detected quota exhaustion - triggering credential rotation")

                try:
                    # Attempt credential rotation
                    rotation_success = self.rotate_credentials()
                    if rotation_success:
                        self.logger.info(f"[QUOTA] ✅ Credential rotation successful - retrying with new credentials")

                        # Retry once with new credentials
                        try:
                            request = youtube_service.videos().list(
                                part="snippet,liveStreamingDetails",
                                id=video_id
                            )
                            response = request.execute()

                            if response.get('items'):
                                video = response['items'][0]
                                snippet = video.get('snippet', {})
                                live_broadcast = snippet.get('liveBroadcastContent', 'none')
                                is_live = live_broadcast == 'live'

                                self.logger.info(f"[QUOTA] ✅ Retry successful after rotation - {video_id} is {'LIVE' if is_live else 'NOT live'}")
                                self._cache_status(video_id, is_live)
                                return is_live
                            else:
                                self.logger.warning(f"[QUOTA] Video {video_id} not found after rotation")
                                return False

                        except Exception as retry_error:
                            self.logger.error(f"[QUOTA] ❌ Retry failed after rotation: {retry_error}")
                            return False
                    else:
                        self.logger.error(f"[QUOTA] ❌ Credential rotation failed - cannot retry")
                        return False

                except Exception as rotation_error:
                    self.logger.error(f"[QUOTA] ❌ Credential rotation error: {rotation_error}")
                    return False

            return False

    def rotate_credentials(self) -> bool:
        """
        Rotate to the next available credential set when quota is exhausted.

        This method attempts to switch to the next credential set in the rotation
        to continue operations when the current set hits quota limits.

        Returns:
            bool: True if rotation was successful, False otherwise
        """
        try:
            # Import the OAuth manager to trigger rotation
            from modules.platform_integration.utilities.oauth_management.src.oauth_manager import get_authenticated_service_with_fallback

            self.logger.info("[QUOTA] 🔄 Triggering credential rotation via OAuth manager")

            # Get a fresh service with rotation logic
            auth_result = get_authenticated_service_with_fallback()

            if auth_result:
                # Update our internal service reference
                new_service, new_creds, new_set = auth_result
                self.logger.info(f"[QUOTA] ✅ Successfully rotated to credential set: {new_set}")
                return True
            else:
                self.logger.error("[QUOTA] ❌ Credential rotation failed - no valid credentials available")
                return False

        except Exception as e:
            self.logger.error(f"[QUOTA] ❌ Error during credential rotation: {e}")
            return False

    def _should_skip_detailed_logging(self, video_id: str, broadcast_content: str,
                                     actual_end: str, actual_start: str) -> bool:
        """
        Determine if we should skip detailed logging for this stream to reduce noise

        Returns True if logging should be skipped (old stream, already processed, etc.)
        """
        # Always log live streams
        if broadcast_content == 'live':
            return False

        # Check duplicate manager first - if we've already posted this video, skip detailed logging
        if self.duplicate_manager:
            try:
                # Check if this video has been posted before
                posted_info = self.duplicate_manager.check_if_already_posted(video_id)
                if posted_info.get('already_posted', False):
                    self.logger.debug(f"[FILTER] Video {video_id} already posted - skipping detailed logging")
                    return True
            except Exception as e:
                self.logger.debug(f"[FILTER] Duplicate check failed: {e}")

        # Check stream age - skip detailed logging for old streams
        if actual_end or broadcast_content == 'completed':
            try:
                # Parse the end time
                if actual_end:
                    end_time = datetime.fromisoformat(actual_end.replace('Z', '+00:00'))
                elif actual_start and broadcast_content == 'completed':
                    # If no end time but marked completed, assume it ended after start
                    end_time = datetime.fromisoformat(actual_start.replace('Z', '+00:00'))
                else:
                    return False  # Can't determine age, log it

                # Check if stream is older than threshold
                age_days = (datetime.now(end_time.tzinfo) - end_time).days
                if age_days > self.max_stream_age_days:
                    self.logger.debug(f"[FILTER] Stream {video_id} is {age_days} days old (> {self.max_stream_age_days}) - skipping detailed logging")
                    return True

            except Exception as e:
                self.logger.debug(f"[FILTER] Age check failed: {e}")

        # Use Qwen intelligence for additional filtering
        if self.qwen_intelligence:
            try:
                # Ask Qwen if this stream is worth detailed logging
                stream_info = {
                    'video_id': video_id,
                    'broadcast_content': broadcast_content,
                    'actual_end': actual_end,
                    'actual_start': actual_start,
                    'age_hours': (datetime.now() - datetime.fromisoformat(actual_end.replace('Z', '+00:00'))).total_seconds() / 3600 if actual_end else None
                }
                should_log = self.qwen_intelligence.should_investigate_stream(stream_info)
                if not should_log:
                    self.logger.debug(f"🤖🧠 [QWEN-FILTER] Qwen recommends skipping detailed logging for {video_id}")
                    return True
            except Exception as e:
                self.logger.debug(f"🤖🧠 [QWEN-FILTER] Qwen filtering failed: {e}")

        # Default: log everything that's recent or uncertain
        return False

    def _conditional_auto_mark(self, video_id: str, title: str, actual_end: str, should_skip_logging: bool) -> None:
        """
        Conditionally mark streams as processed based on their relevance.
        Only mark streams that would have been logged in detail (recent enough to be relevant).

        Args:
            video_id: YouTube video ID
            title: Stream title
            actual_end: When the stream ended (ISO format)
            should_skip_logging: Whether detailed logging was skipped (indicates if stream is too old)
        """
        if not self.duplicate_manager:
            self.logger.debug("[AUTO-MARK] Duplicate manager not available - skipping conditional auto-mark")
            return

        # Only auto-mark streams that are detailed-logged (recent enough to be relevant)
        # Don't waste DB space on ancient streams that are just noise
        if should_skip_logging:
            self.logger.debug(f"[AUTO-MARK] Skipping auto-mark for {video_id} (too old for detailed logging)")
            return

        try:
            # Check stream age - only mark streams that ended recently (within posting window)
            if actual_end:
                end_time = datetime.fromisoformat(actual_end.replace('Z', '+00:00'))
                age_hours = (datetime.now(end_time.tzinfo) - end_time).total_seconds() / 3600

                # Mark streams that ended 1-7 days ago (within potential posting window)
                # Don't mark very recent streams (< 1 day) as they might still be relevant
                # Don't mark ancient streams (> 7 days) as they're just noise
                if 24 <= age_hours <= (7 * 24):  # 1-7 days ago
                    self.duplicate_manager.mark_as_posted(video_id, "AUTO-MARK", title, f"https://www.youtube.com/watch?v={video_id}")
                    self.logger.info(f"[AUTO-MARK] Marked ended stream {video_id} as processed (ended {age_hours:.1f} hours ago)")
                elif age_hours < 24:
                    self.logger.debug(f"[AUTO-MARK] Stream {video_id} too recent ({age_hours:.1f}h) - not auto-marking")
                else:  # age_hours > 7*24
                    self.logger.debug(f"[AUTO-MARK] Stream {video_id} too old ({age_hours:.1f}h) - not auto-marking")
            else:
                self.logger.debug(f"[AUTO-MARK] No end time for {video_id} - not auto-marking")

        except Exception as e:
            self.logger.debug(f"[AUTO-MARK] Failed to conditionally auto-mark {video_id}: {e}")

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

    def _fallback_verification(self, video_id: str, channel_name: str = None) -> Optional[bool]:
        """
        NO-QUOTA verification method using web scraping

        Args:
            video_id: YouTube video ID
            channel_name: Optional channel name

        Returns:
            True if live, False if not live, None if cannot determine (will fallback to API)
        """
        self.logger.info(f"[NO-QUOTA] Attempting web-based verification for {video_id}")

        # Reuse existing checker to avoid rapid re-initialization (StreamDB migration spam)
        if self.no_quota_checker:
            try:
                result = self.no_quota_checker.check_video_is_live(video_id, channel_name)
                is_live = result.get('is_live', False)
                self.logger.info(f"[NO-QUOTA] Web verification: {video_id} is {'LIVE' if is_live else 'NOT live'}")
                return is_live
            except Exception as e:
                self.logger.error(f"[NO-QUOTA] Checker failed: {e}")
                return None
        else:
            self.logger.warning("[NO-QUOTA] No checker available - skipping web verification")
            return None

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