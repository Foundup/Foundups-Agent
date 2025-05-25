import logging
import os
import sys
import asyncio
import time
from dotenv import load_dotenv
from googleapiclient.discovery import build
from modules.stream_resolver import get_active_livestream_video_id, check_video_details, QuotaExceededError
from modules.livechat import LiveChatListener
from utils.oauth_manager import get_authenticated_service, get_authenticated_service_with_fallback, start_credential_cooldown, Credentials
from utils.env_loader import get_env_variable
from modules.banter_engine import BanterEngine
from googleapiclient.errors import HttpError

def mask_sensitive_id(id_str: str) -> str:
    '''Mask sensitive IDs in logs.'''
    if not id_str:
        return "None"
    return f"{id_str[:4]}...{id_str[-4:]}"

async def find_active_livestream(service, channel_id, max_attempts=None):
    '''Continuously search for active livestream with throttling.'''
    logger = logging.getLogger(__name__)
    attempt = 0
    previous_delay = None
    
    while True:
        if max_attempts and attempt >= max_attempts:
            logger.error(f"Max attempts ({max_attempts}) reached without finding livestream")
            return None, None
            
        attempt += 1
        logger.info(f"Attempt {attempt} to find active livestream for channel: {mask_sensitive_id(channel_id)}")
        
        # Calculate and apply throttling delay
        try:
            from utils.timing import calculate_dynamic_delay # Attempt import if not global
        except ImportError:
            def calculate_dynamic_delay(previous_delay=None, **kwargs): return 5.0 # Default fallback
        
        delay = calculate_dynamic_delay(previous_delay=previous_delay)
        logger.info(f"Waiting {delay:.1f} seconds before checking for livestream...")
        await asyncio.sleep(delay)
        
        try:
            result = get_active_livestream_video_id(service, channel_id)
            if result:
                video_id, chat_id = result
                logger.info(f"Found active livestream - Video ID: {mask_sensitive_id(video_id)}, Chat ID: {mask_sensitive_id(chat_id)}")
                return video_id, chat_id
            else:
                logger.info("No active livestream found, will retry...")
                previous_delay = delay
        except QuotaExceededError:
            logger.debug("QuotaExceededError caught in find_active_livestream, re-raising for main loop handler.")
            raise
        except Exception as e:
            logger.error(f"Error searching for livestream: {e}")
            previous_delay = delay * 2  # Double the delay on error

async def main():
    '''Main entry point for the application.'''
    logger = logging.getLogger(__name__)
    
    try:
        # Get channel ID from environment
        channel_id = get_env_variable("CHANNEL_ID")
        if not channel_id:
            logger.error("CHANNEL_ID not found in environment variables")
            return
            
        # Get authenticated service with fallback first
        auth_result = get_authenticated_service_with_fallback()
        if not auth_result:
            logger.error("Failed to get authenticated YouTube service initially")
            return
        service, current_credentials, current_credential_set = auth_result
        logger.info(f"Initial authentication successful with {current_credential_set}")
        
        # Initialize banter engine
        banter_engine = BanterEngine()
        
        # Continuously look for active livestream
        while True:
            try:
                video_id, chat_id = await find_active_livestream(service, channel_id)
                
                if video_id and chat_id:
                    # Initialize chat listener
                    listener = LiveChatListener(service, current_credentials, video_id, chat_id, banter_engine=banter_engine)
                    
                    # Start listening
                    logger.info("Starting chat listener...")
                    await listener.start_listening()
                    
                    # If we get here, the listener has stopped
                    logger.info("Chat listener stopped, will look for new livestream...")
                else:
                    logger.info("No active livestream found, will continue searching...")
            
            except QuotaExceededError:
                logger.warning(f"Quota exceeded with {current_credential_set}. Attempting rotation.")
                start_credential_cooldown(current_credential_set) # Put the failed set in cooldown
                
                # Try to get the next credential set
                auth_result = get_authenticated_service_with_fallback()
                if not auth_result:
                    logger.critical("All credential sets are exhausted or in cooldown. Waiting 1 hour before trying again.")
                    # TODO: Implement a more robust waiting strategy (e.g., exponential backoff)
                    await asyncio.sleep(3600) # Wait 1 hour
                    continue # Restart the auth process
                
                service, current_credentials, current_credential_set = auth_result
                logger.info(f"Successfully rotated to {current_credential_set}")
                # Loop will continue and try find_active_livestream again with the new service
                
            except Exception as e:
                # Catch other potential errors during find_active_livestream or listener execution
                logger.error(f"An unexpected error occurred in the main loop: {e}")
                logger.info("Waiting 60 seconds before retrying...")
                await asyncio.sleep(60) # Wait a bit before retrying the loop
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        raise

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Run the async main function
    asyncio.run(main())