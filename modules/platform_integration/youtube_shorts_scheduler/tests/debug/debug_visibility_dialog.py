"""
Debug script to inspect the Visibility sub-dialog DOM structure.

Run: python -m modules.platform_integration.youtube_shorts_scheduler.tests.debug_visibility_dialog
"""

import time
import json
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By

EDGE_PORT = 9223

def connect_edge():
    """Connect to existing Edge debug session."""
    print(f"[DEBUG] Connecting to Edge on port {EDGE_PORT}...")
    options = Options()
    options.add_experimental_option("debuggerAddress", f"127.0.0.1:{EDGE_PORT}")
    driver = webdriver.Edge(options=options)
    print(f"[DEBUG] Connected! URL: {driver.current_url[:60]}...")
    return driver


def click_filter_input(driver):
    """Click the Filter input to open dropdown."""
    print("[DEBUG] Clicking Filter input...")
    result = driver.execute_script("""
        const filterInput = document.querySelector("input[placeholder='Filter']");
        if (filterInput && filterInput.offsetParent !== null) {
            filterInput.click();
            filterInput.focus();
            return {clicked: true, method: 'direct'};
        }
        return {clicked: false};
    """)
    print(f"  Result: {result}")
    return result.get('clicked', False)


def click_visibility(driver):
    """Click Visibility option in the dropdown."""
    print("[DEBUG] Clicking Visibility...")
    result = driver.execute_script("""
        // Find the dropdown listbox and click Visibility
        const listbox = document.querySelector('tp-yt-paper-listbox[role="listbox"]');
        if (!listbox) return {found: false, error: 'no listbox'};

        const items = listbox.querySelectorAll('tp-yt-paper-item');
        for (let item of items) {
            if (item.textContent.trim().toLowerCase().includes('visibility')) {
                item.click();
                return {clicked: true, text: item.textContent.trim()};
            }
        }
        return {clicked: false, count: items.length};
    """)
    print(f"  Result: {result}")
    return result.get('clicked', False)


