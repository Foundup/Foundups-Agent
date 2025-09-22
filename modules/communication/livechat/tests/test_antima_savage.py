#!/usr/bin/env python3
"""
Test Savage AntiMa Trolling Responses
Tests that responses are cutting and brutal against MAGA trolls
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.llm_integration import GrokIntegration

def test_savage_responses():
    """Test that responses are trolly and cutting"""

    print("Testing Savage AntiMa Trolling System")
    print("=" * 60)

    # Mock LLM connector with savage responses
    class SavageMockLLM:
        def __init__(self):
            self.response_counter = 0
            self.savage_responses = [
                "Nice strawman bro, did Fox News help you build it or are you naturally this stupid?",
                "Ad hominem because your last brain cell died of loneliness? Cope harder snowflake",
                "Whataboutism AGAIN? Your one neuron is stuck on repeat like a broken record",
                "Projecting harder than IMAX! Everything you hate is just you looking in a mirror",
                "Gaslighting won't work, we have screenshots. Your lies are weaker than your jawline",
                "Moving goalposts faster than you move out of mom's basement",
                "Gish gallop of BS! Throwing lies like spaghetti hoping something sticks"
            ]

        def get_response(self, prompt):
            response = self.savage_responses[self.response_counter % len(self.savage_responses)]
            self.response_counter += 1
            return response

    # Message history with typical MAGA BS
    mod_messages = {
        "maga_trolls": [
            {"username": "AntiMa_Patriot", "message": "Democrats want to ban all guns and make us communist!"},
            {"username": "MAGA_Truth", "message": "But what about Hunter's laptop? Hillary's emails?"},
            {"username": "AntiMa_1776", "message": "You're all just triggered liberal snowflakes!"},
        ]
    }

    savage_llm = SavageMockLLM()
    grok = GrokIntegration(savage_llm, mod_messages)

    print("\n--- SAVAGE RESPONSE EXAMPLES ---\n")

    # Test different fallacy types
    test_users = [
        ("AntiMa_Patriot", "STRAWMAN"),
        ("MAGA_Truth", "WHATABOUTISM"),
        ("AntiMa_1776", "AD HOMINEM"),
        ("TrumpWon2020", "PROJECTION"),
        ("StopTheSteal", "GASLIGHTING"),
        ("PatriotEagle", "GOALPOSTS"),
        ("Truth_Warrior", "GISH GALLOP")
    ]

    for username, fallacy_type in test_users:
        response = grok.fact_check(username, "MOD", "fist-hand-open")
        # Clean response for display
        clean_response = response.encode('ascii', 'replace').decode('ascii')
        print(f"[{fallacy_type}]")
        print(f"  {clean_response}")
        print()

        # Verify it's savage
        assert "@" in response, "Should tag the user directly"
        assert "#AntiMa" in response, "Should include #AntiMa"

    print("=" * 60)
    print("SAVAGE MODE ACTIVATED!")
    print("\nYour 800 MODs are armed with:")
    print("  - Brutal mockery that cuts deep")
    print("  - Direct @mentions to call them out")
    print("  - #AntiMa hashtag for viral humiliation")
    print("\nAntiMa trolls will regret commenting!")

if __name__ == "__main__":
    test_savage_responses()