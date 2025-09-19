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
from typing import Optional, Tuple, Dict, Any
import googleapiclient.errors
from googleapiclient.errors import HttpError
from googleapiclient.discovery import Resource
from utils.oauth_manager import get_authenticated_service_with_fallback, get_authenticated_service
from utils.env_loader import get_env_variable
import time
import random
from datetime import datetime, timedelta

# Get a logger instance specific to this module
logger = logging.getLogger(__name__)

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

# Enhanced configuration with better defaults
class StreamResolverConfig:
    """Configuration class for stream resolver settings."""
    
    def __init__(self):
        # Dynamic rate limiting constants
        self.MIN_DELAY = 5.0  # Minimum delay in seconds (high activity)
        self.MAX_DELAY = 60.0  # Maximum delay in seconds (low activity)
        self.MAX_RETRIES = 3  # maximum number of retries for quota errors
        self.QUOTA_ERROR_DELAY = 30.0  # Fixed delay for quota errors
        self.JITTER_FACTOR = 0.2  # Random jitter factor (±20%)
        self.INITIAL_DELAY = 10.0  # Initial delay when no previous delay exists
        self.MAX_CONSECUTIVE_FAILURES = 5  # Maximum number of consecutive failures
        
        # Enhanced retry configuration
        self.EXPONENTIAL_BACKOFF_BASE = 2.0  # Base for exponential backoff
        self.MAX_BACKOFF_DELAY = 300.0  # Maximum backoff delay (5 minutes)
        self.CIRCUIT_BREAKER_THRESHOLD = 10  # Failures before circuit breaker opens
        self.CIRCUIT_BREAKER_TIMEOUT = 600  # Circuit breaker timeout (10 minutes)
        
        # Development override for faster testing
        self.FORCE_DEV_DELAY = os.getenv("FORCE_DEV_DELAY", "false").lower() == "true"
        
        # Load channel ID from environment with validation
        self.CHANNEL_ID = get_env_variable("CHANNEL_ID")
        if not self.CHANNEL_ID:
            raise StreamResolverError("CHANNEL_ID must be defined in environment variables")

# Global configuration instance
config = StreamResolverConfig()

class CircuitBreaker:
    """Circuit breaker pattern implementation for API calls."""
    
    def __init__(self, failure_threshold: int = 10, timeout: int = 600):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
            else:
                raise StreamResolverError("Circuit breaker is OPEN - too many failures")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return True
        return time.time() - self.last_failure_time > self.timeout
    
    def _on_success(self):
        """Handle successful call."""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")

# Global circuit breaker instance
circuit_breaker = CircuitBreaker(
    failure_threshold=config.CIRCUIT_BREAKER_THRESHOLD,
    timeout=config.CIRCUIT_BREAKER_TIMEOUT
)

def calculate_enhanced_delay(
    active_users: int = 0, 
    previous_delay: float = None, 
    consecutive_failures: int = 0,
    retry_count: int = 0
) -> float:
    """
    Enhanced delay calculation with exponential backoff and circuit breaker awareness.
    
    Args:
        active_users: Number of active users in chat (0 if unknown)
        previous_delay: Previous delay used (for smoothing)
        consecutive_failures: Number of consecutive failed attempts
        retry_count: Current retry attempt number
        
    Returns:
        Delay in seconds
    """
    if config.FORCE_DEV_DELAY:
        return 1.0  # Force 1 second delay for fast testing

    # Base delay calculation
    if active_users > 1000:  # High activity
        base_delay = config.MIN_DELAY
    elif active_users > 100:  # Medium activity
        base_delay = config.MIN_DELAY * 2
    elif active_users > 10:  # Low activity
        base_delay = config.MIN_DELAY * 4
    else:  # Very low activity
        base_delay = config.MAX_DELAY

    # Apply exponential backoff for retries
    if retry_count > 0:
        backoff_multiplier = config.EXPONENTIAL_BACKOFF_BASE ** retry_count
        base_delay *= backoff_multiplier
        base_delay = min(base_delay, config.MAX_BACKOFF_DELAY)

    # Increase delay based on consecutive failures
    if consecutive_failures > 0:
        failure_multiplier = 1 + (consecutive_failures * 0.5)  # 50% increase per failure
        base_delay *= failure_multiplier
        base_delay = min(base_delay, config.MAX_DELAY * 2)  # Cap at 2x MAX_DELAY

    # Smooth transitions using previous delay
    if previous_delay is not None:
        smoothing_factor = 0.3
        base_delay = (base_delay * smoothing_factor) + (previous_delay * (1 - smoothing_factor))

    # Add random jitter for human-like behavior
    jitter = base_delay * config.JITTER_FACTOR
    delay = base_delay + random.uniform(-jitter, jitter)
    
    # Ensure delay stays within bounds
    delay = max(config.MIN_DELAY, min(delay, config.MAX_DELAY))
    
    logger.debug(f"Enhanced delay: {delay:.1f}s (base: {base_delay:.1f}s, users: {active_users}, failures: {consecutive_failures}, retry: {retry_count})")
    return delay

