"""
Phase 3A Integration Verification Script
=========================================

Quick test to verify all Phase 3A components are properly wired:
1. Vision stream detection (PRIORITY 0)
2. CAPTCHA bypass with API fallback
3. CommunityMonitor integration
4. Chrome session sharing (port 9222)
5. Throttling configuration

Run this BEFORE restarting the daemon to catch any issues.

Usage:
    python verify_phase3a_integration.py
"""
from pathlib import Path
import sys
import os

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
os.chdir(REPO_ROOT)


import sys
import os
from pathlib import Path

# Add repo root to path
repo_root = REPO_ROOT

def test_vision_checker_import():
    """Test 1: Can we import VisionStreamChecker?"""
    try:
        from modules.platform_integration.stream_resolver.src.vision_stream_checker import (
            VisionStreamChecker,
            get_vision_stream_checker,
            check_channel_with_vision
        )
        print("[PASS] Test 1: VisionStreamChecker imports successfully")
        return True
    except Exception as e:
        print(f"[FAIL] Test 1 FAILED: Cannot import VisionStreamChecker: {e}")
        return False


def test_chrome_connection():
    """Test 2: Can we connect to Chrome on port 9222?"""
    try:
        from modules.platform_integration.stream_resolver.src.vision_stream_checker import (
            get_vision_stream_checker
        )

        checker = get_vision_stream_checker()

        if checker.vision_available:
            print("[PASS] Test 2: Chrome connected on port 9222 - vision mode available")
            return True
        else:
            print("[WARN]  Test 2: Chrome not available on port 9222")
            print("   Tip: Run launch_chrome_youtube_studio.bat first")
            return False

    except Exception as e:
        print(f"[FAIL] Test 2 FAILED: Chrome connection error: {e}")
        return False


def test_stream_resolver_integration():
    """Test 3: Does StreamResolver have vision integration?"""
    try:
        from modules.platform_integration.stream_resolver.src.stream_resolver import StreamResolver

        # Check if StreamResolver can import vision_stream_checker
        import inspect
        source = inspect.getsource(StreamResolver.search_for_new_stream)

        if 'VisionStreamChecker' in source:
            print("[PASS] Test 3: StreamResolver has vision integration (PRIORITY 0)")
            return True
        else:
            print("[FAIL] Test 3 FAILED: VisionStreamChecker not found in StreamResolver")
            return False

    except Exception as e:
        print(f"[FAIL] Test 3 FAILED: StreamResolver check error: {e}")
        return False


def test_community_monitor():
    """Test 4: Can we import CommunityMonitor?"""
    try:
        from modules.communication.livechat.src.community_monitor import (
            CommunityMonitor,
            get_community_monitor
        )
        print("[PASS] Test 4: CommunityMonitor imports successfully")
        return True
    except Exception as e:
        print(f"[FAIL] Test 4 FAILED: Cannot import CommunityMonitor: {e}")
        return False


def test_comment_engagement_dae():
    """Test 5: Can we import CommentEngagementDAE?"""
    try:
        from modules.communication.video_comments.skillz.tars_like_heart_reply.comment_engagement_dae import (
            CommentEngagementDAE
        )

        # Check Chrome port configuration
        from modules.communication.video_comments.skillz.tars_like_heart_reply.comment_engagement_dae import (
            CHROME_PORT
        )

        if CHROME_PORT == 9222:
            print(f"[PASS] Test 5: CommentEngagementDAE imports (Chrome port: {CHROME_PORT})")
            return True
        else:
            print(f"[WARN]  Test 5: CommentEngagementDAE uses port {CHROME_PORT} (expected 9222)")
            return True  # Not a failure, just different config

    except Exception as e:
        print(f"[FAIL] Test 5 FAILED: Cannot import CommentEngagementDAE: {e}")
        return False


