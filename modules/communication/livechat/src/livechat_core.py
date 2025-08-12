"""
LiveChat Core - WSP Compliant Module (<500 lines)
Core YouTube Live Chat listener using modular components
"""

import logging
import os
import time
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, List
import googleapiclient.errors

# Import WSP-compliant modules
from modules.communication.livechat.src.emoji_trigger_handler import EmojiTriggerHandler
from modules.communication.livechat.src.moderation_stats import ModerationStats
from modules.communication.livechat.src.session_manager import SessionManager
from modules.communication.livechat.src.message_processor import MessageProcessor
from modules.communication.livechat.src.chat_sender import ChatSender
from modules.communication.livechat.src.chat_poller import ChatPoller

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
MAX_MESSAGES_PER_CALL = 200

class LiveChatCore:
    """
    Core YouTube Live Chat listener - WSP compliant version.
    Uses modular components for functionality.
    """
    
    def __init__(self, youtube_service, video_id: str, live_chat_id: Optional[str] = None):
        """
        Initialize LiveChatCore with modular components.
        
        Args:
            youtube_service: Authenticated YouTube service
            video_id: YouTube video/stream ID
            live_chat_id: Optional pre-fetched chat ID
        """
        self.youtube = youtube_service
        self.video_id = video_id
        self.live_chat_id = live_chat_id
        self.next_page_token = None
        self.is_running = False
        self.memory_dir = "memory"
        self.processed_message_ids = set()
        
        # Initialize modular components
        self.session_manager = SessionManager(youtube_service, video_id)
        self.emoji_handler = EmojiTriggerHandler()
        self.mod_stats = ModerationStats(self.memory_dir)
        self.message_processor = MessageProcessor()
        self.chat_sender = ChatSender(youtube_service)
        self.chat_poller = ChatPoller(youtube_service)
        
        # Ensure memory directory exists
        os.makedirs(self.memory_dir, exist_ok=True)
        logger.info(f"LiveChatCore initialized for video: {video_id}")
    
    async def initialize(self) -> bool:
        """
        Initialize the chat session.
        
        Returns:
            True if initialization successful
        """
        # Initialize session
        if not await self.session_manager.initialize_session():
            logger.error("Failed to initialize session")
            return False
        
        # Get chat ID from session manager
        self.live_chat_id = self.session_manager.live_chat_id
        self.chat_sender.live_chat_id = self.live_chat_id
        self.chat_poller.live_chat_id = self.live_chat_id
        
        # Send greeting
        await self.session_manager.send_greeting(self.send_chat_message)
        
        logger.info("LiveChatCore initialized successfully")
        return True
    
    async def send_chat_message(self, message_text: str) -> bool:
        """
        Send a message to the live chat.
        
        Args:
            message_text: Message to send
            
        Returns:
            True if message sent successfully
        """
        if not self.live_chat_id:
            logger.error("Cannot send message - no live chat ID")
            return False
        
        return await self.chat_sender.send_message(self.live_chat_id, message_text)
    
    async def poll_messages(self) -> tuple:
        """
        Poll for new chat messages.
        
        Returns:
            Tuple of (messages list, poll interval in ms)
        """
        try:
            response = await self.chat_poller.poll_once(
                self.live_chat_id,
                self.next_page_token
            )
            
            if response:
                messages = response.get("items", [])
                self.next_page_token = response.get("nextPageToken")
                poll_interval = response.get("pollingIntervalMillis", 5000)
                return messages, poll_interval
            
            return [], 5000
            
        except Exception as e:
            logger.error(f"Error polling messages: {e}")
            return [], 5000
    
    async def process_message(self, message: Dict[str, Any]) -> None:
        """
        Process a single chat message.
        
        Args:
            message: Message data from YouTube API
        """
        try:
            # Extract message details
            message_id = message.get("id", "")
            
            # Skip if already processed
            if message_id in self.processed_message_ids:
                return
            
            self.processed_message_ids.add(message_id)
            
            # Get message content
            snippet = message.get("snippet", {})
            author_details = message.get("authorDetails", {})
            
            display_message = snippet.get("displayMessage", "")
            author_name = author_details.get("displayName", "Unknown")
            author_id = author_details.get("channelId", "")
            is_moderator = author_details.get("isChatModerator", False)
            is_owner = author_details.get("isChatOwner", False)
            
            # Log the message
            logger.debug(f"[{author_name}]: {display_message}")
            
            # Update stats
            self.mod_stats.record_message()
            
            # Skip moderation for mods/owners
            if is_moderator or is_owner:
                logger.debug(f"Skipping moderation for mod/owner: {author_name}")
            else:
                # Check for violations (implement as needed)
                pass
            
            # Check for emoji triggers
            if self.emoji_handler.check_trigger_patterns(display_message):
                response = await self.emoji_handler.handle_emoji_trigger(
                    author_name,
                    author_id,
                    display_message
                )
                
                if response:
                    await self.send_chat_message(response)
            
            # Log to user file
            self._log_to_user_file(message)
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def _log_to_user_file(self, message: Dict[str, Any]) -> None:
        """
        Log message to user-specific file.
        
        Args:
            message: Message data
        """
        try:
            author_details = message.get("authorDetails", {})
            snippet = message.get("snippet", {})
            
            author_name = author_details.get("displayName", "Unknown")
            display_message = snippet.get("displayMessage", "")
            published_at = snippet.get("publishedAt", "")
            
            # Create safe filename
            safe_name = "".join(c for c in author_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            if not safe_name:
                safe_name = "Unknown"
            
            # Write to user file
            user_file = os.path.join(self.memory_dir, f"{safe_name}.txt")
            with open(user_file, "a", encoding="utf-8") as f:
                f.write(f"[{published_at}] {author_name}: {display_message}\n")
            
        except Exception as e:
            logger.error(f"Error logging to user file: {e}")
    
    async def process_message_batch(self, messages: List[Dict[str, Any]]) -> None:
        """
        Process a batch of messages.
        
        Args:
            messages: List of messages to process
        """
        for message in messages:
            await self.process_message(message)
    
    async def run_polling_loop(self) -> None:
        """Run the main polling loop."""
        poll_interval_ms = 5000
        
        while self.is_running:
            try:
                # Poll for messages
                messages, poll_interval_ms = await self.poll_messages()
                
                # Process messages
                if messages:
                    logger.info(f"Processing {len(messages)} messages")
                    await self.process_message_batch(messages)
                
                # Update viewer count periodically
                if time.time() % 60 < 1:  # Every minute
                    self.session_manager.update_viewer_count()
                
                # Wait before next poll
                sleep_time = max(poll_interval_ms / 1000.0, 1.0)
                await asyncio.sleep(sleep_time)
                
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt - stopping")
                self.is_running = False
            except Exception as e:
                logger.error(f"Error in polling loop: {e}")
                await asyncio.sleep(5)
    
    async def start_listening(self) -> None:
        """Start listening to chat messages."""
        if self.is_running:
            logger.warning("Already listening")
            return
        
        logger.info("Starting LiveChatCore...")
        
        # Initialize session
        if not await self.initialize():
            logger.error("Failed to initialize - cannot start")
            return
        
        # Start polling
        self.is_running = True
        
        try:
            await self.run_polling_loop()
        finally:
            self.stop_listening()
    
    def stop_listening(self) -> None:
        """Stop listening to chat messages."""
        if not self.is_running:
            return
        
        logger.info("Stopping LiveChatCore...")
        self.is_running = False
        self.session_manager.end_session()
        
        # Save stats
        logger.info("Final stats:")
        logger.info(self.mod_stats.get_moderation_stats())
        logger.info(self.emoji_handler.get_stats())
    
    # Convenience methods for compatibility
    
    def get_moderation_stats(self) -> Dict[str, Any]:
        """Get moderation statistics."""
        return self.mod_stats.get_moderation_stats()
    
    def get_user_violations(self, user_id: str) -> Dict[str, Any]:
        """Get violations for a specific user."""
        return self.mod_stats.get_user_violations(user_id)
    
    def get_top_violators(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top violators."""
        return self.mod_stats.get_top_violators(limit)
    
    def clear_user_violations(self, user_id: str) -> bool:
        """Clear violations for a user."""
        return self.mod_stats.clear_user_violations(user_id)
    
    def add_banned_phrase(self, phrase: str) -> bool:
        """Add a banned phrase."""
        return self.mod_stats.add_banned_phrase(phrase)
    
    def remove_banned_phrase(self, phrase: str) -> bool:
        """Remove a banned phrase."""
        return self.mod_stats.remove_banned_phrase(phrase)
    
    def get_banned_phrases(self) -> List[str]:
        """Get list of banned phrases."""
        return self.mod_stats.get_banned_phrases()
    
    def configure_emoji_triggers(self, **kwargs) -> Dict[str, Any]:
        """Configure emoji trigger settings."""
        return self.emoji_handler.configure(**kwargs)