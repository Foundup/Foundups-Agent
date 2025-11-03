#!/usr/bin/env python3
"""
Simple Social Media Posting Orchestrator
WSP Compliant: Separation of concerns - handles posting logic for all DAE modules

This orchestrator provides a clean interface for any module (YouTube, etc.)
to post to social media without handling browser automation directly.

Implements sequential posting to prevent browser conflicts.

NAVIGATION: Posts verified stream events to LinkedIn and X/Twitter.
-> Called by: modules/platform_integration/stream_resolver/src/stream_resolver.py::_trigger_social_media_post
-> Delegates to: LinkedInPoster, XPoster, content/content_orchestrator.py
-> Related: NAVIGATION.py -> MODULE_GRAPH["core_flows"]["stream_detection_flow"]
-> Quick ref: NAVIGATION.py -> NEED_TO["post to linkedin/twitter"]
"""

import asyncio
import logging
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import threading

logger = logging.getLogger(__name__)

# WSP 77: Agent Coordination - Import child DAE adapters
try:
    from .core.x_twitter_dae_adapter import XTwitterDAEAdapter
    X_ADAPTER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"X Twitter DAE Adapter not available: {e}")
    X_ADAPTER_AVAILABLE = False

# AI Delegation imports (fallback when Qwen/Gemma unavailable)
try:
    from .ai_delegation_orchestrator import get_ai_delegation_orchestrator
    AI_DELEGATION_AVAILABLE = True
except ImportError as e:
    logger.warning(f"AI Delegation Orchestrator not available: {e}")
    AI_DELEGATION_AVAILABLE = False

# Global lock for thread-safe browser operations (X/Twitter)
_POSTER_LOCK = threading.Lock()
_GLOBAL_X_POSTER_FOUNDUPS = None  # Global singleton for @Foundups X account
_GLOBAL_X_POSTER_GEOZAI = None    # Global singleton for @GeozeAi X account


class Platform(Enum):
    """Supported social media platforms"""
    LINKEDIN = "linkedin"
    X_TWITTER = "x_twitter"


@dataclass
class PostResult:
    """Result of a single platform post"""
    success: bool
    platform: Platform
    message: str
    timestamp: datetime
    url: Optional[str] = None


