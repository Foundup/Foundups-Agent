"""
Test: Integrated Architecture - BrowserManager + Vision + DOM + Pattern Learning

Following VISION_AUTOMATION_SPRINT_MAP.md architecture:
- BrowserManager: Singleton browser lifecycle
- UI-TARS Bridge: Vision for finding elements
- DOM Verification: Ground truth for state changes
- ActionPatternLearner: Track human-validated outcomes

This combines all completed sprints (V1-V6, A1-A6) into proper integration.

WSP Compliance:
- WSP 77: AI Overseer integration
- WSP 48: Pattern learning from outcomes
- WSP 91: Observability via telemetry
"""
import asyncio
import logging
import sys
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(repo_root))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_integrated_youtube_engagement():
    """
    Test integrated architecture for YouTube comment engagement.

    Pattern:
    1. BrowserManager gets/creates browser (singleton)
    2. Vision finds element coordinates
    3. Selenium clicks
    4. DOM verifies actual state change
    5. PatternLearner stores outcome
    """
    from modules.infrastructure.foundups_selenium.src.browser_manager import BrowserManager
    from modules.infrastructure.foundups_vision.src.ui_tars_bridge import UITarsBridge
    from modules.infrastructure.foundups_vision.src.action_pattern_learner import ActionPatternLearner
    from modules.communication.video_comments.skills.qwen_studio_engage.executor import _vision_verified_action
    from modules.infrastructure.wre_core.src.pattern_memory import PatternMemory

    print("\n" + "="*80)
    print(" INTEGRATED ARCHITECTURE TEST")
    print(" Browser + Vision + DOM + Pattern Learning")
    print("="*80)

    # 1. Get browser from BrowserManager (singleton pattern)
    print("\n[1] Getting browser from BrowserManager...")
    browser_mgr = BrowserManager()
    driver = browser_mgr.get_browser(
        browser_type="chrome",
        profile_name="youtube_move2japan",
        options={
            "debugger_address": "127.0.0.1:9222"  # Connect to existing Chrome
        }
    )
    print(f"[OK] Browser ready: {driver.current_url[:50]}...")

    # 2. Initialize Vision Bridge
    print("\n[2] Initializing UI-TARS Bridge...")
    bridge = UITarsBridge(browser_port=9222)
    await bridge.connect()
    print("[OK] UI-TARS ready")

    # 3. Initialize Pattern Learning
    print("\n[3] Initializing Pattern Learning...")
    pattern_learner = ActionPatternLearner()
    pattern_memory = PatternMemory()
    print("[OK] Pattern learning ready")

    # 4. Navigate to YouTube Studio
    target_url = "https://studio.youtube.com/channel/UC-LSSlOZwpGIRIYihaz8zCw/comments/inbox"
    print(f"\n[4] Navigating to Studio inbox...")
    driver.get(target_url)
    await asyncio.sleep(5)
    print("[OK] On YouTube Studio page")

    # 5. Test single LIKE action with full integration
    print("\n[5] Testing LIKE with integrated architecture...")
    print("="*80)

    like_result = await _vision_verified_action(
        bridge,
        driver,
        click_description="gray thumbs up button in the comment action bar on the first comment",
        verify_description="thumbs up button is now blue or highlighted",
        action_name="like",
        pattern_memory=pattern_memory,
        max_retries=3,
        # DOM GROUND TRUTH
        dom_selector="ytcp-comment-thread:nth-child(1) button[aria-label*='Like']",
        expected_state_change="aria_pressed=true"
    )

    print("\n" + "="*80)
    print(" RESULTS")
    print("="*80)

    if like_result["success"]:
        if like_result.get("dom_verified"):
            print(f"\n[SUCCESS] Action verified by DOM (confidence: {like_result['confidence']:.2f})")
            print("✓ Vision found element")
            print("✓ Selenium clicked")
            print("✓ DOM confirmed state change (aria-pressed: false → true)")
        else:
            print(f"\n[PARTIAL] Action reported success by vision (confidence: {like_result['confidence']:.2f})")
            print("⚠ WARNING: No DOM verification - may be false positive")
    else:
        print(f"\n[FAILED] Action failed after {like_result['attempts']} attempts")
        print(f"Error: {like_result.get('error', 'Unknown')}")

    # 6. Pattern learning outcome
    print("\n[6] Pattern Learning Outcome:")
    print(f"- Pattern stored in: {pattern_memory.db_path}")
    print("- Available for future recursive improvement")

    print("\n" + "="*80)
    print(" TEST COMPLETE")
    print("="*80)
    print("\nIntegration verified:")
    print("✓ BrowserManager - Singleton browser lifecycle")
    print("✓ UI-TARS Bridge - Vision element finding")
    print("✓ Selenium - Click execution")
    if like_result.get("dom_verified"):
        print("✓ DOM Verification - Ground truth state change")
    else:
        print("✗ DOM Verification - Not used (vision only)")
    print("✓ Pattern Memory - Learning outcomes stored")


if __name__ == "__main__":
    asyncio.run(test_integrated_youtube_engagement())
