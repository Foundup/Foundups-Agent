#!/usr/bin/env python3
"""
LiveChat Orchestrator - Coordinates all livechat components
WSP-Compliant: WSP 3 (Module Organization), WSP 49 (Module Structure)

This is the refactored orchestration logic extracted from livechat_core.py.
It coordinates existing modules without duplicating their functionality.
"""

import logging
import asyncio
from typing import Optional, Dict, Any
from pathlib import Path

# Reuse existing well-designed modules
from modules.communication.livechat.src.session_manager import SessionManager
from modules.communication.livechat.src.chat_sender import ChatSender
from modules.communication.livechat.src.chat_poller import ChatPoller
from modules.communication.livechat.src.moderation_stats import ModerationStats
from modules.communication.livechat.src.chat_memory_manager import ChatMemoryManager

# Import handlers (all are well-designed and reusable)
from modules.communication.livechat.src.message_processor import MessageProcessor
from modules.communication.livechat.src.event_handler import EventHandler
from modules.communication.livechat.src.command_handler import CommandHandler

# Import message router
from modules.communication.livechat.src.core.message_router import (
    MessageRouter, CommandHandlerAdapter, EventHandlerAdapter
)

# Import managers
try:
    from modules.communication.livechat.src.intelligent_throttle_manager import IntelligentThrottleManager
except ImportError:
    IntelligentThrottleManager = None

logger = logging.getLogger(__name__)


