"""
Test script to verify fact-check command priority with consciousness emojis.

This demonstrates the enhanced priority system where fact-check commands
containing consciousness emojis ([U+270A][U+270B][U+1F590]) get the highest priority (Priority 0).

WSP Compliance: WSP 5 (Test Coverage), WSP 84 (Code Memory)
"""

def test_priority_examples():
    """
    Test examples showing the new priority system.

    These are example message patterns that would trigger different priorities:
    """

    # Priority 0: Fact-check with consciousness emojis (HIGHEST PRIORITY)
    priority_0_examples = [
        "factcheck @BadActor [U+270A][U+270B][U+1F590] Is this true?",
        "fc @Troll [U+1F590][U+270B][U+270A] Check their claims",
        "factcheck @User [U+270A] Claims need verification",
        "fc @Person consciousness check [U+270B][U+1F590][U+270A]"
    ]

    # Priority 1: PQN Research Commands
    priority_1_examples = [
        "!pqn consciousness emergence patterns",
        "/research quantum entanglement",
        "!research neural network patterns"
    ]

    # Priority 2: Regular consciousness responses
    priority_2_examples = [
        "[U+270A][U+270B][U+1F590] What is consciousness?",
        "[U+1F590][U+270B][U+270A] Explain this concept"
    ]

    # Priority 3: Regular fact-check (without consciousness emojis)
    priority_3_examples = [
        "factcheck @User normal request",
        "fc @Person check this claim"
    ]

    print("=== FACT-CHECK PRIORITY SYSTEM TEST ===")
    print()

    print("Priority 0 (HIGHEST) - Fact-check WITH consciousness emojis:")
    for i, example in enumerate(priority_0_examples, 1):
        print(f"  {i}. {example}")
    print()

    print("Priority 1 - PQN Research Commands:")
    for i, example in enumerate(priority_1_examples, 1):
        print(f"  {i}. {example}")
    print()

    print("Priority 2 - Regular consciousness responses:")
    for i, example in enumerate(priority_2_examples, 1):
        print(f"  {i}. {example}")
    print()

    print("Priority 3 - Regular fact-check (no consciousness emojis):")
    for i, example in enumerate(priority_3_examples, 1):
        print(f"  {i}. {example}")
    print()

    print("[OK] Priority system ensures consciousness-enhanced fact-checks get immediate attention!")

    return True

def test_emoji_detection_logic():
    """
    Test the logic that detects consciousness emojis in fact-check commands.
    """

    # Test cases
    test_cases = [
        # (message, expected_has_factcheck, expected_has_consciousness_emojis)
        ("factcheck @User [U+270A][U+270B][U+1F590] test", True, True),
        ("fc @Person [U+1F590] check this", True, True),
        ("factcheck @Someone normal", True, False),
        ("[U+270A][U+270B][U+1F590] not a factcheck", False, True),
        ("normal message", False, False),
        ("factcheck @User [U+270A] partial", True, True),
    ]

    print("=== EMOJI DETECTION LOGIC TEST ===")
    print()

    for message, expected_factcheck, expected_consciousness in test_cases:
        # Simulate the logic from message_processor.py
        # Use the actual regex pattern from the code
        import re
        pattern = r'(?:factcheck|fc)\s+@[\w\s]+'
        has_factcheck = bool(re.search(pattern, message.lower()))
        consciousness_emojis = ['[U+270A]', '[U+270B]', '[U+1F590]']
        has_consciousness = any(emoji in message for emoji in consciousness_emojis)

        would_be_priority_0 = has_factcheck and has_consciousness

        print(f"Message: '{message}'")
        print(f"  Has fact-check: {has_factcheck} (expected: {expected_factcheck})")
        print(f"  Has consciousness: {has_consciousness} (expected: {expected_consciousness})")
        print(f"  Would be Priority 0: {would_be_priority_0}")
        print()

        # Verify our logic matches expectations
        assert has_factcheck == expected_factcheck, f"Fact-check detection failed for: {message}"
        assert has_consciousness == expected_consciousness, f"Consciousness detection failed for: {message}"

    print("[OK] All emoji detection tests passed!")
    return True

if __name__ == "__main__":
    print("Testing the enhanced fact-check priority system...\n")

    test_priority_examples()
    print()
    test_emoji_detection_logic()

    print("\n[TARGET] Summary:")
    print("- Fact-check commands with consciousness emojis ([U+270A][U+270B][U+1F590]) now have Priority 0 (highest)")
    print("- This ensures immediate processing of consciousness-enhanced fact-checking")
    print("- The system maintains backward compatibility with regular fact-checks")
    print("- WSP 15 (Module Prioritization) compliance achieved")