def mask_sensitive_id(id_str: str, id_type: str = "default") -> str:
    """
    Enhanced ID masking with better security and formatting.
    
    Args:
        id_str: The ID to mask
        id_type: Type of ID for specific masking rules
        
    Returns:
        Masked ID string
    """
    if not id_str or not isinstance(id_str, str):
        return "None"
        
    # Enhanced masking patterns
    masking_patterns = {
        "channel": lambda s: f"{s[:3]}***...***{s[-4:]}" if len(s) > 10 else "***CHANNEL***",
        "video": lambda s: f"{s[:3]}...{s[-2:]}" if len(s) > 8 else "***VIDEO***",
        "chat": lambda s: f"***ChatID***{s[-4:]}" if len(s) > 8 else "***CHAT***",
        "api_key": lambda s: f"{s[:4]}***...***{s[-4:]}" if len(s) > 12 else "***API_KEY***",
        "default": lambda s: f"{s[:3]}...{s[-2:]}" if len(s) > 8 else "***ID***"
    }
    
    pattern = masking_patterns.get(id_type, masking_patterns["default"])
    return pattern(id_str)

def validate_api_client(youtube_client: Resource) -> bool:
    """
    Validate that the API client is properly configured and functional.
    
    Args:
        youtube_client: YouTube API client to validate
        
    Returns:
        True if client is valid, False otherwise
    """
    if not youtube_client:
        logger.error("API client is None")
        return False
    
    try:
        # Check if client has required methods
        if not hasattr(youtube_client, 'videos') or not hasattr(youtube_client, 'search'):
            logger.error("API client missing required methods")
            return False
        
        # Check if client has developer key or credentials
        if not hasattr(youtube_client, '_developerKey') and not hasattr(youtube_client, '_credentials'):
            logger.error("API client missing authentication")
            return False
        
        logger.debug("API client validation successful")
        return True
        
    except Exception as e:
        logger.error(f"API client validation failed: {e}")
        return False

