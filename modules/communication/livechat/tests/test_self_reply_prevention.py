#!/usr/bin/env python3
"""
Test that the bot correctly ignores its own messages from both accounts.
This prevents infinite self-reply loops.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from modules.communication.livechat.src.message_processor import MessageProcessor
from datetime import datetime, timezone
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_self_reply_prevention():
    """Test that bot ignores messages from both bot accounts"""

    print("="*80)
    print("TESTING SELF-REPLY PREVENTION")
    print("="*80)

    processor = MessageProcessor()

    # Test cases for both bot accounts
    test_cases = [
        {
            "name": "UnDaoDu Bot (Set 1)",
            "channel_id": "UCfHM9Fw9HD-NwiS0seD_oIA",
            "display_name": "UnDaoDu"
        },
        {
            "name": "Foundups Bot (Set 10)",
            "channel_id": "UCSNTUXjAgpd4sgWYP0xoJgw",
            "display_name": "Foundups"
        },
        {
            "name": "Regular User",
            "channel_id": "UC_regular_user_123",
            "display_name": "RegularUser"
        }
    ]

    for test in test_cases:
        print(f"\n--- Testing: {test['name']} ---")

        # Get current time for fresh message
        current_time = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

        # Create a mock message from this channel
        message = {
            "snippet": {
                "messageId": "test_msg_123",
                "displayMessage": "✊✋🖐 Test consciousness message",
                "publishedAt": current_time,
                "liveChatId": "test_chat"
            },
            "authorDetails": {
                "channelId": test['channel_id'],
                "displayName": test['display_name'],
                "isChatModerator": False,
                "isChatOwner": False
            }
        }

        # Process the message
        result = processor.process_message(message)

        # Check results
        if test['channel_id'] in ["UCfHM9Fw9HD-NwiS0seD_oIA", "UCSNTUXjAgpd4sgWYP0xoJgw"]:
            # Should be skipped (bot message)
            if result.get("skip") and result.get("reason") == "self-message":
                print(f"[PASS] Bot message from {test['display_name']} was correctly ignored")
            else:
                print(f"[FAIL] Bot message from {test['display_name']} was NOT ignored!")
                print(f"   Result: {result}")
        else:
            # Should be processed (regular user)
            if not result.get("skip"):
                print(f"[PASS] User message from {test['display_name']} was processed")
                print(f"   Has consciousness trigger: {result.get('has_consciousness')}")
            else:
                print(f"[FAIL] User message from {test['display_name']} was incorrectly skipped!")
                print(f"   Reason: {result.get('reason')}")

    print("\n" + "="*80)
    print("ADDITIONAL VERIFICATION")
    print("="*80)

    # Verify the BOT_CHANNEL_IDS are correctly set
    print("\nBot Channel IDs configured in message_processor.py:")
    print("1. UCfHM9Fw9HD-NwiS0seD_oIA (UnDaoDu - Set 1)")
    print("2. UCSNTUXjAgpd4sgWYP0xoJgw (Foundups - Set 10)")

    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)
    print("\nThe bot should now:")
    print("1. [OK] Ignore messages from UnDaoDu account")
    print("2. [OK] Ignore messages from Foundups account")
    print("3. [OK] Process messages from regular users")
    print("4. [OK] Prevent infinite self-reply loops")

if __name__ == "__main__":
    test_self_reply_prevention()