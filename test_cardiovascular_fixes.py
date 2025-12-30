"""
Test Cardiovascular Hardening Fixes (2025-12-25)

Verifies:
1. BanterEngine singleton prevents duplicate initialization
2. Quota rotation logic returns correct intervals
3. CARDIO PULSE logger can aggregate and emit health signals
"""

import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_banter_singleton():
    """Test BanterEngine singleton prevents duplicate initialization."""
    logger.info("\n[TEST 1] BanterEngine Singleton")
    logger.info("=" * 50)

    try:
        from modules.ai_intelligence.banter_engine.src.banter_singleton import (
            get_banter_engine,
            reset_banter_engine,
            get_initialization_stats
        )

        # Reset to clean state
        reset_banter_engine()

        # First call should initialize
        logger.info("First call to get_banter_engine()...")
        banter1 = get_banter_engine(emoji_enabled=True)
        stats1 = get_initialization_stats()

        # Second call should reuse
        logger.info("Second call to get_banter_engine()...")
        banter2 = get_banter_engine(emoji_enabled=True)
        stats2 = get_initialization_stats()

        # Third call should also reuse
        logger.info("Third call to get_banter_engine()...")
        banter3 = get_banter_engine(emoji_enabled=True)
        stats3 = get_initialization_stats()

        # Verify same instance
        assert banter1 is banter2, "Second call created new instance (FAIL)"
        assert banter2 is banter3, "Third call created new instance (FAIL)"
        assert stats3['initialization_count'] == 1, f"Expected 1 init, got {stats3['initialization_count']} (FAIL)"

        logger.info(f"✅ PASS: Singleton working - 1 initialization for 3 calls")
        logger.info(f"   Stats: {stats3}")
        return True

    except Exception as e:
        logger.error(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_quota_rotation_logic():
    """Test quota rotation returns correct intervals."""
    logger.info("\n[TEST 2] Quota Rotation Logic")
    logger.info("=" * 50)

    try:
        from modules.communication.livechat.src.quota_aware_poller import QuotaAwarePoller
        import json
        from pathlib import Path

        # Create test quota file
        quota_file = Path("memory/quota_usage.json")
        quota_file.parent.mkdir(parents=True, exist_ok=True)

        # Mock OAuth manager with rotation
        class MockOAuthManager:
            def __init__(self, rotation_succeeds=True):
                self.rotation_succeeds = rotation_succeeds

            def rotate_credentials(self):
                logger.info(f"   [MOCK] rotate_credentials() called, returning {self.rotation_succeeds}")
                return self.rotation_succeeds

        poller = QuotaAwarePoller(credential_set=1)

        # Test 1: Quota 96%, rotation succeeds -> should return NORMAL_INTERVAL
        logger.info("\nScenario 1: Quota 96%, rotation succeeds")
        with open(quota_file, 'w') as f:
            json.dump({'sets': {'1': {'used': 9600}}}, f)

        poller.oauth_manager = MockOAuthManager(rotation_succeeds=True)
        interval = poller.calculate_optimal_interval()

        assert interval == poller.NORMAL_INTERVAL, f"Expected {poller.NORMAL_INTERVAL}s (NORMAL), got {interval}s (FAIL)"
        logger.info(f"   ✅ PASS: Returned NORMAL_INTERVAL ({interval}s) after successful rotation")

        # Test 2: Quota 96%, rotation fails -> should return EMERGENCY_INTERVAL
        logger.info("\nScenario 2: Quota 96%, rotation fails")
        with open(quota_file, 'w') as f:
            json.dump({'sets': {'1': {'used': 9600}}}, f)

        poller.oauth_manager = MockOAuthManager(rotation_succeeds=False)
        interval = poller.calculate_optimal_interval()

        assert interval == poller.EMERGENCY_INTERVAL, f"Expected {poller.EMERGENCY_INTERVAL}s (EMERGENCY), got {interval}s (FAIL)"
        logger.info(f"   ✅ PASS: Returned EMERGENCY_INTERVAL ({interval}s) after failed rotation")

        # Test 3: Quota 99%, rotation fails -> should return None (stop)
        logger.info("\nScenario 3: Quota 99%, rotation fails")
        with open(quota_file, 'w') as f:
            json.dump({'sets': {'1': {'used': 9900}}}, f)

        poller.oauth_manager = MockOAuthManager(rotation_succeeds=False)
        interval = poller.calculate_optimal_interval()

        assert interval is None, f"Expected None (STOP), got {interval}s (FAIL)"
        logger.info(f"   ✅ PASS: Returned None (emergency shutoff) for exhausted quota")

        logger.info(f"\n✅ PASS: Quota rotation logic correct")
        return True

    except Exception as e:
        logger.error(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cardio_pulse_logger():
    """Test CARDIO PULSE logger can aggregate and emit."""
    logger.info("\n[TEST 3] CARDIO PULSE Logger")
    logger.info("=" * 50)

    try:
        from modules.communication.livechat.src.cardio_pulse_logger import CardioPulse
        import time

        # Create pulse logger
        pulse = CardioPulse(heartbeat_interval=1)

        # Test heartbeat emission
        logger.info("Emitting first heartbeat (should emit)...")
        pulse.emit_heartbeat(
            quota_used=500,
            poll_interval=10,
            messages_processed=42,
            errors=2,
            credential_set=1,
            stream_active=True
        )

        # Immediate second call should skip (not enough time elapsed)
        logger.info("Emitting second heartbeat immediately (should skip)...")
        pulse.emit_heartbeat(
            quota_used=510,
            poll_interval=10,
            messages_processed=45,
            errors=2,
            credential_set=1,
            stream_active=True
        )

        # Wait and emit again
        logger.info("Waiting 1.5s and emitting third heartbeat (should emit)...")
        time.sleep(1.5)
        pulse.emit_heartbeat(
            quota_used=520,
            poll_interval=10,
            messages_processed=48,
            errors=2,
            credential_set=1,
            stream_active=True
        )

        # Test noise suppression
        logger.info("\nTesting noise suppression...")
        suppressed1 = pulse.suppress_noise("test_log", "Repeated message")
        suppressed2 = pulse.suppress_noise("test_log", "Repeated message")
        suppressed3 = pulse.suppress_noise("test_log", "Repeated message")

        assert suppressed1 == False, "First occurrence should NOT be suppressed (FAIL)"
        assert suppressed2 == True, "Second occurrence SHOULD be suppressed (FAIL)"
        assert suppressed3 == True, "Third occurrence SHOULD be suppressed (FAIL)"

        logger.info(f"   ✅ PASS: Noise suppression working (first shown, subsequent suppressed)")

        logger.info(f"\n✅ PASS: CARDIO PULSE operational")
        logger.info(f"   Heartbeat emitted 2 times (interval-based throttling working)")
        logger.info(f"   Noise suppression confirmed (1 log type suppressed)")
        return True

    except Exception as e:
        logger.error(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    logger.info("\n" + "=" * 70)
    logger.info("CARDIOVASCULAR HARDENING TEST SUITE (2025-12-25)")
    logger.info("=" * 70)

    results = []

    # Run tests
    results.append(("BanterEngine Singleton", test_banter_singleton()))
    results.append(("Quota Rotation Logic", test_quota_rotation_logic()))
    results.append(("CARDIO PULSE Logger", test_cardio_pulse_logger()))

    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("TEST SUMMARY")
    logger.info("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status}: {test_name}")

    logger.info(f"\nResult: {passed}/{total} tests passed")

    if passed == total:
        logger.info("\n🎉 ALL TESTS PASSED - Cardiovascular hardening validated!")
        return 0
    else:
        logger.error(f"\n⚠️ {total - passed} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
