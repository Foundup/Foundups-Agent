#!/usr/bin/env python3
"""
Test AntiMa Fallacy Detection System
Tests the enhanced Grok fact-check with logical fallacy detection
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.llm_integration import GrokIntegration

def test_factcheck_with_fallacy():
    """Test that fact-check detects fallacies and adds #AntiMa"""

    print("Testing AntiMa Fallacy Detection System")
    print("=" * 60)

    # Mock LLM connector for testing
    class MockLLMConnector:
        def get_response(self, prompt):
            # Simulate Grok detecting a strawman fallacy
            if "fallacies" in prompt.lower() and "antima" in prompt.lower():
                return "User is misrepresenting the argument about immigration. Nobody said 'open borders', we said reform."
            return "Standard fact check response"

    # Create Grok integration with mock and message history
    mod_messages = {
        "user123": [
            {"username": "RegularUser", "message": "The election was stolen!"},
            {"username": "AntiMa_Troll", "message": "All immigrants are criminals!"},
            {"username": "MAGAUser", "message": "Democrats want to take all your guns!"}
        ]
    }
    grok = GrokIntegration(MockLLMConnector(), mod_messages)

    # Test 1: Regular user fact-check
    print("\nTest 1: Regular user fact-check")
    response = grok.fact_check("RegularUser", "MOD", "fist-hand-open")
    print(f"Response: {response.encode('ascii', 'replace').decode('ascii')}")
    assert "#AntiMa" in response, "Should add #AntiMa hashtag"
    print("PASSED - #AntiMa added")

    # Test 2: AntiMa user gets special treatment
    print("\nTest 2: AntiMa user fact-check")
    response = grok.fact_check("AntiMa_Troll", "MOD", "fist-hand-open")
    print(f"Response: {response.encode('ascii', 'replace').decode('ascii')}")
    assert "#AntiMa" in response, "Should include #AntiMa"
    print("PASSED - AntiMa user handled")

    # Test 3: Check for fallacy emoji prefix
    print("\nTest 3: Fallacy type detection")
    # Mock a strawman response
    grok.llm.get_response = lambda p: "This is a strawman argument about gun control"
    response = grok.fact_check("MAGAUser", "MOD", "fist-hand-open")
    print(f"Response: {response.encode('ascii', 'replace').decode('ascii')}")
    # The response should have STRAWMAN: prefix (emoji added by code)
    assert "STRAWMAN:" in response, "Should have strawman prefix"
    print("PASSED - Fallacy type detected")

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED! AntiMa fallacy detection ready!")
    print("\nYour 800 MODs can now use:")
    print("  [fist-hand-open emojis] @AntiMa fc - To detect and mock logical fallacies")
    print("  Responses will include #AntiMa hashtag for viral spread")

if __name__ == "__main__":
    test_factcheck_with_fallacy()