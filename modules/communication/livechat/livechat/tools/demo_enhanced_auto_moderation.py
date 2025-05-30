#!/usr/bin/env python3
"""
Enhanced Auto-Moderation System Demonstration

This script demonstrates the enhanced auto-moderation functionality that detects:
1. Banned phrases (original functionality)  
2. Spam rate limiting (5+ messages in 30 seconds)
3. Repetitive/similar content detection (3+ similar messages)
4. Escalating timeout durations for repeat offenders

WSP Compliance: Enhanced demonstration tool for comprehensive spam detection
integrated into the LiveChat module as per WSP 3 (Enterprise Domain Architecture).

Usage:
    python demo_enhanced_auto_moderation.py
"""

import sys
import os
import time
from unittest.mock import Mock

# Add the src directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from auto_moderator import AutoModerator


def demo_banned_phrase_detection():
    """Demonstrate banned phrase detection (original functionality)."""
    print("🔍 BANNED PHRASE DETECTION DEMO")
    print("=" * 50)
    
    mock_youtube = Mock()
    auto_mod = AutoModerator(mock_youtube)
    
    test_messages = [
        "MAGA 2028 is coming!",
        "I Love Trump so much!",
        "Trump is Jesus Christ!",
        "Make America Great Again 2028",
        "Hello everyone! Great stream!",
        "This is normal chat",
    ]
    
    print(f"Testing {len(test_messages)} messages for banned phrases...\n")
    
    for i, message in enumerate(test_messages, 1):
        is_banned, reason = auto_mod.check_message(message, f"user_{i}", f"TestUser{i}")
        status = f"🚫 BANNED ({reason})" if is_banned else "✅ CLEAN"
        print(f"{i:2d}. {status} | {message}")
    
    print()


def demo_rate_limiting():
    """Demonstrate spam rate limiting detection."""
    print("\n📊 SPAM RATE LIMITING DEMO")
    print("=" * 50)
    
    mock_youtube = Mock()
    auto_mod = AutoModerator(mock_youtube)
    
    # Simulate rapid-fire messages from the same user
    rapid_messages = [
        "Hello!",
        "Anyone here?", 
        "Chat is dead",
        "Wake up chat!",
        "Boring stream",
        "This is message 6",  # This should trigger rate limit
    ]
    
    user_id = "spammer_123"
    user_name = "SpamUser"
    
    print(f"Simulating {len(rapid_messages)} rapid messages from {user_name}...")
    print(f"Rate limit: {auto_mod.spam_rate_limit} messages per {auto_mod.spam_time_window}s\n")
    
    for i, message in enumerate(rapid_messages, 1):
        print(f"Message {i}: \"{message}\"")
        
        # Simulate rapid sending (small time gaps)
        if i > 1:
            time.sleep(0.1)  # Very small delay to simulate rapid sending
        
        is_violation, reason = auto_mod.check_message(message, user_id, user_name)
        
        if is_violation:
            print(f"   → 🚫 SPAM DETECTED: {reason}")
        else:
            print(f"   → ✅ Message allowed")
        print()


def demo_repetitive_content():
    """Demonstrate repetitive content detection."""
    print("\n🔄 REPETITIVE CONTENT DETECTION DEMO")
    print("=" * 50)
    
    mock_youtube = Mock()
    auto_mod = AutoModerator(mock_youtube)
    
    # Simulate repetitive messages
    repetitive_messages = [
        "FIRST COMMENT!!!",
        "First comment!!",  # Very similar to first
        "FIRST COMMENT!",   # Very similar again
        "First comment",    # Similar again - should trigger
    ]
    
    user_id = "repeat_user_456"
    user_name = "RepeatUser"
    
    print(f"Simulating repetitive messages from {user_name}...")
    print(f"Similarity threshold: {auto_mod.similarity_threshold*100}%")
    print(f"Repetitive count threshold: {auto_mod.repetitive_count_threshold}\n")
    
    for i, message in enumerate(repetitive_messages, 1):
        print(f"Message {i}: \"{message}\"")
        
        is_violation, reason = auto_mod.check_message(message, user_id, user_name)
        
        if is_violation:
            print(f"   → 🚫 REPETITIVE SPAM: {reason}")
        else:
            print(f"   → ✅ Message allowed")
        print()


