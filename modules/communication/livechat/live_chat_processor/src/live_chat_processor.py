"""
LiveChatProcessor Module for Windsurf Project

Handles processing of live chat messages, including banter triggers and responses.
Integrates with BanterEngine for generating themed responses.
"""

import time
import logging
import threading
import os
import random
import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import googleapiclient.errors
from modules.ai_intelligence.banter_engine import BanterEngine
from modules.communication.livechat.live_chat_poller.src.live_chat_poller import LiveChatPoller
from unittest.mock import Mock, patch, MagicMock
from modules.infrastructure.models.chat_message import ChatMessage, Author
from modules.infrastructure.token_manager.src.token_manager import TokenManager
# StreamResolver import removed as it's unused and caused errors

# Configure logging
logger = logging.getLogger(__name__)

# Suppress overly verbose logging from googleapiclient.discovery
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)

class LiveChatProcessor:
    """
    Processes live chat messages and manages banter responses.
    Handles trigger detection, cooldown management, and message sending.
    """

    # Banter Cooldown settings (in seconds)
    MIN_BANTER_COOLDOWN = 15
    MAX_BANTER_COOLDOWN = 45

    def __init__(self, youtube_service, video_id: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the LiveChatProcessor.

        Args:
            youtube_service: Authenticated YouTube service instance
            video_id (str): ID of the livestream video
            config (Optional[Dict[str, Any]]): Configuration dictionary
        """
        if config is None:
            config = {}

        self.youtube_service = youtube_service
        self.video_id = video_id
        self.live_chat_id = None  # Will be fetched by Poller
        self.config = config
        self.memory_dir = config.get("memory_dir", "memory")
        self.greeting_message = config.get("AGENT_GREETING_MESSAGE", 
                                         os.getenv("AGENT_GREETING_MESSAGE", 
                                         "FoundUps Agent reporting in!"))

        # Ensure memory directory exists
        os.makedirs(self.memory_dir, exist_ok=True)
        log_dir = os.path.join(self.memory_dir, "chat_logs")
        os.makedirs(log_dir, exist_ok=True)
        logger.info(f"Memory directory set to: {self.memory_dir}, Log dir: {log_dir}")

        # Initialize components
        self.banter_engine = BanterEngine()
        self.last_banter_time = 0
        self.current_banter_cooldown = self._get_new_cooldown()
        self.poller = LiveChatPoller(youtube_service, video_id)
        self.is_running = False
        self.poll_thread = None
        logger.info(f"LiveChatProcessor initialized with BanterEngine. Initial cooldown: {self.current_banter_cooldown:.1f}s")

    def _get_new_cooldown(self) -> float:
        """
        Generate a new random cooldown time between MIN and MAX values.
        
        Returns:
            float: Cooldown time in seconds
        """
        return random.uniform(self.MIN_BANTER_COOLDOWN, self.MAX_BANTER_COOLDOWN)

    def _log_to_user_file(self, message: Dict[str, Any]) -> None:
        """
        Logs a clean conversation entry for agent memory.
        
        Args:
            message (Dict[str, Any]): The message to log
        """
        try:
            username = message["authorDetails"].get("displayName", "UnknownAuthor")
            message_text = message["snippet"].get("displayMessage", "")
            timestamp = datetime.now().strftime("%H:%M")
            
            # Create memory directories
            log_dir = os.path.join(self.memory_dir, "chat_logs")
            conversation_dir = os.path.join(self.memory_dir, "conversation")
            os.makedirs(log_dir, exist_ok=True)
            os.makedirs(conversation_dir, exist_ok=True)
            
            # Save clean conversation entry
            clean_entry = {
                "time": timestamp,
                "user": username,
                "message": message_text
            }
            
            # Individual user log
            safe_username = "".join(c for c in username if c.isalnum() or c in (' ', '_', '-')).rstrip()
            if not safe_username:
                safe_username = "InvalidUsername"
            
            log_filename = os.path.join(log_dir, f"{safe_username}.jsonl")
            with open(log_filename, "a", encoding="utf-8") as f:
                json.dump(clean_entry, f, ensure_ascii=False)
                f.write("\n")
            
            # Session conversation log
            session_log = os.path.join(conversation_dir, "current_session.txt")
            with open(session_log, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] {username}: {message_text}\n")
            
            logger.debug(f"Logged clean conversation entry for {username}")
        except Exception as e:
            logger.exception(f"Failed to write to log file: {e}")

    def _check_banter_trigger(self, message_text: str, author_name: str) -> None:
        """
        Check if a message contains the banter trigger sequence and send response if appropriate.
        
        Args:
            message_text (str): The message text to check
            author_name (str): Name of the message author
        """
        trigger_sequence = ["✊", "✋", "🖐️"]
        if all(symbol in message_text for symbol in trigger_sequence):
            current_time = time.time()
            if current_time > self.last_banter_time + self.current_banter_cooldown:
                logger.info(f"Detected trigger sequence '✊✋🖐️' from {author_name}. Attempting to send banter.")
                banter_line = self.banter_engine.get_random_banter(theme="roast")

                if banter_line and banter_line != "...silence...":
                    logger.debug(f"Selected banter line: '{banter_line}'")
                    if self.send_chat_message(banter_line):
                        logger.info(f"Sent banter (roast) successfully: '{banter_line}'")
                        self.last_banter_time = current_time
                        self.current_banter_cooldown = self._get_new_cooldown()
                        logger.info(f"Banter cooldown reset. Next available in {self.current_banter_cooldown:.1f}s")
                    else:
                        logger.warning(f"Failed to send banter for trigger by {author_name}.")
                else:
                    logger.warning(f"BanterEngine returned no suitable line for 'roast' theme triggered by {author_name}.")
            else:
                remaining_cooldown = (self.last_banter_time + self.current_banter_cooldown) - current_time
                logger.debug(f"Trigger sequence '✊✋🖐️' detected from {author_name}, but cooldown active. {remaining_cooldown:.1f}s remaining.")

    def send_chat_message(self, message_text: str) -> bool:
        """
        Send a message to the live chat.
        
        Args:
            message_text (str): The message to send
            
        Returns:
            bool: True if message was sent successfully, False otherwise
        """
        if not self.live_chat_id:
            logger.error("Cannot send message, live_chat_id is not set or became invalid.")
            return False

        logger.debug(f"Preparing to send message to chat ID: {self.live_chat_id}: '{message_text}'")
        max_len = 200
        if len(message_text) > max_len:
            logger.warning(f"Message too long ({len(message_text)} chars), truncating to {max_len}.")
            message_text = message_text[:max_len]

        try:
            request = self.youtube_service.liveChat().messages().insert(
                part="snippet",
                body={
                    "snippet": {
                        "liveChatId": self.live_chat_id,
                        "type": "textMessageEvent",
                        "textMessageDetails": {"messageText": message_text}
                    }
                }
            )
            response = request.execute()
            sent_message_id = response.get('id', 'N/A')
            logger.info(f"Message sent successfully (ID: {sent_message_id}) to chat ID: {self.live_chat_id}")
            return True

        except googleapiclient.errors.HttpError as e:
            logger.error(f"HTTP error while sending message to chat {self.live_chat_id}: {e}")
            try:
                error_details = json.loads(e.content.decode('utf-8')).get('error', {})
                error_message = error_details.get('message', 'No message.')
                error_reason = error_details.get('errors', [{}])[0].get('reason', 'No reason.')
                logger.error(f"API Send Error: Status={e.resp.status}, Reason={error_reason}, Msg='{error_message}'")
                if e.resp.status in [403, 404]:
                    logger.error("Chat may have ended or sending forbidden. Invalidating chat ID.")
                    self.live_chat_id = None
                    self.poller.live_chat_id = None
            except Exception:
                logger.error(f"Could not parse error details from HttpError content. Raw: {e.content}")
            return False
        except Exception as e:
            logger.exception(f"Unexpected error while sending message: {e}")
            return False

    def process_single_message(self, message: Dict[str, Any]) -> None:
        """
        Process a single chat message.
        
        Args:
            message (Dict[str, Any]): The message to process
        """
        try:
            msg_id = message["id"]
            snippet = message["snippet"]
            author_details = message["authorDetails"]
            message_type = snippet.get("type")

            if message_type == 'textMessageEvent':
                display_message = snippet.get("displayMessage", "")
                author_name = author_details.get("displayName", "Unknown Author")
                published_at = snippet.get("publishedAt")

                logger.debug(f"Processing message [{published_at}] {author_name}: {display_message}")

                # Log the message
                self._log_to_user_file(message)

                # Check for triggers
                self._check_banter_trigger(display_message, author_name)

            else:
                logger.debug(f"Ignoring non-text message type: {message_type}")

        except KeyError as ke:
            logger.error(f"KeyError processing message: {ke}. Message dump: {message}")
        except Exception as e:
            logger.exception(f"Unexpected error processing message ID {message.get('id', 'N/A')}: {e}")

    def process_message_batch(self, messages: list) -> int:
        """
        Process a list of messages.
        
        Args:
            messages (list): List of messages to process
            
        Returns:
            int: Number of messages processed
        """
        if not messages:
            return 0

        processed_count = 0
        for message in messages:
            self.process_single_message(message)
            processed_count += 1
        logger.debug(f"Finished processing batch of {processed_count} messages.")
        return processed_count

    def _poll_messages(self) -> None:
        """
        Poll for new messages from the live chat.
        """
        # Initial fetch of Chat ID via Poller
        self.live_chat_id = self.poller.get_live_chat_id()
        if not self.live_chat_id:
            logger.error(f"Could not find active live chat for video {self.video_id}. Cannot start listener.")
            self.is_running = False
            return

        logger.info(f"Successfully connected using chat ID: {self.live_chat_id}")

        # Send greeting message if configured
        if self.greeting_message:
            logger.info(f"Attempting to send greeting message: '{self.greeting_message}'")
            time.sleep(random.uniform(1, 3))
            if self.send_chat_message(self.greeting_message):
                logger.info("Greeting message sent successfully.")
            else:
                logger.error("Failed to send greeting message. Continuing anyway.")
            time.sleep(random.uniform(1, 2))
        else:
            logger.info("No greeting message configured.")

        while self.is_running:
            try:
                # Make sure poller has the latest chat ID if it was invalidated
                if self.live_chat_id:
                    self.poller.live_chat_id = self.live_chat_id
                else:
                    logger.warning("Processor lost chat ID, attempting refetch via Poller...")
                    self.live_chat_id = self.poller.get_live_chat_id()
                    if not self.live_chat_id:
                        logger.error("Failed to re-acquire chat ID after loss. Stopping listener.")
                        self.is_running = False
                        break
                    logger.info(f"Re-acquired chat ID: {self.live_chat_id}")

                # Poll for new messages
                new_messages, poll_interval_ms = self.poller.poll_once()

                # Check if poller indicated chat ID became invalid during poll
                if self.poller.live_chat_id is None and self.live_chat_id is not None:
                    logger.warning("Poller invalidated the chat ID. Will attempt refetch on next loop.")
                    self.live_chat_id = None

                # Process the received messages
                self.process_message_batch(new_messages)

                # Wait for the duration suggested by the poller
                sleep_time_seconds = max(poll_interval_ms / 1000.0, 1.0)
                logger.info(f"Waiting {sleep_time_seconds:.2f}s for next poll cycle.")
                time.sleep(sleep_time_seconds)

            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received. Stopping listener...")
                self.is_running = False
            except Exception as loop_err:
                logger.exception(f"Unexpected error in main processing loop: {loop_err}. Attempting to continue after delay.")
                try:
                    time.sleep(10)
                except KeyboardInterrupt:
                    logger.info("Keyboard interrupt during error backoff. Stopping.")
                    self.is_running = False

        logger.info("Chat processing loop stopped.")

    def start_listening(self) -> None:
        """
        Start the message polling and processing loop.
        """
        if self.is_running:
            logger.warning("Processor is already running")
            return

        logger.info("Attempting to start live chat processing loop...")
        self.is_running = True
        self.poll_thread = threading.Thread(target=self._poll_messages)
        self.poll_thread.daemon = True
        self.poll_thread.start()
        logger.info("Started message polling thread")

    def stop_listening(self) -> None:
        """
        Stop the message polling and processing loop.
        """
        if not self.is_running:
            logger.warning("Processor is not running")
            return

        logger.info("Received stop signal for processor loop.")
        self.is_running = False
        if self.poll_thread:
            self.poll_thread.join(timeout=5)
        logger.info("Stopped message polling thread") 