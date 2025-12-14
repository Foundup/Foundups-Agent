"""
0102 Manual Comment Engagement - Direct JavaScript Clicking
Navigate to ALL comments (no filter) and click buttons directly
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

async def engage_manually():
    """Manually engage with comments using direct JavaScript."""

    print("\n" + "="*80)
    print(" 0102 MANUAL COMMENT ENGAGEMENT")
    print("="*80)

    # 1. Connect to Chrome
    print("\n[1] Connecting to Chrome...")
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=chrome_options)

    # 2. Navigate to unfiltered inbox (remove engaged status filter)
    print("\n[2] Navigating to ALL comments (no filter)...")
    # This URL shows ALL comments, not just "not engaged"
    driver.get("https://studio.youtube.com/channel/UC-LSSlOZwpGIRIYihaz8zCw/comments")
    await asyncio.sleep(5)

    # 3. Check what's on the page
    print("\n[3] Checking page structure...")
    page_info = driver.execute_script("""
        return {
            url: window.location.href,
            threads: document.querySelectorAll('ytcp-comment-thread').length,
            allButtons: document.querySelectorAll('button').length,
            likeButtons: document.querySelectorAll('button[aria-label*="Like"]').length,
            heartButtons: document.querySelectorAll('button[aria-label*="Heart"]').length,
            replyButtons: document.querySelectorAll('button[aria-label*="Reply"]').length,
        };
    """)

    print(f"    URL: {page_info['url']}")
    print(f"    Comment threads: {page_info['threads']}")
    print(f"    All buttons: {page_info['allButtons']}")
    print(f"    Like buttons: {page_info['likeButtons']}")
    print(f"    Heart buttons: {page_info['heartButtons']}")
    print(f"    Reply buttons: {page_info['replyButtons']}")

    if page_info['threads'] == 0:
        print("\n[WARNING] No comment threads found! Please navigate to comments page manually.")
        return

    # 4. Try clicking the first comment's buttons as a test
    print(f"\n[4] Testing with first comment...")
    result = driver.execute_script("""
        // Get first comment thread
        const thread = document.querySelector('ytcp-comment-thread');
        if (!thread) return {success: false, error: 'No thread found'};

        // Scroll into view
        thread.scrollIntoView({behavior: 'smooth', block: 'center'});

        const results = {
            like: false,
            heart: false,
            reply: false,
            error: null
        };

        try {
            // Find Like button within this thread
            const likeBtn = thread.querySelector('button[aria-label*="Like"]');
            if (likeBtn) {
                likeBtn.click();
                results.like = true;
            }

            // Wait a bit
            await new Promise(r => setTimeout(r, 500));

            // Find Heart button
            const heartBtn = thread.querySelector('button[aria-label*="Heart"]');
            if (heartBtn) {
                heartBtn.click();
                results.heart = true;
            }

            await new Promise(r => setTimeout(r, 500));

            // Find Reply button
            const replyBtn = thread.querySelector('button[aria-label*="Reply"]');
            if (replyBtn) {
                replyBtn.click();
                results.reply = true;
            }

            results.success = true;
            return results;

        } catch (e) {
            results.error = e.toString();
            return results;
        }
    """)

    print(f"\n[RESULT]")
    print(f"  Success: {result.get('success', False)}")
    print(f"  Like clicked: {result.get('like', False)}")
    print(f"  Heart clicked: {result.get('heart', False)}")
    print(f"  Reply clicked: {result.get('reply', False)}")
    if result.get('error'):
        print(f"  Error: {result['error']}")

    print("\n" + "="*80)
    print(" TEST COMPLETE")
    print("="*80)
    print("\nCheck YouTube Studio page to see if Like and Heart buttons are now active/blue.")

if __name__ == "__main__":
    asyncio.run(engage_manually())
