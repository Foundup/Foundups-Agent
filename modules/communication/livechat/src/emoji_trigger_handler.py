"""
Emoji Trigger Handler - WSP Compliant Module
Handles emoji detection and response generation for ✊✋🖐️ triggers
"""

import logging
import time
import random
import os
import sys
from typing import Dict, Optional, Any
from modules.ai_intelligence.banter_engine.src.banter_engine import BanterEngine
from modules.communication.livechat.src.llm_bypass_engine import LLMBypassEngine

# Import activity control system
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))
try:
    from modules.infrastructure.activity_control.src.activity_control import is_enabled
except ImportError:
    # Fallback for testing - default to enabled
    def is_enabled(activity): return True

logger = logging.getLogger(__name__)

class EmojiTriggerHandler:
    """
    Handles emoji trigger detection and response generation.
    Separated from LiveChatListener for WSP compliance.
    """
    
    def __init__(self):
        self.banter_engine = BanterEngine()
        self.llm_bypass_engine = LLMBypassEngine()
        self.trigger_emojis = ["✊", "✋", "🖐️"]
        self.last_trigger_time = {}  # Track last trigger time per user
        
        # Dynamic cooldown from live_chat_processor
        self.MIN_TRIGGER_COOLDOWN = 15  # Minimum cooldown
        self.MAX_TRIGGER_COOLDOWN = 45  # Maximum cooldown
        self.trigger_cooldown = self._get_new_cooldown()  # Random cooldown
        
        self.last_global_response = 0  # Track last response time globally
        self.global_cooldown = 5  # Minimum 5 seconds between any responses
        
        logger.info(f"EmojiTriggerHandler initialized with triggers: {self.trigger_emojis}, cooldown: {self.trigger_cooldown:.1f}s")
    
    def _get_new_cooldown(self) -> float:
        """
        Generate a new random cooldown time (from live_chat_processor).
        
        Returns:
            float: Random cooldown time in seconds
        """
        return random.uniform(self.MIN_TRIGGER_COOLDOWN, self.MAX_TRIGGER_COOLDOWN)
    
    def check_trigger_patterns(self, message_text: str) -> bool:
        """
        Check if message contains emoji trigger patterns.
        
        Args:
            message_text: The message text to check
            
        Returns:
            True if trigger patterns are found, False otherwise
        """
        if not message_text:
            return False
        
        # Check for the specific 3-emoji sequence
        trigger_sequence = ["✊", "✋", "🖐️"]
        if all(emoji in message_text for emoji in trigger_sequence):
            logger.debug(f"Found complete trigger sequence in: {message_text}")
            return True
        
        # Also check for individual triggers (configurable)
        for emoji in self.trigger_emojis:
            if emoji in message_text:
                logger.debug(f"Found trigger emoji '{emoji}' in message")
                return True
        
        return False
    
    def is_rate_limited(self, user_id: str) -> bool:
        """
        Check if a user is rate limited from triggering responses.
        
        Args:
            user_id: The user's ID
            
        Returns:
            True if user is rate limited, False otherwise
        """
        current_time = time.time()
        
        # Check global cooldown
        if current_time - self.last_global_response < self.global_cooldown:
            logger.debug(f"Global cooldown active, {self.global_cooldown - (current_time - self.last_global_response):.1f}s remaining")
            return True
        
        # Check per-user cooldown
        if user_id in self.last_trigger_time:
            time_since_last = current_time - self.last_trigger_time[user_id]
            if time_since_last < self.trigger_cooldown:
                logger.debug(f"User {user_id} rate limited for {self.trigger_cooldown - time_since_last:.1f}s")
                return True
        
        return False
    
    def update_trigger_time(self, user_id: str):
        """Update the last trigger time for a user."""
        current_time = time.time()
        self.last_trigger_time[user_id] = current_time
        self.last_global_response = current_time
        # Get new random cooldown (from live_chat_processor)
        self.trigger_cooldown = self._get_new_cooldown()
        logger.debug(f"Updated trigger time for user {user_id}, next cooldown: {self.trigger_cooldown:.1f}s")
    
    async def handle_emoji_trigger(self, author_name: str, author_id: str, message_text: str) -> Optional[str]:
        """
        Handle emoji trigger and generate response.
        
        Args:
            author_name: Name of the message author
            author_id: ID of the message author
            message_text: The message text containing triggers
            
        Returns:
            Response message or None if rate limited
        """
        # Check if emoji triggers are enabled
        if not is_enabled("livechat.consciousness.emoji_triggers"):
            logger.debug("Emoji triggers are disabled by activity control")
            return None
            
        # Check if user is rate limited
        if self.is_rate_limited(author_id):
            return None
        
        try:
            # Update trigger time
            self.update_trigger_time(author_id)
            
            # Try banter engine first
            state_info, response = self.banter_engine.process_input(message_text)
            
            if response and response != "...silence...":
                logger.info(f"Banter engine generated response for {author_name}: {response}")
                return f"@{author_name} {response}"
            
            # Fallback to LLM bypass engine
            logger.debug("Banter engine had no response, trying LLM bypass")
            response = await self.llm_bypass_engine.generate_response(message_text)
            
            if response:
                logger.info(f"LLM bypass generated response for {author_name}: {response}")
                return f"@{author_name} {response}"
            
            # Final fallback
            logger.warning(f"No response generated for trigger from {author_name}")
            return None
            
        except Exception as e:
            logger.error(f"Error handling emoji trigger: {e}")
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about emoji triggers."""
        return {
            "trigger_emojis": self.trigger_emojis,
            "trigger_cooldown": self.trigger_cooldown,
            "global_cooldown": self.global_cooldown,
            "active_users": len(self.last_trigger_time),
            "last_global_response": self.last_global_response
        }
    
    def configure(self, **kwargs) -> Dict[str, Any]:
        """
        Configure trigger handler settings.
        
        Args:
            trigger_emojis: List of trigger emojis
            trigger_cooldown: Per-user cooldown in seconds
            global_cooldown: Global cooldown in seconds
            
        Returns:
            Updated configuration
        """
        if "trigger_emojis" in kwargs:
            self.trigger_emojis = kwargs["trigger_emojis"]
            logger.info(f"Updated trigger emojis: {self.trigger_emojis}")
        
        if "trigger_cooldown" in kwargs:
            self.trigger_cooldown = kwargs["trigger_cooldown"]
            logger.info(f"Updated trigger cooldown: {self.trigger_cooldown}s")
        
        if "global_cooldown" in kwargs:
            self.global_cooldown = kwargs["global_cooldown"]
            logger.info(f"Updated global cooldown: {self.global_cooldown}s")
        
        return self.get_stats()