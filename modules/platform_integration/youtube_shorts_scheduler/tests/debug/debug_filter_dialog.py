"""
Debug script v4 - Focus on YTCP-FILTER-DIALOG element.

Key finding: There's a <YTCP-FILTER-DIALOG> that contains "Apply" and "Unlisted"!
This is the visibility sub-dialog we need to explore.
"""

import time
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By

EDGE_PORT = 9223


def connect_edge():
    print(f"[DEBUG] Connecting to Edge on port {EDGE_PORT}...")
    options = Options()
    options.add_experimental_option("debuggerAddress", f"127.0.0.1:{EDGE_PORT}")
    driver = webdriver.Edge(options=options)
    print(f"[DEBUG] Connected!")
    return driver


def navigate_and_open_filter(driver):
    """Navigate to shorts and open filter dropdown."""
    url = "https://studio.youtube.com/channel/UC-LSSlOZwpGIRIYihaz8zCw/videos/short"
    print(f"[DEBUG] Navigating to shorts page...")
    driver.get(url)
    time.sleep(3)

    # Open filter dropdown
    print("[DEBUG] Opening filter dropdown...")
    driver.execute_script("""
        const filterInput = document.querySelector("input[placeholder='Filter']");
        if (filterInput) {
            filterInput.click();
            filterInput.focus();
        }
    """)
    time.sleep(1.5)

    # Click Visibility
    print("[DEBUG] Clicking Visibility...")
    driver.execute_script("""
        const listbox = document.querySelector('tp-yt-paper-listbox[role="listbox"]');
        if (listbox) {
            const items = listbox.querySelectorAll('tp-yt-paper-item');
            for (let item of items) {
                if (item.textContent.trim().toLowerCase().includes('visibility')) {
                    item.click();
                    break;
                }
            }
        }
    """)
    time.sleep(2)


def explore_ytcp_filter_dialog(driver):
    """Deep exploration of YTCP-FILTER-DIALOG element."""
    print("\n" + "="*60)
    print("EXPLORING YTCP-FILTER-DIALOG")
    print("="*60 + "\n")

    result = driver.execute_script("""
        const dialog = document.querySelector('ytcp-filter-dialog');
        if (!dialog) return {found: false, error: 'No ytcp-filter-dialog found'};

        const info = {
            found: true,
            tag: dialog.tagName,
            visible: dialog.offsetParent !== null,
            display: getComputedStyle(dialog).display,
            visibility: getComputedStyle(dialog).visibility,
            position: getComputedStyle(dialog).position,
            rect: dialog.getBoundingClientRect(),
            children: [],
            shadowRoot: null,
            allText: dialog.textContent.substring(0, 500)
        };

        // Check for shadow root
        if (dialog.shadowRoot) {
            info.shadowRoot = {
                exists: true,
                childCount: dialog.shadowRoot.children.length,
                html: dialog.shadowRoot.innerHTML.substring(0, 1000)
            };
        }

        // Get all children
        for (let child of dialog.children) {
            info.children.push({
                tag: child.tagName,
                id: child.id,
                visible: child.offsetParent !== null
            });
        }

        return info;
    """)

    print(f"Found: {result.get('found')}")
    print(f"Tag: {result.get('tag')}")
    print(f"Visible: {result.get('visible')}")
    print(f"Display: {result.get('display')}")
    print(f"Visibility: {result.get('visibility')}")
    print(f"Position: {result.get('position')}")
    print(f"Rect: {result.get('rect')}")
    print(f"\nChildren: {result.get('children')}")

    if result.get('shadowRoot'):
        print(f"\nShadow Root exists!")
        print(f"  Child count: {result['shadowRoot']['childCount']}")
        print(f"  HTML preview: {result['shadowRoot']['html'][:500]}...")

    print(f"\nAll text in dialog:")
    print(f"  {result.get('allText', '')[:400]}...")

    return result


