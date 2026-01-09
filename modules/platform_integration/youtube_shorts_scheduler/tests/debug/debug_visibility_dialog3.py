"""
Debug script v3 - Simpler approach to find visibility sub-dialog.

Key finding from v2: Visibility is item index 9 (last item)
After clicking, NO new dropdowns/popups appear.

The sub-dialog might be:
1. Inline replacement in the same dropdown
2. A nested listbox within the Visibility item
3. Hidden until hover/focus
"""

import time
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

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


def open_filter_dropdown(driver):
    """Open the filter dropdown and return info."""
    print("\n[STEP 1] Opening Filter dropdown...")
    result = driver.execute_script("""
        const filterInput = document.querySelector("input[placeholder='Filter']");
        if (!filterInput) return {error: 'no filter input'};
        filterInput.click();
        filterInput.focus();
        return {clicked: true};
    """)
    print(f"  Filter click: {result}")
    time.sleep(1.5)
    return result.get('clicked', False)


def get_visibility_item_info(driver):
    """Get detailed info about the Visibility menu item."""
    print("\n[STEP 2] Analyzing Visibility menu item...")

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

        // Get all attributes
        const attrs = {};
        for (let attr of visibilityItem.attributes) {
            attrs[attr.name] = attr.value;
        }

        // Get children info
        const children = [];
        for (let child of visibilityItem.children) {
            children.push({
                tag: child.tagName,
                class: child.className ? String(child.className).substring(0, 50) : '',
                id: child.id || null
            });
        }

        // Look for nested listbox or dropdown
        const nestedListbox = visibilityItem.querySelector('tp-yt-paper-listbox');
        const nestedDropdown = visibilityItem.querySelector('tp-yt-iron-dropdown');
        const nestedDialog = visibilityItem.querySelector('[role="dialog"]');

        return {
            found: true,
            tag: visibilityItem.tagName,
            attributes: attrs,
            children: children,
            hasNestedListbox: !!nestedListbox,
            hasNestedDropdown: !!nestedDropdown,
            hasNestedDialog: !!nestedDialog,
            innerHTML: visibilityItem.innerHTML.substring(0, 500)
        };
    """)

    print(f"  Tag: {result.get('tag')}")
    print(f"  Attributes: {result.get('attributes')}")
    print(f"  Children: {result.get('children')}")
    print(f"  Has nested listbox: {result.get('hasNestedListbox')}")
    print(f"  Has nested dropdown: {result.get('hasNestedDropdown')}")
    print(f"  Has nested dialog: {result.get('hasNestedDialog')}")
    print(f"  innerHTML preview: {result.get('innerHTML', '')[:200]}...")

    return result


def hover_and_click_visibility(driver):
    """Hover over and click Visibility item, then check for changes."""
    print("\n[STEP 3] Hovering and clicking Visibility...")

    # First hover
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

        // Hover events
        visibilityItem.dispatchEvent(new MouseEvent('mouseenter', {bubbles: true}));
        visibilityItem.dispatchEvent(new MouseEvent('mouseover', {bubbles: true}));

        return {hovered: true};
    """)
    print(f"  Hover: {result}")
    time.sleep(0.5)

    # Check for any new visible elements after hover
    hover_result = driver.execute_script("""
        const visibleWithUnlisted = [];
        const allElements = document.querySelectorAll('*');
        for (let el of allElements) {
            if (el.offsetParent !== null &&
                el.textContent.includes('Unlisted') &&
                el.children.length < 100) {
                const rect = el.getBoundingClientRect();
                if (rect.width > 0 && rect.height > 0) {
                    visibleWithUnlisted.push({
                        tag: el.tagName,
                        text: el.textContent.substring(0, 100),
                        rect: {top: rect.top, left: rect.left, w: rect.width, h: rect.height}
                    });
                }
            }
        }
        return visibleWithUnlisted;
    """)
    print(f"  Elements with 'Unlisted' text after hover: {len(hover_result)}")
    for el in hover_result[:3]:
        print(f"    - <{el['tag']}> at ({el['rect']['top']}, {el['rect']['left']})")

    # Now click
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

        visibilityItem.click();
        return {clicked: true};
    """)
    print(f"  Click: {result}")
    time.sleep(2)

    return result


def check_dom_after_click(driver):
    """Check what's in the DOM after clicking Visibility."""
    print("\n[STEP 4] Checking DOM after Visibility click...")

    # Check for any dialog or popup
    result = driver.execute_script("""
        const findings = {
            dialogs: [],
            dropdowns: [],
            listboxes: [],
            elementsWithApply: [],
            elementsWithUnlisted: []
        };

        // Find dialogs
        const dialogs = document.querySelectorAll('ytcp-dialog, tp-yt-paper-dialog, [role="dialog"]');
        for (let d of dialogs) {
            if (d.offsetParent !== null) {
                findings.dialogs.push({
                    tag: d.tagName,
                    hasUnlisted: d.textContent.includes('Unlisted'),
                    hasApply: d.textContent.includes('Apply'),
                    text: d.textContent.substring(0, 150)
                });
            }
        }

        // Find dropdowns (opened)
        const dropdowns = document.querySelectorAll('tp-yt-iron-dropdown[opened], [opened]');
        for (let dd of dropdowns) {
            findings.dropdowns.push({
                tag: dd.tagName,
                hasUnlisted: dd.textContent.includes('Unlisted')
            });
        }

        // Find listboxes
        const listboxes = document.querySelectorAll('tp-yt-paper-listbox');
        for (let lb of listboxes) {
            if (lb.offsetParent !== null) {
                findings.listboxes.push({
                    items: lb.querySelectorAll('tp-yt-paper-item').length,
                    hasUnlisted: lb.textContent.includes('Unlisted'),
                    text: lb.textContent.substring(0, 150)
                });
            }
        }

        // Find any element containing both "Unlisted" and "Apply"
        const all = document.querySelectorAll('*');
        for (let el of all) {
            if (el.offsetParent !== null) {
                const text = el.textContent;
                if (text.includes('Apply') &&
                    text.includes('Unlisted') &&
                    el.children.length > 0 &&
                    el.children.length < 50) {
                    const rect = el.getBoundingClientRect();
                    findings.elementsWithApply.push({
                        tag: el.tagName,
                        id: el.id,
                        rect: {top: rect.top, left: rect.left, w: rect.width, h: rect.height}
                    });
                }
            }
        }

        return findings;
    """)

    print(f"  Visible dialogs: {len(result.get('dialogs', []))}")
    for d in result.get('dialogs', []):
        print(f"    - <{d['tag']}> hasUnlisted={d['hasUnlisted']} hasApply={d['hasApply']}")
        if d['hasUnlisted']:
            print(f"      Text: {d['text'][:100]}...")

    print(f"  Opened dropdowns: {len(result.get('dropdowns', []))}")
    print(f"  Visible listboxes: {len(result.get('listboxes', []))}")
    for lb in result.get('listboxes', []):
        print(f"    - {lb['items']} items, hasUnlisted={lb['hasUnlisted']}")
        if lb['hasUnlisted']:
            print(f"      Text: {lb['text'][:100]}...")

    print(f"  Elements with Apply+Unlisted: {len(result.get('elementsWithApply', []))}")
    for el in result.get('elementsWithApply', []):
        print(f"    - <{el['tag']}> id={el['id']} at top={el['rect']['top']}, left={el['rect']['left']}")

    return result


