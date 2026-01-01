"""
Debug script v5 - Try to open the ytcp-filter-dialog.

Key finding: The dialog exists but is hidden (display: none).
We need to trigger it to open.

The inner <tp-yt-paper-dialog> has:
- display: none
- aria-hidden: true

Try different methods to open it:
1. Call .open() method on paper-dialog
2. Set opened attribute
3. Use a different interaction to trigger the dialog
"""

import time
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

EDGE_PORT = 9223


def connect_edge():
    print(f"[DEBUG] Connecting to Edge on port {EDGE_PORT}...")
    options = Options()
    options.add_experimental_option("debuggerAddress", f"127.0.0.1:{EDGE_PORT}")
    driver = webdriver.Edge(options=options)
    print(f"[DEBUG] Connected!")
    return driver


def navigate_to_shorts(driver):
    url = "https://studio.youtube.com/channel/UC-LSSlOZwpGIRIYihaz8zCw/videos/short"
    print(f"[DEBUG] Navigating to shorts page...")
    driver.get(url)
    time.sleep(3)


def try_open_dialog_directly(driver):
    """Try to open the dialog directly using JavaScript."""
    print("\n" + "="*60)
    print("TRYING TO OPEN DIALOG DIRECTLY")
    print("="*60 + "\n")

    result = driver.execute_script("""
        const filterDialog = document.querySelector('ytcp-filter-dialog');
        if (!filterDialog) return {error: 'no filter dialog found'};

        const paperDialog = filterDialog.querySelector('#dialog');
        if (!paperDialog) return {error: 'no paper dialog found'};

        // Check current state
        const beforeState = {
            display: getComputedStyle(paperDialog).display,
            ariaHidden: paperDialog.getAttribute('aria-hidden'),
            opened: paperDialog.opened || paperDialog.hasAttribute('opened')
        };

        // Method 1: Try calling open() method
        if (typeof paperDialog.open === 'function') {
            paperDialog.open();
        }

        // Method 2: Set opened property/attribute
        paperDialog.opened = true;
        paperDialog.setAttribute('opened', '');
        paperDialog.removeAttribute('aria-hidden');

        // Method 3: Force display
        paperDialog.style.display = 'block';

        // Check after state
        const afterState = {
            display: getComputedStyle(paperDialog).display,
            ariaHidden: paperDialog.getAttribute('aria-hidden'),
            opened: paperDialog.opened || paperDialog.hasAttribute('opened')
        };

        return {
            before: beforeState,
            after: afterState
        };
    """)

    print(f"Before: {result.get('before')}")
    print(f"After: {result.get('after')}")
    time.sleep(1)

    # Check if dialog is now visible
    visible_check = driver.execute_script("""
        const filterDialog = document.querySelector('ytcp-filter-dialog');
        const paperDialog = filterDialog.querySelector('#dialog');
        const checkboxes = filterDialog.querySelectorAll('ytcp-checkbox-lit');

        let visibleCheckboxes = 0;
        for (let cb of checkboxes) {
            if (cb.offsetParent !== null) visibleCheckboxes++;
        }

        return {
            dialogVisible: paperDialog.offsetParent !== null,
            visibleCheckboxes: visibleCheckboxes
        };
    """)
    print(f"Visibility check: {visible_check}")

    return result


def try_visibility_submenu_approach(driver):
    """Try opening the visibility submenu via the correct UI path."""
    print("\n" + "="*60)
    print("TRYING VISIBILITY SUBMENU APPROACH")
    print("="*60 + "\n")

    # Step 1: Open filter dropdown
    print("[STEP 1] Opening filter dropdown...")
    driver.execute_script("""
        const filterInput = document.querySelector("input[placeholder='Filter']");
        if (filterInput) {
            filterInput.click();
            filterInput.focus();
        }
    """)
    time.sleep(1.5)

    # Step 2: Check if Visibility item has an expand icon or submenu trigger
    print("[STEP 2] Analyzing Visibility item structure...")
    result = driver.execute_script("""
        const listbox = document.querySelector('tp-yt-paper-listbox[role="listbox"]');
        if (!listbox) return {error: 'no listbox'};

        const items = listbox.querySelectorAll('tp-yt-paper-item');
        let visibilityItem = null;

        for (let item of items) {
            if (item.textContent.trim().toLowerCase().includes('visibility')) {
                visibilityItem = item;
                break;
            }
        }

        if (!visibilityItem) return {error: 'visibility item not found'};

        // Get detailed structure
        const structure = {
            html: visibilityItem.innerHTML,
            icons: [],
            buttons: [],
            links: []
        };

        // Find icons
        const icons = visibilityItem.querySelectorAll('yt-icon, ytcp-icon, iron-icon, svg');
        for (let icon of icons) {
            structure.icons.push({
                tag: icon.tagName,
                class: icon.className || ''
            });
        }

        // Find buttons
        const buttons = visibilityItem.querySelectorAll('button, ytcp-button');
        for (let btn of buttons) {
            structure.buttons.push({
                tag: btn.tagName,
                text: btn.textContent.substring(0, 20)
            });
        }

        return structure;
    """)
    print(f"Icons in Visibility item: {result.get('icons', [])}")
    print(f"Buttons in Visibility item: {result.get('buttons', [])}")

    # Step 3: Try double-clicking on Visibility
    print("\n[STEP 3] Trying double-click on Visibility...")
    driver.execute_script("""
        const listbox = document.querySelector('tp-yt-paper-listbox[role="listbox"]');
        if (!listbox) return;

        const items = listbox.querySelectorAll('tp-yt-paper-item');
        for (let item of items) {
            if (item.textContent.trim().toLowerCase().includes('visibility')) {
                // Double-click
                item.dispatchEvent(new MouseEvent('dblclick', {bubbles: true}));
                break;
            }
        }
    """)
    time.sleep(1.5)

    # Check dialog state
    state = driver.execute_script("""
        const filterDialog = document.querySelector('ytcp-filter-dialog');
        const paperDialog = filterDialog ? filterDialog.querySelector('#dialog') : null;

        return {
            dialogExists: !!paperDialog,
            dialogVisible: paperDialog ? paperDialog.offsetParent !== null : false,
            displayStyle: paperDialog ? getComputedStyle(paperDialog).display : 'N/A'
        };
    """)
    print(f"Dialog state after double-click: {state}")

    return state


