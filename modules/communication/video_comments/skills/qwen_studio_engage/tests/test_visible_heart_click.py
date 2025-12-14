"""
VISIBLE TEST - YouTube Studio Heart Click
You will SEE this happening on your screen!
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
print("VISIBLE TEST - YouTube Studio Heart Click")
print("="*60 + "\n")

print("[1] Opening browser window (you should SEE this)...")
browser_manager = get_browser_manager()
browser = browser_manager.get_browser(
    browser_type='chrome',
    profile_name='youtube_move2japan'
)

# MAKE WINDOW VISIBLE
print("[1.5] Maximizing window and bringing to front...")
browser.maximize_window()
time.sleep(1)

# Execute JavaScript to focus the window
browser.execute_script("window.focus();")

print("[2] Navigating to YouTube Studio inbox...")
url = "https://studio.youtube.com/channel/UC-LSSlOZwpGIRIYihaz8zCw/comments/inbox"
browser.get(url)

print("[3] Waiting 8 seconds for page to load (WATCH THE BROWSER)...")
time.sleep(8)

print(f"[4] Current URL: {browser.current_url[:80]}...")

print("\n[5] Looking for heart button...")
try:
    # YouTube Studio uses tp-yt-paper-icon-button
    # The heart button is the creator heart (5th button in action bar)

    # Strategy: Find all icon buttons and look for the heart
    wait = WebDriverWait(browser, 10)

    # Wait for comments to load
    print("    Waiting for comments to appear...")
    time.sleep(3)

    # Find all icon buttons
    buttons = browser.find_elements(By.TAG_NAME, "button")
    print(f"    Found {len(buttons)} total buttons on page")

    # Look for aria-label or tooltip that indicates heart/like
    heart_button = None
    like_button = None

    # First pass: look for action bar buttons
    print(f"    Looking for action bar buttons (after 'Reply' and '0 replies')...")
    reply_index = None
    for i, btn in enumerate(buttons):
        aria_label = btn.get_attribute('aria-label') or ''

        if 'Reply' == aria_label:
            reply_index = i
            print(f"    Found Reply button at index {i}")
            break

    # Action bar buttons come after Reply button
    if reply_index is not None:
        # Print ALL buttons after Reply to understand the structure
        print(f"    Checking buttons after Reply...")
        for offset in range(1, 10):
            idx = reply_index + offset
            if idx < len(buttons):
                btn = buttons[idx]
                aria = btn.get_attribute('aria-label') or ''
                btn_id = btn.get_attribute('id') or ''
                print(f"    Button +{offset}: aria='{aria}', id='{btn_id}'")

        # Based on your screenshots: Reply | 0 replies | Like | Dislike | Heart | Menu
        # Try positions 4, 5, 6 for the heart
        print(f"\n    Trying button at position +5 as heart button...")
        idx = reply_index + 5
        if idx < len(buttons):
            heart_button = buttons[idx]
            print(f"    Selected button: aria='{heart_button.get_attribute('aria-label')}'")
        else:
            print(f"    Position +5 out of range, trying +4...")
            idx = reply_index + 4
            if idx < len(buttons):
                heart_button = buttons[idx]

    if heart_button:
        print(f"\n[6] Found heart button! Scrolling into view...")
        browser.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", heart_button)
        time.sleep(2)

        print(f"[7] Clicking heart button NOW (WATCH THE SCREEN)...")
        heart_button.click()

        print(f"[8] CLICKED! You should see a RED HEART appear!")
        time.sleep(3)

        print(f"\n[SUCCESS] Heart button clicked successfully!")
    else:
        print(f"\n[WARN] Could not find heart button by aria-label")
        print(f"[DEBUG] Showing first 10 buttons...")
        for i, btn in enumerate(buttons[:10]):
            aria = btn.get_attribute('aria-label') or 'none'
            print(f"    {i}: {aria[:60]}")

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("Browser window will stay open for 30 seconds")
print("WATCH FOR THE RED HEART")
print("="*60 + "\n")

time.sleep(30)

print("[DONE] Test complete - closing browser...")
