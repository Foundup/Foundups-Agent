"""
Take screenshot of current page state
"""
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(repo_root))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(options=chrome_options)

screenshot_path = Path(__file__).parent / "current_page_state.png"
driver.save_screenshot(str(screenshot_path))

print(f"\nScreenshot saved to: {screenshot_path}")
print("Check if Like button is highlighted/blue on first comment")
