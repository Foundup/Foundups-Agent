"""
Comment Monitor DAE - WSP 27/80 Compliant
Autonomous YouTube comment monitoring and response system
Runs alongside livechat for real-time comment engagement
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import googleapiclient.errors

from modules.platform_integration.youtube_auth.src.youtube_auth import (
    list_video_comments, 
    reply_to_comment,
    get_latest_video_id
)
from modules.communication.livechat.src.agentic_chat_engine import AgenticChatEngine
from modules.communication.livechat.src.chat_memory_manager import ChatMemoryManager

logger = logging.getLogger(__name__)

class CommentMonitorDAE:
    """
    WSP 27 Compliant DAE for YouTube Comments
    Phase -1: Signal (new comments detected)
    Phase 0: Knowledge (comment analysis)
    Phase 1: Protocol (response generation)
    Phase 2: Agentic (autonomous operation)
    """
    
    def __init__(self, youtube_service, channel_id: str, memory_dir: str = "memory"):
        """
        Initialize Comment Monitor DAE
        
        Args:
            youtube_service: Authenticated YouTube service
            channel_id: Channel ID to monitor (Move2Japan)
            memory_dir: Directory for memory persistence
        """
        self.youtube = youtube_service
        self.channel_id = channel_id
        self.memory_dir = memory_dir
        self.is_running = False
        
        # Track processed comments to avoid duplicates
        self.processed_comments = set()
        self.last_check_time = datetime.now()
        
        # Response generation
        self.chat_engine = AgenticChatEngine()
        self.memory_manager = ChatMemoryManager(memory_dir)
        
        # Polling intervals (in seconds)
        self.active_interval = 30  # When stream is active
        self.idle_interval = 300   # When no stream (5 minutes)
        self.current_interval = self.idle_interval
        
        # Quota management
        self.quota_used = 0
        self.quota_limit = 2000  # Reserve 2000 units for comments
        
        logger.info(f"CommentMonitorDAE initialized for channel: {channel_id}")
    
    async def start(self):
        """Start autonomous comment monitoring"""
        self.is_running = True
        logger.info("🤖 Comment Monitor DAE starting autonomous operation")
        
        while self.is_running:
            try:
                await self.monitor_cycle()
                await asyncio.sleep(self.current_interval)
            except Exception as e:
                logger.error(f"Comment monitor error: {e}")
                await asyncio.sleep(60)  # Wait before retry
    
    async def monitor_cycle(self):
        """Single monitoring cycle - check for new comments and respond"""
        try:
            # Phase -1: Signal - Get latest video
            video_id = await self.get_current_video()
            if not video_id:
                logger.debug("No video to monitor")
                self.current_interval = self.idle_interval
                return
            
            # Phase 0: Knowledge - Get comments
            comments = await self.fetch_new_comments(video_id)
            if not comments:
                return
            
            logger.info(f"📝 Found {len(comments)} new comments to process")
            
            # Phase 1: Protocol - Process each comment
            for comment in comments:
                if await self.should_respond(comment):
                    # Phase 2: Agentic - Generate and post response
                    await self.respond_to_comment(comment)
                    
                # Mark as processed
                self.processed_comments.add(comment['id'])
                
                # Rate limiting
                await asyncio.sleep(2)  # 2 seconds between responses
                
        except Exception as e:
            logger.error(f"Monitor cycle error: {e}")
    
    async def get_current_video(self) -> Optional[str]:
        """Get the current/latest video ID to monitor"""
        try:
            # Get latest video from channel
            video_id = get_latest_video_id(self.youtube, self.channel_id)
            return video_id
        except Exception as e:
            logger.error(f"Failed to get video ID: {e}")
            return None
    
    async def fetch_new_comments(self, video_id: str) -> List[Dict[str, Any]]:
        """Fetch comments that haven't been processed yet"""
        try:
            # Get comments from video
            comments = list_video_comments(self.youtube, video_id, max_results=50)
            
            # Filter out already processed
            new_comments = []
            for comment in comments:
                comment_id = comment['id']
                if comment_id not in self.processed_comments:
                    new_comments.append(comment)
            
            return new_comments
            
        except Exception as e:
            logger.error(f"Failed to fetch comments: {e}")
            return []
    
    async def should_respond(self, comment: Dict[str, Any]) -> bool:
        """
        Determine if 0102 should respond to this comment
        
        Criteria:
        - Contains a question
        - Mentions the bot or channel
        - Contains consciousness triggers
        - Is from a recognized user
        """
        text = comment.get('snippet', {}).get('textDisplay', '').lower()
        author = comment.get('snippet', {}).get('authorDisplayName', '')
        
        # Check for consciousness triggers
        if '✊✋🖐' in text:
            logger.info(f"🧠 Consciousness trigger detected from {author}")
            return True
        
        # Check for questions
        if any(q in text for q in ['?', 'why', 'how', 'what', 'when', 'where', 'who']):
            logger.info(f"❓ Question detected from {author}")
            return True
        
        # Check for mentions
        if any(mention in text for mention in ['0102', 'bot', '@undaodu', '@move2japan']):
            logger.info(f"📢 Mention detected from {author}")
            return True
        
        # Check memory for this user
        user_memory = self.memory_manager.get_user_memory(author)
        if user_memory and user_memory.get('interaction_count', 0) > 5:
            logger.info(f"👤 Recognized user {author}")
            return True
        
        return False
    
    async def respond_to_comment(self, comment: Dict[str, Any]):
        """Generate and post an autonomous response"""
        try:
            comment_id = comment['id']
            text = comment.get('snippet', {}).get('textDisplay', '')
            author = comment.get('snippet', {}).get('authorDisplayName', '')
            
            # Generate response using agentic chat engine
            response = await self.generate_response(text, author)
            
            if response:
                # Post the reply
                reply_to_comment(self.youtube, comment_id, response)
                logger.info(f"✅ Responded to {author}: {response[:100]}...")
                
                # Update memory
                self.memory_manager.update_user_memory(author, {
                    'last_comment_response': datetime.now().isoformat(),
                    'comment_interactions': 1
                })
                
                # Track quota usage
                self.quota_used += 50  # Comment post costs ~50 units
                
        except Exception as e:
            logger.error(f"Failed to respond to comment: {e}")
    
    async def generate_response(self, comment_text: str, author: str) -> Optional[str]:
        """Generate contextual response using chat engine"""
        try:
            # Build context
            context = {
                'platform': 'youtube_comments',
                'author': author,
                'is_comment': True,
                'channel': 'Move2Japan'
            }
            
            # Get user memory for personalization
            user_memory = self.memory_manager.get_user_memory(author)
            if user_memory:
                context['user_history'] = user_memory
            
            # Generate response
            response = self.chat_engine.generate_response(
                comment_text,
                author,
                context
            )
            
            # Keep responses concise for comments (YouTube limit)
            if response and len(response) > 500:
                response = response[:497] + "..."
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            return None
    
    def stop(self):
        """Stop the comment monitor"""
        self.is_running = False
        logger.info("Comment Monitor DAE stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the monitor"""
        return {
            'running': self.is_running,
            'processed_comments': len(self.processed_comments),
            'quota_used': self.quota_used,
            'current_interval': self.current_interval,
            'last_check': self.last_check_time.isoformat()
        }


class CommentMonitorIntegration:
    """
    Integration layer to run CommentMonitorDAE alongside LiveChatCore
    """
    
    def __init__(self, youtube_service, channel_id: str):
        """
        Initialize integration layer
        
        Args:
            youtube_service: YouTube service instance
            channel_id: Channel to monitor
        """
        self.monitor = CommentMonitorDAE(youtube_service, channel_id)
        self.monitor_task = None
    
    async def start_alongside_chat(self):
        """Start comment monitoring as background task"""
        if not self.monitor_task or self.monitor_task.done():
            self.monitor_task = asyncio.create_task(self.monitor.start())
            logger.info("Comment monitor started as background task")
    
    def stop(self):
        """Stop comment monitoring"""
        if self.monitor_task and not self.monitor_task.done():
            self.monitor.stop()
            self.monitor_task.cancel()
            logger.info("Comment monitor stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get monitor status"""
        return self.monitor.get_status()