def search_all_checkboxes(driver):
    """Search for all checkbox elements that might be visibility options."""
    print("\n[STEP 5] Searching for checkbox elements...")

    result = driver.execute_script("""
        const checkboxes = [];

        // Method 1: ytcp-checkbox-lit
        const ytcpCheckboxes = document.querySelectorAll('ytcp-checkbox-lit');
        for (let cb of ytcpCheckboxes) {
            if (cb.offsetParent !== null) {
                const parent = cb.parentElement;
                const grandparent = parent ? parent.parentElement : null;
                const nearbyText = (parent ? parent.textContent : '') +
                                 (grandparent ? grandparent.textContent : '');

                // Is this near visibility text?
                if (nearbyText.includes('Public') ||
                    nearbyText.includes('Private') ||
                    nearbyText.includes('Unlisted')) {
                    const rect = cb.getBoundingClientRect();
                    checkboxes.push({
                        type: 'ytcp-checkbox-lit',
                        nearbyText: nearbyText.substring(0, 80),
                        rect: {top: rect.top, left: rect.left}
                    });
                }
            }
        }

        // Method 2: role="checkbox"
        const roleCheckboxes = document.querySelectorAll('[role="checkbox"]');
        for (let cb of roleCheckboxes) {
            if (cb.offsetParent !== null) {
                const parent = cb.parentElement;
                const text = parent ? parent.textContent : '';
                if (text.includes('Unlisted') || text.includes('Public') || text.includes('Private')) {
                    const rect = cb.getBoundingClientRect();
                    checkboxes.push({
                        type: 'role=checkbox',
                        nearbyText: text.substring(0, 80),
                        rect: {top: rect.top, left: rect.left}
                    });
                }
            }
        }

        return checkboxes;
    """)

    print(f"  Found {len(result)} visibility-related checkboxes:")
    for cb in result[:10]:
        print(f"    - {cb['type']} at ({cb['rect']['top']}, {cb['rect']['left']})")
        print(f"      Text: {cb['nearbyText'][:60]}...")

    return result


