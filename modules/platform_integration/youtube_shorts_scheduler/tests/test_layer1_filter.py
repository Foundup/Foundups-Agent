"""
Layer 1 Test: Navigate to Shorts + Filter to Unlisted

Test the cake layer by layer:
1. Connect to Chrome debug session (9222)
2. Navigate to Shorts page
3. Click "Filter" button
4. Click "Visibility" in dropdown
5. Select "Unlisted" from visibility options

Modes:
  - Default (URL-based): Uses URL parameter for filter (most reliable)
  - --ui: Uses DOM selectors to click UI elements
  - --uitars: Uses UI-TARS vision model for visual verification

Run: python -m modules.platform_integration.youtube_shorts_scheduler.tests.test_layer1_filter
     python -m modules.platform_integration.youtube_shorts_scheduler.tests.test_layer1_filter --ui
     python -m modules.platform_integration.youtube_shorts_scheduler.tests.test_layer1_filter --uitars
"""

import time
import asyncio
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Move2Japan channel
CHANNEL_ID = "UC-LSSlOZwpGIRIYihaz8zCw"
CHROME_PORT = 9222


def connect_chrome():
    """Connect to existing Chrome debug session."""
    logger.info(f"[LAYER 1] Connecting to Chrome on port {CHROME_PORT}...")
    options = Options()
    options.add_experimental_option("debuggerAddress", f"127.0.0.1:{CHROME_PORT}")
    driver = webdriver.Chrome(options=options)
    logger.info(f"[LAYER 1] Connected! Current URL: {driver.current_url[:60]}...")
    return driver


def navigate_to_shorts(driver, with_unlisted_filter: bool = False):
    """Navigate to Shorts page, optionally with unlisted filter via URL."""
    if with_unlisted_filter:
        # Navigate directly to unlisted filter via URL parameter
        # Based on YouTube Studio URL structure
        import json
        from urllib.parse import quote

        filter_obj = [{"name": "VISIBILITY", "value": ["UNLISTED"]}]
        filter_param = quote(json.dumps(filter_obj))
        url = f"https://studio.youtube.com/channel/{CHANNEL_ID}/videos/short?filter={filter_param}"
        logger.info(f"[LAYER 1] Navigating to unlisted-filtered URL...")
    else:
        url = f"https://studio.youtube.com/channel/{CHANNEL_ID}/videos/short"

    logger.info(f"[LAYER 1] URL: {url[:80]}...")
    driver.get(url)

    # Wait for video table to load (confirms page is ready)
    logger.info("[LAYER 1] Waiting for video table to load...")
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ytcp-video-row, table, .video-list"))
        )
        logger.info("[LAYER 1] Video table found!")
    except TimeoutException:
        logger.warning("[LAYER 1] Video table not found, continuing anyway...")

    time.sleep(3)  # Extra wait for dynamic content
    logger.info(f"[LAYER 1] Page loaded: {driver.title}")
    return True


