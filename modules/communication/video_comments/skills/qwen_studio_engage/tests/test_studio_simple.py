"""
Simple YouTube Studio navigation test - browser stays open
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.infrastructure.foundups_selenium.src.browser_manager import get_browser_manager

print("\n" + "="*60)
print("YOUTUBE STUDIO - Simple Navigation Test")
print("="*60 + "\n")

# Get browser
print("[1] Getting browser with youtube_move2japan profile...")
browser_manager = get_browser_manager()
browser = browser_manager.get_browser(
    browser_type='chrome',
    profile_name='youtube_move2japan'
)
print("[2] Browser obtained")

# Navigate to Studio inbox
url = "https://studio.youtube.com/channel/UC-LSSlOZwpGIRIYihaz8zCw/comments/inbox"
print(f"[3] Navigating to: {url}")
browser.get(url)
print(f"[4] Navigation complete")
print(f"[5] Current URL: {browser.current_url}")

# Keep browser open indefinitely
print("\n" + "="*60)
print("[WAIT] Browser window is now open at Studio inbox")
print("[WAIT] You can manually interact with it")
print("[WAIT] Press Ctrl+C in terminal to exit and close browser")
print("="*60 + "\n")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n[EXIT] Test terminated by user")
    print("[EXIT] Browser will close now...")