def find_checkboxes_in_dialog(driver):
    """Find checkbox elements within the filter dialog."""
    print("\n" + "="*60)
    print("FINDING CHECKBOXES IN DIALOG")
    print("="*60 + "\n")

    result = driver.execute_script("""
        const dialog = document.querySelector('ytcp-filter-dialog');
        if (!dialog) return {found: false};

        const checkboxes = [];

        // Search in light DOM
        const lightDOMCheckboxes = dialog.querySelectorAll('ytcp-checkbox-lit, [role="checkbox"]');
        for (let cb of lightDOMCheckboxes) {
            checkboxes.push({
                source: 'lightDOM',
                tag: cb.tagName,
                visible: cb.offsetParent !== null,
                text: cb.textContent.substring(0, 50)
            });
        }

        // Search in shadow DOM if exists
        if (dialog.shadowRoot) {
            const shadowCheckboxes = dialog.shadowRoot.querySelectorAll('ytcp-checkbox-lit, [role="checkbox"]');
            for (let cb of shadowCheckboxes) {
                checkboxes.push({
                    source: 'shadowDOM',
                    tag: cb.tagName,
                    visible: cb.offsetParent !== null,
                    text: cb.textContent.substring(0, 50)
                });
            }
        }

        // Also look for any elements with visibility option text
        const visibilityOptions = [];
        const allElements = dialog.querySelectorAll('*');
        for (let el of allElements) {
            const text = el.textContent.trim();
            if ((text === 'Public' || text === 'Private' || text === 'Unlisted' ||
                 text === 'Members' || text === 'Has schedule' || text === 'Draft') &&
                el.children.length === 0) {
                visibilityOptions.push({
                    tag: el.tagName,
                    text: text,
                    visible: el.offsetParent !== null,
                    rect: el.getBoundingClientRect()
                });
            }
        }

        return {
            checkboxes: checkboxes,
            visibilityOptions: visibilityOptions
        };
    """)

    print(f"Checkboxes found: {len(result.get('checkboxes', []))}")
    for cb in result.get('checkboxes', []):
        print(f"  - {cb['source']}: <{cb['tag']}> visible={cb['visible']} text='{cb['text']}'")

    print(f"\nVisibility option labels found: {len(result.get('visibilityOptions', []))}")
    for opt in result.get('visibilityOptions', []):
        print(f"  - '{opt['text']}' <{opt['tag']}> visible={opt['visible']}")
        print(f"    rect: top={opt['rect']['top']}, left={opt['rect']['left']}")

    return result


def find_apply_button(driver):
    """Find the Apply button in the dialog."""
    print("\n" + "="*60)
    print("FINDING APPLY BUTTON")
    print("="*60 + "\n")

    result = driver.execute_script("""
        const dialog = document.querySelector('ytcp-filter-dialog');
        if (!dialog) return {found: false};

        const buttons = [];

        // Find all buttons
        const allButtons = dialog.querySelectorAll('button, ytcp-button, tp-yt-paper-button');
        for (let btn of allButtons) {
            const text = btn.textContent.trim().toLowerCase();
            if (text.includes('apply') || text.includes('done') || text.includes('ok')) {
                buttons.push({
                    tag: btn.tagName,
                    text: btn.textContent.trim(),
                    visible: btn.offsetParent !== null,
                    rect: btn.getBoundingClientRect()
                });
            }
        }

        // Also check shadow DOM
        if (dialog.shadowRoot) {
            const shadowButtons = dialog.shadowRoot.querySelectorAll('button, ytcp-button');
            for (let btn of shadowButtons) {
                const text = btn.textContent.trim().toLowerCase();
                if (text.includes('apply') || text.includes('done')) {
                    buttons.push({
                        source: 'shadowDOM',
                        tag: btn.tagName,
                        text: btn.textContent.trim(),
                        visible: btn.offsetParent !== null
                    });
                }
            }
        }

        return {buttons: buttons};
    """)

    print(f"Apply/Done buttons found: {len(result.get('buttons', []))}")
    for btn in result.get('buttons', []):
        print(f"  - <{btn['tag']}> '{btn['text']}' visible={btn['visible']}")
        if btn.get('rect'):
            print(f"    rect: top={btn['rect']['top']}, left={btn['rect']['left']}")

    return result


