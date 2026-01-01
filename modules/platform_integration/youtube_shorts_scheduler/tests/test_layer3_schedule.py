"""
Layer 3 Test: Open Visibility Dialog and Schedule

Test the cake layer by layer:
1. Navigate to video edit page (uses Layer 1 + 2)
2. Click visibility button (ytcp-icon-button)
3. Select "Schedule" option
4. Set date and time
5. Click Done/Save

Run: python -m modules.platform_integration.youtube_shorts_scheduler.tests.test_layer3_schedule
"""

import time
import json
import logging
from datetime import datetime, timedelta
from urllib.parse import quote
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Import human behavior for natural mouse movements
try:
    from modules.infrastructure.foundups_selenium.src.human_behavior import get_human_behavior
    HUMAN_BEHAVIOR_AVAILABLE = True
except ImportError:
    HUMAN_BEHAVIOR_AVAILABLE = False
    print("[INFO] human_behavior module not available - using standard clicks")

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
    logger.info(f"[LAYER 3] Connecting to Chrome on port {CHROME_PORT}...")
    options = Options()
    options.add_experimental_option("debuggerAddress", f"127.0.0.1:{CHROME_PORT}")
    driver = webdriver.Chrome(options=options)
    logger.info(f"[LAYER 3] Connected!")
    return driver


def navigate_to_first_unlisted_video(driver):
    """Navigate to first unlisted video's edit page (Layer 1 + 2 combined)."""
    # Navigate to unlisted shorts
    filter_obj = [{"name": "VISIBILITY", "value": ["UNLISTED"]}]
    filter_param = quote(json.dumps(filter_obj))
    url = f"https://studio.youtube.com/channel/{CHANNEL_ID}/videos/short?filter={filter_param}"

    logger.info("[LAYER 3] Navigating to unlisted shorts...")
    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ytcp-video-row"))
        )
    except TimeoutException:
        logger.error("Video table not found")
        return False

    time.sleep(2)

    # Get first video URL
    video_rows = driver.find_elements(By.CSS_SELECTOR, "ytcp-video-row")
    if not video_rows:
        logger.error("No video rows found")
        return False

    links = video_rows[0].find_elements(By.CSS_SELECTOR, "a[href*='/video/']")
    if not links:
        logger.error("No video link found")
        return False

    edit_url = links[0].get_attribute("href")
    if "/edit" not in edit_url:
        edit_url = edit_url.rstrip("/") + "/edit"

    # Navigate to edit page
    logger.info(f"[LAYER 3] Navigating to edit page: {edit_url[:60]}...")
    driver.get(edit_url)
    time.sleep(3)

    return "/video/" in driver.current_url