def check_video_details_enhanced(
    youtube_client: Resource, 
    video_id: str, 
    retry_count: int = 0, 
    previous_delay: float = None
) -> Optional[Dict[str, Any]]:
    """
    Enhanced video details checking with better error handling and validation.
    
    Args:
        youtube_client: An authenticated YouTube Data API client instance
        video_id: The ID of the video to check
        retry_count: Number of retries attempted so far
        previous_delay: Previous delay used for smoothing
        
    Returns:
        A dictionary containing the video details if found, None otherwise
    """
    # Input validation
    if not video_id or not isinstance(video_id, str):
        logger.error("Invalid video ID provided")
        return None
    
    if not validate_api_client(youtube_client):
        raise APIClientError("Invalid API client provided")
    
    try:
        # Use circuit breaker for API calls
        def _make_api_call():
            delay = calculate_enhanced_delay(
                previous_delay=previous_delay, 
                retry_count=retry_count
            )
            logger.debug(f"Waiting {delay:.1f} seconds before API call...")
            
            try:
                time.sleep(delay)
            except KeyboardInterrupt:
                logger.info("Operation interrupted by user")
                return None
            
            # Log which API key is being used (enhanced)
            api_key = getattr(youtube_client, '_developerKey', 'OAuth')
            if api_key != 'OAuth':
                key_name = "YOUTUBE_API_KEY2" if api_key == get_env_variable("YOUTUBE_API_KEY2") else "YOUTUBE_API_KEY"
                logger.debug(f"Using API key: {key_name}")
            else:
                logger.debug("Using OAuth credentials")
            
            response = youtube_client.videos().list(
                part="snippet,liveStreamingDetails,status",  # Added status for better validation
                id=video_id
            ).execute()
            
            return response
        
        response = circuit_breaker.call(_make_api_call)
        if response is None:
            return None
        
        items = response.get("items", [])
        if items:
            video_data = items[0]
            
            # Enhanced validation of video data
            if not video_data.get("snippet"):
                logger.warning(f"Video {mask_sensitive_id(video_id, 'video')} missing snippet data")
                return None
            
            # Check if video is available
            status = video_data.get("status", {})
            if status.get("privacyStatus") == "private":
                logger.warning(f"Video {mask_sensitive_id(video_id, 'video')} is private")
                return None
            
            logger.debug(f"Found valid video details for {mask_sensitive_id(video_id, 'video')}")
            return video_data
            
        logger.debug(f"No video details found for {mask_sensitive_id(video_id, 'video')}")
        return None
        
    except googleapiclient.errors.HttpError as e:
        if e.resp.status == 403 and "quotaExceeded" in str(e):
            logger.info(f"Quota exceeded error: {str(e)}")
            if retry_count < config.MAX_RETRIES:
                logger.warning(f"Quota exceeded (attempt {retry_count + 1}/{config.MAX_RETRIES})")
                
                # Enhanced fallback logic
                fallback_key = get_env_variable("YOUTUBE_API_KEY2")
                if fallback_key:
                    logger.info(f"🔁 Retrying with fallback key: {mask_sensitive_id(fallback_key, 'api_key')}")
                    
                    try:
                        from googleapiclient.discovery import build
                        fallback_client = build("youtube", "v3", developerKey=fallback_key)
                        
                        # Validate fallback client
                        if validate_api_client(fallback_client):
                            delay = config.QUOTA_ERROR_DELAY
                            logger.debug(f"Waiting {delay:.1f} seconds before fallback retry...")
                            time.sleep(delay)
                            
                            return check_video_details_enhanced(
                                fallback_client, video_id, retry_count + 1, delay
                            )
                        else:
                            logger.error("Fallback client validation failed")
                            return None
                            
                    except Exception as fallback_error:
                        logger.error(f"Fallback client creation failed: {fallback_error}")
                        return None
                else:
                    logger.error("No fallback API key available")
                    return None
            else:
                logger.error(f"Max retries ({config.MAX_RETRIES}) reached for quota errors")
                raise QuotaExceededError("Quota exceeded after maximum retries")
                
        elif e.resp.status == 404:
            logger.warning(f"Video {mask_sensitive_id(video_id, 'video')} not found (404)")
            return None
        elif e.resp.status == 403:
            logger.warning(f"Access forbidden for video {mask_sensitive_id(video_id, 'video')} (403)")
            return None
        else:
            logger.error(f"HTTP error checking video details: {e}")
            return None
            
    except Exception as e:
        logger.error(f"Unexpected error checking video details: {e}")
        return None

