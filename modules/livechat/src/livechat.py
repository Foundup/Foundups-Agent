import logging
import os
import time
from datetime import datetime
import googleapiclient.errors
from dotenv import load_dotenv
import asyncio
from typing import Optional, Dict, Any
from googleapiclient.discovery import Resource
from modules.banter_engine.src.banter_engine import BanterEngine
from modules.stream_resolver.src.stream_resolver import check_video_details
from utils.env_loader import get_env_variable
import json

# Add project root to Python path for imports
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from utils.throttling import calculate_dynamic_delay
from modules.token_manager import token_manager
from utils.oauth_manager import get_authenticated_service

# Configure logging
logger = logging.getLogger(__name__)

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

# Load environment variables
AGENT_GREETING_MESSAGE = get_env_variable("AGENT_GREETING_MESSAGE")
LOG_LEVEL = get_env_variable("LOG_LEVEL", default="INFO")

# Constants
MAX_MESSAGE_LENGTH = 200
ERROR_BACKOFF_SECONDS = 5

class DelayTuner:
    """Tune polling delay based on message activity."""
    def __init__(self, initial_delay=5, min_delay=1, max_delay=60):
        self.delay = initial_delay
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.zero_streak = 0
        self.valid_streak = 0

    def update(self, message):
        """Update delay based on message activity."""
        if message == "0":
            self.zero_streak += 1
            self.valid_streak = 0
            if self.zero_streak == 5:
                self.delay = min(self.delay + 1, self.max_delay)
                self.zero_streak = 0
        else:
            self.valid_streak += 1
            self.zero_streak = 0
            if self.valid_streak == 5:
                self.delay = max(self.delay - 1, self.min_delay)
                self.valid_streak = 0

    def get_delay(self):
        """Get current delay value."""
        return self.delay