def scan_edit_page_structure(driver):
    """Comprehensive scan of video edit page to find visibility/scheduling controls."""
    logger.info("[LAYER 3] Scanning edit page structure...")

    try:
        result = driver.execute_script("""
            const sections = {
                buttons: [],
                containers: [],
                dropdowns: [],
                status_elements: [],
                visibility_section: null,
                ytcp_elements: []
            };

            // Look specifically for visibility-related custom elements
            const visibilityElements = document.querySelectorAll('[class*="visibility"], [id*="visibility"], ytcp-video-metadata-visibility, ytcp-video-visibility-select');
            for (let el of visibilityElements) {
                sections.ytcp_elements.push({
                    tag: el.tagName,
                    class: el.className ? String(el.className).substring(0, 50) : '',
                    id: el.id || '',
                    children: el.children.length,
                    text: el.textContent.trim().substring(0, 100)
                });
            }

            // Look for the visibility section container
            const visSection = document.querySelector('ytcp-video-metadata-visibility');
            if (visSection) {
                sections.visibility_section = {
                    tag: visSection.tagName,
                    html: visSection.innerHTML.substring(0, 500),
                    buttons: visSection.querySelectorAll('button, ytcp-button, ytcp-icon-button').length
                };
            }

            // Find all buttons with useful text
            const buttons = document.querySelectorAll('button, ytcp-button, ytcp-icon-button');
            for (let btn of buttons) {
                if (btn.offsetParent !== null) {
                    sections.buttons.push({
                        tag: btn.tagName,
                        text: btn.textContent.trim().substring(0, 50),
                        aria: btn.getAttribute('aria-label') || '',
                        id: btn.id || ''
                    });
                }
            }

            // Find video metadata containers
            const containers = document.querySelectorAll('ytcp-video-metadata-editor, ytcp-video-metadata-editor-basics, [class*="metadata"], [class*="basics"]');
            for (let c of containers) {
                if (c.offsetParent !== null) {
                    sections.containers.push({
                        tag: c.tagName,
                        class: c.className.substring(0, 50),
                        text: c.textContent.trim().substring(0, 100)
                    });
                }
            }

            // Find dropdown triggers
            const dropdowns = document.querySelectorAll('ytcp-dropdown-trigger, tp-yt-paper-dropdown-menu, [role="combobox"], [role="listbox"]');
            for (let d of dropdowns) {
                if (d.offsetParent !== null) {
                    sections.dropdowns.push({
                        tag: d.tagName,
                        text: d.textContent.trim().substring(0, 50),
                        aria: d.getAttribute('aria-label') || ''
                    });
                }
            }

            // Find status/visibility related elements by looking for common patterns
            const statusPatterns = ['unlisted', 'public', 'private', 'scheduled', 'draft'];
            const allDivs = document.querySelectorAll('div, span');
            for (let el of allDivs) {
                if (el.offsetParent !== null) {
                    const text = el.textContent.trim().toLowerCase();
                    for (let pattern of statusPatterns) {
                        if (text === pattern || text.startsWith(pattern + ' ')) {
                            sections.status_elements.push({
                                tag: el.tagName,
                                text: el.textContent.trim().substring(0, 30),
                                parent: el.parentElement ? el.parentElement.tagName : ''
                            });
                            break;
                        }
                    }
                }
            }

            return sections;
        """)

        logger.info(f"  Buttons found: {len(result.get('buttons', []))}")
        for btn in result.get('buttons', [])[:15]:
            if btn['text'] or btn['aria']:
                logger.info(f"    - {btn['tag']}: '{btn['text'][:30]}' aria='{btn['aria'][:30]}'")

        logger.info(f"  Status elements found: {len(result.get('status_elements', []))}")
        for el in result.get('status_elements', []):
            logger.info(f"    - {el['tag']}: '{el['text']}' (parent: {el['parent']})")

        logger.info(f"  Dropdowns found: {len(result.get('dropdowns', []))}")
        for dd in result.get('dropdowns', [])[:5]:
            logger.info(f"    - {dd['tag']}: '{dd['text'][:30]}' aria='{dd['aria'][:30]}'")

        logger.info(f"  YTCP visibility elements: {len(result.get('ytcp_elements', []))}")
        for el in result.get('ytcp_elements', []):
            logger.info(f"    - {el['tag']}: id='{el['id']}' children={el['children']} text='{el['text'][:50]}'")

        if result.get('visibility_section'):
            vis = result['visibility_section']
            logger.info(f"  Visibility section found: {vis['buttons']} buttons inside")
            logger.info(f"    HTML preview: {vis['html'][:200]}...")

        return result
    except Exception as e:
        logger.error(f"  Scan failed: {e}")
        return {}


