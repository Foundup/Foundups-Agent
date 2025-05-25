"""
Chat Sender Component

Handles sending messages to YouTube Live Chat.
Separated from the main LiveChatListener for better maintainability.
"""

import logging
import asyncio
from typing import Optional
import googleapiclient.errors

logger = logging.getLogger(__name__)

class ChatSender:
    """Handles sending messages to YouTube Live Chat."""
    
    def __init__(self, youtube_service, live_chat_id):
        self.youtube = youtube_service
        self.live_chat_id = live_chat_id
        self.bot_channel_id = None
        self.send_delay = 2.0  # Delay between sends to avoid rate limiting
        
    async def send_message(self, message_text: str) -> bool:
        """
        Send a message to the live chat.
        
        Args:
            message_text: The message to send
            
        Returns:
            True if message was sent successfully, False otherwise
        """
        if not message_text or not message_text.strip():
            logger.warning("⚠️ Cannot send empty message")
            return False
        
        try:
            # Ensure we have bot channel ID
            if not self.bot_channel_id:
                await self._get_bot_channel_id()
            
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
            
            # Add delay to avoid rate limiting
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
            "has_service": self.youtube is not None
        } 