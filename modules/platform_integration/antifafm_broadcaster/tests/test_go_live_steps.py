#!/usr/bin/env python3
"""
Step-by-step test for YouTube Go Live automation.

Run: python modules/platform_integration/antifafm_broadcaster/tests/test_go_live_steps.py

This test will:
1. Connect to the configured antifaFM browser debug port
2. Navigate to YouTube Studio
3. Print what buttons it finds
4. Try to click Create
5. Try to click Go Live
6. Report results at each step
"""

import os
import sys
import time
import socket

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, PROJECT_ROOT)

BROWSER_DEBUG_PORT = int(
    os.getenv(
        "ANTIFAFM_BROWSER_PORT",
        os.getenv("FOUNDUPS_LIVECHAT_CHROME_PORT", "9223"),
    )
)
BROWSER_NAME = "Edge" if BROWSER_DEBUG_PORT == 9223 else "Chrome"
# For antifaFM broadcaster, use ANTIFAFM channel - NOT FOUNDUPS_CHANNEL_ID fallback
ANTIFAFM_CHANNEL_ID = os.getenv(
    "ANTIFAFM_BROADCAST_CHANNEL_ID",
    os.getenv("ANTIFAFM_CHANNEL_ID", "UCVSmg5aOhP4tnQ9KFUg97qA"),
)
STUDIO_URL = f"https://studio.youtube.com/channel/{ANTIFAFM_CHANNEL_ID}/livestreaming/dashboard"


