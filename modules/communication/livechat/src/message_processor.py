"""
Message Processor Component

Handles message processing, emoji detection, and response generation.
Separated from the main LiveChatListener for better maintainability.
"""

import logging
import time
import os
from typing import Dict, Any, Optional, List, Tuple
from modules.ai_intelligence.banter_engine.src.banter_engine import BanterEngine
from modules.communication.livechat.src.llm_bypass_engine import LLMBypassEngine
from modules.ai_intelligence.banter_engine.src.emoji_sequence_map import EMOJI_TO_NUMBER as EMOJI_TO_NUM

logger = logging.getLogger(__name__)

class MessageProcessor:
    """Handles processing of chat messages and generating responses."""
    
    def __init__(self):
        self.banter_engine = BanterEngine()
        self.llm_bypass_engine = LLMBypassEngine()
        self.trigger_emojis = ["✊", "✋", "🖐️"]  # Configurable emoji trigger set
        self.last_trigger_time = {}  # Track last trigger time per user
        self.trigger_cooldown = 60  # Cooldown period in seconds
        self.memory_dir = "memory"
        
        # Ensure memory directory exists
        os.makedirs(self.memory_dir, exist_ok=True)
        logger.info(f"📁 Memory directory set to: {self.memory_dir}")
    
    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single chat message and extract relevant information.
        
        Args:
            message: Raw message data from YouTube API
            
        Returns:
            Processed message data with additional metadata
        """
        try:
            snippet = message.get("snippet", {})
            author_details = message.get("authorDetails", {})
            
            # Extract basic message info
            message_id = snippet.get("messageId", "")
            message_text = snippet.get("displayMessage", "")
            author_name = author_details.get("displayName", "Unknown")
            author_id = author_details.get("channelId", "")
            published_at = snippet.get("publishedAt", "")
            
            # Check for emoji triggers
            has_trigger = self._check_trigger_patterns(message_text)
            is_rate_limited = self._is_rate_limited(author_id) if has_trigger else False
            
            processed_message = {
                "message_id": message_id,
                "text": message_text,
                "author_name": author_name,
                "author_id": author_id,
                "published_at": published_at,
                "has_trigger": has_trigger,
                "is_rate_limited": is_rate_limited,
                "raw_message": message
            }
            
            logger.debug(f"📝 Processed message from {author_name}: {message_text[:50]}...")
            return processed_message
            
        except Exception as e:
            logger.error(f"❌ Error processing message: {e}")
            return {
                "message_id": "",
                "text": "",
                "author_name": "Unknown",
                "author_id": "",
                "published_at": "",
                "has_trigger": False,
                "is_rate_limited": False,
                "raw_message": message,
                "error": str(e)
            }
    
    def _check_trigger_patterns(self, message_text: str) -> bool:
        """
        Check if message contains emoji trigger patterns.
        
        Args:
            message_text: The message text to check
            
        Returns:
            True if trigger patterns are found, False otherwise
        """
        if not message_text:
            return False
        
        # Check for individual trigger emojis
        for emoji in self.trigger_emojis:
            if emoji in message_text:
                logger.debug(f"🎯 Trigger emoji '{emoji}' found in message")
                return True
        
        # Check for 3-emoji sequences
        emoji_count = sum(message_text.count(emoji) for emoji in self.trigger_emojis)
        if emoji_count >= 3:
            logger.debug(f"🎯 Multiple trigger emojis found ({emoji_count})")
            return True
        
        return False
    
    async def generate_response(self, processed_message: Dict[str, Any]) -> Optional[str]:
        """
        Generate a response to a processed message.
        
        Args:
            processed_message: Processed message data
            
        Returns:
            Response text or None if no response should be generated
        """
        if not processed_message.get("has_trigger"):
            return None
        
        if processed_message.get("is_rate_limited"):
            logger.debug(f"⏳ User {processed_message['author_name']} is rate limited")
            return None
        
        message_text = processed_message.get("text", "")
        author_name = processed_message.get("author_name", "Unknown")
        author_id = processed_message.get("author_id", "")
        
        try:
            # Update trigger time for rate limiting
            self._update_trigger_time(author_id)
            
            # Try banter engine first
            response = await self._generate_banter_response(message_text, author_name)
            
            if response:
                logger.info(f"🎭 Generated banter response for {author_name}")
                return response
            
            # Fallback to LLM bypass engine
            response = await self._generate_fallback_response(message_text, author_name)
            
            if response:
                logger.info(f"🔄 Generated fallback response for {author_name}")
                return response
            
            logger.warning(f"⚠️ No response generated for {author_name}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error generating response for {author_name}: {e}")
            return None
    
    async def _generate_banter_response(self, message_text: str, author_name: str) -> Optional[str]:
        """Generate response using the banter engine."""
        try:
            state_info, response = self.banter_engine.process_input(message_text)
            
            if response:
                # Personalize the response
                personalized_response = f"@{author_name} {response}"
                logger.debug(f"🎭 Banter engine response: {state_info}")
                return personalized_response
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Banter engine error: {e}")
            return None
    
    async def _generate_fallback_response(self, message_text: str, author_name: str) -> Optional[str]:
        """Generate response using the fallback LLM bypass engine."""
        try:
            response = await self.llm_bypass_engine.generate_response(message_text)
            
            if response:
                # Personalize the response
                personalized_response = f"@{author_name} {response}"
                logger.debug(f"🔄 Fallback response generated")
                return personalized_response
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Fallback engine error: {e}")
            return None
    
    def _is_rate_limited(self, user_id: str) -> bool:
        """
        Check if a user is rate limited from triggering gestures.
        
        Args:
            user_id: The user's ID
            
        Returns:
            True if user is rate limited, False otherwise
        """
        current_time = time.time()
        if user_id in self.last_trigger_time:
            time_since_last = current_time - self.last_trigger_time[user_id]
            if time_since_last < self.trigger_cooldown:
                logger.debug(f"⏳ Rate limited user {user_id} for {self.trigger_cooldown - time_since_last:.1f}s")
                return True
        return False
    
    def _update_trigger_time(self, user_id: str):
        """Update the last trigger time for a user."""
        self.last_trigger_time[user_id] = time.time()
        logger.debug(f"⏰ Updated trigger time for user {user_id}")
    
    def log_message_to_file(self, processed_message: Dict[str, Any]):
        """
        Log message to user-specific file.
        
        Args:
            processed_message: Processed message data
        """
        try:
            author_name = processed_message.get("author_name", "Unknown")
            message_text = processed_message.get("text", "")
            published_at = processed_message.get("published_at", "")
            
            # Create safe filename
            safe_author_name = "".join(c for c in author_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            if not safe_author_name:
                safe_author_name = "Unknown"
            
            user_file = os.path.join(self.memory_dir, f"{safe_author_name}.txt")
            
            with open(user_file, "a", encoding="utf-8") as f:
                f.write(f"[{published_at}] {author_name}: {message_text}\n")
            
            logger.debug(f"📝 Logged message to {user_file}")
            
        except Exception as e:
            logger.error(f"❌ Error logging message to file: {e}")
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        return {
            "trigger_cooldown": self.trigger_cooldown,
            "active_users": len(self.last_trigger_time),
            "trigger_emojis": self.trigger_emojis,
            "memory_dir": self.memory_dir
        } 