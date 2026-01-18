"""
Quick diagnostic to check comment detection on Chrome/Edge.
Run this while Chrome/Edge are open on YouTube Studio inbox.
"""
import asyncio
import sys
from pathlib import Path

# Add repo root to sys.path (WSP 50: never assume cwd)
_here = Path(__file__).resolve()
for _parent in [_here] + list(_here.parents):
    if (_parent / "modules").exists() and (_parent / "holo_index.py").exists():
        sys.path.insert(0, str(_parent))
        break

from selenium import webdriver

async def check_comments(port: int, browser_name: str):
    print(f"\n{'='*60}")
    print(f" CHECKING {browser_name} (port {port})")
    print(f"{'='*60}")

    try:
        if browser_name == "Edge":
            from selenium.webdriver.edge.options import Options as EdgeOptions
            opts = EdgeOptions()
            opts.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
            driver = webdriver.Edge(options=opts)
        else:
            from selenium.webdriver.chrome.options import Options
            opts = Options()
            opts.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
            driver = webdriver.Chrome(options=opts)

        print(f"  URL: {driver.current_url[:80]}...")

        # Check for comment threads
        count = driver.execute_script(
            "return document.querySelectorAll('ytcp-comment-thread').length"
        )
        print(f"  Comment threads found: {count}")

        if count > 0:
            # Get first comment details
            first_comment = driver.execute_script("""
                const thread = document.querySelector('ytcp-comment-thread');
                if (!thread) return null;

                // Try to get author and text
                const authorEl = thread.querySelector('[id*="author-text"], .author-text, ytcp-comment-author');
                const textEl = thread.querySelector('[id*="content-text"], .content-text');

                return {
                    author: authorEl ? authorEl.innerText.trim() : 'Unknown',
                    text: textEl ? textEl.innerText.substring(0, 50) : 'Unknown',
                    likeBtn: !!thread.querySelector('#like-button'),
                    heartBtn: !!thread.querySelector('#creator-heart-button'),
                    replyBtn: !!thread.querySelector('#reply-button')
                };
            """)

            if first_comment:
                print(f"  First comment:")
                print(f"    Author: {first_comment['author']}")
                print(f"    Text: {first_comment['text']}...")
                print(f"    Like button: {first_comment['likeBtn']}")
                print(f"    Heart button: {first_comment['heartBtn']}")
                print(f"    Reply button: {first_comment['replyBtn']}")
        else:
            # Check for empty state
            empty_check = driver.execute_script("""
                const bodyText = document.body.innerText || '';
                return {
                    noComments: bodyText.includes('No comments') ||
                                bodyText.includes('All caught up'),
                    bodySnippet: bodyText.substring(0, 200)
                };
            """)
            print(f"  Empty state detected: {empty_check['noComments']}")
            print(f"  Page text snippet: {empty_check['bodySnippet'][:100]}...")

    except Exception as e:
        print(f"  ERROR: {e}")

async def main():
    # Check Chrome
    await check_comments(9222, "Chrome")

    # Check Edge
    await check_comments(9223, "Edge")

    print("\n" + "="*60)
    print(" DIAGNOSTIC COMPLETE")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
