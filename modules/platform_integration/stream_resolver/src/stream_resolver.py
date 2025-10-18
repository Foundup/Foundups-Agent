"""
Enhanced Stream Resolver Module for Windsurf Project

Integrates improvements from test coverage analysis:
- Enhanced error handling and validation
- Better retry logic with exponential backoff
- Improved fallback mechanisms
- More robust API client management
- Better logging and monitoring

Following WSP 3: Enterprise Domain Architecture
"""



import os
import logging
from typing import Optional, Tuple, Dict, Any, List
import googleapiclient.errors
from googleapiclient.errors import HttpError
from googleapiclient.discovery import Resource
from utils.oauth_manager import get_authenticated_service_with_fallback, get_authenticated_service
from utils.env_loader import get_env_variable
import time
import random
from datetime import datetime, timedelta
import json
import asyncio

# Import intelligent quota testing
try:
    from modules.platform_integration.youtube_auth.src.quota_tester import QuotaTester, get_best_credential_set
except ImportError:
    QuotaTester = None
    get_best_credential_set = None

# Import database for pattern learning (WSP 78)
try:
    from .stream_db import StreamResolverDB
except ImportError:
    StreamResolverDB = None
    # Logger defined below, so use print for now
    print("WARNING: Stream database not available - using legacy JSON storage")

# Import existing superior implementations (HoloIndex analysis confirmed these are better)
from modules.platform_integration.social_media_orchestrator.src.core.platform_posting_service import PlatformPostingService
from modules.platform_integration.social_media_orchestrator.src.channel_routing import SocialMediaRouter
from modules.platform_integration.youtube_api_operations.src.youtube_api_operations import YouTubeAPIOperations
# Lazy import to avoid circular dependency: get_qwen_youtube imported when needed
from modules.infrastructure.database.src.agent_db import AgentDB

# Import existing config (simpler but functional)
from .config import config as stream_config

# Import infrastructure utilities (superior implementations)
try:
    from modules.infrastructure.shared_utilities.session_utils import SessionUtils
    session_utils_available = True
except ImportError:
    SessionUtils = None
    session_utils_available = False
    logger.warning("SessionUtils not available, session caching disabled")

try:
    from modules.infrastructure.shared_utilities.validation_utils import ValidationUtils
    validation_utils_available = True
except ImportError:
    ValidationUtils = None
    validation_utils_available = False
    logger.warning("ValidationUtils not available, using fallback validation")

try:
    from modules.infrastructure.shared_utilities.delay_utils import DelayUtils
    delay_utils_available = True
except ImportError:
    DelayUtils = None
    delay_utils_available = False
    logger.warning("DelayUtils not available, using fallback delays")

# Get a logger instance specific to this module
logger = logging.getLogger(__name__)

# WSP 3 Phase 4: Global constants (previously removed but needed for backward compatibility)
CHANNEL_ID = os.getenv('CHANNEL_ID', 'UC-LSSlOZwpGIRIYihaz8zCw')  # UnDaoDu default

# Define custom exceptions for better error handling
class QuotaExceededError(Exception):
    """Custom exception for when API quota is exceeded after retries."""
    pass

class StreamResolverError(Exception):
    """Base exception for stream resolver errors."""
    pass

class APIClientError(Exception):
    """Exception for API client creation/validation errors."""
    pass

# Circuit breaker and configuration now imported from separate modules

# calculate_enhanced_delay moved to infrastructure/shared_utilities/delay_utils.py
# mask_sensitive_id and validate_api_client moved to infrastructure/shared_utilities/validation_utils.py

# Fallback functions for backward compatibility
def mask_sensitive_id(id_str: str, id_type: str = "default") -> str:
    """Fallback function that uses infrastructure utilities when available."""
    try:
        from modules.infrastructure.shared_utilities.validation_utils import ValidationUtils
        return ValidationUtils.mask_sensitive_id(id_str, id_type)
    except ImportError:
        # Basic fallback implementation
        if not id_str or not isinstance(id_str, str):
            return "None"
        return f"{id_str[:3]}...{id_str[-2:]}" if len(id_str) > 8 else "***ID***"

