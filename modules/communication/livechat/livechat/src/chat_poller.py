"""
Chat Poller Component

Handles YouTube Live Chat API polling and message retrieval.
Separated from the main LiveChatListener for better maintainability.
"""

import logging
import time
import asyncio
from typing import List, Dict, Any, Optional
import googleapiclient.errors
from utils.throttling import calculate_dynamic_delay

logger = logging.getLogger(__name__)

class ChatPoller:
    """Handles polling YouTube Live Chat API for new messages."""
    
    def __init__(self, youtube_service, live_chat_id):
        self.youtube = youtube_service
        self.live_chat_id = live_chat_id
        self.next_page_token = None
        self.poll_interval_ms = 10000  # Default: 10 seconds
        self.error_backoff_seconds = 5  # Initial backoff for errors
        self.max_backoff_seconds = 60  # Maximum backoff time
        
    async def poll_messages(self, viewer_count: int = 100) -> List[Dict[str, Any]]:
        """
        Poll the YouTube API for new chat messages.
        
        Args:
            viewer_count: Current viewer count for dynamic delay calculation
            
        Returns:
            List of new chat messages
        """
        try:
            logger.debug(f"🔄 Polling chat messages for live chat ID: {self.live_chat_id}")
            
            response = await self._make_api_call()
            
            # Update polling interval based on server response
            self._update_polling_interval(response, viewer_count)
            
            # Reset error backoff on success
            self.error_backoff_seconds = 5
            
            messages = response.get("items", [])
            if messages:
                logger.debug(f"📨 Received {len(messages)} new messages")
            else:
                logger.debug("📭 No new messages")
                
            return messages
            
        except googleapiclient.errors.HttpError as e:
            logger.error(f"❌ API Error polling messages: {e}")
            raise  # Let the caller handle auth errors
        except Exception as e:
            logger.error(f"❌ Unexpected error polling chat: {e}")
            await self._handle_polling_error()
            return []
    
    async def _make_api_call(self) -> Dict[str, Any]:
        """Make the actual API call to get chat messages."""
        return self.youtube.liveChatMessages().list(
            liveChatId=self.live_chat_id,
            part="snippet,authorDetails",
            pageToken=self.next_page_token
        ).execute()
    
    def _update_polling_interval(self, response: Dict[str, Any], viewer_count: int):
        """Update polling interval based on server response and viewer count."""
        # Get server's recommended polling interval
        server_poll_interval = response.get("pollingIntervalMillis", 10000)
        if not isinstance(server_poll_interval, int):
            server_poll_interval = 10000  # Safe default for mock mode
        
        # Calculate dynamic delay based on viewer count
        try:
            if isinstance(viewer_count, int):
                dynamic_delay = calculate_dynamic_delay(viewer_count)
            else:
                dynamic_delay = 10.0  # Safe default
        except Exception:
            dynamic_delay = 10.0  # Fallback delay
        
        # Use the larger of server's interval or our calculated interval
        self.poll_interval_ms = max(server_poll_interval, int(dynamic_delay * 1000))
        
        # Update next page token
        self.next_page_token = response.get("nextPageToken")
        
        logger.debug(f"⏱️ Updated poll interval: {self.poll_interval_ms}ms")
    
    async def _handle_polling_error(self):
        """Handle polling errors with exponential backoff."""
        logger.warning(f"⏳ Backing off for {self.error_backoff_seconds} seconds")
        await asyncio.sleep(self.error_backoff_seconds)
        
        # Exponential backoff with maximum limit
        self.error_backoff_seconds = min(self.error_backoff_seconds * 2, self.max_backoff_seconds)
    
    def get_poll_interval_seconds(self) -> float:
        """Get the current polling interval in seconds."""
        return self.poll_interval_ms / 1000.0
    
    def reset_polling_state(self):
        """Reset polling state (useful after reconnection)."""
        self.next_page_token = None
        self.error_backoff_seconds = 5
        logger.info("🔄 Polling state reset") 