def dump_visibility_dialog(driver):
    """Dump ALL visible elements in the visibility sub-dialog."""
    print("\n" + "="*60)
    print("VISIBILITY SUB-DIALOG DOM DUMP")
    print("="*60 + "\n")

    result = driver.execute_script("""
        const dump = {
            timestamp: new Date().toISOString(),
            visibleElements: [],
            checkboxElements: [],
            buttonElements: [],
            spanElements: [],
            dialogElements: [],
            ironDropdowns: [],
            paperItems: []
        };

        // Function to get element info
        function getElementInfo(el) {
            const rect = el.getBoundingClientRect();
            return {
                tag: el.tagName,
                id: el.id || null,
                class: el.className || null,
                role: el.getAttribute('role') || null,
                ariaLabel: el.getAttribute('aria-label') || null,
                text: el.textContent.trim().substring(0, 100),
                rect: {
                    top: Math.round(rect.top),
                    left: Math.round(rect.left),
                    width: Math.round(rect.width),
                    height: Math.round(rect.height)
                },
                visible: el.offsetParent !== null
            };
        }

        // Get all visible checkboxes or checkbox-like elements
        const checkboxes = document.querySelectorAll(
            '[role="checkbox"], tp-yt-paper-checkbox, input[type="checkbox"], ' +
            '[class*="checkbox"], ytcp-checkbox-group, ytcp-checkbox-lit'
        );
        for (let el of checkboxes) {
            if (el.offsetParent !== null) {
                dump.checkboxElements.push(getElementInfo(el));
            }
        }

        // Get all visible buttons
        const buttons = document.querySelectorAll('button, ytcp-button, tp-yt-paper-button');
        for (let el of buttons) {
            if (el.offsetParent !== null && el.textContent.trim().length > 0) {
                dump.buttonElements.push(getElementInfo(el));
            }
        }

        // Get all visible spans with text
        const spans = document.querySelectorAll('span');
        for (let el of spans) {
            const text = el.textContent.trim();
            // Filter for visibility-related text
            if (el.offsetParent !== null &&
                el.children.length === 0 &&
                (text === 'Public' || text === 'Private' || text === 'Unlisted' ||
                 text === 'Members' || text === 'Has schedule' || text === 'Draft' ||
                 text === 'Apply' || text === 'Cancel')) {
                dump.spanElements.push(getElementInfo(el));
            }
        }

        // Get all visible dialogs
        const dialogs = document.querySelectorAll(
            '[role="dialog"], tp-yt-paper-dialog, ytcp-dialog, ' +
            'ytcp-video-section-content-dialog, ytcp-dropdown-menu'
        );
        for (let el of dialogs) {
            if (el.offsetParent !== null) {
                dump.dialogElements.push(getElementInfo(el));
            }
        }

        // Get all visible iron-dropdowns (YouTube uses these)
        const ironDropdowns = document.querySelectorAll(
            'tp-yt-iron-dropdown, iron-dropdown, ytcp-iron-dropdown'
        );
        for (let el of ironDropdowns) {
            if (el.offsetParent !== null) {
                dump.ironDropdowns.push(getElementInfo(el));
            }
        }

        // Get all visible paper items
        const paperItems = document.querySelectorAll('tp-yt-paper-item, paper-item, ytcp-ve');
        for (let el of paperItems) {
            if (el.offsetParent !== null) {
                const info = getElementInfo(el);
                // Only include items in the sub-dialog (not the main dropdown)
                if (info.text.includes('Public') || info.text.includes('Private') ||
                    info.text.includes('Unlisted') || info.text.includes('Members') ||
                    info.text.includes('Draft') || info.text.includes('schedule')) {
                    dump.paperItems.push(info);
                }
            }
        }

        // Also try to find the specific sub-dialog container
        const subDialogs = document.querySelectorAll(
            'ytcp-video-section-filter-dialog, ' +
            'ytcp-video-section-content-dialog, ' +
            '[class*="filter-dialog"], ' +
            '[class*="visibility"]'
        );
        for (let el of subDialogs) {
            if (el.offsetParent !== null) {
                dump.dialogElements.push({
                    ...getElementInfo(el),
                    innerHTML: el.innerHTML.substring(0, 500)
                });
            }
        }

        return dump;
    """)

    print("CHECKBOXES:")
    for el in result.get('checkboxElements', []):
        print(f"  <{el['tag']}> id={el['id']} role={el['role']} text='{el['text'][:50]}'")
        print(f"    rect: top={el['rect']['top']} left={el['rect']['left']}")

    print("\nSPAN ELEMENTS (visibility-related):")
    for el in result.get('spanElements', []):
        print(f"  <{el['tag']}> text='{el['text']}' class={el['class'][:50] if el['class'] else None}")
        print(f"    rect: top={el['rect']['top']} left={el['rect']['left']}")

    print("\nBUTTONS:")
    for el in result.get('buttonElements', []):
        if 'apply' in el['text'].lower() or 'cancel' in el['text'].lower():
            print(f"  <{el['tag']}> text='{el['text'][:30]}' aria={el['ariaLabel']}")
            print(f"    rect: top={el['rect']['top']} left={el['rect']['left']}")

    print("\nDIALOGS:")
    for el in result.get('dialogElements', []):
        print(f"  <{el['tag']}> id={el['id']} role={el['role']}")
        print(f"    text preview: '{el['text'][:100]}'")

    print("\nIRON DROPDOWNS:")
    for el in result.get('ironDropdowns', []):
        print(f"  <{el['tag']}> id={el['id']}")
        print(f"    text preview: '{el['text'][:100]}'")

    print("\nPAPER ITEMS (visibility options):")
    for el in result.get('paperItems', []):
        print(f"  <{el['tag']}> text='{el['text'][:50]}'")

    return result


