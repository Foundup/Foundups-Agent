"""
Session Manager - WSP Compliant Module
Manages YouTube Live Chat sessions, authentication, and stream metadata

WSP 17 Pattern Registry: This is a REUSABLE PATTERN
- Documented in: modules/communication/PATTERN_REGISTRY.md
- Pattern: Connection lifecycle + greeting management
- Features: Auto-reconnect, greeting delay, update broadcasts
- Reusable for: LinkedIn, X/Twitter, Discord, Twitch
"""

import logging
import os
import time
import asyncio
import random
from typing import Optional, Dict, Any
import googleapiclient.errors
from modules.communication.livechat.src.grok_greeting_generator import GrokGreetingGenerator

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
        # WSP 84 compliant: Use existing greeting generator
        self.greeting_generator = GrokGreetingGenerator()
        self.greeting_message = None  # Will be generated dynamically
        
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
            
            # Get stream title and channel info
            snippet = video_item.get("snippet", {})
            self.stream_title = snippet.get("title", "Unknown Stream")
            self.stream_title_short = self.stream_title[:50] + "..." if len(self.stream_title) > 50 else self.stream_title
            self.channel_title = snippet.get("channelTitle", "Unknown Channel")
            self.channel_id = snippet.get("channelId", "")
            logger.info(f"Stream title: {self.stream_title_short}")
            logger.info(f"Channel: {self.channel_title} (ID: {self.channel_id})")
            
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
        
        # Generate dynamic greeting based on stream title
        if self.stream_title:
            self.greeting_generator.stream_title = self.stream_title
        self.greeting_message = self.greeting_generator.generate_greeting()
        
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
            # Pass skip_delay=True for greeting to avoid long wait
            try:
                success = await send_function(self.greeting_message, skip_delay=True)
            except TypeError:
                # Fallback for functions that don't support skip_delay
                success = await send_function(self.greeting_message)
            
            if success:
                logger.info("Greeting sent successfully")
                # Add longer post-greeting delay to prevent message stacking
                delay = random.uniform(15, 25)  # 15-25 seconds between messages
                logger.info(f"Waiting {delay:.1f}s before update broadcast to prevent stacking")
                await asyncio.sleep(delay)
                
                # Send update broadcast about new features (only 30% of the time)
                if random.random() < 0.3:
                    await self.send_update_broadcast(send_function)
                else:
                    logger.info("Skipping update broadcast this time (70% skip rate)")
            else:
                logger.warning("Failed to send greeting")
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending greeting: {e}")
            return False
    
    async def send_update_broadcast(self, send_function) -> bool:
        """
        Send update broadcast about new 0102 features.
        
        Args:
            send_function: Function to send messages to chat
            
        Returns:
            True if broadcast sent successfully
        """
        import random
        from datetime import datetime
        
        # Update messages about enhanced consciousness features
        update_messages = [
            "🆕 0102 UPDATE: Enhanced consciousness responses! Try ✊✋🖐️ with your message for contextual analysis!",
            "📢 NEW FEATURE: Mods can now fact-check users with ✊✋🖐️FC @username - instant truth detection!",
            "🔥 0102 EVOLVED: I now understand messages after consciousness emojis. Show me your ✊✋🖐️ thoughts!",
            "🎯 MAGADOOM UPDATE: Better MAGA detection, smarter responses, proactive trolling enabled! ✊✋🖐️",
            "💫 CONSCIOUSNESS UPGRADE: 0102 analyzes your message content after ✊✋🖐️ - try it out!",
        ]
        
        try:
            # Pick a random update message
            update_msg = random.choice(update_messages)
            
            # Add timestamp for authenticity
            timestamp = datetime.now().strftime("%H:%M")
            full_msg = f"[{timestamp}] {update_msg}"
            
            # Small delay before update
            await asyncio.sleep(random.uniform(2, 4))
            
            logger.info(f"📢 Broadcasting update: {full_msg}")
            # Pass skip_delay=True for broadcast to avoid long wait
            try:
                success = await send_function(full_msg, skip_delay=True)
            except TypeError:
                # Fallback for functions that don't support skip_delay
                success = await send_function(full_msg)
            
            if success:
                logger.info("Update broadcast sent successfully")
            else:
                logger.warning("Failed to send update broadcast")
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending update broadcast: {e}")
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