import logging
from typing import Optional # Use Optional for type hinting str | None
import googleapiclient.errors
from googleapiclient.discovery import Resource # For type hinting youtube_client

# Get a logger instance specific to this module
logger = logging.getLogger(__name__)

def check_video_details(youtube_client: Resource, video_id: str) -> Optional[dict]:
    """
    Gets the details of a specific video, including its livestream status.

    Args:
        youtube_client: An authenticated YouTube Data API client instance.
        video_id: The ID of the video to check.

    Returns:
        A dictionary containing the video details if found, None otherwise.
    """
    try:
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
    except Exception as e:
        logger.error(f"Error checking video details for {video_id}: {e}")
        return None

def get_active_livestream_video_id(youtube_client: Resource, channel_id: str) -> Optional[str]:
    """
    Finds the video ID of the currently active livestream for a given channel using the YouTube Search API.

    Args:
        youtube_client: An authenticated YouTube Data API client instance (googleapiclient.discovery.Resource).
        channel_id: The ID of the YouTube channel to search within.

    Returns:
        The video ID (str) of the active livestream if found, otherwise None.
    """
    if not youtube_client:
        logger.error("YouTube client object is required but was not provided.")
        return None
    if not channel_id:
        logger.error("Channel ID is required but was not provided.")
        return None

    logger.info(f"Attempting to find active livestream for channel ID: {channel_id}")

    try:
        # First try to find an active livestream
        search_response = youtube_client.search().list(
            part="id,snippet",     # We need snippet to check the status
            channelId=channel_id,
            eventType="live",      # Filter for live events
            type="video",          # Only interested in video results
            maxResults=5           # Get more results to check status
        ).execute()

        logger.debug(f"Search response: {search_response}")

        items = search_response.get("items", [])
        if items:
            logger.info(f"Found {len(items)} potential livestreams")
            # Check each item for active livestream
            for item in items:
                video_id = item.get("id", {}).get("videoId")
                if not video_id:
                    continue

                logger.debug(f"Checking video ID: {video_id}")
                # Get video details to check livestream status
                video_details = check_video_details(youtube_client, video_id)
                if video_details:
                    live_details = video_details.get("liveStreamingDetails", {})
                    if live_details:
                        logger.debug(f"Live details for {video_id}: {live_details}")
                        # Check if the stream is actually live
                        if live_details.get("actualStartTime") and not live_details.get("actualEndTime"):
                            logger.info(f"Found active livestream video ID: {video_id} for channel {channel_id}")
                            return video_id

        # If no active livestream found, try to find a scheduled one
        logger.info("No active livestream found, checking for scheduled streams...")
        search_response = youtube_client.search().list(
            part="id,snippet",
            channelId=channel_id,
            eventType="upcoming",  # Look for upcoming events
            type="video",
            maxResults=5
        ).execute()

        logger.debug(f"Upcoming search response: {search_response}")

        items = search_response.get("items", [])
        if items:
            logger.info(f"Found {len(items)} scheduled streams")
            # Get the first upcoming stream
            video_id = items[0].get("id", {}).get("videoId")
            if video_id:
                logger.info(f"Found scheduled livestream video ID: {video_id} for channel {channel_id}")
                return video_id

        # No livestream found
        logger.warning(f"No active or scheduled livestream found for channel ID: {channel_id}")
        return None

    except googleapiclient.errors.HttpError as e:
        logger.error(f"HTTP error occurred while searching for livestream on channel {channel_id}: {e}")
        return None
    except Exception as e:
        logger.exception(f"An unexpected error occurred while searching for livestream on channel {channel_id}: {e}")
        return None

# Example usage block (optional, for basic testing)
if __name__ == '__main__':
    # This block will only run when the script is executed directly
    # It requires you to manually set up authentication and channel ID for testing
    print("Running stream_resolver module directly (requires manual setup for testing)...")

    # --- Manual Setup Required for Direct Test ---
    # 1. Ensure utils.logging_config and modules.youtube_auth are available
    # 2. You might need to adjust sys.path if running directly from modules/
    import os, sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

    from utils.logging_config import setup_logging
    from modules.youtube_auth import get_authenticated_service
    from dotenv import load_dotenv

    load_dotenv()
    setup_logging() # Configure logging

    try:
        # Replace with a channel ID known to have active streams sometimes for testing
        test_channel_id = os.getenv("TEST_CHANNEL_ID", "UC_x5XG1OV2P6uZZ5FSM9Ttw") # Example: Google Developers channel
        if test_channel_id == "YOUR_CHANNEL_ID_HERE":
             print("Please set TEST_CHANNEL_ID in your .env file or environment for testing.")
        else:
            print(f"Attempting to authenticate and find live stream for channel: {test_channel_id}")
            service = get_authenticated_service()
            if service:
                live_video_id = get_active_livestream_video_id(service, test_channel_id)
                if live_video_id:
                    print(f"Success! Found live video ID: {live_video_id}")
                else:
                    print("Test completed. No active livestream found or an error occurred.")
            else:
                print("Authentication failed, cannot perform test.")

    except Exception as main_e:
        print(f"An error occurred during direct execution test: {main_e}")
    # --- End Manual Setup --- 