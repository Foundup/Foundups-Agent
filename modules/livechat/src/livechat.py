import logging
import os
import time
from datetime import datetime
import googleapiclient.errors
from dotenv import load_dotenv
from utils.throttling import calculate_dynamic_delay
from modules.token_manager import token_manager
from modules.banter_engine import BanterEngine
from utils.oauth_manager import get_authenticated_service
import asyncio

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
        self.trigger_emojis = ["✊", "✋", "🖐️"]  # Configurable emoji trigger set
        self.last_trigger_time = {}  # Track last trigger time per user
        self.trigger_cooldown = 60  # Cooldown period in seconds

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
                self.viewer_count = int(items[0]["statistics"].get("viewCount", 0))
                logger.debug(f"Updated viewer count: {self.viewer_count}")
        except Exception as e:
            logger.error(f"Failed to update viewer count: {e}")

    async def _poll_chat_messages(self):
        """Polls the YouTube API for new chat messages."""
        try:
            response = self.youtube.liveChatMessages().list(
                liveChatId=self.live_chat_id,
                part="snippet,authorDetails",
                pageToken=self.next_page_token
            ).execute()

            # Get the polling interval from YouTube's response
            server_poll_interval = response.get("pollingIntervalMillis", 10000)  # Default to 10 seconds if not specified
            
            # Calculate dynamic delay based on viewer count
            dynamic_delay = calculate_dynamic_delay(self.viewer_count)
            
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

    async def _process_message(self, message):
        """
        Process a single chat message and handle triggers.
        
        Args:
            message (dict): YouTube chat message object containing:
                - id: Message identifier
                - snippet: Message content and metadata
                - authorDetails: Information about the message sender
                
        Returns:
            dict: Processed log entry containing message details
            
        Raises:
            Exception: If message processing fails
        """
        try:
            msg_id = message["id"]
            snippet = message["snippet"]
            author_details = message["authorDetails"]
            author_id = author_details.get("channelId", "unknown")

            display_message = snippet.get("displayMessage", "")
            author_name = author_details["displayName"]

            # Diagnostic logging for message processing
            logger.debug(f"Chat message received: {display_message}")
            logger.debug(f"Message length: {len(display_message)}")
            logger.debug(f"Looking for emojis: {self.trigger_emojis}")
            
            # Check for exact emoji sequence
            if "✊✋🖐️" in display_message:
                logger.info(f"Emoji sequence detected in message from {author_name}: {display_message}")
                
                # Check rate limiting
                if self._is_rate_limited(author_id):
                    logger.debug(f"Skipping trigger for rate-limited user {author_name}")
                    return None
                
                try:
                    # Get banter response with fallback
                    response = self.banter_engine.get_random_banter(theme="greeting")
                    if not response or not isinstance(response, str) or not response.strip():
                        logger.warning(f"Empty or invalid banter response for {author_name}, using fallback")
                        response = "Hey there! Thanks for the gesture! 👋"
                    
                    logger.debug(f"Generated banter response for {author_name}: {response}")
                    
                    if await self.send_chat_message(response):
                        logger.info(f"Successfully queued banter response for {author_name}")
                        self._update_trigger_time(author_id)
                    else:
                        logger.error(f"Failed to queue banter response for {author_name}")
                except Exception as e:
                    logger.error(f"Error processing emoji trigger for {author_name}: {str(e)}")
                    # Continue processing even if trigger fails

            log_entry = {
                "id": msg_id,
                "author": author_name,
                "message": display_message,
                "timestamp": datetime.now().isoformat()
            }

            self._log_to_user_file(message)
            return log_entry
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            raise

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

    async def start_listening(self):
        """Starts the chat listener loop."""
        if not self.is_running:
            logger.info("Attempting to start live chat listener...")
            
            try:
                if not self.live_chat_id:
                    logger.info("No live_chat_id provided, attempting to fetch it...")
                    self.live_chat_id = self._get_live_chat_id()
                    if not self.live_chat_id:
                        logger.error(f"Could not find active live chat for video {self.video_id}. Exiting listener.")
                        return
                else:
                    logger.info(f"Using provided live chat ID: {self.live_chat_id}")

                logger.info(f"Successfully connected to chat ID: {self.live_chat_id}")

                if self.greeting_message:
                    logger.info(f"Attempting to send greeting message: {self.greeting_message}")
                    try:
                        if await self.send_chat_message(self.greeting_message):
                            logger.info("Greeting message sent successfully")
                        else:
                            logger.error("Failed to send greeting message - send_chat_message returned False")
                    except Exception as e:
                        logger.error(f"Exception while sending greeting message: {e}")
                    time.sleep(2)
                else:
                    logger.warning("No greeting message configured")

                logger.info("Starting chat polling loop...")
                self.is_running = True
                while self.is_running:
                    # Update viewer count and adjust polling interval
                    self._update_viewer_count()
                    
                    messages = await self._poll_chat_messages()
                    if messages is None:  # None indicates critical failure
                        logger.error("Polling failed critically. Stopping listener.")
                        break

                    # Process messages asynchronously if _process_message is async
                    if messages:
                        for message in messages:
                            try:
                                await self._process_message(message)
                            except Exception as processing_e:
                                logger.error(f"Error during message processing: {processing_e}")

                    sleep_time_seconds = self.poll_interval_ms / 1000.0
                    logger.debug(f"Current viewer count: {self.viewer_count}, Waiting {sleep_time_seconds:.2f}s before next poll")
                    await asyncio.sleep(sleep_time_seconds)

            except Exception as e:
                logger.error(f"Critical error in chat listener: {str(e)}")
                raise

            logger.info("Chat listener stopped.")
