#!/usr/bin/env python3
"""
Test Security Fix: /toggle Command OWNER-ONLY Access
Verifies that only OWNER can change consciousness mode, not MOD
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

def test_toggle_security():
    """Test that /toggle is OWNER-ONLY"""
    print("TESTING /toggle SECURITY FIX")
    print("=" * 60)

    # Mock the necessary components
    class MockMessageProcessor:
        def __init__(self):
            self.consciousness_mode = 'everyone'

    class MockTimeoutManager:
        pass

    from modules.communication.livechat.src.command_handler import CommandHandler

    # Initialize handler with mocked dependencies
    handler = CommandHandler(MockTimeoutManager(), MockMessageProcessor())
    handler.message_processor = MockMessageProcessor()

    # Test 1: OWNER should be able to toggle
    print("\n1. Testing OWNER access:")
    result = handler.handle_whack_command('/toggle', 'OwnerUser', 'owner123', 'OWNER')
    success = result and "consciousness responses now" in result
    print(f"   OWNER toggle: {'[PASS]' if success else '[FAIL]'}")
    if result:
        print(f"   Response: {result[:80]}...")

    # Test 2: MOD should be DENIED
    print("\n2. Testing MOD access (should be denied):")
    result = handler.handle_whack_command('/toggle', 'ModUser', 'mod123', 'MOD')
    denied = result and "Only the OWNER can toggle" in result
    print(f"   MOD denied: {'[PASS]' if denied else '[FAIL]'}")
    if result:
        print(f"   Response: {result[:80]}...")

    # Test 3: Regular USER should be DENIED
    print("\n3. Testing USER access (should be denied):")
    result = handler.handle_whack_command('/toggle', 'RegularUser', 'user123', 'USER')
    denied = result and "Only the OWNER can toggle" in result
    print(f"   USER denied: {'[PASS]' if denied else '[FAIL]'}")
    if result:
        print(f"   Response: {result[:80]}...")

    # Test 4: Help shows correct permissions
    print("\n4. Testing help message permissions:")

    # Help for OWNER
    result_owner = handler.handle_whack_command('/help', 'OwnerUser', 'owner123', 'OWNER')
    has_toggle = result_owner and "/toggle" in result_owner
    print(f"   OWNER sees /toggle: {'[PASS]' if has_toggle else '[FAIL]'}")

    # Help for MOD
    result_mod = handler.handle_whack_command('/help', 'ModUser', 'mod123', 'MOD')
    no_toggle = result_mod and "/toggle" not in result_mod
    print(f"   MOD doesn't see /toggle: {'[PASS]' if no_toggle else '[FAIL]'}")

    # Help for USER
    result_user = handler.handle_whack_command('/help', 'RegularUser', 'user123', 'USER')
    no_toggle_user = result_user and "/toggle" not in result_user
    print(f"   USER doesn't see /toggle: {'[PASS]' if no_toggle_user else '[FAIL]'}")

    # Summary
    all_passed = success and denied and denied and has_toggle and no_toggle and no_toggle_user

    print("\n" + "=" * 60)
    print("SECURITY TEST RESULTS")
    print("=" * 60)
    print(f"Overall Security: {'[SECURE]' if all_passed else '[VULNERABLE]'}")

    if all_passed:
        print("[OK] /toggle command is properly secured to OWNER-ONLY")
        print("[OK] Permission escalation vulnerability FIXED")
        print("[OK] Help messages show correct role-based permissions")
    else:
        print("[FAIL] Security issues detected - review implementation")

    return all_passed

if __name__ == "__main__":
    print("TOGGLE COMMAND SECURITY VERIFICATION")
    print("Testing OWNER-ONLY access restriction")
    print("=" * 80)

    success = test_toggle_security()

    if success:
        print("\n[SUCCESS] Security fix verified working correctly!")
        print("[OK] /toggle command is now OWNER-ONLY as required")
    else:
        print("\n[FAILURE] Security issues still present!")
        print("[FAIL] Review the command_handler.py implementation")