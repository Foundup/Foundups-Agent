"""
Layer 2 Test: Click Video → Open Edit Page

Test the cake layer by layer:
1. Connect to Chrome debug session (9222)
2. Navigate to Shorts page with Unlisted filter (via URL)
3. Click first video's edit link
4. Verify we're on the edit page
5. Find visibility button

Run: python -m modules.platform_integration.youtube_shorts_scheduler.tests.test_layer2_edit
"""

import time
import json
import logging
from urllib.parse import quote
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
    logger.info(f"[LAYER 2] Connecting to Chrome on port {CHROME_PORT}...")
    options = Options()
    options.add_experimental_option("debuggerAddress", f"127.0.0.1:{CHROME_PORT}")
    driver = webdriver.Chrome(options=options)
    logger.info(f"[LAYER 2] Connected! Current URL: {driver.current_url[:60]}...")
    return driver


def navigate_to_unlisted_shorts(driver):
    """Navigate to Shorts page with Unlisted filter via URL."""
    filter_obj = [{"name": "VISIBILITY", "value": ["UNLISTED"]}]
    filter_param = quote(json.dumps(filter_obj))
    url = f"https://studio.youtube.com/channel/{CHANNEL_ID}/videos/short?filter={filter_param}"

    logger.info(f"[LAYER 2] Navigating to unlisted shorts...")
    driver.get(url)

    # Wait for video table
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ytcp-video-row"))
        )
        logger.info("[LAYER 2] Video table loaded!")
        return True
    except TimeoutException:
        logger.error("[LAYER 2] Video table not found")
        return False


def get_first_video_edit_url(driver):
    """Get the edit URL for the first unlisted video."""
    logger.info("[LAYER 2] Looking for first video...")

    video_rows = driver.find_elements(By.CSS_SELECTOR, "ytcp-video-row")
    logger.info(f"  Found {len(video_rows)} video rows")

    if not video_rows:
        return None

    # Find edit link in first row
    first_row = video_rows[0]
    links = first_row.find_elements(By.CSS_SELECTOR, "a[href*='/video/'][href*='/edit']")

    if links:
        href = links[0].get_attribute("href")
        logger.info(f"  First video edit URL: {href}")
        return href

    # Fallback: look for any video link
    links = first_row.find_elements(By.CSS_SELECTOR, "a[href*='/video/']")
    if links:
        href = links[0].get_attribute("href")
        # Ensure it's an edit URL
        if "/edit" not in href:
            href = href + "/edit" if not href.endswith("/") else href + "edit"
        logger.info(f"  First video URL (modified): {href}")
        return href

    logger.error("  Could not find video link")
    return None


def navigate_to_video_edit(driver, edit_url):
    """Navigate to video edit page."""
    logger.info(f"[LAYER 2] Navigating to edit page...")
    driver.get(edit_url)

    time.sleep(2)  # Wait for page load

    # Verify we're on edit page
    if "/edit" in driver.current_url or "/video/" in driver.current_url:
        logger.info(f"[LAYER 2] On edit page: {driver.current_url[:60]}...")
        return True

    logger.error(f"[LAYER 2] Not on edit page: {driver.current_url}")
    return False


def find_visibility_button(driver):
    """Find the visibility/scheduling button on edit page."""
    logger.info("[LAYER 2] Looking for visibility button...")

    # Wait for page to fully load
    time.sleep(2)

    # Based on user's DOM analysis - look for Edit visibility button
    # The button has aria-label "Edit video visibility status"
    selectors = [
        "button[aria-label='Edit video visibility status']",
        "button[aria-label*='Edit video visibility']",
        "ytcp-button[aria-label*='visibility']",
        "#visibility-button",
        "[aria-label*='visibility status']",
    ]

    for sel in selectors:
        try:
            elems = driver.find_elements(By.CSS_SELECTOR, sel)
            if elems:
                for elem in elems:
                    if elem.is_displayed():
                        logger.info(f"  Found visibility button with: {sel}")
                        return elem
        except Exception:
            pass

    # XPath approach based on user's documentation
    xpath_selectors = [
        "//button[@aria-label='Edit video visibility status']",
        "//button[contains(@aria-label, 'visibility')]",
        "//ytcp-button[contains(., 'Visibility')]",
    ]

    for xpath in xpath_selectors:
        try:
            elem = driver.find_element(By.XPATH, xpath)
            if elem.is_displayed():
                logger.info(f"  Found visibility button with XPath: {xpath}")
                return elem
        except Exception:
            pass

    # Try JavaScript to find elements with "visibility" text anywhere
    logger.info("  Trying JavaScript deep search...")
    try:
        result = driver.execute_script("""
            // Search for any element containing "visibility" in various attributes
            const allElements = document.querySelectorAll('*');
            const found = [];
            for (let el of allElements) {
                const aria = el.getAttribute('aria-label') || '';
                const text = el.textContent || '';
                const isButton = el.tagName === 'BUTTON' || el.hasAttribute('role') && el.getAttribute('role') === 'button';

                if ((aria.toLowerCase().includes('visibility') || text.toLowerCase().includes('visibility'))
                    && isButton && el.offsetParent !== null) {
                    found.push({
                        tag: el.tagName,
                        aria: aria.substring(0, 50),
                        text: text.substring(0, 30),
                        visible: el.offsetParent !== null
                    });
                }
            }
            return found.slice(0, 5);
        """)
        logger.info(f"  JS deep search found: {result}")
        if result and len(result) > 0:
            return True
    except Exception as e:
        logger.info(f"  JS error: {e}")

    # List all visible buttons for debugging
    logger.info("  Listing all visible buttons...")
    try:
        buttons = driver.find_elements(By.TAG_NAME, "button")
        visible_buttons = [b for b in buttons if b.is_displayed()]
        logger.info(f"  Found {len(visible_buttons)} visible buttons")
        for i, btn in enumerate(visible_buttons[:15]):
            aria = btn.get_attribute("aria-label") or ""
            text = btn.text[:30] if btn.text else ""
            logger.info(f"    Button {i}: aria='{aria}' text='{text}'")
    except Exception as e:
        logger.info(f"  Button listing error: {e}")

    logger.warning("[LAYER 2] Could not find visibility button")
    return None


