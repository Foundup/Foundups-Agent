#!/usr/bin/env python3
"""
Test Autonomous Enhancements Integration
Quick test to verify the enhancements work without breaking main.py
"""

import sys
import os

# Add the autonomous enhancements path
sys.path.append('modules/infrastructure/autonomous_enhancements/src')

def test_autonomous_enhancements():
    """Test that autonomous enhancements load and work"""
    try:
        from autonomous_enhancements import autonomous_enhancements
        print("✅ Autonomous enhancements loaded successfully")

        # Test system status
        stats = autonomous_enhancements.get_system_status()
        print(f"🤖 Quantum State: {stats['quantum_state']}")
        print(f"🎯 Coherence: {stats['coherence']}")
        print(f"📊 QRPE Patterns: {stats['algorithms']['qrpe']['patterns_learned']}")
        print(f"🧠 AIRE Decisions: {stats['algorithms']['aire']['decisions_made']}")

        # Test QRPE basic functionality
        test_context = {'action': 'test_integration', 'phase': 'validation'}
        pattern = autonomous_enhancements.qrpe.recall_pattern(test_context)
        print(f"🔍 QRPE Pattern Recall: {pattern is None}")

        # Test AIRE basic functionality
        recommendation = autonomous_enhancements.aire.resolve_intent(test_context)
        print(f"🎯 AIRE Recommendation: {recommendation}")

        print("\n✅ All autonomous enhancement tests passed!")
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def test_main_py_integration():
    """Test that main.py can still load and run basic functions"""
    try:
        # Test basic import
        import main
        print("✅ main.py imports successfully")

        # Test BlockLauncher creation
        from main import BlockLauncher
        launcher = BlockLauncher()
        print("✅ BlockLauncher creates successfully")

        # Test context generation
        context = launcher.get_context_for_autonomous_enhancement()
        print(f"✅ Context generation works: {len(context)} keys")

        print("\n✅ Main.py integration tests passed!")
        return True

    except Exception as e:
        print(f"❌ Main.py integration error: {e}")
        return False

if __name__ == '__main__':
    print("🧪 Testing Autonomous Enhancements Integration")
    print("="*50)

    # Test autonomous enhancements
    ae_success = test_autonomous_enhancements()
    print()

    # Test main.py integration
    main_success = test_main_py_integration()
    print()

    # Summary
    if ae_success and main_success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Autonomous enhancements are working")
        print("✅ Main.py integration is intact")
        print("✅ No breaking changes detected")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED!")
        print(f"Autonomous Enhancements: {'✅' if ae_success else '❌'}")
        print(f"Main.py Integration: {'✅' if main_success else '❌'}")
        sys.exit(1)
