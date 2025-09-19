#!/usr/bin/env python3
"""
Test @mention validation for 2-letter usernames like JS
Tests that messages with invalid @mentions are properly blocked
"""

import sys
import os
# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
sys.path.insert(0, project_root)

import logging
import asyncio
from modules.communication.livechat.src.chat_sender import ChatSender

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class MockYouTubeService:
    """Mock YouTube service for testing"""
    def __init__(self):
        self.messages_sent = []
    
    def liveChatMessages(self):
        return self
    
    def insert(self, part=None, body=None):
        self.messages_sent.append(body)
        return self
    
    def execute(self):
        return {"id": "test_message_id"}
    
    def channels(self):
        return self
    
    def list(self, part=None, mine=None):
        return self

async def test_mention_validation():
    """Test that @mention validation works correctly"""
    
    # Create mock service and sender
    mock_service = MockYouTubeService()
    sender = ChatSender(mock_service, "test_chat_id")
    sender.bot_channel_id = "test_bot_id"  # Skip fetching
    
    print("="*60)
    print("TESTING @MENTION VALIDATION")
    print("="*60)
    
    # Test cases
    test_cases = [
        # Valid 2-letter usernames (should SEND)
        ("@JS Welcome back! Your consciousness level is evolving!", True, "Valid 2-letter username"),
        ("@AB Test message", True, "Valid 2-letter username"),
        ("Hello @JS, how are you?", True, "Valid mid-message mention"),
        
        # Invalid single letter (should BLOCK)
        ("@J Welcome back!", False, "Single letter username"),
        ("Hi @X!", False, "Single letter username"),
        
        # Invalid with spaces/special chars (should BLOCK)  
        ("@John Doe welcome!", False, "Username with space"),
        ("@user@domain test", False, "Multiple @ symbols"),
        ("@user! test", False, "Username with exclamation"),
        
        # Common words that look like mentions (should BLOCK)
        ("You've been @mentioned", False, "Common word 'mentioned'"),
        ("Hello @everyone", False, "Common word 'everyone'"),
        
        # No mentions (should SEND)
        ("Welcome back JS! Test your consciousness!", True, "No @ symbol"),
        ("Hello world!", True, "No mentions at all"),
        
        # Complex message with mixed mentions
        ("@JS and @A are here", False, "Mixed valid and invalid - blocks entire message"),
        ("Welcome @JS and @ValidUser123!", True, "Multiple valid mentions"),
    ]
    
    print("\nTesting various @mention scenarios:\n")
    
    for message, should_send, description in test_cases:
        # Reset messages
        mock_service.messages_sent = []
        
        # Try to send
        result = await sender.send_message(message, skip_delay=True)
        
        # Check result
        if should_send:
            if result:
                status = "PASS: SENT (as expected)"
            else:
                status = "FAIL: BLOCKED (should have sent!)"
        else:
            if result:
                status = "FAIL: SENT (should have blocked!)"
            else:
                status = "PASS: BLOCKED (as expected)"
        
        print(f"{status}: {description}")
        print(f"   Message: {message}")
        if not result and '@' in message:
            print(f"   Reason: Invalid @mention detected")
        print()
    
    print("="*60)
    print("TEST COMPLETE")
    print("="*60)
    
    # Test the _is_valid_mention function directly
    print("\nDirect validation tests:")
    print("-"*40)
    
    usernames_to_test = [
        ("JS", True, "2-letter username"),
        ("J", False, "1-letter username"),
        ("ABC", True, "3-letter username"),
        ("John Doe", False, "Contains space"),
        ("user@domain", False, "Contains @"),
        ("mentioned", False, "Common word"),
        ("ValidUser123", True, "Normal username"),
        ("", False, "Empty string"),
    ]
    
    for username, expected, description in usernames_to_test:
        result = sender._is_valid_mention(username)
        status = "PASS" if result == expected else "FAIL"
        print(f"{status} '{username}': {result} ({description})")

if __name__ == "__main__":
    asyncio.run(test_mention_validation())