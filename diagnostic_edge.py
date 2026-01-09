"""
Edge Comment Processing Diagnostic
===================================
Tests Edge browser connection and comment detection independently.

Usage:
    python diagnostic_edge.py
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# Add repo root to path
repo_root = Path(__file__).resolve().parent
sys.path.insert(0, str(repo_root))


async def diagnose_edge():
    """Run Edge diagnostic checks."""

    print("\n" + "="*70)
    print(" EDGE COMMENT PROCESSING DIAGNOSTIC")
    print("="*70 + "\n")

    # Step 1: Check if Edge port is open
    print("[STEP 1] Checking Edge debug port 9223...")
    import socket
    try:
        sock = socket.create_connection(("127.0.0.1", 9223), timeout=2.0)
        sock.close()
        print("  ✅ Edge port 9223 is OPEN")
    except Exception as e:
        print(f"  ❌ Edge port 9223 NOT reachable: {e}")
        print("  → Launch Edge with: msedge --remote-debugging-port=9223")
        return

    # Step 2: Connect to Edge via Selenium
    print("\n[STEP 2] Connecting to Edge via Selenium...")
    try:
        from selenium import webdriver
        from selenium.webdriver.edge.options import Options as EdgeOptions

        edge_opts = EdgeOptions()
        edge_opts.add_experimental_option("debuggerAddress", "127.0.0.1:9223")
        driver = webdriver.Edge(options=edge_opts)
        print(f"  ✅ Connected to Edge")
        print(f"  → Current URL: {driver.current_url[:80]}...")
    except Exception as e:
        print(f"  ❌ Failed to connect to Edge: {e}")
        return

    # Step 3: Check if on YouTube Studio
    print("\n[STEP 3] Checking current page...")
    current_url = driver.current_url
    if "studio.youtube.com" in current_url:
        print(f"  ✅ On YouTube Studio")
        if "/comments/inbox" in current_url:
            print(f"  ✅ On comments inbox page")
        else:
            print(f"  ⚠️ NOT on comments inbox (current: {current_url[:60]})")
    else:
        print(f"  ❌ NOT on YouTube Studio")
        print(f"  → Current URL: {current_url}")

    # Step 4: Navigate to FoundUps Studio inbox
    print("\n[STEP 4] Navigating to FoundUps Studio inbox...")
    foundups_channel_id = os.getenv("FOUNDUPS_CHANNEL_ID", "UCSNTUXjAgpd4sgWYP0xoJgw")
    studio_url = f"https://studio.youtube.com/channel/{foundups_channel_id}/comments/inbox"
    try:
        driver.get(studio_url)
        await asyncio.sleep(5)
        print(f"  ✅ Navigated to: {driver.current_url[:60]}...")
    except Exception as e:
        print(f"  ❌ Navigation failed: {e}")
        return

    # Step 5: Count comment threads
    print("\n[STEP 5] Counting comment threads...")
    try:
        count = driver.execute_script(
            "return document.querySelectorAll('ytcp-comment-thread').length"
        )
        print(f"  📊 Found {count} comment threads")

        if count == 0:
            # Check for empty state
            empty = driver.execute_script("""
                const emptySelectors = [
                    'ytcp-comments-empty-state',
                    '.empty-state-content',
                    '[data-empty-state]'
                ];
                for (const sel of emptySelectors) {
                    if (document.querySelector(sel)) return true;
                }
                return false;
            """)
            if empty:
                print("  ℹ️ Empty state detected (no comments to process)")
            else:
                print("  ⚠️ No comments found but no empty state - page may still be loading")
    except Exception as e:
        print(f"  ❌ Error counting comments: {e}")

    # Step 6: Check page for errors
    print("\n[STEP 6] Checking for permission errors...")
    try:
        permission_error = driver.execute_script("""
            const t = (document.body && document.body.innerText) || '';
            return t.includes("don't have permission") ||
                   t.includes('Oops, you don\\'t have permission');
        """)
        if permission_error:
            print("  ❌ PERMISSION ERROR DETECTED!")
            print("  → You may not be logged in as FoundUps account")
        else:
            print("  ✅ No permission errors")
    except Exception as e:
        print(f"  ⚠️ Could not check for errors: {e}")

    # Step 7: Test exact Like button selector (#like-button - from DAE)
    print("\n[STEP 7] Testing Like button detection (#like-button)...")
    try:
        like_result = driver.execute_script("""
            const threads = document.querySelectorAll('ytcp-comment-thread');
            if (threads.length === 0) return {threads: 0, found: false};
            const first = threads[0];

            // Exact selector from DAE
            const likeBtn = first.querySelector('#like-button');

            // Also check shadow DOM
            function findInShadow(root, selector) {
                if (!root) return null;
                const el = root.querySelector(selector);
                if (el) return el;
                const children = root.querySelectorAll('*');
                for (let child of children) {
                    if (child.shadowRoot) {
                        const found = findInShadow(child.shadowRoot, selector);
                        if (found) return found;
                    }
                }
                return null;
            }
            const shadowLike = findInShadow(first.shadowRoot || first, '#like-button');

            return {
                threads: threads.length,
                directFound: !!likeBtn,
                shadowFound: !!shadowLike,
                likeId: likeBtn ? likeBtn.id : null,
                likeTag: likeBtn ? likeBtn.tagName : null
            };
        """)
        print(f"  📊 Threads: {like_result.get('threads')}")
        print(f"  📊 Direct #like-button: {like_result.get('directFound')}")
        print(f"  📊 Shadow #like-button: {like_result.get('shadowFound')}")
        if like_result.get('directFound'):
            print(f"  ✅ Like button found (tag: {like_result.get('likeTag')})")
        elif like_result.get('shadowFound'):
            print(f"  ✅ Like button found in Shadow DOM")
        else:
            print("  ❌ #like-button NOT FOUND - selector may need update")
    except Exception as e:
        print(f"  ❌ Error: {e}")

    # Step 8: Test exact Heart button selector (#creator-heart-button - from DAE)
    print("\n[STEP 8] Testing Heart button detection (#creator-heart-button)...")
    try:
        heart_result = driver.execute_script("""
            const threads = document.querySelectorAll('ytcp-comment-thread');
            if (threads.length === 0) return {threads: 0, found: false};
            const first = threads[0];

            // Exact selector from DAE
            const heartBtn = first.querySelector('#creator-heart-button');

            // Also check shadow DOM
            function findInShadow(root, selector) {
                if (!root) return null;
                const el = root.querySelector(selector);
                if (el) return el;
                const children = root.querySelectorAll('*');
                for (let child of children) {
                    if (child.shadowRoot) {
                        const found = findInShadow(child.shadowRoot, selector);
                        if (found) return found;
                    }
                }
                return null;
            }
            const shadowHeart = findInShadow(first.shadowRoot || first, '#creator-heart-button');

            return {
                threads: threads.length,
                directFound: !!heartBtn,
                shadowFound: !!shadowHeart,
                heartId: heartBtn ? heartBtn.id : null,
                heartTag: heartBtn ? heartBtn.tagName : null
            };
        """)
        print(f"  📊 Direct #creator-heart-button: {heart_result.get('directFound')}")
        print(f"  📊 Shadow #creator-heart-button: {heart_result.get('shadowFound')}")
        if heart_result.get('directFound'):
            print(f"  ✅ Heart button found (tag: {heart_result.get('heartTag')})")
        elif heart_result.get('shadowFound'):
            print(f"  ✅ Heart button found in Shadow DOM")
        else:
            print("  ❌ #creator-heart-button NOT FOUND - selector may need update")
    except Exception as e:
        print(f"  ❌ Error: {e}")

    # Summary
    print("\n" + "="*70)
    print(" DIAGNOSTIC SUMMARY")
    print("="*70)
    print(f"  Edge Port 9223: {'✅ OPEN' if True else '❌ CLOSED'}")
    print(f"  Selenium Connection: ✅ OK")
    print(f"  Comment Threads: {count}")
    print("="*70 + "\n")

    # Don't close driver - leave it for inspection
    print("ℹ️ Driver left open for manual inspection")
    print("ℹ️ To test full processing, run:")
    print("   python -m modules.communication.video_comments.skillz.tars_like_heart_reply.run_skill --browser-port 9223 --channel UCSNTUXjAgpd4sgWYP0xoJgw --max-comments 1")


if __name__ == "__main__":
    asyncio.run(diagnose_edge())
