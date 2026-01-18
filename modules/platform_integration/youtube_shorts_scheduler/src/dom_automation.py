"""
DOM Automation Layer for YouTube Studio

Selenium/UI-TARS selectors and interaction methods for Shorts scheduling.
Based on live DOM inspection of YouTube Studio pages.
"""

import asyncio
import logging
import os
from typing import Optional, List, Dict, Any, Tuple
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)


class DOMSelectors:
    """
    Comprehensive DOM selectors for YouTube Studio.

    Page 1: Channel Content (Shorts List)
    Page 2: Video Details/Edit Page
    Page 3: Visibility/Scheduling Dialog
    """

    # =========================================
    # PAGE 1: SHORTS LIST
    # =========================================

    # Navigation
    SHORTS_TAB = "tab[aria-label='Shorts']"
    FILTER_INPUT = "input[placeholder='Filter']"

    # Video Table
    # Updated: Original selector doesn't match - use ytcp-video-row
    VIDEO_TABLE = "ytcp-video-row"  # Wait for at least one video row to appear
    VIDEO_ROWS = "ytcp-video-row"
    VIDEO_TITLE_LINK = "a[href*='/edit']"
    VIDEO_THUMBNAIL = "img[alt*='Video thumbnail']"

    # Pagination
    NEXT_PAGE_BTN = "button[aria-label='Navigate to the next page']"
    PREV_PAGE_BTN = "button[aria-label='Navigate to the previous page']"

    # XPath selectors for visibility filtering
    XPATH_UNLISTED_ROWS = "//ytcp-video-row[.//span[contains(text(),'Unlisted')]]"
    XPATH_SCHEDULED_ROWS = "//ytcp-video-row[.//span[contains(text(),'Scheduled')]]"
    XPATH_VIDEO_DATE_CELL = "//td[contains(text(),'202')]"  # Matches 2025, 2026, etc.

    # Filter UI selectors (DOM fallback - Layer 1)
    FILTER_ICON_COORDS = (170, 104)  # Hamburger icon + Filter area
    VISIBILITY_MENU_ITEM_XPATH = "//span[text()='Visibility']"
    UNLISTED_CHECKBOX_XPATH = "//span[text()='Unlisted']/ancestor::ytcp-checkbox-lit"
    APPLY_FILTER_BTN_XPATH = "//button[.//span[text()='Apply']]"
    # Filter chip is ytcp-chip element (discovered via diagnose_page.py)
    FILTER_CHIP_UNLISTED = "ytcp-chip"  # Check text content for "Visibility: Unlisted"
    FILTER_CHIP_ANY = "ytcp-chip"  # Any visibility chip

    # =========================================
    # LAYER 2: VIDEO EDIT PAGE SELECTORS
    # =========================================

    # Edit button on video row (hover to reveal)
    EDIT_BUTTON_COORDS = (232, 349)  # Pencil/details icon
    EDIT_BUTTON_SELECTOR = "a#anchor-video-details"
    EDIT_BUTTON_ICON = "ytcp-icon-button#video-details"

    # Title textbox on edit page
    TITLE_TEXTBOX_SELECTOR = "#title-textarea #textbox[contenteditable='true']"
    TITLE_TEXTBOX_XPATH = "//div[@id='textbox'][contains(@aria-label,'Add a title')]"

    # Description textbox on edit page
    DESC_TEXTBOX_SELECTOR = "#description-textarea #textbox[contenteditable='true']"
    DESC_TEXTBOX_XPATH = "//div[@id='textbox'][contains(@aria-label,'Tell viewers')]"

    # Save button
    SAVE_BUTTON = "button#save-button"
    SAVE_BUTTON_XPATH = "//ytcp-button[@id='save-button']"

    # =========================================
    # LAYER 3: SCHEDULING SELECTORS
    # Based on 0102 Scheduling Layer Stack
    # =========================================

    # L1: Visibility Dialog
    VISIBILITY_BUTTON = "button[aria-label*='visibility']"
    VISIBILITY_BUTTON_XPATH = "//button[contains(@aria-label,'Edit video visibility status')]"
    VISIBILITY_STATUS = "#visibility-status-span"

    # L1.1: Schedule Expand
    SCHEDULE_EXPAND_XPATH = "//div[contains(@class,'schedule')]//button[contains(@aria-label,'expand')]"
    SCHEDULE_RADIO_XPATH = "//tp-yt-paper-radio-button[@name='SCHEDULE']"

    # L2: Date
    DATE_DROPDOWN_XPATH = "//div[contains(@class,'date')]//ytcp-dropdown-trigger"
    DATE_INPUT_XPATH = "//input[contains(@aria-label,'Date')]"
    DATE_TEXT_XPATH = "//div[contains(@class,'date')]//span[@class='text']"
    # Current Studio variant: date is a left-container div inside datepicker-trigger
    DATE_TRIGGER_CSS = (
        "ytcp-visibility-scheduler ytcp-text-dropdown-trigger#datepicker-trigger "
        "ytcp-dropdown-trigger div.left-container"
    )
    # Date picker popup input (ytcp-date-picker dialog)
    DATE_PICKER_INPUT_CSS = "ytcp-date-picker tp-yt-paper-dialog#dialog input.tp-yt-paper-input"

    # L3: Time
    TIME_INPUT_XPATH = "//input[contains(@aria-label,'time') or contains(@placeholder,'time')]"
    TIME_TEXTBOX_XPATH = "//ytcp-form-input-container[contains(.,'Time')]//input"
    # Current Studio variant: time input lives under ytcp-datetime-picker form#form time-of-day-container
    TIME_OF_DAY_INPUT_CSS = (
        "ytcp-visibility-scheduler ytcp-datetime-picker form#form "
        "ytcp-form-input-container#time-of-day-container input.tp-yt-paper-input"
    )

    # L4: Done
    DONE_BUTTON_XPATH = "//button[.//span[text()='Done']]"
    DONE_BUTTON = "button#done-button"

    # =========================================
    # L5: RELATED VIDEO + SAVE + RETURN
    # =========================================

    # L5.1: Related Video Modal
    RELATED_VIDEO_SECTION = "ytcp-video-metadata-related-video"
    RELATED_VIDEO_BUTTON = "ytcp-dropdown-trigger#related-video-dropdown"
    RELATED_VIDEO_BUTTON_XPATH = "//ytcp-dropdown-trigger[@id='related-video-dropdown']"
    RELATED_VIDEO_MODAL = "ytcp-video-picker-dialog"
    RELATED_VIDEO_MODAL_XPATH = "//ytcp-video-picker-dialog"

    # L5.1 Search (for future use)
    RELATED_VIDEO_SEARCH_INPUT = "#video-picker-search-input"
    RELATED_VIDEO_SEARCH_XPATH = "//input[@id='video-picker-search-input']"
    RELATED_VIDEO_SEARCH_BTN = "button#video-picker-search-button"

    # L5.2: Video Grid (first = top-left)
    RELATED_VIDEO_GRID = "ytcp-video-picker-item"
    RELATED_VIDEO_FIRST_XPATH = "(//ytcp-video-picker-item)[1]"  # XPath index for first
    RELATED_VIDEO_THUMBNAIL = "ytcp-video-picker-item img.video-thumbnail"
    RELATED_VIDEO_FIRST_THUMBNAIL_XPATH = "(//ytcp-video-picker-item//img[contains(@class,'thumbnail')])[1]"

    # L5.3: Save (reuse existing SAVE_BUTTON)
    # SAVE_BUTTON already defined above

    # L5.4: Return to list
    BACK_BUTTON = "#back-button"
    BACK_BUTTON_XPATH = "//a[@id='back-button']"
    CHANNEL_CONTENT_LINK = "a[href*='/videos/short']"

    # L5.5: Refresh (handled via keyboard F5)

    # =========================================
    # PAGE 2: VIDEO EDIT PAGE
    # =========================================

    TITLE_INPUT = "textbox[placeholder*='Add a title']"
    TITLE_INPUT_XPATH = "//div[@id='textbox' and @aria-label='Add a title that describes your video (type @ to mention a channel)']"

    DESCRIPTION_INPUT = "textbox[placeholder*='Tell viewers']"
    DESCRIPTION_INPUT_XPATH = "//div[@id='textbox' and contains(@aria-label,'Tell viewers about your video')]"

    SAVE_BTN = "button#save-button"
    UNDO_BTN = "button#undo-button"

    VISIBILITY_BTN = "button[aria-label='Edit video visibility status']"
    VISIBILITY_BTN_XPATH = "//button[@aria-label='Edit video visibility status']"

    BACK_TO_LIST = "a[href*='/videos/short']"

    # Sidebar Navigation
    MENU_DETAILS = "a[href*='/edit']"
    MENU_ANALYTICS = "a[href*='/analytics']"
    MENU_MONETIZATION = "a[href*='/monetization']"
    MENU_COMMENTS = "a[href*='/comments']"

    # =========================================
    # PAGE 3: VISIBILITY/SCHEDULING DIALOG
    # =========================================

    VISIBILITY_DIALOG = "dialog[aria-label='Select video privacy']"
    VISIBILITY_DIALOG_XPATH = "//tp-yt-paper-dialog[contains(@aria-label,'visibility') or contains(@aria-label,'privacy')]"

    # Radio buttons
    RADIO_PRIVATE = "//tp-yt-paper-radio-button[.//span[text()='Private']]"
    RADIO_UNLISTED = "//tp-yt-paper-radio-button[.//span[text()='Unlisted']]"
    RADIO_PUBLIC = "//tp-yt-paper-radio-button[.//span[text()='Public']]"
    RADIO_SCHEDULE = "//tp-yt-paper-radio-button[.//span[contains(text(),'Schedule')]]"

    # Schedule section
    SCHEDULE_EXPAND = "//div[contains(text(),'Schedule')]//ancestor::button"
    SCHEDULE_RADIO = "//tp-yt-paper-radio-button[.//span[contains(text(),'private to public')]]"

    # Date/Time inputs
    DATE_PICKER_BTN = "//div[@id='datepicker-trigger']//button"
    DATE_INPUT = "//input[@aria-label='Date picker']"
    TIME_INPUT = "//input[contains(@aria-label,'Time')]"
    TIME_INPUT_TEXTBOX = "//tp-yt-paper-dialog//input[@type='text' and (contains(@value,'AM') or contains(@value,'PM'))]"

    # Dialog buttons
    DONE_BTN = "//button[.//span[text()='Done']]"
    CANCEL_BTN = "//button[.//span[text()='Cancel']]"
    SAVE_CLOSE_BTN = "//button[.//span[contains(text(),'Save')]]"


