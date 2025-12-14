"""
Autonomous YouTube Studio Comment Engagement

Executes full engagement sequence on YouTube Studio comments:
1. Like (thumbs up)
2. Heart (love)
3. Reply "0102 was here"
4. Refresh page (top comment disappears)
5. Loop to next comment

Uses UI-TARS vision verification with retry.
"""
import sys
import asyncio
import time
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(repo_root))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from modules.infrastructure.foundups_vision.src.ui_tars_bridge import UITarsBridge

print("[AUTONOMOUS] YouTube Studio Comment Engagement")
print("=" * 80)

# Configuration
SKILLS_STORE = repo_root / "modules" / "infrastructure" / "wardrobe_ide" / "skills_store"
REPLY_TEXT = "0102 was here"
MAX_RETRIES_PER_ACTION = 3
COMMENT_ENGAGEMENT_LIMIT = int(input("\n[AUTONOMOUS] How many comments to engage? (enter number): ").strip())

# Connect to existing Chrome on port 9222
print("\n[AUTONOMOUS] Connecting to Chrome on port 9222...")
chrome_options = ChromeOptions()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

try:
    driver = webdriver.Chrome(options=chrome_options)
    print(f"[AUTONOMOUS] Connected! Current URL: {driver.current_url}")
except Exception as e:
    print(f"[ERROR] Could not connect to Chrome: {e}")
    print("[ERROR] Make sure Chrome is running with --remote-debugging-port=9222")
    sys.exit(1)

# Switch to YouTube Studio tab if not already on it
if "studio.youtube.com" not in driver.current_url or "comments" not in driver.current_url:
    print(f"[AUTONOMOUS] Not on YouTube Studio, switching tabs...")

    # Get all window handles
    all_windows = driver.window_handles
    print(f"[AUTONOMOUS] Found {len(all_windows)} tabs open")

    # Try to find YouTube Studio tab
    youtube_studio_found = False
    for window in all_windows:
        driver.switch_to.window(window)
        print(f"[AUTONOMOUS]   Checking tab: {driver.current_url[:80]}...")

        if "studio.youtube.com" in driver.current_url and "comments" in driver.current_url:
            print(f"[AUTONOMOUS]   FOUND YouTube Studio tab!")
            youtube_studio_found = True
            break

    if not youtube_studio_found:
        print("[ERROR] Could not find YouTube Studio comments tab")
        print("[ERROR] Please open YouTube Studio comments in Chrome with --remote-debugging-port=9222")
        driver.quit()
        sys.exit(1)

print(f"[AUTONOMOUS] Ready! URL: {driver.current_url[:100]}...")


async def verify_action_succeeded(bridge, description, verify_description, driver, max_retries=3):
    """
    Execute action with visual verification and retry.

    Args:
        bridge: UITarsBridge instance
        description: Natural language description of action target
        verify_description: Natural language description of success state
        driver: Selenium WebDriver instance
        max_retries: Maximum retry attempts

    Returns:
        True if action succeeded, False otherwise
    """
    for attempt in range(1, max_retries + 1):
        print(f"[AUTONOMOUS]   Attempt {attempt}/{max_retries}")

        # Execute the action
        result = await bridge.execute_action(
            action='click',
            description=description,
            driver=driver,
            timeout=90
        )

        if result.success:
            print(f"[AUTONOMOUS]      OK Clicked: {description}")
            print(f"[AUTONOMOUS]      Confidence: {result.confidence:.2f}")
            print(f"[AUTONOMOUS]      Duration: {result.duration_ms}ms")

            # Wait for UI to update
            time.sleep(1)

            # Verify the action succeeded
            print(f"[AUTONOMOUS]      Verifying action succeeded...")

            verify_result = await bridge.execute_action(
                action='verify',
                description=verify_description,
                driver=driver,
                timeout=90
            )

            # Check if verification found the success state
            if verify_result.success and verify_result.confidence > 0.6:
                print(f"[AUTONOMOUS]      VERIFIED: Action succeeded!")
                print(f"[AUTONOMOUS]      Verification confidence: {verify_result.confidence:.2f}")
                return True
            else:
                print(f"[AUTONOMOUS]      VERIFICATION FAILED")
                print(f"[AUTONOMOUS]      Verification confidence: {verify_result.confidence:.2f}")
                if attempt < max_retries:
                    print(f"[AUTONOMOUS]      Retrying...")
                    continue
                else:
                    print(f"[AUTONOMOUS]      Max retries reached")
                    return False
        else:
            print(f"[AUTONOMOUS]      FAILED: {result.error}")
            if attempt < max_retries:
                print(f"[AUTONOMOUS]      Retrying...")
                continue
            else:
                print(f"[AUTONOMOUS]      Max retries reached")
                return False

    return False


