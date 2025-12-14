from pathlib import Path
import sys
import os

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
os.chdir(REPO_ROOT)

"""Detailed diagnosis of YouTube Studio comments page"""
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
    print(" YOUTUBE STUDIO COMMENTS DIAGNOSIS")
    print("="*80)

    print(f"\n[1] Current URL:")
    print(f"    {driver.current_url}")

    # Try multiple selectors for comments
    selectors_to_try = [
        '[id^="comment-card-"]',
        '.comment-item',
        '.comment-thread',
        'ytcp-comment-thread',
        '[aria-label*="comment"]',
        '#comment-list',
        '.comment-list',
    ]

    print(f"\n[2] Testing various comment selectors...")
    for selector in selectors_to_try:
        count = driver.execute_script(f"""
            const elements = document.querySelectorAll('{selector}');
            return elements.length;
        """)
        print(f"    {selector}: {count} found")

    # Check page content
    print(f"\n[3] Checking page content...")
    page_info = driver.execute_script("""
        return {
            hasCommentText: document.body.innerText.toLowerCase().includes('comment'),
            hasInboxText: document.body.innerText.toLowerCase().includes('inbox'),
            hasFilterText: document.body.innerText.toLowerCase().includes('filter'),
            pageTextLength: document.body.innerText.length,
            scriptTags: document.querySelectorAll('script').length,
            divs: document.querySelectorAll('div').length,
        };
    """)

    for key, value in page_info.items():
        print(f"    {key}: {value}")

    # Look for any elements with "comment" in their ID or class
    print(f"\n[4] Elements with 'comment' in ID/class:")
    comment_elements = driver.execute_script("""
        const all = document.querySelectorAll('*');
        const matches = [];
        all.forEach(el => {
            const id = el.id || '';
            const className = el.className || '';
            if (id.toLowerCase().includes('comment') ||
                className.toString().toLowerCase().includes('comment')) {
                matches.push({
                    tag: el.tagName,
                    id: id,
                    class: className.toString().substring(0, 50),
                    text: el.innerText?.substring(0, 30)
                });
            }
        });
        return matches.slice(0, 10);  // First 10 matches
    """)

    for elem in comment_elements:
        print(f"    {elem['tag']} id='{elem['id']}' class='{elem['class']}'")

    # Check if we need to wait for content to load
    print(f"\n[5] Checking for loading state...")
    loading_info = driver.execute_script("""
        return {
            readyState: document.readyState,
            hasSpinner: document.querySelector('[aria-label*="Loading"]') !== null,
            hasProgress: document.querySelector('progress') !== null,
        };
    """)

    for key, value in loading_info.items():
        print(f"    {key}: {value}")

    print("\n" + "="*80)

except Exception as e:
    print(f"[ERROR] {e}")
