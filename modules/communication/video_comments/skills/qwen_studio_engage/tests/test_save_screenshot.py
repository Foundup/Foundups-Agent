"""
Save screenshot to file so we can see what's on the page
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.infrastructure.foundups_selenium.src.browser_manager import get_browser_manager

print("\n" + "="*60)
print("SCREENSHOT TEST")
print("="*60 + "\n")

# Get browser
print("[1] Opening browser...")
browser_manager = get_browser_manager()
browser = browser_manager.get_browser(
    browser_type='chrome',
    profile_name='youtube_move2japan'
)

# Maximize
browser.maximize_window()
time.sleep(1)

# Navigate
url = "https://studio.youtube.com/channel/UC-LSSlOZwpGIRIYihaz8zCw/comments/inbox"
print(f"[2] Navigating to: {url}")
browser.get(url)
time.sleep(8)

# Take screenshot
print(f"[3] Taking screenshot...")
screenshot_path = "O:/Foundups-Agent/tests/youtube_studio_screenshot.png"
browser.save_screenshot(screenshot_path)

print(f"\n[SUCCESS] Screenshot saved to:")
print(f"    {screenshot_path}")
print(f"\n    Please open this file and tell me what you see!")
print(f"    Are there comments visible with action bars?")

print("\n[4] Keeping browser open for 20 seconds...")
print("    Check your taskbar for Chrome window!")
time.sleep(20)

print("[DONE]")