def click_visibility_status(driver):
    """Click the Unlisted status indicator to open visibility dialog."""
    logger.info("[LAYER 3] Looking for visibility select button...")

    # The visibility section has a specific button with id="select-button"
    # This is inside ytcp-video-metadata-visibility
    try:
        # First, scroll the visibility section into view
        scroll_result = driver.execute_script("""
            const visibilitySection = document.querySelector('ytcp-video-metadata-visibility');
            if (visibilitySection) {
                visibilitySection.scrollIntoView({behavior: 'smooth', block: 'center'});
                return {scrolled: true};
            }
            return {scrolled: false};
        """)
        logger.info(f"  Scroll result: {scroll_result}")
        time.sleep(1)

        # Now try clicking with different methods
        result = driver.execute_script("""
            const visibilitySection = document.querySelector('ytcp-video-metadata-visibility');
            if (!visibilitySection) {
                return {clicked: false, error: 'no visibility section'};
            }

            // Method 1: Find and click the select button
            const selectBtn = visibilitySection.querySelector('#select-button');
            if (selectBtn) {
                // Try dispatching a proper click event
                const clickEvent = new MouseEvent('click', {
                    view: window,
                    bubbles: true,
                    cancelable: true
                });
                selectBtn.dispatchEvent(clickEvent);
                return {clicked: true, method: 'dispatchEvent', tag: selectBtn.tagName,
                        aria: selectBtn.getAttribute('aria-label') || ''};
            }

            // Method 2: Try clicking the entire container
            const container = visibilitySection.querySelector('#container');
            if (container) {
                container.click();
                return {clicked: true, method: 'container-click'};
            }

            return {clicked: false, error: 'no clickable element found'};
        """)
        logger.info(f"  Click status result: {result}")

        # Also try Selenium's native ActionChains click
        from selenium.webdriver.common.action_chains import ActionChains
        try:
            # Find the select button using CSS selector
            select_btn = driver.find_element(By.CSS_SELECTOR, "ytcp-video-metadata-visibility #select-button")
            if select_btn and select_btn.is_displayed():
                logger.info("  Trying ActionChains click on select-button...")
                actions = ActionChains(driver)
                actions.move_to_element(select_btn)
                actions.click()
                actions.perform()
                logger.info("  ActionChains click performed!")
        except Exception as e:
            logger.info(f"  ActionChains click failed: {e}")

        if result and result.get('clicked'):
            time.sleep(3)  # Wait longer for any animation/transition

            # Check what appeared after clicking
            post_click = driver.execute_script("""
                const postClick = {
                    new_dialogs: [],
                    visibility_select: null,
                    dropdowns: [],
                    overlays: []
                };

                // Check for ytcp-video-visibility-select element
                const visSelect = document.querySelector('ytcp-video-visibility-select');
                if (visSelect && visSelect.offsetParent !== null) {
                    postClick.visibility_select = {
                        tag: visSelect.tagName,
                        text: visSelect.textContent.trim().substring(0, 200),
                        children: visSelect.children.length
                    };
                }

                // Check for iron-dropdown or any overlay
                const dropdowns = document.querySelectorAll('tp-yt-iron-dropdown, [role="listbox"], [class*="dropdown"]');
                for (let d of dropdowns) {
                    if (d.offsetParent !== null) {
                        postClick.dropdowns.push({
                            tag: d.tagName,
                            text: d.textContent.trim().substring(0, 100)
                        });
                    }
                }

                // Check for overlays or modals
                const overlays = document.querySelectorAll('[class*="overlay"], [class*="modal"], tp-yt-paper-dialog');
                for (let o of overlays) {
                    if (o.offsetParent !== null) {
                        postClick.overlays.push({
                            tag: o.tagName,
                            text: o.textContent.trim().substring(0, 100)
                        });
                    }
                }

                return postClick;
            """)
            logger.info(f"  Post-click scan:")
            logger.info(f"    visibility_select: {post_click.get('visibility_select')}")
            logger.info(f"    dropdowns: {post_click.get('dropdowns', [])}")
            logger.info(f"    overlays: {post_click.get('overlays', [])[:3]}")

            return True
    except Exception as e:
        logger.error(f"  Click status error: {e}")

    return False


def click_visibility_button(driver):
    """Click the visibility button to open dialog."""
    logger.info("[LAYER 3] Looking for visibility button...")

    # Use JavaScript to find and click the button
    try:
        clicked = driver.execute_script("""
            const buttons = document.querySelectorAll('ytcp-icon-button, button');
            for (let btn of buttons) {
                const aria = btn.getAttribute('aria-label') || '';
                if (aria.toLowerCase().includes('visibility') && btn.offsetParent !== null) {
                    btn.click();
                    return true;
                }
            }
            return false;
        """)

        if clicked:
            logger.info("[LAYER 3] Visibility button clicked!")
            time.sleep(1.5)  # Wait for dialog animation
            return True
    except Exception as e:
        logger.error(f"Click error: {e}")

    # Fallback: try direct selectors
    selectors = [
        "ytcp-icon-button[aria-label='Edit video visibility status']",
        "button[aria-label='Edit video visibility status']",
        "[aria-label*='visibility status']",
    ]

    for sel in selectors:
        try:
            elem = driver.find_element(By.CSS_SELECTOR, sel)
            if elem.is_displayed():
                driver.execute_script("arguments[0].click();", elem)
                time.sleep(1.5)
                return True
        except Exception:
            pass

    logger.error("Could not click visibility button")
    return False


