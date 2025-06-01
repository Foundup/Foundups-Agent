import logging
import os
import time
from datetime import datetime
import googleapiclient.errors
from dotenv import load_dotenv
from utils.throttling import calculate_dynamic_delay
from modules.infrastructure.token_manager.token_manager.src.token_manager import token_manager
from modules.ai_intelligence.banter_engine.src.banter_engine import BanterEngine
from modules.infrastructure.oauth_management.oauth_management.src.oauth_manager import get_authenticated_service_with_fallback, start_credential_cooldown
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from utils.env_loader import get_env_variable
from modules.communication.livechat.livechat.src.llm_bypass_engine import LLMBypassEngine
from modules.ai_intelligence.banter_engine.emoji_sequence_map import EMOJI_TO_NUMBER as EMOJI_TO_NUM
from modules.communication.livechat.livechat.src.auto_moderator import AutoModerator
import random

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
        self.poll_interval_ms = 5000  # Default: 5 seconds for faster response
        self.error_backoff_seconds = 5  # Initial backoff for errors
        self.memory_dir = "memory"
        self.greeting_message = os.getenv("AGENT_GREETING_MESSAGE", "FoundUps Agent reporting in!")
        self.message_queue = []  # Queue for storing messages
        self.viewer_count = 0  # Track current viewer count
        self.banter_engine = BanterEngine()  # Initialize banter engine
        self.llm_bypass_engine = LLMBypassEngine()  # Fallback engine for when main engine fails
        self.auto_moderator = AutoModerator(youtube_service)  # Initialize auto-moderation
        self.trigger_emojis = ["✊", "✋", "🖐️"]  # Configurable emoji trigger set
        self.last_trigger_time = {}  # Track last trigger time per user
        self.trigger_cooldown = 30  # Cooldown period in seconds (reduced from 60)
        self.last_global_response = 0  # Track last response time globally
        self.global_cooldown = 5  # Minimum 5 seconds between any responses
        self.is_running = False  # Flag to control the listening loop
        self.stream_title = None  # Cache for stream title
        self.stream_title_short = None  # Cache for shortened stream title
        self.processed_message_ids = set()  # Track processed message IDs to prevent duplicates
        self.max_processed_ids = 1000       # Maximum number of processed IDs to keep in memory

        # User rate limiting
        self.user_trigger_times = {}  # user_id -> last_trigger_time
        self.user_cooldown = 30  # 30 seconds cooldown per user
        
        # WSP Enhancement: Random delay configuration for human-like behavior
        self.random_delay_enabled = True
        self.min_random_delay = 0.8  # Minimum random delay (seconds)
        self.max_random_delay = 4.0  # Maximum random delay (seconds)

        os.makedirs(self.memory_dir, exist_ok=True)
        logger.info(f"Memory directory set to: {self.memory_dir}")
        logger.info("🛡️ Auto-moderation system enabled")

    async def _handle_auth_error(self, error):
        """Handle authentication errors by attempting OAuth credential rotation."""
        if isinstance(error, googleapiclient.errors.HttpError):
            if error.resp.status in [401, 403]:  # Authentication errors
                logger.warning("🔄 Authentication error detected, attempting OAuth credential rotation")
                try:
                    # Use the WSP-compliant OAuth management system with fallback
                    auth_result = get_authenticated_service_with_fallback()
                    if auth_result:
                        service, credentials, credential_set = auth_result
                        self.youtube = service
                        # Update auto-moderator with new service
                        self.auto_moderator = AutoModerator(service)
                        logger.info(f"✅ Re-authenticated with {credential_set}")
                        return True # Indicate success, caller should retry the API call
                    else:
                        logger.error("❌ Failed to get authenticated service after credential rotation")
                        return False
                except Exception as auth_e:
                    logger.error(f"❌ Failed to re-authenticate after credential rotation: {auth_e}")
                    return False # Indicate failure
            elif 'quotaExceeded' in str(error):
                logger.warning("⚠️ Quota exceeded detected, triggering credential rotation")
                try:
                    # Trigger cooldown for current credential and try to get new one
                    auth_result = get_authenticated_service_with_fallback()
                    if auth_result:
                        service, credentials, credential_set = auth_result
                        self.youtube = service
                        # Update auto-moderator with new service
                        self.auto_moderator = AutoModerator(service)
                        logger.info(f"✅ Rotated to {credential_set} due to quota exceeded")
                        return True
                    else:
                        logger.error("❌ All credential sets exceeded quota - service unavailable")
                        return False
                except Exception as auth_e:
                    logger.error(f"❌ Failed to rotate credentials after quota exceeded: {auth_e}")
                    return False
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
        """Polls the YouTube API for new chat messages with intelligent throttling."""
        try:
            response = self.youtube.liveChatMessages().list(
                liveChatId=self.live_chat_id,
                part="snippet,authorDetails",
                pageToken=self.next_page_token
            ).execute()

            # Get the polling interval from YouTube's response (handle mock objects)
            server_poll_interval = response.get("pollingIntervalMillis", 5000)
            if not isinstance(server_poll_interval, int):
                # In mock mode, use a safe default
                server_poll_interval = 5000
            
            # Calculate intelligent dynamic delay based on multiple factors
            try:
                if isinstance(self.viewer_count, int):
                    # Base delay calculation with viewer count
                    if self.viewer_count > 1000:  # High activity
                        base_delay = 2.0
                    elif self.viewer_count > 500:  # Medium-high activity
                        base_delay = 3.0
                    elif self.viewer_count > 100:  # Medium activity
                        base_delay = 5.0
                    elif self.viewer_count > 10:  # Low activity
                        base_delay = 8.0
                    else:  # Very low activity
                        base_delay = 10.0
                    
                    # Adjust based on message volume
                    messages = response.get("items", [])
                    message_count = len(messages)
                    
                    if message_count > 10:  # High message volume
                        base_delay *= 0.7  # Reduce delay for high activity
                    elif message_count > 5:  # Medium message volume
                        base_delay *= 0.85
                    elif message_count == 0:  # No messages
                        base_delay *= 1.3  # Increase delay when quiet
                    
                    # Apply server recommendation with bounds
                    server_delay = server_poll_interval / 1000.0
                    dynamic_delay = max(min(base_delay, server_delay * 1.5), 2.0)  # Min 2s, respect server
                    
                    # Cap the delay at 12 seconds max for responsiveness
                    dynamic_delay = min(dynamic_delay, 12.0)
                else:
                    # In mock mode or if viewer_count is not an int, use intelligent default
                    dynamic_delay = 4.0  # Default 4 second delay for faster response
            except Exception:
                dynamic_delay = 4.0  # Fallback delay
            
            # Use the calculated interval, but respect server minimum
            self.poll_interval_ms = max(int(dynamic_delay * 1000), server_poll_interval)
            
            # Log polling strategy for monitoring
            messages = response.get("items", [])
            if messages:
                logger.info(f"📥 Received {len(messages)} messages | Next poll: {self.poll_interval_ms/1000:.1f}s | Viewers: {self.viewer_count}")
            else:
                logger.debug(f"📭 No new messages | Next poll: {self.poll_interval_ms/1000:.1f}s | Viewers: {self.viewer_count}")
            
            self.next_page_token = response.get("nextPageToken")
            self.error_backoff_seconds = 5  # Reset error backoff on success

            return messages
            
        except googleapiclient.errors.HttpError as e:
            error_code = e.resp.status if hasattr(e, 'resp') else 'unknown'
            
            # Handle quota exceeded and auth errors through unified handler
            if 'quotaExceeded' in str(e) or error_code == 403:
                logger.error(f"🚫 API Error during chat polling (HTTP {error_code}): {e}")
                if await self._handle_auth_error(e):
                    logger.info("🔄 Credential rotation handled, retrying polling...")
                    return []  # Return empty list to continue polling
                else:
                    logger.error("❌ Failed to handle credential rotation - service unavailable")
                    raise e
            
            logger.error(f"❌ API Error polling messages (HTTP {error_code}): {e}")
            if await self._handle_auth_error(e):
                logger.info("🔄 Auth error handled, polling might recover.")
                return []
            else:
                # Apply exponential backoff for other errors
                self.error_backoff_seconds = min(self.error_backoff_seconds * 1.5, 30)
                logger.warning(f"⏳ Applying {self.error_backoff_seconds}s backoff for API error")
                raise
        except Exception as e:
            logger.error(f"❌ Unexpected error polling chat: {e}")
            # Apply backoff for unexpected errors
            self.error_backoff_seconds = min(self.error_backoff_seconds * 2, 60)
            logger.warning(f"⏳ Applying {self.error_backoff_seconds}s backoff for unexpected error")
            time.sleep(self.error_backoff_seconds)
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
                logger.info(f"⏰ Rate limited user {user_id} for {self.trigger_cooldown - time_since_last:.1f}s")
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
        
        logger.info(f"💬 [{author_name}]: {display_message}")
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
        # Define valid emoji sequences that should trigger responses
        # Include both variants: with and without variation selector (️)
        valid_sequences = [
            "✊✊✊", "✊✊✋", "✊✊🖐️", "✊✊🖐", "✊✋✋", "✊✋🖐️", "✊✋🖐", 
            "✊🖐️🖐️", "✊🖐🖐", "✋✋✋", "✋✋🖐️", "✋✋🖐", "✋🖐️🖐️", 
            "✋🖐🖐", "🖐️🖐️🖐️", "🖐🖐🖐"
        ]
        
        # Check if any valid sequence is in the message
        for sequence in valid_sequences:
            if sequence in message_text:
                # Ensure proper UTF-8 encoding for emoji logging
                safe_sequence = sequence.encode('utf-8', errors='replace').decode('utf-8')
                logger.info(f"🎯 Found valid emoji sequence: {safe_sequence}")
                return True
        
        return False

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
        # Ensure proper UTF-8 encoding for emoji logging
        safe_message = message_text.encode('utf-8', errors='replace').decode('utf-8')
        logger.info(f"Emoji sequence detected in message from {author_name}: {safe_message}")
        
        # Check if this is a self-message (bot responding to its own emoji)
        if hasattr(self, 'bot_channel_id') and self.bot_channel_id and author_id == self.bot_channel_id:
            logger.debug(f"🚫 Ignoring self-message from bot {author_name} (channel ID match)")
            return False
        
        # Enhanced check for bot usernames (covers all possible bot names)
        bot_usernames = ["UnDaoDu", "FoundUps Agent", "FoundUpsAgent"]
        if author_name in bot_usernames:
            logger.debug(f"🚫 Ignoring message from bot username {author_name}")
            return False
        
        # Additional check: if the message contains the greeting message, it's likely from the bot
        if self.greeting_message and self.greeting_message.lower() in message_text.lower():
            logger.debug(f"🚫 Ignoring message containing greeting text from {author_name}")
            return False
        
        # Check rate limiting
        if self._is_rate_limited(author_id):
            logger.info(f"⏰ Skipping trigger for rate-limited user {author_name}")
            return False
        
        # Check global rate limiting
        current_time = time.time()
        if current_time - self.last_global_response < self.global_cooldown:
            logger.info(f"🌍 Global rate limit active, waiting {self.global_cooldown - (current_time - self.last_global_response):.1f}s")
            return False
        
        try:
            # Use banter engine to process the message directly - it handles detection internally
            start_time = time.time()
            logger.info(f"🎯 Calling banter_engine.process_input with message: '{message_text}'")
            state_info, response = self.banter_engine.process_input(message_text)
            processing_time = time.time() - start_time
            logger.info(f"Banter engine processed in {processing_time:.2f}s - state: {state_info}, response: {response}")
            
            if not response or not isinstance(response, str) or not response.strip():
                logger.warning(f"Empty or invalid banter response for {author_name}, trying LLM bypass")
                # Try LLM bypass engine as fallback
                try:
                    bypass_state, bypass_response = self.llm_bypass_engine.process_input(message_text)
                    if bypass_response and isinstance(bypass_response, str) and bypass_response.strip():
                        logger.info(f"LLM bypass provided response: {bypass_response}")
                        response = f"@{author_name} {bypass_response}"
                    else:
                        logger.warning(f"LLM bypass also failed, using final fallback")
                        response = self.llm_bypass_engine.get_fallback_response(author_name)
                        if response and not response.startswith(f"@{author_name}"):
                            response = f"@{author_name} {response}"
                except Exception as bypass_error:
                    logger.error(f"LLM bypass engine failed: {bypass_error}")
                    response = f"@{author_name} Hey! Thanks for the gesture! 👋"
            else:
                # Add @mention to successful banter responses too
                if response and not response.startswith(f"@{author_name}"):
                    response = f"@{author_name} {response}"
            
            logger.info(f"🤖 Responding to {author_name}: {response}")
            
            # Send response
            send_start = time.time()
            if await self.send_chat_message(response):
                send_time = time.time() - send_start
                logger.info(f"✅ Successfully sent response to @{author_name} in {send_time:.2f}s")
                self._update_trigger_time(author_id)
                self.last_global_response = time.time()  # Update global response time
                return True
            else:
                send_time = time.time() - send_start
                logger.error(f"❌ Failed to send response to @{author_name} after {send_time:.2f}s")
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
            
            # AUTO-MODERATION CHECK - Check for banned phrases and spam patterns first
            violation_detected, violation_reason = self.auto_moderator.check_message(display_message, author_id, author_name)
            if violation_detected:
                logger.warning(f"🚨 MODERATION ACTION: Timing out {author_name} for {violation_reason}")
                # Apply timeout
                timeout_success = await self.auto_moderator.apply_timeout(
                    self.live_chat_id, author_id, author_name, display_message, violation_reason
                )
                if timeout_success:
                    logger.info(f"✅ Successfully timed out {author_name} for 60 seconds (violation: {violation_reason})")
                else:
                    logger.error(f"❌ Failed to timeout {author_name}")
                
                # Still create log entry for moderation tracking
                log_entry = self._create_log_entry(msg_id, author_name, display_message)
                log_entry["moderation_action"] = "timeout_applied" if timeout_success else "timeout_failed"
                log_entry["reason"] = violation_reason
                log_entry["violation_type"] = violation_reason.split(":")[0] if ":" in violation_reason else violation_reason
                
                # Log the message for record keeping
                try:
                    self._log_to_user_file(message)
                except Exception as log_e:
                    logger.error(f"Failed to log moderated message: {log_e}")
                
                return log_entry
            
            # Check for trigger patterns (only if not moderated)
            logger.debug(f"🔍 Checking trigger patterns for message: '{display_message}'")
            if self._check_trigger_patterns(display_message):
                # Ensure proper UTF-8 encoding for emoji logging
                safe_message = display_message.encode('utf-8', errors='replace').decode('utf-8')
                logger.info(f"🎯 TRIGGER DETECTED! Processing emoji trigger for {author_name}")
                # Handle emoji trigger
                trigger_success = await self._handle_emoji_trigger(author_name, author_id, display_message)
                if not trigger_success and self._is_rate_limited(author_id):
                    # If handling failed due to rate limiting, return None
                    return None
            else:
                logger.debug(f"❌ No trigger patterns found in: '{display_message}'")
            
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

    def _get_stream_title(self):
        """Get and cache the stream title for logging purposes."""
        if self.stream_title is not None:
            return self.stream_title
        
        try:
            response = self.youtube.videos().list(part="snippet", id=self.video_id).execute()
            items = response.get("items", [])
            if items:
                self.stream_title = items[0]["snippet"]["title"]
                # Create shortened version (first 4 words, max 50 chars)
                words = self.stream_title.split()[:4]
                self.stream_title_short = " ".join(words)
                if len(self.stream_title_short) > 50:
                    self.stream_title_short = self.stream_title_short[:47] + "..."
                
                logger.info(f"📺 Stream title cached: {self.stream_title_short}")
                return self.stream_title
        except Exception as e:
            logger.warning(f"Failed to get stream title: {e}")
        
        # Fallback
        self.stream_title = "Unknown Stream"
        self.stream_title_short = "Unknown"
        return self.stream_title

    def _log_to_user_file(self, message):
        """Appends a clean log entry to a user-specific file for LLM consumption."""
        try:
            username = message["authorDetails"]["displayName"]
            channel_id = message["authorDetails"].get("channelId", "unknown")
            message_text = message["snippet"].get("displayMessage", "")
            
            # Skip empty messages
            if not message_text.strip():
                return
            
            # Get stream title for enhanced logging
            self._get_stream_title()
            
            # Create memory directories
            log_dir = os.path.join(self.memory_dir, "chat_logs").replace("\\", "/")
            conversation_dir = os.path.join(self.memory_dir, "conversations").replace("\\", "/")
            os.makedirs(log_dir, exist_ok=True)
            os.makedirs(conversation_dir, exist_ok=True)
            
            # Use channel ID as filename to prevent impersonation
            log_filename = os.path.join(log_dir, f"{channel_id}.jsonl").replace("\\", "/")
            
            # Store just the message content for LLM consumption
            with open(log_filename, "a", encoding="utf-8") as f:
                f.write(message_text + "\n")
            
            # Create enhanced conversation logs with stream title
            msg_id = message["id"]
            date_str = datetime.now().strftime("%Y-%m-%d")
            
            # Enhanced stream-specific conversation log with date, stream title, and video ID
            # Format: YYYY-MM-DD_StreamTitle_VideoID.txt
            safe_title = "".join(c for c in self.stream_title_short if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_title = safe_title.replace(' ', '_')
            stream_log = os.path.join(conversation_dir, f"{date_str}_{safe_title}_{self.video_id}.txt").replace("\\", "/")
            with open(stream_log, "a", encoding="utf-8") as f:
                f.write(f"[{msg_id}] {username}: {message_text}\n")
            
            # Enhanced daily conversation summary with stream context
            daily_summary = os.path.join(conversation_dir, f"daily_summary_{date_str}.txt").replace("\\", "/")
            with open(daily_summary, "a", encoding="utf-8") as f:
                f.write(f"[{self.stream_title_short}] [{msg_id}] {username}: {message_text}\n")
            
            logger.debug(f"Logged message from {username} to {safe_title} stream log")
        except Exception as e:
            logger.error(f"Failed to write to log file: {e}")
            raise

    async def send_chat_message(self, message_text):
        """
        Sends a text message to the live chat with human-like random delay.
        
        WSP Enhancement: Added random pre-send delay for more natural response timing.
        """
        if not self.live_chat_id:
            logger.error("Cannot send message, live_chat_id is not set.")
            return False

        logger.debug(f"Preparing to send message to chat ID: {self.live_chat_id}")
        max_len = 200
        if len(message_text) > max_len - 3:  # Leave room for '...'
            logger.warning(f"Message too long ({len(message_text)} chars), truncating to {max_len}.")
            message_text = message_text[:max_len-3] + "..."

        try:
            # WSP Enhancement: Add random pre-send delay for human-like behavior
            if self.random_delay_enabled:
                random_delay = random.uniform(self.min_random_delay, self.max_random_delay)
                logger.info(f"⏱️ Pre-send random delay: {random_delay:.2f}s (making response more human-like)")
                await asyncio.sleep(random_delay)

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
            logger.info(f"✅ Message sent successfully to chat ID: {self.live_chat_id}")
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

    def configure_random_delays(self, enabled: bool = True, min_delay: float = 0.8, max_delay: float = 4.0):
        """
        Configure random delay settings for human-like behavior.
        
        Args:
            enabled: Whether to enable random delays
            min_delay: Minimum random delay in seconds  
            max_delay: Maximum random delay in seconds
        """
        self.random_delay_enabled = enabled
        self.min_random_delay = max(0.1, min_delay)  # Ensure minimum of 0.1s
        self.max_random_delay = max(self.min_random_delay + 0.1, max_delay)  # Ensure max > min
        
        logger.info(f"🎲 Random delays configured: enabled={enabled}, range={self.min_random_delay:.1f}s-{self.max_random_delay:.1f}s")

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
        Process a batch of messages with proper error handling and deduplication.
        
        Args:
            messages: List of messages to process
        """
        new_messages = 0
        duplicate_messages = 0
        
        for message in messages:
            try:
                # Extract message ID for deduplication
                msg_id = message.get("id")
                if not msg_id:
                    logger.warning("Message missing ID, skipping deduplication check")
                    await self._process_message(message)
                    continue
                
                # Check if we've already processed this message
                if msg_id in self.processed_message_ids:
                    duplicate_messages += 1
                    logger.debug(f"🔄 Skipping already processed message ID: {msg_id}")
                    continue
                
                # Process new message
                await self._process_message(message)
                new_messages += 1
                
                # Add to processed set
                self.processed_message_ids.add(msg_id)
                
                # Cleanup old message IDs if we're getting too many
                if len(self.processed_message_ids) > self.max_processed_ids:
                    # Remove oldest 25% of IDs to free up memory
                    oldest_ids = list(self.processed_message_ids)[:self.max_processed_ids // 4]
                    for old_id in oldest_ids:
                        self.processed_message_ids.discard(old_id)
                    logger.debug(f"🧹 Cleaned up {len(oldest_ids)} old message IDs from memory")
                
            except Exception as processing_e:
                logger.error(f"Error during message processing: {processing_e}")
        
        # Log batch processing summary
        if new_messages > 0 or duplicate_messages > 0:
            logger.debug(f"📊 Batch processed: {new_messages} new, {duplicate_messages} duplicates skipped")

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
        if quota_usage > 80:
            return 30  # High usage, wait 30 seconds
        elif quota_usage > 60:
            return 20  # Medium-high usage, wait 20 seconds
        elif quota_usage > 40:
            return 15  # Medium usage, wait 15 seconds
        else:
            return 10  # Low usage, wait 10 seconds
    
    # Auto-Moderation Management Methods
    
    def get_moderation_stats(self) -> Dict[str, Any]:
        """
        Get auto-moderation statistics including spam detection metrics.
        
        Returns:
            Dict[str, Any]: Comprehensive moderation statistics and configuration
        """
        stats = self.auto_moderator.get_stats()
        stats.update({
            "moderation_enabled": True,
            "enhanced_spam_detection": True
        })
        return stats
    
    def get_user_violations(self, author_id: str) -> Dict[str, Any]:
        """
        Get violation information for a specific user.
        
        Args:
            author_id (str): The user's channel ID
            
        Returns:
            Dict[str, Any]: User violation statistics and recent activity
        """
        return self.auto_moderator.get_user_violations(author_id)
    
    def get_top_violators(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get users with the most violations.
        
        Args:
            limit (int): Maximum number of users to return
            
        Returns:
            List[Dict]: Top violators with their statistics
        """
        return self.auto_moderator.get_top_violators(limit)
    
    def clear_user_violations(self, author_id: str) -> bool:
        """
        Clear violation history for a user (moderator action).
        
        Args:
            author_id (str): The user's channel ID
            
        Returns:
            bool: True if violations were cleared
        """
        return self.auto_moderator.clear_user_violations(author_id)
    
    def adjust_spam_settings(self, **kwargs) -> Dict[str, Any]:
        """
        Adjust spam detection settings.
        
        Args:
            **kwargs: Settings to update (rate_limit, time_window, similarity_threshold, timeout_duration)
            
        Returns:
            Dict[str, Any]: Old and new settings
        """
        return self.auto_moderator.adjust_spam_settings(**kwargs)
    
    def add_banned_phrase(self, phrase: str) -> bool:
        """
        Add a new phrase to the banned phrases list.
        
        Args:
            phrase (str): The phrase to ban
            
        Returns:
            bool: True if phrase was added successfully
        """
        return self.auto_moderator.add_banned_phrase(phrase)
    
    def remove_banned_phrase(self, phrase: str) -> bool:
        """
        Remove a phrase from the banned phrases list.
        
        Args:
            phrase (str): The phrase to remove
            
        Returns:
            bool: True if phrase was removed successfully
        """
        return self.auto_moderator.remove_banned_phrase(phrase)
    
    def get_banned_phrases(self) -> List[str]:
        """
        Get the current list of banned phrases.
        
        Returns:
            List[str]: List of banned phrases
        """
        return self.auto_moderator.get_banned_phrases()



