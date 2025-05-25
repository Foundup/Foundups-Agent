import logging
import os
import sys
import asyncio
import time
from unittest.mock import MagicMock # Added for mocking
from dotenv import load_dotenv
from googleapiclient.discovery import build
from modules.platform_integration.stream_resolver.stream_resolver import get_active_livestream_video_id, check_video_details, QuotaExceededError, calculate_dynamic_delay
from modules.communication.livechat.livechat import LiveChatListener
from utils.oauth_manager import get_authenticated_service, get_authenticated_service_with_fallback, start_credential_cooldown, Credentials
from utils.env_loader import get_env_variable
from modules.ai_intelligence.banter_engine.banter_engine import BanterEngine
from googleapiclient.errors import HttpError

def mask_sensitive_id(id_str: str) -> str:
    """Mask sensitive IDs in logs."""
    if not id_str:
        return "None"
    return f"{id_str[:4]}...{id_str[-4:]}"

async def find_active_livestream(service, channel_id, max_attempts=None):
    """Continuously search for active livestream with throttling."""
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
    """Main entry point for the application."""
    logger = logging.getLogger(__name__)
    
    try:
        # Get channel ID from environment
        channel_id = get_env_variable("CHANNEL_ID")
        if not channel_id:
            logger.error("CHANNEL_ID not found in environment variables")
            return
            
        # --- Authentication with Mocking Option ---
        auth_result = None
        mock_enabled = os.getenv('FOUNDUPS_OAUTH_MOCK_ENABLED') == 'true'
        
        if mock_enabled:
            logger.warning("--- OAuth Mocking Enabled --- FOUNDUPS_OAUTH_MOCK_ENABLED=true")
            # Create mock objects to simulate successful authentication
            mock_service = MagicMock()
            
            # Configure the mock service for find_active_livestream
            search_mock = MagicMock()
            search_list_mock = MagicMock()
            search_list_mock.list.return_value.execute.return_value = {"items": [{"id": {"videoId": "dummy_video_id"}, "snippet": {"title": "Mocked Livestream"}}]}
            mock_service.search.return_value = search_list_mock
            
            # Configure the mock service for check_video_details AND viewer count updates
            videos_mock = MagicMock()
            videos_list_mock = MagicMock()
            
            # Create a function to return different responses based on the 'part' parameter
            def mock_videos_response(*args, **kwargs):
                part = kwargs.get('part', '')
                if 'statistics' in part:
                    # Response for _update_viewer_count calls
                    return MagicMock(execute=MagicMock(return_value={
                        "items": [{
                            "statistics": {
                                "viewCount": "100"
                            }
                        }]
                    }))
                else:
                    # Response for check_video_details calls (liveStreamingDetails)
                    return MagicMock(execute=MagicMock(return_value={
                        "items": [{
                            "liveStreamingDetails": {
                                "activeLiveChatId": "dummy_chat_id"
                            }
                        }]
                    }))
            
            videos_list_mock.list.side_effect = mock_videos_response
            mock_service.videos.return_value = videos_list_mock
            
            # Configure mock for liveChatMessages (used in _poll_chat_messages)
            livechat_mock = MagicMock()
            livechat_list_mock = MagicMock()
            livechat_list_mock.list.return_value.execute.return_value = {
                "pollingIntervalMillis": 10000,
                "nextPageToken": "dummy_next_token",
                "items": []
            }
            mock_service.liveChatMessages.return_value = livechat_list_mock
            
            # Configure mock for channels (used in _get_bot_channel_id)
            channels_mock = MagicMock()
            channels_list_mock = MagicMock()
            channels_list_mock.list.return_value.execute.return_value = {
                "items": [{
                    "id": "dummy_bot_channel_id"
                }]
            }
            mock_service.channels.return_value = channels_list_mock
            
            # Mock credentials
            mock_credentials = MagicMock(spec=Credentials)
            mock_credential_set = 'mock_set_1'
            
            # Add _developerKey to match real service
            mock_service._developerKey = "dummy_developer_key"
            
            auth_result = (mock_service, mock_credentials, mock_credential_set)
            logger.info(f"Using MOCKED authentication result with credential set: {mock_credential_set}")
        else:
            # Get authenticated service with fallback first (Real Path)
            logger.info("Attempting real authentication...")
            auth_result = get_authenticated_service_with_fallback()

        # Check if authentication (real or mocked) succeeded
        if not auth_result:
            logger.error("Failed to get authenticated YouTube service (real or mocked)")
            return
            
        service, current_credentials, current_credential_set = auth_result
        # Log success, indicating if it was mocked
        auth_type = "MOCKED" if mock_enabled else "REAL"
        logger.info(f"Initial {auth_type} authentication successful with {current_credential_set}")
        # --- End Authentication Block ---
        
        # Continuously look for active livestream
        while True:
            try:
                video_id, chat_id = await find_active_livestream(service, channel_id)
                
                if video_id and chat_id:
                    # Initialize chat listener
                    listener = LiveChatListener(service, video_id, chat_id)
                    
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
