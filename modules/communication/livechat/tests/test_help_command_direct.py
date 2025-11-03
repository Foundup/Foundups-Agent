"""
Direct test of /help command processing
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from modules.communication.livechat.src.message_processor import MessageProcessor

def test_help_detection():
    """Test that /help is detected as a whack command"""
    processor = MessageProcessor()
    
    # Test detection
    assert processor._check_whack_command("/help") == True
    assert processor._check_whack_command("/Help") == True
    assert processor._check_whack_command("/HELP") == True
    assert processor._check_whack_command("  /help  ") == True
    
    print("[OK] /help detection works!")

def test_help_processing():
    """Test that /help generates a response"""
    processor = MessageProcessor()
    
    # Create a test message
    test_message = {
        "snippet": {
            "displayMessage": "/help",
            "publishedAt": "2025-08-28T00:00:00Z"
        },
        "authorDetails": {
            "displayName": "TestUser",
            "channelId": "test_channel_id",
            "isChatOwner": False,
            "isChatModerator": False
        }
    }
    
    # Process the message
    processed = processor.process_message(test_message)
    print(f"Processed message: {processed}")
    
    assert processed.get("has_whack_command") == True
    print("[OK] /help is detected as whack command!")
    
    # Now test response generation
    import asyncio
    
    async def test_response():
        response = await processor.generate_response(processed)
        print(f"Generated response: {response}")
        assert response is not None
        assert "MAGADOOM" in response
        return response
    
    response = asyncio.run(test_response())
    print(f"[OK] /help generates response: {response}")

if __name__ == "__main__":
    test_help_detection()
    test_help_processing()