class YouTubeStudioDOM:
    """
    DOM interaction layer for YouTube Studio automation.
    """

    def __init__(self, driver):
        """
        Initialize with Selenium WebDriver.

        Args:
            driver: Selenium WebDriver instance (Chrome or Edge)
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.selectors = DOMSelectors()
        # 012 digital twin (Occam): slow + deterministic + stable.
        # No Bezier cursor paths, no jitter offsets, no mouse jumping.
        self._pre_click_delay = float(os.getenv("YT_SCHEDULER_PRE_CLICK_DELAY_SEC", "0.25"))
        self._post_click_delay = float(os.getenv("YT_SCHEDULER_POST_CLICK_DELAY_SEC", "0.25"))

    # =========================================
    # UTILITY METHODS
    # =========================================

    def wait_for_element(self, selector: str, by: str = By.CSS_SELECTOR, timeout: int = 10):
        """Wait for element to be present and visible."""
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.visibility_of_element_located((by, selector)))

    def wait_for_clickable(self, selector: str, by: str = By.CSS_SELECTOR, timeout: int = 10):
        """Wait for element to be clickable."""
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.element_to_be_clickable((by, selector)))

    def safe_click(self, element, use_js: bool = False):
        """
        012-modeled click (slow + deterministic) with robust fallbacks.

        Args:
            element: WebElement to click
            use_js: Force JavaScript click
        """
        import time
        try:
            if use_js:
                self.driver.execute_script("arguments[0].click();", element)
            else:
                try:
                    self.driver.execute_script(
                        "arguments[0].scrollIntoView({block:'center', inline:'center'});",
                        element,
                    )
                except Exception:
                    pass
                time.sleep(self._pre_click_delay)
                element.click()
                time.sleep(self._post_click_delay)
        except Exception:
            # Fallback order: ActionChains (often works on custom elements) -> JS click
            try:
                time.sleep(self._pre_click_delay)
                ActionChains(self.driver).move_to_element(element).click().perform()
                time.sleep(self._post_click_delay)
            except Exception:
                try:
                    self.driver.execute_script("arguments[0].click();", element)
                    time.sleep(self._post_click_delay)
                except Exception:
                    raise

    def _focus_and_select_all_input(self, el) -> None:
        """
        Ensure an <input> has focus and its entire value is selected.
        This prevents Ctrl+A being applied to the wrong surface (e.g., the page).
        """
        import time
        try:
            self.safe_click(el)
        except Exception:
            try:
                el.click()
            except Exception:
                pass
        time.sleep(0.2)
        try:
            self.driver.execute_script(
                """
                const el = arguments[0];
                if (!el) return false;
                try { el.focus(); } catch (e) {}
                try {
                  const v = el.value || '';
                  if (typeof el.setSelectionRange === 'function') {
                    el.setSelectionRange(0, v.length);
                    return true;
                  }
                } catch (e) {}
                return false;
                """,
                el,
            )
        except Exception:
            pass
        try:
            # Keyboard fallback if setSelectionRange isn't available.
            ActionChains(self.driver).key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).perform()
        except Exception:
            pass
        time.sleep(0.2)

    def human_delay(self, base: float = 0.5, variance: float = 0.3) -> float:
        """Return randomized delay for human-like behavior."""
        import random
        return base + random.uniform(-variance, variance)

    async def async_sleep(self, seconds: float):
        """Async sleep for non-blocking waits."""
        await asyncio.sleep(seconds)

    # =========================================
    # PAGE 1: SHORTS LIST METHODS
    # =========================================

    def navigate_to_shorts(self, channel_id: str, visibility: Optional[str] = None):
        """
        Navigate to Shorts list with optional visibility filter.

        Args:
            channel_id: YouTube channel ID
            visibility: "UNLISTED", "SCHEDULED", "PUBLIC", or None
        """
        from .channel_config import build_studio_url
        url = build_studio_url(channel_id, "short", visibility)
        logger.info(f"[DOM] Navigating to: {url[:80]}...")
        self.driver.get(url)
        self.wait_for_element(self.selectors.VIDEO_TABLE)

    def navigate_to_shorts_with_fallback(
        self, 
        channel_id: str, 
        visibility: str = "UNLISTED"
    ) -> bool:
        """
        Navigate to Shorts with visibility filter using URL-first approach.
        
        Strategy: Try direct URL with filter params first (fast, reliable).
        If filter chip not detected, fallback to DOM-based UI clicking.

        Args:
            channel_id: YouTube channel ID
            visibility: "UNLISTED", "SCHEDULED", "PUBLIC"

        Returns:
            True if filter successfully applied, False otherwise
        """
        import time
        from .channel_config import build_studio_url

        # Step 1: Try URL-based navigation (preferred)
        url = build_studio_url(channel_id, "short", visibility)
        logger.info(f"[DOM] URL-first approach: {url[:80]}...")
        self.driver.get(url)
        
        try:
            # Wait for page load
            self.wait_for_element(self.selectors.VIDEO_TABLE, timeout=10)
            # Allow filter chip to render (UI can be slow/async)
            start = time.time()
            chip_found = False
            visibility_label = visibility.capitalize()  # "UNLISTED" -> "Unlisted"
            while time.time() - start < 8.0:
                chip_found = self.driver.execute_script(f"""
                    const chips = document.querySelectorAll('ytcp-chip');
                    for (let chip of chips) {{
                        const text = (chip.textContent || '').trim();
                        if (text.includes('Visibility:') && text.includes('{visibility_label}')) {{
                            return true;
                        }}
                    }}
                    return false;
                """)
                if chip_found:
                    break
                time.sleep(0.4)

            # Verify filter chip is present using JavaScript (checks text content)
            if chip_found:
                logger.info(f"[DOM] URL filter applied successfully - chip 'Visibility: {visibility_label}' detected")
                return True
            else:
                logger.warning(f"[DOM] Filter chip not found")
        except (TimeoutException, NoSuchElementException) as e:
            logger.warning(f"[DOM] URL filter not applied, falling back to DOM clicking: {e}")
        
        # Step 2: DOM fallback - click through filter UI
        return self._apply_filter_via_dom(visibility)

    def _click_viewport_point(self, x: int, y: int) -> None:
        """
        Click a viewport coordinate reliably.
        Uses ActionChains with element offset to avoid mouse drift from move_by_offset().
        """
        body = self.driver.find_element(By.TAG_NAME, "body")
        ActionChains(self.driver).move_to_element_with_offset(body, x, y).click().perform()

    def _open_filter_ui(self) -> bool:
        """
        Open the filter UI on the Shorts list page.

        YouTube Studio UI changes frequently; do not rely on a single selector.
        """
        selectors = [
            "input#text-input[placeholder='Filter']",
            "input[placeholder='Filter']",
            "ytcp-chip-bar input#text-input",
            "#text-input[placeholder='Filter']",
        ]

        for sel in selectors:
            try:
                elem = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, sel))
                )
                if elem and elem.is_displayed():
                    self.safe_click(elem)
                    return True
            except Exception:
                continue

        # Fallback 1: click known toolbar coords (from module ModLog ADR-008)
        try:
            x, y = self.selectors.FILTER_ICON_COORDS
            self._click_viewport_point(int(x), int(y))
            return True
        except Exception:
            pass

        # Fallback 2: JS click element under point (sometimes enough to open dropdown)
        try:
            x, y = self.selectors.FILTER_ICON_COORDS
            self.driver.execute_script(
                "const el = document.elementFromPoint(arguments[0], arguments[1]); if (el) el.click();",
                int(x), int(y)
            )
            return True
        except Exception:
            return False

    def _apply_filter_via_dom(self, visibility: str = "UNLISTED") -> bool:
        """
        Apply visibility filter by clicking through the filter UI.

        Fallback method when URL-based filtering fails.

        Key Findings (ADR-005, ADR-006, ADR-007):
        - Visibility item needs test-id selector
        - Dialog must be force-opened after clicking Visibility
        - Checkboxes need ActionChains coordinate clicks (not JS .click())

        Args:
            visibility: "UNLISTED", "SCHEDULED", "PUBLIC"

        Returns:
            True if successful
        """
        import time
        from selenium.webdriver.common.action_chains import ActionChains
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        try:
            logger.info(f"[DOM] Applying {visibility} filter via UI interaction")

            # Step 1: Open filter UI (multi-selector + coords fallback)
            logger.info("[DOM] Step 1: Opening filter UI...")
            if not self._open_filter_ui():
                logger.error("[DOM] Could not open filter UI (no filter input/button found)")
                return False
            time.sleep(1.0)

            # Step 2: Click Visibility menu item (test-id first, then XPath)
            visibility_result = {"success": False}

            # Some Studio variants render a listbox with menu items (Visibility is often near the bottom).
            # Prefer scanning the listbox for an item whose text includes "Visibility".
            try:
                visibility_result = self.driver.execute_script("""
                    const tryClick = (el) => {
                        try { el.click(); return true; } catch (e) { return false; }
                    };

                    // 1) listbox menu
                    const listbox = document.querySelector('tp-yt-paper-listbox[role="listbox"]');
                    if (listbox) {
                        const items = listbox.querySelectorAll('tp-yt-paper-item, [role="option"], *');
                        for (let item of items) {
                            const text = (item.textContent || '').trim();
                            if (!text) continue;
                            if (item.offsetParent === null) continue;
                            if (text.toLowerCase() === 'visibility' || text.toLowerCase().includes('visibility')) {
                                if (tryClick(item)) return {success: true, method: 'listbox'};
                            }
                        }
                    }

                    // 2) test-id hooks
                    const testItem = document.querySelector('[test-id*="VISIBILITY"]');
                    if (testItem && testItem.offsetParent !== null) {
                        if (tryClick(testItem)) return {success: true, method: 'test-id'};
                    }

                    // 3) deep visible text scan (last resort)
                    const all = document.querySelectorAll('*');
                    for (let el of all) {
                        if (el.offsetParent === null) continue;
                        if (el.children && el.children.length > 0) continue;
                        const text = (el.textContent || '').trim();
                        if (text === 'Visibility') {
                            if (tryClick(el)) return {success: true, method: 'deep-text'};
                        }
                    }

                    return {success: false};
                """)
            except Exception:
                visibility_result = {"success": False}

            if not visibility_result.get('success'):
                # Fallback: explicit XPath
                try:
                    item = WebDriverWait(self.driver, 4).until(
                        EC.element_to_be_clickable((By.XPATH, self.selectors.VISIBILITY_MENU_ITEM_XPATH))
                    )
                    item.click()
                    visibility_result = {"success": True, "method": "xpath"}
                except Exception:
                    visibility_result = {"success": False}
            if not visibility_result.get('success'):
                logger.error("[DOM] Visibility menu item not found/clickable")
                return False
            time.sleep(0.5)

            # Step 3: Wait for dialog to open naturally; force-open only if needed.
            dialog_open = False
            try:
                dialog_open = WebDriverWait(self.driver, 4).until(lambda d: d.execute_script("""
                    const dialog = document.querySelector('ytcp-filter-dialog #dialog');
                    if (!dialog) return false;
                    const style = window.getComputedStyle(dialog);
                    return style && style.display !== 'none' && dialog.getAttribute('aria-hidden') !== 'true';
                """))
            except Exception:
                dialog_open = False
            if not dialog_open:
                # Last resort (ADR-007): force-open for visibility, but this may not apply without native handlers.
                try:
                    self.driver.execute_script("""
                        const filterDialog = document.querySelector('ytcp-filter-dialog');
                        if (!filterDialog) return;
                        const paperDialog = filterDialog.querySelector('#dialog');
                        if (!paperDialog) return;
                        paperDialog.opened = true;
                        paperDialog.setAttribute('opened', '');
                        paperDialog.removeAttribute('aria-hidden');
                        paperDialog.style.display = 'block';
                    """)
                except Exception:
                    pass
            time.sleep(0.4)

            # Step 4: Select checkbox (ActionChains often required for ytcp-checkbox-lit)
            visibility_label = visibility.capitalize()
            checkbox_coords = self.driver.execute_script(f"""
                const filterDialog = document.querySelector('ytcp-filter-dialog');
                if (!filterDialog) return {{error: 'no dialog'}};

                const spans = filterDialog.querySelectorAll('span');
                for (let span of spans) {{
                    if (span.textContent.trim() === '{visibility_label}' && span.offsetParent !== null) {{
                        let current = span.parentElement;
                        for (let i = 0; i < 10 && current; i++) {{
                            const checkbox = current.querySelector('ytcp-checkbox-lit');
                            if (checkbox && checkbox.offsetParent !== null) {{
                                const rect = checkbox.getBoundingClientRect();
                                return {{
                                    success: true,
                                    x: Math.round(rect.left + rect.width / 2),
                                    y: Math.round(rect.top + rect.height / 2)
                                }};
                            }}
                            current = current.parentElement;
                        }}
                        break;
                    }}
                }}
                return {{success: false, error: 'checkbox not found'}};
            """)

            if not checkbox_coords.get('success'):
                # Fallback: click visible 'Unlisted' label directly (some UIs auto-apply)
                clicked_label = self.driver.execute_script(f"""
                    const spans = document.querySelectorAll('span');
                    for (let span of spans) {{
                        if (span.offsetParent !== null && span.textContent.trim() === '{visibility_label}') {{
                            span.click();
                            return true;
                        }}
                    }}
                    return false;
                """)
                if not clicked_label:
                    logger.error(f"[DOM] Checkbox/label not found for {visibility_label}")
                    return False
            else:
                # ActionChains click at coordinates (required for ytcp-checkbox-lit)
                actions = ActionChains(self.driver)
                actions.move_by_offset(checkbox_coords['x'], checkbox_coords['y']).click().perform()
                actions.move_by_offset(-checkbox_coords['x'], -checkbox_coords['y']).perform()
                time.sleep(0.4)

            # Step 5: Click Apply button if present (some Studio variants auto-apply)
            apply_coords = self.driver.execute_script("""
                const filterDialog = document.querySelector('ytcp-filter-dialog');
                if (!filterDialog) return {error: 'no dialog'};

                const buttons = filterDialog.querySelectorAll('button, ytcp-button');
                for (let btn of buttons) {
                    if (btn.textContent.trim() === 'Apply' && btn.offsetParent !== null) {
                        const rect = btn.getBoundingClientRect();
                        return {
                            success: true,
                            x: Math.round(rect.left + rect.width / 2),
                            y: Math.round(rect.top + rect.height / 2)
                        };
                    }
                }
                return {success: false};
            """)

            if apply_coords.get('success'):
                actions = ActionChains(self.driver)
                actions.move_by_offset(apply_coords['x'], apply_coords['y']).click().perform()
                actions.move_by_offset(-apply_coords['x'], -apply_coords['y']).perform()
                time.sleep(1)

            # Close dropdown with ESC
            self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
            time.sleep(0.5)

            # Step 6: Verify chip (best-effort)
            chip_ok = self.driver.execute_script(f"""
                const chips = document.querySelectorAll('ytcp-chip');
                for (let chip of chips) {{
                    const text = (chip.textContent || '').trim();
                    if (text.includes('Visibility:') && text.includes('{visibility_label}')) {{
                        return true;
                    }}
                }}
                return false;
            """)
            if chip_ok:
                logger.info(f"[DOM] DOM fallback filter applied - chip verified")
                return True

            logger.warning("[DOM] DOM fallback executed but filter chip not verified (UI may differ)")
            return True

        except Exception as e:
            logger.error(f"[DOM] Filter fallback failed: {e}")

        return False

    # =========================================
    # LAYER 2: VIDEO EDIT METHODS
    # =========================================

    def click_first_video_edit_button(self) -> Optional[str]:
        """
        Click edit button on first video row to open edit page.
        
        Returns:
            Video ID if successful, None otherwise
        """
        import time
        from selenium.webdriver.common.action_chains import ActionChains

        try:
            logger.info("[DOM Layer 2] Clicking edit button on first video...")
            
            # Get first video row
            rows = self.driver.find_elements(By.CSS_SELECTOR, self.selectors.VIDEO_ROWS)
            if not rows:
                logger.error("[DOM Layer 2] No video rows found")
                return None
            
            first_row = rows[0]
            
            # Hover to reveal edit button
            actions = ActionChains(self.driver)
            actions.move_to_element(first_row).perform()
            time.sleep(0.5)
            
            # Try to find and click edit button
            try:
                edit_btn = first_row.find_element(By.CSS_SELECTOR, self.selectors.EDIT_BUTTON_SELECTOR)
                if edit_btn:
                    href = edit_btn.get_attribute("href")
                    video_id = href.split("/video/")[1].split("/")[0] if "/video/" in href else None
                    self.safe_click(edit_btn)
                    logger.info(f"[DOM Layer 2] Clicked edit for video: {video_id}")
                    time.sleep(2)  # Wait for page load
                    return video_id
            except NoSuchElementException:
                pass
            
            # Fallback: coordinate-based click
            x, y = self.selectors.EDIT_BUTTON_COORDS
            actions = ActionChains(self.driver)
            actions.move_by_offset(x, y).click().perform()
            actions.reset_actions()
            time.sleep(2)
            
            # Extract video ID from URL
            if "/video/" in self.driver.current_url:
                video_id = self.driver.current_url.split("/video/")[1].split("/")[0]
                logger.info(f"[DOM Layer 2] On edit page for video: {video_id}")
                return video_id
            
        except Exception as e:
            logger.error(f"[DOM Layer 2] Edit button click failed: {e}")
        
        return None

    def get_current_title(self) -> Optional[str]:
        """
        Extract current title from video edit page.
        
        Returns:
            Title text or None
        """
        try:
            # Try CSS selector first
            title_elem = self.driver.find_element(
                By.CSS_SELECTOR, self.selectors.TITLE_TEXTBOX_SELECTOR
            )
            title = title_elem.text or title_elem.get_attribute("textContent")
            logger.info(f"[DOM Layer 2] Current title: {title[:50]}...")
            return title.strip()
        except NoSuchElementException:
            pass
        
        # Try XPath
        try:
            title_elem = self.driver.find_element(
                By.XPATH, self.selectors.TITLE_TEXTBOX_XPATH
            )
            title = title_elem.text or title_elem.get_attribute("textContent")
            logger.info(f"[DOM Layer 2] Current title (XPath): {title[:50]}...")
            return title.strip()
        except NoSuchElementException:
            logger.warning("[DOM Layer 2] Could not find title textbox")
        
        return None

    def get_current_description(self) -> Optional[str]:
        """
        Extract current description from video edit page.
        
        Returns:
            Description text or None
        """
        try:
            desc_elem = self.driver.find_element(
                By.CSS_SELECTOR, self.selectors.DESC_TEXTBOX_SELECTOR
            )
            desc = desc_elem.text or desc_elem.get_attribute("textContent")
            logger.info(f"[DOM Layer 2] Current description: {desc[:50]}...")
            return desc.strip()
        except NoSuchElementException:
            pass
        
        try:
            desc_elem = self.driver.find_element(
                By.XPATH, self.selectors.DESC_TEXTBOX_XPATH
            )
            desc = desc_elem.text or desc_elem.get_attribute("textContent")
            logger.info(f"[DOM Layer 2] Current description (XPath): {desc[:50]}...")
            return desc.strip()
        except NoSuchElementException:
            logger.warning("[DOM Layer 2] Could not find description textbox")
        
        return None

    def set_title(self, new_title: str) -> bool:
        """
        Set new title in video edit page.
        
        Args:
            new_title: New title text
            
        Returns:
            True if successful
        """
        try:
            title_elem = self.driver.find_element(
                By.CSS_SELECTOR, self.selectors.TITLE_TEXTBOX_SELECTOR
            )
            title_elem.click()
            title_elem.send_keys(Keys.CONTROL + "a")  # Select all
            title_elem.send_keys(new_title)
            logger.info(f"[DOM Layer 2] Set title: {new_title[:50]}...")
            return True
        except Exception as e:
            logger.error(f"[DOM Layer 2] Set title failed: {e}")
            return False

    def set_description(self, new_description: str) -> bool:
        """
        Set new description in video edit page.
        
        Args:
            new_description: New description text
            
        Returns:
            True if successful
        """
        try:
            desc_elem = self.driver.find_element(
                By.CSS_SELECTOR, self.selectors.DESC_TEXTBOX_SELECTOR
            )
            desc_elem.click()
            desc_elem.send_keys(Keys.CONTROL + "a")  # Select all
            desc_elem.send_keys(new_description)
            logger.info(f"[DOM Layer 2] Set description: {new_description[:50]}...")
            return True
        except Exception as e:
            logger.error(f"[DOM Layer 2] Set description failed: {e}")
            return False

    def get_video_rows(self) -> List:
        """Get all video row elements from the table."""
        return self.driver.find_elements(By.CSS_SELECTOR, self.selectors.VIDEO_ROWS)

    def get_scheduled_videos(self) -> List[Dict[str, str]]:
        """
        Get all scheduled videos with their dates.

        Returns:
            List of dicts with video_id, title, date
        """
        videos = []
        rows = self.driver.find_elements(By.XPATH, self.selectors.XPATH_SCHEDULED_ROWS)

        for row in rows:
            try:
                # Extract video ID from link href
                link = row.find_element(By.CSS_SELECTOR, self.selectors.VIDEO_TITLE_LINK)
                href = link.get_attribute("href")
                video_id = href.split("/video/")[1].split("/")[0]
                title = link.text

                # Extract date from date cell
                date_cell = row.find_element(By.XPATH, ".//td[contains(text(),'202')]")
                date_text = date_cell.text

                videos.append({
                    "video_id": video_id,
                    "title": title,
                    "date": date_text,
                })
            except Exception as e:
                logger.warning(f"[DOM] Error parsing video row: {e}")

        return videos

    def get_unlisted_videos(self) -> List[Dict[str, str]]:
        """
        Get all unlisted videos.

        Returns:
            List of dicts with video_id, title, href
        """
        videos = []
        rows = self.driver.find_elements(By.XPATH, self.selectors.XPATH_UNLISTED_ROWS)

        for row in rows:
            try:
                link = row.find_element(By.CSS_SELECTOR, self.selectors.VIDEO_TITLE_LINK)
                href = link.get_attribute("href")
                video_id = href.split("/video/")[1].split("/")[0]
                title = link.text

                videos.append({
                    "video_id": video_id,
                    "title": title,
                    "href": href,
                })
            except Exception as e:
                logger.warning(f"[DOM] Error parsing unlisted row: {e}")

        return videos

    def has_next_page(self) -> bool:
        """Check if there's a next page of results."""
        try:
            btn = self.driver.find_element(By.CSS_SELECTOR, self.selectors.NEXT_PAGE_BTN)
            return btn.is_enabled()
        except NoSuchElementException:
            return False

    def click_next_page(self):
        """Navigate to next page of results."""
        btn = self.wait_for_clickable(self.selectors.NEXT_PAGE_BTN)
        self.safe_click(btn)
        import time
        time.sleep(1)  # Wait for page load

    # =========================================
    # PAGE 2: VIDEO EDIT METHODS
    # =========================================

    def navigate_to_video(self, video_id: str):
        """Navigate to video edit page."""
        url = f"https://studio.youtube.com/video/{video_id}/edit"
        logger.info(f"[DOM] Navigating to video: {video_id}")
        self.driver.get(url)
        # Wait for edit page readiness (Studio variants render different visibility controls).
        # We wait for ANY stable marker rather than a single brittle selector.
        wait = WebDriverWait(self.driver, 12)

        def _is_ready(drv) -> bool:
            try:
                candidates = [
                    "ytcp-video-metadata-visibility",
                    "ytcp-video-metadata-visibility #select-button",
                    "button[aria-label='Edit video visibility status']",
                    "#select-button",
                    "#title-textarea",
                    "#description-textarea",
                ]
                for css in candidates:
                    if drv.find_elements(By.CSS_SELECTOR, css):
                        return True
            except Exception:
                return False
            return False

        wait.until(lambda d: _is_ready(d))

    def edit_title(self, new_title: str):
        """Edit video title."""
        import time
        title_input = self.wait_for_element(
            self.selectors.TITLE_INPUT_XPATH, By.XPATH
        )
        self.safe_click(title_input)
        try:
            # 012-modeled: focus is handled by safe_click; replace via Ctrl+A.
            ActionChains(self.driver).key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).perform()
            time.sleep(self.human_delay(0.25, 0.15))
            title_input.send_keys(new_title)
        except Exception as e:
            # ChromeDriver may fail on non-BMP characters (emoji). Fallback to JS assignment.
            logger.warning(f"[DOM] Title send_keys failed, falling back to JS: {type(e).__name__}: {e}")
            self.driver.execute_script(
                """
                const el = arguments[0];
                const text = arguments[1];
                el.focus();
                el.textContent = text;
                el.dispatchEvent(new Event('input', { bubbles: true }));
                """,
                title_input,
                new_title,
            )

    def edit_description(self, new_description: str):
        """Edit video description."""
        import time
        desc_input = self.wait_for_element(
            self.selectors.DESCRIPTION_INPUT_XPATH, By.XPATH
        )
        self.safe_click(desc_input)
        try:
            ActionChains(self.driver).key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).perform()
            time.sleep(self.human_delay(0.25, 0.15))
            desc_input.send_keys(new_description)
        except Exception as e:
            # ChromeDriver may fail on non-BMP characters (emoji). Fallback to JS assignment.
            logger.warning(f"[DOM] Description send_keys failed, falling back to JS: {type(e).__name__}: {e}")
            self.driver.execute_script(
                """
                const el = arguments[0];
                const text = arguments[1];
                el.focus();
                el.textContent = text;
                el.dispatchEvent(new Event('input', { bubbles: true }));
                """,
                desc_input,
                new_description,
            )

    def click_save(self):
        """Click page-level Save button (not dialog Done/Save)."""
        import time

        # Allow dialog close animation to complete (Done/Save just clicked).
        pre_save_delay = float(os.getenv("YT_SCHEDULER_PRE_SAVE_DELAY_SEC", "1.0"))
        time.sleep(pre_save_delay)

        # Best-effort: wait for the visibility dialog to disappear so it doesn't intercept clicks.
        try:
            WebDriverWait(self.driver, 6).until(
                lambda d: not d.find_elements(By.CSS_SELECTOR, "tp-yt-paper-dialog#dialog")
            )
        except Exception:
            pass

        candidates = [
            (By.CSS_SELECTOR, "ytcp-button#save-button button"),
            (By.CSS_SELECTOR, "ytcp-button#save-button"),
            (By.CSS_SELECTOR, "button#save-button"),
            (By.XPATH, "//ytcp-button[@id='save-button']//button"),
            (By.XPATH, "//button[@id='save-button']"),
            (By.XPATH, "//button[.//span[normalize-space(text())='Save']]"),
        ]

        last_err: Exception | None = None
        for by, sel in candidates:
            try:
                el = self.wait_for_clickable(sel, by, timeout=5)
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
                except Exception:
                    pass
                self.safe_click(el)
                time.sleep(2.0)
                return
            except Exception as exc:
                last_err = exc
                continue

        # JS fallback: Studio sometimes renders Save as a custom element without stable ids,
        # or behind wrappers that Selenium "clickable" heuristics miss.
        try:
            clicked = self.driver.execute_script(
                """
                function isVisible(el) {
                  if (!el) return false;
                  if (el.offsetParent === null) return false;
                  const r = el.getBoundingClientRect();
                  return r.width > 0 && r.height > 0;
                }
                function textOf(el) {
                  return ((el && el.textContent) ? el.textContent : '').trim();
                }
                function clickBest(el) {
                  if (!el) return false;
                  // Prefer inner <button> when present.
                  try {
                    const inner = el.querySelector && el.querySelector('button');
                    if (inner && isVisible(inner)) { inner.click(); return true; }
                  } catch (e) {}
                  try { el.click(); return true; } catch (e) {}
                  return false;
                }

                const root = document;
                const all = Array.from(root.querySelectorAll('ytcp-button, button, tp-yt-paper-button, ytcp-button-shape'));
                const saveLike = all
                  .filter(isVisible)
                  .map(el => ({ el, t: textOf(el).toLowerCase(), id: (el.id||'') }))
                  .filter(x => x.t === 'save' || x.id === 'save-button');

                // Prefer explicit id, then visible text Save.
                const preferred = saveLike.find(x => x.id === 'save-button') || saveLike.find(x => x.t === 'save');
                if (preferred && clickBest(preferred.el)) return { clicked: true, id: preferred.id, text: preferred.t };

                return { clicked: false, found: saveLike.slice(0, 8).map(x => ({id:x.id, text:x.t})) };
                """
            )
            if isinstance(clicked, dict) and clicked.get("clicked"):
                time.sleep(2.0)
                return
        except Exception as exc:
            last_err = exc

        raise TimeoutException(f"Save button not found/clickable: {last_err}")

    # =========================================
    # PAGE 3: SCHEDULING DIALOG METHODS
    # =========================================

    def open_visibility_dialog(self):
        """Open the visibility/scheduling dialog."""
        import time

        # YouTube Studio variants render this control as:
        # - <button aria-label="Edit video visibility status">
        # - <ytcp-icon-button id="select-button" aria-label="Edit video visibility status">
        # Prefer robust multi-selector approach.
        vis_btn = None

        # 1) Strict XPath for the known aria-label (button)
        try:
            vis_btn = self.wait_for_clickable(self.selectors.VISIBILITY_BTN_XPATH, By.XPATH, timeout=6)
        except Exception:
            vis_btn = None

        # 2) CSS for the icon button inside the visibility section
        if vis_btn is None:
            try:
                vis_btn = self.wait_for_clickable(
                    "ytcp-video-metadata-visibility #select-button",
                    By.CSS_SELECTOR,
                    timeout=6,
                )
            except Exception:
                vis_btn = None

        # 3) Final XPath fallback: any element with id=select-button and a visibility aria-label
        if vis_btn is None:
            try:
                vis_btn = self.wait_for_clickable(
                    "//*[@id='select-button' and contains(@aria-label,'visibility')]",
                    By.XPATH,
                    timeout=6,
                )
            except Exception:
                vis_btn = None

        if vis_btn is None:
            raise TimeoutException("Visibility button not found/clickable")

        self.safe_click(vis_btn)
        time.sleep(0.6)

        # Wait for the visibility dialog surface (tp-yt-paper-dialog variant is most common)
        try:
            self.wait_for_element(self.selectors.VISIBILITY_DIALOG_XPATH, By.XPATH, timeout=8)
            return
        except Exception:
            pass

        # Fallback: if dialog selector changes, wait for schedule/date/time inputs to exist
        WebDriverWait(self.driver, 8).until(lambda d: d.execute_script("""
            const hasSchedule =
              !!document.querySelector('tp-yt-paper-radio-button[name=\"SCHEDULE\"], tp-yt-paper-radio-button[name=\"SCHEDULED\"], tp-yt-paper-radio-button[name=\"SCHEDULE\"]');
            const hasDate = !!document.querySelector('input[aria-label*=\"Date\"]');
            const hasTime = !!document.querySelector('input[aria-label*=\"Time\"], input[aria-label*=\"time\"]');
            return hasSchedule || (hasDate && hasTime);
        """))

    def select_schedule_option(self):
        """Select the 'Schedule' radio button in visibility dialog."""
        import time

        # YouTube Studio has at least two variants:
        # - Variant A: explicit "Schedule" radio button
        # - Variant B: a "Schedule" section (often #second-container) that expands to show date/time inputs
        #
        # We treat "select schedule" as: ensure the schedule section is expanded and date/time inputs exist.

        # Variant A: try schedule radio if present
        radio_xpaths = [
            getattr(self.selectors, "SCHEDULE_RADIO_XPATH", "//tp-yt-paper-radio-button[@name='SCHEDULE']"),
            getattr(self.selectors, "RADIO_SCHEDULE", "//tp-yt-paper-radio-button[.//span[contains(text(),'Schedule')]]"),
            "//tp-yt-paper-radio-button[contains(translate(., 'SCHEDULE', 'schedule'), 'schedule')]",
        ]
        for xp in radio_xpaths:
            try:
                schedule_radio = self.wait_for_clickable(xp, By.XPATH, timeout=3)
                self.safe_click(schedule_radio)
                time.sleep(0.3)
                break
            except Exception:
                continue

        # Variant B: expand schedule section (common in current Studio)
        expanded = False
        try:
            sched = self.driver.find_element(By.ID, "second-container")
            if sched and sched.is_displayed():
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({behavior:'smooth', block:'center'});",
                    sched,
                )
                time.sleep(0.2)

                # Only click to expand if there is an explicit expanded state and it's currently collapsed.
                toggler = self.driver.execute_script("""
                    const root = document.querySelector('#second-container');
                    if (!root) return null;
                    const candidates = root.querySelectorAll('[aria-expanded]');
                    for (const el of candidates) {
                      if (el.offsetParent === null) continue;
                      const v = el.getAttribute('aria-expanded');
                      if (v === 'false' || v === 'true') return el;
                    }
                    return root;
                """)
                if toggler:
                    # If toggler has aria-expanded=true already, don't click (prevents open->close).
                    try:
                        state = self.driver.execute_script(
                            "return arguments[0].getAttribute('aria-expanded');",
                            toggler,
                        )
                    except Exception:
                        state = None

                    if state == "true":
                        expanded = True
                    else:
                        # 012-modeled click preferred; safe_click has JS fallback if needed.
                        self.safe_click(toggler)
                        time.sleep(0.5)
                        expanded = True
        except Exception:
            expanded = False

        if not expanded:
            # Fallback: legacy expand button selector
            try:
                expand_btn = self.driver.find_element(By.XPATH, self.selectors.SCHEDULE_EXPAND)
                if expand_btn and expand_btn.is_displayed():
                    self.safe_click(expand_btn)
                    time.sleep(0.5)
            except Exception:
                pass

        # Wait for a time input to exist (date may be text until clicked).
        WebDriverWait(self.driver, 8).until(lambda d: d.execute_script("""
            const inputs = Array.from(document.querySelectorAll('input'));
            const visible = inputs.filter(i => i && i.offsetParent !== null);
            // Most common: time input has a value like "12:00 AM" and no aria-label.
            const hasTimeLike = visible.some(i => {
              const v = (i.value || '').trim();
              return /\\d{1,2}:\\d{2}/.test(v);
            });
            // Alternative: aria-labeled time input exists.
            const hasAriaTime = !!document.querySelector('input[aria-label*="Time"], input[aria-label*="time"]');
            return hasTimeLike || hasAriaTime;
        """))

    def set_schedule_date(self, date_str: str):
        """
        Set the schedule date.

        Args:
            date_str: Date string like "Jan 5, 2026"
        """
        import time
        import os

        pre_type_delay = float(os.getenv("YT_SCHEDULER_PRE_TYPE_DELAY_SEC", "0.6"))
        key_delay = float(os.getenv("YT_SCHEDULER_KEY_DELAY_SEC", "0.06"))

        def slow_type(el, text: str):
            # Methodical per-char typing to avoid Studio dropping keystrokes.
            for ch in text:
                el.send_keys(ch)
                time.sleep(key_delay)

        def commit_input(el):
            """
            YouTube Studio sometimes doesn't "commit" until Enter/blur.
            Do Enter + Tab, then dispatch input/change/blur events.
            """
            try:
                el.send_keys(Keys.ENTER)
            except Exception:
                try:
                    ActionChains(self.driver).send_keys(Keys.ENTER).perform()
                except Exception:
                    pass
            time.sleep(pre_type_delay)
            try:
                el.send_keys(Keys.TAB)
            except Exception:
                try:
                    ActionChains(self.driver).send_keys(Keys.TAB).perform()
                except Exception:
                    pass
            time.sleep(pre_type_delay)
            try:
                self.driver.execute_script(
                    """
                    const el = arguments[0];
                    if (!el) return;
                    try { el.dispatchEvent(new Event('input', { bubbles: true })); } catch (e) {}
                    try { el.dispatchEvent(new Event('change', { bubbles: true })); } catch (e) {}
                    try { el.blur(); } catch (e) {}
                    """,
                    el,
                )
            except Exception:
                pass
            time.sleep(pre_type_delay)

        # In current Studio variants, date is often rendered as text (e.g. "Jan 19, 2026")
        # until you click it. We must click the *date field* first, then Ctrl+A replace.
        try:
            # Try an actual Date input first (when already expanded)
            date_input = self.wait_for_element(self.selectors.DATE_INPUT_XPATH, By.XPATH, timeout=3)
        except Exception:
            date_input = None

        if date_input is None:
            # Current Studio variant:
            # - The schedule section shows a date *text* ("Jan 19, 2026") inside
            #   `ytcp-text-dropdown-trigger#datepicker-trigger div.left-container`.
            # - Clicking that opens a `ytcp-date-picker` popup with an <input> we can Ctrl+A replace.
            try:
                date_trigger = self.wait_for_clickable(
                    self.selectors.DATE_TRIGGER_CSS,
                    By.CSS_SELECTOR,
                    timeout=6,
                )
                # Critical: click DATE first (not time/timezone).
                # Occam: deterministic click with slow delays.
                self.safe_click(date_trigger)
                time.sleep(pre_type_delay)
            except Exception:
                # Fallback: click the visible date text inside the schedule container to activate the picker/input.
                self.driver.execute_script("""
                    const root = document.querySelector('#second-container');
                    if (!root) return;
                    const candidates = Array.from(root.querySelectorAll('span, div'))
                      .filter(e => e.offsetParent !== null && e.children.length === 0)
                      .map(e => ({el: e, t: (e.textContent||'').trim()}))
                      .filter(x => /\\b\\w{3}\\b\\s+\\d{1,2},\\s+\\d{4}/.test(x.t));
                    if (candidates.length) candidates[0].el.click();
                """)
                time.sleep(pre_type_delay)

            # Try the date-picker popup input first
            for attempt in range(2):
                try:
                    picker_input = self.wait_for_clickable(
                        self.selectors.DATE_PICKER_INPUT_CSS,
                        By.CSS_SELECTOR,
                        timeout=8,
                    )
                    self._focus_and_select_all_input(picker_input)
                    time.sleep(pre_type_delay)

                    # Replace selected value by typing.
                    slow_type(picker_input, date_str)
                    time.sleep(0.15)
                    commit_input(picker_input)

                    # Verify the value "stuck" (some variants keep value in activeElement)
                    try:
                        val = (picker_input.get_attribute("value") or "").strip()
                        if val and val.lower() == date_str.strip().lower():
                            return
                    except Exception:
                        pass

                    # If verification failed, retry once after an extra delay.
                    if attempt == 0:
                        time.sleep(pre_type_delay)
                        continue
                    return
                except Exception:
                    picker_input = None

            # Alternate variant: aria-labeled Date input exists after clicking trigger
            try:
                date_input = self.wait_for_element(self.selectors.DATE_INPUT_XPATH, By.XPATH, timeout=3)
            except Exception:
                date_input = None

        if date_input is not None:
            self._focus_and_select_all_input(date_input)
            time.sleep(pre_type_delay)
            slow_type(date_input, date_str)
            time.sleep(0.15)
            commit_input(date_input)
            return

        # Fallback: legacy date picker trigger then input (older Studio variants)
        try:
            date_btn = self.wait_for_clickable(self.selectors.DATE_PICKER_BTN, By.XPATH, timeout=6)
            self.safe_click(date_btn)
            time.sleep(0.3)
            date_input = self.wait_for_element(self.selectors.DATE_INPUT, By.XPATH, timeout=6)
            self._focus_and_select_all_input(date_input)
            time.sleep(pre_type_delay)
            slow_type(date_input, date_str)
            time.sleep(0.15)
            commit_input(date_input)
        except Exception as exc:
            raise TimeoutException(f"Date input not found/usable: {exc}")

    def set_schedule_time(self, time_str: str):
        """
        Set the schedule time.

        Args:
            time_str: Time string like "5:00 AM"
        """
        import time
        import os

        pre_type_delay = float(os.getenv("YT_SCHEDULER_PRE_TYPE_DELAY_SEC", "0.5"))
        key_delay = float(os.getenv("YT_SCHEDULER_KEY_DELAY_SEC", "0.05"))

        def slow_type(el, text: str):
            for ch in text:
                el.send_keys(ch)
                time.sleep(key_delay)

        def commit_input(el):
            """
            YouTube Studio time field sometimes requires Enter/blur to stick.
            """
            try:
                el.send_keys(Keys.ENTER)
            except Exception:
                try:
                    ActionChains(self.driver).send_keys(Keys.ENTER).perform()
                except Exception:
                    pass
            time.sleep(pre_type_delay)
            try:
                el.send_keys(Keys.TAB)
            except Exception:
                try:
                    ActionChains(self.driver).send_keys(Keys.TAB).perform()
                except Exception:
                    pass
            time.sleep(pre_type_delay)
            try:
                self.driver.execute_script(
                    """
                    const el = arguments[0];
                    if (!el) return;
                    try { el.dispatchEvent(new Event('input', { bubbles: true })); } catch (e) {}
                    try { el.dispatchEvent(new Event('change', { bubbles: true })); } catch (e) {}
                    try { el.blur(); } catch (e) {}
                    """,
                    el,
                )
            except Exception:
                pass
            time.sleep(pre_type_delay)

        # Prefer direct input replacement (no dropdown selection).
        time_input = None

        # 0) Current Studio variant (explicit DOM path)
        try:
            time_input = self.wait_for_element(
                self.selectors.TIME_OF_DAY_INPUT_CSS,
                By.CSS_SELECTOR,
                timeout=3,
            )
        except Exception:
            time_input = None

        # 1) aria-labeled time inputs (some variants)
        if time_input is None:
            for xp in [self.selectors.TIME_INPUT_XPATH, self.selectors.TIME_INPUT_TEXTBOX]:
                try:
                    time_input = self.wait_for_element(xp, By.XPATH, timeout=2)
                    break
                except Exception:
                    time_input = None

        # 2) common variant: visible input with a value like "12:00 AM" and no aria-label
        if time_input is None:
            try:
                time_input = WebDriverWait(self.driver, 4).until(lambda d: d.execute_script("""
                    const inputs = Array.from(document.querySelectorAll('input'));
                    const visible = inputs.filter(i => i && i.offsetParent !== null);
                    for (const i of visible) {
                      const v = (i.value || '').trim();
                      if (/\\d{1,2}:\\d{2}/.test(v) && (v.toUpperCase().includes('AM') || v.toUpperCase().includes('PM'))) {
                        return i;
                      }
                    }
                    return null;
                """))
            except Exception:
                time_input = None

        if time_input is None:
            raise TimeoutException("Time input not found/usable")

        # Critical: click the actual input field first, then Ctrl+A replace.
        self._focus_and_select_all_input(time_input)
        time.sleep(pre_type_delay)
        slow_type(time_input, time_str)
        time.sleep(0.15)
        commit_input(time_input)

    def click_done(self):
        """Click Done button to confirm scheduling."""
        import time

        # YouTube Studio variants:
        # - native <button> with inner <span>Done</span>
        # - <ytcp-button id="done-button"> wrapper with an internal <button>
        # - dialog "Save" button (some variants replace Done with Save inside dialog)
        # - different DOM/shadow structures
        candidates = [
            (By.XPATH, self.selectors.DONE_BTN),
            (By.XPATH, "//button[.//span[normalize-space(text())='Done']]"),
            (By.XPATH, "//ytcp-button[.//span[normalize-space(text())='Done']]"),
            # Dialog Save button (observed path: tp-yt-paper-dialog#dialog div.button-area ... ytcp-button#save-button)
            # IMPORTANT: scope to button-area to avoid timezone-select-button misclicks.
            (By.CSS_SELECTOR, "tp-yt-paper-dialog#dialog div.button-area ytcp-button#save-button button"),
            (By.CSS_SELECTOR, "tp-yt-paper-dialog#dialog div.button-area ytcp-button#save-button"),
            (By.CSS_SELECTOR, "ytcp-button#done-button"),
            (By.CSS_SELECTOR, "ytcp-button#done-button button"),
            (By.CSS_SELECTOR, "button#done-button"),
        ]

        for by, sel in candidates:
            try:
                el = self.wait_for_clickable(sel, by, timeout=4)

                # Safety: never click timezone selector by accident.
                try:
                    is_timezone = self.driver.execute_script(
                        "return !!(arguments[0] && arguments[0].closest && arguments[0].closest('#timezone-select-button'));",
                        el,
                    )
                    if is_timezone:
                        continue
                except Exception:
                    pass

                # Prefer clicking the inner <button> when wrapped by ytcp-button.
                try:
                    if (el.tag_name or "").lower() == "ytcp-button":
                        inner = el.find_element(By.CSS_SELECTOR, "button")
                        el = inner
                except Exception:
                    pass

                try:
                    # Ensure it's in view (some Studio dialogs require scroll)
                    self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
                except Exception:
                    pass
                self.safe_click(el)
                time.sleep(1)
                return
            except Exception:
                continue

        # Last resort: JS click inside dialog (STRICT scope).
        try:
            clicked = self.driver.execute_script(
                """
                const root = document.querySelector('tp-yt-paper-dialog#dialog') || document;
                // Prefer explicit ids.
                const done = root.querySelector('ytcp-button#done-button button, ytcp-button#done-button, button#done-button');
                if (done) { done.click(); return true; }

                // Studio variant: dialog Save button is the "Done" equivalent.
                const save = root.querySelector('div.button-area ytcp-button#save-button button, div.button-area ytcp-button#save-button');
                if (save) { save.click(); return true; }

                return false;
                """
            )
            if clicked:
                time.sleep(1)
                return
        except Exception:
            pass

        raise TimeoutException("Done/Save button not found/clickable")

    def schedule_video(self, date_str: str, time_str: str) -> bool:
        """
        Full scheduling workflow for current video.

        Args:
            date_str: Date like "Jan 5, 2026"
            time_str: Time like "5:00 AM"

        Returns:
            True if successful
        """
        logger.info(f"[DOM] Scheduling for {date_str} at {time_str}")

        steps = [
            ("open_visibility_dialog", lambda: self.open_visibility_dialog()),
            ("select_schedule_option", lambda: self.select_schedule_option()),
            ("set_schedule_date", lambda: self.set_schedule_date(date_str)),
            ("set_schedule_time", lambda: self.set_schedule_time(time_str)),
            ("click_done", lambda: self.click_done()),
            ("click_save", lambda: self.click_save()),
        ]

        for step_name, fn in steps:
            try:
                fn()
            except Exception as e:
                logger.error(f"[DOM] Scheduling failed at {step_name}: {type(e).__name__}: {e}")
                # Best-effort cleanup: close dialog so the next loop isn't blocked.
                try:
                    ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
                    import time
                    time.sleep(0.5)
                except Exception:
                    pass
                return False

        logger.info(f"[DOM] Successfully scheduled for {date_str} {time_str}")
        return True
