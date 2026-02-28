"""
YouTube "Go Live" Automation for antifaFM Broadcaster

Flow: YouTube Studio → livestreaming/stream → Go Live button
This activates the YouTube Live endpoint so FFmpeg can stream to it.

WSP Compliance:
- WSP 27: Universal DAE Architecture (Phase 2: Agentic execution)
- WSP 84: Code Reuse (studio_account_switcher patterns)
"""

import asyncio
import logging
import os
import time
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Chrome debug port (same as livechat DAE)
CHROME_DEBUG_PORT = int(os.getenv("FOUNDUPS_LIVECHAT_CHROME_PORT", "9222"))

# antifaFM channel - YouTube Studio URL (NOT public channel URL)
ANTIFAFM_CHANNEL_ID = "UCVSmg5aOhP4tnQ9KFUg97qA"
ANTIFAFM_STUDIO_LIVE_URL = f"https://studio.youtube.com/channel/{ANTIFAFM_CHANNEL_ID}/livestreaming/dashboard"


async def click_go_live(driver=None) -> Dict[str, Any]:
    """
    Navigate to YouTube Studio → livestreaming/stream → Click Go Live button.

    Uses existing Chrome session on debug port 9222.

    Args:
        driver: Optional Selenium WebDriver. If None, connects to debug port.

    Returns:
        Dict with success status and details
    """
    logger.info("[GO-LIVE] Starting YouTube Go Live automation for antifaFM...")

    try:
        # Get driver from debug port if not provided
        if driver is None:
            driver = _connect_to_chrome()
            if driver is None:
                return {"success": False, "error": "chrome_connection_failed"}

        # Step 1: Navigate directly to YouTube Studio livestreaming page
        logger.info(f"[GO-LIVE] Step 1/3: Navigating to {ANTIFAFM_STUDIO_LIVE_URL}")
        print(f"[RADIO] Navigating to YouTube Studio: {ANTIFAFM_STUDIO_LIVE_URL}")
        driver.get(ANTIFAFM_STUDIO_LIVE_URL)
        print("[RADIO] Waiting for page to load (5s)...")
        await asyncio.sleep(5)  # Studio loads slower

        # Debug: Print current URL and page title
        current_url = driver.current_url
        page_title = driver.title
        print(f"[RADIO] Page loaded: {page_title}")
        print(f"[RADIO] Current URL: {current_url}")

        # Step 2: Click CREATE button in header
        logger.info("[GO-LIVE] Step 2/3: Looking for Create button in header...")
        print("[RADIO] Step 2/3: Looking for CREATE button...")

        # Click the Create button (#create-icon in YouTube Studio header)
        create_result = driver.execute_script("""
            // Method 1: Look for #create-icon (most specific for YouTube Studio)
            const createIcon = document.querySelector('#create-icon, ytcp-button#create-icon');
            if (createIcon && createIcon.offsetParent !== null) {
                createIcon.click();
                return {clicked: true, method: '#create-icon'};
            }

            // Method 2: Look for button with "Create" aria-label
            const createLabels = document.querySelectorAll('[aria-label="Create"], [aria-label="Create a video or post"]');
            for (const btn of createLabels) {
                if (btn.offsetParent !== null) {
                    btn.click();
                    return {clicked: true, method: 'aria-label'};
                }
            }

            // Method 3: Look for ytcp-button with create in id or text
            const ytcpBtns = document.querySelectorAll('ytcp-button, ytcp-button-shape');
            for (const btn of ytcpBtns) {
                const text = (btn.textContent || '').toLowerCase().trim();
                const id = btn.id || '';
                if (text === 'create' || id.includes('create')) {
                    if (btn.offsetParent !== null) {
                        btn.click();
                        return {clicked: true, method: 'ytcp-button'};
                    }
                }
            }

            return {clicked: false};
        """)

        print(f"[RADIO] Create button result: {create_result}")

        if create_result.get('clicked'):
            print(f"[RADIO] SUCCESS: Clicked Create button ({create_result.get('method')})")

            # Step 2b: Poll for dropdown to appear (DOM verification, not fixed delay)
            dropdown_result = await _verify_dropdown_appeared(driver, timeout=5)

            if dropdown_result.get('visible'):
                logger.info(f"[GO-LIVE] Dropdown verified in {dropdown_result.get('elapsed', 0):.1f}s")
                print(f"[RADIO] Dropdown appeared ({dropdown_result.get('item_count', 0)} items, {dropdown_result.get('elapsed', 0):.1f}s)")
                logger.info("[GO-LIVE] Step 3/3: Clicking 'Go live' in dropdown...")
                print("[RADIO] Step 3/3: Looking for 'Go live' in dropdown...")
            else:
                print(f"[RADIO] WARNING: Dropdown not detected after {dropdown_result.get('elapsed', 5):.1f}s, trying Go Live anyway...")
        else:
            print("[RADIO] WARNING: Create button not found - trying Go Live directly...")

        go_live_result = driver.execute_script("""
            // Look for "Go live" option in dropdown/menu
            const menuItems = document.querySelectorAll('[role="menuitem"], [role="option"], tp-yt-paper-item, ytcp-text-menu a, a, button');
            for (const item of menuItems) {
                const text = (item.textContent || '').toLowerCase().trim();

                // Match "go live" exactly
                if (text === 'go live' || text.includes('go live')) {
                    if (item.offsetParent !== null) {
                        item.click();
                        return {clicked: true, text: 'Go live', method: 'menu'};
                    }
                }
            }

            // Also check for any visible "Go live" button (in case we're already on the right page)
            const buttons = document.querySelectorAll('button, ytcp-button, [role="button"]');
            for (const btn of buttons) {
                const text = (btn.textContent || '').toLowerCase().trim();
                const label = (btn.getAttribute('aria-label') || '').toLowerCase();

                if (text === 'go live' || text.includes('go live') ||
                    label.includes('go live')) {
                    if (btn.offsetParent !== null && !btn.disabled) {
                        btn.click();
                        return {clicked: true, text: btn.textContent.trim().substring(0, 40)};
                    }
                }
            }

            // Collect visible menu items for debugging
            const available = [];
            document.querySelectorAll('[role="menuitem"], [role="option"], tp-yt-paper-item, button, a').forEach(el => {
                const text = (el.textContent || '').trim();
                if (el.offsetParent !== null && text && text.length < 40) {
                    available.push(text.substring(0, 30));
                }
            });

            return {clicked: false, available: available.slice(0, 15), url: window.location.href};
        """)

        if go_live_result.get('clicked'):
            logger.info(f"[GO-LIVE] Go Live clicked: {go_live_result}")
            print(f"[RADIO] Go Live clicked: {go_live_result.get('text', 'OK')}")
            print("[RADIO] Waiting for stream studio to load (15s)...")
            await asyncio.sleep(15)  # Give studio time to fully load

            # Verify stream is now live
            final_url = driver.current_url
            logger.info(f"[GO-LIVE] Success! Stream studio loaded: {final_url}")
            return {
                "success": True,
                "url": final_url,
                "button_text": go_live_result.get('text')
            }
        else:
            # Button not found - maybe stream is already live?
            available = go_live_result.get('available', [])
            logger.warning(f"[GO-LIVE] Go Live button not found. Available buttons: {available}")
            print(f"[RADIO] Go Live button not found. Available: {available}")

            # Check if we're already on the live page (stream might be active)
            is_live = driver.execute_script("""
                // Check if stream appears to be live already
                const liveIndicator = document.querySelector('.live-indicator, [class*="live"], [data-status="live"]');
                const endButton = document.querySelector('button[aria-label*="end"], button[aria-label*="End"]');
                return {
                    live_indicator: !!liveIndicator,
                    has_end_button: !!endButton,
                    url: window.location.href
                };
            """)

            if is_live.get('live_indicator') or is_live.get('has_end_button'):
                logger.info("[GO-LIVE] Stream appears to already be live!")
                print("[RADIO] Stream appears to already be live!")
                return {"success": True, "already_live": True, "url": driver.current_url}

            return {"success": False, "error": "go_live_button_not_found", "available": available}

    except Exception as e:
        logger.error(f"[GO-LIVE] Error: {e}")
        return {"success": False, "error": str(e)}


