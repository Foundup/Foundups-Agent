"""
Test visibility filter using natural Selenium clicks (not forced JS).

The issue: Force-opening the dialog bypasses YouTube's event handlers.
Solution: Use proper Selenium clicks to let YouTube's JS handle the dialog opening.

Key insight: The visibility dialog needs to be opened through YouTube's native
click handlers, not by forcing display:block via JavaScript.
"""

import time
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

EDGE_PORT = 9223
CHANNEL_ID = "UC-LSSlOZwpGIRIYihaz8zCw"


def connect_edge():
    """Connect to existing Edge debug session."""
    print(f"[INFO] Connecting to Edge on port {EDGE_PORT}...")
    options = Options()
    options.add_experimental_option("debuggerAddress", f"127.0.0.1:{EDGE_PORT}")
    driver = webdriver.Edge(options=options)
    print(f"[INFO] Connected!")
    return driver


def navigate_to_shorts(driver):
    """Navigate to the Shorts page."""
    url = f"https://studio.youtube.com/channel/{CHANNEL_ID}/videos/short"
    print(f"[STEP] Navigating to Shorts page...")
    driver.get(url)
    time.sleep(3)
    print(f"[OK] Page loaded")


def step1_click_filter(driver):
    """Click Filter input using Selenium element click."""
    print("\n[STEP 1] Clicking Filter input...")

    try:
        filter_input = driver.find_element(By.CSS_SELECTOR, "input[placeholder='Filter']")
        filter_input.click()
        time.sleep(1.5)
        print("[OK] Filter dropdown opened")
        return True
    except Exception as e:
        print(f"[FAIL] {e}")
        return False


def step2_click_visibility_with_wait(driver):
    """Click Visibility item and wait for dialog to open naturally."""
    print("\n[STEP 2] Clicking Visibility option...")

    # Find the Visibility item using test-id
    try:
        visibility_item = driver.find_element(By.CSS_SELECTOR, '[test-id*="VISIBILITY"]')
        print(f"  Found Visibility item at location: {visibility_item.location}")

        # Use ActionChains for a real click
        actions = ActionChains(driver)
        actions.move_to_element(visibility_item).click().perform()
        print("  Clicked via ActionChains")

        # Wait for dialog to open naturally
        time.sleep(2)

        # Check if dialog is now visible
        dialog_state = driver.execute_script("""
            const dialog = document.querySelector('ytcp-filter-dialog #dialog');
            if (!dialog) return {exists: false};
            return {
                exists: true,
                visible: dialog.offsetParent !== null,
                display: getComputedStyle(dialog).display,
                opened: dialog.hasAttribute('opened')
            };
        """)
        print(f"  Dialog state after click: {dialog_state}")

        if dialog_state.get('visible') or dialog_state.get('display') != 'none':
            print("[OK] Dialog opened naturally!")
            return True
        else:
            print("[WARN] Dialog didn't open, trying alternative approach...")
            return step2b_try_alternative_click(driver)

    except Exception as e:
        print(f"[FAIL] {e}")
        return False


def step2b_try_alternative_click(driver):
    """Alternative: Try clicking directly on the Visibility text element."""
    print("\n[STEP 2b] Trying direct element click...")

    # Find the Visibility paper-item and click with JavaScript dispatch
    result = driver.execute_script("""
        const listbox = document.querySelector('tp-yt-paper-listbox[role="listbox"]');
        if (!listbox) return {error: 'no listbox'};

        const items = listbox.querySelectorAll('tp-yt-paper-item');
        for (let item of items) {
            if (item.textContent.trim().toLowerCase().includes('visibility')) {
                // Fire a complete mouse event sequence
                const rect = item.getBoundingClientRect();
                const opts = {
                    bubbles: true,
                    cancelable: true,
                    view: window,
                    clientX: rect.left + rect.width / 2,
                    clientY: rect.top + rect.height / 2
                };

                item.dispatchEvent(new MouseEvent('mousedown', opts));
                item.dispatchEvent(new MouseEvent('mouseup', opts));
                item.dispatchEvent(new MouseEvent('click', opts));

                // Also try the tap event (for touch/mobile)
                try {
                    item.dispatchEvent(new Event('tap', {bubbles: true}));
                } catch(e) {}

                return {clicked: true};
            }
        }
        return {error: 'visibility not found'};
    """)

    print(f"  Result: {result}")
    time.sleep(2)

    # Check dialog state again
    dialog_state = driver.execute_script("""
        const dialog = document.querySelector('ytcp-filter-dialog #dialog');
        if (!dialog) return {exists: false};
        return {
            visible: dialog.offsetParent !== null,
            display: getComputedStyle(dialog).display
        };
    """)

    return dialog_state.get('visible') or dialog_state.get('display') != 'none'