def click_filter_button(driver):
    """Click the Filter input to open dropdown."""
    logger.info("[LAYER 1] Looking for Filter input...")

    # Based on user's DOM analysis:
    # input#text-input with placeholder="Filter"
    # Located in: ytcp-chip-bar#chip-bar > input#text-input

    # Method 1: Direct CSS selector (RECOMMENDED)
    selectors = [
        "input#text-input[placeholder='Filter']",
        "input[placeholder='Filter']",
        "ytcp-chip-bar input#text-input",
        "#text-input[placeholder='Filter']",
    ]

    for sel in selectors:
        try:
            logger.info(f"  Trying: {sel}")
            elem = driver.find_element(By.CSS_SELECTOR, sel)
            if elem.is_displayed():
                logger.info(f"  FOUND! Clicking...")
                elem.click()
                time.sleep(1)
                logger.info("[LAYER 1] Filter input clicked!")
                return True
        except Exception as e:
            logger.info(f"    Not found: {e}")

    # Method 2: JavaScript click
    logger.info("  Trying JavaScript...")
    try:
        clicked = driver.execute_script("""
            const filterInput = document.querySelector("input[placeholder='Filter']");
            if (filterInput && filterInput.offsetParent !== null) {
                filterInput.click();
                filterInput.focus();
                return 'clicked';
            }
            return 'not found';
        """)
        logger.info(f"  JS result: {clicked}")
        if clicked == 'clicked':
            time.sleep(1)
            return True
    except Exception as e:
        logger.info(f"  JS failed: {e}")

    # CSS selectors to try first (faster than XPath)
    css_selectors = [
        "#filter",  # Direct ID
        "#filter button",
        "#filter ytcp-button",
        "ytcp-video-section-filter",
        "ytcp-video-section-filter button",
        "[id='filter'] button",
    ]

    for selector in css_selectors:
        try:
            logger.info(f"  Trying CSS: {selector}...")
            elems = driver.find_elements(By.CSS_SELECTOR, selector)
            if elems:
                logger.info(f"    Found {len(elems)} elements")
                for i, elem in enumerate(elems):
                    is_vis = elem.is_displayed()
                    logger.info(f"    Element {i} visible={is_vis}")
                    # Try clicking even if not displayed (might be in shadow DOM)
                    try:
                        if is_vis:
                            elem.click()
                        else:
                            driver.execute_script("arguments[0].click();", elem)
                        time.sleep(1)
                        # Check if dropdown opened (look for new elements)
                        dropdowns = driver.find_elements(By.CSS_SELECTOR, "tp-yt-paper-listbox, ytcp-dropdown-menu, [role='listbox']")
                        if dropdowns:
                            logger.info("[LAYER 1] Filter dropdown opened!")
                            return True
                        logger.info("    Click didn't open dropdown, trying next...")
                    except Exception as e:
                        logger.info(f"    Click failed: {e}")
        except Exception as e:
            logger.info(f"    Error: {e}")

    # Try finding filter button by looking at classes with 'filter'
    logger.info("  Trying buttons with 'filter' in class...")
    buttons = driver.find_elements(By.XPATH, "//button[contains(@class, 'filter')]")
    logger.info(f"    Found {len(buttons)} filter-class buttons")
    for i, btn in enumerate(buttons):
        # Inspect each button first
        aria = btn.get_attribute("aria-label") or ""
        cls = btn.get_attribute("class") or ""
        is_vis = btn.is_displayed()
        txt = btn.text[:20] if btn.text else ""
        logger.info(f"    Button {i}: vis={is_vis} aria='{aria}' text='{txt}' class={cls[:50]}")

        # Only click visible buttons
        if is_vis:
            try:
                logger.info(f"    Clicking button {i}...")
                driver.execute_script("arguments[0].click();", btn)
                time.sleep(1.5)  # Wait for dropdown animation

                # Check for filter menu specifically
                filter_menus = driver.find_elements(By.CSS_SELECTOR, "ytcp-video-section-filter tp-yt-paper-item")
                if filter_menus:
                    logger.info(f"[LAYER 1] Found {len(filter_menus)} filter menu items!")
                    return True

                # Also check for any new visible dropdowns
                dropdowns = driver.find_elements(By.CSS_SELECTOR, "tp-yt-paper-listbox[role='listbox'], tp-yt-iron-dropdown")
                visible_dds = [d for d in dropdowns if d.is_displayed()]
                if visible_dds:
                    logger.info(f"[LAYER 1] Found {len(visible_dds)} visible dropdowns!")
                    return True

            except Exception as e:
                logger.info(f"    Failed: {e}")

    # XPath selectors as fallback
    xpath_selectors = [
        # YouTube custom button with Filter text
        "//ytcp-button[.//div[contains(text(), 'Filter')]]",
        "//ytcp-button[contains(., 'Filter')]",
        # Standard button approaches
        "//button[contains(., 'Filter')]",
        "//button[@aria-label='Filter']",
        # Dropdown triggers
        "//ytcp-text-dropdown-trigger[contains(., 'Filter')]",
        "//ytcp-dropdown-trigger[contains(., 'Filter')]",
        # Icon button with filter
        "//ytcp-icon-button[@aria-label='Filter']",
        # Class-based
        "//*[contains(@class, 'filter-button')]",
        # Any element with Filter text that's clickable
        "//*[normalize-space(text())='Filter']",
        "//span[text()='Filter']/ancestor::button",
        "//span[text()='Filter']/ancestor::ytcp-button",
    ]

    for selector in xpath_selectors:
        try:
            logger.info(f"  Trying XPath: {selector[:50]}...")
            elem = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, selector))
            )
            logger.info(f"  FOUND! Clicking...")
            elem.click()
            time.sleep(1)
            logger.info("[LAYER 1] Filter button clicked!")
            return True
        except (TimeoutException, NoSuchElementException):
            continue

    logger.error("[LAYER 1] Could not find Filter button")
    return False


