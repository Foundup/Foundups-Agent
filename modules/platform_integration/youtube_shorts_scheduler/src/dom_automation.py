"""
DOM Automation Layer for YouTube Studio

Selenium/UI-TARS selectors and interaction methods for Shorts scheduling.
Based on live DOM inspection of YouTube Studio pages.
"""

import asyncio
import logging
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

    # L3: Time
    TIME_INPUT_XPATH = "//input[contains(@aria-label,'time') or contains(@placeholder,'time')]"
    TIME_TEXTBOX_XPATH = "//ytcp-form-input-container[contains(.,'Time')]//input"

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
        Click element with fallback to JavaScript click.

        Args:
            element: WebElement to click
            use_js: Force JavaScript click
        """
        try:
            if use_js:
                self.driver.execute_script("arguments[0].click();", element)
            else:
                element.click()
        except Exception:
            # Fallback to JS click
            self.driver.execute_script("arguments[0].click();", element)

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
            time.sleep(1)  # Allow filter chip to render

            # Verify filter chip is present using JavaScript (checks text content)
            visibility_label = visibility.capitalize()  # "UNLISTED" -> "Unlisted"
            chip_found = self.driver.execute_script(f"""
                const chips = document.querySelectorAll('ytcp-chip');
                for (let chip of chips) {{
                    const text = chip.textContent.trim();
                    if (text.includes('Visibility:') && text.includes('{visibility_label}')) {{
                        return true;
                    }}
                }}
                return false;
            """)
            if chip_found:
                logger.info(f"[DOM] URL filter applied successfully - chip 'Visibility: {visibility_label}' detected")
                return True
            else:
                logger.warning(f"[DOM] Filter chip not found")
        except (TimeoutException, NoSuchElementException) as e:
            logger.warning(f"[DOM] URL filter not applied, falling back to DOM clicking: {e}")
        
        # Step 2: DOM fallback - click through filter UI
        return self._apply_filter_via_dom(visibility)

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

            # Step 1: Wait for and click Filter input
            logger.info("[DOM] Step 1: Waiting for Filter input...")
            try:
                filter_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Filter']"))
                )
                # Also wait for it to be visible
                WebDriverWait(self.driver, 5).until(
                    EC.visibility_of(filter_input)
                )
                filter_input.click()
                filter_input.focus() if hasattr(filter_input, 'focus') else None
                logger.info("[DOM] Filter input clicked")
            except TimeoutException:
                logger.error("[DOM] Filter input not found after waiting")
                return False
            time.sleep(1.5)

            # Step 2: Click Visibility item using test-id (from deep dive)
            visibility_result = self.driver.execute_script("""
                const item = document.querySelector('[test-id*="VISIBILITY"]');
                if (item) {
                    item.click();
                    return {success: true};
                }
                return {success: false};
            """)
            if not visibility_result.get('success'):
                logger.error("[DOM] Visibility menu item not found")
                return False
            time.sleep(0.5)

            # Step 3: Force-open the filter dialog (ADR-007)
            dialog_result = self.driver.execute_script("""
                const filterDialog = document.querySelector('ytcp-filter-dialog');
                if (!filterDialog) return {success: false, error: 'no filter dialog'};

                const paperDialog = filterDialog.querySelector('#dialog');
                if (!paperDialog) return {success: false, error: 'no paper dialog'};

                // Force open the dialog
                paperDialog.opened = true;
                paperDialog.setAttribute('opened', '');
                paperDialog.removeAttribute('aria-hidden');
                paperDialog.style.display = 'block';

                return {success: true};
            """)
            if not dialog_result.get('success'):
                logger.error(f"[DOM] Could not open filter dialog: {dialog_result.get('error')}")
                return False
            time.sleep(0.5)

            # Step 4: Find checkbox using ActionChains (ADR-006)
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
                logger.error(f"[DOM] Checkbox not found: {checkbox_coords.get('error')}")
                return False

            # ActionChains click at coordinates (required for ytcp-checkbox-lit)
            actions = ActionChains(self.driver)
            actions.move_by_offset(checkbox_coords['x'], checkbox_coords['y']).click().perform()
            actions.move_by_offset(-checkbox_coords['x'], -checkbox_coords['y']).perform()
            time.sleep(0.5)

            # Step 5: Find and click Apply button
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

            logger.info(f"[DOM] DOM fallback filter applied")
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
        self.wait_for_element(self.selectors.VISIBILITY_BTN)

    def edit_title(self, new_title: str):
        """Edit video title."""
        title_input = self.wait_for_element(
            self.selectors.TITLE_INPUT_XPATH, By.XPATH
        )
        title_input.click()
        title_input.send_keys(Keys.CONTROL + "a")  # Select all
        title_input.send_keys(new_title)

    def edit_description(self, new_description: str):
        """Edit video description."""
        desc_input = self.wait_for_element(
            self.selectors.DESCRIPTION_INPUT_XPATH, By.XPATH
        )
        desc_input.click()
        desc_input.send_keys(Keys.CONTROL + "a")  # Select all
        desc_input.send_keys(new_description)

    def click_save(self):
        """Click save button."""
        save_btn = self.wait_for_clickable(self.selectors.SAVE_BTN)
        self.safe_click(save_btn)
        import time
        time.sleep(1)  # Wait for save

    # =========================================
    # PAGE 3: SCHEDULING DIALOG METHODS
    # =========================================

    def open_visibility_dialog(self):
        """Open the visibility/scheduling dialog."""
        vis_btn = self.wait_for_clickable(
            self.selectors.VISIBILITY_BTN_XPATH, By.XPATH
        )
        self.safe_click(vis_btn)
        import time
        time.sleep(0.5)
        # Wait for dialog to appear
        self.wait_for_element(self.selectors.VISIBILITY_DIALOG)

    def select_schedule_option(self):
        """Select the 'Schedule' radio button in visibility dialog."""
        # First expand the schedule section if needed
        try:
            expand_btn = self.driver.find_element(
                By.XPATH, self.selectors.SCHEDULE_EXPAND
            )
            self.safe_click(expand_btn)
            import time
            time.sleep(0.3)
        except NoSuchElementException:
            pass  # Already expanded

        # Select schedule radio
        schedule_radio = self.wait_for_clickable(
            self.selectors.SCHEDULE_RADIO, By.XPATH
        )
        self.safe_click(schedule_radio)

    def set_schedule_date(self, date_str: str):
        """
        Set the schedule date.

        Args:
            date_str: Date string like "Jan 5, 2026"
        """
        # Click date picker to activate
        date_btn = self.wait_for_clickable(
            self.selectors.DATE_PICKER_BTN, By.XPATH
        )
        self.safe_click(date_btn)
        import time
        time.sleep(0.3)

        # Find and fill date input
        date_input = self.wait_for_element(
            self.selectors.DATE_INPUT, By.XPATH
        )
        date_input.send_keys(Keys.CONTROL + "a")
        date_input.send_keys(date_str)
        date_input.send_keys(Keys.ENTER)

    def set_schedule_time(self, time_str: str):
        """
        Set the schedule time.

        Args:
            time_str: Time string like "5:00 AM"
        """
        time_input = self.wait_for_element(
            self.selectors.TIME_INPUT_TEXTBOX, By.XPATH
        )
        time_input.click()
        time_input.send_keys(Keys.CONTROL + "a")
        time_input.send_keys(time_str)

    def click_done(self):
        """Click Done button to confirm scheduling."""
        done_btn = self.wait_for_clickable(
            self.selectors.DONE_BTN, By.XPATH
        )
        self.safe_click(done_btn)
        import time
        time.sleep(1)  # Wait for dialog to close

    def schedule_video(self, date_str: str, time_str: str) -> bool:
        """
        Full scheduling workflow for current video.

        Args:
            date_str: Date like "Jan 5, 2026"
            time_str: Time like "5:00 AM"

        Returns:
            True if successful
        """
        try:
            logger.info(f"[DOM] Scheduling for {date_str} at {time_str}")

            # Open dialog
            self.open_visibility_dialog()

            # Select schedule option
            self.select_schedule_option()

            # Set date
            self.set_schedule_date(date_str)

            # Set time
            self.set_schedule_time(time_str)

            # Confirm
            self.click_done()

            # Save changes
            self.click_save()

            logger.info(f"[DOM] Successfully scheduled for {date_str} {time_str}")
            return True

        except Exception as e:
            logger.error(f"[DOM] Scheduling failed: {e}")
            return False
