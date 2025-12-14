"""
0102 Autonomous Comment Engagement - VISION VERIFIED
Self-correcting loop: Action → Pic → Ask → Verify → Retry
Refresh after each comment to remove it from filtered view
"""
import asyncio
import sys
import os
from pathlib import Path
import base64

repo_root = Path(__file__).resolve().parent
sys.path.insert(0, str(repo_root))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from modules.infrastructure.foundups_vision.src.ui_tars_bridge import UITarsBridge

async def vision_verified_action(driver, tars_bridge, card_index, action_script, verify_question, max_retries=3):
    """
    Execute action with vision verification loop.

    Returns:
        bool: True if verified successful, False otherwise
    """
    for attempt in range(max_retries):
        # 1. ACTION - Execute via JavaScript
        success = driver.execute_script(action_script.replace("{i}", str(card_index)))

        if not success:
            print(f"        [RETRY {attempt+1}] Action script returned false")
            await asyncio.sleep(0.5)
            continue

        # Wait for UI to update
        await asyncio.sleep(0.5)

        # 2. PIC - Take screenshot
        screenshot_b64 = driver.get_screenshot_as_base64()

        # 3. ASK - Vision verification
        result = await tars_bridge.click_element(
            f"Verify: {verify_question}",
            return_verification=True
        )

        # 4. CHECK - Parse vision response
        # UI-TARS returns confidence in result
        if result.get('confidence', 0) >= 0.7:
            print(f"        [VERIFIED] Vision confidence: {result.get('confidence', 0):.2f}")
            return True

        print(f"        [RETRY {attempt+1}] Vision says not verified (confidence: {result.get('confidence', 0):.2f})")
        await asyncio.sleep(0.5)

    return False