def click_visibility_option(driver):
    """Click Visibility in the filter dropdown.

    Based on user's DOM analysis:
    - Visibility is the LAST (10th) item in the listbox
    - Element tag is 'generic' with text 'Visibility'
    - XPath: //generic[text()='Visibility']
    """
    logger.info("[LAYER 1] Looking for Visibility option in dropdown...")

    # Method 1: Use JavaScript to find and click the last item (Visibility)
    # Based on user's analysis: Visibility is the 10th/last item
    try:
        result = driver.execute_script("""
            // Find the dropdown listbox
            const listbox = document.querySelector('tp-yt-paper-listbox[role="listbox"]');
            if (!listbox) return {found: false, error: 'no listbox'};

            // Get all items in the listbox
            const items = listbox.querySelectorAll('tp-yt-paper-item');
            console.log('Found ' + items.length + ' items in listbox');

            // Visibility is the last item (10th)
            for (let i = 0; i < items.length; i++) {
                const text = items[i].textContent.trim();
                console.log('Item ' + i + ': ' + text);
                if (text.toLowerCase().includes('visibility')) {
                    items[i].click();
                    return {found: true, index: i, text: text};
                }
            }

            // Fallback: click the last item if it exists
            if (items.length > 0) {
                const lastItem = items[items.length - 1];
                const lastText = lastItem.textContent.trim();
                return {found: false, lastItem: lastText, count: items.length};
            }

            return {found: false, count: 0};
        """)
        logger.info(f"  JS listbox search result: {result}")
        if result and result.get('found'):
            logger.info(f"[LAYER 1] Visibility clicked at index {result.get('index')}!")
            time.sleep(1)
            return True
    except Exception as e:
        logger.info(f"  JS listbox search failed: {e}")

    # Method 2: Look for 'generic' element with Visibility text (user's XPath)
    try:
        logger.info("  Trying //generic[text()='Visibility']...")
        elem = driver.find_element(By.XPATH, "//generic[text()='Visibility']")
        if elem.is_displayed():
            elem.click()
            time.sleep(1)
            logger.info("[LAYER 1] Visibility clicked via generic element!")
            return True
    except Exception as e:
        logger.info(f"  generic element not found: {e}")

    # Method 3: Search all visible text for "Visibility"
    try:
        result = driver.execute_script("""
            // Search for any visible element containing "Visibility"
            const allElements = document.querySelectorAll('*');
            for (let el of allElements) {
                if (el.offsetParent !== null &&
                    el.textContent.trim() === 'Visibility' &&
                    el.children.length === 0) {
                    // Found a leaf element with just "Visibility" text
                    el.click();
                    return {clicked: true, tag: el.tagName};
                }
            }
            return {clicked: false};
        """)
        logger.info(f"  Deep text search result: {result}")
        if result and result.get('clicked'):
            time.sleep(1)
            return True
    except Exception as e:
        logger.info(f"  Deep search failed: {e}")

    # Method 4: Traditional XPath selectors
    selectors = [
        "//tp-yt-paper-item[contains(., 'Visibility')]",
        "//ytcp-ve[contains(., 'Visibility')]",
        "//*[normalize-space(text())='Visibility']",
        "//span[text()='Visibility']",
        "//div[text()='Visibility']",
    ]

    for selector in selectors:
        try:
            logger.info(f"  Trying XPath: {selector}...")
            elem = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, selector))
            )
            elem.click()
            time.sleep(1)
            logger.info("[LAYER 1] Visibility option clicked!")
            return True
        except (TimeoutException, NoSuchElementException):
            continue

    logger.error("[LAYER 1] Could not find Visibility option")
    return False


