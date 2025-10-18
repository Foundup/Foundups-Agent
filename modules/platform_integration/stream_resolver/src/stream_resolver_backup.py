import os

# WSP Guard: Prevent accidental overwrites. Requires WSP_ALLOW_STREAM_PATCH=1 env var to run modified versions.
if not os.getenv("WSP_ALLOW_STREAM_PATCH"):
    # Check a sentinel value in the original/locked file to prevent the guard from blocking the intended version.
    # Replace 'SENTINEL_VALUE_STREAM_RESOLVER_LOCKED' with an actual unique string present ONLY in the locked version.
    # For example, a specific comment or a unique part of a docstring added during locking.
    # This check ensures the guard only activates if the file content *differs* from the locked version
    # and the override flag is *not* set.
    # Placeholder check (replace with actual content check):
    try:
        with open(__file__, 'r', encoding='utf-8') as f_guard:
            content = f_guard.read()
            # Example: Check for the manual comment we added earlier
            if "# Locked version 0.1.5 (Rotation Fix)." not in content:
                 raise RuntimeError("stream_resolver.py has been modified from the locked version 0.1.5. Set WSP_ALLOW_STREAM_PATCH=1 to allow running modified code.")
    except Exception as e_guard:
        # Fallback if reading fails or sentinel isn't found - still raise error if flag isn't set
        raise RuntimeError(f"stream_resolver.py is protected (or guard check failed: {e_guard}). Set WSP_ALLOW_STREAM_PATCH=1 to allow modifications.") from e_guard

# WSP: DO NOT OVERWRITE THIS FILE without explicit consent/patch flag.
# Locked version 0.1.5 (Rotation Fix).
import logging
from typing import Optional, Tuple
import googleapiclient.errors
from googleapiclient.errors import HttpError
from googleapiclient.discovery import Resource
from utils.oauth_manager import get_authenticated_service_with_fallback, get_authenticated_service
from utils.env_loader import get_env_variable
import time
import random

# Get a logger instance specific to this module
logger = logging.getLogger(__name__)

# Define custom exception for quota errors
class QuotaExceededError(Exception):
    """Custom exception for when API quota is exceeded after retries."""
    pass

# Development override for faster testing
FORCE_DEV_DELAY = True

# Dynamic rate limiting constants
MIN_DELAY = 5.0  # Minimum delay in seconds (high activity)
MAX_DELAY = 60.0  # Maximum delay in seconds (low activity)
MAX_RETRIES = 3  # maximum number of retries for quota errors
QUOTA_ERROR_DELAY = 30.0  # Fixed delay for quota errors
JITTER_FACTOR = 0.2  # Random jitter factor (±20%)
INITIAL_DELAY = 10.0  # Initial delay when no previous delay exists
MAX_CONSECUTIVE_FAILURES = 5  # Maximum number of consecutive failures before increasing delay

def calculate_dynamic_delay(active_users: int = 0, previous_delay: float = None, consecutive_failures: int = 0) -> float:
    """


    Calculate a human-like delay based on chat activity and failure history.
    
    Args:
        active_users: Number of active users in chat (0 if unknown)
        previous_delay: Previous delay used (for smoothing)
        consecutive_failures: Number of consecutive failed attempts
        
    Returns:
        Delay in seconds
    """
    if FORCE_DEV_DELAY:
        return 1.0  # Force 1 second delay for fast testing

    # Base delay calculation
    if active_users > 1000:  # High activity
        base_delay = MIN_DELAY
    elif active_users > 100:  # Medium activity
        base_delay = MIN_DELAY * 2
    elif active_users > 10:  # Low activity
        base_delay = MIN_DELAY * 4
    else:  # Very low activity
        base_delay = MAX_DELAY

    # Increase delay based on consecutive failures
    if consecutive_failures > 0:
        base_delay *= (1 + (consecutive_failures * 0.5))  # 50% increase per failure
        base_delay = min(base_delay, MAX_DELAY * 2)  # Cap at 2x MAX_DELAY

    # Smooth transitions using previous delay
    if previous_delay is not None:
        # Gradually adjust towards target delay
        smoothing_factor = 0.3
        base_delay = (base_delay * smoothing_factor) + (previous_delay * (1 - smoothing_factor))

    # Add random jitter for human-like behavior
    jitter = base_delay * JITTER_FACTOR
    delay = base_delay + random.uniform(-jitter, jitter)
    
    # Ensure delay stays within bounds
    delay = max(MIN_DELAY, min(delay, MAX_DELAY))
    
    logger.debug(f"Calculated delay: {delay:.1f}s (base: {base_delay:.1f}s, users: {active_users}, failures: {consecutive_failures})")
    return delay

