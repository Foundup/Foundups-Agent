"""
0102 Autonomous Agent - Context-Aware Vision
Give vision model MORE context about where buttons are located
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

from modules.infrastructure.browser_actions.src.action_router import ActionRouter, DriverType
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

async def autonomous_engage():
    """0102 acting as autonomous agent for 012."""

    print("\n" + "="*80)
    print(" 0102 AUTONOMOUS AGENT - CONTEXT-AWARE VISION")
    print(" Acting on behalf of 012")
    print("="*80)

    # Connect to Chrome
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=chrome_options)

    print("\n[1] Connected to 012's Chrome session")
    print(f"    URL: {driver.current_url[:80]}")

    # Navigate to comments
    driver.get("https://studio.youtube.com/channel/UC-LSSlOZwpGIRIYihaz8zCw/comments/inbox")
    await asyncio.sleep(5)

    # Remove "Not engaged" filter using JavaScript
    print("\n[2] Removing filters to show ALL comments...")
    driver.execute_script("""
        // Remove the ENGAGED_STATUS filter from URL
        const url = new URL(window.location.href);
        const filter = JSON.parse(decodeURIComponent(url.searchParams.get('filter') || '[]'));
        const newFilter = filter.filter(f => f.name !== 'ENGAGED_STATUS');
        url.searchParams.set('filter', encodeURIComponent(JSON.stringify(newFilter)));
        window.location.href = url.toString();
    """)
    await asyncio.sleep(5)

    # Count comments
    comment_count = driver.execute_script("""
        return document.querySelectorAll('ytcp-comment-thread').length;
    """)

    print(f"[3] Found {comment_count} comments")

    if comment_count == 0:
        print("[ERROR] No comments visible. Please manually navigate to comments page.")
        return

    # Create ActionRouter with vision
    router = ActionRouter(
        profile="youtube_move2japan",
        selenium_driver=driver,
        fallback_enabled=True,
        feedback_mode=False
    )

    print(f"\n[4] 0102 processing {comment_count} comments autonomously...")
    print("="*80)

    # Process each comment
    for i in range(comment_count):
        print(f"\n[COMMENT {i+1}/{comment_count}]")

        # Scroll comment into view
        driver.execute_script(f"""
            const threads = document.querySelectorAll('ytcp-comment-thread');
            if (threads[{i}]) {{
                threads[{i}].scrollIntoView({{behavior: 'smooth', block: 'center'}});
            }}
        """)
        await asyncio.sleep(2)  # Wait for scroll + vision processing

        # CRITICAL: Use MORE SPECIFIC descriptions with visual context

        # Action 1: LIKE
        print(f"  [1/3] LIKE...")
        like_result = await router.execute(
            "click_element",
            {"description": "gray thumbs up icon button in the comment action toolbar below the comment text"},
            driver=DriverType.VISION,
            timeout=45,
        )
        print(f"      {('LIKED' if like_result.success else 'FAILED')}")
        await asyncio.sleep(1)

        # Action 2: HEART
        print(f"  [2/3] HEART...")
        heart_result = await router.execute(
            "click_element",
            {"description": "heart icon button in the comment action toolbar next to the thumbs up button"},
            driver=DriverType.VISION,
            timeout=45,
        )
        print(f"      {('LOVED' if heart_result.success else 'FAILED')}")
        await asyncio.sleep(1)

        # Action 3: REPLY
        print(f"  [3/3] REPLY...")
        reply_result = await router.execute(
            "click_element",
            {"description": "reply button text link in the comment action toolbar"},
            driver=DriverType.VISION,
            timeout=45,
        )

        if reply_result.success:
            await asyncio.sleep(1)

            # Type reply using JavaScript (more reliable)
            driver.execute_script(f"""
                const threads = document.querySelectorAll('ytcp-comment-thread');
                const thread = threads[{i}];
                if (thread) {{
                    const textarea = thread.querySelector('div[contenteditable="true"]');
                    if (textarea) {{
                        textarea.click();
                        textarea.focus();
                        document.execCommand('insertText', false, '0102 was here');
                    }}
                }}
            """)
            await asyncio.sleep(0.5)

            # Submit reply
            submit_result = await router.execute(
                "click_element",
                {"description": "blue Reply submit button below the text input box"},
                driver=DriverType.VISION,
                timeout=45,
            )
            print(f"      {('REPLIED' if submit_result.success else 'REPLY FAILED')}")
        else:
            print(f"      REPLY FAILED")

        await asyncio.sleep(2)

    print("\n" + "="*80)
    print(" 0102 AUTONOMOUS AGENT COMPLETE")
    print("="*80)
    print(f"\n0102 processed {comment_count} comments on behalf of 012")

if __name__ == "__main__":
    asyncio.run(autonomous_engage())
