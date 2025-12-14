"""
Launch Playwright browser for manual login before recording
"""
from playwright.sync_api import sync_playwright
import time

print("[BROWSER] Launching Playwright browser for login...")
print("[BROWSER] Navigate to YouTube Studio and log in")
print("[BROWSER] Browser will stay open for 5 minutes")
print("[BROWSER] Press Ctrl+C to close early")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, channel="chrome")
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
    page = context.new_page()

    # Navigate to YouTube Studio
    page.goto('https://studio.youtube.com/channel/UC-LSSlOZwpGIRIYihaz8zCw/comments/inbox')

    print("\n[BROWSER] Browser opened!")
    print("[BROWSER] Please log in and navigate to the page you want to record")
    print("[BROWSER] Keeping browser open for 5 minutes...")

    try:
        time.sleep(300)  # 5 minutes
    except KeyboardInterrupt:
        print("\n[BROWSER] Closing browser...")

    browser.close()
    print("[BROWSER] Browser closed")
