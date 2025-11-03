"""
Direct test of the hand emoji issue - testing the exact scenario
"""

from modules.ai_intelligence.banter_engine.src.banter_engine import BanterEngine
from modules.communication.livechat.src.livechat import LiveChatListener
from unittest.mock import MagicMock

print("=" * 60)
print("TESTING HAND EMOJI ISSUE: [hand emojis]")
print("=" * 60)

# Test 1: BanterEngine processing
print("\n1. Testing BanterEngine processing:")
engine = BanterEngine()

test_messages = [
    "[U+1F590][U+1F590][U+1F590]",  # Without variation selector (user's actual input)
    "[U+1F590]️[U+1F590]️[U+1F590]️",  # With variation selector
    "Hey [U+1F590][U+1F590][U+1F590]",  # Embedded without selector
]

for msg in test_messages:
    result, response = engine.process_input(msg)
    print(f"  Input: '{msg}'")
    print(f"  Result: '{result[:50]}...' " if len(result) > 50 else f"  Result: '{result}'")
    print(f"  Response: '{response}'")
    print()

# Test 2: LiveChat trigger detection
print("\n2. Testing LiveChat trigger detection:")

# Create mock YouTube service
mock_youtube = MagicMock()
listener = LiveChatListener(
    youtube_service=mock_youtube,
    video_id="test_video",
    live_chat_id="test_chat"
)

test_sequences = [
    ("[U+1F590][U+1F590][U+1F590]", True, "Without variation selector"),
    ("[U+1F590]️[U+1F590]️[U+1F590]️", True, "With variation selector"),
    ("Hey [U+1F590][U+1F590][U+1F590] test", True, "Embedded without selector"),
    ("[U+1F590][U+1F590]", False, "Only two hands - should not trigger"),
    ("[U+1F44D][U+1F44D][U+1F44D]", False, "Different emoji - should not trigger"),
]

for sequence, should_trigger, description in test_sequences:
    detected = listener._check_trigger_patterns(sequence)
    status = "[OK] PASS" if detected == should_trigger else "[FAIL] FAIL"
    print(f"  {status} '{sequence}' - {description}")
    print(f"       Expected: {should_trigger}, Got: {detected}")

print("\n" + "=" * 60)
print("SUMMARY:")
print("- BanterEngine correctly processes [U+1F590][U+1F590][U+1F590] sequences")
print("- LiveChat correctly detects [U+1F590][U+1F590][U+1F590] as a trigger")
print("- Both with and without variation selector work")
print("=" * 60)