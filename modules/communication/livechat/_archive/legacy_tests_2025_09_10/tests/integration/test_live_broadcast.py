#!/usr/bin/env python3
"""
Test the live broadcast and consciousness features
"""

import sys
import os
import asyncio
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.communication.livechat.src.session_manager import SessionManager
from modules.communication.livechat.src.message_processor import MessageProcessor

async def test_broadcast():
    print("[U+1F52C] Testing 0102 Live Broadcast System\n")
    print("=" * 60)
    
    # Mock YouTube service
    class MockYouTube:
        def videos(self):
            return self
        def list(self, **kwargs):
            return self
        def execute(self):
            return {
                'items': [{
                    'liveStreamingDetails': {'activeLiveChatId': 'test-chat-123'},
                    'snippet': {
                        'title': 'Test Stream for 0102 Testing',
                        'channelTitle': 'Test Channel',
                        'channelId': 'test-channel-123'
                    }
                }]
            }
    
    # Mock send function to capture messages
    sent_messages = []
    async def mock_send(message):
        print(f"[U+1F4E4] SENT TO CHAT: {message}")
        sent_messages.append(message)
        return True
    
    # Initialize session manager
    youtube_service = MockYouTube()
    session = SessionManager(youtube_service, "test-video-123")
    
    # Initialize session
    print("\n[ROCKET] Initializing session...")
    await session.initialize_session()
    print(f"[OK] Session initialized: {session.stream_title_short}")
    
    # Send greeting and update broadcast
    print("\n[U+1F4E2] Sending greeting and update broadcast...")
    await session.send_greeting(mock_send)
    
    print("\n" + "=" * 60)
    print("[CLIPBOARD] Summary of messages sent:")
    for i, msg in enumerate(sent_messages, 1):
        print(f"{i}. {msg}")
    
    print("\n" + "=" * 60)
    
    # Test message processor with consciousness commands
    print("\n[AI] Testing consciousness message processing...")
    processor = MessageProcessor()
    
    test_messages = [
        {
            "snippet": {"displayMessage": "[U+270A][U+270B][U+1F590]️ hello 0102!"},
            "authorDetails": {
                "displayName": "TestUser1",
                "channelId": "user1",
                "isChatModerator": False,
                "isChatOwner": False
            }
        },
        {
            "snippet": {"displayMessage": "[U+270A][U+270B][U+1F590]️FC @MAGATroll"},
            "authorDetails": {
                "displayName": "ModUser",
                "channelId": "mod1",
                "isChatModerator": True,
                "isChatOwner": False
            }
        },
        {
            "snippet": {"displayMessage": "[U+270A][U+270B][U+1F590]️ what is consciousness?"},
            "authorDetails": {
                "displayName": "CuriousUser",
                "channelId": "user2",
                "isChatModerator": False,
                "isChatOwner": False
            }
        }
    ]
    
    for msg_data in test_messages:
        print("\n" + "-" * 40)
        username = msg_data["authorDetails"]["displayName"]
        message = msg_data["snippet"]["displayMessage"]
        print(f"[U+1F4E5] {username}: {message}")
        
        # Process message
        processed = processor.process_message(msg_data)
        
        # Generate response
        if processed and not processed.get("skip"):
            response = await processor.generate_response(processed)
            if response:
                print(f"[U+1F4AC] 0102: {response}")
            else:
                print(f"[U+1F507] No response generated")
    
    print("\n[OK] Test completed!")

if __name__ == "__main__":
    asyncio.run(test_broadcast())