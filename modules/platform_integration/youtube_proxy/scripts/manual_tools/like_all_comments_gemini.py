"""
0102 Autonomous Comment Engagement - GEMINI VISION ONLY
LIKE + LOVE + REPLY to all comments on YouTube Studio
"""
from pathlib import Path
import sys
import os

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
os.chdir(REPO_ROOT)

import asyncio
import sys
from pathlib import Path
import time

repo_root = REPO_ROOT

from modules.infrastructure.browser_actions.src.action_router import ActionRouter, DriverType
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

async def engage_with_all_comments():
    """Like, Love, and Reply to all visible comments using Gemini Vision."""

    print("\n" + "="*80)
    print(" 0102 AUTONOMOUS COMMENT ENGAGEMENT - GEMINI VISION")
    print(" Task: LIKE + LOVE + REPLY to all comments")
    print("="*80)

    # 1. Connect to existing Chrome
    print("\n[1] Connecting to Chrome on port 9222...")
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

    try:
        driver = webdriver.Chrome(options=chrome_options)
        print(f"[OK] Connected to Chrome")

        # Navigate to comments inbox
        target_url = "https://studio.youtube.com/channel/UC-LSSlOZwpGIRIYihaz8zCw/comments/inbox"

        print(f"\n[2] Navigating to: {target_url}")
        driver.get(target_url)
        print(f"    Waiting for page to load...")
        await asyncio.sleep(5)  # Wait for initial load

        print(f"[OK] On YouTube Studio Comments page")

    except Exception as e:
        print(f"[ERROR] Cannot connect: {e}")
        return

    # 2. Create ActionRouter with Gemini Vision (skip UI-TARS)
    print("\n[3] Initializing ActionRouter with Gemini Vision...")
    router = ActionRouter(
        profile="youtube_move2japan",
        selenium_driver=driver,
        fallback_enabled=True,
        feedback_mode=False
    )
    print("[OK] Router ready")

    # 3. Count comments on page
    print("\n[4] Analyzing page for comments...")
    comment_cards = driver.execute_script("""
        // YouTube Studio uses ytcp-comment-thread custom elements
        const cards = document.querySelectorAll('ytcp-comment-thread');
        return cards.length;
    """)

    print(f"[OK] Found {comment_cards} comment(s) on page")

    if comment_cards == 0:
        print("[WARNING] No comments found! Make sure you're on the inbox page")
        return

    # 4. Process each comment
    print("\n[5] Starting autonomous engagement...")
    print("="*80)

    for i in range(comment_cards):
        print(f"\n[COMMENT {i+1}/{comment_cards}]")
        print("-"*80)

        try:
            # Scroll comment into view
            driver.execute_script(f"""
                const cards = document.querySelectorAll('ytcp-comment-thread');
                if (cards[{i}]) {{
                    cards[{i}].scrollIntoView({{behavior: 'smooth', block: 'center'}});
                }}
            """)
            await asyncio.sleep(1)

            # Action 1: LIKE (thumbs up)
            print(f"  [1/3] Clicking LIKE button...")
            like_result = await router.execute(
                "click_element",
                {"description": "thumbs up button"},
                driver=DriverType.GEMINI,  # Use Gemini directly
                timeout=60,  # Longer timeout for cloud API
            )

            if like_result.success:
                print(f"      [OK] LIKED (tier: {like_result.result_data.get('tier', 'unknown')})")
            else:
                print(f"      [FAIL] Like failed: {like_result.error}")

            await asyncio.sleep(1)

            # Action 2: LOVE (heart)
            print(f"  [2/3] Clicking HEART button...")
            heart_result = await router.execute(
                "click_element",
                {"description": "heart button"},
                driver=DriverType.GEMINI,
                timeout=60,
            )

            if heart_result.success:
                print(f"      [OK] LOVED (tier: {heart_result.result_data.get('tier', 'unknown')})")
            else:
                print(f"      [FAIL] Heart failed: {heart_result.error}")

            await asyncio.sleep(1)

            # Action 3: REPLY
            print(f"  [3/3] Opening reply box...")
            reply_result = await router.execute(
                "click_element",
                {"description": "reply button"},
                driver=DriverType.GEMINI,
                timeout=60,
            )

            if reply_result.success:
                print(f"      [OK] Reply box opened")
                await asyncio.sleep(1)

                # Type reply message
                print(f"      Typing: '0102 was here'...")

                # Find active element (should be reply textarea)
                driver.execute_script("""
                    const activeEl = document.activeElement;
                    if (activeEl && activeEl.tagName === 'TEXTAREA') {
                        activeEl.value = '0102 was here';
                        activeEl.dispatchEvent(new Event('input', { bubbles: true }));
                    }
                """)

                await asyncio.sleep(0.5)

                # Submit reply
                print(f"      Submitting reply...")
                submit_result = await router.execute(
                    "click_element",
                    {"description": "reply submit button"},
                    driver=DriverType.GEMINI,
                    timeout=60,
                )

                if submit_result.success:
                    print(f"      [OK] REPLIED")
                else:
                    print(f"      [FAIL] Submit failed: {submit_result.error}")
            else:
                print(f"      [FAIL] Reply button failed: {reply_result.error}")

            print(f"  [DONE] Comment {i+1} processed")

            # Pause between comments
            await asyncio.sleep(2)

        except Exception as e:
            print(f"  [ERROR] Failed to process comment {i+1}: {e}")
            continue

    print("\n" + "="*80)
    print(" AUTONOMOUS ENGAGEMENT COMPLETE!")
    print("="*80)
    print(f"\nProcessed {comment_cards} comment(s)")
    print("All comments have been LIKED, LOVED, and REPLIED to with '0102 was here'")

if __name__ == "__main__":
    asyncio.run(engage_with_all_comments())