def click_unlisted(driver):
    """Select Unlisted from visibility sub-dialog.

    Based on user's DOM analysis:
    - Visibility opens a sub-dialog with checkboxes
    - Unlisted is the 3rd checkbox (index 2)
    - Checkboxes are tp-yt-paper-checkbox elements
    """
    logger.info("[LAYER 1] Looking for Unlisted checkbox...")

    # First, debug what's visible on screen
    try:
        debug_result = driver.execute_script("""
            const result = {
                checkboxes: [],
                listboxes: [],
                dialogs: [],
                paperItems: [],
                anyUnlisted: []
            };

            // Find checkboxes
            const checkboxes = document.querySelectorAll('tp-yt-paper-checkbox, input[type="checkbox"], [role="checkbox"]');
            for (let cb of checkboxes) {
                if (cb.offsetParent !== null) {
                    result.checkboxes.push({
                        tag: cb.tagName,
                        text: cb.textContent.trim().substring(0, 40),
                        role: cb.getAttribute('role')
                    });
                }
            }

            // Find listboxes
            const listboxes = document.querySelectorAll('[role="listbox"], tp-yt-paper-listbox');
            for (let lb of listboxes) {
                if (lb.offsetParent !== null) {
                    result.listboxes.push({
                        tag: lb.tagName,
                        text: lb.textContent.trim().substring(0, 100)
                    });
                }
            }

            // Find dialogs
            const dialogs = document.querySelectorAll('[role="dialog"], tp-yt-paper-dialog, tp-yt-iron-dropdown');
            for (let d of dialogs) {
                if (d.offsetParent !== null) {
                    result.dialogs.push({
                        tag: d.tagName,
                        text: d.textContent.trim().substring(0, 100)
                    });
                }
            }

            // Find paper items
            const paperItems = document.querySelectorAll('tp-yt-paper-item');
            for (let pi of paperItems) {
                if (pi.offsetParent !== null) {
                    result.paperItems.push(pi.textContent.trim().substring(0, 40));
                }
            }

            // Search for anything with "Unlisted" text
            const allElements = document.querySelectorAll('*');
            for (let el of allElements) {
                if (el.offsetParent !== null &&
                    el.textContent.includes('Unlisted') &&
                    el.children.length === 0) {
                    result.anyUnlisted.push({
                        tag: el.tagName,
                        text: el.textContent.trim().substring(0, 40)
                    });
                }
            }

            return result;
        """)
        logger.info(f"  Debug - Checkboxes: {debug_result.get('checkboxes', [])}")
        logger.info(f"  Debug - Listboxes: {debug_result.get('listboxes', [])[:3]}")
        logger.info(f"  Debug - Dialogs: {debug_result.get('dialogs', [])[:3]}")
        logger.info(f"  Debug - Paper items: {debug_result.get('paperItems', [])[:10]}")
        logger.info(f"  Debug - Unlisted matches: {debug_result.get('anyUnlisted', [])}")
    except Exception as e:
        logger.info(f"  Debug failed: {e}")

    # Method 1: Click SPAN element with "Unlisted" text (found by debug)
    # The checkboxes are DIV[role=checkbox] with no text, labels are separate SPANs
    try:
        result = driver.execute_script("""
            // Find SPAN elements with "Unlisted" text and click the first visible one
            const spans = document.querySelectorAll('span');
            for (let span of spans) {
                if (span.offsetParent !== null &&
                    span.textContent.trim() === 'Unlisted') {
                    // Click the span or its parent (which might be a label/checkbox wrapper)
                    span.click();
                    return {clicked: true, method: 'span', text: span.textContent.trim()};
                }
            }

            // Fallback: find the parent container and click the checkbox
            const allElements = document.querySelectorAll('*');
            for (let el of allElements) {
                if (el.offsetParent !== null &&
                    el.textContent.includes('Unlisted') &&
                    !el.textContent.includes('Public') &&
                    el.textContent.length < 100) {
                    // This might be a label container - look for checkbox inside or nearby
                    const checkbox = el.querySelector('[role="checkbox"]') ||
                                   el.closest('[role="checkbox"]') ||
                                   el.parentElement.querySelector('[role="checkbox"]');
                    if (checkbox) {
                        checkbox.click();
                        return {clicked: true, method: 'checkbox-in-parent', tag: el.tagName};
                    }
                    // Just click the element itself
                    el.click();
                    return {clicked: true, method: 'element', tag: el.tagName};
                }
            }

            return {clicked: false};
        """)
        logger.info(f"  JS checkbox result: {result}")
        if result and result.get('clicked'):
            logger.info(f"[LAYER 1] Unlisted clicked at index {result.get('index')}!")
            time.sleep(0.5)
            return True
    except Exception as e:
        logger.info(f"  JS checkbox search failed: {e}")

    # Method 2: XPath selectors
    selectors = [
        "//tp-yt-paper-checkbox[contains(., 'Unlisted')]",
        "//tp-yt-paper-checkbox[contains(., 'unlisted')]",
        "//tp-yt-paper-item[contains(., 'Unlisted')]",
        "//*[contains(text(), 'Unlisted')][@role='checkbox']",
        "//label[contains(., 'Unlisted')]",
    ]

    for selector in selectors:
        try:
            logger.info(f"  Trying: {selector[:50]}...")
            elem = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, selector))
            )
            elem.click()
            time.sleep(0.5)
            logger.info("[LAYER 1] Unlisted selected!")
            return True
        except (TimeoutException, NoSuchElementException):
            continue

    logger.error("[LAYER 1] Could not find Unlisted checkbox")
    return False