async def edit_stream_settings(driver, title: str = None, description: str = None, timeout: int = 10) -> dict:
    """
    Edit stream title and description in YouTube Studio before going live.

    Args:
        driver: Selenium WebDriver
        title: New stream title (optional)
        description: New stream description (optional)
        timeout: Max seconds to wait for edit dialog

    Returns:
        dict with success status and what was changed
    """
    logger.info("[EDIT] Opening stream settings...")
    print("[RADIO] Opening stream settings...")

    try:
        # Step 1: Click "Edit" button - ytcp-button#edit-button
        # DOM: ytls-broadcast-metadata > ytcp-button#edit-button
        edit_result = driver.execute_script("""
            // Method 1: Direct ID selector (from DOM path)
            const editBtn = document.querySelector('ytcp-button#edit-button, #edit-button');
            if (editBtn && editBtn.offsetParent !== null) {
                editBtn.click();
                return {clicked: true, method: '#edit-button'};
            }

            // Method 2: Find button inside ytls-broadcast-metadata
            const metadata = document.querySelector('ytls-broadcast-metadata');
            if (metadata) {
                const btn = metadata.querySelector('ytcp-button, button');
                if (btn && btn.offsetParent !== null) {
                    btn.click();
                    return {clicked: true, method: 'ytls-broadcast-metadata'};
                }
            }

            // Method 3: Fallback - button with exact text "Edit"
            const allBtns = document.querySelectorAll('button, ytcp-button');
            for (const btn of allBtns) {
                const text = (btn.textContent || '').trim();
                if (text === 'Edit') {
                    if (btn.offsetParent !== null) {
                        btn.click();
                        return {clicked: true, method: 'text-Edit'};
                    }
                }
            }

            return {clicked: false};
        """)

        if not edit_result.get('clicked'):
            logger.warning("[EDIT] Edit button not found")
            print("[RADIO] WARNING: Edit button not found in studio")
            return {"success": False, "error": "edit_button_not_found"}

        print(f"[RADIO] Edit button clicked ({edit_result.get('method')})")

        # Step 2: Wait for edit panel/dialog to appear
        await asyncio.sleep(1.5)

        changes = {}

        # Step 3: Update title if provided
        # DOM: ytcp-video-title#title-wrapper > ytcp-social-suggestions-textbox#title-textarea
        if title:
            title_result = driver.execute_script("""
                const title = arguments[0];

                // Method 1: Direct ID selector from 012's DOM path
                // ytcp-social-suggestions-textbox#title-textarea > ytcp-form-input-container#container > div#outer
                const titleWrapper = document.querySelector('#title-wrapper, ytcp-video-title#title-wrapper');
                if (titleWrapper) {
                    const titleBox = titleWrapper.querySelector('#title-textarea, ytcp-social-suggestions-textbox#title-textarea');
                    if (titleBox) {
                        const container = titleBox.querySelector('#container, ytcp-form-input-container#container');
                        const input = container ? container.querySelector('input, textarea, #textbox, [contenteditable="true"]') : titleBox.querySelector('input, textarea, #textbox');
                        if (input && input.offsetParent !== null) {
                            input.focus();
                            if (input.select) input.select();
                            document.execCommand('selectAll', false, null);
                            document.execCommand('insertText', false, title);
                            return {updated: true, field: 'title', method: '#title-textarea'};
                        }
                    }
                }

                // Method 2: Direct #title-textarea selector
                const titleTextarea = document.querySelector('#title-textarea, ytcp-social-suggestions-textbox#title-textarea');
                if (titleTextarea) {
                    const input = titleTextarea.querySelector('input, textarea, #textbox, [contenteditable="true"]');
                    if (input && input.offsetParent !== null) {
                        input.focus();
                        if (input.select) input.select();
                        document.execCommand('selectAll', false, null);
                        document.execCommand('insertText', false, title);
                        return {updated: true, field: 'title', method: 'direct-#title-textarea'};
                    }
                }

                // Method 3: Fallback - aria-label or placeholder
                const titleInputs = document.querySelectorAll(
                    'input[aria-label*="Title"], textarea[aria-label*="Title"], ' +
                    '[contenteditable="true"][aria-label*="Title"]'
                );
                for (const input of titleInputs) {
                    if (input.offsetParent !== null) {
                        input.focus();
                        if (input.select) input.select();
                        document.execCommand('selectAll', false, null);
                        document.execCommand('insertText', false, title);
                        return {updated: true, field: 'title', method: 'aria-label'};
                    }
                }

                return {updated: false, reason: 'title_input_not_found'};
            """, title)

            if title_result.get('updated'):
                changes['title'] = title
                print(f"[RADIO] Title set: {title[:50]}...")
            else:
                print(f"[RADIO] WARNING: Could not update title")

        # Step 4: Update description if provided
        # DOM: ytcp-video-description#description-wrapper > ytcp-social-suggestions-textbox#description-textarea
        if description:
            desc_result = driver.execute_script("""
                const desc = arguments[0];

                // Method 1: Direct ID selector from 012's DOM path
                // ytcp-social-suggestions-textbox#description-textarea > ytcp-form-input-container#container
                const descWrapper = document.querySelector('#description-wrapper, ytcp-video-description#description-wrapper');
                if (descWrapper) {
                    const descBox = descWrapper.querySelector('#description-textarea, ytcp-social-suggestions-textbox#description-textarea');
                    if (descBox) {
                        const container = descBox.querySelector('#container, ytcp-form-input-container#container');
                        const textarea = container ? container.querySelector('textarea, #textbox, [contenteditable="true"]') : descBox.querySelector('textarea, #textbox');
                        if (textarea && textarea.offsetParent !== null) {
                            textarea.focus();
                            if (textarea.select) textarea.select();
                            document.execCommand('selectAll', false, null);
                            document.execCommand('insertText', false, desc);
                            return {updated: true, field: 'description', method: '#description-textarea'};
                        }
                    }
                }

                // Method 2: Direct #description-textarea selector
                const descTextarea = document.querySelector('#description-textarea, ytcp-social-suggestions-textbox#description-textarea');
                if (descTextarea) {
                    const textarea = descTextarea.querySelector('textarea, #textbox, [contenteditable="true"]');
                    if (textarea && textarea.offsetParent !== null) {
                        textarea.focus();
                        if (textarea.select) textarea.select();
                        document.execCommand('selectAll', false, null);
                        document.execCommand('insertText', false, desc);
                        return {updated: true, field: 'description', method: 'direct-#description-textarea'};
                    }
                }

                // Method 3: Fallback - aria-label or placeholder
                const descInputs = document.querySelectorAll(
                    'textarea[aria-label*="Description"], [contenteditable="true"][aria-label*="Description"]'
                );
                for (const input of descInputs) {
                    if (input.offsetParent !== null) {
                        input.focus();
                        if (input.select) input.select();
                        document.execCommand('selectAll', false, null);
                        document.execCommand('insertText', false, desc);
                        return {updated: true, field: 'description', method: 'aria-label'};
                    }
                }

                return {updated: false, reason: 'description_input_not_found'};
            """, description)

            if desc_result.get('updated'):
                changes['description'] = description[:100] + "..." if len(description) > 100 else description
                print(f"[RADIO] Description set: {description[:50]}...")
            else:
                print(f"[RADIO] WARNING: Could not update description")

        # Step 5: Save/close the edit dialog
        await asyncio.sleep(0.5)

        save_result = driver.execute_script("""
            // Method 1: Direct ID selector from 012's DOM path
            // ytcp-button#save-button
            const saveBtn = document.querySelector('#save-button, ytcp-button#save-button');
            if (saveBtn && saveBtn.offsetParent !== null) {
                saveBtn.click();
                return {saved: true, method: '#save-button'};
            }

            // Method 2: Look for button with exact text "Save"
            const allBtns = document.querySelectorAll('button, ytcp-button, [role="button"]');
            for (const btn of allBtns) {
                const text = (btn.textContent || '').trim();
                if (text === 'Save') {
                    if (btn.offsetParent !== null && !btn.disabled) {
                        btn.click();
                        return {saved: true, method: 'exact-text-Save'};
                    }
                }
            }

            // Method 3: Look for Save button with aria-label
            const saveBtns = document.querySelectorAll(
                'button[aria-label*="Save"], ytcp-button[aria-label*="Save"]'
            );
            for (const btn of saveBtns) {
                if (btn.offsetParent !== null && !btn.disabled) {
                    btn.click();
                    return {saved: true, method: 'aria-label-save'};
                }
            }

            // If no save button found, click outside to close (may auto-save)
            document.body.click();
            return {saved: false, auto_close: true};
        """)

        if save_result.get('saved'):
            print(f"[RADIO] Settings saved ({save_result.get('method')})")
        else:
            print("[RADIO] Settings may have auto-saved")

        await asyncio.sleep(1)

        return {
            "success": True,
            "changes": changes,
            "save_result": save_result
        }

    except Exception as e:
        logger.error(f"[EDIT] Error: {e}")
        return {"success": False, "error": str(e)}


