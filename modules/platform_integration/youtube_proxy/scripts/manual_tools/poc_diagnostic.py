"""
Diagnostic Script for YouTube POC
Checks:
1. Connection to Chrome @ 9222
2. Current URL
3. Visibility of key elements (Reply buttons, Like buttons)
4. Vision API basic health
"""
from pathlib import Path
import sys
import os

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
os.chdir(REPO_ROOT)

import sys
import os
import asyncio
import logging

sys.path.append('.')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Diagnostic")

try:
    from modules.infrastructure.foundups_selenium.src.foundups_driver import FoundUpsDriver
    from modules.platform_integration.social_media_orchestrator.src.gemini_vision_analyzer import GeminiVisionAnalyzer
except ImportError as e:
    logger.error(f"Import failed: {e}")
    sys.exit(1)

def check_browser():
    print("\n--- CHECKING BROWSER ---")
    try:
        driver = FoundUpsDriver(port=9222)
        print(f"Connected! Current URL: {driver.current_url}")
        if "studio.youtube.com" not in driver.current_url:
            print("[WARN] Not on YouTube Studio!")
        return driver
    except Exception as e:
        print(f"[FAIL] Could not connect to browser: {e}")
        return None

def check_elements(driver):
    print("\n--- CHECKING ELEMENTS (DOM) ---")
    from selenium.webdriver.common.by import By
    
    # Try generic button search
    buttons = driver.find_elements(By.TAG_NAME, "button")
    print(f"Total buttons found: {len(buttons)}")
    
    # Try finding specific interactables
    reply_btns = [b for b in buttons if "reply" in (b.get_attribute("aria-label") or "").lower() or "reply" in b.text.lower()]
    print(f"Likely 'Reply' buttons: {len(reply_btns)}")
    
    thumbs_up = driver.find_elements(By.XPATH, "//*[@id='like-button']") # Generic guess
    print(f"Generic 'like-button' IDs found: {len(thumbs_up)}")

def check_vision(driver):
    print("\n--- CHECKING VISION ---")
    try:
        analyzer = GeminiVisionAnalyzer()
        if not analyzer.model:
            print("[FAIL] Gemini Vision not initialized (Key missing?)")
            return

        print("Capturing screenshot...")
        png = driver.get_screenshot_as_png()
        print(f"Screenshot captured ({len(png)} bytes)")
        
        print("Sending to Gemini... (Timeout 30s)")
        # Simple test
        res = analyzer.find_element_by_description(png, "the YouTube Studio logo")
        print(f"Vision Result: {res}")
        
    except Exception as e:
        print(f"[FAIL] Vision check failed: {e}")

if __name__ == "__main__":
    driver = check_browser()
    if driver:
        check_elements(driver)
        check_vision(driver)
    
    print("\n--- DIAGNOSTIC COMPLETE ---")