def try_keyboard_navigation(driver):
    """Try using keyboard to navigate the Visibility submenu."""
    print("\n[STEP 6] Trying keyboard navigation...")

    # Focus the filter input, then use arrow keys
    driver.execute_script("""
        const filterInput = document.querySelector("input[placeholder='Filter']");
        if (filterInput) filterInput.focus();
    """)
    time.sleep(0.5)

    # Press down arrow to navigate to Visibility (it's the 10th/last item)
    body = driver.find_element(By.TAG_NAME, "body")
    for i in range(10):
        body.send_keys(Keys.ARROW_DOWN)
        time.sleep(0.1)

    print("  Pressed DOWN 10 times to reach Visibility")
    time.sleep(0.5)

    # Press right arrow or Enter to expand submenu
    body.send_keys(Keys.ARROW_RIGHT)
    print("  Pressed RIGHT to expand submenu")
    time.sleep(1)

    # Check what's visible now
    result = driver.execute_script("""
        const visible = [];
        const all = document.querySelectorAll('*');
        for (let el of all) {
            if (el.offsetParent !== null &&
                el.textContent.includes('Unlisted') &&
                el.children.length === 0) {
                const rect = el.getBoundingClientRect();
                visible.push({
                    tag: el.tagName,
                    text: el.textContent.trim(),
                    rect: {top: rect.top, left: rect.left}
                });
            }
        }
        return visible;
    """)

    print(f"  Elements with 'Unlisted' text: {len(result)}")
    for el in result[:5]:
        print(f"    - <{el['tag']}> '{el['text']}' at ({el['rect']['top']}, {el['rect']['left']})")

    return result


def main():
    print("\n" + "="*60)
    print("VISIBILITY SUB-DIALOG DEBUG v3")
    print("="*60 + "\n")

    driver = None
    try:
        driver = connect_edge()
        navigate_to_shorts(driver)
        time.sleep(2)

        # Open filter dropdown
        if not open_filter_dropdown(driver):
            return

        # Get Visibility item info
        get_visibility_item_info(driver)

        # Hover and click Visibility
        hover_and_click_visibility(driver)

        # Check DOM after click
        check_dom_after_click(driver)

        # Search for checkboxes
        search_all_checkboxes(driver)

        # Try keyboard navigation
        # First, reopen filter dropdown
        print("\n[REOPEN] Reopening filter dropdown for keyboard test...")
        driver.execute_script("""
            document.body.click();  // Close any open dropdown
        """)
        time.sleep(1)
        open_filter_dropdown(driver)
        try_keyboard_navigation(driver)

        print("\n" + "="*60)
        print("DEBUG v3 COMPLETE")
        print("="*60)

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