def search_livestreams_enhanced(
    youtube_client: Resource, 
    event_type: str = "live", 
    retry_count: int = 0, 
    previous_delay: float = None, 
    consecutive_failures: int = 0
) -> Optional[str]:
    """
    Enhanced livestream search with better error handling and validation.
    
    Args:
        youtube_client: YouTube API client
        event_type: Type of event to search for ("live" or "upcoming")
        retry_count: Number of retries attempted
        previous_delay: Previous delay for smoothing
        consecutive_failures: Number of consecutive failures
        
    Returns:
        Video ID of found livestream or None
    """
    # Input validation
    if event_type not in ["live", "upcoming"]:
        logger.error(f"Invalid event type: {event_type}")
        return None
    
    if not validate_api_client(youtube_client):
        raise APIClientError("Invalid API client provided")
    
    try:
        def _make_search_call():
            delay = calculate_enhanced_delay(
                previous_delay=previous_delay, 
                consecutive_failures=consecutive_failures,
                retry_count=retry_count
            )
            logger.info(f"Waiting {delay:.1f} seconds before checking for {event_type} stream...")
            
            try:
                time.sleep(delay)
            except KeyboardInterrupt:
                logger.info("Operation interrupted by user")
                return None

            request = youtube_client.search().list(
                part="id,snippet",
                channelId=config.CHANNEL_ID,
                eventType=event_type,
                type="video",
                maxResults=5,
                order="date"  # Get most recent first
            )
            
            return request.execute()
        
        response = circuit_breaker.call(_make_search_call)
        if response is None:
            return None
        
        items = response.get("items", [])
        if items:
            for item in items:
                video_id = item["id"]["videoId"]
                title = item["snippet"]["title"]
                published_at = item["snippet"].get("publishedAt", "Unknown")
                
                logger.info(f"Found {event_type} stream: {title} (ID: {mask_sensitive_id(video_id, 'video')}, Published: {published_at})")
                
                # Additional validation - check if the stream is actually live/upcoming
                video_details = check_video_details_enhanced(youtube_client, video_id)
                if video_details and "liveStreamingDetails" in video_details:
                    return video_id
                else:
                    logger.debug(f"Stream {mask_sensitive_id(video_id, 'video')} has no live streaming details, skipping")
                    continue
                    
        logger.info(f"No {event_type} livestream found")
        return None
        
    except HttpError as e:
        if "quotaExceeded" in str(e) and retry_count < config.MAX_RETRIES:
            logger.warning(f"Quota exceeded for {event_type} search (attempt {retry_count + 1}/{config.MAX_RETRIES})")
            
            # Enhanced quota handling with exponential backoff
            quota_delay = config.QUOTA_ERROR_DELAY * (config.EXPONENTIAL_BACKOFF_BASE ** retry_count)
            quota_delay = min(quota_delay, config.MAX_BACKOFF_DELAY)
            
            logger.info(f"Waiting {quota_delay:.1f} seconds before retrying...")
            try:
                time.sleep(quota_delay)
            except KeyboardInterrupt:
                logger.info("Operation interrupted by user")
                return None

            return search_livestreams_enhanced(
                youtube_client, event_type, retry_count + 1, quota_delay, consecutive_failures
            )
            
        elif "quotaExceeded" in str(e) and retry_count >= config.MAX_RETRIES:
            logger.error(f"Max retries ({config.MAX_RETRIES}) reached for quota errors")
            raise QuotaExceededError("Quota exceeded after maximum retries")
        else:
            logger.error(f"HTTP error searching for {event_type} streams: {e}")
            return None
            
    except Exception as e:
        logger.error(f"Unexpected error searching for {event_type} streams: {e}")
        return None

