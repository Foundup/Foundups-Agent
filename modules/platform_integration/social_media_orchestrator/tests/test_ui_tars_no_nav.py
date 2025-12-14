"""
Test UI-TARS clicking without navigation - use existing Chrome on 9222
"""
import asyncio
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parent
sys.path.insert(0, str(repo_root))

# Direct UI-TARS Desktop connection via CDP
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def connect_to_existing_chrome():
    """Connect to Chrome on port 9222 without launching new window"""
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

    driver = webdriver.Chrome(options=chrome_options)
    return driver

print("[1] Connecting to existing Chrome on port 9222...")
driver = connect_to_existing_chrome()

print(f"[2] Current URL: {driver.current_url}")
print(f"[3] Page title: {driver.title}")

# Get all open tabs
tabs = driver.window_handles
print(f"[4] Found {len(tabs)} tabs")

# Switch to Studio tab
for i, tab in enumerate(tabs):
    driver.switch_to.window(tab)
    if "studio.youtube.com" in driver.current_url:
        print(f"[5] Switched to Studio tab: {driver.title}")
        break

print("\n[6] Current page ready for UI-TARS actions!")
print(f"    URL: {driver.current_url}")
print("\n[7] Now open UI-TARS Desktop and:")
print("    - Make sure 'Use Local Browser' is checked")
print("    - Click the grounding mode (target icon)")
print("    - Type: 'Click the gray heart icon in the first comment'")
print("    - Press Enter")
print("\n[8] Watch UI-TARS click the heart in THIS Chrome window!")

input("\nPress Enter when done to close...")
driver.quit()
