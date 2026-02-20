#!/usr/bin/env python3
"""Quick test for holiday awareness."""
import sys
sys.path.insert(0, 'O:/Foundups-Agent')

from modules.communication.livechat.src.holiday_awareness import (
    get_holiday_context,
    get_session_holiday_greeting,
    get_countdown_message
)

print("=" * 50)
print("HOLIDAY AWARENESS TEST")
print("=" * 50)

ctx = get_holiday_context()
print(f"\nContext: {ctx}")

greeting = get_session_holiday_greeting()
print(f"\nSession Greeting: {greeting}")

countdown = get_countdown_message()
print(f"\nCountdown Message: {countdown}")

print("\n" + "=" * 50)
