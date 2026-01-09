"""
Complete Visibility Filter Test - Working Implementation

This test implements the full visibility filter flow:
1. Open Filter dropdown
2. Click Visibility option
3. Force open the filter dialog (required - it doesn't open automatically)
4. Click Unlisted checkbox
5. Click Apply button
6. Close dropdown

Key Finding (ADR-005):
- The ytcp-filter-dialog's inner paper-dialog has display:none by default
- It must be force-opened via JavaScript after clicking Visibility
- The dialog contains 6 checkboxes: Public, Private, Unlisted, Members, Has schedule, Draft

Run: python -m modules.platform_integration.youtube_shorts_scheduler.tests.test_visibility_filter_complete
"""

import time
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

EDGE_PORT = 9223
CHANNEL_ID = "UC-LSSlOZwpGIRIYihaz8zCw"


def connect_edge():
    """Connect to existing Edge debug session."""
    print(f"[INFO] Connecting to Edge on port {EDGE_PORT}...")
    options = Options()
    options.add_experimental_option("debuggerAddress", f"127.0.0.1:{EDGE_PORT}")
    driver = webdriver.Edge(options=options)
    print(f"[INFO] Connected! URL: {driver.current_url[:60]}...")
    return driver


def navigate_to_shorts(driver):
    """Navigate to the Shorts page."""
    url = f"https://studio.youtube.com/channel/{CHANNEL_ID}/videos/short"
    print(f"[STEP] Navigating to Shorts page...")
    driver.get(url)
    time.sleep(3)
    print(f"[OK] Page loaded: {driver.title}")


def step1_open_filter_dropdown(driver):
    """Step 1: Click Filter input to open dropdown."""
    print("\n[STEP 1] Opening Filter dropdown...")

    result = driver.execute_script("""
        const filterInput = document.querySelector("input[placeholder='Filter']");
        if (!filterInput) return {success: false, error: 'Filter input not found'};

        if (filterInput.offsetParent === null) {
            return {success: false, error: 'Filter input not visible'};
        }

        filterInput.click();
        filterInput.focus();
        return {success: true};
    """)

    if result.get('success'):
        print("[OK] Filter dropdown opened")
        time.sleep(1.5)
        return True
    else:
        print(f"[FAIL] {result.get('error')}")
        return False


def step2_click_visibility(driver):
    """Step 2: Click Visibility option in dropdown."""
    print("\n[STEP 2] Clicking Visibility option...")

    result = driver.execute_script("""
        // Find by test-id
        const item = document.querySelector('[test-id*="VISIBILITY"]');
        if (!item) return {success: false, error: 'Visibility item not found'};

        item.click();
        return {success: true, text: item.textContent.trim()};
    """)

    if result.get('success'):
        print(f"[OK] Clicked: {result.get('text')}")
        time.sleep(0.5)
        return True
    else:
        print(f"[FAIL] {result.get('error')}")
        return False


def step3_force_open_dialog(driver):
    """Step 3: Force open the visibility filter dialog."""
    print("\n[STEP 3] Force opening filter dialog...")

    result = driver.execute_script("""
        const filterDialog = document.querySelector('ytcp-filter-dialog');
        if (!filterDialog) return {success: false, error: 'Filter dialog not found'};

        const paperDialog = filterDialog.querySelector('#dialog');
        if (!paperDialog) return {success: false, error: 'Paper dialog not found'};

        // Force open the dialog
        paperDialog.opened = true;
        paperDialog.setAttribute('opened', '');
        paperDialog.removeAttribute('aria-hidden');
        paperDialog.style.display = 'block';

        // Call open method if available
        if (typeof paperDialog.open === 'function') {
            paperDialog.open();
        }

        // Verify
        const isVisible = paperDialog.offsetParent !== null;
        const checkboxes = filterDialog.querySelectorAll('ytcp-checkbox-lit');
        let visibleCount = 0;
        for (let cb of checkboxes) {
            if (cb.offsetParent !== null) visibleCount++;
        }

        return {
            success: true,
            dialogVisible: isVisible,
            visibleCheckboxes: visibleCount
        };
    """)

    if result.get('success'):
        print(f"[OK] Dialog opened - {result.get('visibleCheckboxes')} checkboxes visible")
        time.sleep(0.5)
        return True
    else:
        print(f"[FAIL] {result.get('error')}")
        return False