def check_chrome_port():
    """Check if Chrome debug port is open."""
    print(f"\n[STEP 1] Checking {BROWSER_NAME} debug port {BROWSER_DEBUG_PORT}...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('127.0.0.1', BROWSER_DEBUG_PORT))
        sock.close()
        if result == 0:
            print(f"  [OK] Port {BROWSER_DEBUG_PORT} is OPEN")
            return True
        else:
            print(f"  [FAIL] Port {BROWSER_DEBUG_PORT} is CLOSED")
            if BROWSER_NAME == "Edge":
                print(f"  [INFO] Start Edge with: msedge.exe --remote-debugging-port={BROWSER_DEBUG_PORT}")
            else:
                print(f"  [INFO] Start Chrome with: chrome.exe --remote-debugging-port={BROWSER_DEBUG_PORT}")
            return False
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


def connect_to_chrome():
    """Connect to Chrome via Selenium."""
    print(f"\n[STEP 2] Connecting to {BROWSER_NAME}...")
    try:
        from selenium import webdriver

        if BROWSER_NAME == "Edge":
            from selenium.webdriver.edge.options import Options as EdgeOptions

            opts = EdgeOptions()
            opts.add_experimental_option("debuggerAddress", f"127.0.0.1:{BROWSER_DEBUG_PORT}")
            driver = webdriver.Edge(options=opts)
        else:
            from selenium.webdriver.chrome.options import Options

            opts = Options()
            opts.add_experimental_option("debuggerAddress", f"127.0.0.1:{BROWSER_DEBUG_PORT}")
            driver = webdriver.Chrome(options=opts)

        print(f"  [OK] Connected to {BROWSER_NAME}")
        print(f"  [INFO] Current URL: {driver.current_url}")
        print(f"  [INFO] Title: {driver.title}")
        return driver
    except Exception as e:
        print(f"  [FAIL] Could not connect to {BROWSER_NAME}: {e}")
        return None


def navigate_to_studio(driver):
    """Navigate to YouTube Studio livestreaming page."""
    print(f"\n[STEP 3] Navigating to YouTube Studio...")
    print(f"  [INFO] URL: {STUDIO_URL}")
    try:
        driver.get(STUDIO_URL)
        print("  [INFO] Waiting 5 seconds for page load...")
        time.sleep(5)

        print(f"  [OK] Page loaded")
        print(f"  [INFO] Current URL: {driver.current_url}")
        print(f"  [INFO] Title: {driver.title}")
        return True
    except Exception as e:
        print(f"  [FAIL] Navigation failed: {e}")
        return False


def scan_for_buttons(driver):
    """Scan page for all visible buttons and print them."""
    print(f"\n[STEP 4] Scanning for buttons on page...")
    try:
        result = driver.execute_script("""
            const buttons = [];

            // Scan all button-like elements
            document.querySelectorAll('button, ytcp-button, [role="button"], ytcp-icon-button').forEach(el => {
                if (el.offsetParent !== null) {  // Only visible elements
                    const text = (el.textContent || '').trim().substring(0, 50);
                    const ariaLabel = el.getAttribute('aria-label') || '';
                    const tagName = el.tagName.toLowerCase();
                    const icon = el.getAttribute('icon') || '';

                    if (text || ariaLabel || icon) {
                        buttons.push({
                            tag: tagName,
                            text: text,
                            ariaLabel: ariaLabel,
                            icon: icon
                        });
                    }
                }
            });

            return buttons;
        """)

        print(f"  [OK] Found {len(result)} visible buttons:")
        for i, btn in enumerate(result[:20]):  # Show first 20
            text = btn.get('text', '').replace('\n', ' ')[:30]
            label = btn.get('ariaLabel', '')[:30]
            icon = btn.get('icon', '')
            print(f"    {i+1}. [{btn['tag']}] text='{text}' aria='{label}' icon='{icon}'")

        if len(result) > 20:
            print(f"    ... and {len(result) - 20} more")

        return result
    except Exception as e:
        print(f"  [FAIL] Scan failed: {e}")
        return []


def scan_for_menu_items(driver):
    """Scan for menu items (after Create is clicked)."""
    print(f"\n[STEP 5b] Scanning for menu items...")
    try:
        result = driver.execute_script("""
            const items = [];

            document.querySelectorAll('[role="menuitem"], [role="option"], tp-yt-paper-item, ytcp-text-menu a').forEach(el => {
                if (el.offsetParent !== null) {
                    const text = (el.textContent || '').trim().substring(0, 50);
                    if (text) {
                        items.push({
                            tag: el.tagName.toLowerCase(),
                            text: text,
                            href: el.getAttribute('href') || ''
                        });
                    }
                }
            });

            return items;
        """)

        print(f"  [OK] Found {len(result)} menu items:")
        for i, item in enumerate(result[:15]):
            text = item.get('text', '').replace('\n', ' ')[:40]
            print(f"    {i+1}. [{item['tag']}] '{text}'")

        return result
    except Exception as e:
        print(f"  [FAIL] Scan failed: {e}")
        return []


def verify_dropdown_appeared(driver, timeout=5):
    """Poll DOM to verify dropdown menu appeared after Create click."""
    import time
    start = time.time()
    poll_interval = 0.3  # Check every 300ms

    while (time.time() - start) < timeout:
        try:
            result = driver.execute_script("""
                // Look for dropdown menu items
                const menuItems = document.querySelectorAll(
                    '[role="menuitem"], [role="option"], tp-yt-paper-item, ' +
                    'ytcp-text-menu a, ytd-menu-service-item-renderer'
                );

                // Filter to only visible items
                const visibleItems = [];
                menuItems.forEach(item => {
                    if (item.offsetParent !== null) {
                        const text = (item.textContent || '').trim();
                        if (text && text.length < 50) {
                            visibleItems.push(text.substring(0, 30));
                        }
                    }
                });

                return {
                    visible: visibleItems.length > 0,
                    item_count: visibleItems.length,
                    items: visibleItems.slice(0, 5)
                };
            """)

            if result.get('visible'):
                elapsed = time.time() - start
                print(f"  [INFO] Dropdown detected in {elapsed:.1f}s: {result.get('items', [])}")
                return True

        except Exception as e:
            print(f"  [WARN] Poll error: {e}")

        time.sleep(poll_interval)

    # Timeout
    elapsed = time.time() - start
    print(f"  [WARN] Dropdown not detected after {elapsed:.1f}s")
    return False


def click_create_button(driver):
    """Try to click the CREATE button in YouTube Studio header."""
    print(f"\n[STEP 5] Clicking CREATE button (header)...")
    try:
        result = driver.execute_script("""
            // YouTube Studio CREATE button is usually in the header
            // It's a ytcp-button with id="create-icon" or similar

            // Method 1: Look for #create-icon (most specific)
            const createIcon = document.querySelector('#create-icon, ytcp-button#create-icon');
            if (createIcon && createIcon.offsetParent !== null) {
                createIcon.click();
                return {clicked: true, method: '#create-icon', element: createIcon.tagName};
            }

            // Method 2: Look for button with "Create" aria-label
            const createLabels = document.querySelectorAll('[aria-label="Create"], [aria-label="Create a video or post"]');
            for (const btn of createLabels) {
                if (btn.offsetParent !== null) {
                    btn.click();
                    return {clicked: true, method: 'aria-label', element: btn.tagName};
                }
            }

            // Method 3: Look for ytcp-button-shape with create
            const ytcpBtns = document.querySelectorAll('ytcp-button, ytcp-button-shape');
            for (const btn of ytcpBtns) {
                const text = (btn.textContent || '').toLowerCase().trim();
                const id = btn.id || '';
                if (text === 'create' || id.includes('create')) {
                    if (btn.offsetParent !== null) {
                        btn.click();
                        return {clicked: true, method: 'ytcp-button', element: btn.tagName, id: id};
                    }
                }
            }

            // Method 4: Look in header area specifically
            const header = document.querySelector('ytcp-masthead, #masthead, header');
            if (header) {
                const headerBtns = header.querySelectorAll('button, ytcp-button, [role="button"]');
                for (const btn of headerBtns) {
                    const text = (btn.textContent || '').toLowerCase().trim();
                    if (text === 'create' || text.includes('create')) {
                        if (btn.offsetParent !== null) {
                            btn.click();
                            return {clicked: true, method: 'header-scan', element: btn.tagName};
                        }
                    }
                }
            }

            // Debug: List all ytcp-buttons for diagnosis
            const allYtcp = [];
            document.querySelectorAll('ytcp-button, ytcp-icon-button').forEach(el => {
                allYtcp.push({
                    tag: el.tagName,
                    id: el.id,
                    text: (el.textContent || '').trim().substring(0, 30),
                    aria: el.getAttribute('aria-label') || ''
                });
            });

            return {clicked: false, reason: 'Create button not found', ytcp_buttons: allYtcp.slice(0, 10)};
        """)

        if result.get('clicked'):
            print(f"  [OK] Clicked via {result.get('method')} ({result.get('element')})")
            print("  [INFO] Verifying dropdown appeared (polling DOM)...")

            # Poll for dropdown to appear instead of fixed wait
            dropdown_verified = verify_dropdown_appeared(driver, timeout=5)

            if dropdown_verified:
                print(f"  [OK] Dropdown verified!")
            else:
                print(f"  [WARN] Dropdown not detected, continuing anyway...")

            return True
        else:
            print(f"  [FAIL] {result.get('reason')}")
            if result.get('ytcp_buttons'):
                print(f"  [DEBUG] ytcp-buttons found:")
                for btn in result.get('ytcp_buttons', []):
                    print(f"    - id='{btn.get('id')}' text='{btn.get('text')}' aria='{btn.get('aria')}'")
            return False

    except Exception as e:
        print(f"  [FAIL] Click failed: {e}")
        return False


def click_go_live_in_dropdown(driver):
    """Try to click Go Live in the dropdown."""
    print(f"\n[STEP 6] Clicking GO LIVE in dropdown...")
    try:
        result = driver.execute_script("""
            // Look for "Go live" in menu items
            const menuItems = document.querySelectorAll('[role="menuitem"], [role="option"], tp-yt-paper-item, a');
            for (const item of menuItems) {
                const text = (item.textContent || '').toLowerCase().trim();
                if (text.includes('go live')) {
                    if (item.offsetParent !== null) {
                        console.log('Found Go Live:', item);
                        item.click();
                        return {clicked: true, text: item.textContent.trim()};
                    }
                }
            }

            // Also try buttons
            const buttons = document.querySelectorAll('button, ytcp-button');
            for (const btn of buttons) {
                const text = (btn.textContent || '').toLowerCase().trim();
                const label = (btn.getAttribute('aria-label') || '').toLowerCase();
                if (text.includes('go live') || label.includes('go live')) {
                    if (btn.offsetParent !== null) {
                        console.log('Found Go Live button:', btn);
                        btn.click();
                        return {clicked: true, text: btn.textContent.trim()};
                    }
                }
            }

            return {clicked: false};
        """)

        if result.get('clicked'):
            print(f"  [OK] Clicked: '{result.get('text')}'")
            print("  [INFO] Waiting 3 seconds for stream page...")
            time.sleep(3)
            return True
        else:
            print(f"  [FAIL] Go Live button not found in dropdown")
            return False

    except Exception as e:
        print(f"  [FAIL] Click failed: {e}")
        return False


def check_stream_status(driver):
    """Check if we're on a live stream page."""
    print(f"\n[STEP 7] Checking stream status...")
    try:
        result = driver.execute_script("""
            const bodyText = document.body.innerText.toLowerCase();
            return {
                url: window.location.href,
                title: document.title,
                has_connect_encoder: bodyText.includes('connect your encoder'),
                has_youre_live: bodyText.includes("you're live") || bodyText.includes("you are live"),
                has_stream_key: bodyText.includes('stream key'),
                has_go_live_btn: !!document.querySelector('button[aria-label*="Go live"], ytcp-button[aria-label*="Go live"]'),
                has_end_stream: !!document.querySelector('button[aria-label*="End stream"]')
            };
        """)

        print(f"  [INFO] URL: {result.get('url')}")
        print(f"  [INFO] Title: {result.get('title')}")
        print(f"  [INFO] 'Connect your encoder' visible: {result.get('has_connect_encoder')}")
        print(f"  [INFO] 'You're live' visible: {result.get('has_youre_live')}")
        print(f"  [INFO] Stream key visible: {result.get('has_stream_key')}")
        print(f"  [INFO] 'Go Live' button visible: {result.get('has_go_live_btn')}")
        print(f"  [INFO] 'End stream' button visible: {result.get('has_end_stream')}")

        if result.get('has_connect_encoder') or result.get('has_stream_key'):
            print(f"  [OK] Stream page ready - waiting for encoder (FFmpeg)")
            return "ready_for_encoder"
        elif result.get('has_youre_live') or result.get('has_end_stream'):
            print(f"  [OK] Stream is LIVE!")
            return "live"
        elif result.get('has_go_live_btn'):
            print(f"  [INFO] Go Live button still visible - need to click it")
            return "needs_go_live"
        else:
            print(f"  [INFO] Unknown state")
            return "unknown"

    except Exception as e:
        print(f"  [FAIL] Status check failed: {e}")
        return "error"


def take_screenshot(driver, name="debug"):
    """Take a screenshot for debugging."""
    try:
        screenshot_path = os.path.join(PROJECT_ROOT, "logs", f"screenshot_{name}_{int(time.time())}.png")
        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
        driver.save_screenshot(screenshot_path)
        print(f"  [INFO] Screenshot saved: {screenshot_path}")
        return screenshot_path
    except Exception as e:
        print(f"  [WARN] Screenshot failed: {e}")
        return None


def test_edit_stream(driver):
    """Test editing stream settings in the studio."""
    print(f"\n[STEP 6b] Testing stream edit functionality...")

    # First scan for edit button
    try:
        result = driver.execute_script("""
            const editBtns = [];

            // Look for edit buttons
            document.querySelectorAll(
                'button[aria-label*="Edit"], ytcp-button[aria-label*="Edit"], ' +
                '[aria-label*="edit"], button[id*="edit"], ' +
                'ytcp-icon-button, tp-yt-paper-icon-button'
            ).forEach(btn => {
                if (btn.offsetParent !== null) {
                    editBtns.push({
                        tag: btn.tagName.toLowerCase(),
                        text: (btn.textContent || '').trim().substring(0, 30),
                        aria: btn.getAttribute('aria-label') || '',
                        icon: btn.getAttribute('icon') || ''
                    });
                }
            });

            // Also look for title/description fields that might be visible
            const inputs = [];
            document.querySelectorAll('input, textarea').forEach(el => {
                if (el.offsetParent !== null) {
                    inputs.push({
                        tag: el.tagName.toLowerCase(),
                        type: el.type || 'textarea',
                        placeholder: el.placeholder || '',
                        aria: el.getAttribute('aria-label') || '',
                        value: (el.value || '').substring(0, 30)
                    });
                }
            });

            return {
                edit_buttons: editBtns.slice(0, 10),
                input_fields: inputs.slice(0, 10),
                page_title: document.title
            };
        """)

        print(f"  [INFO] Page: {result.get('page_title', 'N/A')}")

        if result.get('edit_buttons'):
            print(f"  [INFO] Found {len(result['edit_buttons'])} potential edit buttons:")
            for btn in result['edit_buttons'][:5]:
                print(f"    - [{btn['tag']}] text='{btn['text']}' aria='{btn['aria']}' icon='{btn['icon']}'")
        else:
            print(f"  [INFO] No edit buttons found")

        if result.get('input_fields'):
            print(f"  [INFO] Found {len(result['input_fields'])} input fields:")
            for inp in result['input_fields'][:5]:
                print(f"    - [{inp['tag']}] type='{inp['type']}' aria='{inp['aria']}' placeholder='{inp['placeholder']}'")
        else:
            print(f"  [INFO] No input fields visible (edit dialog not open)")

        # Try clicking edit button
        click_result = driver.execute_script("""
            // Try to click any edit button
            const editBtns = document.querySelectorAll(
                'button[aria-label*="Edit"], ytcp-button[aria-label*="Edit"], ' +
                'ytcp-icon-button[icon="edit"], [aria-label*="edit"]'
            );

            for (const btn of editBtns) {
                if (btn.offsetParent !== null) {
                    btn.click();
                    return {clicked: true, aria: btn.getAttribute('aria-label') || 'N/A'};
                }
            }

            return {clicked: false};
        """)

        if click_result.get('clicked'):
            print(f"  [OK] Clicked edit button: {click_result.get('aria')}")
            print("  [INFO] Waiting 2 seconds for edit dialog...")
            time.sleep(2)
            take_screenshot(driver, "edit_dialog")

            # Now scan for input fields
            fields_result = driver.execute_script("""
                const inputs = [];
                document.querySelectorAll('input, textarea, [contenteditable="true"]').forEach(el => {
                    if (el.offsetParent !== null) {
                        inputs.push({
                            tag: el.tagName.toLowerCase(),
                            type: el.type || 'textarea',
                            placeholder: el.placeholder || '',
                            aria: el.getAttribute('aria-label') || '',
                            value: (el.value || el.textContent || '').substring(0, 50)
                        });
                    }
                });
                return inputs;
            """)

            if fields_result:
                print(f"  [OK] Edit dialog opened - {len(fields_result)} fields found:")
                for inp in fields_result[:8]:
                    print(f"    - [{inp['tag']}] aria='{inp['aria']}' value='{inp['value']}'")
            else:
                print(f"  [WARN] No input fields found in edit dialog")
        else:
            print(f"  [INFO] No edit button clicked - may need to look for different selector")

    except Exception as e:
        print(f"  [FAIL] Edit test failed: {e}")


def main():
    print("=" * 60)
    print("YouTube Go Live - Step-by-Step Test")
    print("=" * 60)
    print(f"Target URL: {STUDIO_URL}")
    print(f"{BROWSER_NAME} debug port: {BROWSER_DEBUG_PORT}")
    print("=" * 60)

    # Step 1: Check Chrome port
    if not check_chrome_port():
        print(f"\n[ABORT] {BROWSER_NAME} not running on debug port. Start it first!")
        return False

    # Step 2: Connect to Chrome
    driver = connect_to_chrome()
    if not driver:
        print(f"\n[ABORT] Could not connect to {BROWSER_NAME}")
        return False

    # Step 3: Navigate to Studio
    if not navigate_to_studio(driver):
        print("\n[ABORT] Could not navigate to YouTube Studio")
        return False

    # Step 4: Scan for buttons
    buttons = scan_for_buttons(driver)

    # Take screenshot before clicking
    take_screenshot(driver, "before_click")

    # Step 5: Click Create button in header
    if click_create_button(driver):
        # Take screenshot after Create clicked
        take_screenshot(driver, "after_create")

        # Scan for menu items in dropdown
        print("\n[STEP 5b] Scanning menu items after Create click...")
        scan_for_menu_items(driver)

        # Step 6: Click Go Live in dropdown
        if click_go_live_in_dropdown(driver):
            # Take screenshot after Go Live
            take_screenshot(driver, "after_go_live")
            print("  [OK] Stream studio should be opening...")
            print("  [INFO] Waiting 15 seconds for studio to fully load...")
            time.sleep(15)  # Wait for studio to fully load

            # Step 6b: Try to edit stream settings
            take_screenshot(driver, "studio_loaded")
            test_edit_stream(driver)
    else:
        print("\n[STEP 5c] Create button not found - check screenshots")

    # Step 7: Check status
    status = check_stream_status(driver)

    # Final screenshot
    take_screenshot(driver, "final")

    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print(f"Final status: {status}")

    if status == "ready_for_encoder":
        print("\n[SUCCESS] Stream page is ready!")
        print("Now run FFmpeg to connect to the stream.")
        return True
    elif status == "live":
        print("\n[SUCCESS] Stream is already live!")
        return True
    else:
        print("\n[INCOMPLETE] Stream not fully set up")
        print("Check the screenshots in logs/ folder for debugging")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