def mask_sensitive_id(id_str: str, id_type: str = "default") -> str:
    """
    Mask sensitive IDs in logs with consistent formatting.
    
    Args:
        id_str: The ID to mask
        id_type: Type of ID for specific masking rules ("channel", "video", "chat", "default")
        
    Returns:
        Masked ID string
    """
    if not id_str:
        return "None"
        
    if id_type == "channel":
        # Channel IDs start with UC-, mask middle
        return f"{id_str[:3]}***...***{id_str[-4:]}"
    elif id_type == "video":
        # Video IDs are shorter, show first 3 and last 2
        return f"{id_str[:3]}...{id_str[-2:]}"
    elif id_type == "chat":
        # Chat IDs are longer, mask most of it
        return f"***ChatID***{id_str[-4:]}"
    else:
        # Default masking: show first 3 and last 2
        return f"{id_str[:3]}...{id_str[-2:]}"

# Load channel ID from environment
CHANNEL_ID = get_env_variable("CHANNEL_ID")

def check_video_details(youtube_client: Resource, video_id: str, retry_count: int = 0, previous_delay: float = None) -> Optional[dict]:
    """
    Gets the details of a specific video, including its livestream status.
    
    Args:
        youtube_client: An authenticated YouTube Data API client instance.
        video_id: The ID of the video to check.
        retry_count: Number of retries attempted so far.
        previous_delay: Previous delay used for smoothing.
        
    Returns:
        A dictionary containing the video details if found, None otherwise.
    """
    try:
        delay = calculate_dynamic_delay(previous_delay=previous_delay)
        logger.debug(f"Waiting {delay:.1f} seconds before API call...")
        try:
            time.sleep(delay)
        except KeyboardInterrupt:
            logger.info("Operation interrupted by user")
            return None
        
        # Log which API key is being used
        api_key = youtube_client._developerKey
        key_name = "YOUTUBE_API_KEY2" if api_key == get_env_variable("YOUTUBE_API_KEY2") else "YOUTUBE_API_KEY"
        logger.debug(f"Using API key: {key_name}")
        
        response = youtube_client.videos().list(
            part="snippet,liveStreamingDetails",
            id=video_id
        ).execute()
        
        items = response.get("items", [])
        if items:
            logger.debug(f"Found video details: {items[0]}")
            return items[0]
        logger.debug("No video details found")
        return None
        
    except googleapiclient.errors.HttpError as e:
        if e.resp.status == 403 and "quotaExceeded" in str(e):
            logger.info(f"Caught quota exceeded error: {str(e)}")
            if retry_count < MAX_RETRIES:
                logger.warning(f"Quota exceeded with primary credentials (attempt {retry_count + 1}/{MAX_RETRIES})")
                delay = QUOTA_ERROR_DELAY
                logger.debug(f"Waiting {delay:.1f} seconds before retry...")
                try:
                    time.sleep(delay)
                except KeyboardInterrupt:
                    logger.info("Operation interrupted by user")
                    return None
                
                # Try with fallback API key
                fallback_key = get_env_variable("YOUTUBE_API_KEY2")
                if fallback_key:
                    logger.info(f"🔁 Retrying with fallback key: {mask_sensitive_id(fallback_key)}")
                    # Create new client with fallback key
                    from googleapiclient.discovery import build
                    fallback_client = build("youtube", "v3", developerKey=fallback_key)
                    return check_video_details(fallback_client, video_id, retry_count + 1, delay)
                else:
                    logger.error("No fallback API key available")
                    return None
            else:
                logger.error(f"Max retries ({MAX_RETRIES}) reached for quota errors")
                return None
        logger.error(f"Error checking video details for {video_id}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error checking video details for {video_id}: {e}")
        return None

def search_livestreams(youtube_client, event_type="live", retry_count: int = 0, previous_delay: float = None, consecutive_failures: int = 0):
    """Search for livestreams with the given event type."""
    try:
        # Calculate and apply throttling delay
        delay = calculate_dynamic_delay(previous_delay=previous_delay, consecutive_failures=consecutive_failures)
        logger.info(f"Waiting {delay:.1f} seconds before checking for {event_type} stream...")
        try:
            time.sleep(delay)
        except KeyboardInterrupt:
            logger.info("Operation interrupted by user")
            return None

        request = youtube_client.search().list(
            part="id,snippet",
            channelId=CHANNEL_ID,
            eventType=event_type,
            type="video",
            maxResults=5
        )
        response = request.execute()
        if response.get("items"):
            for item in response["items"]:
                video_id = item["id"]["videoId"]
                title = item["snippet"]["title"]
                logger.info(f"Found {event_type} stream: {title} (ID: {mask_sensitive_id(video_id, 'video')})")
                return video_id
        logger.info("No active livestream found")
        return None
    except HttpError as e:
        if "quotaExceeded" in str(e) and retry_count < MAX_RETRIES:
            logger.warning(f"Quota exceeded with current credentials (attempt {retry_count + 1}/{MAX_RETRIES})")
            # Apply quota error delay
            quota_delay = QUOTA_ERROR_DELAY
            logger.info(f"Waiting {quota_delay:.1f} seconds before retrying...")
            try:
                time.sleep(quota_delay)
            except KeyboardInterrupt:
                logger.info("Operation interrupted by user")
                return None

            # Retry with the *same* client
            logger.info("🔁 Retrying API call with same credentials")
            return search_livestreams(youtube_client, event_type, retry_count + 1, quota_delay, consecutive_failures)
        elif "quotaExceeded" in str(e) and retry_count >= MAX_RETRIES:
            logger.error(f"Max retries ({MAX_RETRIES}) reached for quota errors with current credentials.")
            raise QuotaExceededError("Quota exceeded after maximum retries.")
        elif retry_count >= MAX_RETRIES:
            logger.error(f"Max retries ({MAX_RETRIES}) reached for other errors")
            return None
        else:
            logger.error(f"Error searching for livestreams: {e}")
            consecutive_failures += 1
            return None
    except Exception as e:
        logger.error(f"Unexpected error searching for livestreams: {e}")
        return None

