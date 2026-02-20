#!/usr/bin/env python3
"""
Message Router - Unified message routing for LiveChat
WSP-Compliant: WSP 3 (Module Organization), WSP 49 (Module Structure)

Routes messages to appropriate handlers based on type and content.
Provides a unified interface for all message processors.
"""

import logging
from typing import List, Dict, Any, Optional, Protocol
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class MessageHandler(Protocol):
    """Protocol for message handlers."""
    
    def can_handle(self, message: Dict[str, Any]) -> bool:
        """Check if this handler can process the message."""
        ...
    
    def process(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process the message and return response if any."""
        ...


class BaseMessageHandler(ABC):
    """Base class for all message handlers."""
    
    @abstractmethod
    def can_handle(self, message: Dict[str, Any]) -> bool:
        """Check if this handler can process the message."""
        pass
    
    @abstractmethod
    def process(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process the message and return response if any."""
        pass
    
    def get_priority(self) -> int:
        """Get handler priority (higher = processed first)."""
        return 0


class MessageRouter:
    """
    Routes messages to appropriate handlers.
    
    This router maintains a list of handlers and routes messages
    to the first handler that can process them. Handlers are
    checked in priority order.
    """
    
    def __init__(self):
        """Initialize the message router."""
        self.handlers: List[MessageHandler] = []
        self.handler_stats = {}
        logger.info("MessageRouter initialized")
    
    def register_handler(self, handler: MessageHandler, priority: int = 0) -> None:
        """
        Register a message handler.
        
        Args:
            handler: Handler to register
            priority: Handler priority (higher = processed first)
        """
        # Insert handler sorted by priority
        self.handlers.append((priority, handler))
        self.handlers.sort(key=lambda x: x[0], reverse=True)
        
        handler_name = type(handler).__name__
        self.handler_stats[handler_name] = {
            'registered': True,
            'messages_handled': 0,
            'priority': priority
        }
        
        logger.info(f"Registered handler: {handler_name} (priority: {priority})")
    
    def unregister_handler(self, handler: MessageHandler) -> None:
        """
        Unregister a message handler.
        
        Args:
            handler: Handler to unregister
        """
        self.handlers = [(p, h) for p, h in self.handlers if h != handler]
        handler_name = type(handler).__name__
        if handler_name in self.handler_stats:
            self.handler_stats[handler_name]['registered'] = False
        logger.info(f"Unregistered handler: {handler_name}")
    
    def route_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Route a message to the appropriate handler.
        
        Args:
            message: Message to route
            
        Returns:
            Response from handler or None
        """
        # Extract message info for logging
        msg_type = message.get('type', 'unknown')
        author = message.get('authorDetails', {}).get('displayName', 'Unknown')
        
        # Try each handler in priority order
        for priority, handler in self.handlers:
            try:
                if handler.can_handle(message):
                    handler_name = type(handler).__name__
                    logger.debug(f"Routing {msg_type} from {author} to {handler_name}")
                    
                    # Process message
                    response = handler.process(message)
                    
                    # Update stats
                    if handler_name in self.handler_stats:
                        self.handler_stats[handler_name]['messages_handled'] += 1
                    
                    # Return first response (handlers are priority ordered)
                    if response:
                        logger.info(f"{handler_name} generated response for {author}")
                        return response
                    
                    # Handler processed but no response needed
                    return None
                    
            except Exception as e:
                handler_name = type(handler).__name__
                logger.error(f"Error in handler {handler_name}: {e}")
                continue
        
        # No handler could process the message
        logger.debug(f"No handler for {msg_type} from {author}")
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get router statistics.
        
        Returns:
            Dictionary of statistics
        """
        total_messages = sum(
            stats['messages_handled'] 
            for stats in self.handler_stats.values()
        )
        
        return {
            'total_handlers': len(self.handlers),
            'active_handlers': sum(1 for _, h in self.handlers),
            'total_messages_routed': total_messages,
            'handler_stats': self.handler_stats
        }
    
    def clear_handlers(self) -> None:
        """Clear all registered handlers."""
        self.handlers = []
        self.handler_stats = {}
        logger.info("Cleared all handlers")


class CommandHandlerAdapter(BaseMessageHandler):
    """Adapter to make CommandHandler work with router."""
    
    def __init__(self, command_handler):
        """
        Initialize adapter.
        
        Args:
            command_handler: Existing CommandHandler instance
        """
        self.command_handler = command_handler
    
    def can_handle(self, message: Dict[str, Any]) -> bool:
        """Check if message is a command."""
        text = message.get('snippet', {}).get('displayMessage', '')
        return text.startswith('/')
    
    def process(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process command and return response."""
        result = self.command_handler.process_command(message)
        if result and result.get('response'):
            return {
                'response': result['response'],
                'response_type': 'command_response'
            }
        return None
    
    def get_priority(self) -> int:
        """Commands have high priority."""
        return 100


class EventHandlerAdapter(BaseMessageHandler):
    """Adapter to make EventHandler work with router."""
    
    def __init__(self, event_handler):
        """
        Initialize adapter.
        
        Args:
            event_handler: Existing EventHandler instance
        """
        self.event_handler = event_handler
    
    def can_handle(self, message: Dict[str, Any]) -> bool:
        """Check if message is an event."""
        msg_type = message.get('type', '')
        return msg_type in ['ban_event', 'timeout_event', 'deletion_event']
    
    def process(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process event and return announcement."""
        if message.get('type') in ['ban_event', 'timeout_event']:
            result = self.event_handler.process_ban_event(message)
            if result and result.get('announcement'):
                return {
                    'response': result['announcement'],
                    'response_type': 'event_announcement'
                }
        return None
    
    def get_priority(self) -> int:
        """Events have medium priority."""
        return 50


class ConsciousnessHandlerAdapter(BaseMessageHandler):
    """Adapter for consciousness trigger handler."""
    
    def __init__(self, consciousness_handler):
        """
        Initialize adapter.
        
        Args:
            consciousness_handler: Existing consciousness handler
        """
        self.handler = consciousness_handler
    
    def can_handle(self, message: Dict[str, Any]) -> bool:
        """Check if message contains consciousness triggers."""
        text = message.get('snippet', {}).get('displayMessage', '')
        return '✊' in text or '👊' in text or '✋' in text or '🖐' in text
    
    def process(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process consciousness trigger."""
        result = self.handler.process_consciousness_trigger(message)
        if result and result.get('response'):
            return {
                'response': result['response'],
                'response_type': 'consciousness_response'
            }
        return None
    
    def get_priority(self) -> int:
        """Consciousness triggers have very high priority."""
        return 90


# Example usage
if __name__ == "__main__":
    # Create router
    router = MessageRouter()
    
    # Register handlers (would use real handlers in production)
    class TestHandler(BaseMessageHandler):
        def can_handle(self, message):
            return 'test' in message.get('text', '').lower()
        
        def process(self, message):
            return {'response': 'Test response'}
    
    router.register_handler(TestHandler(), priority=10)
    
    # Route a message
    test_message = {'text': 'This is a test message'}
    response = router.route_message(test_message)
    print(f"Response: {response}")
    
    # Get stats
    stats = router.get_stats()
    print(f"Router stats: {stats}")