"""
Simple browser navigation test
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.infrastructure.foundups_selenium.src.browser_manager import get_browser_manager

# Get browser
print("[1] Getting browser...")
browser_manager = get_browser_manager()
browser = browser_manager.get_browser(
    browser_type='chrome',
    profile_name='youtube_move2japan'
)
print("[2] Browser obtained")

# Navigate
url = "https://studio.youtube.com/channel/UC-LSSlOZwpGIRIYihaz8zCw/comments/inbox"
print(f"[3] Navigating to: {url}")
browser.get(url)
print(f"[4] Navigation complete")
print(f"[5] Current URL: {browser.current_url}")

# Wait
print("[6] Browser window staying open - Press Ctrl+C to exit...")
input("Press Enter to close...")
