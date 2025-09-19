#!/usr/bin/env python3
"""
Test for UnifiedMessageRouter - WSP 5/6 Testing Compliance
Tests the enhanced message routing architecture without breaking existing functionality.
"""

import unittest
from unittest.mock import Mock, AsyncMock, patch
import pytest
import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
sys.path.insert(0, project_root)

from modules.communication.livechat.src.unified_message_router import (
    UnifiedMessageRouter, 
    MessageContext, 
    MessageType
)

class TestUnifiedMessageRouter(unittest.TestCase):
    """Test cases for UnifiedMessageRouter"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock message processor with all required methods
        self.mock_processor = Mock()
        self.mock_processor._check_consciousness_trigger = Mock(return_value=False)
        self.mock_processor._check_factcheck_command = Mock(return_value=False)
        self.mock_processor.greeting_generator = Mock()
        self.mock_processor.greeting_generator.get_response_to_maga = Mock(return_value=None)
        self.mock_processor._check_trigger_emojis = Mock(return_value=False)
        self.mock_processor._is_rate_limited = Mock(return_value=False)
        self.mock_processor._update_trigger_time = Mock()
        self.mock_processor.emoji_limiter = None
        
        # Mock handler methods
        self.mock_processor._generate_banter_response = AsyncMock(return_value="Mocked response")
        self.mock_processor._handle_whack_command = Mock(return_value="Whack response")
        self.mock_processor._handle_factcheck = AsyncMock(return_value="Factcheck response")
        
        # Initialize router
        self.router = UnifiedMessageRouter(self.mock_processor)
    
    def test_message_type_classification(self):
        """Test that messages are properly classified"""
        # Test consciousness trigger classification
        self.mock_processor._check_consciousness_trigger.return_value = True
        msg_type, throttle = self.router.classify_message("✊✋🖐️ test", {})
        self.assertEqual(msg_type, MessageType.CONSCIOUSNESS_TRIGGER)
        self.assertTrue(throttle)
        
        # Reset mock
        self.mock_processor._check_consciousness_trigger.return_value = False
        
        # Test research commands
        for cmd in ["/pqn status", "/quiz start", "/facts history"]:
            msg_type, throttle = self.router.classify_message(cmd, {})
            self.assertEqual(msg_type, MessageType.RESEARCH_COMMAND)
            self.assertTrue(throttle)
        
        # Test system commands (no throttling)
        for cmd in ["/help", "/toggle"]:
            msg_type, throttle = self.router.classify_message(cmd, {})
            self.assertEqual(msg_type, MessageType.SYSTEM_COMMAND)
            self.assertFalse(throttle)
        
        # Test gamification commands
        for cmd in ["/score", "/rank", "/whacks"]:
            msg_type, throttle = self.router.classify_message(cmd, {})
            self.assertEqual(msg_type, MessageType.GAMIFICATION_COMMAND)
            self.assertTrue(throttle)
    
    @pytest.mark.asyncio
    async def test_consciousness_routing(self):
        """Test consciousness trigger routing to Grok 3"""
        context = MessageContext(
            text="✊✋🖐️ test consciousness",
            author_name="TestUser",
            author_id="123",
            role="USER",
            message_type=MessageType.CONSCIOUSNESS_TRIGGER,
            requires_throttling=True,
            raw_message={}
        )
        
        response = await self.router._route_consciousness(context)
        
        # Verify it called the correct handler with proper args
        self.mock_processor._generate_banter_response.assert_called_once_with(
            "✊✋🖐️ test consciousness", "TestUser", "USER"
        )
        self.assertEqual(response, "Mocked response")
    
    def test_research_command_routing(self):
        """Test research commands (PQN) routing"""
        context = MessageContext(
            text="/PQN status",
            author_name="TestUser", 
            author_id="123",
            role="USER",
            message_type=MessageType.RESEARCH_COMMAND,
            requires_throttling=True,
            raw_message={}
        )
        
        response = self.router._route_research(context)
        
        # Verify it routes through existing whack handler (where PQN lives)
        self.mock_processor._handle_whack_command.assert_called_once_with(
            "/PQN status", "TestUser", "123", "USER"
        )
        self.assertEqual(response, "Whack response")
    
    @pytest.mark.asyncio
    async def test_throttling_enforcement(self):
        """Test that throttling is properly enforced"""
        context = MessageContext(
            text="/score",
            author_name="TestUser",
            author_id="123", 
            role="USER",
            message_type=MessageType.GAMIFICATION_COMMAND,
            requires_throttling=True,
            raw_message={}
        )
        
        # Test throttling blocks response
        self.mock_processor._is_rate_limited.return_value = True
        response = await self.router.route_message(context)
        self.assertIsNone(response)
        
        # Test throttling allows response when not limited
        self.mock_processor._is_rate_limited.return_value = False
        response = await self.router.route_message(context)
        self.assertIsNotNone(response)
        
        # Verify throttling state was updated
        self.mock_processor._update_trigger_time.assert_called_with("123")
    
    def test_system_commands_no_throttling(self):
        """Test that system commands bypass throttling"""
        context = MessageContext(
            text="/help",
            author_name="TestUser",
            author_id="123",
            role="USER", 
            message_type=MessageType.SYSTEM_COMMAND,
            requires_throttling=False,
            raw_message={}
        )
        
        # Should not check throttling for system commands
        response = self.router._route_system(context)
        
        # Verify handler was called directly without throttling checks
        self.mock_processor._handle_whack_command.assert_called_once_with(
            "/help", "TestUser", "123", "USER"
        )
    
    def test_message_type_enum_completeness(self):
        """Test that all message types are properly defined"""
        expected_types = {
            'CONSCIOUSNESS_TRIGGER',
            'RESEARCH_COMMAND', 
            'GAMIFICATION_COMMAND',
            'SYSTEM_COMMAND',
            'FACT_CHECK',
            'MAGA_CONTENT',
            'EMOJI_TRIGGER',
            'REGULAR_CHAT'
        }
        
        actual_types = {msg_type.name for msg_type in MessageType}
        self.assertEqual(expected_types, actual_types)
    
    def test_backwards_compatibility(self):
        """Test that router works with existing message processor interface"""
        # Verify router initializes with mock processor
        self.assertIsNotNone(self.router.message_processor)
        self.assertEqual(self.router.message_processor, self.mock_processor)
        
        # Verify handler map is properly populated
        self.assertEqual(len(self.router.handler_map), 8)
        self.assertIn(MessageType.CONSCIOUSNESS_TRIGGER, self.router.handler_map)
        self.assertIn(MessageType.RESEARCH_COMMAND, self.router.handler_map)

class TestMessageContext(unittest.TestCase):
    """Test MessageContext data structure"""
    
    def test_message_context_creation(self):
        """Test MessageContext can be created with all required fields"""
        context = MessageContext(
            text="test message",
            author_name="TestUser",
            author_id="123",
            role="USER",
            message_type=MessageType.REGULAR_CHAT,
            requires_throttling=False,
            raw_message={"test": "data"}
        )
        
        self.assertEqual(context.text, "test message")
        self.assertEqual(context.author_name, "TestUser")
        self.assertEqual(context.author_id, "123")
        self.assertEqual(context.role, "USER")
        self.assertEqual(context.message_type, MessageType.REGULAR_CHAT)
        self.assertFalse(context.requires_throttling)
        self.assertEqual(context.raw_message, {"test": "data"})

if __name__ == '__main__':
    unittest.main()