
# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
# === END UTF-8 ENFORCEMENT ===

import logging
from modules.platform_integration.youtube_auth.src.youtube_auth import get_authenticated_service
from utils.env_loader import get_env_variable
import os
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(levelname)-8s | %(name)-12s | %(funcName)-20s | %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    # Force reload environment variables
    load_dotenv(override=True)
    
    # Debug: Print raw environment variable
    logger.info(f"Raw CHANNEL_ID from os.environ: {os.environ.get('CHANNEL_ID')}")
    
    # Get channel ID
    channel_id = get_env_variable('CHANNEL_ID')
    if not channel_id:
        logger.error("CHANNEL_ID not found in environment variables")
        return
    
    logger.info(f"Using channel ID: {channel_id}")
    
    # Get YouTube service
    youtube_service = get_authenticated_service()
    if not youtube_service:
        logger.error("Failed to get YouTube service")
        return
    
    try:
        # Get channel details with minimal parts
        logger.info("Making channel request...")
        channel_response = youtube_service.channels().list(
            part="snippet",
            id=channel_id
        ).execute()
        
        logger.info(f"Channel response: {channel_response}")
        
        if channel_response.get('items'):
            channel = channel_response['items'][0]
            logger.info(f"Found channel: {channel['snippet']['title']}")
            logger.info(f"Channel description: {channel['snippet']['description']}")
        else:
            logger.error("No channel found with this ID")
            
    except Exception as e:
        logger.error(f"Error accessing channel: {str(e)}")

if __name__ == "__main__":
    main() 