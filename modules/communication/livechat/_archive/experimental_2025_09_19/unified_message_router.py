#!/usr/bin/env python3
"""
Unified Message Router - Clean Architecture for YouTube DAE
Rewires the existing messy message system without breaking current modules.
WSP 84: Enhance existing modules, don't vibecode new ones.
"""

import logging
from typing import Optional, Dict, Any, Tuple
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class MessageType(Enum):
    """Clear message categories that match actual functionality"""
    CONSCIOUSNESS_TRIGGER = "consciousness"    # [U+270A][U+270B][U+1F590]️ patterns
    RESEARCH_COMMAND = "research"              # /PQN, /quiz, /facts
    GAMIFICATION_COMMAND = "gamification"     # /score, /rank, /whacks
    SYSTEM_COMMAND = "system"                 # /help, /toggle, /stats
    FACT_CHECK = "factcheck"                  # factcheck @user
    MAGA_CONTENT = "maga"                     # MAGA content detection
    EMOJI_TRIGGER = "emoji"                   # Other emoji patterns
    REGULAR_CHAT = "chat"                     # Normal conversation

@dataclass
class MessageContext:
    """Clean message context object"""
    text: str
    author_name: str
    author_id: str
    role: str  # 'USER', 'MOD', 'OWNER'
    message_type: MessageType
    requires_throttling: bool
    raw_message: Dict[str, Any]

