"""
Debug the checkbox click in the visibility filter dialog.

The issue: We click Unlisted checkbox but the filter doesn't apply.
Need to understand the exact checkbox structure.
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
    return driver


def setup_dialog(driver):
    """Navigate and open the visibility dialog."""
    url = "https://studio.youtube.com/channel/UC-LSSlOZwpGIRIYihaz8zCw/videos/short"
    print(f"[DEBUG] Navigating to shorts page...")
    driver.get(url)
    time.sleep(3)

    # Open filter dropdown
    driver.execute_script("""
        const filterInput = document.querySelector("input[placeholder='Filter']");
        if (filterInput) {
            filterInput.click();
            filterInput.focus();
        }
    """)
    time.sleep(1.5)

    # Click Visibility
    driver.execute_script("""
        const item = document.querySelector('[test-id*="VISIBILITY"]');
        if (item) item.click();
    """)
    time.sleep(0.5)

    # Force open dialog
    driver.execute_script("""
        const filterDialog = document.querySelector('ytcp-filter-dialog');
        const paperDialog = filterDialog.querySelector('#dialog');
        if (paperDialog) {
            paperDialog.opened = true;
            paperDialog.setAttribute('opened', '');
            paperDialog.removeAttribute('aria-hidden');
            paperDialog.style.display = 'block';
        }
    """)
    time.sleep(1)


def analyze_checkbox_structure(driver):
    """Analyze the structure of checkbox elements."""
    print("\n" + "="*60)
    print("CHECKBOX STRUCTURE ANALYSIS")
    print("="*60 + "\n")

    result = driver.execute_script("""
        const filterDialog = document.querySelector('ytcp-filter-dialog');
        if (!filterDialog) return {error: 'no dialog'};

        // Find all ytcp-checkbox-lit elements
        const checkboxes = filterDialog.querySelectorAll('ytcp-checkbox-lit');
        const analysis = [];

        for (let i = 0; i < checkboxes.length; i++) {
            const cb = checkboxes[i];
            if (cb.offsetParent === null) continue;

            // Get the label text by looking for nearby span
            const siblings = cb.parentElement ? Array.from(cb.parentElement.children) : [];
            let labelText = '';
            for (let sibling of siblings) {
                if (sibling.tagName === 'SPAN' || sibling.tagName === 'DIV') {
                    const text = sibling.textContent.trim();
                    if (text && text.length < 50) {
                        labelText = text;
                        break;
                    }
                }
            }

            // If no sibling label, check parent's text
            if (!labelText && cb.parentElement) {
                const parentText = cb.parentElement.textContent.trim();
                if (parentText.length < 50) labelText = parentText;
            }

            // Get checkbox inner structure
            const innerDiv = cb.querySelector('#checkbox');
            const isChecked = cb.hasAttribute('checked') ||
                            (innerDiv && innerDiv.getAttribute('aria-checked') === 'true');

            analysis.push({
                index: i,
                labelText: labelText,
                isChecked: isChecked,
                hasInnerCheckbox: !!innerDiv,
                parentTag: cb.parentElement ? cb.parentElement.tagName : null,
                rect: cb.getBoundingClientRect()
            });
        }

        return analysis;
    """)

    print("Visible checkboxes and their labels:")
    for item in result:
        checked = "[x]" if item.get('isChecked') else "[ ]"
        print(f"  {checked} Index {item['index']}: '{item['labelText']}'")
        print(f"      parent: {item['parentTag']}, top: {item['rect']['top']}")

    return result


def find_unlisted_checkbox(driver):
    """Find the correct element to click for Unlisted."""
    print("\n" + "="*60)
    print("FINDING UNLISTED CLICKABLE ELEMENT")
    print("="*60 + "\n")

    result = driver.execute_script("""
        const filterDialog = document.querySelector('ytcp-filter-dialog');
        if (!filterDialog) return {error: 'no dialog'};

        // Get the form/contents area
        const form = filterDialog.querySelector('#contentsForm');
        if (!form) return {error: 'no form'};

        // Find all row containers that have checkbox and label
        const rows = form.querySelectorAll('ytcp-checkbox-group, .checkbox-label-container, [class*="checkbox"]');
        const rowAnalysis = [];

        for (let row of rows) {
            if (row.offsetParent === null) continue;
            const text = row.textContent.trim();
            if (text.includes('Unlisted')) {
                rowAnalysis.push({
                    tag: row.tagName,
                    class: row.className,
                    text: text.substring(0, 50),
                    hasCheckbox: !!row.querySelector('ytcp-checkbox-lit, [role="checkbox"]')
                });
            }
        }

        // Alternative: find by walking the DOM from "Unlisted" span
        const spans = filterDialog.querySelectorAll('span');
        let unlistedInfo = null;

        for (let span of spans) {
            if (span.textContent.trim() === 'Unlisted' && span.offsetParent !== null) {
                // Walk up to find the row container
                let current = span;
                let rowContainer = null;
                for (let i = 0; i < 10 && current; i++) {
                    current = current.parentElement;
                    if (!current) break;

                    // Check if this is a row with a checkbox
                    const checkbox = current.querySelector('ytcp-checkbox-lit, [role="checkbox"]');
                    if (checkbox && checkbox.offsetParent !== null) {
                        rowContainer = current;
                        break;
                    }
                }

                if (rowContainer) {
                    const checkbox = rowContainer.querySelector('ytcp-checkbox-lit');
                    const innerDiv = checkbox ? checkbox.querySelector('#checkbox') : null;

                    unlistedInfo = {
                        found: true,
                        rowTag: rowContainer.tagName,
                        rowClass: rowContainer.className.substring(0, 50),
                        checkboxTag: checkbox ? checkbox.tagName : null,
                        innerCheckboxRole: innerDiv ? innerDiv.getAttribute('role') : null,
                        innerCheckboxAria: innerDiv ? innerDiv.getAttribute('aria-checked') : null
                    };
                }
                break;
            }
        }

        return {
            rows: rowAnalysis,
            unlisted: unlistedInfo
        };
    """)

    print(f"Rows with Unlisted: {result.get('rows', [])}")
    print(f"Unlisted info: {result.get('unlisted')}")

    return result


def click_unlisted_properly(driver):
    """Try to click Unlisted with the correct element."""
    print("\n" + "="*60)
    print("CLICKING UNLISTED PROPERLY")
    print("="*60 + "\n")

    # Method 1: Click the inner #checkbox div
    result = driver.execute_script("""
        const filterDialog = document.querySelector('ytcp-filter-dialog');
        if (!filterDialog) return {error: 'no dialog'};

        // Find Unlisted span
        const spans = filterDialog.querySelectorAll('span');
        let targetCheckbox = null;

        for (let span of spans) {
            if (span.textContent.trim() === 'Unlisted' && span.offsetParent !== null) {
                // Walk up to find the checkbox
                let current = span.parentElement;
                for (let i = 0; i < 10 && current; i++) {
                    const checkbox = current.querySelector('ytcp-checkbox-lit');
                    if (checkbox && checkbox.offsetParent !== null) {
                        targetCheckbox = checkbox;
                        break;
                    }
                    current = current.parentElement;
                }
                break;
            }
        }

        if (!targetCheckbox) return {error: 'Unlisted checkbox not found'};

        // Get inner checkbox div
        const innerDiv = targetCheckbox.querySelector('#checkbox');
        const beforeState = innerDiv ? innerDiv.getAttribute('aria-checked') : 'unknown';

        // Try clicking the inner div
        if (innerDiv) {
            innerDiv.click();
        }

        // Also try clicking the checkbox-lit element itself
        targetCheckbox.click();

        // Check state after
        const afterState = innerDiv ? innerDiv.getAttribute('aria-checked') : 'unknown';

        return {
            success: true,
            beforeState: beforeState,
            afterState: afterState
        };
    """)

    print(f"Click result: {result}")
    time.sleep(1)

    # Verify checkbox state
    verify = driver.execute_script("""
        const filterDialog = document.querySelector('ytcp-filter-dialog');
        const checkboxes = filterDialog.querySelectorAll('ytcp-checkbox-lit');

        const states = [];
        for (let cb of checkboxes) {
            if (cb.offsetParent === null) continue;

            const innerDiv = cb.querySelector('#checkbox');
            const isChecked = innerDiv ? innerDiv.getAttribute('aria-checked') === 'true' : false;
            const text = cb.parentElement ? cb.parentElement.textContent.trim().substring(0, 30) : '';

            states.push({
                text: text,
                checked: isChecked
            });
        }
        return states;
    """)

    print(f"Checkbox states after click: {verify}")

    return result


def click_by_coordinates(driver):
    """Click the Unlisted checkbox by coordinates as last resort."""
    print("\n" + "="*60)
    print("TRYING COORDINATE-BASED CLICK")
    print("="*60 + "\n")

    from selenium.webdriver.common.action_chains import ActionChains

    # Get Unlisted checkbox coordinates
    coords = driver.execute_script("""
        const filterDialog = document.querySelector('ytcp-filter-dialog');
        if (!filterDialog) return {error: 'no dialog'};

        const spans = filterDialog.querySelectorAll('span');
        for (let span of spans) {
            if (span.textContent.trim() === 'Unlisted' && span.offsetParent !== null) {
                let current = span.parentElement;
                for (let i = 0; i < 10 && current; i++) {
                    const checkbox = current.querySelector('ytcp-checkbox-lit');
                    if (checkbox && checkbox.offsetParent !== null) {
                        const rect = checkbox.getBoundingClientRect();
                        return {
                            x: rect.left + rect.width / 2,
                            y: rect.top + rect.height / 2,
                            width: rect.width,
                            height: rect.height
                        };
                    }
                    current = current.parentElement;
                }
                break;
            }
        }
        return {error: 'not found'};
    """)

    print(f"Unlisted checkbox coordinates: {coords}")

    if coords.get('x'):
        # Use ActionChains to click at coordinates
        actions = ActionChains(driver)
        actions.move_by_offset(coords['x'], coords['y']).click().perform()
        # Reset position
        actions.move_by_offset(-coords['x'], -coords['y']).perform()
        print("[OK] Clicked by coordinates")
        time.sleep(1)

        # Verify
        verify = driver.execute_script("""
            const filterDialog = document.querySelector('ytcp-filter-dialog');
            const spans = filterDialog.querySelectorAll('span');
            for (let span of spans) {
                if (span.textContent.trim() === 'Unlisted') {
                    let current = span.parentElement;
                    for (let i = 0; i < 10 && current; i++) {
                        const checkbox = current.querySelector('ytcp-checkbox-lit');
                        if (checkbox) {
                            const innerDiv = checkbox.querySelector('#checkbox');
                            return {
                                checked: innerDiv ? innerDiv.getAttribute('aria-checked') : 'unknown'
                            };
                        }
                        current = current.parentElement;
                    }
                }
            }
            return {error: 'not found'};
        """)
        print(f"Unlisted checked state: {verify}")

    return coords


def main():
    print("\n" + "="*60)
    print("CHECKBOX CLICK DEBUGGING")
    print("="*60 + "\n")

    driver = None
    try:
        driver = connect_edge()
        setup_dialog(driver)

        analyze_checkbox_structure(driver)
        find_unlisted_checkbox(driver)
        click_unlisted_properly(driver)
        click_by_coordinates(driver)

        print("\n" + "="*60)
        print("DEBUG COMPLETE")
        print("="*60)

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
