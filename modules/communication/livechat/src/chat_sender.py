"""
Chat Sender Component

Handles sending messages to YouTube Live Chat.
Separated from the main LiveChatListener for better maintainability.

WSP Enhancement: Added random response delays for human-like behavior (v1.1)
"""

import logging
import asyncio
import random
from typing import Optional
import googleapiclient.errors
from modules.communication.livechat.src.throttle_manager import ThrottleManager

logger = logging.getLogger(__name__)

class ChatSender:
    """Handles sending messages to YouTube Live Chat with human-like random delays."""
    
    def __init__(self, youtube_service, live_chat_id=None):
        self.youtube = youtube_service
        self.live_chat_id = live_chat_id
        self.bot_channel_id = None
        self.send_delay = 2.0  # Base delay between sends to avoid rate limiting
        
        # WSP Enhancement: Random delay configuration for human-like behavior
        self.random_delay_enabled = True
        self.min_random_delay = 0.5  # Minimum random delay (seconds)
        self.max_random_delay = 3.0  # Maximum random delay (seconds)
        
        # Adaptive throttle manager
        self.throttle = ThrottleManager()
        
    async def send_message(self, message_text: str, response_type: str = 'general', skip_delay: bool = False) -> bool:
        """
        Send a message to the live chat with adaptive throttling.
        
        Args:
            message_text: The message to send
            response_type: Type of response (consciousness, factcheck, maga, general)
            skip_delay: If True, skip the adaptive delay (for greetings/broadcasts)
            
        Returns:
            True if message was sent successfully, False otherwise
        """
        if not message_text or not message_text.strip():
            logger.warning("⚠️ Cannot send empty message")
            return False
        
        # Check throttling (skip for consciousness commands and timeout announcements)
        if response_type not in ['consciousness', 'timeout_announcement'] and not self.throttle.should_respond(response_type):
            logger.info(f"⏰ Throttled {response_type} response (chat too active)")
            return False
        
        try:
            # Ensure we have bot channel ID
            if not self.bot_channel_id:
                await self._get_bot_channel_id()
            
            # Adaptive delay based on chat activity (skip for greetings/broadcasts/consciousness/timeouts)
            if not skip_delay and response_type not in ['consciousness', 'timeout_announcement']:
                adaptive_delay = self.throttle.calculate_adaptive_delay()
                logger.info(f"⏱️ Adaptive delay: {adaptive_delay:.2f}s based on chat activity")
                await asyncio.sleep(adaptive_delay)
            else:
                if response_type == 'consciousness':
                    logger.info("⚡ Skipping adaptive delay for consciousness trigger response")
                elif response_type == 'timeout_announcement':
                    logger.info("⚡🎮 PRIORITY: Skipping ALL delays for timeout announcement!")
                else:
                    logger.info("⚡ Skipping adaptive delay for greeting/broadcast")
            
            # WSP Enhancement: Add random pre-send delay for human-like behavior
            # Skip for timeout announcements (highest priority)
            if self.random_delay_enabled and response_type != 'timeout_announcement':
                random_delay = random.uniform(self.min_random_delay, self.max_random_delay)
                logger.debug(f"⏱️ Additional random delay: {random_delay:.2f}s")
                await asyncio.sleep(random_delay)
            
            logger.info(f"📤 Sending message: {message_text}")
            
            # Prepare message data
            message_data = {
                "snippet": {
                    "liveChatId": self.live_chat_id,
                    "type": "textMessageEvent",
                    "textMessageDetails": {
                        "messageText": message_text
                    }
                }
            }
            
            # Send the message
            response = self.youtube.liveChatMessages().insert(
                part="snippet",
                body=message_data
            ).execute()
            
            message_id = response.get("id", "unknown")
            logger.info(f"✅ Message sent successfully (ID: {message_id})")
            
            # Record response for throttling
            self.throttle.record_response(response_type)
            
            # Add base delay to avoid rate limiting
            await asyncio.sleep(self.send_delay)
            
            return True
            
        except googleapiclient.errors.HttpError as e:
            error_details = str(e)
            
            if "quotaExceeded" in error_details or "quota" in error_details.lower():
                logger.error(f"📊 Quota exceeded while sending message: {e}")
            elif "forbidden" in error_details.lower():
                logger.error(f"🚫 Forbidden error sending message (check permissions): {e}")
            elif "unauthorized" in error_details.lower():
                logger.error(f"🔐 Unauthorized error sending message: {e}")
                raise  # Let caller handle auth errors
            else:
                logger.error(f"❌ HTTP error sending message: {e}")
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Unexpected error sending message: {e}")
            return False
    
    def configure_random_delays(self, enabled: bool = True, min_delay: float = 0.5, max_delay: float = 3.0):
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
    
    async def send_greeting(self, greeting_message: str) -> bool:
        """
        Send a greeting message to the chat.
        
        Args:
            greeting_message: The greeting message to send
            
        Returns:
            True if greeting was sent successfully, False otherwise
        """
        logger.info("👋 Sending greeting message to chat")
        
        if not greeting_message:
            greeting_message = "FoundUps Agent reporting in! 🤖"
        
        success = await self.send_message(greeting_message)
        
        if success:
            logger.info("✅ Greeting message sent successfully")
        else:
            logger.warning("⚠️ Failed to send greeting message")
        
        return success
    
    async def _get_bot_channel_id(self) -> Optional[str]:
        """Get the bot's channel ID for message sending."""
        try:
            logger.debug("🔍 Fetching bot channel ID")
            
            response = self.youtube.channels().list(
                part="id",
                mine=True
            ).execute()
            
            items = response.get("items", [])
            if items:
                self.bot_channel_id = items[0]["id"]
                logger.info(f"🤖 Bot channel ID: {self.bot_channel_id}")
                return self.bot_channel_id
            else:
                logger.error("❌ No channel found for authenticated user")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error getting bot channel ID: {e}")
            return None
    
    def update_youtube_service(self, new_service):
        """
        Update the YouTube service (useful after token rotation).
        
        Args:
            new_service: New authenticated YouTube service
        """
        self.youtube = new_service
        self.bot_channel_id = None  # Reset channel ID to refetch with new service
        logger.info("🔄 YouTube service updated")
    
    def get_sender_stats(self) -> dict:
        """Get sender statistics and status."""
        return {
            "live_chat_id": self.live_chat_id,
            "bot_channel_id": self.bot_channel_id,
            "send_delay": self.send_delay,
            "random_delay_enabled": self.random_delay_enabled,
            "random_delay_range": f"{self.min_random_delay:.1f}s-{self.max_random_delay:.1f}s",
            "has_service": self.youtube is not None
        } 