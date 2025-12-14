"""
Ultra simple Chrome test - just open Google
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from selenium import webdriver

print("Opening Chrome - you should SEE a window appear...")

# Create a basic Chrome instance (no profile)
driver = webdriver.Chrome()

print("Maximizing window...")
driver.maximize_window()

print("Navigating to Google...")
driver.get("https://www.google.com")

print("\n\n")
print("="*60)
print("DO YOU SEE A CHROME WINDOW WITH GOOGLE?")
print("="*60)
print("\n")

print("Window will stay open for 20 seconds...")
time.sleep(20)

print("Closing...")
driver.quit()