def click_apply_button(driver):
    """Click the Apply button to apply the filter.

    Based on user's DOM analysis:
    - Apply button XPath: //button[contains(.,'Apply')]
    """
    logger.info("[LAYER 1] Looking for Apply button...")

    # First, debug what buttons are visible
    try:
        debug_result = driver.execute_script("""
            const result = {
                buttons: [],
                ytcpButtons: [],
                anyApply: []
            };

            // Find all visible buttons
            const buttons = document.querySelectorAll('button');
            for (let btn of buttons) {
                if (btn.offsetParent !== null) {
                    result.buttons.push({
                        text: btn.textContent.trim().substring(0, 30),
                        aria: btn.getAttribute('aria-label') || ''
                    });
                }
            }

            // Find all visible ytcp-button elements
            const ytcpButtons = document.querySelectorAll('ytcp-button');
            for (let btn of ytcpButtons) {
                if (btn.offsetParent !== null) {
                    result.ytcpButtons.push({
                        text: btn.textContent.trim().substring(0, 30),
                        aria: btn.getAttribute('aria-label') || ''
                    });
                }
            }

            // Search for anything with "Apply" text
            const allElements = document.querySelectorAll('*');
            for (let el of allElements) {
                if (el.offsetParent !== null &&
                    el.textContent.includes('Apply') &&
                    el.children.length === 0) {
                    result.anyApply.push({
                        tag: el.tagName,
                        text: el.textContent.trim().substring(0, 30)
                    });
                }
            }

            return result;
        """)
        logger.info(f"  Debug - Buttons: {debug_result.get('buttons', [])[:10]}")
        logger.info(f"  Debug - ytcp-buttons: {debug_result.get('ytcpButtons', [])[:10]}")
        logger.info(f"  Debug - Apply matches: {debug_result.get('anyApply', [])}")
    except Exception as e:
        logger.info(f"  Debug failed: {e}")

    # Method 1: JavaScript search - look within the visibility filter dialog
    try:
        result = driver.execute_script("""
            // Look for Apply button - specifically in the visibility filter dialog
            // The dialog appears to be a tp-yt-paper-dialog or similar container

            // First try finding buttons with exact "Apply" text
            const allButtons = document.querySelectorAll('button, ytcp-button, tp-yt-paper-button');
            for (let btn of allButtons) {
                const text = btn.textContent.trim();
                if (text === 'Apply' && btn.offsetParent !== null) {
                    btn.click();
                    return {clicked: true, text: text, method: 'exact-match'};
                }
            }

            // Look for Apply within any open dialog/dropdown
            const dialogs = document.querySelectorAll('tp-yt-paper-dialog, tp-yt-iron-dropdown, [role="dialog"]');
            for (let dialog of dialogs) {
                if (dialog.offsetParent !== null) {
                    const buttons = dialog.querySelectorAll('button, ytcp-button');
                    for (let btn of buttons) {
                        const text = btn.textContent.trim().toLowerCase();
                        if (text.includes('apply') && btn.offsetParent !== null) {
                            btn.click();
                            return {clicked: true, text: btn.textContent.trim(), method: 'dialog-search'};
                        }
                    }
                }
            }

            // Fallback: any visible button with apply/done/ok
            for (let btn of allButtons) {
                const text = btn.textContent.trim().toLowerCase();
                const aria = (btn.getAttribute('aria-label') || '').toLowerCase();
                if ((text.includes('apply') || aria.includes('apply') ||
                     text === 'done' || text === 'ok' || text === 'submit') &&
                    btn.offsetParent !== null) {
                    btn.click();
                    return {clicked: true, text: btn.textContent.trim(), method: 'fallback'};
                }
            }
            return {clicked: false};
        """)
        logger.info(f"  JS Apply search result: {result}")
        if result and result.get('clicked'):
            logger.info("[LAYER 1] Apply button clicked!")
            time.sleep(1)
            return True
    except Exception as e:
        logger.info(f"  JS search failed: {e}")

    # Method 2: XPath
    selectors = [
        "//button[contains(.,'Apply')]",
        "//ytcp-button[contains(.,'Apply')]",
        "//button[text()='Apply']",
        "//*[@aria-label='Apply']",
    ]

    for selector in selectors:
        try:
            logger.info(f"  Trying: {selector}...")
            elem = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, selector))
            )
            elem.click()
            time.sleep(1)
            logger.info("[LAYER 1] Apply button clicked!")
            return True
        except (TimeoutException, NoSuchElementException):
            continue

    logger.error("[LAYER 1] Could not find Apply button")
    return False


def dump_page_text(driver):
    """Dump visible page text to find Filter button text."""
    logger.info("[DEBUG] Dumping page text to find 'Filter'...")

    # Get all visible text on page
    body = driver.find_element(By.TAG_NAME, "body")
    page_text = body.text

    # Look for filter-related text
    lines = page_text.split('\n')
    for i, line in enumerate(lines):
        if 'filter' in line.lower() or 'Filter' in line:
            logger.info(f"  Line {i}: '{line[:80]}'")

    # Also search for common filter-area elements
    logger.info("[DEBUG] Looking for filter-area elements...")

    # Look for the toolbar/filter row area
    toolbar_selectors = [
        "#filter-container",
        ".filter-row",
        "#filter",
        "[class*='filter']",
        "ytcp-animatable-controls-row",
        ".top-row-controls",
    ]

    for sel in toolbar_selectors:
        try:
            elems = driver.find_elements(By.CSS_SELECTOR, sel)
            if elems:
                logger.info(f"  Found {len(elems)} elements matching '{sel}'")
                for elem in elems[:2]:
                    text = elem.text[:100] if elem.text else "(no text)"
                    html = elem.get_attribute("innerHTML")[:200] if elem.get_attribute("innerHTML") else ""
                    logger.info(f"    Text: '{text}'")
                    if "Filter" in html or "filter" in html:
                        logger.info(f"    HTML contains 'filter'!")
        except Exception:
            pass


