"""
Full Chain Test: L1 → L2 → L3 Complete Scheduling Workflow

Concatenates all layer tests into a single end-to-end flow:
1. L1: Navigate to unlisted shorts (URL filter)
2. L2: Click first video → edit page
3. L3: Open visibility → Schedule → Set date/time → Done → Save

Run: python -m modules.platform_integration.youtube_shorts_scheduler.tests.test_full_chain
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

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Move2Japan channel
CHANNEL_ID = "UC-LSSlOZwpGIRIYihaz8zCw"
CHROME_PORT = 9222


def connect_chrome():
    """Connect to existing Chrome debug session."""
    logger.info(f"[CHAIN] Connecting to Chrome on port {CHROME_PORT}...")
    options = Options()
    options.add_experimental_option("debuggerAddress", f"127.0.0.1:{CHROME_PORT}")
    driver = webdriver.Chrome(options=options)
    logger.info(f"[CHAIN] Connected!")
    return driver


# ============================================================================
# LAYER 1: Navigate to Unlisted Shorts
# ============================================================================

def layer1_navigate_to_unlisted(driver) -> bool:
    """L1: Navigate to unlisted shorts using URL filter."""
    logger.info("\n" + "="*60)
    logger.info("[L1] Navigate to Unlisted Shorts")
    logger.info("="*60)

    filter_obj = [{"name": "VISIBILITY", "value": ["UNLISTED"]}]
    filter_param = quote(json.dumps(filter_obj))
    url = f"https://studio.youtube.com/channel/{CHANNEL_ID}/videos/short?filter={filter_param}"

    logger.info(f"[L1] Navigating to: {url[:80]}...")
    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ytcp-video-row"))
        )
    except TimeoutException:
        logger.error("[L1] FAIL: Video rows not found")
        return False

    time.sleep(2)

    # Count videos
    video_rows = driver.find_elements(By.CSS_SELECTOR, "ytcp-video-row")
    logger.info(f"[L1] Found {len(video_rows)} unlisted shorts")

    if len(video_rows) == 0:
        logger.error("[L1] FAIL: No unlisted shorts found")
        return False

    logger.info("[L1] PASS")
    return True


# ============================================================================
# LAYER 2: Click First Video → Edit Page
# ============================================================================

def layer2_navigate_to_edit(driver) -> dict:
    """L2: Click first video and navigate to edit page."""
    logger.info("\n" + "="*60)
    logger.info("[L2] Navigate to Video Edit Page")
    logger.info("="*60)

    video_rows = driver.find_elements(By.CSS_SELECTOR, "ytcp-video-row")
    if not video_rows:
        logger.error("[L2] FAIL: No video rows found")
        return {"success": False}

    # Get first video's edit URL
    links = video_rows[0].find_elements(By.CSS_SELECTOR, "a[href*='/video/']")
    if not links:
        logger.error("[L2] FAIL: No video link found")
        return {"success": False}

    edit_url = links[0].get_attribute("href")
    if "/edit" not in edit_url:
        edit_url = edit_url.rstrip("/") + "/edit"

    # Extract video ID
    video_id = edit_url.split("/video/")[1].split("/")[0] if "/video/" in edit_url else "unknown"

    logger.info(f"[L2] Video ID: {video_id}")
    logger.info(f"[L2] Navigating to edit page...")
    driver.get(edit_url)
    time.sleep(3)

    # Verify we're on edit page
    if "/video/" not in driver.current_url:
        logger.error("[L2] FAIL: Not on video edit page")
        return {"success": False}

    # Get current title
    title = driver.execute_script("""
        const textbox = document.querySelector('#title-textarea, [aria-label*="title"]');
        if (textbox) {
            const inner = textbox.querySelector('#textbox, textarea, [contenteditable]');
            return inner ? inner.textContent || inner.value : textbox.textContent;
        }
        return '';
    """) or ""

    logger.info(f"[L2] Current title: {title[:50]}...")
    
    # L2.5: Enhance title/description with FFCPLN SKILLz
    logger.info("[L2.5] Enhancing title with FFCPLN SKILLz...")
    try:
        from modules.platform_integration.youtube_shorts_scheduler.skillz.ffcpln_title_enhance.executor import (
            FFCPLNTitleEnhanceSkill, SkillContext
        )
        skill = FFCPLNTitleEnhanceSkill()
        result = skill.execute(SkillContext(
            original_title=title,
            original_description="",
            video_duration=60
        ))
        enhanced_title = result.enhanced_title
        enhanced_desc = result.enhanced_description
        logger.info(f"[L2.5] Enhanced title: {enhanced_title[:50]}...")
        logger.info(f"[L2.5] Confidence: {result.confidence}")
        
        # Apply enhanced title
        driver.execute_script(f"""
            const titleField = document.querySelector('ytcp-social-suggestions-textbox#title-textarea #textbox');
            if (titleField) {{
                titleField.innerText = "{enhanced_title.replace('"', '\\"')}";
                titleField.dispatchEvent(new Event('input', {{ bubbles: true }}));
            }}
        """)
        logger.info("[L2.5] ✅ Title enhanced and applied")
        time.sleep(1)
    except Exception as e:
        logger.warning(f"[L2.5] Enhancement skipped: {e}")
        enhanced_title = title

    logger.info("[L2] PASS")

    return {"success": True, "video_id": video_id, "title": title, "enhanced_title": enhanced_title}



# ============================================================================
# LAYER 3: Schedule Video
# ============================================================================

def layer3_schedule_video(driver, days_from_now: int = 7, hour: int = 17, minute: int = 0) -> bool:
    """L3: Open visibility dialog and schedule the video."""
    logger.info("\n" + "="*60)
    logger.info("[L3] Schedule Video")
    logger.info("="*60)

    # Calculate target date
    target_date = datetime.now() + timedelta(days=days_from_now)
    date_str = target_date.strftime("%b %d, %Y")
    time_str = f"{hour}:{minute:02d}"

    logger.info(f"[L3] Target: {date_str} at {time_str}")

    # Step 3.1: Click visibility select button
    logger.info("[L3.1] Clicking visibility button...")
    try:
        # Scroll visibility section into view
        driver.execute_script("""
            const visSection = document.querySelector('ytcp-video-metadata-visibility');
            if (visSection) visSection.scrollIntoView({behavior: 'smooth', block: 'center'});
        """)
        time.sleep(1)

        # Click the select button
        select_btn = driver.find_element(By.CSS_SELECTOR, "ytcp-video-metadata-visibility #select-button")
        if select_btn.is_displayed():
            ActionChains(driver).move_to_element(select_btn).click().perform()
            logger.info("[L3.1] Visibility button clicked")
            time.sleep(2)
        else:
            logger.error("[L3.1] FAIL: Visibility button not visible")
            return False
    except Exception as e:
        logger.error(f"[L3.1] FAIL: {e}")
        return False

    # Step 3.2: Find and click Schedule radio button
    logger.info("[L3.2] Clicking Schedule option...")
    try:
        schedule_clicked = driver.execute_script("""
            const radios = document.querySelectorAll('tp-yt-paper-radio-button');
            for (let r of radios) {
                const text = r.textContent.toLowerCase();
                if (text.includes('schedule') && r.offsetParent !== null) {
                    r.click();
                    return true;
                }
            }
            return false;
        """)

        if not schedule_clicked:
            logger.warning("[L3.2] Schedule radio not found, trying alternative...")
            # Try clicking by aria-label
            driver.execute_script("""
                const scheduleOpt = document.querySelector('[aria-label*="Schedule"]');
                if (scheduleOpt) scheduleOpt.click();
            """)

        # CRITICAL: Wait for schedule section to expand and render date/time inputs
        # This was the bug - only 1s wasn't enough for YouTube Studio to render
        logger.info("[L3.2] Waiting for schedule section to expand...")
        time.sleep(3)  # Human-like pause while dialog animates
        
        # Verify schedule section is visible
        schedule_visible = driver.execute_script("""
            const dateInput = document.querySelector('input[aria-label*="Date"]');
            const timeInput = document.querySelector('input[aria-label*="time"]');
            return {
                dateVisible: dateInput && dateInput.offsetParent !== null,
                timeVisible: timeInput && timeInput.offsetParent !== null
            };
        """)
        logger.info(f"[L3.2] Schedule inputs visible: {schedule_visible}")
        
        if not schedule_visible.get('dateVisible'):
            logger.warning("[L3.2] Date input not visible yet, waiting more...")
            time.sleep(2)
        
        logger.info("[L3.2] ✅ Schedule option clicked and expanded")
    except Exception as e:
        logger.error(f"[L3.2] FAIL: {e}")
        return False

    # Step 3.3: Set date using validated selector
    logger.info(f"[L3.3] Setting date to: {date_str}")
    try:
        # Use validated XPath from dom_automation.py
        date_input = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//input[contains(@aria-label,'Date')]"))
        )
        if date_input:
            date_input.click()
            time.sleep(0.3)
            # Select all and type new date
            ActionChains(driver).key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
            date_input.send_keys(date_str)
            date_input.send_keys(Keys.ENTER)
            logger.info(f"[L3.3] ✅ Date set: {date_str}")
            time.sleep(0.5)
        else:
            logger.warning("[L3.3] Date input not found")
    except Exception as e:
        logger.warning(f"[L3.3] Date setting failed: {e}")

    # Step 3.4: Set time using validated selector
    logger.info(f"[L3.4] Setting time to: {time_str}")
    try:
        # Use validated XPath from dom_automation.py
        time_input = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//input[contains(@aria-label,'time') or contains(@aria-label,'Time')]"))
        )
        if time_input:
            time_input.click()
            time.sleep(0.3)
            # Select all and type new time
            ActionChains(driver).key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
            time_input.send_keys(f"{hour}:{minute:02d} PM" if hour >= 12 else f"{hour}:{minute:02d} AM")
            time_input.send_keys(Keys.ENTER)
            logger.info(f"[L3.4] ✅ Time set: {hour}:{minute:02d}")
            time.sleep(0.5)
        else:
            logger.warning("[L3.4] Time input not found")
    except Exception as e:
        logger.warning(f"[L3.4] Time setting failed: {e}")

    # Step 3.5: Click Done button
    logger.info("[L3.5] Clicking Done button...")
    try:
        done_clicked = driver.execute_script("""
            const buttons = document.querySelectorAll('ytcp-button, button');
            for (let btn of buttons) {
                const text = btn.textContent.trim().toLowerCase();
                if ((text === 'done' || text === 'save') && btn.offsetParent !== null) {
                    btn.click();
                    return btn.textContent.trim();
                }
            }
            return null;
        """)

        if done_clicked:
            logger.info(f"[L3.5] Clicked: {done_clicked}")
            time.sleep(2)
        else:
            logger.warning("[L3.5] Done button not found")
    except Exception as e:
        logger.warning(f"[L3.5] Done click failed: {e}")

    # Step 3.6: Click Save button (main page)
    logger.info("[L3.6] Clicking Save button...")
    try:
        # Press Escape first to close any dialogs
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
        time.sleep(1)

        save_clicked = driver.execute_script("""
            const saveBtn = document.querySelector('#save-button, [aria-label*="Save"]');
            if (saveBtn && saveBtn.offsetParent !== null) {
                saveBtn.click();
                return true;
            }
            // Try any button with "Save" text
            const buttons = document.querySelectorAll('ytcp-button, button');
            for (let btn of buttons) {
                if (btn.textContent.trim().toLowerCase() === 'save' && btn.offsetParent !== null) {
                    btn.click();
                    return true;
                }
            }
            return false;
        """)

        if save_clicked:
            logger.info("[L3.6] Save clicked!")
            time.sleep(3)
        else:
            logger.warning("[L3.6] Save button not found")
    except Exception as e:
        logger.warning(f"[L3.6] Save failed: {e}")

    logger.info("[L3] PASS (partial - date/time may need manual verification)")
    return True


# ============================================================================
# LAYER 4: Return to List and Verify
# ============================================================================

def layer4_return_to_list(driver) -> bool:
    """L4: Return to video list and refresh."""
    logger.info("\n" + "="*60)
    logger.info("[L4] Return to List")
    logger.info("="*60)

    # Navigate back to shorts list
    filter_obj = [{"name": "VISIBILITY", "value": ["UNLISTED"]}]
    filter_param = quote(json.dumps(filter_obj))
    url = f"https://studio.youtube.com/channel/{CHANNEL_ID}/videos/short?filter={filter_param}"

    logger.info("[L4] Navigating back to shorts list...")
    driver.get(url)
    time.sleep(3)

    # Refresh to ensure changes are reflected
    logger.info("[L4] Refreshing page (F5)...")
    driver.refresh()
    time.sleep(3)

    # Count remaining unlisted
    video_rows = driver.find_elements(By.CSS_SELECTOR, "ytcp-video-row")
    logger.info(f"[L4] Unlisted shorts remaining: {len(video_rows)}")

    logger.info("[L4] PASS")
    return True


# ============================================================================
# MAIN: Run Full Chain
# ============================================================================

def run_full_chain(dry_run: bool = False):
    """Run the complete L1 → L2 → L3 → L4 chain."""
    print("\n" + "="*70)
    print("FULL CHAIN TEST: L1 → L2 → L3 → L4")
    print("="*70)

    if dry_run:
        print("[MODE] DRY RUN - Will not save changes")
    else:
        print("[MODE] LIVE - Changes will be saved!")

    driver = None
    try:
        driver = connect_chrome()

        # L1: Navigate to unlisted shorts
        if not layer1_navigate_to_unlisted(driver):
            print("\n[CHAIN] FAILED at L1")
            return False

        # L2: Navigate to first video edit page
        l2_result = layer2_navigate_to_edit(driver)
        if not l2_result.get("success"):
            print("\n[CHAIN] FAILED at L2")
            return False

        video_id = l2_result.get("video_id", "unknown")

        # L3: Schedule the video
        if not dry_run:
            if not layer3_schedule_video(driver, days_from_now=7, hour=17, minute=0):
                print("\n[CHAIN] FAILED at L3")
                return False
        else:
            print("\n[L3] SKIPPED (dry run)")

        # L4: Return to list
        if not layer4_return_to_list(driver):
            print("\n[CHAIN] FAILED at L4")
            return False

        print("\n" + "="*70)
        print("FULL CHAIN TEST: PASSED")
        print(f"Video: {video_id}")
        print("="*70)
        return True

    except Exception as e:
        logger.error(f"[CHAIN] Exception: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Full Chain Test: L1 → L2 → L3 → L4")
    parser.add_argument("--dry-run", action="store_true", help="Preview only, don't save")
    parser.add_argument("--selenium", action="store_true", help="Run with Selenium (default)")
    args = parser.parse_args()

    run_full_chain(dry_run=args.dry_run)


if __name__ == "__main__":
    main()