@dataclass
class PostResponse:
    """Response containing results from all platforms"""
    request_id: str
    results: List[PostResult]
    success_count: int = 0
    failure_count: int = 0
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class SimplePostingOrchestrator:
    """
    Simple orchestrator for posting to social media platforms.
    Handles duplicate prevention and sequential posting.
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.request_counter = 0
        self.posted_streams = self._load_posted_history()
        self.posting_in_progress = set()  # Prevent concurrent posting of same stream
        self.channel_config = self._load_channel_configuration()

        # SINGLETON POSTER INSTANCES - Reuse same browser sessions
        self._linkedin_poster = None
        self._x_poster = None

        # WSP 77: Child DAE Adapters - New architecture
        self._x_twitter_dae_adapter = None
        self._initialize_child_dae_adapters()

        # Register cleanup on exit
        import atexit
        atexit.register(self._cleanup_browsers)
        atexit.register(self._cleanup_child_daes)

    def _initialize_child_dae_adapters(self):
        """Initialize child DAE adapters (WSP 77 Agent Coordination)"""
        if X_ADAPTER_AVAILABLE:
            try:
                self._x_twitter_dae_adapter = XTwitterDAEAdapter(parent_orchestrator=self)
                self.logger.info("X Twitter child DAE adapter initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize X Twitter child DAE adapter: {e}")
                self._x_twitter_dae_adapter = None
        else:
            self.logger.warning("X Twitter child DAE adapter not available")

    def _cleanup_child_daes(self):
        """Cleanup child DAE adapters"""
        if self._x_twitter_dae_adapter:
            try:
                asyncio.run(self._x_twitter_dae_adapter.cleanup())
            except Exception as e:
                self.logger.error(f"Child DAE cleanup error: {e}")

    async def authenticate_child_dae(self, platform: str, credentials: Dict[str, Any]) -> bool:
        """
        Authenticate child DAE for platform (WSP 77 Agent Coordination)

        Args:
            platform: Platform identifier ('x_twitter', 'linkedin')
            credentials: Authentication credentials

        Returns:
            bool: Authentication success
        """
        if platform.lower() == 'x_twitter' and self._x_twitter_dae_adapter:
            try:
                self.logger.info(f"[AUTH] Authenticating X Twitter child DAE...")
                success = await self._x_twitter_dae_adapter.authenticate(credentials)
                if success:
                    self.logger.info("[AUTH] X Twitter child DAE authenticated successfully")
                else:
                    self.logger.error("[AUTH] X Twitter child DAE authentication failed")
                return success
            except Exception as e:
                self.logger.error(f"[AUTH] X Twitter child DAE authentication error: {e}")
                return False
        else:
            self.logger.warning(f"[AUTH] Child DAE authentication not available for platform: {platform}")
            return False

    def _load_channel_configuration(self) -> Dict[str, Any]:
        """Load channel routing configuration from JSON file"""
        import json
        config_path = os.path.join(
            os.path.dirname(__file__),
            '../config/channel_routing.json'
        )

        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding="utf-8") as f:
                    return json.load(f)
            else:
                self.logger.warning(f"[CONFIG] Channel routing config not found at {config_path}")
        except Exception as e:
            self.logger.error(f"[CONFIG] Error loading channel configuration: {e}")

        # Return default configuration if file not found
        return {
            "channel_routing": {},
            "default_routing": {
                "linkedin_page_id": "1263645",
                "x_account": "X_Acc2"
            }
        }

    def _get_x_account_for_linkedin_page(self, linkedin_page: str) -> bool:
        """Determine if we should use FoundUps X account based on LinkedIn page.

        Returns:
            True to use FoundUps account (X_Acc2), False to use GeozeAi (X_Acc1)
        """
        # Find the channel routing that matches this LinkedIn page
        for channel_id, config in self.channel_config.get('channel_routing', {}).items():
            if config.get('linkedin_page_id') == linkedin_page:
                x_account = config.get('x_account', 'X_Acc2')
                # Return True for FoundUps (X_Acc2), False for GeozeAi (X_Acc1)
                return x_account == 'X_Acc2'

        # Default to FoundUps account
        return True

    def _cleanup_browsers(self):
        """Clean up browser instances on exit"""
        global _GLOBAL_LINKEDIN_POSTER, _GLOBAL_X_POSTER

        try:
            if _GLOBAL_LINKEDIN_POSTER and hasattr(_GLOBAL_LINKEDIN_POSTER, 'driver'):
                if _GLOBAL_LINKEDIN_POSTER.driver:
                    try:
                        _GLOBAL_LINKEDIN_POSTER.driver.quit()
                        self.logger.info("[CLEANUP] LinkedIn browser closed")
                    except:
                        pass  # Browser already closed
                _GLOBAL_LINKEDIN_POSTER = None

            if _GLOBAL_X_POSTER_FOUNDUPS and hasattr(_GLOBAL_X_POSTER_FOUNDUPS, 'driver'):
                if _GLOBAL_X_POSTER_FOUNDUPS.driver:
                    try:
                        _GLOBAL_X_POSTER_FOUNDUPS.driver.quit()
                        self.logger.info("[CLEANUP] FoundUps X browser closed")
                    except:
                        pass  # Browser already closed
                _GLOBAL_X_POSTER_FOUNDUPS = None

            if _GLOBAL_X_POSTER_GEOZAI and hasattr(_GLOBAL_X_POSTER_GEOZAI, 'driver'):
                if _GLOBAL_X_POSTER_GEOZAI.driver:
                    try:
                        _GLOBAL_X_POSTER_GEOZAI.driver.quit()
                        self.logger.info("[CLEANUP] GeozeAi X browser closed")
                    except:
                        pass  # Browser already closed
                _GLOBAL_X_POSTER_GEOZAI = None
        except Exception as e:
            self.logger.debug(f"[CLEANUP] Error during cleanup: {e}")
    
    async def post_stream_notification(self, stream_title: str, stream_url: str,
                                     platforms: Optional[List[Platform]] = None,
                                     linkedin_page: str = None) -> PostResponse:
        """
        Post stream notification to social media platforms.

        SIMPLIFIED: Trusts the caller's stream detection.
        - No redundant API verification (scraping already detected it)
        - Prevents duplicate posting via cache
        - Clear logging at every step
        """
        self.request_counter += 1
        request_id = f"stream_post_{self.request_counter}_{datetime.now().strftime('%H%M%S')}"

        if platforms is None:
            platforms = [Platform.LINKEDIN, Platform.X_TWITTER]

        # Extract video ID from URL for duplicate tracking
        import re
        video_id_match = re.search(r'[?&]v=([^&]+)', stream_url)
        video_id = video_id_match.group(1) if video_id_match else stream_url

        # CRITICAL: Check for duplicate posting FIRST
        logger.info("="*80)
        logger.info(f"[ORCHESTRATOR] [TARGET] SOCIAL MEDIA POSTING REQUEST")
        logger.info(f"[ORCHESTRATOR] [U+1F4FA] Stream: {stream_title}")
        logger.info(f"[ORCHESTRATOR] [LINK] URL: {stream_url}")
        logger.info(f"[ORCHESTRATOR] �E Video ID: {video_id}")
        logger.info("="*80)

        # Check which platforms have already posted (per-platform duplicate prevention)
        platforms_to_post = []
        platforms_already_posted = []

        if video_id in self.posted_streams:
            posted_info = self.posted_streams[video_id]
            previously_posted = posted_info.get('platforms_posted', [])

            for platform in platforms:
                if platform.value in previously_posted:
                    platforms_already_posted.append(platform)
                    logger.info(f"[ORCHESTRATOR] [U+2701]E{platform.value} already posted at {posted_info['timestamp']}")
                else:
                    platforms_to_post.append(platform)
                    logger.info(f"[ORCHESTRATOR] [U+1F4F1] {platform.value} not yet posted - will attempt")
        else:
            # New stream - post to all platforms
            platforms_to_post = platforms
            logger.info(f"[ORCHESTRATOR] [U+2701]ENEW STREAM - Will post to all platforms")

        # If all platforms already posted, return early
        if not platforms_to_post:
            logger.warning(f"[ORCHESTRATOR] [U+1F6E1]�E�EALL PLATFORMS ALREADY POSTED")
            return PostResponse(
                request_id=request_id,
                results=[
                    PostResult(
                        success=False,
                        platform=platform,
                        message=f"Already posted at {self.posted_streams[video_id]['timestamp']}",
                        timestamp=datetime.now()
                    ) for platform in platforms_already_posted
                ],
                success_count=0,
                failure_count=len(platforms_already_posted)
            )

        # Check if posting is already in progress
        if video_id in self.posting_in_progress:
            logger.warning(f"[ORCHESTRATOR] ⏳ POSTING ALREADY IN PROGRESS for {video_id}")
            return PostResponse(
                request_id=request_id,
                results=[
                    PostResult(
                        success=False,
                        platform=platform,
                        message="Posting already in progress",
                        timestamp=datetime.now()
                    ) for platform in platforms
                ],
                success_count=0,
                failure_count=len(platforms)
            )

        # Mark as in progress
        self.posting_in_progress.add(video_id)

        logger.info(f"[ORCHESTRATOR] [U+2701]EPROCEEDING WITH POST")
        logger.info(f"[ORCHESTRATOR] [ROCKET] POSTING TO: {[p.value for p in platforms_to_post]}")
        if platforms_already_posted:
            logger.info(f"[ORCHESTRATOR] ⏭�E�ESKIPPING: {[p.value for p in platforms_already_posted]} (already posted)")

        # Determine channel handle based on LinkedIn page
        channel_handle = "@UnDaoDu"  # Default
        if linkedin_page:
            # Map LinkedIn page IDs to channel handles
            page_to_handle = {
                "68706058": "@UnDaoDu",     # UnDaoDu page
                "1263645": "@FoundUps",     # FoundUps page
                "104834798": "@Move2Japan"  # Move2Japan page
            }
            channel_handle = page_to_handle.get(linkedin_page, "@UnDaoDu")

        # Create post content
        content = f"""{channel_handle} going live!

{stream_title}