def demo_user_tracking():
    """Demonstrate user violation tracking and escalation."""
    print("\n👤 USER TRACKING & ESCALATION DEMO")
    print("=" * 50)
    
    mock_youtube = Mock()
    auto_mod = AutoModerator(mock_youtube)
    
    # Simulate multiple violations from the same user
    user_id = "problem_user_789"
    user_name = "ProblemUser"
    
    violations = [
        ("MAGA 2028!", "banned phrase"),
        ("spam spam spam spam spam spam", "rate limiting after rapid fire"),
        ("Trump is Jesus!", "banned phrase again"),
    ]
    
    print(f"Simulating multiple violations from {user_name}...\n")
    
    for i, (message, description) in enumerate(violations, 1):
        print(f"Violation {i} ({description}): \"{message}\"")
        
        # First simulate the violation
        is_violation, reason = auto_mod.check_message(message, user_id, user_name)
        
        if is_violation:
            print(f"   → 🚫 VIOLATION: {reason}")
            
            # Check escalation
            violation_count = auto_mod.user_violations[user_id] + 1  # +1 because it will be incremented
            if violation_count >= 3:
                timeout_duration = 300  # 5 minutes
            elif violation_count >= 2:
                timeout_duration = 180  # 3 minutes  
            else:
                timeout_duration = 60   # 1 minute
            
            print(f"   → ⏰ Timeout duration: {timeout_duration}s (violation #{violation_count})")
            
            # Simulate the violation being recorded
            auto_mod.user_violations[user_id] = violation_count
        else:
            print(f"   → ✅ No violation detected")
        print()


def demo_stats_and_management():
    """Demonstrate statistics and user management features."""
    print("\n📈 STATISTICS & MANAGEMENT DEMO")
    print("=" * 50)
    
    mock_youtube = Mock()
    auto_mod = AutoModerator(mock_youtube)
    
    # Simulate some activity
    test_users = [
        ("good_user_1", ["Hello!", "Nice stream", "Thanks for content"]),
        ("spam_user_2", ["MAGA 2028!", "spam spam spam", "Trump is Jesus!"]),
        ("repeat_user_3", ["First!", "First!!", "FIRST!!!"]),
    ]
    
    print("Simulating various user behaviors...\n")
    
    for user_id, messages in test_users:
        for msg in messages:
            is_violation, reason = auto_mod.check_message(msg, user_id, f"User_{user_id}")
            if is_violation:
                auto_mod.user_violations[user_id] = auto_mod.user_violations.get(user_id, 0) + 1
    
    # Show statistics
    stats = auto_mod.get_stats()
    print("📊 MODERATION STATISTICS:")
    print(f"   Banned phrases: {stats['banned_phrases_count']}")
    print(f"   Users with violations: {stats['users_with_violations']}")
    print(f"   Total violations: {stats['total_user_violations']}")
    print(f"   Tracked users: {stats['tracked_users']}")
    print(f"   Rate limit: {stats['spam_rate_limit']} msgs/{stats['spam_time_window']}s")
    print(f"   Similarity threshold: {stats['similarity_threshold']}%")
    print()
    
    # Show top violators
    print("🏆 TOP VIOLATORS:")
    top_violators = auto_mod.get_top_violators(5)
    for i, violator in enumerate(top_violators, 1):
        print(f"   {i}. User {violator['user_id']}: {violator['violation_count']} violations")
    print()
    
    # Demonstrate settings adjustment
    print("⚙️ ADJUSTING SETTINGS:")
    old_new = auto_mod.adjust_spam_settings(
        rate_limit=3,  # Stricter rate limiting
        similarity_threshold=0.7  # Lower similarity threshold
    )
    print(f"   Rate limit: {old_new['old']['rate_limit']} → {old_new['new']['rate_limit']}")
    print(f"   Similarity threshold: {old_new['old']['similarity_threshold']} → {old_new['new']['similarity_threshold']}")