def try_click_unlisted(driver):
    """Try clicking the Unlisted option."""
    print("\n" + "="*60)
    print("TRYING TO CLICK UNLISTED")
    print("="*60 + "\n")

    result = driver.execute_script("""
        const dialog = document.querySelector('ytcp-filter-dialog');
        if (!dialog) return {error: 'no dialog'};

        // Find element with text "Unlisted"
        const allElements = dialog.querySelectorAll('*');
        for (let el of allElements) {
            if (el.textContent.trim() === 'Unlisted' && el.children.length === 0) {
                // Found the label, try clicking
                el.click();

                // Also try clicking the parent (might be a label/checkbox wrapper)
                if (el.parentElement) {
                    el.parentElement.click();
                }

                return {
                    clicked: true,
                    element: {
                        tag: el.tagName,
                        parent: el.parentElement ? el.parentElement.tagName : null
                    }
                };
            }
        }

        // Alternative: look for checkbox with Unlisted aria-label
        const checkboxes = dialog.querySelectorAll('[role="checkbox"]');
        for (let cb of checkboxes) {
            const label = cb.getAttribute('aria-label') || '';
            if (label.toLowerCase().includes('unlisted')) {
                cb.click();
                return {clicked: true, method: 'aria-label', label: label};
            }
        }

        return {clicked: false};
    """)

    print(f"Result: {result}")
    time.sleep(1)

    # Check if checkbox state changed
    state = driver.execute_script("""
        const dialog = document.querySelector('ytcp-filter-dialog');
        if (!dialog) return {};

        // Check for any checked checkboxes
        const checkboxes = dialog.querySelectorAll('ytcp-checkbox-lit[checked], [role="checkbox"][aria-checked="true"]');
        const checked = [];
        for (let cb of checkboxes) {
            checked.push({
                tag: cb.tagName,
                text: cb.textContent.substring(0, 50)
            });
        }

        return {checkedCount: checkboxes.length, checked: checked};
    """)

    print(f"Checkbox state after click: {state}")
    return result


def dump_full_dialog_html(driver):
    """Dump the full HTML of the dialog for manual inspection."""
    print("\n" + "="*60)
    print("FULL DIALOG HTML DUMP")
    print("="*60 + "\n")

    result = driver.execute_script("""
        const dialog = document.querySelector('ytcp-filter-dialog');
        if (!dialog) return {found: false};

        return {
            outerHTML: dialog.outerHTML.substring(0, 3000),
            innerHTML: dialog.innerHTML.substring(0, 3000)
        };
    """)

    if result.get('outerHTML'):
        print("First 2000 chars of outerHTML:")
        print(result['outerHTML'][:2000])

    return result


def main():
    print("\n" + "="*60)
    print("YTCP-FILTER-DIALOG EXPLORATION")
    print("="*60 + "\n")

    driver = None
    try:
        driver = connect_edge()
        navigate_and_open_filter(driver)

        # Explore the dialog
        dialog_info = explore_ytcp_filter_dialog(driver)

        if not dialog_info.get('found'):
            print("[FAIL] No ytcp-filter-dialog found. Trying alternative element names...")

            # Try alternative element names
            result = driver.execute_script("""
                const names = [
                    'ytcp-filter-dialog',
                    'ytcp-video-section-filter-dialog',
                    'ytcp-video-section-content-dialog',
                    'ytcp-visibility-selector'
                ];
                const found = [];
                for (let name of names) {
                    const el = document.querySelector(name);
                    if (el) {
                        found.push({
                            name: name,
                            visible: el.offsetParent !== null,
                            text: el.textContent.substring(0, 100)
                        });
                    }
                }
                return found;
            """)
            print(f"Alternative elements found: {result}")
        else:
            # Continue exploration
            find_checkboxes_in_dialog(driver)
            find_apply_button(driver)
            try_click_unlisted(driver)
            dump_full_dialog_html(driver)

        print("\n" + "="*60)
        print("EXPLORATION COMPLETE")
        print("="*60)

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
