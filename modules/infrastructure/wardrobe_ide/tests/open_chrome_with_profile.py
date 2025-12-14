"""
Open Chrome with YouTube profile for manual login/verification
"""
import sys
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(repo_root))

from modules.infrastructure.foundups_selenium.src.browser_manager import get_browser_manager

print("[BROWSER] Opening Chrome with YouTube profile...")
print("[BROWSER] Profile: youtube_move2japan")

manager = get_browser_manager()
driver = manager.get_browser("chrome", "youtube_move2japan")

print("\n[BROWSER] Chrome opened!")
print("[BROWSER] Navigating to YouTube Studio...")

driver.get('https://studio.youtube.com/channel/UC-LSSlOZwpGIRIYihaz8zCw/comments/inbox')

print("\n[BROWSER] Browser is now open at YouTube Studio")
print("[BROWSER] Please log in if needed")
print("[BROWSER] Press Enter when ready to close browser...")

input()

print("\n[BROWSER] Closing browser...")
manager.close_browser()
print("[BROWSER] Browser closed")
