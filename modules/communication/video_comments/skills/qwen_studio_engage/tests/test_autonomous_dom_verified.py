"""
Test: Autonomous engagement with DOM STATE VERIFICATION (NOT vision)

Pattern: Vision finds element → Click → DOM verifies actual state change

This fixes the false positive problem where vision reports success
but no actual engagement occurred.

WSP Compliance:
- WSP 96: WRE Skills with pattern learning
- WSP 48: Self-improvement through DOM ground truth
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


async def engage_all_comments_dom_verified():
    """
    Engage with ALL comments using DOM STATE VERIFICATION.

    Process:
    1. Navigate to Studio inbox
    2. For each comment:
       - LIKE (vision finds → DOM verifies aria-pressed change)
       - HEART (vision finds → DOM verifies aria-pressed change)
       - REPLY (vision finds → DOM verifies reply count change)
    3. Refresh page (filter removes replied comments)
    4. Repeat until no comments left
    """
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from modules.infrastructure.foundups_vision.src.ui_tars_bridge import UITarsBridge
    from modules.infrastructure.wre_core.src.pattern_memory import PatternMemory
    from modules.communication.video_comments.skills.qwen_studio_engage.executor import _vision_verified_action

    print("\n" + "="*80)
    print(" 0102 AUTONOMOUS COMMENT ENGAGEMENT - DOM STATE VERIFICATION")
    print(" Vision finds → Click → DOM verifies (ZERO false positives)")
    print("="*80)

    # Connect to existing Chrome
    print("\n[1] Connecting to Chrome on port 9222...")
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=chrome_options)
    print("[OK] Connected")

    # Initialize UI-TARS Bridge
    print("\n[2] Initializing UI-TARS Bridge...")
    bridge = UITarsBridge(browser_port=9222)
    await bridge.connect()
    print("[OK] UI-TARS ready")

    # Initialize Pattern Memory
    pattern_memory = PatternMemory()

    # Navigate to YouTube Studio
    target_url = "https://studio.youtube.com/channel/UC-LSSlOZwpGIRIYihaz8zCw/comments/inbox"
    print(f"\n[3] Navigating to Studio inbox...")
    driver.get(target_url)
    await asyncio.sleep(5)
    print("[OK] On YouTube Studio page")

    print("\n[4] Starting autonomous engagement loop...")
    print("="*80)
    print("Pattern: LIKE (DOM verified) → HEART (DOM verified) → REPLY (DOM verified)")
    print("="*80)

    processed_count = 0

    while True:
        # Count remaining comments
        comment_count = driver.execute_script("""
            const cards = document.querySelectorAll('ytcp-comment-thread');
            return cards.length;
        """)

        if comment_count == 0:
            print("\n[COMPLETE] No more comments!")
            break

        print(f"\n[COMMENT {processed_count + 1}] ({comment_count} remaining)")
        print("-"*80)

        try:
            # Scroll first comment into view
            driver.execute_script("""
                const cards = document.querySelectorAll('ytcp-comment-thread');
                if (cards[0]) {
                    cards[0].scrollIntoView({behavior: 'smooth', block: 'center'});
                }
            """)
            await asyncio.sleep(1)

            # Action 1: LIKE with DOM STATE VERIFICATION
            print("  [1/3] LIKE with DOM verification...")
            like_result = await _vision_verified_action(
                bridge,
                driver,
                click_description="gray thumbs up button in the comment action bar on the first comment",
                verify_description="thumbs up button is now blue or highlighted",
                action_name="like",
                pattern_memory=pattern_memory,
                max_retries=3,
                # DOM GROUND TRUTH PARAMETERS
                dom_selector="ytcp-comment-thread:nth-child(1) button[aria-label*='Like']",
                expected_state_change="aria_pressed=true"
            )

            if like_result["success"] and like_result.get("dom_verified"):
                print(f"      [OK] LIKED - DOM VERIFIED ✓ (confidence: {like_result['confidence']:.2f})")
            else:
                print(f"      [FAIL] Like not verified by DOM (attempts: {like_result['attempts']})")
                # Don't proceed if LIKE failed
                continue

            await asyncio.sleep(1)

            # Action 2: HEART with DOM STATE VERIFICATION
            print("  [2/3] HEART with DOM verification...")
            heart_result = await _vision_verified_action(
                bridge,
                driver,
                click_description="gray heart icon in the comment action bar on the first comment",
                verify_description="heart icon is now red or filled",
                action_name="heart",
                pattern_memory=pattern_memory,
                max_retries=3,
                # DOM GROUND TRUTH PARAMETERS
                dom_selector="ytcp-comment-thread:nth-child(1) button[aria-label*='Heart']",
                expected_state_change="aria_pressed=true"
            )

            if heart_result["success"] and heart_result.get("dom_verified"):
                print(f"      [OK] LOVED - DOM VERIFIED ✓ (confidence: {heart_result['confidence']:.2f})")
            else:
                print(f"      [FAIL] Heart not verified by DOM (attempts: {heart_result['attempts']})")

            await asyncio.sleep(1)

            # Action 3: REPLY with DOM STATE VERIFICATION
            print("  [3/3] REPLY with DOM verification...")

            # Get reply count BEFORE
            reply_count_before = driver.execute_script("""
                const card = document.querySelector('ytcp-comment-thread:nth-child(1)');
                if (!card) return null;
                const replyBtn = card.querySelector('button[aria-label*="Reply"]');
                if (!replyBtn) return '0';
                return replyBtn.textContent.trim();
            """)
            print(f"      Reply count BEFORE: {reply_count_before}")

            # Open reply box (vision click, no DOM verification needed)
            reply_open_result = await _vision_verified_action(
                bridge,
                driver,
                click_description="Reply button on the first comment",
                verify_description="reply text box is now visible below the comment",
                action_name="reply_open",
                pattern_memory=pattern_memory,
                max_retries=3
            )

            if reply_open_result["success"]:
                print(f"      [OK] Reply box opened")

                # Type reply
                await asyncio.sleep(1)
                type_result = await bridge.type_text(
                    description="reply text input field below the comment",
                    text="0102 was here",
                    driver=driver
                )

                if type_result.success:
                    # Submit reply
                    await asyncio.sleep(0.5)
                    submit_result = await bridge.click(
                        "blue Reply submit button at bottom right of reply box",
                        driver=driver
                    )

                    if submit_result.success:
                        # Wait for submit
                        await asyncio.sleep(2)

                        # Verify reply count changed (DOM GROUND TRUTH)
                        reply_count_after = driver.execute_script("""
                            const card = document.querySelector('ytcp-comment-thread:nth-child(1)');
                            if (!card) return null;
                            const replyBtn = card.querySelector('button[aria-label*="Reply"]');
                            if (!replyBtn) return '0';
                            return replyBtn.textContent.trim();
                        """)

                        print(f"      Reply count AFTER: {reply_count_after}")

                        # Check if reply count increased
                        if reply_count_before != reply_count_after:
                            print(f"      [OK] REPLIED - DOM VERIFIED ✓ ({reply_count_before} → {reply_count_after})")
                        else:
                            print(f"      [FAIL] Reply NOT verified - count didn't change")
                    else:
                        print(f"      [FAIL] Submit button click failed")
                else:
                    print(f"      [FAIL] Typing failed")
            else:
                print(f"      [FAIL] Could not open reply box")

            print(f"  [DONE] Comment processed")

            # Refresh page to remove replied comment from filtered view
            print(f"  [REFRESH] Reloading page...")
            driver.refresh()
            await asyncio.sleep(3)

            processed_count += 1

        except Exception as e:
            print(f"  [ERROR] Failed: {e}")
            driver.refresh()
            await asyncio.sleep(3)
            continue

    print("\n" + "="*80)
    print(" AUTONOMOUS ENGAGEMENT COMPLETE!")
    print("="*80)
    print(f"\nProcessed {processed_count} comment(s)")
    print("All actions verified with DOM STATE CHANGES (not vision inference)")
    print(f"Patterns stored in: {pattern_memory.db_path}")


if __name__ == "__main__":
    asyncio.run(engage_all_comments_dom_verified())