async def verify_stream_connected(driver, timeout: int = 30) -> dict:
    """
    Verify stream is actually connected using DOM checks and visual verification.

    Polls YouTube Studio to confirm:
    - "Connect your encoder" message is GONE
    - Live indicator or video preview is visible

    Args:
        driver: Selenium WebDriver
        timeout: Max seconds to wait for connection

    Returns:
        dict with verified status
    """
    import time
    start = time.time()
    check_interval = 3  # Check every 3 seconds

    logger.info(f"[VERIFY] Waiting for stream to connect (max {timeout}s)...")
    print(f"[RADIO] Verifying stream connection (max {timeout}s)...")

    while (time.time() - start) < timeout:
        result = driver.execute_script("""
            // Check for "Connect your encoder" message (BAD - means not connected)
            const connectMsg = document.body.innerText.includes('Connect your encoder');

            // Check for live indicators (GOOD - means connected)
            const liveText = document.body.innerText.toLowerCase();
            const isLive = liveText.includes('you\\'re live') ||
                          liveText.includes('live now') ||
                          document.querySelector('[class*="live-indicator"]') !== null;

            // Check for video preview (canvas or video element with content)
            const preview = document.querySelector('video, canvas');
            const hasPreview = preview && preview.offsetWidth > 100;

            // Check for viewer count (indicates live)
            const viewerCount = document.querySelector('[class*="viewer"]');

            return {
                connect_encoder_visible: connectMsg,
                is_live: isLive,
                has_preview: !!hasPreview,
                has_viewer_count: !!viewerCount,
                elapsed: Math.round((Date.now() - window._verifyStart || Date.now()) / 1000)
            };
        """)

        # Set start time on first check
        driver.execute_script("window._verifyStart = window._verifyStart || Date.now();")

        logger.debug(f"[VERIFY] Check: {result}")

        # Success conditions
        if result.get('is_live') or (result.get('has_preview') and not result.get('connect_encoder_visible')):
            elapsed = time.time() - start
            logger.info(f"[VERIFY] Stream connected in {elapsed:.1f}s!")
            print(f"[RADIO] Stream connected! (verified in {elapsed:.1f}s)")
            return {"verified": True, "elapsed": elapsed, **result}

        # Still showing "Connect your encoder" - keep waiting
        if result.get('connect_encoder_visible'):
            logger.debug(f"[VERIFY] Still waiting for encoder... ({time.time() - start:.0f}s)")

        await asyncio.sleep(check_interval)

    # Timeout
    elapsed = time.time() - start
    logger.warning(f"[VERIFY] Timeout after {elapsed:.0f}s - stream may not be connected")
    print(f"[RADIO] WARNING: Stream verification timeout ({elapsed:.0f}s)")
    return {"verified": False, "timeout": True, "elapsed": elapsed}