def inspect_page_elements(driver):
    """Debug helper - inspect what elements are on page."""
    logger.info("[DEBUG] Inspecting page elements...")

    # Look for buttons
    buttons = driver.find_elements(By.TAG_NAME, "button")
    logger.info(f"  Found {len(buttons)} buttons")
    for i, btn in enumerate(buttons[:15]):
        text = btn.text[:30] if btn.text else "(no text)"
        aria = btn.get_attribute("aria-label") or "(no aria)"
        cls = btn.get_attribute("class") or ""
        logger.info(f"    [{i}] '{text}' | aria: '{aria}' | class: {cls[:40]}")

    # Look for dropdowns
    dropdowns = driver.find_elements(By.CSS_SELECTOR, "ytcp-text-dropdown-trigger, tp-yt-paper-dropdown-menu, ytcp-dropdown-trigger")
    logger.info(f"  Found {len(dropdowns)} dropdown triggers")
    for i, dd in enumerate(dropdowns[:10]):
        text = dd.text[:40] if dd.text else "(no text)"
        logger.info(f"    [{i}] '{text}'")

    # Look for anything with "filter" in text or class
    logger.info("  Looking for 'filter' anywhere...")
    filter_elems = driver.find_elements(By.XPATH, "//*[contains(translate(text(), 'FILTER', 'filter'), 'filter') or contains(@class, 'filter') or contains(@id, 'filter')]")
    logger.info(f"  Found {len(filter_elems)} elements with 'filter'")
    for i, elem in enumerate(filter_elems[:10]):
        tag = elem.tag_name
        text = elem.text[:30] if elem.text else "(no text)"
        cls = elem.get_attribute("class") or ""
        logger.info(f"    [{i}] <{tag}> '{text}' class: {cls[:40]}")

    # Look for ytcp-button elements (YouTube custom buttons)
    logger.info("  Looking for ytcp-button elements...")
    ytcp_buttons = driver.find_elements(By.TAG_NAME, "ytcp-button")
    logger.info(f"  Found {len(ytcp_buttons)} ytcp-button elements")
    for i, btn in enumerate(ytcp_buttons[:10]):
        text = btn.text[:30] if btn.text else "(no text)"
        logger.info(f"    [{i}] '{text}'")


def test_ui_filter(driver):
    """Test the UI-based filter approach (clicking Filter -> Visibility -> Unlisted -> Apply)."""
    print("\n--- UI-BASED FILTER TEST ---\n")

    # Step 1: Navigate to Shorts page (no filter)
    if not navigate_to_shorts(driver, with_unlisted_filter=False):
        print("[FAIL] Navigation failed\n")
        return False

    print("[OK] On Shorts page\n")
    time.sleep(2)

    # Step 2: Click Filter input to open dropdown
    print("[STEP 2] Clicking Filter input...")
    if not click_filter_button(driver):
        print("[FAIL] Could not click Filter input\n")
        return False
    print("[OK] Filter dropdown opened\n")
    time.sleep(1)

    # Step 3: Click Visibility option
    print("[STEP 3] Clicking Visibility option...")
    if not click_visibility_option(driver):
        print("[FAIL] Could not click Visibility\n")
        return False
    print("[OK] Visibility sub-dialog opened\n")
    time.sleep(1)

    # Step 4: Click Unlisted checkbox
    print("[STEP 4] Clicking Unlisted checkbox...")
    if not click_unlisted(driver):
        print("[FAIL] Could not click Unlisted\n")
        return False
    print("[OK] Unlisted selected\n")
    time.sleep(1)

    # Step 5: Try to click Apply button (may not exist in new YouTube Studio UI)
    print("[STEP 5] Looking for Apply button...")
    apply_clicked = click_apply_button(driver)
    if apply_clicked:
        print("[OK] Apply button clicked\n")
    else:
        print("[INFO] No Apply button - filter may auto-apply on selection\n")

    # Wait for filter to be applied (either via Apply button or auto-apply)
    time.sleep(2)

    # Step 6: Close any remaining dropdowns by clicking elsewhere
    print("[STEP 6] Closing dropdowns...")
    try:
        from selenium.webdriver.common.keys import Keys
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
        time.sleep(1)
    except Exception:
        pass

    # Verify results
    video_rows = driver.find_elements(By.CSS_SELECTOR, "ytcp-video-row")
    print(f"[RESULT] Found {len(video_rows)} video rows after filter\n")

    return True