def main():
    """Run Layer 2 test."""
    print("\n" + "="*60)
    print("LAYER 2 TEST: Click Video → Open Edit Page")
    print("="*60 + "\n")

    driver = None
    try:
        # Step 1: Connect
        driver = connect_chrome()
        print("[OK] Connected to Chrome\n")

        # Step 2: Navigate to unlisted shorts
        if not navigate_to_unlisted_shorts(driver):
            print("[FAIL] Could not navigate to unlisted shorts\n")
            return
        print("[OK] Navigated to unlisted shorts\n")

        time.sleep(2)

        # Step 3: Get first video URL
        edit_url = get_first_video_edit_url(driver)
        if not edit_url:
            print("[FAIL] Could not find video edit URL\n")
            return
        print(f"[OK] Found video: {edit_url.split('/video/')[1].split('/')[0]}\n")

        # Step 4: Navigate to edit page
        if not navigate_to_video_edit(driver, edit_url):
            print("[FAIL] Could not navigate to edit page\n")
            return
        print("[OK] On video edit page\n")

        # Step 5: Find visibility button
        vis_btn = find_visibility_button(driver)
        if vis_btn:
            print("[OK] Found visibility button\n")
        else:
            print("[INFO] Visibility button not found via selectors\n")
            print("       May need to scroll or use different approach\n")

        print("="*60)
        print("LAYER 2 COMPLETE - On video edit page!")
        print(f"Current URL: {driver.current_url}")
        print("="*60)

    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

    print("\n[INFO] Browser left open for inspection")


def test_layer2_enhance():
    """
    Test Layer 2 enhancement workflow: extract title/description and enhance.
    
    Run: python -m modules.platform_integration.youtube_shorts_scheduler.tests.test_layer2_edit --enhance
    """
    print("\n" + "="*60)
    print("LAYER 2 ENHANCEMENT TEST")
    print("="*60 + "\n")

    try:
        driver = connect_chrome()
        print("[OK] Connected to Chrome\n")

        # Import enhancement functions
        from modules.platform_integration.youtube_shorts_scheduler.src.content_generator import (
            enhance_title, enhance_description
        )
        from modules.platform_integration.youtube_shorts_scheduler.src.dom_automation import YouTubeStudioDOM

        dom = YouTubeStudioDOM(driver)

        # Step 1: Navigate to unlisted shorts with URL filter
        print("[STEP 1] Navigating to unlisted shorts...")
        if not navigate_to_unlisted_shorts(driver):
            print("[FAIL] Navigation failed")
            return False
        print("[OK] On unlisted shorts page\n")
        time.sleep(2)

        # Step 2: Click edit on first video
        print("[STEP 2] Clicking edit on first video...")
        video_id = dom.click_first_video_edit_button()
        if not video_id:
            print("[FAIL] Could not click edit button")
            return False
        print(f"[OK] On edit page for video: {video_id}\n")
        time.sleep(2)

        # Step 3: Extract current title/description
        print("[STEP 3] Extracting current content...")
        current_title = dom.get_current_title()
        current_desc = dom.get_current_description()
        
        print(f"  CURRENT TITLE: {current_title[:60] if current_title else 'N/A'}...")
        print(f"  CURRENT DESC: {current_desc[:60] if current_desc else 'N/A'}...\n")

        # Step 4: Generate enhanced versions
        print("[STEP 4] Generating enhanced content...")
        enhanced_title = enhance_title(current_title or "Untitled")
        enhanced_desc = enhance_description(current_desc or "")
        
        print(f"  ENHANCED TITLE: {enhanced_title}")
        print(f"  ENHANCED DESC (first 100 chars):\n    {enhanced_desc[:100]}...\n")

        # Step 5: Show comparison
        print("="*60)
        print("BEFORE/AFTER COMPARISON")
        print("="*60)
        print("\n🔴 BEFORE:")
        print(f"  Title: {current_title}")
        print(f"  Desc: {current_desc[:80]}...")
        print("\n🟢 AFTER:")
        print(f"  Title: {enhanced_title}")
        print(f"  Desc: {enhanced_desc[:80]}...")
        print("="*60)

        # Note: NOT saving changes
        print("\n⚠️  CHANGES NOT SAVED - Preview only")
        print("To apply, use dom.set_title() and dom.set_description()")

        return True

    except Exception as e:
        logger.error(f"Enhancement test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import sys
    
    if "--enhance" in sys.argv:
        test_layer2_enhance()
    else:
        main()

