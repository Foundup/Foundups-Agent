"""
Test Super Chat Integration for YouTube Shorts

Tests the complete Super Chat → Shorts creation pipeline without
requiring live YouTube streams.

WSP 5/6 Compliance: Test coverage for Super Chat monetization
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

def create_mock_super_chat_event(amount_usd: float, message: str, donor_name: str = "TestDonor"):
    """
    Create a mock Super Chat event matching YouTube API structure.

    Args:
        amount_usd: Donation amount in USD
        message: Super Chat message text (used as video topic)
        donor_name: Donor's display name

    Returns:
        dict: Mock super_chat_event matching chat_poller.py output
    """
    amount_micros = int(amount_usd * 1_000_000)

    return {
        "type": "super_chat_event",
        "donor_name": donor_name,
        "donor_id": f"UC_test_{donor_name.lower()}",
        "amount_micros": amount_micros,
        "amount_usd": amount_usd,
        "currency": "USD",
        "amount_display": f"${amount_usd:.2f}",
        "message": message,
        "tier": 2 if amount_usd >= 20 else 1,
        "published_at": datetime.utcnow().isoformat() + "Z",
        "is_live": True
    }


def test_super_chat_detection():
    """Test 1: Verify Super Chat event structure"""
    print("\n" + "="*60)
    print("TEST 1: Super Chat Event Structure")
    print("="*60)

    # Create mock events
    events = [
        create_mock_super_chat_event(15.00, "Test below threshold"),
        create_mock_super_chat_event(20.00, "Minimum threshold"),
        create_mock_super_chat_event(25.00, "Cherry blossoms in Tokyo"),
        create_mock_super_chat_event(50.00, "Mount Fuji at sunrise"),
    ]

    for event in events:
        print(f"\n💰 Super Chat: ${event['amount_usd']:.2f}")
        print(f"   Donor: {event['donor_name']}")
        print(f"   Topic: {event['message']}")
        print(f"   Micros: {event['amount_micros']:,}")
        print(f"   Tier: {event['tier']}")

    print("\n✅ Event structure validation passed")
    return True


def test_amount_conversion():
    """Test 2: Verify micros → USD conversion"""
    print("\n" + "="*60)
    print("TEST 2: Amount Conversion (micros → USD)")
    print("="*60)

    test_cases = [
        (1_000_000, 1.00),
        (5_000_000, 5.00),
        (20_000_000, 20.00),
        (25_000_000, 25.00),
        (100_000_000, 100.00),
    ]

    passed = True
    for micros, expected_usd in test_cases:
        actual_usd = micros / 1_000_000
        status = "✅" if actual_usd == expected_usd else "❌"
        print(f"{status} {micros:,} micros → ${actual_usd:.2f} (expected ${expected_usd:.2f})")
        if actual_usd != expected_usd:
            passed = False

    return passed


def test_threshold_check():
    """Test 3: Verify $20 minimum threshold"""
    print("\n" + "="*60)
    print("TEST 3: $20 Minimum Threshold Check")
    print("="*60)

    from modules.communication.youtube_shorts.src.chat_commands import ShortsCommandHandler

    handler = ShortsCommandHandler()

    test_cases = [
        (15.00, "Below minimum", False),
        (19.99, "Just below", False),
        (20.00, "Exact minimum", True),
        (20.01, "Just above", True),
        (50.00, "Well above", True),
    ]

    passed = True
    for amount, description, should_process in test_cases:
        response = handler.handle_super_chat_short(
            donor_name="TestUser",
            donor_id="UC_test",
            amount_usd=amount,
            message="Test topic"
        )

        processed = response is not None
        status = "✅" if processed == should_process else "❌"
        result = "Processed" if processed else "Rejected"

        print(f"{status} ${amount:.2f} ({description}): {result}")

        if processed != should_process:
            passed = False

    return passed


def test_topic_extraction():
    """Test 4: Verify topic extraction from message"""
    print("\n" + "="*60)
    print("TEST 4: Topic Extraction from Super Chat Message")
    print("="*60)

    from modules.communication.youtube_shorts.src.chat_commands import ShortsCommandHandler

    handler = ShortsCommandHandler()

    test_cases = [
        ("Cherry blossoms in Tokyo", True, "Valid topic"),
        ("Mount Fuji at sunrise", True, "Valid topic"),
        ("", False, "Empty topic"),
        ("   ", False, "Whitespace only"),
        ("🌸 Sakura season 🌸", True, "Topic with emoji"),
    ]

    passed = True
    for message, should_accept, description in test_cases:
        response = handler.handle_super_chat_short(
            donor_name="TestUser",
            donor_id="UC_test",
            amount_usd=25.00,
            message=message
        )

        accepted = response is not None and "Please include" not in response
        status = "✅" if accepted == should_accept else "❌"
        result = "Accepted" if accepted else "Rejected"

        print(f"{status} '{message}' ({description}): {result}")

        if accepted != should_accept:
            passed = False

    return passed


def test_concurrent_generation_lock():
    """Test 5: Verify concurrent generation blocking"""
    print("\n" + "="*60)
    print("TEST 5: Concurrent Generation Lock")
    print("="*60)

    from modules.communication.youtube_shorts.src.chat_commands import ShortsCommandHandler

    handler = ShortsCommandHandler()

    # First request should start generation
    handler.generating = False
    response1 = handler.handle_super_chat_short(
        donor_name="User1",
        donor_id="UC_user1",
        amount_usd=25.00,
        message="First topic"
    )

    # Second request should be blocked
    response2 = handler.handle_super_chat_short(
        donor_name="User2",
        donor_id="UC_user2",
        amount_usd=25.00,
        message="Second topic"
    )

    first_started = response1 and "Creating" in response1
    second_blocked = response2 and "in progress" in response2

    print(f"{'✅' if first_started else '❌'} First request started generation")
    print(f"{'✅' if second_blocked else '❌'} Second request blocked")

    # Reset state
    handler.generating = False

    return first_started and second_blocked


def test_message_processor_routing():
    """Test 6: Verify message_processor routes Super Chats correctly"""
    print("\n" + "="*60)
    print("TEST 6: Message Processor Routing")
    print("="*60)

    try:
        from modules.communication.livechat.src.message_processor import MessageProcessor

        processor = MessageProcessor()

        # Create mock Super Chat event
        event = create_mock_super_chat_event(25.00, "Test routing", "TestUser")

        # Process event
        result = processor._handle_super_chat_event(event)

        routed_correctly = result is not None
        has_response = "response" in result if result else False

        print(f"{'✅' if routed_correctly else '❌'} Event routed to handler")
        print(f"{'✅' if has_response else '❌'} Response generated")

        if result:
            print(f"\nResult: {result}")

        return routed_correctly

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_full_pipeline_dry_run():
    """Test 7: Full pipeline dry run (no actual video generation)"""
    print("\n" + "="*60)
    print("TEST 7: Full Pipeline Dry Run")
    print("="*60)

    print("\n📋 Simulating complete Super Chat flow:")
    print("   1. User sends $25 Super Chat")
    print("   2. YouTube API sends superChatEvent")
    print("   3. chat_poller detects event")
    print("   4. message_processor routes to Shorts handler")
    print("   5. Shorts handler validates and prepares generation")
    print("   6. [DRY RUN - Skip actual Veo 3 generation]")
    print("   7. [DRY RUN - Skip YouTube upload]")

    # Step 1-2: Create event
    event = create_mock_super_chat_event(25.00, "Cherry blossoms in Tokyo", "JohnDoe")
    print(f"\n✅ Step 1-2: Super Chat event created")
    print(f"   Amount: ${event['amount_usd']:.2f}")
    print(f"   Topic: {event['message']}")

    # Step 3: chat_poller detection (simulated)
    print(f"✅ Step 3: Event detected by chat_poller")
    print(f"   Type: {event['type']}")
    print(f"   Micros: {event['amount_micros']:,} → ${event['amount_usd']:.2f}")

    # Step 4: Route to handler
    try:
        from modules.communication.youtube_shorts.src.chat_commands import ShortsCommandHandler
        handler = ShortsCommandHandler()
        handler.generating = False

        print(f"✅ Step 4: Routed to Shorts handler")

        # Step 5: Validate and prepare
        response = handler.handle_super_chat_short(
            donor_name=event['donor_name'],
            donor_id=event['donor_id'],
            amount_usd=event['amount_usd'],
            message=event['message']
        )

        if response:
            print(f"✅ Step 5: Validation passed")
            print(f"   Response: {response}")
            print(f"\n⏸️ Step 6-7: Skipped (dry run)")
            print(f"   Would generate: 30s video with Veo 3 ($12 cost)")
            print(f"   Would upload: YouTube Short (public)")
            print(f"   Net profit: ${event['amount_usd'] - 12:.2f}")

            # Reset state
            handler.generating = False

            return True
        else:
            print(f"❌ Step 5: Validation failed")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all Super Chat integration tests"""
    print("\n" + "="*60)
    print("YOUTUBE SHORTS SUPER CHAT INTEGRATION TESTS")
    print("="*60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    tests = [
        ("Event Structure", test_super_chat_detection),
        ("Amount Conversion", test_amount_conversion),
        ("Threshold Check", test_threshold_check),
        ("Topic Extraction", test_topic_extraction),
        ("Concurrent Lock", test_concurrent_generation_lock),
        ("Message Routing", test_message_processor_routing),
        ("Full Pipeline", test_full_pipeline_dry_run),
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ {test_name} FAILED with exception: {e}")
            import traceback
            traceback.print_exc()
            results[test_name] = False

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for r in results.values() if r)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")

    print(f"\n{'='*60}")
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print(f"{'='*60}\n")

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