def check_dialog_opened(driver):
    """Check if visibility dialog is open."""
    logger.info("[LAYER 3] Checking if dialog opened...")

    # Comprehensive scan of what's visible in any open dialog
    try:
        result = driver.execute_script("""
            const dialogInfo = {
                dialogs: [],
                radio_buttons: [],
                all_text_content: [],
                visibility_options: false,
                made_for_kids: false
            };

            // Find all dialogs
            const dialogs = document.querySelectorAll('tp-yt-paper-dialog, [role="dialog"], ytcp-video-visibility-select');
            for (let d of dialogs) {
                if (d.offsetParent !== null) {
                    dialogInfo.dialogs.push({
                        tag: d.tagName,
                        text: d.textContent.trim().substring(0, 200)
                    });
                }
            }

            // Find all radio buttons
            const radios = document.querySelectorAll('tp-yt-paper-radio-button, [role="radio"]');
            for (let r of radios) {
                if (r.offsetParent !== null) {
                    const text = r.textContent.trim();
                    dialogInfo.radio_buttons.push(text.substring(0, 50));

                    // Check for visibility options
                    const lower = text.toLowerCase();
                    if (lower.includes('public') || lower.includes('private') ||
                        lower.includes('unlisted') || lower.includes('schedule')) {
                        dialogInfo.visibility_options = true;
                    }
                    if (lower.includes('made for kids')) {
                        dialogInfo.made_for_kids = true;
                    }
                }
            }

            // Find any visible text containing schedule/public/private
            const allVisible = document.querySelectorAll('*');
            for (let el of allVisible) {
                if (el.offsetParent !== null && el.children.length === 0) {
                    const text = el.textContent.trim().toLowerCase();
                    if (text.includes('schedule') || text === 'public' ||
                        text === 'private' || text === 'unlisted' ||
                        text.includes('publish')) {
                        dialogInfo.all_text_content.push({
                            tag: el.tagName,
                            text: el.textContent.trim().substring(0, 40)
                        });
                    }
                }
            }

            return dialogInfo;
        """)

        logger.info(f"  Dialogs found: {len(result.get('dialogs', []))}")
        for d in result.get('dialogs', []):
            logger.info(f"    - {d['tag']}: '{d['text'][:60]}...'")

        logger.info(f"  Radio buttons: {result.get('radio_buttons', [])}")
        logger.info(f"  Visibility options found: {result.get('visibility_options', False)}")
        logger.info(f"  Made for kids dialog: {result.get('made_for_kids', False)}")
        logger.info(f"  Text containing schedule/visibility keywords: {len(result.get('all_text_content', []))}")
        for t in result.get('all_text_content', [])[:10]:
            logger.info(f"    - {t['tag']}: '{t['text']}'")

        # Return True if we found visibility options (not just Made for kids)
        if result.get('visibility_options'):
            return True
        if result.get('made_for_kids') and not result.get('visibility_options'):
            logger.warning("  Only 'Made for kids' dialog found - need to find actual visibility dialog")
            return False
        if result.get('dialogs'):
            return True

    except Exception as e:
        logger.error(f"  Dialog check error: {e}")

    logger.warning("  Dialog not detected")
    return False


def inspect_dialog_options(driver):
    """Inspect what options are available in the visibility dialog."""
    logger.info("[LAYER 3] Inspecting dialog options...")

    try:
        result = driver.execute_script("""
            const options = [];

            // Look for radio buttons
            const radios = document.querySelectorAll('tp-yt-paper-radio-button');
            for (let r of radios) {
                if (r.offsetParent !== null) {
                    options.push({
                        type: 'radio',
                        text: r.textContent.trim().substring(0, 50),
                        checked: r.hasAttribute('checked')
                    });
                }
            }

            // Look for any clickable items in dialog
            const dialog = document.querySelector('tp-yt-paper-dialog[aria-modal="true"]');
            if (dialog) {
                const buttons = dialog.querySelectorAll('button, ytcp-button');
                for (let b of buttons) {
                    if (b.offsetParent !== null) {
                        options.push({
                            type: 'button',
                            text: b.textContent.trim().substring(0, 30),
                            aria: b.getAttribute('aria-label') || ''
                        });
                    }
                }
            }

            return options;
        """)
        logger.info(f"  Dialog options: {json.dumps(result, indent=2)}")
        return result
    except Exception as e:
        logger.error(f"  Inspection error: {e}")
        return []