def try_test_id_click(driver):
    """Try clicking the Visibility item using test-id attribute."""
    print("\n" + "="*60)
    print("TRYING TEST-ID BASED CLICK")
    print("="*60 + "\n")

    # The Visibility item has test-id='{"filterName":"VISIBILITY"}'
    result = driver.execute_script("""
        // Find item by test-id
        const item = document.querySelector('[test-id*="VISIBILITY"]');
        if (!item) return {error: 'item not found by test-id'};

        // Simulate user interaction more completely
        item.focus();
        item.dispatchEvent(new MouseEvent('mousedown', {bubbles: true, cancelable: true}));
        item.dispatchEvent(new MouseEvent('mouseup', {bubbles: true, cancelable: true}));
        item.dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}));

        return {clicked: true, testId: item.getAttribute('test-id')};
    """)
    print(f"Test-ID click result: {result}")
    time.sleep(2)

    # Check dialog state
    state = driver.execute_script("""
        const filterDialog = document.querySelector('ytcp-filter-dialog');
        const paperDialog = filterDialog ? filterDialog.querySelector('#dialog') : null;

        return {
            dialogVisible: paperDialog ? paperDialog.offsetParent !== null : false,
            displayStyle: paperDialog ? getComputedStyle(paperDialog).display : 'N/A'
        };
    """)
    print(f"Dialog state after test-id click: {state}")

    return state


def try_action_chain_click(driver):
    """Try using Selenium ActionChains for a more realistic click."""
    print("\n" + "="*60)
    print("TRYING ACTION CHAIN CLICK")
    print("="*60 + "\n")

    # First navigate fresh
    navigate_to_shorts(driver)
    time.sleep(2)

    # Open filter dropdown
    print("[STEP 1] Opening filter dropdown via ActionChains...")
    filter_input = driver.find_element(By.CSS_SELECTOR, "input[placeholder='Filter']")
    actions = ActionChains(driver)
    actions.move_to_element(filter_input).click().perform()
    time.sleep(1.5)

    # Find and click Visibility using ActionChains
    print("[STEP 2] Finding Visibility item...")
    visibility_item = driver.execute_script("""
        const items = document.querySelectorAll('tp-yt-paper-item');
        for (let item of items) {
            if (item.textContent.trim().toLowerCase().includes('visibility') &&
                item.offsetParent !== null) {
                return item;
            }
        }
        return null;
    """)

    if visibility_item:
        print("[STEP 3] Clicking Visibility with ActionChains...")
        actions = ActionChains(driver)
        actions.move_to_element(visibility_item).click().perform()
        time.sleep(2)

        # Check dialog state
        state = driver.execute_script("""
            const filterDialog = document.querySelector('ytcp-filter-dialog');
            const paperDialog = filterDialog ? filterDialog.querySelector('#dialog') : null;

            if (!paperDialog) return {found: false};

            return {
                found: true,
                visible: paperDialog.offsetParent !== null,
                display: getComputedStyle(paperDialog).display,
                top: paperDialog.getBoundingClientRect().top,
                height: paperDialog.getBoundingClientRect().height
            };
        """)
        print(f"Dialog state after ActionChains click: {state}")

        # If dialog is now visible, check for checkboxes
        if state.get('visible') or state.get('display') != 'none':
            print("\n[SUCCESS] Dialog may be open! Checking for checkboxes...")
            checkboxes = driver.execute_script("""
                const filterDialog = document.querySelector('ytcp-filter-dialog');
                const checkboxes = filterDialog.querySelectorAll('ytcp-checkbox-lit');
                const results = [];
                for (let cb of checkboxes) {
                    const visible = cb.offsetParent !== null;
                    const rect = cb.getBoundingClientRect();
                    if (rect.height > 0) {
                        results.push({
                            visible: visible,
                            rect: {top: rect.top, left: rect.left, height: rect.height}
                        });
                    }
                }
                return results;
            """)
            print(f"Visible checkboxes: {checkboxes}")
    else:
        print("[WARN] Could not find Visibility item")

    return None


def main():
    print("\n" + "="*60)
    print("DIALOG OPENING EXPLORATION")
    print("="*60 + "\n")

    driver = None
    try:
        driver = connect_edge()

        # Try ActionChains first (most realistic user interaction)
        try_action_chain_click(driver)

        # If that didn't work, try other approaches
        try_visibility_submenu_approach(driver)

        try_test_id_click(driver)

        # Last resort: force open
        try_open_dialog_directly(driver)

        print("\n" + "="*60)
        print("EXPLORATION COMPLETE")
        print("="*60)

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
