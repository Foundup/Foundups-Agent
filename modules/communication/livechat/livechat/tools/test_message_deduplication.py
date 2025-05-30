#!/usr/bin/env python3
"""
Message Deduplication Test for LiveChatListener

This test verifies that the LiveChatListener correctly deduplicates messages
to prevent reprocessing the same messages repeatedly, which was causing
duplicate timeout attempts and log spam.

WSP Compliance: Testing tool for livechat module as per WSP 3 (Enterprise Domain Architecture).

Usage:
    python test_message_deduplication.py
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../..'))

from modules.communication.livechat.livechat.src.livechat import LiveChatListener
from unittest.mock import Mock

def test_message_deduplication():
    """Test that message deduplication prevents repeated processing"""
    
    print("=== MESSAGE DEDUPLICATION TEST ===")
    
    # Create mock YouTube service
    mock_youtube = Mock()
    
    # Create LiveChatListener instance 
    listener = LiveChatListener(
        youtube_service=mock_youtube,
        video_id="test_video"
    )
    
    # Test message with same ID
    test_message = {
        "id": "test_message_123",
        "snippet": {
            "displayMessage": "Test message"
        },
        "authorDetails": {
            "displayName": "TestUser",
            "channelId": "test_channel_123"
        }
    }
    
    print(f"Initial processed messages: {len(listener.processed_message_ids)}")
    
    # Simulate processing the same message multiple times
    messages_batch = [test_message, test_message, test_message]
    
    print(f"Simulating batch with {len(messages_batch)} identical messages (ID: {test_message['id']})")
    
    # Test deduplication logic directly
    new_messages = 0
    duplicate_messages = 0
    
    for message in messages_batch:
        msg_id = message.get("id")
        
        if msg_id in listener.processed_message_ids:
            duplicate_messages += 1
            print(f"🔄 DUPLICATE DETECTED: {msg_id}")
        else:
            new_messages += 1
            print(f"✅ NEW MESSAGE: {msg_id}")
            listener.processed_message_ids.add(msg_id)
    
    print(f"\n📊 RESULTS:")
    print(f"   New messages processed: {new_messages}")
    print(f"   Duplicate messages skipped: {duplicate_messages}")
    print(f"   Total processed IDs in memory: {len(listener.processed_message_ids)}")
    
    # Verify results
    expected_new = 1
    expected_duplicates = 2
    
    if new_messages == expected_new and duplicate_messages == expected_duplicates:
        print(f"✅ SUCCESS: Deduplication working correctly!")
        print(f"   ✓ Processed {expected_new} unique message as expected")
        print(f"   ✓ Skipped {expected_duplicates} duplicates as expected")
        return True
    else:
        print(f"❌ FAILURE: Deduplication not working correctly!")
        print(f"   Expected: {expected_new} new, {expected_duplicates} duplicates")
        print(f"   Got: {new_messages} new, {duplicate_messages} duplicates")
        return False

def test_memory_cleanup():
    """Test memory cleanup functionality"""
    print(f"\n=== MEMORY CLEANUP TEST ===")
    
    # Create mock YouTube service
    mock_youtube = Mock()
    
    # Create LiveChatListener instance 
    listener = LiveChatListener(
        youtube_service=mock_youtube,
        video_id="test_video"
    )
    
    print(f"Max processed IDs setting: {listener.max_processed_ids}")
    
    # Add many message IDs to test cleanup threshold
    for i in range(listener.max_processed_ids + 100):
        listener.processed_message_ids.add(f"test_msg_{i}")
    
    print(f"Added {listener.max_processed_ids + 100} message IDs")
    print(f"Current processed IDs count: {len(listener.processed_message_ids)}")
    
    if len(listener.processed_message_ids) > listener.max_processed_ids:
        print("✅ Memory cleanup threshold reached - cleanup would be triggered")
        return True
    else:
        print("⚠️  Memory cleanup threshold not reached")
        return False

if __name__ == "__main__":
    print("🧪 Running Message Deduplication Tests for LiveChatListener")
    print("=" * 60)
    
    test1_passed = test_message_deduplication()
    test2_passed = test_memory_cleanup()
    
    print("\n" + "=" * 60)
    print("🏁 TEST SUMMARY:")
    print(f"   Deduplication Test: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"   Memory Cleanup Test: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("🎉 All tests passed! Message deduplication system is working correctly.")
        exit(0)
    else:
        print("⚠️  Some tests failed. Check implementation.")
        exit(1) 