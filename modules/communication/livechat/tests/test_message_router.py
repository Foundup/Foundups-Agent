#!/usr/bin/env python3
"""
Test Message Router
Verifies the message router correctly routes messages to handlers
"""

import unittest
from unittest.mock import Mock, MagicMock
import sys
from pathlib import Path

# Add parent directory to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from modules.communication.livechat.src.core.message_router import (
    MessageRouter, BaseMessageHandler, CommandHandlerAdapter, EventHandlerAdapter
)


class TestMessageRouter(unittest.TestCase):
    """Test the message router."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.router = MessageRouter()
    
    def test_router_initialization(self):
        """Test router initializes correctly."""
        self.assertIsNotNone(self.router)
        self.assertEqual(len(self.router.handlers), 0)
        self.assertEqual(self.router.get_stats()['total_handlers'], 0)
    
    def test_handler_registration(self):
        """Test handler registration."""
        # Create mock handler
        handler = Mock()
        handler.can_handle = Mock(return_value=True)
        handler.process = Mock(return_value={'response': 'test'})
        
        # Register handler
        self.router.register_handler(handler, priority=50)
        
        # Verify registration
        self.assertEqual(len(self.router.handlers), 1)
        self.assertEqual(self.router.handlers[0][0], 50)  # priority
        self.assertEqual(self.router.handlers[0][1], handler)
    
    def test_priority_ordering(self):
        """Test handlers are ordered by priority."""
        # Create handlers with different priorities
        handler1 = Mock()
        handler2 = Mock()
        handler3 = Mock()
        
        # Register in random order
        self.router.register_handler(handler2, priority=50)
        self.router.register_handler(handler1, priority=100)
        self.router.register_handler(handler3, priority=10)
        
        # Verify ordering (highest priority first)
        self.assertEqual(self.router.handlers[0][0], 100)
        self.assertEqual(self.router.handlers[1][0], 50)
        self.assertEqual(self.router.handlers[2][0], 10)
    
    def test_message_routing(self):
        """Test message is routed to correct handler."""
        # Create two handlers
        handler1 = Mock()
        handler1.can_handle = Mock(return_value=False)
        handler1.process = Mock()
        
        handler2 = Mock()
        handler2.can_handle = Mock(return_value=True)
        handler2.process = Mock(return_value={'response': 'handled'})
        
        # Register handlers
        self.router.register_handler(handler1, priority=100)
        self.router.register_handler(handler2, priority=50)
        
        # Route message
        message = {'type': 'test'}
        response = self.router.route_message(message)
        
        # Verify routing
        handler1.can_handle.assert_called_once_with(message)
        handler2.can_handle.assert_called_once_with(message)
        handler1.process.assert_not_called()  # First handler can't handle
        handler2.process.assert_called_once_with(message)  # Second handler processes
        self.assertEqual(response, {'response': 'handled'})
    
    def test_command_handler_adapter(self):
        """Test CommandHandlerAdapter works correctly."""
        # Create mock command handler
        command_handler = Mock()
        command_handler.process_command = Mock(return_value={
            'response': 'Command executed'
        })
        
        # Create adapter
        adapter = CommandHandlerAdapter(command_handler)
        
        # Test can_handle
        command_msg = {'snippet': {'displayMessage': '/test command'}}
        normal_msg = {'snippet': {'displayMessage': 'normal message'}}
        
        self.assertTrue(adapter.can_handle(command_msg))
        self.assertFalse(adapter.can_handle(normal_msg))
        
        # Test process
        response = adapter.process(command_msg)
        self.assertEqual(response['response'], 'Command executed')
        self.assertEqual(response['response_type'], 'command_response')
    
    def test_event_handler_adapter(self):
        """Test EventHandlerAdapter works correctly."""
        # Create mock event handler
        event_handler = Mock()
        event_handler.process_ban_event = Mock(return_value={
            'announcement': 'User banned'
        })
        
        # Create adapter
        adapter = EventHandlerAdapter(event_handler)
        
        # Test can_handle
        ban_event = {'type': 'ban_event'}
        timeout_event = {'type': 'timeout_event'}
        normal_msg = {'type': 'textMessageEvent'}
        
        self.assertTrue(adapter.can_handle(ban_event))
        self.assertTrue(adapter.can_handle(timeout_event))
        self.assertFalse(adapter.can_handle(normal_msg))
        
        # Test process
        response = adapter.process(ban_event)
        self.assertEqual(response['response'], 'User banned')
        self.assertEqual(response['response_type'], 'event_announcement')
    
    def test_router_statistics(self):
        """Test router statistics tracking."""
        # Create handler
        handler = Mock()
        handler.can_handle = Mock(return_value=True)
        handler.process = Mock(return_value={'response': 'test'})
        
        # Register and route messages
        self.router.register_handler(handler, priority=50)
        self.router.route_message({'type': 'test1'})
        self.router.route_message({'type': 'test2'})
        
        # Check stats
        stats = self.router.get_stats()
        self.assertEqual(stats['total_handlers'], 1)
        self.assertEqual(stats['total_messages_routed'], 2)
    
    def test_error_handling(self):
        """Test router handles errors gracefully."""
        # Create handler that throws error
        handler = Mock()
        handler.can_handle = Mock(return_value=True)
        handler.process = Mock(side_effect=Exception("Test error"))
        
        # Register handler
        self.router.register_handler(handler, priority=50)
        
        # Route message (should not raise)
        response = self.router.route_message({'type': 'test'})
        
        # Should return None when handler errors
        self.assertIsNone(response)
    
    def test_handler_unregistration(self):
        """Test handler can be unregistered."""
        # Create and register handler
        handler = Mock()
        self.router.register_handler(handler, priority=50)
        self.assertEqual(len(self.router.handlers), 1)
        
        # Unregister
        self.router.unregister_handler(handler)
        self.assertEqual(len(self.router.handlers), 0)
    
    def test_clear_handlers(self):
        """Test clearing all handlers."""
        # Register multiple handlers
        for i in range(3):
            handler = Mock()
            self.router.register_handler(handler, priority=i*10)
        
        self.assertEqual(len(self.router.handlers), 3)
        
        # Clear all
        self.router.clear_handlers()
        self.assertEqual(len(self.router.handlers), 0)
        self.assertEqual(self.router.get_stats()['total_handlers'], 0)


if __name__ == "__main__":
    print("\n" + "="*60)
    print("[TEST] MESSAGE ROUTER")
    print("="*60)
    
    # Run tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMessageRouter)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*60)
    if result.wasSuccessful():
        print("[SUCCESS] MESSAGE ROUTER WORKS!")
        print("\nBenefits achieved:")
        print("  - Unified message routing")
        print("  - Priority-based handler ordering")
        print("  - Extensible handler system")
        print("  - Statistics tracking")
        print("  - Error resilience")
    else:
        print("[FAIL] Some tests failed")
    print("="*60)