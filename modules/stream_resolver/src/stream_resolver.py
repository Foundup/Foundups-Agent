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

# Development override for faster testing
FORCE_DEV_DELAY = True

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

# Dynamic rate limiting constants
MIN_DELAY = 5.0  # Minimum delay in seconds (high activity)
MAX_DELAY = 60.0  # Maximum delay in seconds (low activity)
MAX_RETRIES = 3  # maximum number of retries for quota errors
QUOTA_ERROR_DELAY = 30.0  # Fixed delay for quota errors
JITTER_FACTOR = 0.2  # Random jitter factor (±20%)

def calculate_dynamic_delay(active_users: int = 0, previous_delay: float = None) -> float:
    """
    Calculate a human-like delay based on chat activity.
    
    Args:
        active_users: Number of active users in chat (0 if unknown)
        previous_delay: Previous delay used (for smoothing)
        
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
    
    logger.debug(f"Calculated delay: {delay:.1f}s (base: {base_delay:.1f}s, users: {active_users})")
    return delay

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

def search_livestreams(youtube_client: Resource, event_type: str = "live") -> Optional[str]:
    """
    Search for livestreams with the given event type.
    Returns the video ID of the first matching livestream, or None if none found.
    """
    try:
        # Calculate delay based on channel size (using default value)
        delay = calculate_dynamic_delay(active_users=0)
        logger.debug(f"Waiting {delay:.1f} seconds before API call...")
        time.sleep(delay)
        
        # Search for livestreams
        request = youtube_client.search().list(
            part="id,snippet",
            channelId=CHANNEL_ID,
            eventType=event_type,
            type="video",
            maxResults=5
        )
        
        try:
            response = request.execute()
        except HttpError as e:
            if "quotaExceeded" in str(e):
                logger.warning(f"Quota exceeded with current credentials for {event_type} search")
                # Let the quota manager handle credential rotation
                fallback_client = get_authenticated_service_with_fallback()
                if fallback_client:
                    logger.info("Retrying with fallback credentials")
                    return search_livestreams(fallback_client, event_type)
                else:
                    logger.error("No fallback credentials available")
                    return None
            else:
                logger.error(f"HTTP error searching for {event_type} streams: {e}")
                return None
        
        # Process response
        if response.get("items"):
            for item in response["items"]:
                video_id = item["id"]["videoId"]
                title = item["snippet"]["title"]
                logger.info(f"Found {event_type} stream: {title} (ID: {mask_sensitive_id(video_id, 'video')})")
                return video_id
                
        logger.info(f"No {event_type} streams found")
        return None
        
    except Exception as e:
        logger.error(f"Error searching for {event_type} streams: {e}")
        return None

def get_active_livestream_video_id(youtube_client: Resource, channel_id: str) -> Optional[Tuple[str, str]]:
    """
    Get the video ID and live chat ID of the active livestream for a channel.
    
    Args:
        youtube_client: Authenticated YouTube API client
        channel_id: YouTube channel ID
        
    Returns:
        tuple: (video_id, live_chat_id) if found, None otherwise
    """
    logger.info(f"Attempting to find active livestream for channel ID: {mask_sensitive_id(channel_id, 'channel')}")
    
    # Optional override using .env YOUTUBE_VIDEO_ID
    env_video_id = get_env_variable("YOUTUBE_VIDEO_ID", default=None)
    if env_video_id:
        logger.info(f"Using YOUTUBE_VIDEO_ID override from .env: {mask_sensitive_id(env_video_id, 'video')}")
        video_details = check_video_details(youtube_client, env_video_id)
        if video_details and "liveStreamingDetails" in video_details:
            live_chat_id = video_details["liveStreamingDetails"].get("activeLiveChatId")
            if live_chat_id:
                logger.info(f"Found live chat ID from override video: {mask_sensitive_id(live_chat_id, 'chat')}")
                return env_video_id, live_chat_id

    # Calculate initial delay based on activity level
    delay = calculate_dynamic_delay()
    logger.debug(f"Calculated delay: {delay:.1f}s (base: {MIN_DELAY}s)")
    
    # First try to find active livestream
    try:
        logger.debug(f"Waiting {delay:.1f} seconds before API call...")
        time.sleep(delay)
        video_id = search_livestreams(youtube_client, event_type="live")
        if video_id:
            logger.info(f"Found live stream: {mask_sensitive_id(video_id, 'video')}")
            # Get live chat ID for the video
            video_details = check_video_details(youtube_client, video_id)
            if video_details and "liveStreamingDetails" in video_details:
                live_chat_id = video_details["liveStreamingDetails"].get("activeLiveChatId")
                if live_chat_id:
                    return video_id, live_chat_id
    except Exception as e:
        logger.error(f"Error searching for live streams: {str(e)}")
    
    # If no active livestream, try upcoming streams
    try:
        delay = calculate_dynamic_delay()
        logger.debug(f"Waiting {delay:.1f} seconds before API call...")
        time.sleep(delay)
        video_id = search_livestreams(youtube_client, event_type="upcoming")
        if video_id:
            logger.info(f"Found upcoming stream: {mask_sensitive_id(video_id, 'video')}")
            # Get live chat ID for the video
            video_details = check_video_details(youtube_client, video_id)
            if video_details and "liveStreamingDetails" in video_details:
                live_chat_id = video_details["liveStreamingDetails"].get("activeLiveChatId")
                if live_chat_id:
                    return video_id, live_chat_id
    except Exception as e:
        logger.error(f"Error searching for upcoming streams: {str(e)}")
    
    logger.info("No active livestream found")
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