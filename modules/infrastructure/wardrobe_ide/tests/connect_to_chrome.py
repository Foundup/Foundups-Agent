"""
Connect Playwright to existing Chrome instance on port 9222
"""
from playwright.sync_api import sync_playwright
import time

print("[BROWSER] Connecting to Chrome on port 9222...")

with sync_playwright() as p:
    # Connect to existing Chrome instance via CDP
    browser = p.chromium.connect_over_cdp("http://localhost:9222")

    # Get existing context or create new one
    contexts = browser.contexts
    if contexts:
        context = contexts[0]
        print(f"[BROWSER] Using existing context with {len(context.pages)} pages")
    else:
        context = browser.new_context()
        print("[BROWSER] Created new context")

    # Get existing page or create new one
    pages = context.pages
    if pages:
        page = pages[0]
        print(f"[BROWSER] Using existing page: {page.url}")
    else:
        page = context.new_page()
        print("[BROWSER] Created new page")

    # Navigate to YouTube Studio
    print("[BROWSER] Navigating to YouTube Studio...")
    page.goto('https://studio.youtube.com/channel/UC-LSSlOZwpGIRIYihaz8zCw/comments/inbox', wait_until='networkidle')

    print("\n[BROWSER] Connected to Chrome!")
    print("[BROWSER] Current URL:", page.url)
    print("[BROWSER] Keeping connection open for 5 minutes...")
    print("[BROWSER] Press Ctrl+C to disconnect")

    try:
        time.sleep(300)  # 5 minutes
    except KeyboardInterrupt:
        print("\n[BROWSER] Disconnecting...")

    # Don't close browser - just disconnect
    browser.close()
    print("[BROWSER] Disconnected (Chrome still running)")
