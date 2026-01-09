"""
Test Selenium-based like/heart on YouTube Studio comments
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.infrastructure.foundups_selenium.src.browser_manager import get_browser_manager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

print("\n" + "="*60)
print("YOUTUBE STUDIO - Selenium Like/Heart Test")
print("="*60 + "\n")

# Get browser
print("[1] Getting browser...")
browser_manager = get_browser_manager()
browser = browser_manager.get_browser(
    browser_type='chrome',
    profile_name='youtube_move2japan'
)

# Navigate
url = "https://studio.youtube.com/channel/UC-LSSlOZwpGIRIYihaz8zCw/comments/inbox"
print(f"[2] Navigating to: {url}")
browser.get(url)
time.sleep(5)

print(f"[3] Waiting for comments to load...")
time.sleep(3)

# Try to find like button
print(f"[4] Looking for like button...")
try:
    # YouTube Studio uses aria-label for buttons
    # Try different selectors
    possible_selectors = [
        "//button[@aria-label='Like']",
        "//button[@aria-label='Like this comment']",
        "//button[contains(@aria-label, 'Like')]",
        "//button[@title='Like']",
        "//tp-yt-paper-icon-button[@id='like-button']",
    ]

    like_button = None
    for selector in possible_selectors:
        try:
            buttons = browser.find_elements(By.XPATH, selector)
            if buttons:
                print(f"   Found {len(buttons)} buttons with: {selector}")
                like_button = buttons[0]
                break
        except Exception as e:
            continue

    if like_button:
        print(f"[5] Clicking like button...")
        like_button.click()
        print(f"[6] ✓ Like button clicked!")
        time.sleep(2)
    else:
        print(f"[5] Could not find like button")
        print(f"[DEBUG] Let me dump all buttons...")
        all_buttons = browser.find_elements(By.TAG_NAME, "button")
        print(f"   Total buttons found: {len(all_buttons)}")
        for i, btn in enumerate(all_buttons[:10]):  # First 10
            aria = btn.get_attribute('aria-label')
            title = btn.get_attribute('title')
            text = btn.text
            print(f"   Button {i}: aria={aria}, title={title}, text={text}")

except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()

print("\n[WAIT] Browser staying open - Press Ctrl+C to exit...")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n[EXIT] Test terminated")
