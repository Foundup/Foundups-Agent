"""
Debug script v2 - Focus on finding the Visibility sub-dialog within shadow DOM.

The issue: Clicking Visibility in the dropdown menu should open a sub-dialog
with checkboxes (Public, Private, Unlisted, etc.), but we're not finding it.

This script will:
1. Wait longer after clicking Visibility
2. Explore shadow DOM roots
3. Look for iron-dropdown popups
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
    print(f"[DEBUG] Connected! URL: {driver.current_url[:60]}...")
    return driver


def navigate_to_shorts(driver):
    """Navigate to Shorts page first."""
    url = "https://studio.youtube.com/channel/UC-LSSlOZwpGIRIYihaz8zCw/videos/short"
    print(f"[DEBUG] Navigating to {url[:60]}...")
    driver.get(url)
    time.sleep(3)
    print(f"[DEBUG] Page loaded: {driver.title}")


def click_filter_input(driver):
    """Click the Filter input to open dropdown."""
    print("[STEP 1] Clicking Filter input...")
    result = driver.execute_script("""
        const filterInput = document.querySelector("input[placeholder='Filter']");
        if (filterInput && filterInput.offsetParent !== null) {
            filterInput.click();
            filterInput.focus();
            return {clicked: true};
        }
        return {clicked: false, error: 'Filter input not found'};
    """)
    print(f"  Result: {result}")
    return result.get('clicked', False)


def dump_dropdown_state(driver):
    """Dump the state of any open dropdowns."""
    print("\n[DEBUG] Checking dropdown state...")
    result = driver.execute_script("""
        const state = {
            listboxes: [],
            ironDropdowns: [],
            openPopups: []
        };

        // Check tp-yt-paper-listbox
        const listboxes = document.querySelectorAll('tp-yt-paper-listbox');
        for (let lb of listboxes) {
            if (lb.offsetParent !== null) {
                state.listboxes.push({
                    items: lb.querySelectorAll('tp-yt-paper-item').length,
                    text: lb.textContent.substring(0, 200)
                });
            }
        }

        // Check iron-dropdown
        const dropdowns = document.querySelectorAll('tp-yt-iron-dropdown, iron-dropdown');
        for (let dd of dropdowns) {
            const style = getComputedStyle(dd);
            const opened = dd.hasAttribute('opened') || dd.opened;
            state.ironDropdowns.push({
                tag: dd.tagName,
                opened: opened,
                display: style.display,
                text: dd.textContent.substring(0, 200)
            });
        }

        // Check for any element with opened attribute
        const openedElements = document.querySelectorAll('[opened]');
        for (let el of openedElements) {
            state.openPopups.push({
                tag: el.tagName,
                class: el.className.substring(0, 50),
                text: el.textContent.substring(0, 100)
            });
        }

        return state;
    """)
    print(f"  Listboxes: {len(result.get('listboxes', []))}")
    for lb in result.get('listboxes', []):
        print(f"    - {lb['items']} items")
        items_preview = lb['text'].replace('\n', ' ')[:150]
        print(f"      Preview: {items_preview}...")

    print(f"  Iron dropdowns: {len(result.get('ironDropdowns', []))}")
    for dd in result.get('ironDropdowns', []):
        print(f"    - {dd['tag']} opened={dd['opened']} display={dd['display']}")

    print(f"  Open popups: {len(result.get('openPopups', []))}")
    return result


def click_visibility_and_wait(driver):
    """Click Visibility and wait for sub-dialog."""
    print("\n[STEP 2] Clicking Visibility...")

    # First, click Visibility
    result = driver.execute_script("""
        const listbox = document.querySelector('tp-yt-paper-listbox[role="listbox"]');
        if (!listbox) return {clicked: false, error: 'no listbox'};

        const items = listbox.querySelectorAll('tp-yt-paper-item');
        const itemTexts = [];
        let visibilityItem = null;

        for (let i = 0; i < items.length; i++) {
            const text = items[i].textContent.trim();
            itemTexts.push({index: i, text: text.substring(0, 30)});
            if (text.toLowerCase().includes('visibility')) {
                visibilityItem = items[i];
            }
        }

        if (visibilityItem) {
            visibilityItem.click();
            return {clicked: true, items: itemTexts};
        }
        return {clicked: false, items: itemTexts};
    """)
    print(f"  Dropdown items: {result.get('items', [])}")
    if result.get('clicked'):
        print("  Visibility clicked!")
    else:
        print("  [FAIL] Visibility not found in dropdown")
        return False

    # Wait for sub-dialog to appear
    print("  Waiting 2 seconds for sub-dialog...")
    time.sleep(2)
    return True


def explore_visibility_dialog(driver):
    """Deep exploration of visibility sub-dialog using shadow DOM traversal."""
    print("\n[STEP 3] Exploring visibility sub-dialog...")

    result = driver.execute_script("""
        const exploration = {
            filterDialogs: [],
            contentDialogs: [],
            shadowRoots: [],
            visibilityElements: []
        };

        // Function to search shadow DOM recursively
        function searchShadowDOM(root, depth = 0) {
            if (depth > 5) return;  // Limit depth

            const elements = root.querySelectorAll('*');
            for (let el of elements) {
                // Check for visibility-related text
                if (el.textContent.includes('Unlisted') ||
                    el.textContent.includes('Private') ||
                    el.textContent.includes('Members')) {
                    // Is this a container with visibility options?
                    if (el.textContent.includes('Public') &&
                        el.textContent.includes('Unlisted') &&
                        el.children.length > 0 &&
                        el.children.length < 30) {
                        exploration.visibilityElements.push({
                            tag: el.tagName,
                            class: el.className.substring(0, 50),
                            childCount: el.children.length,
                            depth: depth,
                            visible: el.offsetParent !== null,
                            rect: el.getBoundingClientRect()
                        });
                    }
                }

                // Check for filter dialogs
                if (el.tagName.includes('FILTER') ||
                    (el.className && el.className.includes('filter'))) {
                    exploration.filterDialogs.push({
                        tag: el.tagName,
                        class: el.className.substring(0, 50),
                        visible: el.offsetParent !== null
                    });
                }

                // Traverse shadow root if exists
                if (el.shadowRoot) {
                    exploration.shadowRoots.push({
                        tag: el.tagName,
                        depth: depth
                    });
                    searchShadowDOM(el.shadowRoot, depth + 1);
                }
            }
        }

        // Start from document
        searchShadowDOM(document);

        // Also specifically look for ytcp-video-section-filter-dialog
        const filterDialogEl = document.querySelector('ytcp-video-section-filter-dialog');
        if (filterDialogEl) {
            exploration.contentDialogs.push({
                tag: 'ytcp-video-section-filter-dialog',
                visible: filterDialogEl.offsetParent !== null,
                html: filterDialogEl.innerHTML.substring(0, 500)
            });
        }

        // Look for ytcp-video-section-content-dialog
        const contentDialogEl = document.querySelector('ytcp-video-section-content-dialog');
        if (contentDialogEl) {
            exploration.contentDialogs.push({
                tag: 'ytcp-video-section-content-dialog',
                visible: contentDialogEl.offsetParent !== null,
                html: contentDialogEl.innerHTML.substring(0, 500)
            });
        }

        return exploration;
    """)

    print(f"  Filter dialogs found: {len(result.get('filterDialogs', []))}")
    for fd in result.get('filterDialogs', []):
        print(f"    - <{fd['tag']}> class={fd['class']} visible={fd['visible']}")

    print(f"  Content dialogs found: {len(result.get('contentDialogs', []))}")
    for cd in result.get('contentDialogs', []):
        print(f"    - <{cd['tag']}> visible={cd['visible']}")
        if cd.get('html'):
            print(f"      HTML preview: {cd['html'][:200]}...")

    print(f"  Visibility elements found: {len(result.get('visibilityElements', []))}")
    for ve in result.get('visibilityElements', []):
        print(f"    - <{ve['tag']}> children={ve['childCount']} visible={ve['visible']} depth={ve['depth']}")

    print(f"  Shadow roots traversed: {len(result.get('shadowRoots', []))}")

    return result


def try_alternative_click(driver):
    """Try clicking Visibility differently - maybe it needs specific interaction."""
    print("\n[STEP 4] Trying alternative Visibility click...")

    # Try clicking and triggering events manually
    result = driver.execute_script("""
        const listbox = document.querySelector('tp-yt-paper-listbox[role="listbox"]');
        if (!listbox) return {error: 'no listbox'};

        const items = listbox.querySelectorAll('tp-yt-paper-item');

        // Find Visibility item
        let visibilityItem = null;
        for (let item of items) {
            if (item.textContent.trim().toLowerCase().includes('visibility')) {
                visibilityItem = item;
                break;
            }
        }

        if (!visibilityItem) return {error: 'visibility not found'};

        // Get info before click
        const beforeInfo = {
            tag: visibilityItem.tagName,
            hasPopup: visibilityItem.querySelector('tp-yt-iron-dropdown, [role="listbox"]') !== null,
            ariaExpanded: visibilityItem.getAttribute('aria-expanded'),
            ariaHasPopup: visibilityItem.getAttribute('aria-haspopup')
        };

        // Try different click methods
        // Method 1: Normal click
        visibilityItem.click();

        // Method 2: Dispatch click event
        visibilityItem.dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}));

        // Method 3: Focus and enter
        visibilityItem.focus();

        return {
            beforeClick: beforeInfo,
            afterAriaExpanded: visibilityItem.getAttribute('aria-expanded')
        };
    """)

    print(f"  Result: {result}")
    time.sleep(2)

    # Check if anything changed
    print("  Checking for new elements after click...")
    new_elements = driver.execute_script("""
        // Look for any newly visible elements with visibility options
        const visible = [];
        const allElements = document.querySelectorAll('*');
        for (let el of allElements) {
            if (el.offsetParent !== null) {
                const text = el.textContent;
                // Is this a container with exactly the visibility options?
                if (text.includes('Public') &&
                    text.includes('Private') &&
                    text.includes('Unlisted') &&
                    text.includes('Apply') &&
                    el.children.length > 0 &&
                    el.children.length < 50) {
                    const rect = el.getBoundingClientRect();
                    visible.push({
                        tag: el.tagName,
                        class: el.className.substring(0, 80),
                        id: el.id,
                        rect: {top: rect.top, left: rect.left, width: rect.width, height: rect.height}
                    });
                }
            }
        }
        return visible;
    """)

    print(f"  Found {len(new_elements)} potential visibility dialog containers:")
    for el in new_elements:
        print(f"    - <{el['tag']}> id={el['id']} class={el['class'][:50]}")
        print(f"      rect: top={el['rect']['top']}, left={el['rect']['left']}, w={el['rect']['width']}, h={el['rect']['height']}")

    return new_elements


def dump_all_paper_items(driver):
    """Dump ALL tp-yt-paper-item elements currently visible."""
    print("\n[STEP 5] Dumping all visible paper items...")

    result = driver.execute_script("""
        const items = [];
        const paperItems = document.querySelectorAll('tp-yt-paper-item');
        for (let item of paperItems) {
            if (item.offsetParent !== null) {
                const rect = item.getBoundingClientRect();
                items.push({
                    text: item.textContent.trim().substring(0, 50),
                    rect: {top: Math.round(rect.top), left: Math.round(rect.left)},
                    parent: item.parentElement ? item.parentElement.tagName : null,
                    hasNestedListbox: item.querySelector('tp-yt-paper-listbox') !== null
                });
            }
        }
        return items;
    """)

    print(f"  Found {len(result)} visible paper items:")
    for item in result:
        print(f"    - '{item['text'][:40]}' @ top={item['rect']['top']}, nested={item['hasNestedListbox']}")

    return result


def main():
    print("\n" + "="*60)
    print("VISIBILITY SUB-DIALOG DEBUG v2")
    print("="*60 + "\n")

    driver = None
    try:
        driver = connect_edge()

        # Navigate to shorts page first
        navigate_to_shorts(driver)
        time.sleep(2)

        # Click filter and check dropdown state
        if not click_filter_input(driver):
            print("[FAIL] Could not click Filter input")
            return
        time.sleep(1.5)

        # Dump current dropdown state
        dump_dropdown_state(driver)

        # Click Visibility
        if not click_visibility_and_wait(driver):
            return

        # Dump dropdown state again
        dump_dropdown_state(driver)

        # Deep exploration
        explore_visibility_dialog(driver)

        # Try alternative click
        try_alternative_click(driver)

        # Dump all paper items
        dump_all_paper_items(driver)

        print("\n" + "="*60)
        print("DEBUG COMPLETE")
        print("="*60)

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