def demo_political_spam_detection():
    """
    Demo political spam detection with comprehensive MAGA/Trump spam patterns.
    """
    print("\n🚨 === POLITICAL SPAM DETECTION DEMO ===")
    
    # Create mock YouTube service
    mock_youtube = Mock()
    auto_mod = AutoModerator(mock_youtube)
    
    # Political spam test cases
    political_spam_messages = [
        "MAGA 2028 is coming!",
        "Trump 2028 will save America!",
        "Make America Great Again 2028",
        "MAGA forever patriots!",
        "Trump train has no brakes!",
        "WWG1WGA trust the plan",
        "Stop the steal! Election fraud everywhere!",
        "Let's go Brandon! FJB!",
        "Trump is our savior and messiah",
        "God Emperor Trump rules all",
        "Civil war now! Take back America!",
        "All hail Trump, bow to daddy Trump",
        "January 6th patriots are heroes",
        "Nothing can stop what is coming",
        "Deep state vs Trump",
        "Fight fight fight for America First!"
    ]
    
    # Test legitimate political discussion (should NOT trigger)
    legitimate_messages = [
        "I disagree with Trump's policies",
        "Biden won the 2020 election",
        "Trump was president from 2017-2021",
        "Political discussion is important",
        "Vote in elections",
        "Democracy matters"
    ]
    
    print("🔴 Testing Political Spam (Should be detected):")
    spam_detected = 0
    for i, message in enumerate(political_spam_messages, 1):
        violation_detected, reason = auto_mod.check_message(message, f"spammer_{i}", f"Spammer{i}")
        status = "🚨 DETECTED" if violation_detected else "❌ MISSED"
        print(f"  {i:2d}. {status}: '{message}' -> {reason}")
        if violation_detected:
            spam_detected += 1
    
    print(f"\n✅ Spam Detection Rate: {spam_detected}/{len(political_spam_messages)} ({100*spam_detected/len(political_spam_messages):.1f}%)")
    
    print("\n🟢 Testing Legitimate Political Discussion (Should NOT be detected):")
    false_positives = 0
    for i, message in enumerate(legitimate_messages, 1):
        violation_detected, reason = auto_mod.check_message(message, f"user_{i}", f"User{i}")
        status = "❌ FALSE POSITIVE" if violation_detected else "✅ ALLOWED"
        print(f"  {i:2d}. {status}: '{message}' -> {reason}")
        if violation_detected:
            false_positives += 1
    
    print(f"\n✅ False Positive Rate: {false_positives}/{len(legitimate_messages)} ({100*false_positives/len(legitimate_messages):.1f}%)")
    
    # Test case variations
    print("\n🔄 Testing Case Variations:")
    test_variations = [
        "maga 2028",           # lowercase
        "MAGA 2028",          # uppercase  
        "MaGa 2028",          # mixed case
        "Trump DADDY",        # mixed case
        "WWGOWGA trust THE plan"  # mixed case QAnon
    ]
    
    for message in test_variations:
        violation_detected, reason = auto_mod.check_message(message, "test_user", "TestUser")
        status = "🚨 DETECTED" if violation_detected else "❌ MISSED"
        print(f"  {status}: '{message}' -> {reason}")