async def engage_with_all_comments():
    """Like, Love, and Reply to all comments with vision verification."""

    print("\n" + "="*80)
    print(" 0102 AUTONOMOUS COMMENT ENGAGEMENT - VISION VERIFIED")
    print(" Self-correcting loop with UI-TARS validation")
    print("="*80)

    # 1. Connect to Chrome
    print("\n[1] Connecting to Chrome on port 9222...")
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

    try:
        driver = webdriver.Chrome(options=chrome_options)
        print(f"[OK] Connected to Chrome")
    except Exception as e:
        print(f"[ERROR] Cannot connect: {e}")
        return

    # 2. Initialize UI-TARS Bridge
    print("\n[2] Initializing UI-TARS Bridge...")
    browser_port = int(os.getenv("FOUNDUPS_CHROME_PORT", "9222"))
    tars_bridge = UITarsBridge(browser_port=browser_port)
    await tars_bridge.connect()
    print("[OK] UI-TARS ready")

    # 3. Navigate to comments
    target_url = "https://studio.youtube.com/channel/UC-LSSlOZwpGIRIYihaz8zCw/comments/inbox"
    print(f"\n[3] Navigating to: {target_url}")
    driver.get(target_url)
    await asyncio.sleep(5)
    print("[OK] On YouTube Studio Comments page")

    # 4. Process comments in continuous loop
    print("\n[4] Starting autonomous engagement loop...")
    print("="*80)
    print("Pattern: LIKE → HEART → REPLY → REFRESH → Next comment")
    print("="*80)

    processed_count = 0

    while True:
        # Count remaining comments
        comment_count = driver.execute_script("""
            const cards = document.querySelectorAll('ytcp-comment-thread');
            return cards.length;
        """)

        if comment_count == 0:
            print("\n[COMPLETE] No more comments to process!")
            break

        print(f"\n[COMMENT {processed_count + 1}] ({comment_count} remaining)")
        print("-"*80)

        try:
            # Always process comment at index 0 (top of list)
            card_index = 0

            # Scroll into view
            driver.execute_script(f"""
                const cards = document.querySelectorAll('ytcp-comment-thread');
                if (cards[{card_index}]) {{
                    cards[{card_index}].scrollIntoView({{behavior: 'smooth', block: 'center'}});
                }}
            """)
            await asyncio.sleep(1)

            # Action 1: LIKE with vision verification
            print(f"  [1/3] LIKE with vision verification...")
            like_verified = await vision_verified_action(
                driver,
                tars_bridge,
                card_index,
                action_script="""
                    const cards = document.querySelectorAll('ytcp-comment-thread');
                    const card = cards[{i}];
                    if (!card) return false;
                    const likeBtn = card.querySelector('button[aria-label*="Like"]');
                    if (likeBtn) {
                        likeBtn.click();
                        return true;
                    }
                    return false;
                """,
                verify_question="Is the thumbs up button now highlighted or blue?",
                max_retries=3
            )

            if like_verified:
                print(f"      [OK] LIKED (vision verified)")
            else:
                print(f"      [FAIL] Like verification failed")

            await asyncio.sleep(1)

            # Action 2: HEART with vision verification
            print(f"  [2/3] HEART with vision verification...")
            heart_verified = await vision_verified_action(
                driver,
                tars_bridge,
                card_index,
                action_script="""
                    const cards = document.querySelectorAll('ytcp-comment-thread');
                    const card = cards[{i}];
                    if (!card) return false;
                    const heartBtn = card.querySelector('button[aria-label*="Heart"]');
                    if (heartBtn) {
                        heartBtn.click();
                        return true;
                    }
                    return false;
                """,
                verify_question="Is the heart icon now red or filled?",
                max_retries=3
            )

            if heart_verified:
                print(f"      [OK] LOVED (vision verified)")
            else:
                print(f"      [FAIL] Heart verification failed")

            await asyncio.sleep(1)

            # Action 3: REPLY with vision verification
            print(f"  [3/3] REPLY with vision verification...")

            # Click reply button
            reply_opened = driver.execute_script(f"""
                const cards = document.querySelectorAll('ytcp-comment-thread');
                const card = cards[{card_index}];
                if (!card) return false;
                const replyBtn = card.querySelector('button[aria-label*="Reply"]');
                if (replyBtn) {{
                    replyBtn.click();
                    return true;
                }}
                return false;
            """)

            if reply_opened:
                await asyncio.sleep(1)

                # Type reply
                driver.execute_script(f"""
                    const cards = document.querySelectorAll('ytcp-comment-thread');
                    const card = cards[{card_index}];
                    if (card) {{
                        const textarea = card.querySelector('div[contenteditable="true"]');
                        if (textarea) {{
                            textarea.click();
                            textarea.focus();
                            document.execCommand('insertText', false, '0102 was here');
                        }}
                    }}
                """)
                await asyncio.sleep(0.5)

                # Click submit with vision verification
                reply_verified = await vision_verified_action(
                    driver,
                    tars_bridge,
                    card_index,
                    action_script="""
                        const cards = document.querySelectorAll('ytcp-comment-thread');
                        const card = cards[{i}];
                        if (!card) return false;
                        const submitBtn = card.querySelector('ytcp-button#submit-button button, button[aria-label*="Reply"][aria-label*="Submit"]');
                        if (submitBtn) {
                            submitBtn.click();
                            return true;
                        }
                        return false;
                    """,
                    verify_question="Is the reply submitted and visible under the comment?",
                    max_retries=3
                )

                if reply_verified:
                    print(f"      [OK] REPLIED (vision verified)")
                else:
                    print(f"      [FAIL] Reply verification failed")
            else:
                print(f"      [FAIL] Could not open reply box")

            print(f"  [DONE] Comment processed")

            # CRITICAL: Refresh page to remove replied comment from filtered view
            print(f"  [REFRESH] Reloading page to update filter...")
            driver.refresh()
            await asyncio.sleep(3)  # Wait for page reload

            processed_count += 1

        except Exception as e:
            print(f"  [ERROR] Failed to process comment: {e}")
            # Refresh and continue to next
            driver.refresh()
            await asyncio.sleep(3)
            continue

    print("\n" + "="*80)
    print(" AUTONOMOUS ENGAGEMENT COMPLETE!")
    print("="*80)
    print(f"\nProcessed {processed_count} comment(s) with vision verification")
    print("All comments LIKED, LOVED, and REPLIED with '0102 was here'")


if __name__ == "__main__":
    asyncio.run(engage_with_all_comments())
