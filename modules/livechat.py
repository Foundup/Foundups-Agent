import logging
import os
import time
from datetime import datetime
import googleapiclient.errors
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class LiveChatListener:
    """
    Connects to a YouTube livestream chat, listens for messages,
    logs them, and provides hooks for sending messages and AI interaction.
    """
    def __init__(self, youtube_service, video_id):
        self.youtube = youtube_service
        self.video_id = video_id
        self.live_chat_id = None
        self.next_page_token = None
        self.poll_interval_ms = 10000  # Default: 10 seconds
        self.error_backoff_seconds = 5  # Initial backoff for errors
        self.memory_dir = "memory"
        self.greeting_message = os.getenv("AGENT_GREETING_MESSAGE", "FoundUps Agent reporting in!")
        self.message_queue = []  # Queue for storing messages

        os.makedirs(self.memory_dir, exist_ok=True)
        logger.info(f"Memory directory set to: {self.memory_dir}")

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

    def _poll_chat_messages(self):
        """Polls the YouTube API for new chat messages."""
        try:
            response = self.youtube.liveChatMessages().list(
                liveChatId=self.live_chat_id,
                part="snippet,authorDetails",
                pageToken=self.next_page_token
            ).execute()

            self.next_page_token = response.get("nextPageToken")
            self.poll_interval_ms = response.get("pollingIntervalMillis", self.poll_interval_ms)
            self.error_backoff_seconds = 5  # Reset error backoff on success

            messages = response.get("items", [])
            if messages:
                logger.debug(f"Received {len(messages)} new messages.")
                for message in messages:
                    try:
                        self._process_message(message)
                    except Exception as e:
                        logger.error(f"Error processing message: {e}")
            else:
                logger.debug("No new messages.")

            return messages

        except googleapiclient.errors.HttpError as e:
            logger.error(f"HTTP Error during polling: {e}")
            if e.resp.status in [403, 429, 500, 503]:
                logger.warning(f"Received status {e.resp.status}. Backing off for {self.error_backoff_seconds} seconds.")
                time.sleep(self.error_backoff_seconds)
                self.error_backoff_seconds = min(self.error_backoff_seconds * 2, 60)
            return []
        except Exception as e:
            logger.error(f"Unexpected error polling chat: {e}")
            time.sleep(self.error_backoff_seconds)
            self.error_backoff_seconds = min(self.error_backoff_seconds * 2, 60)
            return []

    def _process_message(self, message):
        """Processes a single chat message and logs it."""
        try:
            msg_id = message["id"]
            snippet = message["snippet"]
            author_details = message["authorDetails"]

            display_message = snippet.get("displayMessage", "")
            author_name = author_details["displayName"]

            log_entry = {
                "id": msg_id,
                "author": author_name,
                "message": display_message,
                "timestamp": datetime.now().isoformat()
            }

            self._log_to_user_file(message)
            return log_entry
        except Exception as e:
            logger.error(f"Error processing message: {e}")
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

    def send_chat_message(self, message_text):
        """Sends a text message to the live chat."""
        if not self.live_chat_id:
            logger.error("Cannot send message, live_chat_id is not set.")
            return False

        max_len = 200
        if len(message_text) > max_len - 3:  # Leave room for '...'
            logger.warning(f"Message too long ({len(message_text)} chars), truncating to {max_len}.")
            message_text = message_text[:max_len-3] + "..."

        try:
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
            response = request.execute()
            logger.info("Message sent successfully")
            return True
        except googleapiclient.errors.HttpError as e:
            logger.error(f"Failed to send message: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False

    def start_listening(self):
        """Starts the main loop to poll for chat messages."""
        logger.info("Attempting to start live chat listener...")
        if not self._get_live_chat_id():
            logger.error(f"Could not find active live chat for video {self.video_id}. Exiting listener.")
            return

        logger.info(f"Successfully connected to chat ID: {self.live_chat_id}")

        if self.greeting_message:
            self.send_chat_message(self.greeting_message)
            time.sleep(2)

        logger.info("Starting chat polling loop...")
        while True:
            messages = self._poll_chat_messages()
            if messages is None:  # None indicates critical failure
                logger.error("Polling failed critically. Stopping listener.")
                break

            sleep_time_seconds = self.poll_interval_ms / 1000.0
            logger.debug(f"Sleeping for {sleep_time_seconds:.2f} seconds...")
            try:
                time.sleep(sleep_time_seconds)
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received. Stopping listener...")
                break

        logger.info("Chat listener stopped.")