async def _verify_dropdown_appeared(driver, timeout: int = 5) -> dict:
    """
    Poll DOM to verify Create dropdown menu appeared after click.

    Args:
        driver: Selenium WebDriver
        timeout: Max seconds to wait for dropdown

    Returns:
        dict with visibility status and item count
    """
    start = time.time()
    poll_interval = 0.3  # Check every 300ms

    while (time.time() - start) < timeout:
        result = driver.execute_script("""
            // Look for dropdown menu items (YouTube Studio uses these patterns)
            const menuItems = document.querySelectorAll(
                '[role="menuitem"], [role="option"], tp-yt-paper-item, ' +
                'ytcp-text-menu a, ytd-menu-service-item-renderer'
            );

            // Filter to only visible items
            const visibleItems = [];
            menuItems.forEach(item => {
                if (item.offsetParent !== null) {
                    const text = (item.textContent || '').trim();
                    if (text && text.length < 50) {
                        visibleItems.push(text.substring(0, 30));
                    }
                }
            });

            // Also check for "Go live" specifically
            const hasGoLive = visibleItems.some(t => t.toLowerCase().includes('go live'));

            return {
                visible: visibleItems.length > 0,
                item_count: visibleItems.length,
                has_go_live: hasGoLive,
                items: visibleItems.slice(0, 5)
            };
        """)

        if result.get('visible'):
            elapsed = time.time() - start
            logger.debug(f"[DROPDOWN] Detected in {elapsed:.1f}s: {result.get('items', [])}")
            return {"visible": True, "elapsed": elapsed, **result}

        await asyncio.sleep(poll_interval)

    # Timeout - dropdown didn't appear
    elapsed = time.time() - start
    logger.warning(f"[DROPDOWN] Not detected after {elapsed:.1f}s")
    return {"visible": False, "elapsed": elapsed, "item_count": 0}