def get_active_livestream_video_id_enhanced(
    youtube_client: Resource, 
    channel_id: str
) -> Optional[Tuple[str, str]]:
    """
    Enhanced livestream detection with better error handling and validation.
    
    Args:
        youtube_client: Authenticated YouTube Data API client
        channel_id: YouTube channel ID to search
        
    Returns:
        Tuple (video_id, live_chat_id) if found, None otherwise
    """
    # Input validation
    if not channel_id or not isinstance(channel_id, str):
        logger.error("Invalid channel ID provided")
        return None
    
    if not validate_api_client(youtube_client):
        raise APIClientError("Invalid API client provided")
    
    logger.debug(f"Looking for active/upcoming livestream for channel {mask_sensitive_id(channel_id, 'channel')}")
    
    # Check for environment override with enhanced validation
    env_video_id = get_env_variable("YOUTUBE_VIDEO_ID", default=None)
    if env_video_id:
        logger.info(f"Using override video ID from environment: {mask_sensitive_id(env_video_id, 'video')}")
        
        try:
            video_details = check_video_details_enhanced(youtube_client, env_video_id)
            if video_details and "liveStreamingDetails" in video_details:
                live_chat_id = video_details["liveStreamingDetails"].get("activeLiveChatId")
                if live_chat_id:
                    logger.info(f"Found live chat ID from override video: {mask_sensitive_id(live_chat_id, 'chat')}")
                    return env_video_id, live_chat_id
                else:
                    logger.warning("Override video has no active live chat")
            else:
                logger.warning("Override video has no live streaming details")
        except Exception as e:
            logger.error(f"Error checking override video: {e}")
    
    # Enhanced search with failure tracking
    consecutive_failures = 0
    previous_delay = config.INITIAL_DELAY
    search_attempts = 0
    max_search_attempts = config.MAX_CONSECUTIVE_FAILURES * 2  # Allow more attempts for search

    while consecutive_failures < config.MAX_CONSECUTIVE_FAILURES and search_attempts < max_search_attempts:
        search_attempts += 1
        
        try:
            # Search for active livestream first (higher priority)
            logger.debug(f"Search attempt {search_attempts}/{max_search_attempts}")
            
            video_id = search_livestreams_enhanced(
                youtube_client, 
                event_type="live", 
                previous_delay=previous_delay, 
                consecutive_failures=consecutive_failures
            )
            
            if video_id:
                video_details = check_video_details_enhanced(youtube_client, video_id)
                if video_details and "liveStreamingDetails" in video_details:
                    live_chat_id = video_details["liveStreamingDetails"].get("activeLiveChatId")
                    if live_chat_id:
                        logger.info(f"Found active livestream with chat ID: {mask_sensitive_id(live_chat_id, 'chat')}")
                        return video_id, live_chat_id
                    else:
                        logger.debug("Active livestream found but no chat ID available")

            # If no active livestream, check for upcoming streams
            video_id = search_livestreams_enhanced(
                youtube_client, 
                event_type="upcoming", 
                previous_delay=previous_delay, 
                consecutive_failures=consecutive_failures
            )
            
            if video_id:
                video_details = check_video_details_enhanced(youtube_client, video_id)
                if video_details and "liveStreamingDetails" in video_details:
                    live_chat_id = video_details["liveStreamingDetails"].get("activeLiveChatId")
                    if live_chat_id:
                        logger.info(f"Found upcoming livestream with chat ID: {mask_sensitive_id(live_chat_id, 'chat')}")
                        return video_id, live_chat_id
                    else:
                        logger.debug("Upcoming livestream found but no chat ID available yet")
            
            # Reset consecutive failures on successful search (even if no results)
            consecutive_failures = 0
            
        except QuotaExceededError:
            logger.error("Quota exceeded during livestream search")
            raise
        except APIClientError:
            logger.error("API client error during livestream search")
            raise
        except Exception as e:
            logger.error(f"Error during livestream search: {e}")
            consecutive_failures += 1

        # Update delay for next iteration
        previous_delay = calculate_enhanced_delay(
            consecutive_failures=consecutive_failures, 
            previous_delay=previous_delay
        )
        
        if consecutive_failures > 0:
            logger.info(f"No livestream found (failure {consecutive_failures}/{config.MAX_CONSECUTIVE_FAILURES})")

    if consecutive_failures >= config.MAX_CONSECUTIVE_FAILURES:
        logger.warning("Max consecutive failures reached")
    elif search_attempts >= max_search_attempts:
        logger.warning("Max search attempts reached")
    
    logger.info("No active or upcoming livestream found")
    return None

# Backward compatibility aliases
calculate_dynamic_delay = calculate_enhanced_delay
mask_sensitive_id = mask_sensitive_id  # Already enhanced
check_video_details = check_video_details_enhanced
search_livestreams = search_livestreams_enhanced
get_active_livestream_video_id = get_active_livestream_video_id_enhanced

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
        
        test_channel_id = os.getenv("TEST_CHANNEL_ID", config.CHANNEL_ID)
        if not test_channel_id:
            print("Please set TEST_CHANNEL_ID or CHANNEL_ID in your .env file")
            sys.exit(1)
        
        print(f"Testing with channel: {mask_sensitive_id(test_channel_id, 'channel')}")
        
        service = get_authenticated_service_with_fallback()
        if service:
            result = get_active_livestream_video_id_enhanced(service, test_channel_id)
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