async def test_uitars_filter(driver):
    """
    Test UI-TARS vision-based filter approach.

    Uses the UI-TARS 1.5 7B vision model (via LM Studio) to:
    1. Find and click the Filter input
    2. Find and click "Visibility" option
    3. Find and click "Unlisted" checkbox
    4. Find and click "Apply" button (if visible)

    This is more robust than DOM selectors for complex YouTube Studio dialogs.
    """
    print("\n--- UI-TARS VISION FILTER TEST ---\n")

    try:
        from modules.infrastructure.foundups_vision.src.ui_tars_bridge import UITarsBridge
    except ImportError as e:
        print(f"[FAIL] Could not import UITarsBridge: {e}")
        print("       Make sure foundups_vision module is available")
        return False

    # Create UI-TARS bridge
    bridge = UITarsBridge(browser_port=CHROME_PORT)

    try:
        # Connect to UI-TARS (checks LM Studio availability)
        print("[STEP 0] Connecting to UI-TARS (LM Studio)...")
        await bridge.connect()
        print("[OK] UI-TARS connected\n")
    except Exception as e:
        print(f"[WARN] UI-TARS connection warning: {e}")
        print("       Make sure LM Studio is running with ui-tars-1.5-7b model")
        print("       Continuing anyway...\n")

    # Step 1: Navigate to Shorts page (no filter)
    if not navigate_to_shorts(driver, with_unlisted_filter=False):
        print("[FAIL] Navigation failed\n")
        return False
    print("[OK] On Shorts page\n")
    time.sleep(2)

    # Step 2: Click Filter input using UI-TARS vision
    print("[STEP 2] Finding Filter input with UI-TARS...")
    result = await bridge.execute_action(
        action="click",
        description="Filter input field in the toolbar at the top of the video list",
        driver=driver,
        timeout=120  # Allow time for 7B model inference
    )

    if result.success:
        print(f"[OK] Filter input clicked (confidence: {result.confidence:.2f})")
        if result.metadata.get("thought"):
            print(f"     Model thought: {result.metadata['thought'][:80]}...")
    else:
        print(f"[WARN] UI-TARS couldn't find Filter: {result.error}")
        print("       Falling back to DOM selector...")
        if not click_filter_button(driver):
            print("[FAIL] Could not click Filter input\n")
            return False

    print("[OK] Filter dropdown should be open\n")
    time.sleep(1.5)

    # Step 3: Click Visibility option using UI-TARS
    print("[STEP 3] Finding Visibility option with UI-TARS...")
    result = await bridge.execute_action(
        action="click",
        description="Visibility option in the dropdown menu - it should be near the bottom of the list",
        driver=driver,
        timeout=120
    )

    if result.success:
        print(f"[OK] Visibility clicked (confidence: {result.confidence:.2f})")
        if result.metadata.get("thought"):
            print(f"     Model thought: {result.metadata['thought'][:80]}...")
    else:
        print(f"[WARN] UI-TARS couldn't find Visibility: {result.error}")
        print("       Falling back to DOM selector...")
        if not click_visibility_option(driver):
            print("[FAIL] Could not click Visibility\n")
            return False

    print("[OK] Visibility sub-dialog should be open\n")
    time.sleep(1.5)

    # Step 4: Click Unlisted checkbox using UI-TARS
    print("[STEP 4] Finding Unlisted checkbox with UI-TARS...")
    result = await bridge.execute_action(
        action="click",
        description="Unlisted checkbox or radio button in the visibility options dialog",
        driver=driver,
        timeout=120
    )

    if result.success:
        print(f"[OK] Unlisted clicked (confidence: {result.confidence:.2f})")
        if result.metadata.get("thought"):
            print(f"     Model thought: {result.metadata['thought'][:80]}...")
    else:
        print(f"[WARN] UI-TARS couldn't find Unlisted: {result.error}")
        print("       Falling back to DOM selector...")
        if not click_unlisted(driver):
            print("[FAIL] Could not click Unlisted\n")
            return False

    print("[OK] Unlisted selected\n")
    time.sleep(1)

    # Step 5: Try to click Apply button using UI-TARS
    print("[STEP 5] Looking for Apply button with UI-TARS...")
    result = await bridge.execute_action(
        action="click",
        description="Apply button at the bottom of the visibility filter dialog",
        driver=driver,
        timeout=120
    )

    if result.success:
        print(f"[OK] Apply button clicked (confidence: {result.confidence:.2f})")
        if result.metadata.get("thought"):
            print(f"     Model thought: {result.metadata['thought'][:80]}...")
    else:
        print(f"[INFO] Apply button not found or not visible: {result.error}")
        print("       Filter may auto-apply on selection\n")

    # Wait for filter to be applied
    time.sleep(2)

    # Step 6: Close any remaining dropdowns by pressing ESC
    print("[STEP 6] Closing dropdowns...")
    try:
        from selenium.webdriver.common.keys import Keys
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
        time.sleep(1)
    except Exception:
        pass

    # Verify results
    video_rows = driver.find_elements(By.CSS_SELECTOR, "ytcp-video-row")
    print(f"[RESULT] Found {len(video_rows)} video rows after filter\n")

    # Close bridge
    bridge.close()

    return True