def scan_page_for_visibility_sections(driver):
    """Scan entire page for visibility/scheduling elements."""
    logger.info("[LAYER 3] Scanning page for visibility sections...")

    try:
        result = driver.execute_script("""
            const found = [];

            // Look for any element with visibility/schedule/publish text
            const keywords = ['visibility', 'schedule', 'publish', 'unlisted', 'private', 'public', 'save', 'done'];
            const allElements = document.querySelectorAll('*');

            for (let el of allElements) {
                const text = (el.textContent || '').toLowerCase();
                const aria = (el.getAttribute('aria-label') || '').toLowerCase();
                const id = (el.id || '').toLowerCase();
                const cls = (el.className || '').toLowerCase();

                for (let kw of keywords) {
                    if ((text.includes(kw) || aria.includes(kw) || id.includes(kw) || cls.includes(kw)) && el.offsetParent !== null) {
                        // Only include if it's likely interactive or a container
                        const tag = el.tagName;
                        if (['BUTTON', 'A', 'INPUT', 'SELECT', 'YTCP-BUTTON', 'YTCP-ICON-BUTTON',
                             'TP-YT-PAPER-RADIO-BUTTON', 'TP-YT-PAPER-DROPDOWN-MENU', 'DIV', 'SPAN',
                             'YTCP-VIDEO-VISIBILITY-SELECT', 'YTCP-DROPDOWN-TRIGGER'].includes(tag)) {
                            found.push({
                                tag: tag,
                                text: el.textContent.trim().substring(0, 60),
                                aria: aria.substring(0, 40),
                                id: el.id || '',
                                keyword: kw
                            });
                        }
                        break;
                    }
                }
            }

            // Deduplicate
            const unique = [];
            const seen = new Set();
            for (let f of found) {
                const key = f.tag + f.text + f.aria + f.id;
                if (!seen.has(key)) {
                    seen.add(key);
                    unique.push(f);
                }
            }

            return unique.slice(0, 25);
        """)
        logger.info(f"  Found {len(result)} visibility-related elements:")
        for item in result:
            logger.info(f"    {item['tag']}: '{item['text'][:30]}' (keyword: {item['keyword']})")
        return result
    except Exception as e:
        logger.error(f"  Scan error: {e}")
        return []


def select_schedule_option(driver):
    """Click the Schedule EXPAND button (#second-container-expand-button).
    
    DOM Structure found by browser subagent:
    - Schedule section is in #second-container
    - Expand button: ytcp-icon-button#second-container-expand-button
    - Aria-label: "Click to expand"
    """
    logger.info("[LAYER 3] Looking for Schedule expand button...")

    try:
        # Method 1: Click the specific expand button (most reliable)
        clicked = driver.execute_script("""
            // The Schedule expand button has a specific ID
            const expandBtn = document.querySelector('#second-container-expand-button');
            if (expandBtn && expandBtn.offsetParent !== null) {
                expandBtn.click();
                return {clicked: true, method: 'expand-button', aria: expandBtn.getAttribute('aria-label')};
            }
            
            // Method 2: Click the header container
            const header = document.querySelector('#second-container .early-access-header');
            if (header && header.offsetParent !== null) {
                header.click();
                return {clicked: true, method: 'header-click'};
            }
            
            // Method 3: Fallback - find element with "Schedule" text and click its header
            const scheduleText = document.querySelector('#visibility-title');
            if (scheduleText) {
                const header = scheduleText.closest('.early-access-header');
                if (header) {
                    header.click();
                    return {clicked: true, method: 'schedule-header'};
                }
            }
            
            return {clicked: false, error: 'expand button not found'};
        """)
        
        logger.info(f"  Click result: {clicked}")
        
        if clicked.get('clicked'):
            # CRITICAL: Wait for animation to complete
            logger.info("  Waiting 3s for Schedule section to expand...")
            time.sleep(3)
            
            # Validate: Check if date/time inputs are now visible
            validation = driver.execute_script("""
                const dateInput = document.querySelector('#datepicker-trigger input') ||
                                  document.querySelector('input[aria-label*="Date"]') ||
                                  document.querySelector('#second-container input');
                const timeInput = document.querySelector('#time-of-day-trigger input') ||
                                  document.querySelector('input[aria-label*="ime"]');
                return {
                    dateVisible: dateInput && dateInput.offsetParent !== null,
                    timeVisible: timeInput && timeInput.offsetParent !== null,
                    dateValue: dateInput ? dateInput.value : null,
                    timeValue: timeInput ? timeInput.value : null
                };
            """)
            logger.info(f"  [VALIDATE] Schedule inputs: {validation}")
            
            if validation.get('dateVisible') and validation.get('timeVisible'):
                logger.info("  [OK] Schedule section expanded - date/time inputs visible!")
                return True
            else:
                logger.warning("  [WARN] Schedule clicked but date/time not visible - may need scroll")
        
        return clicked.get('clicked', False)
        

    except Exception as e:
        logger.error(f"  Schedule click error: {e}")
        return False