def _connect_to_chrome():
    """Connect to existing Chrome via debug port, or launch if not running."""
    import socket

    # Quick check if port 9222 is open before trying Selenium
    def port_open(port, timeout=2):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            return result == 0
        except:
            return False

    print(f"[RADIO] Checking if Chrome is on port {CHROME_DEBUG_PORT}...")
    if not port_open(CHROME_DEBUG_PORT):
        logger.info(f"[GO-LIVE] Port {CHROME_DEBUG_PORT} not open, launching Chrome...")
        print(f"[RADIO] Chrome not running on port {CHROME_DEBUG_PORT}, launching...")
        return _launch_chrome()
    else:
        print(f"[RADIO] Chrome already on port {CHROME_DEBUG_PORT}")

    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options

        opts = Options()
        opts.add_experimental_option("debuggerAddress", f"127.0.0.1:{CHROME_DEBUG_PORT}")
        driver = webdriver.Chrome(options=opts)
        logger.info(f"[GO-LIVE] Connected to Chrome on port {CHROME_DEBUG_PORT}")
        return driver
    except Exception as e:
        logger.warning(f"[GO-LIVE] Chrome connection failed: {e}, launching...")

        return _launch_chrome()


def _launch_chrome():
    """Launch Chrome with debug port enabled."""
    import subprocess
    import time

    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    # Use the same profile as dependency_launcher (logged into YouTube)
    user_data = r"O:\Foundups-Agent\modules\platform_integration\browser_profiles\youtube_move2japan\chrome"

    try:
        print(f"[RADIO] Launching Chrome with debug port {CHROME_DEBUG_PORT}...")
        subprocess.Popen([
            chrome_path,
            f"--remote-debugging-port={CHROME_DEBUG_PORT}",
            f"--user-data-dir={user_data}",
            "--no-first-run",
            "https://www.youtube.com"
        ])

        logger.info(f"[GO-LIVE] Launched Chrome with debug port {CHROME_DEBUG_PORT}")
        print(f"[RADIO] Waiting for Chrome to start (5s)...")
        time.sleep(5)

        # Try connecting
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options

        opts = Options()
        opts.add_experimental_option("debuggerAddress", f"127.0.0.1:{CHROME_DEBUG_PORT}")
        driver = webdriver.Chrome(options=opts)
        logger.info(f"[GO-LIVE] Connected to newly launched Chrome")

        # Smart wait for login - check if user is logged in
        driver = _wait_for_login(driver)
        return driver

    except Exception as launch_error:
        logger.error(f"[GO-LIVE] Chrome launch failed: {launch_error}")
        print(f"[RADIO] ERROR: Chrome launch failed: {launch_error}")
        return None


