"""
Session Manager - WSP Compliant Module
Manages YouTube Live Chat sessions, authentication, and stream metadata
"""

import logging
import os
import time
import asyncio
import random
from typing import Optional, Dict, Any
import googleapiclient.errors

logger = logging.getLogger(__name__)

class SessionManager:
    """
    Manages YouTube Live Chat sessions.
    Handles authentication, stream discovery, and session lifecycle.
    """
    
    def __init__(self, youtube_service, video_id: str):
        self.youtube = youtube_service
        self.video_id = video_id
        self.live_chat_id = None
        self.stream_title = None
        self.stream_title_short = None
        self.viewer_count = 0
        self.is_active = False
        self.greeting_message = os.getenv("AGENT_GREETING_MESSAGE", "🤖 Bot is now monitoring chat! ✊✋🖐️")
        
        logger.info(f"SessionManager initialized for video: {video_id}")
    
    def get_live_chat_id(self) -> Optional[str]:
        """
        Fetch the live chat ID for the video.
        
        Returns:
            Live chat ID if found, None otherwise
        """
        try:
            logger.info(f"Fetching live chat ID for video: {self.video_id}")
            
            # Get video details
            video_response = self.youtube.videos().list(
                part="liveStreamingDetails,snippet",
                id=self.video_id
            ).execute()
            
            if not video_response.get("items"):
                logger.error(f"No video found with ID: {self.video_id}")
                return None
            
            video_item = video_response["items"][0]
            
            # Get stream title
            snippet = video_item.get("snippet", {})
            self.stream_title = snippet.get("title", "Unknown Stream")
            self.stream_title_short = self.stream_title[:50] + "..." if len(self.stream_title) > 50 else self.stream_title
            logger.info(f"Stream title: {self.stream_title_short}")
            
            # Get live chat ID
            streaming_details = video_item.get("liveStreamingDetails", {})
            self.live_chat_id = streaming_details.get("activeLiveChatId")
            
            if not self.live_chat_id:
                logger.error(f"No active live chat found for video: {self.video_id}")
                return None
            
            # Get viewer count if available
            self.viewer_count = streaming_details.get("concurrentViewers", 0)
            logger.info(f"Found live chat ID: {self.live_chat_id}, Viewers: {self.viewer_count}")
            
            self.is_active = True
            return self.live_chat_id
            
        except googleapiclient.errors.HttpError as e:
            logger.error(f"HTTP error fetching live chat ID: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching live chat ID: {e}")
            return None
    
    def update_viewer_count(self) -> int:
        """
        Update the current viewer count.
        
        Returns:
            Current viewer count
        """
        try:
            video_response = self.youtube.videos().list(
                part="liveStreamingDetails",
                id=self.video_id
            ).execute()
            
            if video_response.get("items"):
                streaming_details = video_response["items"][0].get("liveStreamingDetails", {})
                self.viewer_count = int(streaming_details.get("concurrentViewers", 0))
                logger.debug(f"Updated viewer count: {self.viewer_count}")
            
        except Exception as e:
            logger.error(f"Error updating viewer count: {e}")
        
        return self.viewer_count
    
    async def initialize_session(self) -> bool:
        """
        Initialize a new chat session.
        
        Returns:
            True if session initialized successfully
        """
        logger.info("Initializing chat session...")
        
        # Get live chat ID
        if not self.get_live_chat_id():
            logger.error("Failed to initialize session - no live chat ID")
            return False
        
        logger.info(f"Session initialized successfully for: {self.stream_title_short}")
        return True
    
    async def send_greeting(self, send_function) -> bool:
        """
        Send greeting message to chat.
        
        Args:
            send_function: Function to send messages to chat
            
        Returns:
            True if greeting sent successfully
        """
        if not self.greeting_message:
            logger.info("No greeting message configured")
            return True
        
        try:
            # Add delay before greeting (from live_chat_processor)
            import random
            delay = random.uniform(1, 3)
            logger.info(f"Waiting {delay:.1f}s before greeting")
            await asyncio.sleep(delay)
            
            logger.info(f"Sending greeting: {self.greeting_message}")
            success = await send_function(self.greeting_message)
            
            if success:
                logger.info("Greeting sent successfully")
                # Add post-greeting delay (from live_chat_processor)
                await asyncio.sleep(random.uniform(1, 2))
            else:
                logger.warning("Failed to send greeting")
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending greeting: {e}")
            return False
    
    def end_session(self):
        """End the current chat session."""
        logger.info(f"Ending session for: {self.stream_title_short}")
        self.is_active = False
        self.live_chat_id = None
    
    def get_session_info(self) -> Dict[str, Any]:
        """
        Get current session information.
        
        Returns:
            Dictionary containing session details
        """
        return {
            "video_id": self.video_id,
            "live_chat_id": self.live_chat_id,
            "stream_title": self.stream_title,
            "viewer_count": self.viewer_count,
            "is_active": self.is_active,
            "greeting_message": self.greeting_message
        }
    
    def handle_auth_error(self, error: Exception) -> bool:
        """
        Handle authentication errors.
        
        Args:
            error: The authentication error
            
        Returns:
            True if error was handled and session can continue
        """
        if isinstance(error, googleapiclient.errors.HttpError):
            if error.resp.status == 401:
                logger.error("Authentication failed - token may be expired")
                return False
            elif error.resp.status == 403:
                logger.error("Access forbidden - check API permissions")
                return False
            elif error.resp.status == 404:
                logger.error("Chat not found - stream may have ended")
                self.end_session()
                return False
        
        logger.error(f"Unhandled auth error: {error}")
        return False
    
    def is_session_active(self) -> bool:
        """Check if the session is still active."""
        return self.is_active and self.live_chat_id is not None