def set_schedule_date_time(driver, date_str, time_str):
    """Set the schedule date and time with human-like behavior.
    
    Key fixes:
    - Uses Ctrl+A before typing to highlight existing text
    - Uses human_behavior for natural mouse movements
    """
    logger.info(f"[LAYER 3] Setting date to: {date_str}, time to: {time_str}")
    
    # Initialize human behavior if available
    human = None
    if HUMAN_BEHAVIOR_AVAILABLE:
        try:
            human = get_human_behavior(driver)
            logger.info("  [HUMAN] Using human-like mouse movements")
        except Exception as e:
            logger.warning(f"  [HUMAN] Could not init human behavior: {e}")
    
    try:
        # Step 1: Find and click date input
        date_input = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[aria-label*="Date"]'))
        )
        
        if date_input:
            logger.info("  [DATE] Found date input, clicking...")
            
            # Human-like click or standard click
            if human:
                human.human_click(date_input)
            else:
                ActionChains(driver).move_to_element(date_input).click().perform()
            
            time.sleep(0.5)
            
            # CRITICAL: Ctrl+A to select all existing text before typing
            logger.info("  [DATE] Selecting all existing text (Ctrl+A)...")
            ActionChains(driver).key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
            time.sleep(0.3)
            
            # Type the new date
            logger.info(f"  [DATE] Typing: {date_str}")
            if human:
                date_input.send_keys(date_str)  # human_type is too slow for dates
            else:
                date_input.send_keys(date_str)
            
            time.sleep(0.3)
            date_input.send_keys(Keys.ENTER)
            time.sleep(1)
            logger.info("  [DATE] ✅ Date set successfully")
        
        # Step 2: Find and click time input
        time_input = driver.find_element(By.CSS_SELECTOR, 'input[aria-label*="ime"]')  # time or Time
        
        if time_input:
            logger.info("  [TIME] Found time input, clicking...")
            
            if human:
                human.human_click(time_input)
            else:
                ActionChains(driver).move_to_element(time_input).click().perform()
            
            time.sleep(0.5)
            
            # CRITICAL: Ctrl+A to select all existing text before typing
            logger.info("  [TIME] Selecting all existing text (Ctrl+A)...")
            ActionChains(driver).key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
            time.sleep(0.3)
            
            # Type the new time (with AM/PM format for YouTube)
            logger.info(f"  [TIME] Typing: {time_str}")
            time_input.send_keys(time_str)
            time.sleep(0.3)
            time_input.send_keys(Keys.ENTER)
            time.sleep(1)
            logger.info("  [TIME] ✅ Time set successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"  [ERROR] Date/time setting failed: {e}")
        return False


def set_schedule_date(driver, date_str):
    """Legacy wrapper for set_schedule_date_time."""
    return set_schedule_date_time(driver, date_str, "5:00 PM")


def main():
    """Run Layer 3 test."""
    print("\n" + "="*60)
    print("LAYER 3 TEST: Open Visibility Dialog and Schedule")
    print("="*60 + "\n")

    driver = None
    try:
        # Step 1: Connect
        driver = connect_chrome()
        print("[OK] Connected to Chrome\n")

        # Step 2: Navigate to first unlisted video
        if not navigate_to_first_unlisted_video(driver):
            print("[FAIL] Could not navigate to video\n")
            return
        print("[OK] On video edit page\n")

        # Step 3: Scan page structure first
        print("[STEP 3] Scanning edit page structure...")
        page_structure = scan_edit_page_structure(driver)
        print(f"  Found {len(page_structure.get('buttons', []))} buttons")
        print(f"  Found {len(page_structure.get('status_elements', []))} status elements")
        print()

        # Step 4a: Try clicking the Unlisted status indicator first
        print("[STEP 4a] Trying to click Unlisted status indicator...")
        status_clicked = click_visibility_status(driver)
        if status_clicked:
            print("[OK] Unlisted status clicked\n")
        else:
            print("[INFO] Status click didn't work, trying visibility button...\n")
            # Step 4b: Fall back to visibility button
            if not click_visibility_button(driver):
                print("[FAIL] Could not click visibility button\n")
                return
            print("[OK] Visibility button clicked\n")

        # Step 5: Check dialog opened
        if not check_dialog_opened(driver):
            print("[WARN] Dialog detection uncertain\n")
        else:
            print("[OK] Visibility dialog opened\n")

        # Step 5: Inspect options
        options = inspect_dialog_options(driver)
        if options:
            print(f"[OK] Found {len(options)} dialog options\n")
            for opt in options[:5]:
                print(f"  - {opt.get('type')}: {opt.get('text', opt.get('aria', ''))[:40]}")
            print()

        # Step 5b: Close dialog and scan entire page
        print("[INFO] Dialog shows 'Made for kids' - need to find actual visibility section\n")

        # Step 6: Try to select Schedule (will click expand button and wait)
        print("[STEP 6] Clicking Schedule expand button...")
        if select_schedule_option(driver):
            print("[OK] Schedule section expanded\n")
            
            # Step 7: Set date and time with Ctrl+A before typing
            print("[STEP 7] Setting date and time...")
            target_date = datetime.now() + timedelta(days=7)
            date_str = target_date.strftime("%b %d, %Y")  # e.g., "Jan 08, 2026"
            time_str = "5:30 PM"
            
            if set_schedule_date_time(driver, date_str, time_str):
                print(f"[OK] Date/time set: {date_str} at {time_str}\n")
                
                # Step 8: Click Done button
                print("[STEP 8] Clicking Done button...")
                try:
                    done_btn = driver.execute_script("""
                        const buttons = document.querySelectorAll('ytcp-button, button');
                        for (let btn of buttons) {
                            const text = btn.textContent.toLowerCase().trim();
                            if ((text === 'done' || text === 'schedule') && 
                                btn.offsetParent !== null) {
                                btn.click();
                                return btn.textContent.trim();
                            }
                        }
                        return null;
                    """)
                    if done_btn:
                        print(f"[OK] Clicked: {done_btn}\n")
                        time.sleep(2)
                        
                        # Check final status
                        final_status = driver.execute_script("""
                            const visText = document.querySelector('#visibility-text');
                            return visText ? visText.textContent.trim() : 'unknown';
                        """)
                        print(f"[RESULT] Visibility status: {final_status}")
                    else:
                        print("[WARN] Done button not found\n")
                except Exception as e:
                    print(f"[ERROR] Done click failed: {e}")
            else:
                print("[FAIL] Could not set date/time\n")
        else:
            print("[INFO] Could not auto-select Schedule option\n")

        print("="*60)
        print("LAYER 3 TEST COMPLETE")
        print("="*60)

    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

    print("\n[INFO] Browser left open for inspection")


def run_with_visual_verification():
    """Run L3 test with WRE-TARS visual verification at each step."""
    from modules.infrastructure.foundups_selenium.src.wre_visual_runner import create_wre_runner
    
    print("\n" + "="*60)
    print("LAYER 3 TEST: WRE-TARS Visual Verification Mode")
    print("="*60 + "\n")
    
    driver = connect_chrome()
    print("[OK] Connected to Chrome\n")
    
    # Navigate to edit page first
    if not navigate_to_first_unlisted_video(driver):
        print("[FAIL] Could not navigate to video")
        return
    print("[OK] On video edit page\n")
    
    # Create WRE runner
    runner = create_wre_runner(
        driver=driver,
        skill_name="youtube_schedule_l3",
        use_uitars=True,
        use_pattern_memory=True
    )
    
    # Calculate target date
    target_date = datetime.now() + timedelta(days=9)
    date_str = target_date.strftime("%b %d, %Y")
    time_str = "5:30 PM"
    
    # Step-by-step with visual verification
    runner.step(
        "L3.1 Click Visibility",
        action=lambda: click_visibility_status(driver),
        verify_prompt="Is a visibility dialog or panel open showing visibility options?"
    )
    
    runner.step(
        "L3.2 Expand Schedule",
        action=lambda: select_schedule_option(driver),
        verify_prompt="Is the Schedule section expanded showing date and time input fields?"
    )
    
    runner.step(
        "L3.3 Set Date",
        action=lambda: set_schedule_date_time(driver, date_str, time_str),
        verify_prompt=f"Does the date input show '{date_str}' and time show '{time_str}'?"
    )
    
    # Print summary
    runner.print_summary()
    
    return runner.get_summary()


if __name__ == "__main__":
    import sys
    
    if "--wre-tars" in sys.argv:
        run_with_visual_verification()
    else:
        main()

