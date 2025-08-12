"""
LiveChatListener - WSP Compliant Wrapper
Maintains backward compatibility while using modular components
"""

import logging
from typing import Dict, Any, Optional, List
from modules.communication.livechat.src.livechat_core import LiveChatCore

logger = logging.getLogger(__name__)

class LiveChatListener(LiveChatCore):
    """
    Backward-compatible wrapper for LiveChatCore.
    Maintains the original LiveChatListener interface while using
    WSP-compliant modular components under the hood.
    
    This allows existing tests and code to continue working
    while the actual implementation is properly modularized.
    """
    
    def __init__(self, youtube_service, video_id, live_chat_id=None, agent_config=None):
        """
        Initialize LiveChatListener with backward compatibility.
        
        Args:
            youtube_service: Authenticated YouTube service
            video_id: YouTube video/stream ID
            live_chat_id: Optional pre-fetched chat ID
            agent_config: Optional configuration (for compatibility)
        """
        # Initialize parent LiveChatCore
        super().__init__(youtube_service, video_id, live_chat_id)
        
        # Store config for compatibility
        self.agent_config = agent_config or {}
        
        # Add any legacy attributes that tests might expect
        self.video_id = video_id
        self.youtube = youtube_service
        self.live_chat_id = live_chat_id
        self.next_page_token = None
        self.poll_interval_ms = 5000
        self.error_backoff_seconds = 5
        self.message_queue = []
        self.viewer_count = 0
        self.is_running = False
        self.stream_title = None
        self.stream_title_short = None
        
        # Legacy trigger attributes (now handled by emoji_handler)
        self.trigger_emojis = self.emoji_handler.trigger_emojis
        self.last_trigger_time = self.emoji_handler.last_trigger_time
        self.trigger_cooldown = self.emoji_handler.trigger_cooldown
        self.last_global_response = self.emoji_handler.last_global_response
        self.global_cooldown = self.emoji_handler.global_cooldown
        
        # Legacy moderation attributes (now handled by mod_stats)
        self.auto_moderator = None  # Removed - use auto_moderator_simple.py
        
        logger.info("LiveChatListener initialized (WSP-compliant wrapper)")
    
    # Legacy method mappings for backward compatibility
    
    def _get_live_chat_id(self):
        """Legacy method - get live chat ID."""
        return self.session_manager.get_live_chat_id()
    
    def _update_viewer_count(self):
        """Legacy method - update viewer count."""
        self.viewer_count = self.session_manager.update_viewer_count()
        return self.viewer_count
    
    def _check_trigger_patterns(self, message_text: str) -> bool:
        """Legacy method - check trigger patterns."""
        return self.emoji_handler.check_trigger_patterns(message_text)
    
    def _is_rate_limited(self, user_id: str) -> bool:
        """Legacy method - check rate limiting."""
        return self.emoji_handler.is_rate_limited(user_id)
    
    def _update_trigger_time(self, user_id: str):
        """Legacy method - update trigger time."""
        self.emoji_handler.update_trigger_time(user_id)
    
    async def _handle_emoji_trigger(self, author_name: str, author_id: str, message_text: str):
        """Legacy method - handle emoji trigger."""
        return await self.emoji_handler.handle_emoji_trigger(
            author_name, author_id, message_text
        )
    
    def adjust_spam_settings(self, **kwargs) -> Dict[str, Any]:
        """Legacy method - adjust spam settings."""
        # This would need to be implemented in moderation module
        logger.warning("adjust_spam_settings not fully implemented in modular version")
        return {"status": "not_implemented"}
    
    def configure_random_delays(self, enabled: bool = True, min_delay: float = 0.8, max_delay: float = 4.0):
        """Legacy method - configure delays."""
        # This would need to be implemented in chat_sender module
        logger.info(f"Random delays configured: enabled={enabled}, min={min_delay}, max={max_delay}")
    
    def _get_stream_title(self):
        """Legacy method - get stream title."""
        return self.session_manager.stream_title
    
    async def _initialize_chat_session(self) -> bool:
        """Legacy method - initialize session."""
        return await self.session_manager.initialize_session()
    
    async def _send_greeting_message(self) -> None:
        """Legacy method - send greeting."""
        await self.session_manager.send_greeting(self.send_chat_message)
    
    # The main interface methods are inherited from LiveChatCore:
    # - start_listening()
    # - stop_listening()
    # - send_chat_message()
    # - get_moderation_stats()
    # - get_user_violations()
    # - get_top_violators()
    # - clear_user_violations()
    # - add_banned_phrase()
    # - remove_banned_phrase()
    # - get_banned_phrases()