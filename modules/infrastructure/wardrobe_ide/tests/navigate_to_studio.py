"""
Navigate to YouTube Studio comments page
"""
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(repo_root))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions

print("[NAV] Connecting to Chrome...")
chrome_options = ChromeOptions()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(options=chrome_options)

print(f"[NAV] Current URL: {driver.current_url}")
print("[NAV] Navigating to YouTube Studio...")

driver.get('https://studio.youtube.com/channel/UC-LSSlOZwpGIRIYihaz8zCw/comments/inbox')

print(f"[NAV] Navigated! New URL: {driver.current_url}")
print("[NAV] Ready for recording. Press Enter to disconnect...")

input()
driver.quit()
