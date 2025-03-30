import logging
import os
import sys
import asyncio
from dotenv import load_dotenv
from googleapiclient.discovery import build
from modules.stream_resolver.src.stream_resolver import get_active_livestream_video_id
from modules.livechat.src.livechat import LiveChatListener
from utils.oauth_manager import get_authenticated_service
from utils.env_loader import get_env_variable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def mask_sensitive_id(id_str: str) -> str:
    """Mask sensitive IDs in logs."""
    if not id_str:
        return "None"
    return f"{id_str[:4]}...{id_str[-4:]}"

async def main():
    """Main entry point for the FoundUps Agent."""
    try:
        # Load environment variables
        load_dotenv()
        
        # Get API key and channel ID
        api_key = get_env_variable("YOUTUBE_API_KEY")
        channel_id = get_env_variable("CHANNEL_ID")
        
        if not api_key or not channel_id:
            logger.error("Missing required environment variables")
            return
            
        # Initialize YouTube API client with OAuth
        youtube = get_authenticated_service()
        if not youtube:
            logger.error("Failed to get authenticated YouTube service")
            return
        
        # Get active livestream
        logger.info(f"Attempting to find active livestream for channel ID: {mask_sensitive_id(channel_id)}")
        result = get_active_livestream_video_id(youtube, channel_id)
        
        if not result:
            logger.error("No active livestream found")
            return
            
        video_id, chat_id = result
        logger.info(f"Found active livestream - Video ID: {mask_sensitive_id(video_id)}, Chat ID: {mask_sensitive_id(chat_id)}")
        
        # Initialize chat listener
        logger.info("Starting chat listener...")
        listener = LiveChatListener(youtube, video_id, chat_id)
        
        # Start listening to chat
        logger.info("Starting chat polling...")
        await listener.start_listening()
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