{stream_url}"""

        self.logger.info(f"[ORCHESTRATOR] Processing post request {request_id}")
        self.logger.info(f"[ORCHESTRATOR] Platforms to post: {[p.value for p in platforms_to_post]}")
        self.logger.info(f"[ORCHESTRATOR] Content: {stream_title}")

        # SEQUENTIAL POSTING - LinkedIn first, then X ONLY if LinkedIn succeeds
        results = []

        # Add skipped platforms to results
        for platform in platforms_already_posted:
            results.append(PostResult(
                success=False,
                platform=platform,
                message="Already posted - skipped",
                timestamp=datetime.now()
            ))

        # Track LinkedIn success for conditional X posting
        # CRITICAL: If LinkedIn was already posted, consider it successful for X posting
        linkedin_posted_successfully = Platform.LINKEDIN in platforms_already_posted

        # DEBUG: Log what platforms we're iterating over
        self.logger.info(f"[DEBUG] platforms_to_post = {[p.value for p in platforms_to_post]}")
        self.logger.info(f"[DEBUG] Starting platform iteration loop...")

        for platform in platforms_to_post:
            if platform == Platform.LINKEDIN:
                self.logger.info("="*80)
                self.logger.info("[ORCHESTRATOR] [U+1F535] STARTING LINKEDIN POSTING SEQUENCE")
                self.logger.info(f"[ORCHESTRATOR] ⏰ Time: {datetime.now().strftime('%H:%M:%S')}")
                self.logger.info("="*80)

                result = await self._post_to_linkedin(content, linkedin_page)
                results.append(result)
                linkedin_posted_successfully = result.success

                # DEBUG: Log the LinkedIn result
                self.logger.info(f"[DEBUG] LinkedIn result: success={result.success}, message={result.message}")
                self.logger.info(f"[DEBUG] linkedin_posted_successfully = {linkedin_posted_successfully}")

                if result.success:
                    self.logger.info("="*80)
                    self.logger.info("[ORCHESTRATOR] [U+2701]ELINKEDIN POSTED SUCCESSFULLY")
                    self.logger.info(f"[ORCHESTRATOR] ⏰ Completed at: {datetime.now().strftime('%H:%M:%S')}")
                    self.logger.info("="*80)

                    # CRITICAL: Save LinkedIn success immediately to prevent re-posting
                    if video_id not in self.posted_streams:
                        self.posted_streams[video_id] = {
                            'timestamp': datetime.now().isoformat(),
                            'title': stream_title,
                            'url': stream_url,
                            'platforms_posted': []
                        }

                    if 'linkedin' not in self.posted_streams[video_id]['platforms_posted']:
                        self.posted_streams[video_id]['platforms_posted'].append('linkedin')
                        self._save_posted_history()
                        self.logger.info(f"[ORCHESTRATOR] [U+1F4BE] Saved LinkedIn post to history immediately")

                    # Wait for browser cleanup before next platform
                    if Platform.X_TWITTER in platforms_to_post:  # Only wait if X will post
                        self.logger.info("[ORCHESTRATOR] ⏳ BROWSER CLEANUP DELAY: Starting 10-second wait...")
                        for i in range(10, 0, -1):
                            self.logger.info(f"[ORCHESTRATOR] ⏳ Cleanup countdown: {i} seconds remaining...")
                            await asyncio.sleep(1)
                        self.logger.info("[ORCHESTRATOR] [U+2701]EBrowser cleanup complete - ready for X")
                else:
                    self.logger.warning("="*80)
                    self.logger.warning("[ORCHESTRATOR] [U+2741]ELINKEDIN FAILED - X WILL BE SKIPPED")
                    self.logger.warning(f"[ORCHESTRATOR] ⏰ Failed at: {datetime.now().strftime('%H:%M:%S')}")
                    self.logger.warning(f"[ORCHESTRATOR] [NOTE] Reason: {result.message}")
                    self.logger.warning("="*80)

            elif platform == Platform.X_TWITTER:
                # CRITICAL: Only post to X if LinkedIn was successful
                if not linkedin_posted_successfully:
                    self.logger.warning("="*80)
                    self.logger.warning("[ORCHESTRATOR] ⏭�E�ESKIPPING X/TWITTER")
                    self.logger.warning("[ORCHESTRATOR] [NOTE] Reason: LinkedIn posting failed")
                    self.logger.warning(f"[ORCHESTRATOR] ⏰ Time: {datetime.now().strftime('%H:%M:%S')}")
                    self.logger.warning("="*80)
                    results.append(PostResult(
                        success=False,
                        platform=Platform.X_TWITTER,
                        message="Skipped - LinkedIn posting failed",
                        timestamp=datetime.now()
                    ))
                else:
                    self.logger.info("="*80)
                    self.logger.info("[ORCHESTRATOR] [BIRD] STARTING X/TWITTER POSTING SEQUENCE")
                    self.logger.info("[ORCHESTRATOR] [U+2701]EPrerequisite: LinkedIn posted successfully")
                    self.logger.info(f"[ORCHESTRATOR] ⏰ Time: {datetime.now().strftime('%H:%M:%S')}")
                    self.logger.info("="*80)

                    result = await self._post_to_x_twitter(content, linkedin_page)
                    results.append(result)

                    if result.success:
                        self.logger.info("="*80)
                        self.logger.info("[ORCHESTRATOR] [U+2701]EX/TWITTER POSTED SUCCESSFULLY")
                        self.logger.info(f"[ORCHESTRATOR] ⏰ Completed at: {datetime.now().strftime('%H:%M:%S')}")
                        self.logger.info("="*80)

                        # CRITICAL: Save X success immediately to prevent re-posting
                        if video_id not in self.posted_streams:
                            self.posted_streams[video_id] = {
                                'timestamp': datetime.now().isoformat(),
                                'title': stream_title,
                                'url': stream_url,
                                'platforms_posted': []
                            }

                        if 'x_twitter' not in self.posted_streams[video_id]['platforms_posted']:
                            self.posted_streams[video_id]['platforms_posted'].append('x_twitter')
                            self._save_posted_history()
                            self.logger.info(f"[ORCHESTRATOR] [U+1F4BE] Saved X/Twitter post to history immediately")
                    else:
                        self.logger.warning("="*80)
                        self.logger.warning("[ORCHESTRATOR] [U+2741]EX/TWITTER POSTING FAILED")
                        self.logger.warning(f"[ORCHESTRATOR] [NOTE] Reason: {result.message}")
                        self.logger.warning(f"[ORCHESTRATOR] ⏰ Failed at: {datetime.now().strftime('%H:%M:%S')}")
                        self.logger.warning("="*80)
        
        # Count successes and failures
        success_count = sum(1 for r in results if r.success)
        failure_count = len(results) - success_count
        
        response = PostResponse(
            request_id=request_id,
            results=results,
            success_count=success_count,
            failure_count=failure_count
        )

        # Record in posted history (merge with existing if partial success)
        if success_count > 0 or len(platforms) == 0:  # Save even when testing with no platforms
            # Get existing platforms if stream was partially posted before
            existing_platforms = []
            if video_id in self.posted_streams:
                existing_platforms = self.posted_streams[video_id].get('platforms_posted', [])

            # Add newly successful platforms
            newly_posted = [r.platform.value for r in results
                          if r.success and r.message != "Already posted - skipped"]

            # Merge platforms (avoid duplicates)
            all_posted_platforms = list(set(existing_platforms + newly_posted))

            self.posted_streams[video_id] = {
                'timestamp': datetime.now().isoformat(),
                'title': stream_title,
                'url': stream_url,
                'platforms_posted': all_posted_platforms
            }
            self._save_posted_history()
            logger.info(f"[ORCHESTRATOR] [U+1F4BE] Saved to posted history: {video_id}")
            logger.info(f"[ORCHESTRATOR] [DATA] Platforms posted: {all_posted_platforms}")

        # Remove from in-progress set
        self.posting_in_progress.discard(video_id)

        self.logger.info(f"[ORCHESTRATOR] Completed {request_id}: {success_count}/{len(results)} successful")
        return response

    async def schedule_stream_notification(self, stream_title: str, stream_url: str,
                                         delay_hours: int = 24,
                                         linkedin_page: str = None) -> Dict[str, Any]:
        """
        Schedule stream notification using AI delegation pipeline.

        Instead of posting immediately, this method:
        1. Uses AI delegation orchestrator to draft content
        2. Schedules post via UI-TARS for later execution
        3. Allows 012 review and editing before posting

        Args:
            stream_title: Title of the stream
            stream_url: URL of the stream
            delay_hours: Hours to delay scheduling (default: 24)
            linkedin_page: LinkedIn company page to post to

        Returns:
            Dict with scheduling result and draft information
        """
        if not AI_DELEGATION_AVAILABLE:
            return {
                'success': False,
                'error': 'AI delegation orchestrator not available',
                'fallback_possible': False
            }

        try:
            # Initialize AI delegation orchestrator
            ai_orchestrator = get_ai_delegation_orchestrator()

            # Create trigger event for AI drafting
            trigger_event = {
                'type': 'stream_start',
                'title': stream_title,
                'url': stream_url,
                'description': f"🔴 LIVE: {stream_title} - {stream_url}",
                'timestamp': datetime.now().isoformat(),
                'platforms': ['linkedin'],
                'company_page': linkedin_page or 'foundups'
            }

            self.logger.info("="*80)
            self.logger.info("[ORCHESTRATOR] [AI] STARTING SCHEDULED POSTING SEQUENCE")
            self.logger.info(f"[ORCHESTRATOR] 🎯 Stream: {stream_title}")
            self.logger.info(f"[ORCHESTRATOR] ⏰ Scheduling for: {delay_hours} hours from now")
            self.logger.info("="*80)

            # Draft content using AI delegation
            draft_result = await ai_orchestrator.draft_linkedin_content(
                trigger_event, target_platform='linkedin'
            )

            if not draft_result:
                return {
                    'success': False,
                    'error': 'AI content drafting failed',
                    'trigger_event': trigger_event
                }

            self.logger.info(f"[ORCHESTRATOR] [AI] Content drafted using {draft_result.get('ai_service', 'unknown')}")
            self.logger.info(f"[ORCHESTRATOR] 📝 Draft hash: {draft_result['draft_hash'][:8]}...")

            # Schedule the draft using UI-TARS
            scheduling_success = await ai_orchestrator.schedule_draft(draft_result, delay_hours)

            if scheduling_success:
                self.logger.info("="*80)
                self.logger.info("[ORCHESTRATOR] [✅] LINKEDIN POST SCHEDULED SUCCESSFULLY")
                self.logger.info(f"[ORCHESTRATOR] 📅 Scheduled for: {(datetime.now() + timedelta(hours=delay_hours)).strftime('%Y-%m-%d %H:%M')}")
                self.logger.info(f"[ORCHESTRATOR] 🔗 Review in LinkedIn: https://linkedin.com/company/foundups/admin/scheduled-posts")
                self.logger.info("="*80)

                return {
                    'success': True,
                    'draft_hash': draft_result['draft_hash'],
                    'ai_service': draft_result.get('ai_service'),
                    'scheduled_time': (datetime.now() + timedelta(hours=delay_hours)).isoformat(),
                    'content_preview': draft_result['content'][:100] + '...',
                    'review_url': 'https://linkedin.com/company/foundups/admin/scheduled-posts',
                    'trigger_event': trigger_event,
                    'draft_result': draft_result
                }
            else:
                self.logger.error("[ORCHESTRATOR] [❌] Failed to schedule post with UI-TARS")
                return {
                    'success': False,
                    'error': 'UI-TARS scheduling failed',
                    'draft_result': draft_result,
                    'trigger_event': trigger_event
                }

        except Exception as e:
            self.logger.error(f"[ORCHESTRATOR] Scheduled posting failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'trigger_event': trigger_event if 'trigger_event' in locals() else None
            }

    async def _verify_live_status_before_posting(self) -> bool:
        """
        SIMPLIFIED: Since we now trust the caller's detection, this is optional.
        Only used for manual verification calls.
        """
        try:
            self.logger.info("[VERIFICATION] Manual verification requested...")

            # Use scraping only - no API needed
            try:
                from modules.platform_integration.stream_resolver.src.no_quota_stream_checker import NoQuotaStreamChecker
                scraper = NoQuotaStreamChecker()

                # Check both channels
                channels = [
                    ("UC-LSSlOZwpGIRIYihaz8zCw", "UnDaoDu"),
                    ("UCSNTUXjAgpd4sgWYP0xoJgw", "FoundUps")
                ]

                for channel_id, channel_name in channels:
                    live_info = scraper.check_channel_for_live(channel_id)
                    if live_info:
                        self.logger.info(f"[VERIFICATION] [U+2701]E{channel_name} is LIVE")
                        return True

                self.logger.info("[VERIFICATION] [U+1F4ED] No channels are live")
                return False

            except Exception as e:
                self.logger.error(f"[VERIFICATION] Scraping failed: {e}")
                # When in doubt, trust the original detection
                return True

        except Exception as e:
            self.logger.error(f"[VERIFICATION] Error in manual verification: {e}")
            return True  # Trust the original detection

    def check_if_already_posted(self, video_id: str) -> Dict[str, Any]:
        """
        Check if a video has already been posted to social media platforms.

        Args:
            video_id: YouTube video ID to check

        Returns:
            Dictionary with posting status for each platform
        """
        self.logger.info("="*60)
        self.logger.info("[SEARCH] DUPLICATE PREVENTION CHECK INITIATED")
        self.logger.info(f"[U+1F4F9] Video ID: {video_id}")
        self.logger.info("="*60)

        result = {
            'video_id': video_id,
            'already_posted': False,
            'platforms_posted': [],
            'timestamp': None
        }

        # Check in-memory cache first
        self.logger.info("[U+1F4C2] Checking in-memory cache...")
        if video_id in self.posted_streams:
            posted_info = self.posted_streams[video_id]
            result['already_posted'] = True
            result['platforms_posted'] = posted_info.get('platforms_posted', [])
            result['timestamp'] = posted_info.get('timestamp')

            self.logger.info("[OK] FOUND IN MEMORY CACHE:")
            self.logger.info(f"   • Platforms posted: {result['platforms_posted']}")
            self.logger.info(f"   • Posted at: {result['timestamp']}")
            self.logger.info("[FORBIDDEN] DUPLICATE PREVENTION ACTIVE - Will skip these platforms")
        else:
            self.logger.info("[FAIL] NOT in memory cache")

            # Check database as backup
            self.logger.info("[U+1F5C4]️ Checking database...")
            if self._check_database_for_post(video_id):
                self.logger.info("[OK] FOUND IN DATABASE - Loading to memory")
                # Reload and check again
                self.posted_streams = self._load_posted_history()
                if video_id in self.posted_streams:
                    posted_info = self.posted_streams[video_id]
                    result['already_posted'] = True
                    result['platforms_posted'] = posted_info.get('platforms_posted', [])
                    result['timestamp'] = posted_info.get('timestamp')
                    self.logger.info(f"   • Platforms posted: {result['platforms_posted']}")
                    self.logger.info("[FORBIDDEN] DUPLICATE PREVENTION ACTIVE")
            else:
                self.logger.info("[FAIL] NOT in database")
                self.logger.info("[OK] NEW VIDEO - OK to post to all platforms")

        self.logger.info("="*60)
        return result

    def _check_database_for_post(self, video_id: str) -> bool:
        """Check if video exists in database"""
        import sqlite3
        import os

        module_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        db_path = os.path.join(
            module_root,
            "gamification", "whack_a_magat", "data", "magadoom_scores.db"
        )

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT video_id FROM social_posts WHERE video_id = ?", (video_id,))
            result = cursor.fetchone()
            conn.close()
            return result is not None
        except:
            return False

    async def verify_live_status_manually(self) -> bool:
        """
        [ALERT] ENHANCEMENT TRIGGER: Manual verification method

        This method can be called independently to verify if @UnDaoDu and Move2Japan
        are currently live. Useful for testing and manual triggers.

        Returns True if at least one channel is confirmed live.
        """
        return await self._verify_live_status_before_posting()

    def _load_posted_history(self) -> dict:
        """Load history of posted streams from SQLite database"""
        import sqlite3
        import json
        import os

        # Use existing whack-a-maga database for all gamification/tracking
        # Navigate from platform_integration/social_media_orchestrator/src to modules root
        module_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        db_path = os.path.join(
            module_root,
            "gamification", "whack_a_magat", "data", "magadoom_scores.db"
        )

        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Create table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS social_posts (
                    video_id TEXT PRIMARY KEY,
                    title TEXT,
                    url TEXT,
                    platforms_posted TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Load all posted streams
            cursor.execute("SELECT video_id, title, url, platforms_posted, timestamp FROM social_posts")
            rows = cursor.fetchall()

            history = {}
            for video_id, title, url, platforms_json, timestamp in rows:
                platforms = json.loads(platforms_json) if platforms_json else []
                history[video_id] = {
                    'title': title,
                    'url': url,
                    'platforms_posted': platforms,
                    'timestamp': timestamp
                }

            conn.close()
            self.logger.info(f"[ORCHESTRATOR] [BOOKS] Loaded {len(history)} posted streams from database")
            return history

        except Exception as e:
            self.logger.error(f"[ORCHESTRATOR] Error loading from database: {e}")
            # Fallback to JSON if database fails
            return self._load_posted_history_json()

    def _load_posted_history_json(self) -> dict:
        """Fallback: Load history from JSON file"""
        import json
        history_file = "memory/orchestrator_posted_streams.json"
        try:
            with open(history_file, 'r', encoding="utf-8") as f:
                history = json.load(f)
                self.logger.info(f"[ORCHESTRATOR] [BOOKS] Loaded {len(history)} posted streams from JSON fallback")
                return history
        except FileNotFoundError:
            self.logger.info("[ORCHESTRATOR] [BOOKS] No JSON history found, starting fresh")
            return {}
        except Exception as e:
            self.logger.error(f"[ORCHESTRATOR] Error loading JSON: {e}")
            return {}

    def _save_posted_history(self):
        """Save posted history to SQLite database"""
        import sqlite3
        import json
        import os
        from datetime import datetime

        # Use existing whack-a-maga database
        # Navigate from platform_integration/social_media_orchestrator/src to modules root
        module_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        db_path = os.path.join(
            module_root,
            "gamification", "whack_a_magat", "data", "magadoom_scores.db"
        )

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Update or insert each stream
            for video_id, data in self.posted_streams.items():
                platforms_json = json.dumps(data.get('platforms_posted', []))

                cursor.execute("""
                    INSERT OR REPLACE INTO social_posts
                    (video_id, title, url, platforms_posted, timestamp, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    video_id,
                    data.get('title', ''),
                    data.get('url', ''),
                    platforms_json,
                    data.get('timestamp', datetime.now().isoformat()),
                    datetime.now().isoformat()
                ))

            conn.commit()
            conn.close()
            self.logger.info(f"[ORCHESTRATOR] [U+1F4BE] Saved {len(self.posted_streams)} posted streams to database")

        except Exception as e:
            self.logger.error(f"[ORCHESTRATOR] Error saving to database: {e}")
            # Fallback to JSON
            self._save_posted_history_json()

    def _save_posted_history_json(self):
        """Fallback: Save to JSON file"""
        import json
        import os

        os.makedirs("memory", exist_ok=True)
        history_file = "memory/orchestrator_posted_streams.json"

        try:
            with open(history_file, 'w', encoding="utf-8") as f:
                json.dump(self.posted_streams, f, indent=2)
            self.logger.info(f"[ORCHESTRATOR] [U+1F4BE] Saved {len(self.posted_streams)} posted streams to JSON")
        except Exception as e:
            self.logger.error(f"[ORCHESTRATOR] Error saving JSON: {e}")

    async def _post_to_linkedin(self, content: str, linkedin_page: str = None) -> PostResult:
        """Post to LinkedIn using existing anti-detection poster"""
        try:
            self.logger.info("="*60)
            self.logger.info("[LINKEDIN] [U+1F535] ATTEMPTING LINKEDIN POST")
            self.logger.info("="*60)

            if not (os.getenv('LINKEDIN_EMAIL') and os.getenv('LINKEDIN_PASSWORD')):
                self.logger.warning("[LINKEDIN] [U+2741]ELinkedIn credentials not configured")
                return PostResult(
                    success=False,
                    platform=Platform.LINKEDIN,
                    message="LinkedIn credentials not configured",
                    timestamp=datetime.now()
                )

            self.logger.info("[LINKEDIN] [U+2701]ECredentials found")
            self.logger.info(f"[LINKEDIN] [NOTE] Content length: {len(content)} chars")
            self.logger.info("[LINKEDIN] [ROCKET] Starting anti-detection poster...")

            # Try unified LinkedIn interface first (WSP 3 compliant)
            try:
                from modules.platform_integration.social_media_orchestrator.src.unified_linkedin_interface import post_stream_notification, post_general_content

                # Extract video ID for duplicate prevention
                video_id = None
                import re
                video_match = re.search(r'youtube\.com/watch\?v=([a-zA-Z0-9_-]+)', content)
                if video_match:
                    video_id = video_match.group(1)

                self.logger.info("[LINKEDIN] [REFRESH] Attempting API-based posting...")
                # Try API posting first
                if video_id and linkedin_page:
                    result = await post_stream_notification(content, linkedin_page)
                else:
                    result = await post_general_content(content)

                if result.get('success'):
                    self.logger.info("[LINKEDIN] [U+2701]EAPI posting successful")
                    return PostResult(
                        success=True,
                        platform=Platform.LINKEDIN,
                        message=f"Posted via API: {result.get('message', 'Success')}",
                        timestamp=datetime.now(),
                        url=result.get('url')
                    )
                else:
                    self.logger.warning(f"[LINKEDIN] [U+26A0]�E�EAPI posting failed: {result.get('error', 'Unknown error')}")
                    # Fall back to URL sharing
                    self.logger.info("[LINKEDIN] [REFRESH] Falling back to URL sharing method...")
                    return await self._linkedin_url_share_fallback(content)

            except Exception as api_error:
                self.logger.warning(f"[LINKEDIN] [U+26A0]�E�EAPI posting unavailable ({api_error}), using URL sharing fallback")
                self.logger.info("[LINKEDIN] [REFRESH] Using LinkedIn Share URL method...")

                # Fallback: Use LinkedIn Share URL (Solution 4 from SOLUTION_GUIDE.md)
                return await self._linkedin_url_share_fallback(content)

        except Exception as e:
            self.logger.error(f"[LINKEDIN] [FAIL] LinkedIn posting failed: {e}")
            return PostResult(
                success=False,
                platform=Platform.LINKEDIN,
                message=f"LinkedIn posting failed: {e}",
                timestamp=datetime.now()
            )

    async def _linkedin_url_share_fallback(self, content: str) -> PostResult:
        """Fallback LinkedIn posting using share URL (no API required)"""
        try:
            import webbrowser
            import urllib.parse

            self.logger.info("[LINKEDIN] [U+1F310] Opening LinkedIn share URL in browser...")

            # Extract title and URL from content
            import re
            lines = content.strip().split('\n')

            # Parse content format: "Channel going live!\n\nTitle\n\nURL"
            stream_url = None
            stream_title = None

            for line in lines:
                line = line.strip()
                if line.startswith('http'):
                    stream_url = line
                elif line and 'going live' not in line.lower():
                    stream_title = line

            # Fallbacks
            if not stream_url:
                stream_url = 'https://www.youtube.com/@UnDaoDu/live'
            if not stream_title:
                stream_title = '0102 Live Stream'

            # Clean up content for summary (shorter version)
            clean_content = content.replace('\n', ' ').strip()
            if len(clean_content) > 200:  # LinkedIn URL limit
                clean_content = clean_content[:197] + "..."

            # Create LinkedIn share URL
            share_url = "https://www.linkedin.com/sharing/share-offsite/"
            params = {
                'url': stream_url,  # Actual stream URL
                'title': stream_title,  # Actual stream title
                'summary': clean_content
            }

            full_url = share_url + '?' + urllib.parse.urlencode(params)
            webbrowser.open(full_url, encoding="utf-8")

            self.logger.info("[LINKEDIN] [OK] LinkedIn share URL opened in browser")
            self.logger.info("[LINKEDIN] [CLIPBOARD] Content ready for manual posting")

            return PostResult(
                success=True,
                platform=Platform.LINKEDIN,
                message="LinkedIn share URL opened in browser (manual posting required)",
                timestamp=datetime.now(),
                url=full_url
            )

        except Exception as e:
            self.logger.error(f"[LINKEDIN] [FAIL] URL sharing failed: {e}")
            return PostResult(
                success=False,
                platform=Platform.LINKEDIN,
                message=f"URL sharing failed: {e}",
                timestamp=datetime.now()
            )

    async def _post_to_x_twitter(self, content: str, linkedin_page: str = None) -> PostResult:
        """
        Post to X/Twitter using child DAE adapter (WSP 77 Agent Coordination)

        WSP 77: Agent Coordination Protocol
        - Uses child DAE adapter instead of direct script calls
        - Full WSP 26-29 DAE integration
        - Parent-child orchestrator relationship
        """
        try:
            self.logger.info("="*60)
            self.logger.info("[X/TWITTER DAE] [BIRD] CHILD DAE POSTING VIA ADAPTER")
            self.logger.info("="*60)

            # Check if child DAE adapter is available
            if not self._x_twitter_dae_adapter or not self._x_twitter_dae_adapter.is_enabled():
                self.logger.warning("[X/TWITTER DAE] Child DAE adapter not available, falling back to legacy poster")
                return await self._post_to_x_twitter_legacy(content, linkedin_page)

            # Prepare base content for child DAE
            base_content = {
                'mention': f'@{linkedin_page}' if linkedin_page else '@FoundUps',
                'action': 'going live!',
                'title': content,  # Content contains the title/stream info
                'url': '',  # URL extraction would happen here if needed
                'tags': []
            }

            self.logger.info(f"[X/TWITTER DAE] [NOTE] Base content prepared: {base_content['mention']} {base_content['action']}")
            self.logger.info("[X/TWITTER DAE] [ROCKET] Posting via child DAE adapter...")

            # Post via child DAE adapter (WSP 77 coordination)
            posting_result = await self._x_twitter_dae_adapter.receive_base_content(base_content)

            if posting_result.success:
                self.logger.info(f"[X/TWITTER DAE] [OK] Child DAE posting successful: {posting_result.post_id}")
                self.logger.info(f"[X/TWITTER DAE] [DATA] CABR Score: {posting_result.cabr_score:.3f}")

                return PostResult(
                    success=True,
                    platform=Platform.X_TWITTER,
                    message=f"Posted via child DAE: {posting_result.post_id}",
                    timestamp=posting_result.timestamp,
                    url=f"https://twitter.com/i/status/{posting_result.post_id}" if posting_result.post_id else None
                )
            else:
                self.logger.error(f"[X/TWITTER DAE] [FAIL] Child DAE posting failed: {posting_result.message}")
                return PostResult(
                    success=False,
                    platform=Platform.X_TWITTER,
                    message=f"Child DAE failed: {posting_result.message}",
                    timestamp=posting_result.timestamp
                )

        except Exception as e:
            self.logger.error(f"[X/TWITTER DAE] [U+1F4A5] Child DAE adapter error: {e}")
            self.logger.info("[X/TWITTER DAE] Falling back to legacy poster...")
            return await self._post_to_x_twitter_legacy(content, linkedin_page)

    async def _post_to_x_twitter_legacy(self, content: str, linkedin_page: str = None) -> PostResult:
        """Legacy X/Twitter posting using anti-detection poster (fallback)"""
        try:
            self.logger.info("="*60)
            self.logger.info("[X/TWITTER LEGACY] [BIRD] FALLBACK TO ANTI-DETECTION POSTER")
            self.logger.info("="*60)

            # Load environment variables
            from dotenv import load_dotenv
            load_dotenv()

            if not (os.getenv('X_Acc1') and os.getenv('x_Acc_pass')):
                self.logger.warning("[X/TWITTER LEGACY] [U+2741]EX/Twitter credentials not configured")
                return PostResult(
                    success=False,
                    platform=Platform.X_TWITTER,
                    message="X/Twitter credentials not configured",
                    timestamp=datetime.now()
                )

            self.logger.info("[X/TWITTER LEGACY] [U+2701]ECredentials found")
            self.logger.info(f"[X/TWITTER LEGACY] [NOTE] Content length: {len(content)} chars")
            self.logger.info("[X/TWITTER LEGACY] [ROCKET] Starting anti-detection poster...")

            # Import and use existing X poster
            from modules.platform_integration.x_twitter.src.x_anti_detection_poster import AntiDetectionX
            
            # Run in thread to not block async (same pattern as livechat)
            import threading
            
            x_success = False
            error_message = None
            x_completed = threading.Event()
            
            def post_to_x():
                nonlocal x_success, error_message
                global _GLOBAL_X_POSTER_FOUNDUPS, _GLOBAL_X_POSTER_GEOZAI

                try:
                    # Use global singleton with thread-safe lock
                    with _POSTER_LOCK:
                        # Check if browser was manually closed
                        browser_closed = False
                        # Check if either browser instance was closed manually
                        if _GLOBAL_X_POSTER_FOUNDUPS:
                            try:
                                _ = _GLOBAL_X_POSTER_FOUNDUPS.driver.current_url
                            except:
                                _GLOBAL_X_POSTER_FOUNDUPS = None
                        if _GLOBAL_X_POSTER_GEOZAI:
                            try:
                                _ = _GLOBAL_X_POSTER_GEOZAI.driver.current_url
                            except:
                                _GLOBAL_X_POSTER_GEOZAI = None

                        # Determine which X account to use based on channel configuration
                        use_foundups = self._get_x_account_for_linkedin_page(linkedin_page)
                        self.logger.info(f"[X THREAD] [SEARCH] LinkedIn page: {linkedin_page}")
                        self.logger.info(f"[X THREAD] [SEARCH] use_foundups: {use_foundups} (True=@Foundups/Edge, False=@GeozeAi/Chrome)")
                        account_name = 'FoundUps (@Foundups)' if use_foundups else 'Move2Japan (@GeozeAi)'
                        self.logger.info(f"[X THREAD] [TARGET] Account routing: {account_name}")

                        if use_foundups:
                            # Use FoundUps account (@Foundups)
                            self.logger.info("[X THREAD] [U+1F415] Using FoundUps X account (@Foundups)")

                            if _GLOBAL_X_POSTER_FOUNDUPS is None:
                                self.logger.info("[X THREAD] [NEW] Creating FoundUps X browser (Chrome)...")
                                self.logger.info("[X THREAD] [IDEA] This will open a Chrome window for @Foundups")
                                _GLOBAL_X_POSTER_FOUNDUPS = AntiDetectionX(use_foundups=True)
                                self.logger.info("[X THREAD] [U+2701]EFoundUps X poster created")
                            else:
                                self.logger.info("[X THREAD] [U+267B]�E�EREUSING FoundUps Chrome browser")

                            poster = _GLOBAL_X_POSTER_FOUNDUPS
                        else:
                            # Use Move2Japan/GeozeAi account (@GeozeAi)
                            self.logger.info("[X THREAD] [U+1F38C] Using Move2Japan X account (@GeozeAi)")
                            self.logger.info("[X THREAD] [U+26A0]�E�ENOTE: Make sure you're logged into @GeozeAi in a separate browser")

                            if _GLOBAL_X_POSTER_GEOZAI is None:
                                self.logger.info("[X THREAD] [NEW] Creating GeozeAi X browser...")
                                self.logger.info("[X THREAD] [IDEA] This will open another browser window for @GeozeAi")
                                self.logger.info("[X THREAD] [IDEA] TIP: Use Edge or Firefox for @GeozeAi to avoid conflicts")
                                _GLOBAL_X_POSTER_GEOZAI = AntiDetectionX(use_foundups=False)
                                self.logger.info("[X THREAD] [U+2701]EGeozeAi X poster created")
                            else:
                                self.logger.info("[X THREAD] [U+267B]�E�EREUSING GeozeAi browser")

                            poster = _GLOBAL_X_POSTER_GEOZAI

                        self.logger.info("[X THREAD] [U+1F4E4] Calling post_to_x()...")
                        self.logger.info(f"[X THREAD] ⏰ Start time: {datetime.now().strftime('%H:%M:%S')}")
                        result = poster.post_to_x(content)  # Use the selected poster
                        self.logger.info(f"[X THREAD] ⏰ End time: {datetime.now().strftime('%H:%M:%S')}")

                    x_success = bool(result)
                    if not x_success:
                        error_message = "X poster returned False"
                except Exception as e:
                    error_message = str(e)
                finally:
                    x_completed.set()
            
            thread = threading.Thread(target=post_to_x, daemon=False)
            thread.start()
            
            # Wait for completion (convert to async wait)
            while not x_completed.is_set():
                await asyncio.sleep(0.1)
            
            if x_success:
                self.logger.info("[ORCHESTRATOR] [U+2701]EX/Twitter posting successful")
                return PostResult(
                    success=True,
                    platform=Platform.X_TWITTER,
                    message="Posted successfully",
                    timestamp=datetime.now()
                )
            else:
                self.logger.warning(f"[ORCHESTRATOR] [U+2741]EX/Twitter posting failed: {error_message}")
                return PostResult(
                    success=False,
                    platform=Platform.X_TWITTER,
                    message=error_message or "Unknown error",
                    timestamp=datetime.now()
                )
            
        except Exception as e:
            self.logger.error(f"[ORCHESTRATOR] X/Twitter error: {e}")
            return PostResult(
                success=False,
                platform=Platform.X_TWITTER,
                message=str(e),
                timestamp=datetime.now()
            )


