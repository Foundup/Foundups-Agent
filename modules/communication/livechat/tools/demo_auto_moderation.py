#!/usr/bin/env python3
"""
Auto-Moderation System Demonstration

This script demonstrates the auto-moderation functionality that automatically
detects banned phrases like "MAGA 2028", "Love Trump", "Trump is Jesus", etc.
and applies 10-second timeouts to users.

WSP Compliance: Demonstration tool for auto-moderation functionality
integrated into the LiveChat module as per WSP 3 (Enterprise Domain Architecture).

Usage:
    python demo_auto_moderation.py
"""

import sys
import os
from unittest.mock import Mock

# Add the src directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from auto_moderator import AutoModerator


def demo_banned_phrase_detection():
    """Demonstrate banned phrase detection."""
    print("🔍 BANNED PHRASE DETECTION DEMO")
    print("=" * 50)
    
    # Create a mock YouTube service (for demo purposes)
    mock_youtube = Mock()
    auto_mod = AutoModerator(mock_youtube)
    
    # Test messages
    test_messages = [
        "MAGA 2028 is coming!",
        "I Love Trump so much!",
        "Trump is Jesus Christ!",
        "Make America Great Again 2028",
        "trump forever and ever",
        "God Emperor Trump rules!",
        "This is a normal message",
        "I love pizza",
        "Trump news today",  # Should not trigger
        "MAGA hat",  # Should not trigger (not the full phrase)
        "Hello everyone! How's your day?",
        "Great stream today!",
    ]
    
    print(f"Testing {len(test_messages)} messages for banned phrases...\n")
    
    for i, message in enumerate(test_messages, 1):
        is_banned = auto_mod.contains_banned_phrase(message)
        status = "🚫 BANNED" if is_banned else "✅ CLEAN"
        print(f"{i:2d}. {status} | {message}")
    
    print(f"\nBanned phrases configured: {len(auto_mod.banned_phrases)}")
    print("Sample banned phrases:", list(auto_mod.banned_phrases)[:5])


def demo_timeout_logic():
    """Demonstrate timeout cooldown logic."""
    print("\n\n⏰ TIMEOUT COOLDOWN LOGIC DEMO")
    print("=" * 50)
    
    mock_youtube = Mock()
    auto_mod = AutoModerator(mock_youtube)
    
    user_id = "demo_user_123"
    
    print(f"User ID: {user_id}")
    print(f"Timeout duration: {auto_mod.timeout_duration} seconds")
    print(f"Cooldown period: {auto_mod.timeout_cooldown} seconds\n")
    
    # First timeout attempt
    can_timeout = auto_mod.should_timeout_user(user_id)
    print(f"1. First timeout attempt: {'✅ ALLOWED' if can_timeout else '🚫 BLOCKED'}")
    
    if can_timeout:
        # Simulate recording the timeout
        import time
        auto_mod.recent_timeouts[user_id] = time.time()
        print("   → Timeout recorded")
    
    # Immediate retry
    can_timeout = auto_mod.should_timeout_user(user_id)
    print(f"2. Immediate retry: {'✅ ALLOWED' if can_timeout else '🚫 BLOCKED (cooldown active)'}")
    
    # Show cooldown status
    if user_id in auto_mod.recent_timeouts:
        time_since = time.time() - auto_mod.recent_timeouts[user_id]
        remaining = max(0, auto_mod.timeout_cooldown - time_since)
        print(f"   → Cooldown remaining: {remaining:.1f} seconds")


def demo_message_processing():
    """Demonstrate full message processing."""
    print("\n\n📨 MESSAGE PROCESSING DEMO")
    print("=" * 50)
    
    mock_youtube = Mock()
    auto_mod = AutoModerator(mock_youtube)
    
    # Mock successful timeout response
    mock_youtube.liveChatBans().insert().execute.return_value = {"id": "ban_123"}
    
    test_messages = [
        {
            'authorDetails': {'channelId': 'user_001'},
            'snippet': {'displayMessage': 'Hello everyone!'}
        },
        {
            'authorDetails': {'channelId': 'user_002'},
            'snippet': {'displayMessage': 'MAGA 2028 forever!'}
        },
        {
            'authorDetails': {'channelId': 'user_003'},
            'snippet': {'displayMessage': 'Love Trump so much!'}
        },
        {
            'authorDetails': {'channelId': 'user_002'},  # Same user again
            'snippet': {'displayMessage': 'Trump is Jesus!'}
        }
    ]
    
    chat_id = "demo_chat_456"
    
    print(f"Processing {len(test_messages)} messages...\n")
    
    for i, message in enumerate(test_messages, 1):
        user_id = message['authorDetails']['channelId']
        text = message['snippet']['displayMessage']
        
        print(f"{i}. User {user_id}: \"{text}\"")
        
        was_moderated = auto_mod.process_message(message, chat_id)
        
        if was_moderated:
            print("   → 🚫 MESSAGE MODERATED - User timed out for 10 seconds")
        else:
            contains_banned = auto_mod.contains_banned_phrase(text)
            if contains_banned:
                print("   → ⏰ Banned phrase detected but user on cooldown")
            else:
                print("   → ✅ Message allowed")
        print()


def demo_statistics():
    """Demonstrate statistics gathering."""
    print("\n📊 MODERATION STATISTICS DEMO")
    print("=" * 50)
    
    mock_youtube = Mock()
    auto_mod = AutoModerator(mock_youtube)
    
    # Add some fake timeout data
    import time
    auto_mod.recent_timeouts = {
        'user_001': time.time() - 30,   # 30 seconds ago
        'user_002': time.time() - 120,  # 2 minutes ago
        'user_003': time.time() - 45,   # 45 seconds ago
    }
    
    stats = auto_mod.get_stats()
    
    print("Current moderation statistics:")
    print(f"  • Timeout duration: {stats['timeout_duration']} seconds")
    print(f"  • Cooldown period: {stats['timeout_cooldown']} seconds")
    print(f"  • Banned phrases configured: {stats['banned_phrases_count']}")
    print(f"  • Recent timeouts: {stats['recent_timeouts_count']}")
    print(f"  • Sample banned phrases: {list(stats['banned_phrases'])[:3]}")


def main():
    """Run all demonstrations."""
    print("🤖 AUTO-MODERATION SYSTEM DEMONSTRATION")
    print("=" * 60)
    print("This demo shows how the system automatically detects banned")
    print("phrases and applies 10-second timeouts to users.")
    print("=" * 60)
    
    try:
        demo_banned_phrase_detection()
        demo_timeout_logic()
        demo_message_processing()
        demo_statistics()
        
        print("\n\n✅ DEMONSTRATION COMPLETE")
        print("=" * 50)
        print("The auto-moderation system is ready to:")
        print("  • Detect banned phrases in real-time")
        print("  • Apply 10-second timeouts automatically")
        print("  • Respect cooldown periods to prevent spam")
        print("  • Handle API errors gracefully")
        print("  • Provide detailed statistics")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 