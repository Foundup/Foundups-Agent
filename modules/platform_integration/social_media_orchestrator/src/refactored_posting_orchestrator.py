"""
Refactored Posting Orchestrator
Clean, modular orchestrator using extracted core components
Replaces the monolithic simple_posting_orchestrator.py
"""

import os
import logging
import threading
from typing import Dict, Optional, Any, List

# Import all core components
from .core import (
    DuplicatePreventionManager,
    LiveStatusVerifier,
    ChannelConfigurationManager,
    PlatformPostingService,
    LinkedInPage,
    XAccount,
    PostingStatus
)


class RefactoredPostingOrchestrator:
    """
    Clean orchestrator that coordinates all social media posting activities
    Uses modular core components for better maintainability
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the orchestrator with core components

        Args:
            config: Optional configuration dictionary
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = config or {}

        # Initialize core components with QWEN intelligence enabled
        self.duplicate_manager = DuplicatePreventionManager(qwen_enabled=True)
        self.status_verifier = LiveStatusVerifier()
        self.channel_config = ChannelConfigurationManager()
        self.posting_service = PlatformPostingService(
            browser_timeout=self.config.get('browser_timeout', 120)
        )

        # State
        self.is_posting = False
        self.last_posted_video = None
        self.cancel_requested = False  # 012 cancel capability
        self.current_operation = None  # Track current operation for logging

        # Log QWEN status
        if self.duplicate_manager.qwen_enabled:
            self.logger.info("[AI_BRAIN] [QWEN-ORCHESTRATOR] Intelligence features enabled")

        self.logger.info("[PASS] RefactoredPostingOrchestrator initialized with core components")

    def cancel_posting(self) -> Dict[str, Any]:
        """
        Cancel current posting operation - 012 intervention capability

        Returns:
            Status dictionary with cancellation info
        """
        if not self.is_posting:
            self.logger.info("[CANCEL] No posting in progress")
            return {'cancelled': False, 'reason': 'not_posting'}

        self.cancel_requested = True
        self.logger.warning("[012-CANCEL] Cancellation requested - aborting current posting")
        self.logger.warning(f"[012-CANCEL] Current operation: {self.current_operation}")

        return {
            'cancelled': True,
            'current_operation': self.current_operation,
            'message': 'Cancellation signal sent - posting will abort at next checkpoint'
        }

    def get_posting_status(self) -> Dict[str, Any]:
        """
        Get current posting status - for 012 monitoring

        Returns:
            Status dictionary
        """
        return {
            'is_posting': self.is_posting,
            'current_operation': self.current_operation,
            'cancel_requested': self.cancel_requested,
            'last_posted_video': self.last_posted_video
        }

    def handle_stream_detected(
        self,
        video_id: str,
        title: str,
        url: str,
        channel_name: str,
        skip_live_verification: bool = False
    ) -> Dict[str, Any]:
        """
        Main entry point for stream detection events
        Coordinates all posting activities

        Args:
            video_id: YouTube video ID
            title: Stream title
            url: Stream URL
            channel_name: Channel name/handle
            skip_live_verification: Skip redundant live status check (for streams already verified)

        Returns:
            Results dictionary with posting status
        """
        self.logger.info("[ORCHESTRATOR-TRACE] === ENTERED handle_stream_detected ===")
        self.logger.info(f"[ORCHESTRATOR-TRACE] video_id={video_id}, skip_live={skip_live_verification}")
        self.logger.info("="*80)
        self.logger.info("[CAMERA] STREAM DETECTION EVENT RECEIVED")
        self.logger.info(f"[VIDEO] Video: {video_id}")
        self.logger.info(f"[TV] Channel: {channel_name}")
        self.logger.info(f"[NOTE] Title: {title}")
        self.logger.info(f"[LINK] URL: {url}")
        self.logger.info("="*80)

        results = {
            'video_id': video_id,
            'posted': False,
            'platforms': {},
            'errors': []
        }

        # Step 1: Check if already posting
        self.logger.info(f"[ORCHESTRATOR-TRACE] Step 1: Checking is_posting flag = {self.is_posting}")
        if self.is_posting:
            self.logger.warning("[WARNING] Already posting, skipping duplicate request")
            results['errors'].append("Already processing another posting request")
            self.logger.info("[ORCHESTRATOR-TRACE] Returning early - already posting")
            return results

        # Step 2: Verify live status FIRST (before duplicate check)
        # Skip for streams already verified by live detection system
        self.logger.info(f"[ORCHESTRATOR-TRACE] Step 2: Live verification, skip={skip_live_verification}")
        if not skip_live_verification:
            live_status_result = self.status_verifier.verify_live_status(video_id)
            self.logger.info(f"[ORCHESTRATOR-TRACE] Live status result: {live_status_result}")
            if not live_status_result:
                self.logger.warning("[WARNING] Stream not verified as live, skipping")
                results['errors'].append("Stream not verified as live")
                self.logger.info("[ORCHESTRATOR-TRACE] Returning early - not live")
                return results
        else:
            self.logger.info("[SKIP] Skipping redundant live verification (already verified by detection system)")

        # Step 3: Check duplicate WITH live status information
        # This allows duplicate manager to block stale/ended content
        self.logger.info(f"[ORCHESTRATOR-TRACE] Step 3: Checking duplicate for video_id={video_id}")
        duplicate_check = self.duplicate_manager.check_if_already_posted(video_id, {
            'broadcast_content': getattr(self.status_verifier, '_last_broadcast_content', 'live'),
            'actual_end': getattr(self.status_verifier, '_last_actual_end', None),
            'age_hours': getattr(self.status_verifier, '_last_age_hours', None)
        })
        self.logger.info(f"[ORCHESTRATOR-TRACE] Duplicate check result: {duplicate_check}")

        if duplicate_check['already_posted']:
            blocked_reason = duplicate_check.get('blocked_reason', 'already posted')
            if blocked_reason == 'already_posted':
                self.logger.info("[REPEAT] Video already posted, skipping")
            else:
                self.logger.warning(f"[BLOCKED] Video blocked: {blocked_reason}")
            results['platforms'] = {
                platform: blocked_reason
                for platform in duplicate_check.get('platforms_posted', [])
            }
            self.logger.info("[ORCHESTRATOR-TRACE] Returning early - duplicate/blocked")
            return results

        # Step 4: Get channel configuration
        self.logger.info(f"[ORCHESTRATOR-TRACE] Step 4: Getting config for channel={channel_name}")
        channel_config = self.channel_config.get_channel_config(channel_name)
        self.logger.info(f"[ORCHESTRATOR-TRACE] Channel config result: {channel_config}")
        if not channel_config:
            self.logger.error(f"[FAIL] No configuration found for channel: {channel_name}")
            results['errors'].append(f"No configuration for channel: {channel_name}")
            self.logger.info("[ORCHESTRATOR-TRACE] Returning early - no config")
            return results

        if not channel_config.get('enabled', True):
            self.logger.info(f"[MUTE] Channel {channel_name} is disabled, skipping")
            results['errors'].append(f"Channel {channel_name} is disabled")
            return results

        # Step 5: QWEN Pre-posting Intelligence Check
        stream_info = {
            'video_id': video_id,
            'title': title,
            'url': url,
            'channel_name': channel_name
        }

        # Determine target platforms from channel config
        target_platforms = []
        if channel_config.get('linkedin_page'):
            target_platforms.append('linkedin')
        if channel_config.get('x_account'):
            target_platforms.append('x_twitter')

        # Get QWEN intelligence decision
        qwen_decision = self.duplicate_manager.qwen_pre_posting_check(stream_info, target_platforms)

        if qwen_decision.get('qwen_active'):
            self.logger.info("[AI_BRAIN] [QWEN-ORCHESTRATOR] Intelligence analysis complete")

            # Check if QWEN blocks posting
            if not qwen_decision['should_post']:
                self.logger.warning(f"[AI_BRAIN] [QWEN-BLOCK] Posting blocked: {qwen_decision['warnings']}")
                results['errors'].extend(qwen_decision['warnings'])
                return results

            # Update platforms based on QWEN decision
            approved_platforms = qwen_decision.get('approved_platforms', target_platforms)
            posting_delays = qwen_decision.get('delays', {})
            posting_order = qwen_decision.get('posting_order', approved_platforms)

            # Log QWEN optimizations
            for optimization in qwen_decision.get('optimizations', []):
                self.logger.info(f"[AI_BRAIN] [QWEN-OPTIMIZE] {optimization}")
        else:
            # QWEN not active, use default behavior
            approved_platforms = target_platforms
            posting_delays = {}
            posting_order = target_platforms

        # Step 6: Post to platforms in background
        self.logger.info("[RELEASE] Starting background posting thread")
        posting_thread = threading.Thread(
            target=self._post_to_platforms_background,
            args=(video_id, title, url, channel_config, results, approved_platforms, posting_delays, posting_order),
            daemon=True
        )
        posting_thread.start()

        # Return immediately (posting happens in background)
        return results

    def _post_to_platforms_background(
        self,
        video_id: str,
        title: str,
        url: str,
        channel_config: Dict[str, Any],
        results: Dict[str, Any],
        approved_platforms: List[str] = None,
        posting_delays: Dict[str, float] = None,
        posting_order: List[str] = None
    ):
        """
        Background thread for posting to platforms with QWEN intelligence

        Args:
            video_id: YouTube video ID
            title: Stream title
            url: Stream URL
            channel_config: Channel configuration
            results: Results dictionary to update
            approved_platforms: QWEN-approved platforms
            posting_delays: QWEN-recommended delays per platform
            posting_order: QWEN-optimized posting order
        """
        try:
            self.is_posting = True
            self.cancel_requested = False  # Reset cancel flag
            self.current_operation = f"Posting {video_id}"

            # Use QWEN parameters if available
            posting_delays = posting_delays or {}
            posting_order = posting_order or []

            # Get platform accounts (Facebook posting disabled/not implemented)
            linkedin_page = channel_config.get('linkedin_page')
            x_account = channel_config.get('x_account')
            # facebook_account = None  # Facebook posting DISABLED

            if not linkedin_page and not x_account:
                self.logger.error("[FAIL] No platform accounts configured")
                results['errors'].append("No platform accounts configured")
                return

            # IMPLEMENT PROPER HANDOFF: LinkedIn first, then X ONLY if LinkedIn succeeds
            linkedin_success = False
            x_success = False

            # POSTING FINGERPRINT: Add delays for process visibility
            import time

            # Post to LinkedIn first
            if linkedin_page:
                # CHECKPOINT: Check cancellation before LinkedIn
                if self.cancel_requested:
                    self.logger.warning("[012-CANCEL] Posting cancelled before LinkedIn")
                    results['errors'].append("Posting cancelled by 012")
                    return

                self.current_operation = "LinkedIn posting"
                self.logger.info("[BLUE] [FINGERPRINT-1] STARTING LINKEDIN POSTING SEQUENCE")
                time.sleep(1)  # 1s delay for visibility

                # Apply QWEN delay for LinkedIn if specified
                if 'linkedin' in posting_delays and posting_delays['linkedin'] > 0:
                    self.logger.info(f"[AI_BRAIN] [QWEN-DELAY] Waiting {posting_delays['linkedin']:.0f}s for LinkedIn")
                    time.sleep(posting_delays['linkedin'])

                self.logger.info("[BLUE] [FINGERPRINT-2] Calling LinkedIn posting service...")
                time.sleep(0.5)

                linkedin_result = self.posting_service.post_to_linkedin(
                    title=title,
                    url=url,
                    linkedin_page=linkedin_page
                )

                self.logger.info(f"[BLUE] [FINGERPRINT-3] LinkedIn result: {linkedin_result.status.value}")
                time.sleep(0.5)

                results['platforms']['linkedin'] = linkedin_result.status.value
                linkedin_success = linkedin_result.status == PostingStatus.SUCCESS

                # Update QWEN monitoring
                self.duplicate_manager.qwen_monitor_posting_progress(
                    f"{video_id}_linkedin", 'linkedin', linkedin_result.status, {'result': linkedin_result.status.value}
                )

                if linkedin_success:
                    self.logger.info("[CUT]E[FINGERPRINT-4] LINKEDIN SUCCESS - proceeding to X")
                    results['posted'] = True
                    self.last_posted_video = video_id
                    time.sleep(1)  # Pause to show success

                    # Mark as posted immediately to prevent duplicates
                    self.duplicate_manager.mark_as_posted(
                        video_id=video_id,
                        platform='linkedin',
                        title=title,
                        url=url
                    )
                    self.logger.info("[CUT]E[FINGERPRINT-5] LinkedIn marked as posted")
                else:
                    self.logger.warning("[FLOWER]E[FINGERPRINT-4] LINKEDIN FAILED - X will be skipped")
                    results['errors'].append(f"LinkedIn failed: {linkedin_result.message}")

                    # Mark as posted (FAILED status) to prevent infinite retries
                    self.duplicate_manager.mark_as_posted(
                        video_id=video_id,
                        platform='linkedin',
                        title=title,
                        url=url
                    )
                    self.logger.info("[CUT]E[FINGERPRINT-4B] LinkedIn marked as FAILED to prevent retries")
                    time.sleep(1)

            # Post to X ONLY if LinkedIn succeeded
            if x_account:
                if linkedin_success:
                    # CHECKPOINT: Check cancellation before X
                    if self.cancel_requested:
                        self.logger.warning("[012-CANCEL] Posting cancelled before X/Twitter")
                        results['errors'].append("Posting cancelled by 012 (LinkedIn completed)")
                        return

                    self.current_operation = "X/Twitter posting"
                    self.logger.info("[BIRD] [FINGERPRINT-6] STARTING X/TWITTER POSTING SEQUENCE (LinkedIn prerequisite met)")
                    time.sleep(1)

                    # Apply QWEN delay for X if specified
                    if 'x_twitter' in posting_delays and posting_delays['x_twitter'] > 0:
                        self.logger.info(f"[AI_BRAIN] [QWEN-DELAY] Waiting {posting_delays['x_twitter']:.0f}s for X/Twitter")
                        time.sleep(posting_delays['x_twitter'])

                    self.logger.info("[BIRD] [FINGERPRINT-7] Calling X/Twitter posting service...")
                    time.sleep(0.5)

                    x_result = self.posting_service.post_to_x(
                        title=title,
                        url=url,
                        x_account=x_account
                    )

                    self.logger.info(f"[BIRD] [FINGERPRINT-8] X/Twitter result: {x_result.status.value}")
                    time.sleep(0.5)

                    results['platforms']['x_twitter'] = x_result.status.value
                    x_success = x_result.status == PostingStatus.SUCCESS

                    # Update QWEN monitoring
                    self.duplicate_manager.qwen_monitor_posting_progress(
                        f"{video_id}_x_twitter", 'x_twitter', x_result.status, {'result': x_result.status.value}
                    )

                    if x_success:
                        self.logger.info("[CUT]E[FINGERPRINT-9] X/TWITTER SUCCESS")
                        time.sleep(1)

                        # Mark as posted immediately to prevent duplicates
                        self.duplicate_manager.mark_as_posted(
                            video_id=video_id,
                            platform='x_twitter',
                            title=title,
                            url=url
                        )
                        self.logger.info("[CUT]E[FINGERPRINT-10] X/Twitter marked as posted")
                    else:
                        self.logger.warning(f"[FLOWER]E[FINGERPRINT-9] X/TWITTER FAILED: {x_result.message}")
                        results['errors'].append(f"X/Twitter failed: {x_result.message}")

                else:
                    self.logger.warning("[SKIP][FINGERPRINT-6] SKIPPING X/TWITTER - LinkedIn prerequisite not met")
                    results['platforms']['x_twitter'] = 'skipped_linkedin_failed'
                    results['errors'].append("X/Twitter skipped - LinkedIn posting failed")
                    time.sleep(1)

            # Mark as posted if successful
            platforms_posted = []
            if linkedin_success:
                platforms_posted.append('linkedin')
            if x_success:
                platforms_posted.append('x_twitter')

                if platforms_posted:
                    # Mark each platform as posted individually
                    for platform in platforms_posted:
                        self.duplicate_manager.mark_as_posted(
                            video_id=video_id,
                            platform=platform,
                            title=title,
                            url=url
                        )
                    results['posted'] = True
                    self.last_posted_video = video_id
                else:
                    # Both failed but don't mark - allow retry
                    self.logger.warning(f"[WARNING] Both platforms failed for {video_id}, will retry on next detection")

            # Post to LinkedIn only
            elif linkedin_page:
                self.logger.info("[BLUE_BOOK] Posting to LinkedIn only")

                linkedin_result = self.posting_service.post_to_linkedin(
                    title=title,
                    url=url,
                    linkedin_page=linkedin_page
                )

                results['platforms']['linkedin'] = linkedin_result.status.value

                if linkedin_result.status == PostingStatus.SUCCESS:
                    self.duplicate_manager.mark_as_posted(
                        video_id=video_id,
                        platform='linkedin',
                        title=title,
                        url=url
                    )
                    results['posted'] = True
                    self.last_posted_video = video_id
                else:
                    # Check if user cancelled (closed browser window)
                    error_msg = linkedin_result.message or ""
                    if 'unknown error' in error_msg.lower() or 'closed' in error_msg.lower():
                        # User cancelled - mark as attempted to prevent retry
                        self.logger.warning(f"[BLOCKED] LinkedIn cancelled by user for {video_id}, marking as attempted")
                        self.duplicate_manager.mark_as_posted(
                            video_id=video_id,
                            platform='linkedin_cancelled',
                            title=title,
                            url=url
                        )
                    else:
                        # Real error - allow retry
                        self.logger.warning(f"[WARNING] LinkedIn failed for {video_id}, will retry on next detection")

            # Post to X only
            elif x_account:
                self.logger.info("[BIRD] Posting to X/Twitter only")

                x_result = self.posting_service.post_to_x(
                    title=title,
                    url=url,
                    x_account=x_account
                )

                results['platforms']['x_twitter'] = x_result.status.value

                if x_result.status == PostingStatus.SUCCESS:
                    self.duplicate_manager.mark_as_posted(
                        video_id=video_id,
                        platform='x_twitter',
                        title=title,
                        url=url
                    )
                    results['posted'] = True
                    self.last_posted_video = video_id
                else:
                    # Mark as attempted even on failure to prevent infinite retries
                    self.logger.warning(f"[WARNING] X/Twitter failed for {video_id}, marking as attempted")
                    self.duplicate_manager.mark_as_posted(
                        video_id=video_id,
                        platform='failed_x',
                        title=title,
                        url=url
                    )

            # Log final results
            self.logger.info("="*60)
            self.logger.info("[STATS] POSTING COMPLETE")
            self.logger.info(f"[PASS] Success: {results['posted']}")
            self.logger.info(f"[MOBILE] Platforms: {results['platforms']}")
            self.logger.info("="*60)

        except Exception as e:
            self.logger.error(f"[FAIL] Background posting error: {str(e)}")
            results['errors'].append(str(e))
            # DO NOT mark as failed_attempt - let it retry naturally
            # Browser-based posting should be allowed to retry
            self.logger.info("[WARNING] Error occurred but NOT marking as failed - will retry on next detection")
        finally:
            was_cancelled = self.cancel_requested
            self.is_posting = False
            self.cancel_requested = False
            self.current_operation = None
            if was_cancelled:
                self.logger.info("[012-CANCEL] Posting operation cleaned up after cancellation")

    def get_posting_stats(self) -> Dict[str, Any]:
        """
        Get posting statistics

        Returns:
            Statistics dictionary
        """
        stats = self.duplicate_manager.get_posting_stats()
        stats['is_posting'] = self.is_posting
        stats['last_posted_video'] = self.last_posted_video
        stats['channel_config'] = self.channel_config.get_configuration_summary()

        return stats

    def handle_multiple_streams_detected(self, detected_streams: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Handle multiple detected streams with proper priority and sequencing.
        This is the proper WSP 3 compliant handoff from livechat DAE.

        Args:
            detected_streams: List of stream dictionaries with keys:
                - video_id: YouTube video ID
                - channel_id: YouTube channel ID
                - channel_name: Human-readable channel name
                - live_chat_id: Optional chat ID

        Returns:
            Results dictionary with posting status for all streams
        """
        import time

        self.logger.info("="*80)
        self.logger.info("[ORCHESTRATOR] MULTIPLE STREAMS DETECTED")
        self.logger.info(f"[ORCHESTRATOR] Processing {len(detected_streams)} streams")
        self.logger.info("="*80)

        results = {
            'success': True,
            'streams_processed': 0,
            'errors': [],
            'stream_results': {}
        }

        # Deduplicate by video_id first (safety check)
        unique_videos = {}
        for stream in detected_streams:
            video_id = stream.get('video_id')
            if video_id and video_id not in unique_videos:
                unique_videos[video_id] = stream
            elif video_id:
                self.logger.warning(f"[DUPLICATE] Ignoring duplicate stream {video_id} from {stream.get('channel_name')}")

        # Use only unique streams
        unique_streams = list(unique_videos.values())

        if len(unique_streams) != len(detected_streams):
            self.logger.info(f"[DEDUP] Reduced {len(detected_streams)} streams to {len(unique_streams)} unique streams")

        # Sort streams by priority: Move2Japan -> UnDaoDu -> FoundUps
        priority_order = {
            'UCklMTNnu5POwRmQsg5JJumA': 1,  # Move2Japan
            'UCSNTUXjAgpd4sgWYP0xoJgw': 2,   # UnDaoDu
            'UC-LSSlOZwpGIRIYihaz8zCw': 3,   # FoundUps
            'UC8NMhWbOE9OVJF0V4DRmNnQ': 3,   # FoundUps alt
        }

        sorted_streams = sorted(
            unique_streams,
            key=lambda s: priority_order.get(s['channel_id'], 999)
        )

        # Process each stream with proper delays
        for idx, stream in enumerate(sorted_streams, 1):
            video_id = stream['video_id']
            channel_id = stream['channel_id']
            channel_name = stream['channel_name']

            # BLOCK TEST VIDEOS from posting
            if video_id and 'TEST' in video_id.upper():
                self.logger.warning(f"[SKIP] [{idx}/{len(sorted_streams)}] Skipping TEST video: {video_id}")
                continue

            self.logger.info(f"[{idx}/{len(sorted_streams)}] Processing {channel_name} stream...")

            # Build stream URL
            stream_url = f"https://www.youtube.com/watch?v={video_id}"

            # Use actual stream title from detection (not generic)
            stream_title = stream.get('title', f"{channel_name} Live Stream")

            # Add hashtags for social media visibility
            if '#' not in stream_title:  # Only add if not already present
                stream_title = f"{stream_title} #YouTube #Live #Streaming"

            self.logger.info(f"[NOTE] Post content: {stream_title}")

            # Handle this stream
            result = self.handle_stream_detected(
                video_id=video_id,
                title=stream_title,
                url=stream_url,
                channel_name=channel_name,  # Pass channel name for config lookup (NOT channel_id which is None for cached streams)
                skip_live_verification=True  # Skip redundant verification for streams already verified by detection system
            )

            results['stream_results'][channel_name] = result

            if result.get('posted'):
                results['streams_processed'] += 1
                self.logger.info(f"[SUCCESS] {channel_name} posted successfully")
            else:
                self.logger.warning(f"[WARNING] {channel_name} posting issues: {result.get('errors')}")
                results['errors'].extend(result.get('errors', []))

            # Add delay between posts (except after last one)
            if idx < len(sorted_streams):
                delay_seconds = 15
                self.logger.info(f"[DELAY] Waiting {delay_seconds}s before next post...")
                time.sleep(delay_seconds)

        # Summary
        self.logger.info("="*60)
        self.logger.info("[ORCHESTRATOR] POSTING SEQUENCE COMPLETE")
        self.logger.info(f"[ORCHESTRATOR] Processed: {results['streams_processed']}/{len(detected_streams)} streams")
        if results['errors']:
            self.logger.warning(f"[ORCHESTRATOR] Errors: {results['errors']}")
        self.logger.info("="*60)

        return results

    def clear_live_cache(self, video_id: Optional[str] = None):
        """
        Clear live status cache

        Args:
            video_id: Optional specific video ID to clear
        """
        if video_id:
            self.status_verifier.clear_cache(video_id)
        else:
            self.status_verifier.clear_cache()

    def validate_configuration(self) -> Dict[str, Any]:
        """
        Validate all component configurations

        Returns:
            Validation results
        """
        validation = {
            'valid': True,
            'components': {}
        }

        # Validate posting service
        posting_validation = self.posting_service.validate_configuration()
        validation['components']['posting_service'] = posting_validation
        if not posting_validation['valid']:
            validation['valid'] = False

        # Check channel configurations
        channels = self.channel_config.get_enabled_channels()
        validation['components']['channels'] = {
            'enabled': channels,
            'count': len(channels)
        }
        if not channels:
            validation['valid'] = False

        return validation


# Singleton instance
_orchestrator_instance = None


def get_orchestrator() -> RefactoredPostingOrchestrator:
    """
    Get singleton orchestrator instance

    Returns:
        RefactoredPostingOrchestrator instance
    """
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = RefactoredPostingOrchestrator()
    return _orchestrator_instance


# Public API for backward compatibility
def handle_stream_detected(video_id: str, title: str, url: str, channel_name: str) -> Dict[str, Any]:
    """
    Public API for stream detection events
    Maintains backward compatibility with existing code

    Args:
        video_id: YouTube video ID
        title: Stream title
        url: Stream URL
        channel_name: Channel name/handle

    Returns:
        Results dictionary
    """
    orchestrator = get_orchestrator()
    return orchestrator.handle_stream_detected(video_id, title, url, channel_name)