# Convenient instance for import
# TEMP FIX WSP90: orchestrator = SimplePostingOrchestrator()


# Convenience functions for easy import
async def post_stream_notification(stream_title: str, stream_url: str) -> PostResponse:
    """Convenience function for posting stream notifications"""
    return await orchestrator.post_stream_notification(stream_title, stream_url)


def handle_stream_detected(video_id: str, stream_title: str = None, linkedin_page: str = None) -> None:
    """
    Handle stream detection from stream_resolver - runs posting in background.
    This is the WSP 3 compliant entry point for stream detection events.

    Args:
        video_id: YouTube video ID of detected stream
        stream_title: Optional title of stream
        linkedin_page: LinkedIn company page ID to post to (determines routing)
    """
    import threading
    import asyncio

    logger = logging.getLogger(__name__)

    logger.info("="*80)
    logger.info("[ORCHESTRATOR] [TARGET] STREAM DETECTION HANDLER CALLED")
    logger.info(f"[ORCHESTRATOR] [U+1F4F9] Video ID: {video_id}")
    logger.info(f"[ORCHESTRATOR] [NOTE] Title: {stream_title}")
    logger.info(f"[ORCHESTRATOR] [U+1F3E2] LinkedIn Page: {linkedin_page}")
    logger.info("="*80)

    def post_in_background():
        try:
            logger.info("[ORCHESTRATOR] [U+1F9F5] Background thread started")
            # Check if already posted
            status = orchestrator.check_if_already_posted(video_id)
            if status['already_posted']:
                platforms = status['platforms_posted']
                logger.info(f"[ORCHESTRATOR] [U+26A0]️ Video {video_id} already posted to: {platforms}")

            # Build stream URL
            stream_url = f"https://www.youtube.com/watch?v={video_id}"
            final_title = stream_title or "Live Stream"

            logger.info(f"[ORCHESTRATOR] Processing stream detected: {final_title}")

            # Run async method in sync context
            response = asyncio.run(orchestrator.post_stream_notification(
                stream_title=final_title,
                stream_url=stream_url,
                platforms=[Platform.LINKEDIN, Platform.X_TWITTER],
                linkedin_page=linkedin_page
            ))

            # Log results
            if response.failure_count == 0:
                logger.info(f"[ORCHESTRATOR] [U+2701]EPosted to all platforms successfully")
            else:
                logger.info(f"[ORCHESTRATOR] Posted to {response.success_count}/{len(response.results)} platforms")

        except Exception as e:
            logger.error(f"[ORCHESTRATOR] Background posting error: {e}")

    # Start posting in background thread
    thread = threading.Thread(target=post_in_background, daemon=True)
    thread.start()
    logger.info(f"[ORCHESTRATOR] Social media posting triggered in background for {video_id}")