class LiveChatOrchestrator:
    """Orchestrates all livechat components - coordinates without implementing business logic."""
    
    def __init__(self, youtube_service, video_id: str, live_chat_id: Optional[str] = None,
                 channel_name: str = None, channel_id: str = None):
        """Initialize the orchestrator with all necessary components."""
        self.youtube = youtube_service
        self.video_id = video_id
        self.live_chat_id = live_chat_id
        self.channel_name = channel_name or "StreamOwner"
        self.channel_id = channel_id or "owner"
        self.is_running = False
        
        # Initialize components (all are existing, well-tested modules)
        self._init_managers()
        self._init_processors()
        self._init_communication()
        
        logger.info(f"LiveChatOrchestrator initialized for video: {video_id}")
    
    def _init_managers(self):
        """Initialize manager components."""
        # Session management
        self.session_manager = SessionManager(self.youtube, self.video_id)
        
        # Memory and stats
        self.memory_manager = ChatMemoryManager("memory")
        self.mod_stats = ModerationStats("memory")
        
        # Throttling (use intelligent if available)
        if IntelligentThrottleManager:
            self.throttle_manager = IntelligentThrottleManager(
                memory_path=Path("memory")
            )
            self.throttle_manager.enable_learning(True)
            self.throttle_manager.set_agentic_mode(True)
            logger.info("[ORCHESTRATOR] Using intelligent throttle manager")
        else:
            self.throttle_manager = None
            logger.info("[ORCHESTRATOR] No throttle manager available")
    
    def _init_processors(self):
        """Initialize message processors and router."""
        # Initialize individual handlers
        self.message_processor = MessageProcessor(
            self.youtube,
            self.memory_manager,
            None  # No chat_sender available in orchestrator context
        )
        self.event_handler = EventHandler(memory_dir="memory")
        self.command_handler = CommandHandler(
            self.youtube,
            self.memory_manager
        )
        
        # Initialize message router
        self.message_router = MessageRouter()
        
        # Register handlers with router using adapters
        self.message_router.register_handler(
            CommandHandlerAdapter(self.command_handler),
            priority=100  # Commands have highest priority
        )
        self.message_router.register_handler(
            EventHandlerAdapter(self.event_handler),
            priority=50   # Events have medium priority
        )
        
        logger.info("[ORCHESTRATOR] Message router configured with handlers")
    
    def _init_communication(self):
        """Initialize communication components."""
        # Message sending
        self.chat_sender = ChatSender(
            self.youtube, 
            self.live_chat_id
        )
        
        # Message polling
        self.chat_poller = ChatPoller(
            self.youtube,
            self.live_chat_id,
            self.channel_name,
            self.channel_id
        )
    
    async def initialize(self) -> bool:
        """Initialize the chat session."""
        if not await self.session_manager.initialize_session():
            logger.error("Failed to initialize session")
            return False
        
        # Update components with session info
        self.live_chat_id = self.session_manager.live_chat_id
        self.channel_name = getattr(self.session_manager, 'channel_title', self.channel_name)
        self.channel_id = getattr(self.session_manager, 'channel_id', self.channel_id)
        
        # Update communication components
        self.chat_sender.live_chat_id = self.live_chat_id
        self.chat_poller.live_chat_id = self.live_chat_id
        self.chat_poller.channel_name = self.channel_name
        self.chat_poller.channel_id = self.channel_id
        
        await self.session_manager.send_greeting(self.send_message)
        logger.info("Orchestrator initialized successfully")
        return True
    
    async def send_message(self, message_text: str, skip_delay: bool = False, 
                          response_type: str = 'general') -> bool:
        """Send a message to the live chat with throttling."""
        if not self.live_chat_id:
            logger.error("Cannot send message - no live chat ID")
            return False
        
        # Apply throttling if available
        if self.throttle_manager and not skip_delay:
            self.throttle_manager.track_api_call(quota_cost=5)
            if not self.throttle_manager.should_respond(response_type):
                delay = self.throttle_manager.calculate_adaptive_delay(response_type)
                logger.info(f"[THROTTLE] Delaying {response_type} by {delay:.1f}s")
                return False
        
        # Delegate to chat sender
        success = await self.chat_sender.send_message(
            message_text, skip_delay=skip_delay, response_type=response_type
        )
        
        # Record success for learning
        if self.throttle_manager and success:
            self.throttle_manager.record_response(response_type, success=True)
        
        return success
    
    async def poll_messages(self) -> tuple:
        """Poll for new chat messages."""
        try:
            messages = await self.chat_poller.poll_messages(
                viewer_count=getattr(self.session_manager, 'viewer_count', 0)
            )
            return (messages, self.chat_poller.poll_interval_ms) if messages else ([], 5000)
        except Exception as e:
            logger.error(f"Error polling messages: {e}")
            return [], 5000
    
    async def process_message(self, message: Dict[str, Any], use_router: bool = False) -> None:
        """Process a single chat message, routing by type."""
        try:
            if use_router and hasattr(self, 'message_router'):
                # Use unified message router
                response = self.message_router.route_message(message)
                if response:
                    await self.send_message(
                        response['response'],
                        response_type=response.get('response_type', 'general')
                    )
            else:
                # Use legacy direct routing
                msg_type = message.get("type")
                if msg_type in ["ban_event", "timeout_event"]:
                    await self._process_ban_event(message)
                else:
                    await self._process_regular_message(message)
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    async def _process_regular_message(self, message: Dict[str, Any]) -> None:
        """Process regular chat message."""
        # Update stats
        self.mod_stats.record_message()
        
        # Process through message processor
        processed = self.message_processor.process_message(message)
        
        # Generate and send response if needed
        if processed.get("response"):
            response = processed["response"]
            response_type = processed.get("response_type", "general")
            
            await self.send_message(response, response_type=response_type)
    
    async def _process_ban_event(self, ban_event: Dict[str, Any]) -> None:
        """Process ban/timeout event."""
        # Delegate to event handler
        processed = self.event_handler.process_ban_event(ban_event)
        
        # Send announcement if generated
        if processed.get("announcement"):
            await self.send_message(
                processed["announcement"],
                response_type="timeout_announcement"
            )
    
    async def start_listening(self) -> None:
        """Start the main listening loop."""
        if not await self.initialize():
            logger.error("Failed to initialize, cannot start listening")
            return
        
        self.is_running = True
        logger.info("Started listening to chat")
        
        while self.is_running:
            try:
                messages, poll_interval = await self.poll_messages()
                for message in messages:
                    await self.process_message(message)
                await asyncio.sleep(poll_interval / 1000)
            except Exception as e:
                logger.error(f"Error in listening loop: {e}")
                await asyncio.sleep(5)
    
    def stop_listening(self):
        """Stop the listening loop."""
        self.is_running = False
        logger.info("Stopped listening to chat")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current orchestrator status."""
        return {
            'is_running': self.is_running,
            'video_id': self.video_id,
            'live_chat_id': self.live_chat_id,
            'channel_name': self.channel_name,
            'messages_processed': self.mod_stats.total_messages,
            'throttle_enabled': self.throttle_manager is not None
        }

    def get_moderation_stats(self) -> Dict[str, Any]:
        """Get moderation statistics - compatibility with LiveChatCore"""
        return self.mod_stats.get_stats() if hasattr(self.mod_stats, 'get_stats') else {
            'total_messages': getattr(self.mod_stats, 'total_messages', 0),
            'total_timeouts': getattr(self.mod_stats, 'total_timeouts', 0),
            'timeout_rate': getattr(self.mod_stats, 'timeout_rate', 0.0)
        }