def get_active_livestream_video_id(youtube_client: Resource, channel_id: str) -> Optional[Tuple[str, str]]:
    """
    Get the video ID of an active or upcoming livestream and its chat ID.
    Handles both active and upcoming streams, with preference to active.
    
    Args:
        youtube_client: Authenticated YouTube Data API client
        channel_id: YouTube channel ID to search
        
    Returns:
        Tuple (video_id, live_chat_id) if found, None otherwise
    """
    logger.debug(f"Looking for active/upcoming livestream for channel {mask_sensitive_id(channel_id, 'channel')}")
    
    # First check if there's an override video ID in environment
    env_video_id = get_env_variable("YOUTUBE_VIDEO_ID", default=None)
    if env_video_id:
        logger.info(f"Using override video ID from environment: {mask_sensitive_id(env_video_id, 'video')}")
        video_details = check_video_details(youtube_client, env_video_id)
        if video_details and "liveStreamingDetails" in video_details:
            live_chat_id = video_details["liveStreamingDetails"].get("activeLiveChatId")
            if live_chat_id:
                logger.info(f"Found live chat ID from override video: {mask_sensitive_id(live_chat_id, 'chat')}")
                return env_video_id, live_chat_id

    # Search for active livestream with consecutive failures tracking
    consecutive_failures = 0
    previous_delay = INITIAL_DELAY

    while consecutive_failures < MAX_CONSECUTIVE_FAILURES:
        try:
            # Search for active livestream
            video_id = search_livestreams(youtube_client, event_type="live", previous_delay=previous_delay, consecutive_failures=consecutive_failures)
            if video_id:
                video_details = check_video_details(youtube_client, video_id)
                if video_details and "liveStreamingDetails" in video_details:
                    live_chat_id = video_details["liveStreamingDetails"].get("activeLiveChatId")
                    if live_chat_id:
                        logger.info(f"Found active livestream with chat ID: {mask_sensitive_id(live_chat_id, 'chat')}")
                        return video_id, live_chat_id

            # If no active livestream found, check for upcoming streams
            video_id = search_livestreams(youtube_client, event_type="upcoming", previous_delay=previous_delay, consecutive_failures=consecutive_failures)
            if video_id:
                video_details = check_video_details(youtube_client, video_id)
                if video_details and "liveStreamingDetails" in video_details:
                    live_chat_id = video_details["liveStreamingDetails"].get("activeLiveChatId")
                    if live_chat_id:
                        logger.info(f"Found upcoming livestream with chat ID: {mask_sensitive_id(live_chat_id, 'chat')}")
                        return video_id, live_chat_id
        except Exception as e:
            logger.error(f"Error while searching for livestream: {e}")
            # Continue with the failure handling logic below

        # Increment consecutive failures and update delay
        consecutive_failures += 1
        previous_delay = calculate_dynamic_delay(consecutive_failures=consecutive_failures, previous_delay=previous_delay)
        logger.info(f"No livestream found (attempt {consecutive_failures}/{MAX_CONSECUTIVE_FAILURES})")

    logger.info("Max consecutive failures reached, waiting for next cycle")
    return None

# Example usage block (optional, for basic testing)
if __name__ == '__main__':
    # This block will only run when the script is executed directly
    print("Running stream_resolver module directly (requires manual setup for testing)...")

    # --- Manual Setup Required for Direct Test ---
    import os, sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

    from utils.logging_config import setup_logging
    from dotenv import load_dotenv

    load_dotenv()
    setup_logging()

    try:
        test_channel_id = os.getenv("TEST_CHANNEL_ID", "UC_x5XG1OV2P6uZZ5FSM9Ttw")
        if test_channel_id == "YOUR_CHANNEL_ID_HERE":
            print("Please set TEST_CHANNEL_ID in your .env file or environment for testing.")
        else:
            print(f"Attempting to authenticate and find live stream for channel: {test_channel_id}")
            service = get_authenticated_service_with_fallback()
            if service:
                live_video_id, live_chat_id = get_active_livestream_video_id(service, test_channel_id)
                if live_video_id:
                    print(f"Success! Found live video ID: {live_video_id}, chat ID: {live_chat_id}")
                else:
                    print("Test completed. No active livestream found or an error occurred.")
            else:
                print("Authentication failed, cannot perform test.")

    except Exception as main_e:
        print(f"An error occurred during direct execution test: {main_e}")
    # --- End Manual Setup --- 