def step3_click_unlisted(driver):
    """Click Unlisted checkbox using coordinates."""
    print("\n[STEP 3] Clicking Unlisted checkbox...")

    # First check if we can see the checkboxes
    checkbox_info = driver.execute_script("""
        const filterDialog = document.querySelector('ytcp-filter-dialog');
        if (!filterDialog) return {error: 'no dialog'};

        const spans = filterDialog.querySelectorAll('span');
        for (let span of spans) {
            if (span.textContent.trim() === 'Unlisted') {
                let current = span.parentElement;
                for (let i = 0; i < 10 && current; i++) {
                    const checkbox = current.querySelector('ytcp-checkbox-lit');
                    if (checkbox && checkbox.offsetParent !== null) {
                        const rect = checkbox.getBoundingClientRect();
                        return {
                            found: true,
                            x: Math.round(rect.left + rect.width / 2),
                            y: Math.round(rect.top + rect.height / 2)
                        };
                    }
                    current = current.parentElement;
                }
            }
        }
        return {found: false, error: 'Unlisted not visible'};
    """)

    if not checkbox_info.get('found'):
        print(f"  [WARN] Checkbox not visible - dialog may not have opened")
        print(f"  Info: {checkbox_info}")
        return False

    print(f"  Checkbox at ({checkbox_info['x']}, {checkbox_info['y']})")

    # Click using ActionChains
    actions = ActionChains(driver)
    actions.move_by_offset(checkbox_info['x'], checkbox_info['y']).click().perform()
    actions.move_by_offset(-checkbox_info['x'], -checkbox_info['y']).perform()

    time.sleep(0.5)

    # Verify
    checked = driver.execute_script("""
        const filterDialog = document.querySelector('ytcp-filter-dialog');
        const spans = filterDialog.querySelectorAll('span');
        for (let span of spans) {
            if (span.textContent.trim() === 'Unlisted') {
                let current = span.parentElement;
                for (let i = 0; i < 10 && current; i++) {
                    const checkbox = current.querySelector('ytcp-checkbox-lit');
                    if (checkbox) {
                        const inner = checkbox.querySelector('#checkbox');
                        return inner ? inner.getAttribute('aria-checked') : 'unknown';
                    }
                    current = current.parentElement;
                }
            }
        }
        return 'not found';
    """)

    print(f"  Checkbox aria-checked: {checked}")
    return checked == 'true'


def step4_click_apply(driver):
    """Click Apply button."""
    print("\n[STEP 4] Clicking Apply button...")

    # Get Apply button coordinates
    apply_info = driver.execute_script("""
        const filterDialog = document.querySelector('ytcp-filter-dialog');
        if (!filterDialog) return {error: 'no dialog'};

        const buttons = filterDialog.querySelectorAll('button, ytcp-button');
        for (let btn of buttons) {
            if (btn.textContent.trim() === 'Apply' && btn.offsetParent !== null) {
                const rect = btn.getBoundingClientRect();
                return {
                    found: true,
                    x: Math.round(rect.left + rect.width / 2),
                    y: Math.round(rect.top + rect.height / 2)
                };
            }
        }
        return {found: false};
    """)

    if not apply_info.get('found'):
        print(f"  [WARN] Apply button not visible")
        return False

    print(f"  Apply at ({apply_info['x']}, {apply_info['y']})")

    # Click using ActionChains
    actions = ActionChains(driver)
    actions.move_by_offset(apply_info['x'], apply_info['y']).click().perform()
    actions.move_by_offset(-apply_info['x'], -apply_info['y']).perform()

    print("[OK] Applied")
    time.sleep(2)
    return True


def verify_filter(driver):
    """Verify the filter was applied."""
    print("\n[VERIFY] Checking filter application...")

    # Wait for page to update
    time.sleep(1)

    # Check URL
    url = driver.current_url
    has_filter = 'filter=' in url or 'UNLISTED' in url.upper()
    print(f"  URL has filter: {has_filter}")
    print(f"  URL: {url[:100]}...")

    # Count video rows
    rows = driver.find_elements(By.CSS_SELECTOR, "ytcp-video-row")
    print(f"  Video rows: {len(rows)}")

    # Check for visibility indicators
    visibility_info = driver.execute_script("""
        const rows = document.querySelectorAll('ytcp-video-row');
        const visibilities = [];
        for (let row of rows) {
            const visCell = row.querySelector('[role="cell"]:nth-child(3)');
            if (visCell) {
                visibilities.push(visCell.textContent.trim().substring(0, 20));
            }
        }
        return visibilities.slice(0, 5);
    """)
    print(f"  First 5 video visibilities: {visibility_info}")

    return has_filter


def main():
    print("\n" + "="*60)
    print("VISIBILITY FILTER TEST - NATURAL CLICKS")
    print("="*60)

    driver = None
    try:
        driver = connect_edge()
        navigate_to_shorts(driver)

        if not step1_click_filter(driver):
            return False

        if not step2_click_visibility_with_wait(driver):
            print("\n[INFO] Dialog didn't open naturally.")
            print("[INFO] This suggests the Visibility item needs a different interaction pattern.")
            print("[INFO] Consider: The Visibility menu item may be a submenu trigger, not a dialog opener.")
            return False

        if not step3_click_unlisted(driver):
            return False

        if not step4_click_apply(driver):
            return False

        success = verify_filter(driver)

        print("\n" + "="*60)
        if success:
            print("TEST PASSED!")
        else:
            print("TEST NEEDS VERIFICATION")
        print("="*60)

        return success

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    main()
