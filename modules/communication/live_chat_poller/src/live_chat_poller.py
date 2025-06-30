"""
LiveChatPoller Module for Windsurf Project

Handles polling of YouTube Live Chat messages.
"""

import logging
import time
import googleapiclient.errors

logger = logging.getLogger(__name__)

class LiveChatPoller:
    """
    Polls YouTube Live Chat for new messages.
    Handles pagination, rate limiting, and error recovery.
    """

    def __init__(self, youtube_service, video_id: str):
        """
        Initialize the LiveChatPoller.

        Args:
            youtube_service: Authenticated YouTube service instance
            video_id (str): ID of the livestream video
        """
        self.youtube = youtube_service
        self.video_id = video_id
        self.live_chat_id = None
        self.next_page_token = None
        logger.info("LiveChatPoller initialized")

    def get_live_chat_id(self) -> str:
        """
        Fetch the live chat ID for the video.
        
        Returns:
            str: Live chat ID if found, None otherwise
        """
        try:
            video_response = self.youtube.videos().list(
                part="liveStreamingDetails",
                id=self.video_id
            ).execute()

            if not video_response.get("items"):
                logger.error(f"No video found with ID {self.video_id}")
                return None

            details = video_response["items"][0].get("liveStreamingDetails", {})
            chat_id = details.get("activeLiveChatId")
            
            if not chat_id:
                logger.error(f"No active live chat found for video {self.video_id}")
                return None

            logger.info(f"Found live chat ID: {chat_id}")
            self.live_chat_id = chat_id
            return chat_id

        except Exception as e:
            logger.error(f"Error fetching live chat ID: {e}")
            return None

    def poll_once(self) -> tuple:
        """
        Poll for new messages once.
        
        Returns:
            tuple: (list of messages, polling interval in milliseconds)
        """
        if not self.live_chat_id:
            self.live_chat_id = self.get_live_chat_id()
            if not self.live_chat_id:
                return [], 5000

        try:
            response = self.youtube.liveChatMessages().list(
                liveChatId=self.live_chat_id,
                part="snippet,authorDetails",
                pageToken=self.next_page_token
            ).execute()

            self.next_page_token = response.get("nextPageToken")
            messages = response.get("items", [])
            polling_interval = response.get("pollingIntervalMillis", 5000)

            if messages:
                logger.debug(f"Fetched {len(messages)} new messages")
            
            return messages, polling_interval

        except googleapiclient.errors.HttpError as e:
            if e.resp.status in [403, 404]:
                logger.error(f"Chat ended or access forbidden: {e}")
                self.live_chat_id = None
            else:
                logger.error(f"HTTP error while polling: {e}")
            return [], 5000

        except Exception as e:
            logger.error(f"Error polling messages: {e}")
            return [], 5000 