def find_clickable_unlisted(driver):
    """Try different approaches to find and click Unlisted."""
    print("\n" + "="*60)
    print("FINDING CLICKABLE UNLISTED ELEMENT")
    print("="*60 + "\n")

    # Method 1: Find by aria-label
    result = driver.execute_script("""
        // Look for elements with aria-label containing "Unlisted"
        const ariaElements = document.querySelectorAll('[aria-label*="Unlisted"], [aria-label*="unlisted"]');
        const found = [];
        for (let el of ariaElements) {
            if (el.offsetParent !== null) {
                found.push({
                    tag: el.tagName,
                    ariaLabel: el.getAttribute('aria-label'),
                    clickable: true
                });
            }
        }
        return {method: 'aria-label', found: found};
    """)
    print(f"Method 1 (aria-label): {result}")

    # Method 2: Find by data attributes
    result = driver.execute_script("""
        const dataElements = document.querySelectorAll(
            '[data-filter-value="UNLISTED"], ' +
            '[data-visibility="unlisted"], ' +
            '[data-value="UNLISTED"]'
        );
        const found = [];
        for (let el of dataElements) {
            if (el.offsetParent !== null) {
                found.push({
                    tag: el.tagName,
                    id: el.id,
                    attrs: [...el.attributes].map(a => a.name + '=' + a.value).join(', ')
                });
            }
        }
        return {method: 'data-attr', found: found};
    """)
    print(f"Method 2 (data attributes): {result}")

    # Method 3: Find parent of "Unlisted" text and look for clickable sibling
    result = driver.execute_script("""
        // Find SPAN with "Unlisted" text, then find clickable parent or sibling
        const spans = document.querySelectorAll('span');
        for (let span of spans) {
            if (span.offsetParent !== null && span.textContent.trim() === 'Unlisted') {
                // Found the span, now look for clickable element
                const parent = span.parentElement;
                const grandparent = parent ? parent.parentElement : null;

                // Try parent
                const parentInfo = parent ? {
                    tag: parent.tagName,
                    class: parent.className,
                    role: parent.getAttribute('role'),
                    clickable: parent.onclick !== null ||
                               parent.getAttribute('role') === 'checkbox' ||
                               parent.tagName === 'LABEL'
                } : null;

                // Try grandparent
                const grandparentInfo = grandparent ? {
                    tag: grandparent.tagName,
                    class: grandparent.className,
                    role: grandparent.getAttribute('role')
                } : null;

                // Look for checkbox sibling
                let checkboxSibling = null;
                if (parent) {
                    const siblings = parent.querySelectorAll('[role="checkbox"], input[type="checkbox"]');
                    if (siblings.length > 0) {
                        checkboxSibling = {
                            tag: siblings[0].tagName,
                            role: siblings[0].getAttribute('role')
                        };
                    }
                }

                return {
                    method: 'span-parent-search',
                    spanRect: span.getBoundingClientRect(),
                    parent: parentInfo,
                    grandparent: grandparentInfo,
                    checkboxSibling: checkboxSibling
                };
            }
        }
        return {method: 'span-parent-search', found: false};
    """)
    print(f"Method 3 (span parent search): {json.dumps(result, indent=2)}")

    # Method 4: Look for ytcp-checkbox-lit or ytcp-checkbox-group
    result = driver.execute_script("""
        const ytcpCheckboxes = document.querySelectorAll('ytcp-checkbox-lit, ytcp-checkbox-group');
        const found = [];
        for (let el of ytcpCheckboxes) {
            if (el.offsetParent !== null) {
                found.push({
                    tag: el.tagName,
                    text: el.textContent.trim().substring(0, 50),
                    checked: el.hasAttribute('checked'),
                    class: el.className
                });
            }
        }
        return {method: 'ytcp-checkbox', found: found};
    """)
    print(f"Method 4 (ytcp-checkbox): {result}")

    # Method 5: Get full DOM tree of visible sub-dialog
    result = driver.execute_script("""
        // Find any element containing all visibility options
        const containers = document.querySelectorAll('*');
        for (let el of containers) {
            const text = el.textContent;
            if (el.offsetParent !== null &&
                text.includes('Public') &&
                text.includes('Private') &&
                text.includes('Unlisted') &&
                text.children && text.children.length < 50) {
                // This might be our container
                return {
                    method: 'container-search',
                    tag: el.tagName,
                    class: el.className,
                    id: el.id,
                    children: el.children.length,
                    innerHTML: el.innerHTML.substring(0, 1000)
                };
            }
        }
        return {method: 'container-search', found: false};
    """)
    print(f"Method 5 (container search): tag={result.get('tag')}, class={result.get('class')[:50] if result.get('class') else None}")
    if result.get('innerHTML'):
        print(f"  innerHTML preview: {result['innerHTML'][:300]}...")


def main():
    """Run the diagnostic."""
    print("\n" + "="*60)
    print("VISIBILITY SUB-DIALOG DOM DIAGNOSTIC")
    print("="*60 + "\n")

    driver = None
    try:
        driver = connect_edge()

        # Step 1: Click Filter input
        print("\n[STEP 1] Click Filter input...")
        if not click_filter_input(driver):
            print("[FAIL] Could not click Filter input")
            return
        time.sleep(1.5)

        # Step 2: Click Visibility
        print("\n[STEP 2] Click Visibility...")
        if not click_visibility(driver):
            print("[FAIL] Could not click Visibility")
            return
        time.sleep(1.5)

        # Step 3: Dump the sub-dialog DOM
        print("\n[STEP 3] Dumping sub-dialog DOM...")
        dump_visibility_dialog(driver)

        # Step 4: Try to find clickable Unlisted
        print("\n[STEP 4] Finding clickable Unlisted element...")
        find_clickable_unlisted(driver)

        print("\n" + "="*60)
        print("DIAGNOSTIC COMPLETE")
        print("="*60)

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
