"""
0102 Autonomous Comment Engagement - PRECISE TARGETING
Use DOM-based clicking for reliability
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

repo_root = REPO_ROOT

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

async def engage_with_all_comments():
    """Like, Love, and Reply to all comments using DOM selectors."""

    print("\n" + "="*80)
    print(" 0102 AUTONOMOUS COMMENT ENGAGEMENT - PRECISE DOM TARGETING")
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
        await asyncio.sleep(5)
        print(f"[OK] On YouTube Studio Comments page")

    except Exception as e:
        print(f"[ERROR] Cannot connect: {e}")
        return

    # 3. Count comments
    print("\n[3] Analyzing page for comments...")
    comment_threads = driver.find_elements(By.CSS_SELECTOR, "ytcp-comment-thread")
    print(f"[OK] Found {len(comment_threads)} comment(s)")

    if len(comment_threads) == 0:
        print("[WARNING] No comments found!")
        return

    # 4. Process each comment using DOM clicking
    print("\n[4] Starting autonomous engagement...")
    print("="*80)

    for i, thread in enumerate(comment_threads, 1):
        print(f"\n[COMMENT {i}/{len(comment_threads)}]")
        print("-"*80)

        try:
            # Scroll into view
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", thread)
            await asyncio.sleep(1)

            # Find action buttons within this specific comment thread
            # YouTube Studio uses specific button IDs

            # Action 1: LIKE (thumbs up)
            print(f"  [1/3] Clicking LIKE button...")
            try:
                like_button = thread.find_element(By.CSS_SELECTOR, "button[aria-label*='Like']")
                like_button.click()
                print(f"      [OK] LIKED")
                await asyncio.sleep(1)
            except Exception as e:
                print(f"      [FAIL] Like failed: {e}")

            # Action 2: LOVE (heart)
            print(f"  [2/3] Clicking HEART button...")
            try:
                heart_button = thread.find_element(By.CSS_SELECTOR, "button[aria-label*='Heart']")
                heart_button.click()
                print(f"      [OK] LOVED")
                await asyncio.sleep(1)
            except Exception as e:
                print(f"      [FAIL] Heart failed: {e}")

            # Action 3: REPLY
            print(f"  [3/3] Opening reply box...")
            try:
                reply_button = thread.find_element(By.CSS_SELECTOR, "button[aria-label*='Reply']")
                reply_button.click()
                await asyncio.sleep(1)
                print(f"      [OK] Reply box opened")

                # Find reply textarea
                reply_textarea = thread.find_element(By.CSS_SELECTOR, "div[contenteditable='true']")
                reply_textarea.click()
                reply_textarea.send_keys("0102 was here")
                await asyncio.sleep(0.5)

                print(f"      Typed: '0102 was here'")

                # Submit reply
                submit_button = thread.find_element(By.CSS_SELECTOR, "button[aria-label*='Reply'][aria-label*='Submit'], ytcp-button#submit-button button")
                submit_button.click()
                print(f"      [OK] REPLIED")
                await asyncio.sleep(1)

            except Exception as e:
                print(f"      [FAIL] Reply failed: {e}")

            print(f"  [DONE] Comment {i} processed")
            await asyncio.sleep(2)

        except Exception as e:
            print(f"  [ERROR] Failed to process comment {i}: {e}")
            continue

    print("\n" + "="*80)
    print(" AUTONOMOUS ENGAGEMENT COMPLETE!")
    print("="*80)
    print(f"\nProcessed {len(comment_threads)} comment(s)")

if __name__ == "__main__":
    asyncio.run(engage_with_all_comments())
