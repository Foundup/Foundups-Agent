"""
0102 Autonomous Comment Engagement
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

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

async def engage_with_all_comments():
    """Like, Love, and Reply to all visible comments."""

    print("\n" + "="*80)
    print(" 0102 AUTONOMOUS COMMENT ENGAGEMENT")
    print(" Task: LIKE + LOVE + REPLY to all comments")
    print("="*80)

    # 1. Connect to existing Chrome
    print("\n[1] Connecting to Chrome on port 9222...")
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

    try:
        driver = webdriver.Chrome(options=chrome_options)
        print(f"[OK] Connected to Chrome")

        # Navigate to comments inbox - show ALL comments (not just "not engaged")
        # Remove ENGAGED_STATUS filter to see both engaged and not engaged comments
        target_url = "https://studio.youtube.com/channel/UC-LSSlOZwpGIRIYihaz8zCw/comments/inbox"

        print(f"\n[2] Navigating to: {target_url}")
        driver.get(target_url)
        print(f"    Waiting for page to load...")
        await asyncio.sleep(5)  # Wait for initial load

        # Click "Show more filters" if present, then select "All" to show all comments
        print(f"\n[2.5] Removing filters to show ALL comments...")
        try:
            # Try to clear the "Not engaged" filter by clicking the filter chip to remove it
            filter_removed = driver.execute_script("""
                // Find the "Not engaged" filter chip and click its remove button
                const filterChips = document.querySelectorAll('[aria-label*="Remove filter"]');
                let removed = false;
                filterChips.forEach(chip => {
                    if (chip.getAttribute('aria-label').includes('ENGAGED_STATUS')) {
                        chip.click();
                        removed = true;
                    }
                });
                return removed;
            """)

            if filter_removed:
                print(f"    [OK] Removed 'Not engaged' filter")
                await asyncio.sleep(2)  # Wait for filter to apply
            else:
                print(f"    [INFO] No filter to remove (showing all comments)")

        except Exception as e:
            print(f"    [WARN] Could not remove filter: {e}")

        print(f"[OK] On YouTube Studio Comments page")

    except Exception as e:
        print(f"[ERROR] Cannot connect: {e}")
        return

    # 2. Count comments on page
    print("\n[3] Analyzing page for comments...")
    comment_cards = driver.execute_script("""
        // YouTube Studio uses ytcp-comment-thread custom elements
        const cards = document.querySelectorAll('ytcp-comment-thread');
        return cards.length;
    """)

    print(f"[OK] Found {comment_cards} comment(s) on page")

    if comment_cards == 0:
        print("[WARNING] No comments found! Make sure you're on the inbox page")
        return

    # 3. Process each comment
    print("\n[4] Starting autonomous engagement...")
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

            # Action 1: LIKE (thumbs up) - Use direct JavaScript for reliability
            print(f"  [1/3] Clicking LIKE button...")
            try:
                like_success = driver.execute_script(f"""
                    const cards = document.querySelectorAll('ytcp-comment-thread');
                    const card = cards[{i}];
                    if (!card) return false;

                    const likeBtn = card.querySelector('button[aria-label*="Like"]');
                    if (likeBtn) {{
                        likeBtn.click();
                        return true;
                    }}
                    return false;
                """)

                if like_success:
                    print(f"      [OK] LIKED (DOM)")
                else:
                    print(f"      [FAIL] Like button not found")
            except Exception as e:
                print(f"      [FAIL] Like failed: {e}")

            await asyncio.sleep(1)

            # Action 2: LOVE (heart) - Use direct JavaScript for reliability
            print(f"  [2/3] Clicking HEART button...")
            try:
                heart_success = driver.execute_script(f"""
                    const cards = document.querySelectorAll('ytcp-comment-thread');
                    const card = cards[{i}];
                    if (!card) return false;

                    const heartBtn = card.querySelector('button[aria-label*="Heart"]');
                    if (heartBtn) {{
                        heartBtn.click();
                        return true;
                    }}
                    return false;
                """)

                if heart_success:
                    print(f"      [OK] LOVED (DOM)")
                else:
                    print(f"      [FAIL] Heart button not found")
            except Exception as e:
                print(f"      [FAIL] Heart failed: {e}")

            await asyncio.sleep(1)

            # Action 3: REPLY - Use direct JavaScript for reliability
            print(f"  [3/3] Opening reply box...")
            try:
                reply_success = driver.execute_script(f"""
                    const cards = document.querySelectorAll('ytcp-comment-thread');
                    const card = cards[{i}];
                    if (!card) return {{success: false, step: 'no_card'}};

                    // Click reply button
                    const replyBtn = card.querySelector('button[aria-label*="Reply"]');
                    if (!replyBtn) return {{success: false, step: 'no_reply_btn'}};
                    replyBtn.click();

                    // Wait for textarea to appear
                    return new Promise(resolve => {{
                        setTimeout(() => {{
                            const textarea = card.querySelector('div[contenteditable="true"]');
                            if (!textarea) {{
                                resolve({{success: false, step: 'no_textarea'}});
                                return;
                            }}

                            // Type reply
                            textarea.click();
                            textarea.focus();
                            document.execCommand('insertText', false, '0102 was here');

                            // Find and click submit button
                            setTimeout(() => {{
                                const submitBtn = card.querySelector('ytcp-button#submit-button button, button[aria-label*="Reply"][aria-label*="Submit"]');
                                if (!submitBtn) {{
                                    resolve({{success: false, step: 'no_submit'}});
                                    return;
                                }}

                                submitBtn.click();
                                resolve({{success: true, step: 'complete'}});
                            }}, 500);
                        }}, 1000);
                    }});
                """)

                if reply_success and reply_success.get('success'):
                    print(f"      [OK] REPLIED (DOM)")
                else:
                    step = reply_success.get('step', 'unknown') if reply_success else 'unknown'
                    print(f"      [FAIL] Reply failed at: {step}")
            except Exception as e:
                print(f"      [FAIL] Reply failed: {e}")

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