def validate_api_client(youtube_client) -> bool:
    """Fallback function that uses infrastructure utilities when available."""
    try:
        from modules.infrastructure.shared_utilities.validation_utils import ValidationUtils
        return ValidationUtils.validate_api_client(youtube_client)
    except ImportError:
        # Basic fallback implementation
        return youtube_client is not None

# ============================================================================
# YouTube API Operations Extraction (WSP 3 Phase 4)
# ============================================================================
# The following 415 lines of standalone YouTube API functions have been
# extracted to modules/platform_integration/youtube_api_operations/
#
# CRITICAL BUGS FIXED:
# - Line 185: self.circuit_breaker.call() in module-level function (no self!)
# - Line 306: self.circuit_breaker.call() in module-level function (no self!)
# - Line 298: self.config.CHANNEL_ID in module-level function (no self!)
#
# These functions are now properly implemented as instance methods in the
# YouTubeAPIOperations class with correct self references and dependency injection.
#
# Usage: self.youtube_api_ops.get_active_livestream_video_id_enhanced(youtube, channel_id)
# ============================================================================

class StreamResolver:
    def __init__(self,
                 youtube_service,
                 circuit_breaker=None,  # from circuit_breaker module
                 config=None,           # from stream_config module
                 database=None,         # from stream_db module
                 social_poster=None,    # from social_media_orchestrator
                 qwen_integration=None, # from qwen_youtube_integration
                 cache_manager=None,    # from session_cache module
                 no_quota_checker=None, # from no_quota_stream_checker module
                 use_intelligent_sorting=True):
        """
        StreamResolver with full dependency injection.

        Args:
            youtube_service: YouTube API service instance
            circuit_breaker: Circuit breaker instance (optional, uses global if None)
            config: Configuration instance (optional, uses global if None)
            database: Database instance (optional, creates if None)
            social_poster: Social media posting service (optional)
            qwen_integration: QWEN intelligence instance (optional)
            cache_manager: Cache manager instance (optional, uses global if None)
            no_quota_checker: NO-QUOTA checker instance (optional, creates if None and needed)
            use_intelligent_sorting: Whether to use intelligent sorting
        """
        self.youtube = youtube_service
        self.logger = logging.getLogger(__name__)

        # Store circuit_breaker reference (used by youtube_api_ops)
        self.circuit_breaker = circuit_breaker  # May be None, that's okay

        # Store config reference (used by resolve_stream for channel fallback)
        self.config = config  # May be None, that's okay

        # Use superior existing implementations (HoloIndex confirmed)
        self.use_intelligent_sorting = use_intelligent_sorting

        # Initialize existing superior services
        self._quota_tester = QuotaTester() if QuotaTester and use_intelligent_sorting else None
        self._tested_credentials = set()
        self._cache = {}
        self._last_stream_check = {}

        # QWEN Intelligence - Use existing superior implementation (lazy import to avoid circular dependency)
        if qwen_integration is not None:
            self.qwen = qwen_integration
        else:
            try:
                from modules.communication.livechat.src.qwen_youtube_integration import get_qwen_youtube
                self.qwen = get_qwen_youtube()
                self.logger.info("[QWEN] [QWEN-RESOLVER] QWEN intelligence connected to StreamResolver")
            except Exception as e:
                self.logger.debug(f"QWEN not available for StreamResolver: {e}")
                self.qwen = None

        # Database - Use existing superior AgentDB from infrastructure
        if database is not None:
            self.db = database
        else:
            try:
                self.db = AgentDB()  # Use superior infrastructure database
            except Exception as e:
                self.logger.warning(f"AgentDB not available, falling back to StreamResolverDB: {e}")
        self.db = StreamResolverDB() if StreamResolverDB else None

        # Social media poster - Use existing superior implementation
        if social_poster is not None:
            self.social_poster = social_poster
        else:
            try:
                self.social_poster = PlatformPostingService()
                self.logger.info("[SOCIAL] Social media posting service connected")
            except Exception as e:
                self.logger.warning(f"PlatformPostingService not available: {e}")
                self.social_poster = None

        # YouTube API Operations - Use extracted superior implementation
        self.youtube_api_ops = YouTubeAPIOperations(
            circuit_breaker=circuit_breaker,
            logger=self.logger
        )

        # Infrastructure utilities - Use superior implementations
        if cache_manager is not None:
            self.session_utils = cache_manager
        elif session_utils_available:
            self.session_utils = SessionUtils()
            self.logger.info("[SESSION] Session utilities connected from infrastructure")
        else:
            self.session_utils = None
            self.logger.warning("[SESSION] No session utilities available")

        # Validation utilities
        if validation_utils_available:
            self.validation_utils = ValidationUtils()
            self.logger.info("[VALIDATION] Validation utilities connected from infrastructure")
        else:
            self.validation_utils = None
            self.logger.warning("[VALIDATION] No validation utilities available")

        # Delay utilities
        if delay_utils_available:
            self.delay_utils = DelayUtils()
            self.logger.info("[DELAY] Delay utilities connected from infrastructure")
        else:
            self.delay_utils = None
            self.logger.warning("[DELAY] No delay utilities available")

        # NO-QUOTA checker - Use existing implementation
        if no_quota_checker is not None:
            self.no_quota_checker = no_quota_checker
        elif not self.youtube:
            try:
                from .no_quota_stream_checker import NoQuotaStreamChecker
                self.no_quota_checker = NoQuotaStreamChecker()
                self.logger.info("[NO-QUOTA] NO-QUOTA mode initialized - using web scraping")
            except ImportError:
                self.logger.warning("NoQuotaStreamChecker not available")
                self.no_quota_checker = None
        else:
            self.no_quota_checker = None

    def reset_circuit_breaker(self):
        """Reset the circuit breaker to recover from stuck OPEN state."""
        if self.circuit_breaker:
            self.circuit_breaker.reset()
            self.logger.info("[RESET] Circuit breaker reset requested from StreamResolver")
    
    def _ensure_memory_dir(self):
        """Ensure memory directory exists for session caching."""
        os.makedirs("memory", exist_ok=True)

    def _get_channel_display_name(self, channel_id: str) -> str:
        """Get human-readable channel name for logging with visual indicators"""
        return SocialMediaRouter.get_display_name(channel_id)


    def _get_linkedin_page_for_channel(self, channel_id: str) -> str:
        """Determine which LinkedIn page to post to based on YouTube channel.

        Uses centralized SocialMediaRouter for single source of truth.
        Replaced complex config file + fallback logic with simple routing call.
        """
        return SocialMediaRouter.get_linkedin_page(channel_id)
    
    def clear_cache(self):
        """Clear all cached stream data for fresh lookup."""
        import os
        # Clear in-memory cache
        self._cache = {}
        self._last_stream_check = {}
        
        # Clear session cache file using SessionUtils
        if self.session_utils:
            cache_file = getattr(self.session_utils, 'DEFAULT_CACHE_FILE', 'memory/session_cache.json')
            if os.path.exists(cache_file):
                try:
                    os.remove(cache_file)
                    self.logger.info("[CLEAR] Cleared session cache file for fresh search")
                except Exception as e:
                    self.logger.warning(f"Could not clear session cache: {e}")
        else:
            self.logger.warning("[CLEAR] No session utilities available for cache clearing")
        
        self.logger.info("[CLEAN] All caches cleared - will perform fresh stream search")
    
    def get_best_available_service(self):
        """
        Get the best available YouTube service with quota.
        Uses intelligent testing to find credentials with remaining quota.
        
        Returns:
            tuple: (service, credential_set) or (None, None) if all exhausted
        """
        if not self.use_intelligent_sorting or not self._quota_tester:
            # Fall back to normal rotation
            return self.youtube, getattr(self.youtube, '_credential_set', 0)
        
        self.logger.info("[TEST] Testing credentials for available quota...")
        
        # Get recommended order from quota tester
        recommended = self._quota_tester.get_recommended_order()
        
        if not recommended:
            self.logger.error("[ERROR] No credentials with available quota!")
            return None, None
        
        # Try credentials in recommended order
        for cred_set in recommended:
            if cred_set in self._tested_credentials:
                continue  # Skip already tested in this session
                
            try:
                self.logger.info(f"Testing credential set {cred_set}...")
                from modules.platform_integration.youtube_auth.src.youtube_auth import get_authenticated_service
                
                service, actual_set = get_authenticated_service(
                    force_credential_set=cred_set,
                    skip_validation=False
                )
                
                if service:
                    self.logger.info(f"[SUCCESS] Using credential set {cred_set} with available quota")
                    self._tested_credentials.add(cred_set)
                    return service, cred_set
                    
            except Exception as e:
                self.logger.warning(f"Failed to use credential set {cred_set}: {e}")
                self._tested_credentials.add(cred_set)
                continue
        
        self.logger.error("[ERROR] All recommended credentials failed")
        return None, None
    
    def _load_session_cache(self):
        """Load cached session data using SessionUtils from infrastructure."""
        if self.session_utils:
            return self.session_utils.load_cache()
        return None
    
    def _save_session_cache(self, video_id, chat_id):
        """Save successful connection data using SessionUtils from infrastructure."""
        if self.session_utils:
            stream_title = self._get_stream_title(video_id)
            return self.session_utils.save_cache(video_id, chat_id)
        return False
    
    def _try_cached_stream(self, cache):
        """Try to connect to cached stream using SessionUtils from infrastructure."""
        if self.session_utils:
            return self.session_utils.try_cached_stream(cache)
            return None, None
    
    def resolve_stream(self, channel_id=None):
        """
        Main method to resolve active livestream with intelligent cache-first approach.

        Args:
            channel_id: Optional channel ID to search (uses config default if not provided)

        Returns:
            Tuple of (video_id, chat_id) if found, None otherwise
        """
        # Record check attempt start (WSP 78)
        check_start_time = datetime.now()
        search_channel_id = channel_id or CHANNEL_ID
        
        # PRIORITY 1: Try cached stream first for instant reconnection
        cache = self._load_session_cache()
        if cache:
            self.logger.info("[RESET] Attempting cached stream reconnection...")
            video_id, chat_id = self._try_cached_stream(cache)
            if video_id and chat_id:
                self.logger.info(f"🚀 INSTANT reconnection successful using cached stream!")
                return video_id, chat_id
            else:
                self.logger.info("[ERROR] Cached stream no longer active, proceeding to fresh search")
        
        # PRIORITY 2: Check circuit breaker before making API calls
        if self.circuit_breaker and hasattr(self.circuit_breaker, 'state') and self.circuit_breaker.state == "OPEN":
            self.logger.warning(f"🚫 Circuit breaker OPEN - API calls blocked for {self.circuit_breaker.timeout/60:.1f} minutes")
            # Try to reset if timeout expired
            if hasattr(self.circuit_breaker, '_should_attempt_reset') and self.circuit_breaker._should_attempt_reset():
                self.logger.info("[RESET] Circuit breaker timeout expired, attempting reset...")
                self.circuit_breaker.state = "HALF_OPEN"
            else:
                self.logger.error("[ERROR] Circuit breaker still OPEN, cannot search for new streams")
                return None
        
        # PRIORITY 3: Use provided channel_id or fall back to config
        search_channel_id = channel_id or (self.config.CHANNEL_ID if self.config else None)
        if not search_channel_id:
            self.logger.error("[ERROR] No channel ID provided and none configured")
            return None
        
        # PRIORITY 4: NO-QUOTA mode - persistent idle loop (prioritize to conserve API quota)
        if self.no_quota_checker:
            logger.info("="*60)
            logger.info("[NO-QUOTA] NO-QUOTA STREAM SEARCH (MULTI-CHANNEL ROTATION)")
            logger.info(f"   Using web scraping (0 API units)")

            # Get all channels to rotate through in idle mode
            channels_to_rotate = [
                os.getenv('MOVE2JAPAN_CHANNEL_ID', 'UCklMTNnu5POwRmQsg5JJumA'),  # Move2Japan first
                os.getenv('CHANNEL_ID', 'UC-LSSlOZwpGIRIYihaz8zCw'),         # UnDaoDu second
                os.getenv('CHANNEL_ID2', 'UCSNTUXjAgpd4sgWYP0xoJgw'),       # FoundUps last
            ]
            channels_to_rotate = [ch for ch in channels_to_rotate if ch]  # Filter None values

            if channel_id:
                # Specific channel requested - just check that one
                logger.info(f"   Channel: {search_channel_id} ({self._get_channel_display_name(search_channel_id)})")
                logger.info(f"   Mode: Single channel search")
                channels_to_check = [search_channel_id]
            else:
                # No specific channel - rotate through all channels
                logger.info(f"   Rotating through {len(channels_to_rotate)} channels:")
                for i, ch in enumerate(channels_to_rotate, 1):
                    logger.info(f"     {i}. {self._get_channel_display_name(ch)} ({ch[:12]}...)")
                logger.info(f"   Mode: Multi-channel rotation until stream found")
                channels_to_check = channels_to_rotate

            logger.info("="*60)

            # NO-QUOTA mode: Intelligent pattern-based checking
            total_channels = len(channels_to_check) or 1
            channels_queue = list(channels_to_check)
            attempt = 0

            # Get pattern-based predictions for all channels
            channel_predictions = {}
            for cid in channels_to_check:
                if self.db:
                    predictions = self.db.predict_next_stream_time(cid)
                    if predictions:
                        channel_predictions[cid] = predictions

            while channels_queue:
                attempt += 1

                # Simple round-robin selection (QWEN provides intelligent prioritization via should_check_now)
                current_channel_id = channels_queue.pop(0)

                channel_name = self._get_channel_display_name(current_channel_id)
                pattern_info = ""
                if current_channel_id in channel_predictions:
                    pred = channel_predictions[current_channel_id]
                    pattern_info = f" (predicted: {pred.get('confidence', 0):.2f} confidence)"

                if channel_id:
                    logger.info(f"[TEST] NO-QUOTA check for {channel_name}{pattern_info}")
                else:
                    logger.info(f"[QWEN] [RESET] NO-QUOTA rotation [{attempt}/{total_channels}] - QWEN checking {channel_name}{pattern_info}")

                if self.qwen:
                    try:
                        profile = self.qwen.get_channel_profile(current_channel_id, channel_name)
                        should_check, reason = profile.should_check_now()
                        if not should_check:
                            logger.info(f"⏭️ Skipping {channel_name}: {reason}")
                            continue
                    except Exception as q_err:
                        logger.debug(f"QWEN profile lookup failed for {channel_name}: {q_err}")

                env_video_id = get_env_variable("YOUTUBE_VIDEO_ID", default=None)
                if env_video_id:
                    logger.info(f"📺 Checking specific video from env: {env_video_id}")
                    env_result = self.no_quota_checker.check_video_is_live(env_video_id, channel_name)
                    if env_result.get('rate_limited'):
                        cooldown = env_result.get('cooldown')
                        if cooldown:
                            logger.warning(f"⚠️ Rate limit hit while checking env video {env_video_id} on {channel_name} – pausing {cooldown:.0f}s")
                        else:
                            logger.warning(f"⚠️ Rate limit hit while checking env video {env_video_id} on {channel_name}")
                        if self.qwen:
                            try:
                                profile = self.qwen.get_channel_profile(current_channel_id, channel_name)
                                profile.record_429_error()
                                self.qwen.global_heat_level = min(self.qwen.global_heat_level + 1, 10)
                            except Exception as q_err:
                                logger.debug(f"QWEN rate-limit record failed: {q_err}")
                        continue
                    if env_result.get('live'):
                        logger.info("[SUCCESS] STREAM IS LIVE (via NO-QUOTA video check)")
                        if self.db:
                            try:
                                self.db.record_stream_start(current_channel_id, env_video_id, env_result.get('title', 'Live Stream'))
                                self.db.analyze_and_update_patterns(current_channel_id)
                            except Exception as db_err:
                                logger.warning(f"Database error (non-critical): {db_err}")
                        return env_video_id, None
                    logger.info("[ERROR] Specified video not live")

                logger.info(f"[TEST] Searching {channel_name} ({current_channel_id[:12]}...) for live streams...")
                check_start = time.time()
                result = self.no_quota_checker.check_channel_for_live(current_channel_id, channel_name)
                check_duration = int((time.time() - check_start) * 1000)

                if self.db:
                    found = bool(result and result.get('live'))
                    self.db.record_check(current_channel_id, found, check_duration)

                if isinstance(result, dict) and result.get('rate_limited'):
                    cooldown = result.get('cooldown')
                    if cooldown:
                        logger.warning(f"⚠️ Rate limit encountered while scraping {channel_name} – cooling down for {cooldown:.0f}s")
                    else:
                        logger.warning(f"⚠️ Rate limit encountered while scraping {channel_name}")
                    if current_channel_id in channel_predictions:
                        channel_predictions[current_channel_id]['confidence'] = 0.0
                    if self.qwen:
                        try:
                            profile = self.qwen.get_channel_profile(current_channel_id, channel_name)
                            profile.record_429_error()
                            self.qwen.global_heat_level = min(self.qwen.global_heat_level + 1, 10)
                        except Exception as q_err:
                            logger.debug(f"QWEN rate-limit record failed: {q_err}")
                    continue

                if result and result.get('live'):
                    video_id = result.get('video_id')
                    if video_id:
                        logger.info(f"[SUCCESS] Found live stream on {channel_name}: {video_id} 🎉")
                        if self.db:
                            try:
                                self.db.record_stream_start(current_channel_id, video_id, result.get('title', 'Live Stream'))
                                self.db.analyze_and_update_patterns(current_channel_id)
                            except Exception as db_err:
                                logger.warning(f"Database error (non-critical): {db_err}")
                        return video_id, None

                if channels_queue:
                    delay = 2.0
                    next_channel = self._get_channel_display_name(channels_queue[0]) if channels_queue else channel_name
                    logger.info(f"⏳ No stream on {channel_name}, checking {next_channel} in {delay:.1f}s...")
                    time.sleep(delay)
                else:
                    logger.info(f"[ERROR] No stream on {channel_name} (last channel checked)")

            if channel_id:
                logger.info(f"[ERROR] No stream found on {self._get_channel_display_name(channel_id)}")
            else:
                logger.info(f"[ERROR] No streams found on any of the {total_channels} channels")
            return None
        else:
            # NO-QUOTA mode not available but could be initialized
            logger.info("⚠️ NO-QUOTA mode not available, attempting to initialize...")
            try:
                from .no_quota_stream_checker import NoQuotaStreamChecker
                self.no_quota_checker = NoQuotaStreamChecker()
                logger.info("[SUCCESS] NO-QUOTA mode initialized successfully, retrying...")
                # Recurse to retry with NO-QUOTA mode
                return self.resolve_stream(channel_id)
            except Exception as e:
                logger.warning(f"[ERROR] Failed to initialize NO-QUOTA mode: {e}")
                logger.info("⚠️ Falling back to API mode")

        # PRIORITY 5: Fallback to API mode if NO-QUOTA is not available
        # Check if API client is available before attempting
        if self.youtube is None:
            logger.error("[ERROR] API client is None")
            logger.info("[RESET] Attempting to initialize NO-QUOTA mode as emergency fallback...")
            try:
                from .no_quota_stream_checker import NoQuotaStreamChecker
                self.no_quota_checker = NoQuotaStreamChecker()
                logger.info("[SUCCESS] NO-QUOTA mode initialized as emergency fallback")
                return self.resolve_stream(channel_id)  # Retry with NO-QUOTA
            except Exception as e:
                logger.error(f"[ERROR] Failed to initialize emergency NO-QUOTA mode: {e}")
                # WSP 3 Phase 4: circuit_breaker now handled by youtube_api_ops
                raise StreamResolverError("No API client available and NO-QUOTA mode failed")

        logger.info("="*60)
        logger.info("[TEST] FALLBACK: API STREAM SEARCH STARTING")
        logger.info(f"   Target Channel: {search_channel_id} ({self._get_channel_display_name(search_channel_id)})")
        logger.info(f"   Using Service: {getattr(self.youtube, '_credential_set', 'Unknown') if self.youtube else 'None'}")
        logger.info("="*60)

        try:

            # Try with current service first
            try:
                # Use YouTubeAPIOperations for enhanced API call
                result = self.youtube_api_ops.get_active_livestream_video_id_enhanced(
                    self.youtube, search_channel_id
                )

                if result:
                    video_id, chat_id = result
                    # Record stream start in database (WSP 78)
                    stream_title = self._get_stream_title(video_id)
                    if self.db:
                        self.db.record_stream_start(search_channel_id, video_id, stream_title)
                    # Note: Social media posting handled by auto_moderator_dae
                    # self._trigger_social_media_post(video_id, stream_title)
                    # Save successful connection to cache for future instant access
                    self._save_session_cache(video_id, chat_id)
                    self.logger.info(f"[SUCCESS] Found and cached new livestream for future instant access")
                    return video_id, chat_id
                else:
                    self.logger.info("[ERROR] No active livestream found")
                    return None
                    
            except QuotaExceededError:
                self.logger.warning("[RESET] Quota exceeded during stream search, trying credential rotation...")
                # Try with credential rotation
                fallback_result = get_authenticated_service_with_fallback()
                if fallback_result:
                    fallback_service, fallback_creds, credential_set = fallback_result
                    self.logger.info(f"[SUCCESS] Rotated to credential {credential_set} for stream search")
                    
                    # Update our service instance
                    self.youtube = fallback_service

                    # WSP 3 Phase 4: circuit_breaker now managed by youtube_api_ops
                    self.logger.info("[RESET] Credential rotation successful - youtube_api_ops will handle circuit breaker")
                    
                    # Retry with new credentials using YouTubeAPIOperations
                    result = self.youtube_api_ops.get_active_livestream_video_id_enhanced(
                        self.youtube, search_channel_id
                    )
                    
                    if result:
                        video_id, chat_id = result
                        # Save successful connection to cache for future instant access
                        self._save_session_cache(video_id, chat_id)
                        self.logger.info(f"[SUCCESS] Found and cached new livestream with rotated credentials")
                        return video_id, chat_id
                    else:
                        self.logger.info("[ERROR] No active livestream found with rotated credentials")
                        return None
                else:
                    self.logger.error("[ERROR] Credential rotation failed for stream search")
                    return None
                
        except StreamResolverError as e:
            if "Circuit breaker is OPEN" in str(e):
                self.logger.error("🚫 Circuit breaker prevented API call - too many recent failures")
            else:
                self.logger.error(f"[ERROR] Stream resolution failed: {e}")
            return None
        except Exception as e:
            self.logger.error(f"[ERROR] Unexpected error during stream resolution: {e}")
            return None

    def _get_stream_title(self, video_id: str) -> Optional[str]:
        """
        Get the title of a YouTube stream from its video ID.

        Args:
            video_id: The YouTube video ID

        Returns:
            Stream title if available, None otherwise
        """
        try:
            if self.youtube:
                response = self.youtube.videos().list(
                    part="snippet",
                    id=video_id
                ).execute()

                if response.get("items"):
                    return response["items"][0]["snippet"].get("title")
            return None
        except Exception as e:
            self.logger.debug(f"Could not get stream title: {e}")
            return None

# Example usage block with enhanced error handling
if __name__ == '__main__':
    print("Running enhanced stream_resolver module directly...")
    
    try:
        import sys
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        
        from utils.logging_config import setup_logging
        from dotenv import load_dotenv
        
        load_dotenv()
        setup_logging()
        
        test_channel_id = os.getenv("TEST_CHANNEL_ID", CHANNEL_ID)
        if not test_channel_id:
            print("Please set TEST_CHANNEL_ID or CHANNEL_ID in your .env file")
            sys.exit(1)
        
        print(f"Testing with channel: {mask_sensitive_id(test_channel_id, 'channel')}")
        
        service = get_authenticated_service_with_fallback()
        if service:
            result = get_active_livestream_video_id(service, test_channel_id)
            if result:
                video_id, chat_id = result
                print(f"Success! Found livestream: {mask_sensitive_id(video_id, 'video')}")
                print(f"Chat ID: {mask_sensitive_id(chat_id, 'chat')}")
            else:
                print("No active livestream found")
        else:
            print("Authentication failed")
            
    except Exception as e:
        logger.exception(f"Error during direct execution: {e}")
        print(f"Error: {e}")
        sys.exit(1) 
        sys.exit(1) 