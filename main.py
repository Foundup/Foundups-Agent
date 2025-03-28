import os
import logging
import argparse
from dotenv import load_dotenv
import googleapiclient.errors
from modules.youtube_auth import get_authenticated_service
from modules.livechat import LiveChatListener
from modules.stream_resolver import get_active_livestream_video_id
from utils.logging_config import setup_logging
from utils.env_loader import get_env_variable

# --- Setup Logging ---
# This must be done before importing modules that use logging
setup_logging()

# --- Load Environment Variables ---
# This ensures proper loading order: system > .env.local > .env
load_dotenv(override=True)  # Force reload environment variables

# Get environment variables after loading
CHANNEL_ID = get_env_variable("CHANNEL_ID")
YOUTUBE_API_KEY = get_env_variable("YOUTUBE_API_KEY")
AGENT_GREETING_MESSAGE = get_env_variable("AGENT_GREETING_MESSAGE", default="Hello everyone! reporting for duty. I'm here to listen and learn (and maybe crack a joke). Beep boop!")

def main():
    """Main entry point for the FoundUps Agent."""
    logger = logging.getLogger(__name__)
    logger.info("--- FoundUps Agent Initializing ---")

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="FoundUps Agent - YouTube Livestream Chat Bot")
    parser.add_argument(
        "--video-id",
        help="YouTube Video ID of the livestream to join. If not provided, will search for active livestream on the channel.",
        default=None
    )
    args = parser.parse_args()

    try:
        # Attempt YouTube authentication
        logger.info("Attempting YouTube authentication...")
        youtube_service = get_authenticated_service()
        logger.info("Authentication successful.")

        # Get video ID either from command line or by searching for active livestream
        video_id = args.video_id
        if not video_id:
            if not CHANNEL_ID:
                logger.critical("Error: CHANNEL_ID is required in .env file when no video ID is provided.")
                return
                
            logger.info("No video ID provided, searching for active livestream...")
            video_id = get_active_livestream_video_id(youtube_service, CHANNEL_ID)
            if video_id:
                logger.info(f"Found active livestream with video ID: {video_id}")
            else:
                logger.error("No active livestream found on the channel.")
                return

        # Initialize and start the chat listener
        logger.info(f"Initializing chat listener for video ID: {video_id}")
        chat_listener = LiveChatListener(youtube_service, video_id)
        chat_listener.start_listening()

    except googleapiclient.errors.HttpError as http_error:
        logger.error(f"HTTP error occurred: {http_error}")
    except Exception as e:
        logger.error(f"Critical error: {e}")
        raise

if __name__ == "__main__":
    main()
