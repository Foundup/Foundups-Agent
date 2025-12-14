"""
Map out the actual DOM structure to find buttons properly
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.infrastructure.foundups_selenium.src.browser_manager import get_browser_manager
from selenium.webdriver.common.by import By

print("\n" + "="*60)
print("MAP DOM STRUCTURE")
print("="*60 + "\n")

browser_manager = get_browser_manager()
browser = browser_manager.get_browser(
    browser_type='chrome',
    profile_name='youtube_move2japan'
)

browser.maximize_window()
time.sleep(1)

url = "https://studio.youtube.com/channel/UC-LSSlOZwpGIRIYihaz8zCw/comments/inbox"
print(f"[1] Navigating to: {url}")
browser.get(url)
time.sleep(8)

print(f"\n[2] Mapping comment structure...")

# Find the first comment container
try:
    # YouTube Studio comments are in ytd-comment-renderer elements
    comment_containers = browser.find_elements(By.TAG_NAME, "ytd-comment-renderer")

    if not comment_containers:
        print("[ERROR] No comment containers found")
        print("Looking for alternative containers...")

        # Try alternative selectors
        comment_containers = browser.find_elements(By.CSS_SELECTOR, "[id*='comment']")
        print(f"Found {len(comment_containers)} elements with 'comment' in ID")

    if comment_containers:
        first_comment = comment_containers[0]
        print(f"[3] Found first comment container")

        # Find all buttons within this comment
        buttons = first_comment.find_elements(By.TAG_NAME, "button")
        print(f"    Found {len(buttons)} buttons in first comment")

        print(f"\n[4] Button details:")
        for i, btn in enumerate(buttons):
            aria = btn.get_attribute('aria-label') or ''
            btn_id = btn.get_attribute('id') or ''
            btn_class = btn.get_attribute('class') or ''
            text = btn.text or ''
            inner_html = btn.get_attribute('innerHTML')[:100] if btn.get_attribute('innerHTML') else ''

            print(f"\n  Button {i}:")
            print(f"    aria-label: {aria}")
            print(f"    id: {btn_id}")
            print(f"    class: {btn_class[:60]}...")
            print(f"    text: {text}")
            print(f"    innerHTML: {inner_html}...")

        # Now try to find the action buttons specifically
        print(f"\n[5] Looking for action buttons container...")

        # Try to find the action buttons toolbar
        toolbars = first_comment.find_elements(By.CSS_SELECTOR, "[id='toolbar'], [class*='action'], [class*='button']")
        print(f"    Found {len(toolbars)} potential action containers")

        for i, toolbar in enumerate(toolbars[:3]):
            print(f"\n  Container {i}:")
            inner_buttons = toolbar.find_elements(By.TAG_NAME, "button")
            print(f"    Contains {len(inner_buttons)} buttons")

            for j, btn in enumerate(inner_buttons):
                aria = btn.get_attribute('aria-label') or 'none'
                print(f"      Button {j}: {aria}")

        # Try clicking the heart button if we can identify it
        print(f"\n[6] Attempting to find and highlight heart button...")

        # Strategy: find yt-icon-button elements (YouTube's custom buttons)
        icon_buttons = first_comment.find_elements(By.TAG_NAME, "yt-icon-button")
        print(f"    Found {len(icon_buttons)} yt-icon-button elements")

        for i, icon_btn in enumerate(icon_buttons):
            # Get the button inside
            inner_btn = icon_btn.find_element(By.TAG_NAME, "button")
            aria = inner_btn.get_attribute('aria-label') or ''
            btn_id = inner_btn.get_attribute('id') or ''

            print(f"    Icon button {i}: aria='{aria}', id='{btn_id}'")

            # Highlight this button so user can see
            browser.execute_script(f"arguments[0].style.border='3px solid {['red', 'blue', 'green', 'orange', 'purple'][i % 5]}'", inner_btn)

        print(f"\n[7] Buttons highlighted with colored borders!")
        print(f"    Check the browser - each button should have a different color")
        print(f"    Tell me which color is on the HEART button")

    else:
        print("[ERROR] Could not find comment containers")

except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("WINDOW STAYS OPEN")
print("Check which colored border is on the HEART button")
print("Press Ctrl+C to exit")
print("="*60 + "\n")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n[EXIT]")
