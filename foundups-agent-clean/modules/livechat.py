import logging
import os
import time
from datetime import datetime
import googleapiclient.errors
from dotenv import load_dotenv
from modules.youtube_auth import get_authenticated_service

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

    def _handle_quota_error(self, e):
        """Handle quota exceeded error by recreating service with secondary API key."""
        if "quota" in str(e).lower():
            logger.warning("Quota exceeded, attempting to switch to secondary API key...")
            try:
                self.youtube = get_authenticated_service()  # This will try secondary key if primary fails
                return True
            except Exception as e2:
                logger.error(f"Failed to switch to secondary API key: {e2}")
        return False

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
            if self._handle_quota_error(e):
                return self._get_live_chat_id()  # Retry with new service
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
            if self._handle_quota_error(e):
                return self._poll_chat_messages()  # Retry with new service
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