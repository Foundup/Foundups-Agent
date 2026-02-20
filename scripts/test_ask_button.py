#!/usr/bin/env python
"""Test script to find the YouTube Ask button."""
import subprocess
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Use automation profile (Move2Japan/UnDaoDu - logged in)
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
USER_DATA_DIR = r"O:/Foundups-Agent/modules/platform_integration/browser_profiles/youtube_move2japan/chrome"

cmd = [
    CHROME_PATH,
    "--remote-debugging-port=9222",
    f"--user-data-dir={USER_DATA_DIR}",
    "--disable-backgrounding-occluded-windows",
    "--disable-renderer-backgrounding",
    "--disable-background-timer-throttling",
    "https://www.youtube.com/watch?v=GDxfVlf_KB0"
]

print("[INFO] Launching Chrome with debug port 9222 and default profile...")
print(f"[INFO] Profile: {USER_DATA_DIR}")
proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(f"[INFO] Chrome PID: {proc.pid}")

print("[INFO] Waiting 10s for Chrome to start...")
time.sleep(10)

# Connect to Chrome
opts = Options()
opts.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

driver = webdriver.Chrome(options=opts)
print(f"[OK] Connected to Chrome")
print(f"[OK] URL: {driver.current_url}")
print(f"[OK] Title: {driver.title}")

# Wait for dynamic content
time.sleep(3)

# Test: Find Ask button
js_code = """
var flexItems = document.querySelector('#flexible-item-buttons');
var allButtons = [];

if (flexItems) {
    var viewModels = flexItems.querySelectorAll('yt-button-view-model');
    for (var i = 0; i < viewModels.length; i++) {
        var vm = viewModels[i];
        var text = (vm.textContent || '').trim();
        allButtons.push(text.substring(0, 30));
        if (text.toLowerCase() === 'ask') {
            allButtons.push('>>> FOUND ASK BUTTON <<<');
        }
    }
}
return {buttons_in_flex: allButtons, found_flex: flexItems != null};
"""

result = driver.execute_script(js_code)
print(f"[TEST] Result: {result}")

# Don't close browser so user can see it
print("[INFO] Browser left open for inspection")