def _wait_for_login(driver, max_wait=60):
    """Wait for user to log into YouTube if not already logged in."""
    import time

    def is_logged_in():
        try:
            result = driver.execute_script("""
                // Multiple ways to detect logged-in state on YouTube

                // 1. Avatar image in header (most reliable)
                const avatarImg = document.querySelector('img#avatar-btn, img.yt-spec-avatar-shape__image, #avatar img, button[aria-label*="Account"] img');
                if (avatarImg && avatarImg.offsetParent !== null) {
                    return {logged_in: true, method: 'avatar-img'};
                }

                // 2. Avatar button without img (fallback)
                const avatarBtn = document.querySelector('#avatar-btn, button#avatar-btn, [aria-label="Account menu"]');
                if (avatarBtn && avatarBtn.offsetParent !== null) {
                    return {logged_in: true, method: 'avatar-btn'};
                }

                // 3. User's channel/subscription links (indicates logged in)
                const yourChannel = document.querySelector('a[href*="/channel/"], a[title="Your channel"]');
                if (yourChannel && yourChannel.offsetParent !== null) {
                    return {logged_in: true, method: 'channel-link'};
                }

                // 4. "Sign in" button visible = NOT logged in
                const signInBtn = document.querySelector('a[href*="accounts.google.com/ServiceLogin"], ytd-button-renderer a[href*="signin"], [aria-label="Sign in"]');
                if (signInBtn && signInBtn.offsetParent !== null) {
                    return {logged_in: false, sign_in_visible: true};
                }

                // 5. No Sign in button and page loaded = probably logged in
                if (document.readyState === 'complete' && !signInBtn) {
                    return {logged_in: true, method: 'no-signin-btn'};
                }

                return {logged_in: false, sign_in_visible: false};
            """)
            return result.get('logged_in', False)
        except:
            return False

    # First check
    if is_logged_in():
        print("[RADIO] YouTube account logged in!")
        return driver

    # Not logged in - wait for user
    print("[RADIO] Waiting for YouTube login...")
    print("[RADIO] Please log into YouTube in the browser window")

    wait_intervals = [60, 120]  # 60s then 120s
    total_waited = 0

    for wait_time in wait_intervals:

        time.sleep(wait_time)
        total_waited += wait_time

        if is_logged_in():
            print("[RADIO] YouTube account logged in!")
            return driver

        print(f"[RADIO] Still waiting for login... ({total_waited}s)")

    print("[RADIO] WARNING: Login not detected, continuing anyway...")
    return driver