def main():
    """Run Layer 1 test."""
    import sys

    print("\n" + "="*60)
    print("LAYER 1 TEST: Navigate + Filter to Unlisted")
    print("="*60 + "\n")

    # Check for flags
    use_ui = "--ui" in sys.argv
    use_uitars = "--uitars" in sys.argv
    use_fallback = "--fallback" in sys.argv

    # Handle fallback test separately (doesn't need driver setup here)
    if use_fallback:
        print("[MODE] URL-first with DOM fallback test (--fallback flag)\n")
        test_url_with_dom_fallback()
        return

    driver = None
    try:
        # Step 1: Connect
        driver = connect_chrome()
        print("[OK] Connected to Chrome\n")

        if use_uitars:
            # Test UI-TARS vision-based filter approach
            print("[MODE] UI-TARS vision filter test (--uitars flag)\n")
            success = asyncio.run(test_uitars_filter(driver))
            if success:
                print("="*60)
                print("LAYER 1 UI-TARS FILTER COMPLETE!")
                print("="*60)
            else:
                print("="*60)
                print("LAYER 1 UI-TARS FILTER INCOMPLETE - See errors above")
                print("="*60)
        elif use_ui:
            # Test UI-based filter approach
            print("[MODE] UI-based filter test (--ui flag)\n")
            success = test_ui_filter(driver)
            if success:
                print("="*60)
                print("LAYER 1 UI FILTER COMPLETE!")
                print("="*60)
            else:
                print("="*60)
                print("LAYER 1 UI FILTER INCOMPLETE - See errors above")
                print("="*60)
        else:
            # Default: URL-based filter approach (more reliable)
            print("[MODE] URL-based filter approach (use --ui for UI test)\n")

            if navigate_to_shorts(driver, with_unlisted_filter=True):
                print("[OK] Navigated to Shorts page with Unlisted filter\n")
            else:
                print("[FAIL] Navigation failed\n")
                return

            # Check if we have unlisted videos
            time.sleep(2)

            # Look for video rows
            video_rows = driver.find_elements(By.CSS_SELECTOR, "ytcp-video-row")
            logger.info(f"[LAYER 1] Found {len(video_rows)} video rows")

            if video_rows:
                print(f"[OK] Found {len(video_rows)} video rows\n")

                # Try to get first video's title
                for i, row in enumerate(video_rows[:3]):
                    try:
                        # Look for title link
                        links = row.find_elements(By.CSS_SELECTOR, "a[href*='/video/']")
                        if links:
                            title = links[0].text[:40] if links[0].text else "(no title)"
                            href = links[0].get_attribute("href")
                            logger.info(f"  Video {i}: {title} -> {href}")
                            print(f"  Video {i}: {title}")
                    except Exception as e:
                        logger.warning(f"  Video {i}: Error - {e}")

                print()

            print("="*60)
            print("LAYER 1 COMPLETE - Unlisted filter applied via URL!")
            print(f"Current URL: {driver.current_url[:80]}...")
            print("="*60)

    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

    # Don't close - leave browser open for inspection
    print("\n[INFO] Browser left open for inspection")


def test_url_with_dom_fallback():
    """
    Test the URL-first navigation with DOM fallback pattern.
    
    This tests the new navigate_to_shorts_with_fallback method in dom_automation.py.
    
    Run: python -m modules.platform_integration.youtube_shorts_scheduler.tests.test_layer1_filter --fallback
    """
    print("\n" + "="*60)
    print("TESTING URL-FIRST WITH DOM FALLBACK")
    print("="*60 + "\n")

    try:
        driver = connect_chrome()
        print("[OK] Connected to Chrome\n")

        # Import and use the new fallback method
        from modules.platform_integration.youtube_shorts_scheduler.src.dom_automation import YouTubeStudioDOM

        dom = YouTubeStudioDOM(driver)
        
        print("[STEP 1] Testing navigate_to_shorts_with_fallback...")
        success = dom.navigate_to_shorts_with_fallback(
            channel_id=CHANNEL_ID,
            visibility="UNLISTED"
        )

        if success:
            print("[OK] Visibility filter applied successfully!\n")
        else:
            print("[FAIL] Could not apply visibility filter\n")
            return False

        # Verify results
        print("[STEP 2] Verifying filtered results...")
        time.sleep(2)
        
        unlisted_videos = dom.get_unlisted_videos()
        print(f"[RESULT] Found {len(unlisted_videos)} unlisted videos\n")

        for i, video in enumerate(unlisted_videos[:5]):
            print(f"  {i+1}. {video['title'][:50]}...")

        print("\n" + "="*60)
        print("URL-FIRST WITH DOM FALLBACK TEST COMPLETE!")
        print(f"Current URL: {driver.current_url[:80]}...")
        print("="*60)

        return True

    except Exception as e:
        logger.error(f"Fallback test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    main()
