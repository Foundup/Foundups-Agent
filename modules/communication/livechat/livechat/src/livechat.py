import logging
import os
import time
from datetime import datetime
import googleapiclient.errors
from dotenv import load_dotenv
from utils.throttling import calculate_dynamic_delay
from modules.infrastructure.token_manager.token_manager import token_manager
from modules.ai_intelligence.banter_engine.banter_engine import BanterEngine
from utils.oauth_manager import get_authenticated_service
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from utils.env_loader import get_env_variable
from modules.communication.livechat.livechat.src.llm_bypass_engine import LLMBypassEngine
from modules.ai_intelligence.banter_engine.banter_engine.src.emoji_sequence_map import EMOJI_TO_NUM

logger = logging.getLogger(__name__)

class LiveChatListener:
    """
    Connects to a YouTube livestream chat, listens for messages,
    logs them, and provides hooks for sending messages and AI interaction.
    """
    def __init__(self, youtube_service, video_id, live_chat_id=None):
        self.youtube = youtube_service
        self.video_id = video_id
        self.live_chat_id = live_chat_id
        self.next_page_token = None
        self.poll_interval_ms = 100000  # Default: 100 seconds
        self.error_backoff_seconds = 5  # Initial backoff for errors
        self.memory_dir = "memory"
        self.greeting_message = os.getenv("AGENT_GREETING_MESSAGE", "FoundUps Agent reporting in!")
        self.message_queue = []  # Queue for storing messages
        self.viewer_count = 0  # Track current viewer count
        self.banter_engine = BanterEngine()  # Initialize banter engine
        self.llm_bypass_engine = LLMBypassEngine()  # Fallback engine for when main engine fails
        self.trigger_emojis = ["✊", "✋", "🖐️"]  # Configurable emoji trigger set
        self.last_trigger_time = {}  # Track last trigger time per user
        self.trigger_cooldown = 60  # Cooldown period in seconds
        self.is_running = False  # Flag to control the listening loop

        os.makedirs(self.memory_dir, exist_ok=True)
        logger.info(f"Memory directory set to: {self.memory_dir}")

    async def _handle_auth_error(self, error):
        """Handle authentication errors by attempting token rotation."""
        if isinstance(error, googleapiclient.errors.HttpError):
            if error.resp.status in [401, 403]:  # Authentication errors
                logger.warning("Authentication error detected, attempting token rotation")
                new_token_index = await token_manager.rotate_tokens()
                if new_token_index is not None:
                    logger.info(f"Successfully rotated to token set_{new_token_index + 1}")
                    # Re-authenticate with the new token
                    try:
                        self.youtube = get_authenticated_service(new_token_index)
                        logger.info("Re-authenticated with new token.")
                        return True # Indicate success, caller should retry the API call
                    except Exception as auth_e:
                        logger.error(f"Failed to re-authenticate after token rotation: {auth_e}")
                        return False # Indicate failure
                else:
                    logger.error("Token rotation failed, unable to recover.")
                    return False # Indicate failure
        return False # Error not handled

    def _get_live_chat_id(self):
        """Retrieves the liveChatId for the specified video_id."""
        try:
            logger.info(f"Fetching livestream details for video ID: {self.video_id}")
            response = self.youtube.videos().list(
                part="liveStreamingDetails",
                id=self.video_id
            ).execute()

            items = response.get("items", [])
            if not items:
                logger.error(f"Video not found: {self.video_id}")
                raise ValueError(f"Video not found: {self.video_id}")

            live_streaming_details = items[0].get("liveStreamingDetails", {})
            if not live_streaming_details:
                logger.error(f"No active live chat for video: {self.video_id}")
                raise ValueError(f"No active live chat for video: {self.video_id}")

            chat_id = live_streaming_details.get("activeLiveChatId")
            if not chat_id:
                logger.error(f"No active live chat for video: {self.video_id}")
                raise ValueError(f"No active live chat for video: {self.video_id}")
                
            self.live_chat_id = chat_id
            logger.info(f"Retrieved live chat ID: {chat_id}")
            return chat_id
            
        except googleapiclient.errors.HttpError as e:
            logger.error(f"HTTP error getting live chat ID: {e}")
            raise
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting live chat ID: {e}")
            raise ValueError(f"Failed to get live chat ID: {e}")

    def _update_viewer_count(self):
        """Update viewer count from livestream statistics."""
        try:
            response = self.youtube.videos().list(
                part="statistics",
                id=self.video_id
            ).execute()
            
            items = response.get("items", [])
            if items:
                # Handle both real and mock responses
                statistics = items[0].get("statistics", {})
                if hasattr(statistics, 'get'):  # Real response
                    view_count_str = statistics.get("viewCount", "0")
                    self.viewer_count = int(view_count_str)
                else:  # Mock response - use a default value
                    self.viewer_count = 100  # Default viewer count for mocking
                logger.debug(f"Updated viewer count: {self.viewer_count}")
            else:
                self.viewer_count = 0  # No items found
        except Exception as e:
            logger.error(f"Failed to update viewer count: {e}")
            self.viewer_count = 100  # Fallback viewer count

    async def _poll_chat_messages(self):
        """Polls the YouTube API for new chat messages."""
        try:
            response = self.youtube.liveChatMessages().list(
                liveChatId=self.live_chat_id,
                part="snippet,authorDetails",
                pageToken=self.next_page_token
            ).execute()

            # Get the polling interval from YouTube's response (handle mock objects)
            server_poll_interval = response.get("pollingIntervalMillis", 10000)
            if not isinstance(server_poll_interval, int):
                # In mock mode, use a safe default
                server_poll_interval = 10000
            
            # Calculate dynamic delay based on viewer count (handle mock objects)
            try:
                if isinstance(self.viewer_count, int):
                    dynamic_delay = calculate_dynamic_delay(self.viewer_count)
                else:
                    # In mock mode or if viewer_count is not an int, use a safe default
                    dynamic_delay = 10.0  # Default 10 second delay
            except Exception:
                dynamic_delay = 10.0  # Fallback delay
            
            # Use the larger of server's interval or our calculated interval
            self.poll_interval_ms = max(server_poll_interval, int(dynamic_delay * 1000))
            
            self.next_page_token = response.get("nextPageToken")
            self.error_backoff_seconds = 5  # Reset error backoff on success

            messages = response.get("items", [])
            if messages:
                logger.debug(f"Received {len(messages)} new messages.")
                return messages
            else:
                logger.debug("No new messages.")
                return []
            
        except googleapiclient.errors.HttpError as e:
            logger.error(f"API Error polling messages: {e}")
            if await self._handle_auth_error(e):
                logger.info("Auth error handled, polling might recover.")
                return []
            else:
                raise
        except Exception as e:
            logger.error(f"Unexpected error polling chat: {e}")
            time.sleep(self.error_backoff_seconds)
            self.error_backoff_seconds = min(self.error_backoff_seconds * 2, 60)
            return []

    def _is_rate_limited(self, user_id):
        """
        Check if a user is rate limited from triggering gestures.
        
        Args:
            user_id (str): The user's ID
            
        Returns:
            bool: True if user is rate limited, False otherwise
        """
        current_time = time.time()
        if user_id in self.last_trigger_time:
            time_since_last = current_time - self.last_trigger_time[user_id]
            if time_since_last < self.trigger_cooldown:
                logger.debug(f"Rate limited user {user_id} for {self.trigger_cooldown - time_since_last:.1f}s")
            return True
        return False

    def _update_trigger_time(self, user_id):
        """Update the last trigger time for a user."""
        self.last_trigger_time[user_id] = time.time()

    def _extract_message_metadata(self, message):
        """
        Extract key metadata from a chat message.
        
        Args:
            message (dict): The YouTube chat message object
            
        Returns:
            tuple: (msg_id, display_message, author_name, author_id)
            
        Raises:
            KeyError: If required message fields are missing
        """
        msg_id = message["id"]
        snippet = message["snippet"]
        author_details = message["authorDetails"]
        
        author_id = author_details.get("channelId", "unknown")
        display_message = snippet.get("displayMessage", "")
        author_name = author_details["displayName"]
        
        logger.debug(f"Chat message received: {display_message}")
        logger.debug(f"Message length: {len(display_message)}")
        
        return msg_id, display_message, author_name, author_id
    
    def _check_trigger_patterns(self, message_text):
        """
        Check if a message contains any trigger patterns.
        
        Args:
            message_text (str): The message text to check
            
        Returns:
            bool: True if a trigger pattern was found, False otherwise
        """
        # Count emojis properly, handling multi-character emojis
        emoji_count = 0
        i = 0
        while i < len(message_text):
            # Check for multi-character emoji first (🖐️)
            if i + 1 < len(message_text):
                two_char = message_text[i:i+2]
                if two_char in EMOJI_TO_NUM:
                    emoji_count += 1
                    i += 2
                    continue
            
            # Check for single-character emoji
            char = message_text[i]
            if char in EMOJI_TO_NUM:
                emoji_count += 1
            i += 1
        
        return emoji_count >= 3

    async def _handle_emoji_trigger(self, author_name, author_id, message_text):
        """
        Handle a detected emoji trigger sequence.
        
        Args:
            author_name (str): Display name of the message author
            author_id (str): Channel ID of the message author
            message_text (str): The message text containing the trigger
            
        Returns:
            bool: True if the trigger was handled successfully, False otherwise
        """
        logger.info(f"Emoji sequence detected in message from {author_name}: {message_text}")
        
        # Check if this is a self-message (bot responding to its own emoji)
        if hasattr(self, 'bot_channel_id') and self.bot_channel_id and author_id == self.bot_channel_id:
            logger.debug(f"Ignoring self-message from bot {author_name}")
            return False
        
        # Check rate limiting
        if self._is_rate_limited(author_id):
            logger.debug(f"Skipping trigger for rate-limited user {author_name}")
            return False
        
        try:
            # Use banter engine to process the message directly - it handles detection internally
            state_info, response = self.banter_engine.process_input(message_text)
            logger.info(f"Banter engine returned state: {state_info}, response: {response}")
            
            if not response or not isinstance(response, str) or not response.strip():
                logger.warning(f"Empty or invalid banter response for {author_name}, trying LLM bypass")
                # Try LLM bypass engine as fallback
                try:
                    bypass_state, bypass_response = self.llm_bypass_engine.process_input(message_text)
                    if bypass_response and isinstance(bypass_response, str) and bypass_response.strip():
                        logger.info(f"LLM bypass provided response: {bypass_response}")
                        response = bypass_response
                    else:
                        logger.warning(f"LLM bypass also failed, using final fallback")
                        response = self.llm_bypass_engine.get_fallback_response(author_name)
                except Exception as bypass_error:
                    logger.error(f"LLM bypass engine failed: {bypass_error}")
                    response = f"Hey {author_name}! Thanks for the gesture! 👋"
            
            logger.debug(f"Generated banter response for {author_name}: {response}")
            
            # Send response
            if await self.send_chat_message(response):
                logger.info(f"Successfully queued banter response for {author_name}")
                self._update_trigger_time(author_id)
                return True
            else:
                logger.error(f"Failed to queue banter response for {author_name}")
                return False
        except Exception as e:
            logger.error(f"Error processing emoji trigger for {author_name}: {str(e)}")
            return False

    async def _get_bot_channel_id(self):
        """
        Get the channel ID of the bot to prevent responding to its own messages.
        
        Returns:
            str: The bot's channel ID, or None if unable to retrieve
        """
        try:
            request = self.youtube.channels().list(part='id', mine=True)
            response = request.execute()
            items = response.get('items', [])
            if items:
                bot_channel_id = items[0]['id']
                logger.info(f"Bot channel ID identified: {bot_channel_id}")
                return bot_channel_id
        except Exception as e:
            logger.warning(f"Could not get bot channel ID: {e}")
        return None

    def _create_log_entry(self, msg_id, author_name, display_message):
        """
        Create a standardized log entry from message data.
        
        Args:
            msg_id (str): Message identifier
            author_name (str): Display name of the author
            display_message (str): Message content
            
        Returns:
            dict: Log entry with standardized fields
        """
        return {
            "id": msg_id,
            "author": author_name,
            "message": display_message,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _process_message(self, message):
        """
        Process a single chat message and handle triggers.
        
        Args:
            message (dict): YouTube chat message object
                    
        Returns:
            dict: Processed log entry containing message details
            
        Notes:
            Returns None if an error occurs or if the message contains a trigger
            that was rate-limited
        """
        try:
            # Extract message metadata
            msg_id, display_message, author_name, author_id = self._extract_message_metadata(message)
            
            # Check for trigger patterns
            if self._check_trigger_patterns(display_message):
                # Handle emoji trigger
                trigger_success = await self._handle_emoji_trigger(author_name, author_id, display_message)
                if not trigger_success and self._is_rate_limited(author_id):
                    # If handling failed due to rate limiting, return None
                    return None
            
            # Create log entry
            log_entry = self._create_log_entry(msg_id, author_name, display_message)
            
            # Log the message
            try:
                self._log_to_user_file(message)
            except Exception as log_e:
                # Log but don't fail the whole processing if logging fails
                logger.error(f"Failed to log message: {log_e}")
            
            return log_entry
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            # Return a minimal log entry with error information rather than raising
            # This prevents a single bad message from breaking batch processing
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _log_to_user_file(self, message):
        """Appends a log entry to a user-specific file."""
        try:
            username = message["authorDetails"]["displayName"]
            log_dir = os.path.join(self.memory_dir, "chat_logs").replace("\\", "/")
            os.makedirs(log_dir, exist_ok=True)
            
            log_filename = os.path.join(log_dir, f"{username}.jsonl").replace("\\", "/")
            with open(log_filename, "a", encoding="utf-8") as f:
                import json
                f.write(json.dumps(message) + "\n")
            logger.debug(f"Logged message from {username}")
        except Exception as e:
            logger.error(f"Failed to write to log file: {e}")
            raise

    async def send_chat_message(self, message_text):
        """Sends a text message to the live chat."""
        if not self.live_chat_id:
            logger.error("Cannot send message, live_chat_id is not set.")
            return False

        logger.debug(f"Preparing to send message to chat ID: {self.live_chat_id}")
        max_len = 200
        if len(message_text) > max_len - 3:  # Leave room for '...'
            logger.warning(f"Message too long ({len(message_text)} chars), truncating to {max_len}.")
            message_text = message_text[:max_len-3] + "..."

        try:
            logger.debug("Constructing API request...")
            request = self.youtube.liveChatMessages().insert(
                part="snippet",
                body={
                    "snippet": {
                        "liveChatId": self.live_chat_id,
                        "type": "textMessageEvent",
                        "textMessageDetails": {
                            "messageText": message_text
                        }
                    }
                }
            )
            logger.debug("Executing API request...")
            response = request.execute()
            logger.info(f"Message sent successfully to chat ID: {self.live_chat_id}")
            return True
        except googleapiclient.errors.HttpError as e:
            logger.error(f"Failed to send message: {e}")
            if await self._handle_auth_error(e):
                logger.info("Auth error handled during send, retrying might work if implemented.")
                # Consider implementing a retry mechanism here if needed
                return False # Indicate failure for this attempt
            else:
                return False # Unhandled error or rotation failed
        except Exception as e:
            logger.error(f"Unexpected error sending message: {e}")
            return False

    async def _initialize_chat_session(self) -> bool:
        """
        Initialize the chat session by validating or obtaining the chat ID.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        if not self.live_chat_id:
            logger.info("No live_chat_id provided, attempting to fetch it...")
            try:
                self.live_chat_id = self._get_live_chat_id()
                if not self.live_chat_id:
                    logger.error(f"Could not find active live chat for video {self.video_id}. Exiting listener.")
                    return False
            except Exception as e:
                logger.error(f"Failed to fetch live chat ID: {e}")
                return False
        else:
            logger.info(f"Using provided live chat ID: {self.live_chat_id}")
        
        logger.info(f"Successfully connected to chat ID: {self.live_chat_id}")
        return True
        
    async def _send_greeting_message(self) -> None:
        """Send a greeting message to the chat if configured."""
        if not self.greeting_message:
            logger.warning("No greeting message configured")
            return
                
        logger.info(f"Attempting to send greeting message: {self.greeting_message}")
        try:
            if await self.send_chat_message(self.greeting_message):
                logger.info("Greeting message sent successfully")
            else:
                logger.error("Failed to send greeting message - send_chat_message returned False")
        except Exception as e:
            logger.error(f"Exception while sending greeting message: {e}")
        
        # Brief pause after greeting (using asyncio.sleep to avoid blocking)
        await asyncio.sleep(2)
        
    async def _poll_chat_cycle(self) -> bool:
        """
        Execute a single polling cycle (update viewers, poll messages, process messages).
        
        Returns:
            bool: True if a critical failure occurred, False otherwise
        """
        # Update viewer count and adjust polling interval
        self._update_viewer_count()
        
        # Poll for new messages
        messages = await self._poll_chat_messages()
        if messages is None:  # None indicates critical failure
            logger.error("Polling failed critically. Stopping listener.")
            return True
        
        # Process received messages
        if messages:
            await self._process_message_batch(messages)
        
        return False
        
    async def _process_message_batch(self, messages) -> None:
        """
        Process a batch of messages with proper error handling.
        
        Args:
            messages: List of messages to process
        """
        for message in messages:
            try:
                await self._process_message(message)
            except Exception as processing_e:
                logger.error(f"Error during message processing: {processing_e}")
        
    async def start_listening(self):
        """Starts the chat listener loop."""
        if not self.is_running:
            logger.info("Attempting to start live chat listener...")
            
            try:
                # Initialize chat session
                if not await self._initialize_chat_session():
                    return

                # Get bot channel ID for self-response prevention
                self.bot_channel_id = await self._get_bot_channel_id()
                
                # Send greeting message
                await self._send_greeting_message()
                
                # Start polling loop
                logger.info("Starting chat polling loop...")
                self.is_running = True
                
                while self.is_running:
                    # Execute one polling cycle
                    critical_failure = await self._poll_chat_cycle()
                    if critical_failure:
                        break
                    
                    # Sleep until next poll
                    sleep_time_seconds = self.poll_interval_ms / 1000.0
                    logger.debug(f"Current viewer count: {self.viewer_count}, Waiting {sleep_time_seconds:.2f}s before next poll")
                    await asyncio.sleep(sleep_time_seconds)
                    
            except Exception as e:
                logger.error(f"Critical error in chat listener: {str(e)}")
                raise
            
            logger.info("Chat listener stopped.")
            
    def stop_listening(self):
        """Stops the chat listener loop by setting is_running to False."""
        logger.info("Stopping live chat listener...")
        self.is_running = False

    def calculate_wait_time(self, quota_usage):
        """Calculate wait time based on quota usage."""
        if not quota_usage:
            return 0
        
        # Base calculation on user limit vs current usage
        if self.user_rate_limit is not None:
            if quota_usage < self.user_rate_limit:
                return 0
            
            # If over limit, wait proportionally to how far over
            overage = quota_usage - self.user_rate_limit
            return max(5, overage // 5)
        
        return 0



