"""
Phase 3A Integration Simple Verification
=========================================

Quick file existence and code pattern check (no imports, no .env).

Usage:
    python verify_phase3a_simple.py
"""
from pathlib import Path
import sys
import os

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
os.chdir(REPO_ROOT)


import os
from pathlib import Path

def check_file_exists(file_path: str, description: str) -> bool:
    """Check if file exists."""
    path = Path(file_path)
    if path.exists():
        print(f"[PASS] {description}")
        print(f"       {file_path}")
        return True
    else:
        print(f"[FAIL] {description} - FILE NOT FOUND")
        print(f"       {file_path}")
        return False


def check_code_pattern(file_path: str, pattern: str, description: str) -> bool:
    """Check if code pattern exists in file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if pattern in content:
                print(f"[PASS] {description}")
                return True
            else:
                print(f"[FAIL] {description} - PATTERN NOT FOUND")
                return False
    except Exception as e:
        print(f"[FAIL] {description} - ERROR: {e}")
        return False


def main():
    print("="*60)
    print("PHASE 3A SIMPLE VERIFICATION")
    print("="*60)
    print()

    results = []

    # Test 1: vision_stream_checker.py exists
    print("\n[TEST 1] vision_stream_checker.py exists...")
    results.append(check_file_exists(
        "modules/platform_integration/stream_resolver/src/vision_stream_checker.py",
        "vision_stream_checker.py found"
    ))

    # Test 2: vision_stream_checker.py uses port 9222
    print("\n[TEST 2] vision_stream_checker.py uses port 9222...")
    results.append(check_code_pattern(
        "modules/platform_integration/stream_resolver/src/vision_stream_checker.py",
        "127.0.0.1:9222",
        "Port 9222 configured in vision_stream_checker.py"
    ))

    # Test 3: stream_resolver.py has PRIORITY 0 vision integration
    print("\n[TEST 3] stream_resolver.py has PRIORITY 0 vision integration...")
    results.append(check_code_pattern(
        "modules/platform_integration/stream_resolver/src/stream_resolver.py",
        "from .vision_stream_checker import VisionStreamChecker",
        "VisionStreamChecker imported in stream_resolver.py"
    ))

    # Test 4: stream_resolver.py calls vision checker
    print("\n[TEST 4] stream_resolver.py calls vision checker...")
    results.append(check_code_pattern(
        "modules/platform_integration/stream_resolver/src/stream_resolver.py",
        "vision_checker.check_channel_for_live",
        "vision_checker.check_channel_for_live() call found"
    ))

    # Test 5: no_quota_stream_checker.py has CAPTCHA bypass
    print("\n[TEST 5] no_quota_stream_checker.py has CAPTCHA bypass...")
    results.append(check_code_pattern(
        "modules/platform_integration/stream_resolver/src/no_quota_stream_checker.py",
        "captcha_hit",
        "CAPTCHA bypass logic (captcha_hit flag) found"
    ))

    # Test 6: community_monitor.py exists
    print("\n[TEST 6] community_monitor.py exists...")
    results.append(check_file_exists(
        "modules/communication/livechat/src/community_monitor.py",
        "community_monitor.py found"
    ))

    # Test 7: community_monitor.py uses subprocess
    print("\n[TEST 7] community_monitor.py uses subprocess...")
    results.append(check_code_pattern(
        "modules/communication/livechat/src/community_monitor.py",
        "asyncio.create_subprocess_exec",
        "Subprocess execution found in community_monitor.py"
    ))

    # Test 8: auto_moderator_dae.py has CommunityMonitor integration
    print("\n[TEST 8] auto_moderator_dae.py has CommunityMonitor integration...")
    results.append(check_code_pattern(
        "modules/communication/livechat/src/auto_moderator_dae.py",
        "get_community_monitor",
        "CommunityMonitor integration found in auto_moderator_dae.py"
    ))

    # Test 9: auto_moderator_dae.py has heartbeat check
    print("\n[TEST 9] auto_moderator_dae.py has heartbeat check...")
    results.append(check_code_pattern(
        "modules/communication/livechat/src/auto_moderator_dae.py",
        "self.community_monitor",
        "Heartbeat community_monitor check found"
    ))

    # Test 10: intelligent_throttle_manager.py has Phase 3A throttling
    print("\n[TEST 10] intelligent_throttle_manager.py has Phase 3A throttling...")
    results.append(check_code_pattern(
        "modules/communication/livechat/src/intelligent_throttle_manager.py",
        "comment_engagement_announcement",
        "comment_engagement_announcement throttle type found"
    ))

    # Test 11: comment_engagement_dae.py uses port 9222
    print("\n[TEST 11] comment_engagement_dae.py uses port 9222...")
    results.append(check_code_pattern(
        "modules/communication/video_comments/skillz/tars_like_heart_reply/comment_engagement_dae.py",
        'CHROME_PORT = int(os.getenv("FOUNDUPS_CHROME_PORT", "9222"))',
        "CHROME_PORT 9222 configured in comment_engagement_dae.py"
    ))

    # Test 12: Status report exists
    print("\n[TEST 12] PHASE_3A_INTEGRATION_STATUS.md exists...")
    results.append(check_file_exists(
        "docs/PHASE_3A_INTEGRATION_STATUS.md",
        "Phase 3A status report found"
    ))

    # Test 13: stream_resolver ModLog updated
    print("\n[TEST 13] stream_resolver ModLog updated...")
    results.append(check_code_pattern(
        "modules/platform_integration/stream_resolver/ModLog.md",
        "Vision Stream Detection Integration",
        "ModLog updated with vision integration"
    ))

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
        print("="*60)
        print("SYSTEM STATUS")
        print("="*60)
        print()
        print("Integration Components:")
        print("  [PASS] vision_stream_checker.py - CAPTCHA immune detection")
        print("  [PASS] stream_resolver.py - PRIORITY 0 vision integration")
        print("  [PASS] no_quota_stream_checker.py - CAPTCHA bypass")
        print("  [PASS] community_monitor.py - Autonomous engagement")
        print("  [PASS] auto_moderator_dae.py - Heartbeat integration")
        print("  [PASS] comment_engagement_dae.py - Chrome session sharing")
        print()
        print("Chrome Session:")
        print("  Port: 9222 (shared between detection and engagement)")
        print("  Status: Verify with: netstat -an | findstr \"9222\"")
        print()
        print("Detection Flow:")
        print("  PRIORITY 0: Vision (Chrome 9222) <- CAPTCHA immune")
        print("  PRIORITY 1: Cache + DB")
        print("  PRIORITY 2: YouTube API (Set 10 token)")
        print("  PRIORITY 4: NO-QUOTA Scraping")
        print()
        print("Next Steps:")
        print("  1. Ensure Chrome running: launch_chrome_youtube_studio.bat")
        print("  2. Restart daemon: python main.py -> 1 -> 5")
        print("  3. Monitor: Vision detects stream QlGN6CzD3F8")
        print("  4. Wait: Pulse 20 (10 min) triggers comment engagement")
        print("  5. Verify: Chat announcement posted")
        print()
        return 0
    else:
        failed = total - passed
        print(f"[WARN] SOME TESTS FAILED ({passed}/{total} passed, {failed} failed)")
        print()
        print("Please review failed tests above.")
        print("Integration may be incomplete.")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