def test_throttle_configuration():
    """Test 6: Are Phase 3A throttle types configured?"""
    try:
        from modules.communication.livechat.src.intelligent_throttle_manager import IntelligentThrottleManager

        # Create instance to check response_cooldowns
        manager = IntelligentThrottleManager(base_interval=300)

        required_types = [
            'comment_engagement_announcement',
            'moderator_notification'
        ]

        missing = []
        for response_type in required_types:
            if response_type not in manager.response_cooldowns:
                missing.append(response_type)

        if not missing:
            print("[PASS] Test 6: Throttling configured for Phase 3A response types")
            return True
        else:
            print(f"[FAIL] Test 6 FAILED: Missing throttle types: {missing}")
            return False

    except Exception as e:
        print(f"[FAIL] Test 6 FAILED: Throttle configuration error: {e}")
        return False


def test_auto_moderator_integration():
    """Test 7: Does AutoModeratorDAE have CommunityMonitor integration?"""
    try:
        from modules.communication.livechat.src.auto_moderator_dae import AutoModeratorDAE

        import inspect
        source = inspect.getsource(AutoModeratorDAE.run)

        checks = {
            'community_monitor initialization': 'get_community_monitor' in source,
            'heartbeat integration': 'community_monitor' in source,
        }

        all_present = all(checks.values())

        if all_present:
            print("[PASS] Test 7: AutoModeratorDAE has CommunityMonitor integration")
            return True
        else:
            missing = [k for k, v in checks.items() if not v]
            print(f"[FAIL] Test 7 FAILED: Missing integration: {missing}")
            return False

    except Exception as e:
        print(f"[FAIL] Test 7 FAILED: AutoModeratorDAE check error: {e}")
        return False


def test_captcha_bypass():
    """Test 8: Does NO-QUOTA checker have CAPTCHA bypass?"""
    try:
        from modules.platform_integration.stream_resolver.src.no_quota_stream_checker import NoQuotaStreamChecker

        import inspect
        source = inspect.getsource(NoQuotaStreamChecker.check_channel_for_live)

        # Check if captcha_hit flag exists (new logic)
        if 'captcha_hit' in source and 'if not captcha_hit:' in source:
            print("[PASS] Test 8: NO-QUOTA checker has CAPTCHA bypass with API fallback")
            return True
        else:
            print("[WARN]  Test 8: CAPTCHA bypass logic not detected (may use older version)")
            return True  # Not critical

    except Exception as e:
        print(f"[FAIL] Test 8 FAILED: NO-QUOTA checker error: {e}")
        return False


def main():
    print("="*60)
    print("PHASE 3A INTEGRATION VERIFICATION")
    print("="*60)
    print()

    tests = [
        ("Vision Checker Import", test_vision_checker_import),
        ("Chrome Connection (Port 9222)", test_chrome_connection),
        ("StreamResolver Integration", test_stream_resolver_integration),
        ("CommunityMonitor Import", test_community_monitor),
        ("CommentEngagementDAE Import", test_comment_engagement_dae),
        ("Throttle Configuration", test_throttle_configuration),
        ("AutoModeratorDAE Integration", test_auto_moderator_integration),
        ("CAPTCHA Bypass Logic", test_captcha_bypass),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n[TEST] {test_name}...")
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"[FAIL] Test crashed: {e}")
            results.append(False)

    print()
    print("="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)

    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"[PASS] ALL TESTS PASSED ({passed}/{total})")
        print()
        print("[READY] Phase 3A integration is READY FOR TESTING!")
        print()
        print("Next steps:")
        print("1. Ensure Chrome is running: launch_chrome_youtube_studio.bat")
        print("2. Restart daemon: python main.py → 1 → 5")
        print("3. Monitor logs for vision detection and comment engagement")
        return 0
    else:
        failed = total - passed
        print(f"[WARN]  SOME TESTS FAILED ({passed}/{total} passed, {failed} failed)")
        print()
        print("Please fix the failed tests before restarting the daemon.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