class LiveChatListener:
    """
    Connects to a YouTube livestream chat, listens for messages,
    logs them, and provides hooks for sending messages and AI interaction.
    """
    def __init__(self, youtube_service, video_id, live_chat_id=None, banter_engine=None):
        self.youtube = youtube_service
        self.video_id = video_id
        self.live_chat_id = live_chat_id
        self.next_page_token = None
        self.poll_interval_ms = 100000  # Default: 100 seconds
        self.error_backoff_seconds = 5  # Initial backoff for errors
        self.memory_dir = "memory"
        self.greeting_message = AGENT_GREETING_MESSAGE
        self.message_queue = []  # Queue for storing messages
        self.viewer_count = 0  # Track current viewer count
        self.banter_engine = banter_engine
        self.last_trigger_time = {}  # Track last trigger time per user
        self.trigger_cooldown = 60  # Cooldown period in seconds
        self.greeting_sent = False  # Track if greeting has been sent
        self.delay_tuner = DelayTuner()  # Initialize delay tuner
        self.last_banter_time = 0  # Track last banter reply time
        self.banter_cooldown = 10  # seconds between allowed banter replies
        self.bot_name = "Foundups Agent"  # Bot's display name
        self.logger = logging.getLogger(__name__)  # Initialize logger

        os.makedirs(self.memory_dir, exist_ok=True)
        self.logger.info(f"Memory directory set to: {self.memory_dir}")

    async def _handle_auth_error(self, error):
        """Handle authentication errors by attempting token rotation."""
        if isinstance(error, googleapiclient.errors.HttpError):
            if error.resp.status in [401, 403]:  # Authentication errors
                logger.warning("Authentication error detected, attempting token rotation")
                try:
                    new_token_index = await token_manager.rotate_tokens()
                    if new_token_index is not None:
                        logger.info(f"Successfully rotated to token set_{new_token_index + 1}")
                        # Reinitialize service with new token
                        self.youtube = get_authenticated_service(new_token_index)
                        return True
                    else:
                        logger.error("Token rotation failed")
                        return False
                except Exception as e:
                    logger.error(f"Error during token rotation: {e}")
                    return False
        return False

    def _get_live_chat_id(self):
        """Get the live chat ID for the current video."""
        try:
            request = self.youtube.videos().list(
                part="liveStreamingDetails",
                id=self.video_id
            )
            response = request.execute()
            
            if not response.get('items'):
                logger.error(f"No video found with ID: {self.video_id}")
                return None
                
            live_details = response['items'][0].get('liveStreamingDetails', {})
            chat_id = live_details.get('activeLiveChatId')
            
            if not chat_id:
                logger.warning(f"No active chat found for video: {self.video_id}")
                return None
                
            logger.info(f"Found live chat ID: {chat_id}")
            self.live_chat_id = chat_id  # Assign the chat ID to the instance
            return chat_id
            
        except googleapiclient.errors.HttpError as e:
            logger.error(f"Error getting live chat ID: {str(e)}")
            return None

    def _update_viewer_count(self):
        """Update the current viewer count from the video."""
        try:
            request = self.youtube.videos().list(
                part="liveStreamingDetails",
                id=self.video_id
            )
            response = request.execute()
            
            if response.get('items'):
                live_details = response['items'][0].get('liveStreamingDetails', {})
                self.viewer_count = int(live_details.get('concurrentViewers', 0))
                logger.debug(f"Updated viewer count: {self.viewer_count}")
                
        except Exception as e:
            logger.error(f"Error updating viewer count: {str(e)}")

    async def _poll_chat_messages(self):
        """Poll for new chat messages."""
        logger.info("🔍 Starting _poll_chat_messages()")
        try:
            if not self.live_chat_id:
                logger.info("⚠️ No live_chat_id, attempting to get it")
                self.live_chat_id = self._get_live_chat_id()
                if not self.live_chat_id:
                    logger.error("❌ No live chat ID available")
                    return []

            logger.info(f"📡 Polling chat with ID: {mask_sensitive_id(self.live_chat_id, 'chat')}")
            request = self.youtube.liveChatMessages().list(
                liveChatId=self.live_chat_id,
                part="snippet,authorDetails",
                maxResults=2000,
                pageToken=self.next_page_token
            )
            
            logger.debug("🔄 Executing chat messages request")
            response = request.execute()
            messages = response.get('items', [])
            logger.info(f"📥 Received {len(messages)} messages")
            
            self.next_page_token = response.get('nextPageToken')
            
            # Process messages
            for message in messages:
                message_text = message.get('snippet', {}).get('displayMessage', '')
                author_name = message.get('authorDetails', {}).get('displayName', '')
                
                # Skip messages sent by the bot itself
                if author_name == self.bot_name:
                    logger.debug(f"⏭️ Skipping bot's own message: {message_text}")
                    continue
                
                logger.debug(f"📝 Processing message from {author_name}: {message_text}")
                await self._process_message(message)
                
            return messages
            
        except googleapiclient.errors.HttpError as e:
            logger.error(f"❌ HTTP Error in _poll_chat_messages: {str(e)}")
            if not await self._handle_auth_error(e):
                logger.error(f"❌ Error polling chat messages: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"❌ Unexpected error in _poll_chat_messages: {str(e)}")
            return []

    def _is_rate_limited(self, user_id):
        """Check if a user is rate limited based on their last trigger time."""
        if user_id not in self.last_trigger_time:
            return False
            
        last_time = self.last_trigger_time[user_id]
        current_time = time.time()
        
        if current_time - last_time < self.trigger_cooldown:
            self.logger.debug(f"User {user_id} is rate limited")
            return True
            
        return False

    def _update_trigger_time(self, user_id):
        """Update the last trigger time for a user."""
        self.last_trigger_time[user_id] = time.time()

    async def _process_message(self, message):
        """Process a single chat message."""
        try:
            if self.should_ignore(message):
                return

            # Extract message text
            message_text = message.get('snippet', {}).get('displayMessage', '')
            
            # Process message with BanterEngine if available
            if self.banter_engine and message_text:
                result, response = self.banter_engine.process_input(message_text)
                self.logger.info(f"BanterEngine processed '{message_text}': {result}")
                
                # If we got a valid response, send it
                if response:
                    author = message.get('authorDetails', {})
                    user_id = author.get('channelId', '')
                    
                    # Check rate limiting
                    if not self._is_rate_limited(user_id):
                        if await self.send_chat_message(response):
                            self.logger.info(f"✅ Successfully sent banter response: {response}")
                            self._update_trigger_time(user_id)
                        else:
                            self.logger.error("❌ Failed to send banter response")
                    else:
                        self.logger.debug(f"⏳ User {user_id} is rate limited")

            # Extract message details
            snippet = message.get('snippet', {})
            author = message.get('authorDetails', {})
            user_id = author.get('channelId', '')
            
            self.logger.debug(f"🔍 Processing message from {user_id}: {message_text}")
            
            # Log message to user file
            self._log_to_user_file(message)
            
            # Send greeting if not sent yet
            if self.greeting_message and not self.greeting_sent:
                self.logger.info("🚀 Sending initial greeting message...")
                if await self.send_chat_message(self.greeting_message):
                    self.greeting_sent = True
                    self.logger.info("Greeting message sent successfully")
                else:
                    self.logger.error("Failed to send greeting message")
                        
        except Exception as e:
            self.logger.error(f"❌ Error processing message: {str(e)}")

    def _check_emoji_trigger(self, message):
        """Check if a message contains the trigger emoji sequence."""
        try:
            message_text = message.get('snippet', {}).get('displayMessage', '')
            self.logger.debug(f"🔍 Checking for emojis {self.trigger_emojis} in message: {message_text}")
            
            # Log each emoji's presence
            for emoji in self.trigger_emojis:
                if emoji in message_text:
                    self.logger.debug(f"✅ Found emoji {emoji} in message")
                else:
                    self.logger.debug(f"❌ Emoji {emoji} not found in message")
            
            has_trigger = all(emoji in message_text for emoji in self.trigger_emojis)
            self.logger.debug(f"🎯 Emoji trigger check result: {has_trigger}")
            return has_trigger
        except Exception as e:
            self.logger.error(f"❌ Error checking emoji trigger: {str(e)}")
            return False

    def normalize_username(self, raw_name):
        """Normalize username for file paths."""
        # Lowercase, remove underscores, strip spaces
        return raw_name.lower().replace("_", " ").strip()

    def is_youtube_json(self, message):
        """Check if message is a raw YouTube JSON dump."""
        return '"kind": "youtube#liveChatMessage"' in str(message)

    def should_ignore(self, message):
        """Check if message should be ignored (e.g., system messages)."""
        return '"kind": "youtube#liveChatMessage"' in str(message)

    def _log_to_user_file(self, message):
        """Log chat message to user-specific file."""
        try:
            # Block raw YouTube JSON messages
            if self.is_youtube_json(message):
                self.logger.debug("⏭️ Skipping raw YouTube JSON message")
                return

            # Extract user details
            author = message.get('authorDetails', {})
            user = author.get('displayName', 'unknown')
            
            # Normalize username for file path
            normalized_user = self.normalize_username(user)
            self.logger.debug(f"👤 Normalized username: {user} -> {normalized_user}")
            
            # Create user directory if it doesn't exist
            user_dir = os.path.join(self.memory_dir, normalized_user)
            os.makedirs(user_dir, exist_ok=True)
            self.logger.debug(f"📁 Ensured user directory exists: {user_dir}")
            
            # Write message to file
            filepath = os.path.join(user_dir, "chat_history.txt")
            with open(filepath, "a", encoding="utf-8") as f:
                json.dump(message, f)
                f.write("\n")
            self.logger.debug(f"📝 Logged message from {user} to {filepath}")
            
        except Exception as e:
            self.logger.error(f"❌ Error logging to user file: {str(e)}")
            # Don't raise the exception - logging errors shouldn't break the chat

    def _truncate_message(self, message, max_length=200):
        """Truncate a message to fit YouTube's length limit."""
        if len(message) <= max_length - 3:  # Account for "..."
            return message
        return message[:max_length-3] + "..."

    async def send_chat_message(self, message):
        """Send a message to the live chat."""
        try:
            if not self.live_chat_id:
                self.logger.error("No live chat ID available")
                return False

            # Truncate message if needed
            truncated_message = self._truncate_message(message)
            self.logger.debug(f"Attempting to send message: {truncated_message}")
            
            request = self.youtube.liveChatMessages().insert(
                part="snippet",
                body={
                    "snippet": {
                        "liveChatId": self.live_chat_id,
                        "type": "textMessageEvent",
                        "textMessageDetails": {
                            "messageText": truncated_message
                        }
                    }
                }
            )
            
            # Wrap synchronous API call in asyncio.to_thread
            response = await asyncio.to_thread(request.execute)
            self.logger.info(f"Successfully sent message: {truncated_message}")
            return True
            
        except googleapiclient.errors.HttpError as e:
            if not await self._handle_auth_error(e):
                self.logger.error(f"Failed to send message: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error sending message: {str(e)}")
            return False

    async def start_listening(self):
        """Start listening to the live chat."""
        self.logger.info("🚀 Starting chat listener")
        try:
            self.logger.info(f"📺 Initializing for video ID: {mask_sensitive_id(self.video_id, 'video')}")
            
            # Get live chat ID if not already set
            if not self.live_chat_id:
                self.logger.info("🔍 No live_chat_id, checking video details")
                video_details = check_video_details(self.youtube, self.video_id)
                if video_details and "liveStreamingDetails" in video_details:
                    self.live_chat_id = video_details["liveStreamingDetails"].get("activeLiveChatId")
                    if self.live_chat_id:
                        self.logger.info(f"✅ Found live chat ID: {mask_sensitive_id(self.live_chat_id, 'chat')}")
                        # Send greeting only after we have confirmed live_chat_id and haven't sent it yet
                        if self.greeting_message and not self.greeting_sent:
                            self.logger.info("🚀 Sending initial greeting message...")
                            if await self.send_chat_message(self.greeting_message):
                                self.greeting_sent = True
                                self.logger.info("✅ Greeting message sent successfully")
                            else:
                                self.logger.error("❌ Failed to send greeting message")
                    else:
                        self.logger.error("❌ No active live chat ID found")
                        return
                else:
                    self.logger.error("❌ Could not get video details")
                    return
            
            # Start polling for messages
            self.logger.info("🔄 Starting chat message polling loop")
            while True:
                try:
                    self.logger.debug("🔄 Polling for new messages...")
                    messages = await self._poll_chat_messages()
                    
                    # Update delay based on message count
                    message_count = len(messages)
                    self.delay_tuner.update(str(message_count))
                    current_delay = self.delay_tuner.get_delay()
                    
                    self.logger.debug(f"⏳ Waiting {current_delay}s before next poll (messages: {message_count})")
                    await asyncio.sleep(current_delay)
                    
                except googleapiclient.errors.HttpError as e:
                    if e.resp.status == 403 and "quotaExceeded" in str(e):
                        self.logger.warning("⚠️ Quota exceeded, waiting before retry...")
                        await asyncio.sleep(30)
                    else:
                        self.logger.error(f"❌ Error polling chat: {e}")
                        await asyncio.sleep(5)
                except Exception as e:
                    self.logger.error(f"❌ Error in chat polling loop: {e}")
                    await asyncio.sleep(5)
                    
        except Exception as e:
            self.logger.error(f"❌ Error starting chat listener: {e}")
            raise 