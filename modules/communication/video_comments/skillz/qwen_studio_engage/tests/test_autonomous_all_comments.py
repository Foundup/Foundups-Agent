"""
Test: Autonomous engagement with ALL comments - Self-correcting vision loop

Pattern: Action → Pic → Ask "is it selected?" → If NO (retry + learn) → If YES (next)

WSP Compliance:
- WSP 3: Proper module location (communication/video_comments)
- WSP 96: WRE Skills with pattern learning
- WSP 77: Multi-tier vision (UI-TARS)
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


async def engage_all_comments():
    """
    Engage with ALL comments on YouTube Studio using self-correcting vision loop.

    Process:
    1. Navigate to Studio inbox
    2. For each comment:
       - LIKE (with vision verification)
       - HEART (with vision verification)
       - REPLY "0102 was here" (with vision verification)
    3. Refresh page (filter removes replied comments)
    4. Repeat until no comments left
    """
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from modules.infrastructure.foundups_vision.src.ui_tars_bridge import UITarsBridge
    from modules.infrastructure.wre_core.src.pattern_memory import PatternMemory

    print("\n" + "="*80)
    print(" 0102 AUTONOMOUS COMMENT ENGAGEMENT - SELF-CORRECTING VISION")
    print(" Pattern: Action → Pic → Ask → Verify → Retry + Learn")
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

    # Import the self-correcting action function
    from modules.communication.video_comments.skillz.qwen_studio_engage.executor import _vision_verified_action

    print("\n[4] Starting autonomous engagement loop...")
    print("="*80)
    print("Pattern per comment: LIKE → HEART → REPLY → REFRESH")
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

            # Action 1: LIKE with self-correcting vision
            print("  [1/3] LIKE with vision verification...")
            like_result = await _vision_verified_action(
                bridge,
                driver,  # Pass Selenium driver
                click_description="gray thumbs up button in the comment action bar on the first comment",
                verify_description="thumbs up button is now blue or highlighted",
                action_name="like",
                pattern_memory=pattern_memory,
                max_retries=3
            )

            if like_result["success"]:
                print(f"      [OK] LIKED (confidence: {like_result['confidence']:.2f}, attempts: {like_result['attempts']})")
            else:
                print(f"      [FAIL] Like failed after {like_result['attempts']} attempts")

            await asyncio.sleep(1)

            # Action 2: HEART with self-correcting vision
            print("  [2/3] HEART with vision verification...")
            heart_result = await _vision_verified_action(
                bridge,
                driver,  # Pass Selenium driver
                click_description="gray heart icon in the comment action bar on the first comment",
                verify_description="heart icon is now red or filled",
                action_name="heart",
                pattern_memory=pattern_memory,
                max_retries=3
            )

            if heart_result["success"]:
                print(f"      [OK] LOVED (confidence: {heart_result['confidence']:.2f}, attempts: {heart_result['attempts']})")
            else:
                print(f"      [FAIL] Heart failed after {heart_result['attempts']} attempts")

            await asyncio.sleep(1)

            # Action 3: REPLY with self-correcting vision
            print("  [3/3] REPLY with vision verification...")

            # Open reply box
            reply_open_result = await _vision_verified_action(
                bridge,
                driver,  # Pass Selenium driver
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
                    driver=driver  # Pass Selenium driver
                )

                if type_result.success:
                    # Submit reply
                    await asyncio.sleep(0.5)
                    submit_result = await _vision_verified_action(
                        bridge,
                        driver,  # Pass Selenium driver
                        click_description="blue Reply submit button at bottom right of reply box",
                        verify_description="reply '0102 was here' is now visible under the comment",
                        action_name="reply_submit",
                        pattern_memory=pattern_memory,
                        max_retries=3
                    )

                    if submit_result["success"]:
                        print(f"      [OK] REPLIED (confidence: {submit_result['confidence']:.2f}, attempts: {submit_result['attempts']})")
                    else:
                        print(f"      [FAIL] Reply submit failed")
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
    print("All actions verified with UI-TARS vision + pattern learning")
    print(f"Patterns stored in: {pattern_memory.db_path}")


if __name__ == "__main__":
    asyncio.run(engage_all_comments())