class UnifiedMessageRouter:
    """
    Clean router that works WITH existing handlers.
    Rewires the message flow without breaking current modules.
    """
    
    def __init__(self, message_processor):
        """Initialize with existing MessageProcessor to leverage current handlers"""
        self.message_processor = message_processor
        self.logger = logging.getLogger(__name__)
        
        # Map message types to existing handler methods
        self.handler_map = {
            MessageType.CONSCIOUSNESS_TRIGGER: self._route_consciousness,
            MessageType.RESEARCH_COMMAND: self._route_research,
            MessageType.GAMIFICATION_COMMAND: self._route_gamification, 
            MessageType.SYSTEM_COMMAND: self._route_system,
            MessageType.FACT_CHECK: self._route_factcheck,
            MessageType.MAGA_CONTENT: self._route_maga,
            MessageType.EMOJI_TRIGGER: self._route_emoji,
            MessageType.REGULAR_CHAT: self._route_chat
        }
    
    def classify_message(self, text: str, author_details: Dict) -> Tuple[MessageType, bool]:
        """
        Clean message classification.
        Returns: (MessageType, requires_throttling)
        """
        text_lower = text.lower().strip()
        
        # Check for consciousness triggers first (highest priority)
        if self.message_processor._check_consciousness_trigger(text):
            return MessageType.CONSCIOUSNESS_TRIGGER, True
        
        # Check for slash commands
        if text_lower.startswith('/'):
            # Research commands
            if any(text_lower.startswith(cmd) for cmd in ['/pqn', '/quiz', '/facts', '/answer']):
                return MessageType.RESEARCH_COMMAND, True
            
            # System commands (no throttling for help)
            if any(text_lower.startswith(cmd) for cmd in ['/help', '/toggle']):
                return MessageType.SYSTEM_COMMAND, False
            
            # Gamification commands
            if any(text_lower.startswith(cmd) for cmd in ['/score', '/rank', '/whacks', '/frags', '/leaderboard', '/sprees']):
                return MessageType.GAMIFICATION_COMMAND, True
        
        # Check for fact-check commands
        if self.message_processor._check_factcheck_command(text):
            return MessageType.FACT_CHECK, True
        
        # Check for MAGA content
        if self.message_processor.greeting_generator.get_response_to_maga(text):
            return MessageType.MAGA_CONTENT, False
        
        # Check for other emoji triggers
        if self.message_processor._check_trigger_emojis(text):
            return MessageType.EMOJI_TRIGGER, True
        
        # Default to regular chat
        return MessageType.REGULAR_CHAT, False
    
    async def route_message(self, context: MessageContext) -> Optional[str]:
        """
        Clean routing that uses existing handlers.
        Single point of throttling and routing decisions.
        """
        # Single throttling check point
        if context.requires_throttling:
            if self._is_throttled(context):
                self.logger.debug(f"⏳ Message throttled for {context.author_name}: {context.message_type.value}")
                return None
            
            # Update throttling state
            self._update_throttling(context)
        
        # Route to appropriate handler
        handler = self.handler_map.get(context.message_type)
        if handler:
            try:
                # Check if handler is async
                import inspect
                if inspect.iscoroutinefunction(handler):
                    response = await handler(context)
                else:
                    response = handler(context)
                
                if response:
                    self.logger.info(f"[OK] {context.message_type.value} response for {context.author_name}")
                return response
            except Exception as e:
                self.logger.error(f"[FAIL] Handler error for {context.message_type.value}: {e}")
                return None
        
        self.logger.warning(f"[U+1F937] No handler for message type: {context.message_type.value}")
        return None
    
    # ====== ROUTING METHODS (Use existing handlers) ======
    
    async def _route_consciousness(self, context: MessageContext) -> Optional[str]:
        """Route consciousness triggers to existing Grok 3 system"""
        return await self.message_processor._generate_banter_response(
            context.text, context.author_name, context.role
        )
    
    def _route_research(self, context: MessageContext) -> Optional[str]:
        """Route research commands through existing whack handler (PQN lives there)"""
        return self.message_processor._handle_whack_command(
            context.text, context.author_name, context.author_id, context.role
        )
    
    def _route_gamification(self, context: MessageContext) -> Optional[str]:
        """Route gamification commands through existing whack handler"""
        return self.message_processor._handle_whack_command(
            context.text, context.author_name, context.author_id, context.role
        )
    
    def _route_system(self, context: MessageContext) -> Optional[str]:
        """Route system commands through existing whack handler"""
        return self.message_processor._handle_whack_command(
            context.text, context.author_name, context.author_id, context.role
        )
    
    async def _route_factcheck(self, context: MessageContext) -> Optional[str]:
        """Route fact-check commands to existing handler"""
        return await self.message_processor._handle_factcheck(
            context.text, context.author_name, context.role
        )
    
    async def _route_maga(self, context: MessageContext) -> Optional[str]:
        """Route MAGA content to existing handler"""
        return self.message_processor.greeting_generator.get_response_to_maga(context.text)
    
    async def _route_emoji(self, context: MessageContext) -> Optional[str]:
        """Route emoji triggers to existing banter system"""
        return await self.message_processor._generate_banter_response(
            context.text, context.author_name
        )
    
    async def _route_chat(self, context: MessageContext) -> Optional[str]:
        """Route regular chat - currently no handler"""
        return None
    
    # ====== UNIFIED THROTTLING ======
    
    def _is_throttled(self, context: MessageContext) -> bool:
        """Unified throttling check - uses existing emoji limiter"""
        if hasattr(self.message_processor, 'emoji_limiter') and self.message_processor.emoji_limiter:
            should_respond, reason = self.message_processor.emoji_limiter.should_respond_to_emoji(
                context.author_id, context.author_name, context.text
            )
            return not should_respond
        
        # Fallback to simple rate limiting
        return self.message_processor._is_rate_limited(context.author_id)
    
    def _update_throttling(self, context: MessageContext) -> None:
        """Update throttling state - uses existing systems"""
        if hasattr(self.message_processor, 'emoji_limiter') and self.message_processor.emoji_limiter:
            self.message_processor.emoji_limiter.record_emoji_response(
                context.author_id, context.author_name
            )
        
        # Update trigger time for rate limiting
        self.message_processor._update_trigger_time(context.author_id)

    def get_message_stats(self) -> Dict[str, int]:
        """Get routing statistics for monitoring"""
        # Could add message type counters here for WSP 48 analytics
        return {
            "total_routed": getattr(self, '_total_routed', 0),
            "throttled_count": getattr(self, '_throttled_count', 0)
        }