# CLI for OpenClaw/IronClaw programmatic access
if __name__ == "__main__":
    import sys
    import json

    logging.basicConfig(level=logging.INFO)

    def print_usage():
        print("""
YouTube Go Live CLI - antifaFM Broadcaster
For use by OpenClaw, IronClaw, or manual control

Usage:
  python youtube_go_live.py                       # Go live (default)
  python youtube_go_live.py --edit                # Open edit dialog only
  python youtube_go_live.py --title "Title"       # Set stream title
  python youtube_go_live.py --desc "Description"  # Set stream description
  python youtube_go_live.py --go-live             # Full flow: Go Live + Edit
  python youtube_go_live.py --json                # Output JSON (for agents)
  python youtube_go_live.py --status              # Check stream status only

Examples:
  # OpenClaw: Start stream with custom title
  python youtube_go_live.py --json --title "antifaFM Radio - Live Now"

  # IronClaw: Edit existing stream description
  python youtube_go_live.py --edit --json --desc "24/7 resistance music"

  # Full automation: Go live, set title and description
  python youtube_go_live.py --go-live --title "Morning Show" --desc "Live from the resistance"

Output (--json mode):
  {"success": true, "go_live": {...}, "edit": {...}}
  {"success": false, "error": "chrome_connection_failed"}
""")

    async def cli_main():
        args = sys.argv[1:]

        # Parse arguments
        title = None
        description = None
        do_go_live = len(args) == 0 or "--go-live" in args
        do_edit = "--edit" in args
        json_output = "--json" in args
        status_only = "--status" in args

        for i, arg in enumerate(args):
            if arg == "--title" and i + 1 < len(args):
                title = args[i + 1]
            elif arg == "--desc" and i + 1 < len(args):
                description = args[i + 1]
            elif arg == "--help" or arg == "-h":
                print_usage()
                return

        # Collect results for JSON output
        results = {"success": False}

        if not json_output:
            print("[RADIO] YouTube Go Live CLI (antifaFM)")
            print("=" * 50)
            print(f"[CONFIG] Chrome debug port: {CHROME_DEBUG_PORT}")
            print(f"[CONFIG] Studio URL: {ANTIFAFM_STUDIO_LIVE_URL}")
            print("=" * 50)

        # Connect to Chrome
        driver = _connect_to_chrome()
        if not driver:
            results["error"] = "chrome_connection_failed"
            if json_output:
                print(json.dumps(results))
            else:
                print("[ERROR] Could not connect to Chrome")
            return

        # Status check only
        if status_only:
            status = await verify_stream_connected(driver, timeout=5)
            results["status"] = status
            results["success"] = True
            if json_output:
                print(json.dumps(results))
            else:
                print(f"[STATUS] {status}")
            return

        # Step 1: Go Live (if requested or default)
        if do_go_live:
            if not json_output:
                print("\n[STEP 1] Going live...")
            go_live_result = await click_go_live(driver)
            results["go_live"] = go_live_result

            if not json_output:
                print(f"[RESULT] Go Live: {go_live_result}")

            if not go_live_result.get("success"):
                results["error"] = "go_live_failed"
                if json_output:
                    print(json.dumps(results))
                else:
                    print("[ERROR] Go Live failed, cannot edit stream")
                return

        # Step 2: Edit stream settings (if title/desc provided or --edit)
        if title or description or do_edit:
            if not json_output:
                print("\n[STEP 2] Editing stream settings...")
            edit_result = await edit_stream_settings(driver, title=title, description=description)
            results["edit"] = edit_result

            if not json_output:
                print(f"[RESULT] Edit: {edit_result}")

        results["success"] = True

        if json_output:
            print(json.dumps(results))
        else:
            print("\n[DONE] CLI complete")

    asyncio.run(cli_main())