def demo_trout_slap_messages():
    """
    Demo the classic IRC trout slap messages for different violation types.
    """
    print("\n🐟 === TROUT SLAP MESSAGES DEMO ===")
    
    # Create mock YouTube service
    mock_youtube = Mock()
    auto_mod = AutoModerator(mock_youtube)
    
    # Test different violation scenarios and their trout slaps
    violation_scenarios = [
        {
            "message": "MAGA 2028 forever!",
            "author": "PoliticalSpammer",
            "type": "Political spam"
        },
        {
            "message": "Trust the plan! WWG1WGA!",
            "author": "ConspiracyUser", 
            "type": "Conspiracy theory"
        },
        {
            "message": "spam spam spam spam spam spam",
            "author": "RegularSpammer",
            "type": "Rate limiting"
        },
        {
            "message": "Love Trump forever and ever!",
            "author": "TrumpFan2028",
            "type": "Religious/worship spam"
        }
    ]
    
    print("Testing trout slap message generation for different violation types:\n")
    
    for i, scenario in enumerate(violation_scenarios, 1):
        # Get violation result
        violation_detected, reason = auto_mod.check_message(
            scenario["message"], 
            f"user_{i}", 
            scenario["author"]
        )
        
        if violation_detected:
            print(f"{i}. {scenario['type']} - {scenario['author']}")
            print(f"   Message: \"{scenario['message']}\"")
            print(f"   Violation: {reason}")
            
            # Show what trout slap would be sent (simulate the selection logic)
            import random
            random.seed(42)  # For consistent demo output
            
            # Simulate trout slap message selection
            trout_slaps = [
                f"🐟 *slaps {scenario['author']} around a bit with a large trout* 🐟",
                f"🐟 *whacks {scenario['author']} with a mighty salmon for 60s* 🐟",
                f"🐟 *bonks {scenario['author']} with a hefty halibut* - Chat rules matter! 🐟"
            ]
            
            political_slaps = [
                f"🐟 *slaps {scenario['author']} with a democracy-defending trout* - Political spam is not welcome! 🐟",
                f"🐟 *whacks {scenario['author']} with a bipartisan bass* - Keep politics civil or stay quiet! 🐟"
            ]
            
            conspiracy_slaps = [
                f"🐟 *slaps {scenario['author']} with a fact-checking flounder* - Conspiracy theories not allowed! 🐟",
                f"🐟 *whacks {scenario['author']} with a reality-checking ray* - Stay grounded in facts! 🐟"
            ]
            
            # Choose appropriate slap based on violation reason
            if "banned_phrase" in reason and any(phrase in reason for phrase in ["maga", "trump", "biden", "election"]):
                if any(phrase in reason for phrase in ["deep state", "trust the plan", "storm", "wwg1wga"]):
                    slap_message = random.choice(conspiracy_slaps)
                else:
                    slap_message = random.choice(political_slaps)
            else:
                slap_message = random.choice(trout_slaps)
            
            print(f"   🐟 Trout Slap: {slap_message}")
            print()
        else:
            print(f"{i}. No violation detected for: \"{scenario['message']}\"")
            print()
    
    print("🎣 Classic IRC moderation brought to modern YouTube Live Chat!")
    print("The trout slap messages will be automatically sent to chat when users are timed out.")


def main():
    """Run all demonstration scenarios."""
    print("🛡️ ENHANCED AUTO-MODERATION SYSTEM DEMO")
    print("=" * 60)
    print("This demo shows comprehensive spam detection including:")
    print("• Banned phrase detection")
    print("• Rate limiting (messages per time window)")
    print("• Repetitive/similar content detection") 
    print("• User violation tracking with escalation")
    print("• Statistics and management features")
    print("=" * 60)
    
    demo_banned_phrase_detection()
    demo_rate_limiting()
    demo_repetitive_content()
    demo_user_tracking()
    demo_stats_and_management()
    demo_political_spam_detection()
    demo_trout_slap_messages()
    
    print("\n✅ DEMO COMPLETE!")
    print("The enhanced AutoModerator now provides comprehensive")
    print("protection against both political spam and general spam patterns!")


if __name__ == "__main__":
    main() 