async def reply_with_text(bridge, driver, text, max_retries=3):
    """
    Execute reply sequence: click Reply → type text → submit.

    Returns:
        True if reply succeeded, False otherwise
    """
    print(f"[AUTONOMOUS]   Replying with: '{text}'")

    # Step 1: Click Reply button
    for attempt in range(1, max_retries + 1):
        print(f"[AUTONOMOUS]   Attempt {attempt}/{max_retries} - Opening reply box...")

        result = await bridge.execute_action(
            action='click',
            description="Reply button",
            driver=driver,
            timeout=90
        )

        if result.success:
            print(f"[AUTONOMOUS]      OK Clicked Reply button")
            time.sleep(1)

            # Verify textarea appeared
            verify_result = await bridge.execute_action(
                action='verify',
                description="reply text box is visible and active",
                driver=driver,
                timeout=90
            )

            if verify_result.success and verify_result.confidence > 0.6:
                print(f"[AUTONOMOUS]      VERIFIED: Reply box opened")
                break
            else:
                print(f"[AUTONOMOUS]      VERIFICATION FAILED: Reply box not visible")
                if attempt < max_retries:
                    print(f"[AUTONOMOUS]      Retrying...")
                    continue
                else:
                    return False
        else:
            print(f"[AUTONOMOUS]      FAILED: {result.error}")
            if attempt < max_retries:
                continue
            else:
                return False

    # Step 2: Type text directly (textarea should already be focused after clicking Reply)
    time.sleep(1)  # Wait for reply box to fully expand

    type_result = await bridge.type_text(
        description="reply text input area",
        text=text,
        driver=driver,
        timeout=90
    )

    if not type_result.success:
        print(f"[AUTONOMOUS]      FAILED to type text")
        return False

    print(f"[AUTONOMOUS]      OK Typed: '{text}'")
    time.sleep(1)

    # Step 4: Submit reply
    submit_result = await bridge.execute_action(
        action='click',
        description="Reply submit button",
        driver=driver,
        timeout=90
    )

    if not submit_result.success:
        print(f"[AUTONOMOUS]      FAILED to submit reply")
        return False

    print(f"[AUTONOMOUS]      OK Submitted reply")
    time.sleep(2)  # Wait for submission to complete

    return True


async def engage_comment(bridge, driver, comment_number):
    """
    Execute full engagement sequence on one comment.

    Returns:
        True if all actions succeeded, False otherwise
    """
    print(f"\n{'='*80}")
    print(f"[AUTONOMOUS] ENGAGING COMMENT #{comment_number}")
    print(f"{'='*80}")

    # Action 1: Like (thumbs up)
    print(f"\n[AUTONOMOUS] Action 1/3: LIKE")
    like_success = await verify_action_succeeded(
        bridge=bridge,
        description="Like button (thumbs up icon)",
        verify_description="highlighted thumbs up button (filled/blue icon showing it's been liked)",
        driver=driver,
        max_retries=MAX_RETRIES_PER_ACTION
    )

    if not like_success:
        print(f"[AUTONOMOUS]   FAILED to like comment")
        return False

    print(f"[AUTONOMOUS]   SUCCESS: Comment liked")
    time.sleep(1)

    # Action 2: Heart (love)
    print(f"\n[AUTONOMOUS] Action 2/3: HEART")
    heart_success = await verify_action_succeeded(
        bridge=bridge,
        description="Heart button (love icon)",
        verify_description="highlighted heart button (filled/red icon showing it's been loved)",
        driver=driver,
        max_retries=MAX_RETRIES_PER_ACTION
    )

    if not heart_success:
        print(f"[AUTONOMOUS]   FAILED to heart comment")
        return False

    print(f"[AUTONOMOUS]   SUCCESS: Comment hearted")
    time.sleep(1)

    # Action 3: Reply with "0102 was here"
    print(f"\n[AUTONOMOUS] Action 3/3: REPLY")
    reply_success = await reply_with_text(
        bridge=bridge,
        driver=driver,
        text=REPLY_TEXT,
        max_retries=MAX_RETRIES_PER_ACTION
    )

    if not reply_success:
        print(f"[AUTONOMOUS]   FAILED to reply to comment")
        return False

    print(f"[AUTONOMOUS]   SUCCESS: Reply posted")

    print(f"\n[AUTONOMOUS] Comment #{comment_number}: FULLY ENGAGED")
    return True


async def main():
    """Main orchestration loop."""

    # Initialize UI-TARS bridge
    print(f"\n[AUTONOMOUS] Initializing UI-TARS bridge...")
    bridge = UITarsBridge(browser_port=9222)
    await bridge.connect()
    print(f"[AUTONOMOUS] UI-TARS connected (ui-tars-1.5-7b via LM Studio)")

    comments_engaged = 0
    comments_failed = 0

    for i in range(1, COMMENT_ENGAGEMENT_LIMIT + 1):
        try:
            # Engage the current comment
            success = await engage_comment(bridge, driver, i)

            if success:
                comments_engaged += 1
                print(f"\n[AUTONOMOUS] Progress: {comments_engaged}/{COMMENT_ENGAGEMENT_LIMIT} comments engaged")
            else:
                comments_failed += 1
                print(f"\n[AUTONOMOUS] WARNING: Comment #{i} engagement failed")

            # Reload page to move to next comment (engaged comment disappears from filter)
            if i < COMMENT_ENGAGEMENT_LIMIT and success:
                print(f"\n[AUTONOMOUS] Reloading page to show next comment...")
                current_url = driver.current_url
                driver.get(current_url)  # Navigate to same URL (safer than driver.refresh())
                time.sleep(4)  # Wait for page to reload
                print(f"[AUTONOMOUS] Page reloaded - top comment should be the next one")

        except Exception as e:
            print(f"\n[AUTONOMOUS] ERROR on comment #{i}: {str(e)[:200]}")
            comments_failed += 1
            continue

    # Summary
    print(f"\n{'='*80}")
    print(f"[AUTONOMOUS] ENGAGEMENT COMPLETE")
    print(f"{'='*80}")
    print(f"[AUTONOMOUS] Comments engaged: {comments_engaged}")
    print(f"[AUTONOMOUS] Comments failed: {comments_failed}")
    print(f"[AUTONOMOUS] Success rate: {comments_engaged}/{COMMENT_ENGAGEMENT_LIMIT} ({(comments_engaged/COMMENT_ENGAGEMENT_LIMIT*100):.1f}%)")

    bridge.close()
    print(f"\n[AUTONOMOUS] UI-TARS bridge closed")


# Run autonomous engagement
asyncio.run(main())

print("\n[AUTONOMOUS] Disconnecting from Chrome (browser stays open)")
driver.quit()
