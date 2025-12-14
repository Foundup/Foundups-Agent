from pathlib import Path
import sys
import os

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
os.chdir(REPO_ROOT)

"""Check current page status and comment count"""
import sys
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

repo_root = REPO_ROOT

# Connect to existing Chrome
chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

try:
    driver = webdriver.Chrome(options=chrome_options)

    print("\n" + "="*80)
    print(" PAGE STATUS CHECK")
    print("="*80)

    print(f"\n[Current URL]")
    print(f"  {driver.current_url}")

    print(f"\n[Page Title]")
    print(f"  {driver.title}")

    print(f"\n[Window Size]")
    print(f"  {driver.get_window_size()}")

    # Check for comment cards
    comment_info = driver.execute_script("""
        const cards = document.querySelectorAll('[id^="comment-card-"]');
        const comments = document.querySelectorAll('.comment-text');
        const toolbar = document.querySelectorAll('.comment-toolbar');

        return {
            comment_cards: cards.length,
            comment_texts: comments.length,
            toolbars: toolbar.length,
            page_state: document.readyState,
            body_text: document.body.innerText.substring(0, 500)
        };
    """)

    print(f"\n[Comment Elements]")
    print(f"  Comment cards: {comment_info['comment_cards']}")
    print(f"  Comment texts: {comment_info['comment_texts']}")
    print(f"  Toolbars: {comment_info['toolbars']}")
    print(f"  Page state: {comment_info['page_state']}")

    print(f"\n[Page Content Preview]")
    print(f"  {comment_info['body_text'][:200]}...")

    # Check if we're on the right page
    if "studio.youtube.com" in driver.current_url:
        if "comments/inbox" in driver.current_url:
            print(f"\n[✓] On YouTube Studio Comments Inbox")
        else:
            print(f"\n[!] On YouTube Studio but NOT on comments inbox")
            print(f"    Expected: .../comments/inbox")
    else:
        print(f"\n[!] NOT on YouTube Studio")

    print("\n" + "="*80)

except Exception as e:
    print(f"[ERROR] Cannot connect to Chrome: {e}")