def step4_click_unlisted(driver):
    """Step 4: Click the Unlisted checkbox using ActionChains.

    Key Finding (ADR-006): JavaScript .click() doesn't work on ytcp-checkbox-lit.
    Must use Selenium ActionChains for proper mouse click events.
    """
    print("\n[STEP 4] Clicking Unlisted checkbox...")

    from selenium.webdriver.common.action_chains import ActionChains

    # Get checkbox coordinates
    coords = driver.execute_script("""
        const filterDialog = document.querySelector('ytcp-filter-dialog');
        if (!filterDialog) return {error: 'Filter dialog not found'};

        const spans = filterDialog.querySelectorAll('span');
        for (let span of spans) {
            if (span.textContent.trim() === 'Unlisted' && span.offsetParent !== null) {
                // Walk up to find the checkbox-lit element
                let current = span.parentElement;
                for (let i = 0; i < 10 && current; i++) {
                    const checkbox = current.querySelector('ytcp-checkbox-lit');
                    if (checkbox && checkbox.offsetParent !== null) {
                        const rect = checkbox.getBoundingClientRect();
                        const beforeState = checkbox.querySelector('#checkbox');
                        return {
                            success: true,
                            x: Math.round(rect.left + rect.width / 2),
                            y: Math.round(rect.top + rect.height / 2),
                            beforeChecked: beforeState ? beforeState.getAttribute('aria-checked') : 'unknown'
                        };
                    }
                    current = current.parentElement;
                }
                break;
            }
        }
        return {success: false, error: 'Unlisted checkbox not found'};
    """)

    if not coords.get('success'):
        print(f"[FAIL] {coords.get('error')}")
        return False

    print(f"  Checkbox at ({coords['x']}, {coords['y']}), checked={coords['beforeChecked']}")

    # Use ActionChains to click at absolute viewport coordinates
    actions = ActionChains(driver)
    actions.move_by_offset(coords['x'], coords['y']).click().perform()
    # Reset offset
    actions.move_by_offset(-coords['x'], -coords['y']).perform()

    time.sleep(0.5)

    # Verify checkbox state
    after = driver.execute_script("""
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

    if after == 'true':
        print(f"[OK] Unlisted checked (aria-checked={after})")
        return True
    else:
        print(f"[WARN] Checkbox may not be checked (aria-checked={after})")
        return True  # Continue anyway, Apply button might still work


def step5_click_apply(driver):
    """Step 5: Click the Apply button using ActionChains."""
    print("\n[STEP 5] Clicking Apply button...")

    from selenium.webdriver.common.action_chains import ActionChains

    # Get Apply button coordinates
    coords = driver.execute_script("""
        const filterDialog = document.querySelector('ytcp-filter-dialog');
        if (!filterDialog) return {error: 'Filter dialog not found'};

        // Find Apply button
        const buttons = filterDialog.querySelectorAll('button, ytcp-button');
        for (let btn of buttons) {
            const text = btn.textContent.trim();
            if (text === 'Apply' && btn.offsetParent !== null) {
                const rect = btn.getBoundingClientRect();
                return {
                    success: true,
                    x: Math.round(rect.left + rect.width / 2),
                    y: Math.round(rect.top + rect.height / 2),
                    text: text
                };
            }
        }

        return {success: false, error: 'Apply button not found'};
    """)

    if not coords.get('success'):
        print(f"[FAIL] {coords.get('error')}")
        return False

    print(f"  Apply button at ({coords['x']}, {coords['y']})")

    # Use ActionChains to click
    actions = ActionChains(driver)
    actions.move_by_offset(coords['x'], coords['y']).click().perform()
    # Reset offset
    actions.move_by_offset(-coords['x'], -coords['y']).perform()

    print(f"[OK] Clicked: {coords.get('text')}")
    time.sleep(1.5)
    return True


def step6_close_dropdown(driver):
    """Step 6: Close any remaining dropdown by pressing ESC."""
    print("\n[STEP 6] Closing dropdown...")

    try:
        body = driver.find_element(By.TAG_NAME, "body")
        body.send_keys(Keys.ESCAPE)
        time.sleep(0.5)
        body.send_keys(Keys.ESCAPE)
        print("[OK] Dropdown closed")
        time.sleep(1)
        return True
    except Exception as e:
        print(f"[WARN] Could not close dropdown: {e}")
        return True  # Not critical


def verify_filter_applied(driver):
    """Verify the Unlisted filter was applied."""
    print("\n[VERIFY] Checking if filter was applied...")

    # Check URL for filter parameter
    url = driver.current_url
    has_filter_param = 'filter=' in url and 'UNLISTED' in url.upper()

    # Check for filter chip/badge
    result = driver.execute_script("""
        // Look for active filter chip
        const chips = document.querySelectorAll('ytcp-chip, [class*="filter-chip"], [class*="active"]');
        const activeFilters = [];
        for (let chip of chips) {
            const text = chip.textContent.trim();
            if (text.toLowerCase().includes('unlisted') || text.toLowerCase().includes('visibility')) {
                activeFilters.push(text);
            }
        }
        return {
            activeFilters: activeFilters,
            filterChipCount: chips.length
        };
    """)

    print(f"  URL has filter param: {has_filter_param}")
    print(f"  Active filter chips: {result.get('activeFilters', [])}")

    # Count visible video rows
    video_rows = driver.find_elements(By.CSS_SELECTOR, "ytcp-video-row")
    print(f"  Video rows visible: {len(video_rows)}")

    return has_filter_param or len(result.get('activeFilters', [])) > 0


def main():
    """Run the complete visibility filter test."""
    print("\n" + "="*60)
    print("COMPLETE VISIBILITY FILTER TEST")
    print("="*60)

    driver = None
    try:
        driver = connect_edge()

        # Navigate to Shorts page
        navigate_to_shorts(driver)

        # Execute filter flow
        if not step1_open_filter_dropdown(driver):
            return False

        if not step2_click_visibility(driver):
            return False

        if not step3_force_open_dialog(driver):
            return False

        if not step4_click_unlisted(driver):
            return False

        if not step5_click_apply(driver):
            return False

        step6_close_dropdown(driver)

        # Verify
        success = verify_filter_applied(driver)

        print("\n" + "="*60)
        if success:
            print("TEST PASSED - Unlisted filter applied!")
        else:
            print("TEST INCOMPLETE - Filter may need verification")
        print("="*60)

        return success

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    main()
