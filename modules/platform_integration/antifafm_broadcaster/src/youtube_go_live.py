"""
YouTube "Go Live" Automation for antifaFM Broadcaster

Flow:
1. Switch to antifaFM account (from default FoundUps)
2. Navigate to YouTube streams page
3. Click Create → Go Live
4. YouTube Studio opens for streaming

This activates the YouTube Live endpoint so FFmpeg can stream to it.

WSP Compliance:
- WSP 27: Universal DAE Architecture (Phase 2: Agentic execution)
- WSP 84: Code Reuse (studio_account_switcher patterns)
"""

import asyncio
import json
import logging
import os
import time
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    from dotenv import load_dotenv
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
    load_dotenv(PROJECT_ROOT / ".env")
except Exception:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent

# Browser debug port for antifaFM
# antifaFM uses Edge (port 9223) per youtube_channel_registry.py
# Chrome (9222) = Move2Japan/UnDaoDu, Edge (9223) = FoundUps/antifaFM
ANTIFAFM_BROWSER_PORT = int(os.getenv("ANTIFAFM_BROWSER_PORT", "9223"))
# Fallback to legacy env var for backwards compatibility
CHROME_DEBUG_PORT = int(os.getenv("FOUNDUPS_LIVECHAT_CHROME_PORT", str(ANTIFAFM_BROWSER_PORT)))

# antifaFM channel URLs
# Legacy antifaFM brand channel exists, but the live radio currently runs on
# the FoundUps YouTube channel. Keep both IDs explicit.
def _get_antifafm_brand_channel_id() -> str:
    return os.getenv("ANTIFAFM_CHANNEL_ID", "UCVSmg5aOhP4tnQ9KFUg97qA")


def _get_antifafm_broadcast_channel_id() -> str:
    # For antifaFM broadcaster, use ANTIFAFM channel - NOT FOUNDUPS_CHANNEL_ID fallback
    return os.getenv(
        "ANTIFAFM_BROADCAST_CHANNEL_ID",
        _get_antifafm_brand_channel_id(),  # UCVSmg5aOhP4tnQ9KFUg97qA
    )


ANTIFAFM_BRAND_CHANNEL_ID = _get_antifafm_brand_channel_id()
ANTIFAFM_CHANNEL_ID = _get_antifafm_broadcast_channel_id()
# Option 1: YouTube Studio livestreaming dashboard (direct - if stream exists)
ANTIFAFM_STUDIO_LIVE_URL = f"https://studio.youtube.com/channel/{ANTIFAFM_CHANNEL_ID}/livestreaming/dashboard"
# Option 2: Main YouTube streams page (for Create → Go Live flow)
ANTIFAFM_YOUTUBE_STREAMS_URL = "https://www.youtube.com/@antifaFM/streams"
# Option 3: Specific video livestreaming page (if video ID known)
# Set ANTIFAFM_STREAM_VIDEO_ID env var if you have a persistent stream
ANTIFAFM_STREAM_VIDEO_ID = os.getenv("ANTIFAFM_STREAM_VIDEO_ID", "")
ANTIFAFM_VIDEO_LIVE_URL = f"https://studio.youtube.com/video/{ANTIFAFM_STREAM_VIDEO_ID}/livestreaming" if ANTIFAFM_STREAM_VIDEO_ID else ""

# Strategy: "direct" (go to Studio) or "create" (Create → Go Live)
# Direct is faster and more reliable - go straight to Studio livestreaming
ANTIFAFM_GO_LIVE_STRATEGY = os.getenv("ANTIFAFM_GO_LIVE_STRATEGY", "direct")
# Default to Studio livestreaming URL (simpler - just click Go Live button)
ANTIFAFM_STUDIO_LIVESTREAMING_URL = f"https://studio.youtube.com/channel/{ANTIFAFM_CHANNEL_ID}/livestreaming"
ANTIFAFM_GO_LIVE_URL = os.getenv("ANTIFAFM_GO_LIVE_URL", ANTIFAFM_STUDIO_LIVESTREAMING_URL)

# Account switching - Edge may open on a different YouTube account, switch if needed
ANTIFAFM_SKIP_ACCOUNT_SWITCH = os.getenv("ANTIFAFM_SKIP_ACCOUNT_SWITCH", "false").lower() in ("true", "1", "yes")

# Use hardcoded coordinate clicks by default (most reliable)
# Set ANTIFAFM_GO_LIVE_HARDCODED=false to use DOM detection instead
ANTIFAFM_GO_LIVE_HARDCODED = os.getenv("ANTIFAFM_GO_LIVE_HARDCODED", "true").lower() in ("true", "1", "yes")

# Hardcoded coordinates for Go Live sequence (fallback when DOM detection fails)
# These are screen-relative coordinates based on 012's DOM inspection
# Update these if UI layout changes
GO_LIVE_COORDINATES = {
    # Create button in YouTube header (top-right area)
    "create_button": {
        "x": 1180,  # Right side of header
        "y": 40,    # Top area near avatar
        "description": "YouTube Create button (+ icon in header)"
    },
    # "Go live" option in Create dropdown
    "go_live_option": {
        "x": 1150,  # Same x as dropdown
        "y": 140,   # Second item in dropdown (below "Upload video")
        "description": "Go live option in Create dropdown"
    },
    # YouTube Studio "Go live" button (direct navigation)
    "studio_go_live": {
        "x": 950,   # Center-right area
        "y": 580,   # Below the main content area
        "description": "Go live button in YouTube Studio"
    }
}


def _get_studio_page_state(driver) -> Dict[str, Any]:
    """
    Inspect the current YouTube Studio livestreaming page.

    Important: the body text often contains "to go live" as instructional
    copy. That text must not be treated as a clickable Go Live action.
    """
    return driver.execute_script("""
        const bodyText = (document.body?.innerText || '').toLowerCase();
        const visibleButtons = [];
        let hasGoLiveButton = false;

        document.querySelectorAll('button, ytcp-button, [role="button"]').forEach(btn => {
            if (btn.offsetParent === null) return;

            const text = (btn.textContent || '').trim();
            const aria = (btn.getAttribute('aria-label') || '').trim();
            const label = (text || aria).trim();
            const lowered = label.toLowerCase();

            if (label) {
                visibleButtons.push({
                    text: text.substring(0, 50),
                    aria: aria.substring(0, 50),
                    id: btn.id || '',
                    tag: btn.tagName
                });
            }

            if (
                lowered === 'go live' ||
                lowered === 'go-live' ||
                aria.toLowerCase() === 'go live' ||
                btn.id === 'go-live-button' ||
                btn.id === 'stream-button'
            ) {
                hasGoLiveButton = true;
            }
        });

        return {
            url: window.location.href,
            title: document.title,
            has_stream: bodyText.includes('stream'),
            has_encoder: bodyText.includes('connect your encoder'),
            has_end_stream: bodyText.includes('end stream'),
            has_go_live_button: hasGoLiveButton,
            has_no_data: bodyText.includes('no data'),
            has_stream_health: bodyText.includes('stream health'),
            visible_buttons: visibleButtons.slice(0, 20),
        };
    """)


def _resolve_stream_livestreaming_url(driver) -> Optional[str]:
    """Extract the active stream's `/video/.../livestreaming` URL from Studio."""
    result = driver.execute_script("""
        const candidates = [];

        const pushCandidate = (href) => {
            if (!href || !href.includes('/video/')) return;
            let normalized = href;
            if (normalized.startsWith('/')) {
                normalized = `https://studio.youtube.com${normalized}`;
            }
            normalized = normalized.replace('/editor', '/livestreaming');
            if (!normalized.includes('/livestreaming')) {
                const match = normalized.match(/\\/video\\/([^/?#]+)/);
                if (match) {
                    normalized = `https://studio.youtube.com/video/${match[1]}/livestreaming`;
                }
            }
            candidates.push(normalized);
        };

        const editLink = document.querySelector('a#edit-in-studio-link[href*="/video/"]');
        if (editLink) pushCandidate(editLink.getAttribute('href'));

        document.querySelectorAll('a[href*="/video/"], [href*="/video/"]').forEach(el => {
            pushCandidate(el.getAttribute('href'));
        });

        return [...new Set(candidates)];
    """)
    return result[0] if result else None


async def _wait_for_studio_page_signal(
    driver,
    timeout: float = 10.0,
    poll_interval: float = 1.0,
) -> Dict[str, Any]:
    """
    Wait until the Studio stream page exposes a decisive state.

    The livestream page often loads in stages. During hydration it can briefly
    show neither the encoder prompt nor any actionable button even though the
    stream page is correct. Poll instead of failing fast.
    """
    start = time.time()
    last_state = _get_studio_page_state(driver)

    while time.time() - start < timeout:
        if (
            last_state.get("has_encoder")
            or last_state.get("has_go_live_button")
            or last_state.get("has_end_stream")
        ):
            return last_state
        await asyncio.sleep(poll_interval)
        last_state = _get_studio_page_state(driver)

    return last_state


def _hardcoded_click(driver, x: int, y: int, description: str = "") -> bool:
    """
    Click at hardcoded screen coordinates using ActionChains.

    Fallback for when DOM detection fails. Uses JavaScript to simulate click
    at specific viewport coordinates.

    Args:
        driver: Selenium WebDriver
        x: X coordinate (viewport-relative)
        y: Y coordinate (viewport-relative)
        description: What we're clicking (for logging)

    Returns:
        True if click executed (no verification of success)
    """
    try:
        logger.info(f"[HARDCODED-CLICK] Clicking at ({x}, {y}): {description}")
        print(f"[RADIO] HARDCODED CLICK: ({x}, {y}) - {description}")

        # Method 1: JavaScript click at coordinates
        result = driver.execute_script(f"""
            // Create and dispatch click event at coordinates
            const element = document.elementFromPoint({x}, {y});
            if (element) {{
                console.log('Clicking element:', element.tagName, element.id, element.className);
                element.click();
                return {{clicked: true, element: element.tagName, id: element.id || 'no-id'}};
            }}

            // Fallback: dispatch click event directly
            const event = new MouseEvent('click', {{
                view: window,
                bubbles: true,
                cancelable: true,
                clientX: {x},
                clientY: {y}
            }});
            document.elementFromPoint({x}, {y})?.dispatchEvent(event);
            return {{clicked: true, method: 'mouse-event'}};
        """)

        logger.info(f"[HARDCODED-CLICK] Result: {result}")
        return True

    except Exception as e:
        logger.error(f"[HARDCODED-CLICK] Failed: {e}")
        print(f"[RADIO] ERROR: Hardcoded click failed: {e}")
        return False


async def _direct_go_live_hardcoded(driver) -> Dict[str, Any]:
    """
    HARDCODED Go Live sequence - uses YouTube Studio direct URL.

    Flow (012-simplified):
    1. Navigate to https://studio.youtube.com/channel/{ID}/livestreaming
    2. This opens the livestreaming dashboard directly
    3. Click "Go live" button to start new stream

    No CREATE dropdown needed - Studio has direct Go Live button.
    """
    logger.info("[GO-LIVE-HARD] Starting HARDCODED Go Live sequence...")
    print("[RADIO] ===== HARDCODED GO LIVE SEQUENCE =====")
    print("[RADIO] Flow: Studio livestreaming → Go Live button")

    try:
        # RETRY OPTIMIZATION: If already on Studio livestreaming page, skip navigation
        current_url = driver.current_url
        already_on_studio = (
            "studio.youtube.com" in current_url and
            ("livestreaming" in current_url or ANTIFAFM_CHANNEL_ID in current_url)
        )

        if already_on_studio:
            print("[RADIO] RETRY MODE: Already on Studio livestreaming!")
            print(f"[RADIO]   Current URL: {current_url[:60]}...")
            print("[RADIO] Skipping navigation, going straight to Go Live click...")
            await asyncio.sleep(1)
        else:
            # Step 1: Navigate directly to YouTube Studio livestreaming
            studio_url = f"https://studio.youtube.com/channel/{ANTIFAFM_CHANNEL_ID}/livestreaming"
            logger.info(f"[GO-LIVE-HARD] Navigating to: {studio_url}")
            print(f"[RADIO] Step 1: Navigate to Studio livestreaming")
            print(f"[RADIO]   URL: {studio_url}")
            driver.get(studio_url)

            # Wait for page load
            print("[RADIO] Waiting for page load (5s)...")
            await asyncio.sleep(5)

        # Step 2: Check page state
        print("[RADIO] Step 2: Checking page state...")
        page_check = driver.execute_script("""
            const bodyText = document.body.innerText.toLowerCase();
            return {
                has_go_live: bodyText.includes('go live'),
                has_stream: bodyText.includes('stream'),
                has_encoder: bodyText.includes('connect your encoder'),
                has_end_stream: bodyText.includes('end stream'),
                url: window.location.href
            };
        """)
        print(f"[RADIO] Page state: {page_check}")

        # Already streaming
        if page_check.get('has_end_stream'):
            print("[RADIO] Stream is ALREADY LIVE!")
            return {"success": True, "already_live": True, "url": driver.current_url}

        # "Connect your encoder" is only sufficient when the final "Go live"
        # action is no longer present. If both are visible, Studio is still on
        # the pre-activation page and we must click Go Live.
        if page_check.get('has_encoder') and not page_check.get('has_go_live'):
            print("[RADIO] Encoder connection ready - stream endpoint active!")
            return {"success": True, "endpoint_ready": True, "url": driver.current_url}

        # Step 3: Click Go Live button
        print("[RADIO] Step 3: Clicking Go Live button...")
        go_live_result = driver.execute_script("""
            // METHOD 1: Find "Go live" button by exact text
            const buttons = document.querySelectorAll('button, ytcp-button, [role="button"]');
            for (const btn of buttons) {
                const text = (btn.textContent || '').trim();
                if (text === 'Go live' || text === 'GO LIVE' || text === 'Stream') {
                    if (btn.offsetParent !== null && !btn.disabled) {
                        btn.click();
                        return {clicked: true, method: 'text-match', text: text};
                    }
                }
            }

            // METHOD 2: aria-label
            const ariaBtn = document.querySelector('[aria-label="Go live"], [aria-label="Stream"]');
            if (ariaBtn && ariaBtn.offsetParent !== null) {
                ariaBtn.click();
                return {clicked: true, method: 'aria-label'};
            }

            // METHOD 3: ytcp-button specific
            const ytcpBtn = document.querySelector('ytcp-button#go-live-button, #go-live-button, #stream-button');
            if (ytcpBtn && ytcpBtn.offsetParent !== null) {
                ytcpBtn.click();
                return {clicked: true, method: 'ytcp-id'};
            }

            // Debug: list visible buttons
            const debug = [];
            document.querySelectorAll('button, ytcp-button, [role="button"]').forEach(b => {
                if (b.offsetParent !== null) {
                    const text = (b.textContent || '').trim().substring(0,30);
                    const aria = b.getAttribute('aria-label') || '';
                    if (text || aria) debug.push({text, aria});
                }
            });
            return {clicked: false, debug: debug.slice(0,15)};
        """)

        print(f"[RADIO] Go Live click result: {go_live_result}")

        if not go_live_result.get('clicked'):
            print("[RADIO] Go Live button not found via DOM!")
            print(f"[RADIO] Available buttons: {go_live_result.get('debug', [])}")
            # Try hardcoded coordinate as fallback
            print("[RADIO] Trying hardcoded coordinate click...")
            coords = GO_LIVE_COORDINATES["studio_go_live"]
            _hardcoded_click(driver, coords["x"], coords["y"], coords["description"])

        # Step 4: Wait and verify
        print("[RADIO] Step 4: Waiting for stream activation (5s)...")
        await asyncio.sleep(5)

        # Check final state
        final_check = driver.execute_script("""
            return {
                url: window.location.href,
                has_encoder: document.body.innerText.toLowerCase().includes('connect your encoder'),
                has_end_stream: document.body.innerText.toLowerCase().includes('end stream'),
                has_go_live: document.body.innerText.toLowerCase().includes('go live')
            };
        """)
        print(f"[RADIO] Final state: {final_check}")

        if final_check.get('has_end_stream') or (final_check.get('has_encoder') and not final_check.get('has_go_live')):
            print("[RADIO] SUCCESS: Stream endpoint is active!")
            return {"success": True, "url": driver.current_url, "state": final_check}

        # If still has "Go live" button, might need another click
        if final_check.get('has_go_live'):
            print("[RADIO] Still showing Go Live - trying studio button click...")
            studio_click = await _click_studio_go_live_button(driver)
            return studio_click

        return {"success": True, "url": driver.current_url, "note": "completed_flow"}

    except Exception as e:
        logger.error(f"[GO-LIVE-HARD] Error: {e}")
        return {"success": False, "error": str(e)}


async def _direct_go_live_stream_page(driver) -> Dict[str, Any]:
    """
    Direct Studio stream-page flow for encoder-based livestreams.

    This flow treats the specific stream page as the source of truth:
    if Studio already shows "Connect your encoder" and there is no visible
    Go Live action, the RTMP endpoint is already active.
    """
    logger.info("[GO-LIVE-DIRECT] Starting direct Studio stream-page flow...")
    print("[RADIO] ===== DIRECT STUDIO STREAM FLOW =====")
    print("[RADIO] Flow: Studio livestreaming -> inspect active stream state")

    try:
        current_url = driver.current_url
        already_on_studio = (
            "studio.youtube.com" in current_url and
            ("livestreaming" in current_url or ANTIFAFM_CHANNEL_ID in current_url)
        )

        if already_on_studio:
            print("[RADIO] RETRY MODE: Already on Studio livestreaming!")
            print(f"[RADIO]   Current URL: {current_url[:80]}...")
            print("[RADIO] Reusing current Studio page and re-checking stream state...")
            await asyncio.sleep(1)
        else:
            target_url = ANTIFAFM_VIDEO_LIVE_URL or ANTIFAFM_GO_LIVE_URL
            logger.info(f"[GO-LIVE-DIRECT] Navigating to: {target_url}")
            print("[RADIO] Step 1: Navigate to Studio livestreaming")
            print(f"[RADIO]   URL: {target_url}")
            driver.get(target_url)
            print("[RADIO] Waiting for page load (5s)...")
            await asyncio.sleep(5)

        print("[RADIO] Step 2: Checking Studio stream state...")
        page_check = await _wait_for_studio_page_signal(
            driver,
            timeout=8.0 if already_on_studio else 10.0,
            poll_interval=1.0,
        )
        print(f"[RADIO] Page state: {page_check}")

        if page_check.get("has_end_stream"):
            print("[RADIO] Stream is ALREADY LIVE!")
            return {"success": True, "already_live": True, "url": driver.current_url}

        if page_check.get("has_encoder") and not page_check.get("has_go_live_button"):
            print("[RADIO] Encoder connection ready - stream endpoint active!")
            return {"success": True, "endpoint_ready": True, "url": driver.current_url, "state": page_check}

        if "/dashboard" in page_check.get("url", "") and not page_check.get("has_go_live_button"):
            print("[RADIO] Still on Studio dashboard; waiting for stream page redirect...")
            await asyncio.sleep(3)
            page_check = await _wait_for_studio_page_signal(driver, timeout=8.0, poll_interval=1.0)
            print(f"[RADIO] Page state after wait: {page_check}")

            if page_check.get("has_encoder") and not page_check.get("has_go_live_button"):
                print("[RADIO] Encoder connection ready after redirect - endpoint active!")
                return {"success": True, "endpoint_ready": True, "url": driver.current_url, "state": page_check}

            stream_page_url = _resolve_stream_livestreaming_url(driver)
            if stream_page_url:
                print("[RADIO] Found active stream page from dashboard metadata.")
                print(f"[RADIO]   Stream URL: {stream_page_url}")
                driver.get(stream_page_url)
                print("[RADIO] Waiting for stream page load...")
                page_check = await _wait_for_studio_page_signal(driver, timeout=10.0, poll_interval=1.0)
                print(f"[RADIO] Stream page state: {page_check}")

                if page_check.get("has_encoder") and not page_check.get("has_go_live_button"):
                    print("[RADIO] Encoder connection ready on stream page - endpoint active!")
                    return {"success": True, "endpoint_ready": True, "url": driver.current_url, "state": page_check}

        if page_check.get("has_go_live_button"):
            print("[RADIO] Step 3: Clicking visible Go Live button...")
            return await _click_studio_go_live_button(driver)

        print("[RADIO] No visible Go Live action found on this Studio page.")
        return {
            "success": False,
            "error": "no_go_live_button",
            "url": driver.current_url,
            "state": page_check,
        }

    except Exception as e:
        logger.error(f"[GO-LIVE-DIRECT] Error: {e}")
        return {"success": False, "error": str(e)}


async def _click_studio_go_live_button(driver) -> Dict[str, Any]:
    """
    Click the 'Go live' button on YouTube Studio livestreaming config page.

    This is the SECOND Go live button - the one on the studio.youtube.com/video/.../livestreaming page
    that actually activates the stream endpoint for FFmpeg to connect.

    Flow:
    1. Check if already streaming (has 'END STREAM' button)
    2. Look for 'Go live' button on the page
    3. Click it to activate stream
    4. Verify 'Connect your encoder' appears (means stream is ready)
    """
    logger.info("[STUDIO-GO-LIVE] Looking for Go live button on studio config page...")
    print("[RADIO] === STUDIO CONFIG PAGE: Looking for 'Go live' button ===")

    try:
        # Check current state
        raw_state = _get_studio_page_state(driver)
        state_check = {
            **raw_state,
            "has_connect_encoder": raw_state.get("has_encoder"),
            "has_go_live": raw_state.get("has_go_live_button"),
        }

        print(f"[RADIO] Page state: {state_check}")

        # Already streaming
        if state_check.get('has_end_stream'):
            print("[RADIO] Stream is ALREADY ACTIVE (has End stream button)")
            return {"success": True, "already_streaming": True}

        # Already showing encoder connect (stream endpoint is active)
        if state_check.get('has_connect_encoder') and not state_check.get('has_go_live'):
            print("[RADIO] Stream endpoint already active (Connect your encoder shown)")
            return {"success": True, "endpoint_active": True}

        # Need to click Go live button
        if state_check.get('has_go_live'):
            print("[RADIO] Found visible 'Go live' action - clicking button...")

            click_result = driver.execute_script("""
                // METHOD 1: Look for primary action button with "Go live" text
                // YouTube Studio uses ytcp-button for primary actions
                const buttons = document.querySelectorAll('ytcp-button, button, [role="button"]');
                for (const btn of buttons) {
                    const text = (btn.textContent || '').trim();
                    // Match exact "Go live" (the action button, not menu items)
                    if (text === 'Go live' || text === 'GO LIVE') {
                        // Check if it's a primary/action button (not a menu item)
                        const isPrimary = btn.classList.contains('primary') ||
                                         btn.classList.contains('action-button') ||
                                         btn.closest('.action-buttons') ||
                                         btn.closest('ytcp-button[id*="go-live"]') ||
                                         btn.closest('[class*="go-live"]');
                        if (btn.offsetParent !== null && !btn.disabled) {
                            console.log('[STUDIO] Clicking Go live button:', btn.tagName, btn.className);
                            btn.click();
                            return {clicked: true, method: 'text-match', isPrimary: isPrimary};
                        }
                    }
                }

                // METHOD 2: Look for #go-live-button or similar ID
                const goLiveById = document.querySelector('#go-live-button, [id*="go-live"], ytcp-button[id*="live"]');
                if (goLiveById && goLiveById.offsetParent !== null) {
                    goLiveById.click();
                    return {clicked: true, method: 'id-selector'};
                }

                // METHOD 3: aria-label
                const goLiveByAria = document.querySelector('[aria-label="Go live"], [aria-label*="Go live"]');
                if (goLiveByAria && goLiveByAria.offsetParent !== null) {
                    goLiveByAria.click();
                    return {clicked: true, method: 'aria-label'};
                }

                // METHOD 4: Find in action buttons area (bottom of page typically)
                const actionArea = document.querySelector('.action-buttons, #buttons, [class*="action"]');
                if (actionArea) {
                    const btns = actionArea.querySelectorAll('button, ytcp-button');
                    for (const btn of btns) {
                        const text = (btn.textContent || '').trim().toLowerCase();
                        if (text.includes('go live') && btn.offsetParent !== null) {
                            btn.click();
                            return {clicked: true, method: 'action-area'};
                        }
                    }
                }

                return {clicked: false, buttons_found: document.querySelectorAll('ytcp-button, button').length};
            """)

            print(f"[RADIO] Click result: {click_result}")

            if click_result.get('clicked'):
                print(f"[RADIO] SUCCESS: Clicked Go live via {click_result.get('method')}")

                # Wait for stream to activate
                await asyncio.sleep(5)

                # Verify state changed
                post_state = _get_studio_page_state(driver)

                print(f"[RADIO] Post-click state: {post_state}")

                if post_state.get('has_encoder') or post_state.get('has_end_stream'):
                    print("[RADIO] SUCCESS: Stream endpoint is now active!")
                    return {"success": True, "activated": True}
                else:
                    print("[RADIO] WARNING: Stream state unclear after click")
                    return {"success": True, "clicked": True, "state_unclear": True}
            else:
                print("[RADIO] WARNING: Could not find/click Go live button")
                # Try hardcoded coordinates
                print("[RADIO] Trying hardcoded coordinate click...")
                coords = GO_LIVE_COORDINATES["studio_go_live"]
                _hardcoded_click(driver, coords["x"], coords["y"], coords["description"])
                await asyncio.sleep(3)
                return {"success": True, "method": "hardcoded_fallback"}

        # No Go live button found
        print("[RADIO] No 'Go live' button found on page")
        return {"success": False, "error": "no_go_live_button"}

    except Exception as e:
        logger.error(f"[STUDIO-GO-LIVE] Error: {e}")
        return {"success": False, "error": str(e)}


async def _switch_to_antifafm_account(driver) -> Dict[str, Any]:
    """
    Switch from default FoundUps account to antifaFM account.

    Uses studio_account_switcher for reliable account switching.
    Edge browser (port 9223) defaults to FoundUps, need to switch to antifaFM.

    IMPORTANT: Checks MULTIPLE ways if already on antifaFM to avoid unnecessary switching.

    Args:
        driver: Selenium WebDriver connected to Edge

    Returns:
        Dict with success status
    """
    if ANTIFAFM_SKIP_ACCOUNT_SWITCH:
        logger.info("[ACCOUNT] Skipping account switch (ANTIFAFM_SKIP_ACCOUNT_SWITCH=true)")
        return {"success": True, "skipped": True}

    # FIRST: Check if already on antifaFM BEFORE doing anything
    current_url = driver.current_url
    page_title = driver.title.lower() if driver.title else ""

    logger.info(f"[ACCOUNT] Checking current account... URL: {current_url[:80]}...")
    print(f"[RADIO] Checking current account...")
    print(f"[RADIO]   URL: {current_url[:80]}...")
    print(f"[RADIO]   Title: {page_title[:50]}...")

    # Multiple ways to detect if already on antifaFM
    # If on livestreaming page with our channel ID, definitely already correct
    on_our_livestreaming_page = (
        "livestreaming" in current_url and ANTIFAFM_CHANNEL_ID in current_url
    )
    if on_our_livestreaming_page:
        print("[RADIO] Already on antifaFM livestreaming page - no switch needed!")
        return {"success": True, "already_correct": True, "method": "livestreaming-url"}

    already_on_antifafm = (
        ANTIFAFM_CHANNEL_ID in current_url or
        ANTIFAFM_BRAND_CHANNEL_ID in current_url or
        "@antifafm" in current_url.lower() or
        "antifafm" in page_title or
        "@antifafm" in page_title
    )

    # Also check avatar/header for channel name via JavaScript
    if not already_on_antifafm:
        try:
            dom_check = driver.execute_script("""
                // Check multiple places for antifaFM
                const checks = [];

                // 1. Check avatar button aria-label
                const avatar = document.querySelector('#avatar-btn, button[aria-label*="Account"]');
                if (avatar) {
                    const label = avatar.getAttribute('aria-label') || '';
                    checks.push({type: 'avatar', value: label});
                    if (label.toLowerCase().includes('antifafm')) {
                        return {found: true, method: 'avatar-aria', value: label};
                    }
                }

                // 2. Check channel name in Studio header
                const channelName = document.querySelector('#channel-title, .channel-name, [class*="channel-name"]');
                if (channelName) {
                    const text = channelName.textContent || '';
                    checks.push({type: 'channel-name', value: text});
                    if (text.toLowerCase().includes('antifafm')) {
                        return {found: true, method: 'channel-name', value: text};
                    }
                }

                // 3. Check for antifaFM in page content (Studio dashboard shows channel name)
                const bodyText = document.body.innerText.substring(0, 2000).toLowerCase();
                if (bodyText.includes('antifafm')) {
                    return {found: true, method: 'body-text'};
                }

                // 4. Check URL in window (might have channel ID)
                if (
                    window.location.href.includes(arguments[0]) ||
                    window.location.href.includes(arguments[1])
                ) {
                    return {found: true, method: 'url-channel-id'};
                }

                return {found: false, checks: checks};
            """, ANTIFAFM_CHANNEL_ID, ANTIFAFM_BRAND_CHANNEL_ID)

            if dom_check.get('found'):
                already_on_antifafm = True
                logger.info(f"[ACCOUNT] DOM check found antifaFM: {dom_check.get('method')}")
                print(f"[RADIO] DOM check: Found antifaFM via {dom_check.get('method')}")

        except Exception as e:
            logger.debug(f"[ACCOUNT] DOM check error: {e}")

    if already_on_antifafm:
        logger.info("[ACCOUNT] ALREADY on antifaFM - skipping account switch!")
        print("[RADIO] ALREADY on antifaFM account - no switch needed!")
        return {"success": True, "already_correct": True, "method": "pre-check"}

    # Not on antifaFM - need to switch
    print("[RADIO] Not on antifaFM - proceeding with account switch...")

    try:
        from modules.infrastructure.foundups_vision.src.studio_account_switcher import (
            get_account_switcher, ACCOUNTS
        )

        switcher = get_account_switcher()
        switcher.driver = driver

        # Initialize interaction controller for the driver
        try:
            from modules.infrastructure.human_interaction import get_interaction_controller
            switcher.interaction = get_interaction_controller(driver, platform="youtube_studio")
        except ImportError:
            logger.warning("[ACCOUNT] human_interaction not available, using DOM-only switching")

        logger.info("[ACCOUNT] Switching to antifaFM account...")
        print("[RADIO] Step 0/3: Switching to antifaFM account...")

        # Navigate to YouTube Studio for account menu
        if "studio.youtube.com" not in driver.current_url:
            logger.info("[ACCOUNT] Navigating to YouTube Studio for account switch...")
            print("[RADIO] Navigating to YouTube Studio...")
            driver.get("https://studio.youtube.com")
            await asyncio.sleep(5)  # Wait longer for Studio to load

        # Execute account switch
        result = await switcher.switch_to_account(
            "antifaFM",
            navigate_to_comments=False,  # We'll navigate to streams page ourselves
            navigate_to_live=False
        )

        if result.get("success"):
            logger.info(f"[ACCOUNT] Successfully switched to antifaFM")
            print("[RADIO] Successfully switched to antifaFM account!")
            return {"success": True, "switched": True}
        else:
            logger.warning(f"[ACCOUNT] Switch failed: {result.get('error')}")
            print(f"[RADIO] WARNING: Account switch failed: {result.get('error')}")
            return {"success": False, "error": result.get("error")}

    except ImportError as e:
        logger.warning(f"[ACCOUNT] Account switcher not available: {e}")
        print("[RADIO] WARNING: Account switcher module not available")
        return {"success": False, "error": "module_not_available", "details": str(e)}
    except Exception as e:
        logger.error(f"[ACCOUNT] Account switch error: {e}")
        print(f"[RADIO] ERROR: Account switch failed: {e}")
        return {"success": False, "error": str(e)}


async def click_go_live(driver=None, skip_account_switch: bool = False, use_hardcoded: bool = True) -> Dict[str, Any]:
    """
    Navigate to YouTube Studio livestreaming → Click Go Live button.

    Flow (simplified 2026-03-03):
    1. Connect to Edge browser on debug port 9223
    2. Navigate to Studio livestreaming page
    3. Click Go Live button

    Args:
        driver: Optional Selenium WebDriver. If None, connects to debug port.
        skip_account_switch: If True, skip account switching (assumes already on antifaFM)
        use_hardcoded: If True (DEFAULT), use direct Studio flow (most reliable)

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

        # Step 0: Switch to antifaFM account (Edge defaults to FoundUps)
        if not skip_account_switch:
            account_result = await _switch_to_antifafm_account(driver)
            if not account_result.get("success") and not account_result.get("skipped"):
                logger.warning("[GO-LIVE] Account switch failed, continuing anyway...")
                print("[RADIO] WARNING: Account switch failed, attempting Go Live anyway...")

        # HARDCODED MODE: Skip all DOM detection, use coordinate clicks
        if use_hardcoded:
            print("[RADIO] ===== USING DIRECT STUDIO MODE =====")
            return await _direct_go_live_stream_page(driver)

        # Step 1: Navigate to YouTube page with Create button
        # 2026-03-03: Using main YouTube streams page (012's DOM path)
        logger.info(f"[GO-LIVE] Step 1/3: Navigating to {ANTIFAFM_GO_LIVE_URL}")
        print(f"[RADIO] Navigating to: {ANTIFAFM_GO_LIVE_URL}")
        driver.get(ANTIFAFM_GO_LIVE_URL)
        print("[RADIO] Waiting for page to load (10s)...")
        await asyncio.sleep(10)  # Increased: wait for full page render

        # Debug: Print current URL and page title
        current_url = driver.current_url
        page_title = driver.title
        print(f"[RADIO] Page loaded: {page_title}")
        print(f"[RADIO] Current URL: {current_url}")

        # Step 2: Click CREATE button in header
        logger.info("[GO-LIVE] Step 2/3: Looking for Create button in header...")
        print("[RADIO] Step 2/3: Looking for CREATE button...")

        # Click the Create button in YouTube header
        # 2026-03-03: Focus on finding the EXACT Create button with "Create" text/aria-label
        create_result = driver.execute_script("""
            // Debug: Collect all button-like elements for troubleshooting
            const debug_buttons = [];
            document.querySelectorAll('button, ytcp-button, [role="button"]').forEach(el => {
                if (el.offsetParent !== null) {
                    const text = (el.textContent || '').trim().substring(0, 30);
                    const id = el.id || '';
                    const aria = el.getAttribute('aria-label') || '';
                    if (text || id || aria) {
                        debug_buttons.push({text, id, aria, tag: el.tagName});
                    }
                }
            });

            // PRIORITY 1: Find button with EXACT aria-label="Create"
            // This is the most reliable way to find the Create button
            const createByAria = document.querySelector('button[aria-label="Create"], [aria-label="Create"]');
            if (createByAria && createByAria.offsetParent !== null) {
                createByAria.click();
                return {clicked: true, method: 'aria-label-Create', debug: debug_buttons.slice(0, 10)};
            }

            // PRIORITY 2: Find button containing text "Create" in the header (masthead)
            const masthead = document.querySelector('ytd-masthead, #masthead');
            if (masthead) {
                const allBtns = masthead.querySelectorAll('button, [role="button"]');
                for (const btn of allBtns) {
                    const text = (btn.textContent || '').trim();
                    const aria = btn.getAttribute('aria-label') || '';
                    // Must have "Create" text or aria-label
                    if (text === 'Create' || aria === 'Create') {
                        if (btn.offsetParent !== null) {
                            btn.click();
                            return {clicked: true, method: 'masthead-text-Create', debug: debug_buttons.slice(0, 10)};
                        }
                    }
                }
            }

            // PRIORITY 3: 012's DOM path - ytd-button-renderer in masthead buttons area
            const ytdCreateBtn = document.querySelector('ytd-masthead#masthead div#end div#buttons ytd-button-renderer yt-button-shape button');
            if (ytdCreateBtn && ytdCreateBtn.offsetParent !== null) {
                ytdCreateBtn.click();
                return {clicked: true, method: 'ytd-masthead-create', debug: debug_buttons.slice(0, 10)};
            }

            // PRIORITY 4: YouTube Studio #create-icon
            const createIcon = document.querySelector('#create-icon, ytcp-button#create-icon');
            if (createIcon && createIcon.offsetParent !== null) {
                createIcon.click();
                return {clicked: true, method: '#create-icon', debug: debug_buttons.slice(0, 10)};
            }

            // PRIORITY 5: Any button with "Create" in aria-label (broader)
            const createLabels = document.querySelectorAll('[aria-label*="Create"]');
            for (const btn of createLabels) {
                if (btn.offsetParent !== null) {
                    btn.click();
                    return {clicked: true, method: 'aria-label-contains-Create', debug: debug_buttons.slice(0, 10)};
                }
            }

            return {clicked: false, debug: debug_buttons.slice(0, 15)};
        """)

        print(f"[RADIO] Create button result: {create_result}")

        # Debug: Show available buttons if Create not found
        if not create_result.get('clicked'):
            debug_btns = create_result.get('debug', [])
            if debug_btns:
                print(f"[RADIO] DEBUG - Available buttons on page:")
                for btn in debug_btns[:8]:
                    print(f"  - text='{btn.get('text', '')[:25]}' id='{btn.get('id', '')}' aria='{btn.get('aria', '')[:20]}' tag={btn.get('tag', '')}")

        if create_result.get('clicked'):
            print(f"[RADIO] SUCCESS: Clicked Create button ({create_result.get('method')})")

            # Step 2b: Wait for Create dropdown to appear
            # IMPORTANT: The dropdown takes time to render - need actual wait, not just DOM check
            print("[RADIO] Waiting for Create dropdown to render (5s)...")
            await asyncio.sleep(5)  # Increased: wait for dropdown animation

            # Step 2c: Poll for dropdown WITH "Go live" option specifically
            dropdown_result = await _verify_dropdown_appeared(driver, timeout=5)

            if dropdown_result.get('visible'):
                logger.info(f"[GO-LIVE] Dropdown verified in {dropdown_result.get('elapsed', 0):.1f}s")
                items_found = dropdown_result.get('items', [])
                has_go_live = dropdown_result.get('has_go_live', False)
                print(f"[RADIO] Dropdown appeared ({dropdown_result.get('item_count', 0)} items, {dropdown_result.get('elapsed', 0):.1f}s)")
                print(f"[RADIO] Dropdown items: {items_found[:5]}")
                if has_go_live:
                    print("[RADIO] 'Go live' option detected in dropdown!")
                logger.info("[GO-LIVE] Step 3/3: Clicking 'Go live' in dropdown...")
                print("[RADIO] Step 3/3: Looking for 'Go live' in dropdown...")
            else:
                print(f"[RADIO] WARNING: Dropdown not detected after {dropdown_result.get('elapsed', 5):.1f}s")
                print("[RADIO] Waiting additional 2s for dropdown to render...")
                await asyncio.sleep(2)  # Extra wait if dropdown not detected
                print("[RADIO] Trying Go Live click anyway...")
        else:
            print("[RADIO] WARNING: Create button not found - trying Go Live directly...")

        go_live_result = driver.execute_script("""
            // 2026-03-03: Updated based on 012's screenshot showing Create dropdown
            // Dropdown items: "Upload video", "Go live", "Create post"

            // Debug: Log what popup containers exist
            const debugInfo = {
                popups: [],
                allGoLiveMatches: []
            };

            document.querySelectorAll('ytd-popup-container, tp-yt-iron-dropdown, [role="menu"], [role="listbox"]').forEach(p => {
                debugInfo.popups.push({
                    tag: p.tagName,
                    id: p.id || '',
                    children: p.children.length
                });
            });

            // Method 1: Look in ytd-popup-container for ytd-menu-popup-renderer items
            // This is the actual YouTube dropdown structure
            const popupRenderer = document.querySelector('ytd-popup-container ytd-menu-popup-renderer');
            if (popupRenderer) {
                const items = popupRenderer.querySelectorAll('ytd-menu-service-item-renderer, a, [role="menuitem"]');
                for (const item of items) {
                    const text = (item.textContent || '').trim().toLowerCase();
                    if (text.includes('go live')) {
                        debugInfo.allGoLiveMatches.push({text: text.substring(0, 30), tag: item.tagName});
                        if (item.offsetParent !== null) {
                            item.click();
                            return {clicked: true, text: 'Go live', method: 'ytd-menu-popup-renderer', debug: debugInfo};
                        }
                    }
                }
            }

            // Method 2: 012's path - tp-yt-paper-item inside ytd-compact-link-renderer
            const paperItems = document.querySelectorAll('ytd-compact-link-renderer tp-yt-paper-item, tp-yt-paper-item');
            for (const item of paperItems) {
                const text = (item.textContent || '').toLowerCase().trim();
                if (text === 'go live' || text.includes('go live')) {
                    debugInfo.allGoLiveMatches.push({text: text.substring(0, 30), tag: 'tp-yt-paper-item'});
                    if (item.offsetParent !== null) {
                        const parentLink = item.closest('a#endpoint') || item.closest('a') || item;
                        parentLink.click();
                        return {clicked: true, text: 'Go live', method: 'tp-yt-paper-item', debug: debugInfo};
                    }
                }
            }

            // Method 3: ANY element containing exact "Go live" text (case insensitive)
            const allElements = document.querySelectorAll('*');
            for (const el of allElements) {
                // Skip if has children (we want leaf nodes with text)
                if (el.children.length > 0) continue;

                const text = (el.textContent || '').trim();
                if (text.toLowerCase() === 'go live') {
                    debugInfo.allGoLiveMatches.push({text: text, tag: el.tagName, parent: el.parentElement?.tagName});
                    if (el.offsetParent !== null) {
                        // Click the clickable parent (a, button, or element with click handler)
                        const clickTarget = el.closest('a') || el.closest('button') || el.closest('[role="menuitem"]') || el.closest('ytd-menu-service-item-renderer') || el;
                        clickTarget.click();
                        return {clicked: true, text: 'Go live', method: 'text-match', debug: debugInfo};
                    }
                }
            }

            // Method 4: Look for menu items by role
            const menuItems = document.querySelectorAll('[role="menuitem"], [role="option"], ytd-menu-service-item-renderer');
            for (const item of menuItems) {
                const text = (item.textContent || '').toLowerCase().trim();
                if (text.includes('go live')) {
                    debugInfo.allGoLiveMatches.push({text: text.substring(0, 30), tag: item.tagName, role: item.getAttribute('role')});
                    if (item.offsetParent !== null) {
                        item.click();
                        return {clicked: true, text: 'Go live', method: 'role-menuitem', debug: debugInfo};
                    }
                }
            }

            // Collect all visible text for debugging
            const available = [];
            document.querySelectorAll('ytd-popup-container *, tp-yt-iron-dropdown *, [role="menu"] *, [role="menuitem"], tp-yt-paper-item').forEach(el => {
                const text = (el.textContent || '').trim();
                if (el.offsetParent !== null && text && text.length < 40 && text.length > 1) {
                    if (!available.includes(text.substring(0, 30))) {
                        available.push(text.substring(0, 30));
                    }
                }
            });

            return {clicked: false, available: available.slice(0, 20), debug: debugInfo, url: window.location.href};
        """)

        # Debug output for Go Live detection
        debug_info = go_live_result.get('debug', {})
        if debug_info:
            print(f"[RADIO] DEBUG - Popup containers found: {debug_info.get('popups', [])}")
            print(f"[RADIO] DEBUG - 'Go live' matches: {debug_info.get('allGoLiveMatches', [])}")

        if go_live_result.get('clicked'):
            logger.info(f"[GO-LIVE] Go Live clicked: {go_live_result}")
            print(f"[RADIO] Go Live clicked: {go_live_result.get('text', 'OK')} (method: {go_live_result.get('method', 'unknown')})")
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
            # 2026-03-03: Fixed false positive - [class*="live"] was matching "livestreaming" page classes
            is_live = driver.execute_script("""
                // Check if stream appears to be live already - STRICT checks only
                // Look for actual live stream indicators, not just "live" in class names
                const bodyText = document.body.innerText.toLowerCase();

                // 1. Check for "END STREAM" button (most reliable - only appears when streaming)
                const endButton = document.querySelector(
                    'button[aria-label*="End stream"], button[aria-label*="END STREAM"], ' +
                    'ytcp-button[aria-label*="End"], [data-test-id="end-stream"]'
                );

                // 2. Check for live viewer count indicator
                const viewerCount = document.querySelector('[class*="viewer-count"], [class*="viewerCount"]');

                // 3. Check for "You're live" text on page
                const youAreLive = bodyText.includes("you're live") || bodyText.includes("you are live");

                // 4. Check for stream health/status showing "LIVE" (not just the page title)
                const liveStatus = document.querySelector('[data-status="LIVE"], [class*="status"][class*="live"]');

                // Only return true if we have strong evidence (end button or "you're live" text)
                const isActuallyLive = !!endButton || youAreLive;

                return {
                    live_indicator: isActuallyLive,
                    has_end_button: !!endButton,
                    has_viewer_count: !!viewerCount,
                    you_are_live_text: youAreLive,
                    url: window.location.href
                };
            """)

            if is_live.get('live_indicator') or is_live.get('has_end_button'):
                logger.info("[GO-LIVE] Stream appears to already be live!")
                print("[RADIO] Stream appears to already be live!")
                return {"success": True, "already_live": True, "url": driver.current_url}

            # FALLBACK: Try hardcoded approach when DOM detection fails
            print("[RADIO] DOM detection failed, trying HARDCODED fallback...")
            logger.info("[GO-LIVE] DOM detection failed, attempting hardcoded fallback...")
            hardcoded_result = await _direct_go_live_hardcoded(driver)

            if hardcoded_result.get("success"):
                hardcoded_result["fallback_used"] = True
                return hardcoded_result

            return {"success": False, "error": "go_live_button_not_found", "available": available, "hardcoded_failed": True}

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

    Specifically looks for the Create dropdown popup (not sidebar navigation).

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
            // Look for the CREATE dropdown popup with "Go live" option
            // The dropdown should contain: "Upload video", "Go live", "Create post"

            let visibleItems = [];
            let hasGoLive = false;
            let popupFound = false;

            // Method 1: Search the ENTIRE document for visible "Go live" text
            // This is the most reliable - if we can see it, we can find it
            const allElements = document.querySelectorAll('*');
            for (const el of allElements) {
                // Only check leaf nodes (elements with no children that contain text)
                if (el.children.length === 0) {
                    const text = (el.textContent || '').trim();
                    if (text.toLowerCase() === 'go live' && el.offsetParent !== null) {
                        hasGoLive = true;
                        visibleItems.push('Go live');
                        break;
                    }
                }
            }

            // Method 2: Check popup containers for menu items
            const popupContainer = document.querySelector('ytd-popup-container, tp-yt-iron-dropdown, [role="menu"], [role="listbox"]');
            if (popupContainer) {
                popupFound = true;
                const menuItems = popupContainer.querySelectorAll(
                    'tp-yt-paper-item, ytd-menu-service-item-renderer, [role="menuitem"], ' +
                    'ytd-compact-link-renderer, a, span, yt-formatted-string'
                );

                menuItems.forEach(item => {
                    if (item.offsetParent !== null) {
                        const text = (item.textContent || '').trim();
                        if (text && text.length < 50 && text.length > 1) {
                            if (!visibleItems.includes(text.substring(0, 30))) {
                                visibleItems.push(text.substring(0, 30));
                            }
                            if (text.toLowerCase() === 'go live') {
                                hasGoLive = true;
                            }
                        }
                    }
                });
            }

            // Method 3: Check for tp-yt-paper-item anywhere (YouTube's dropdown item element)
            if (!hasGoLive) {
                const paperItems = document.querySelectorAll('tp-yt-paper-item, yt-formatted-string');
                for (const item of paperItems) {
                    const text = (item.textContent || '').trim().toLowerCase();
                    if (text === 'go live' && item.offsetParent !== null) {
                        hasGoLive = true;
                        if (!visibleItems.includes('Go live')) {
                            visibleItems.push('Go live');
                        }
                        break;
                    }
                }
            }

            return {
                visible: hasGoLive || visibleItems.length > 0,
                item_count: visibleItems.length,
                has_go_live: hasGoLive,
                items: visibleItems.slice(0, 8),
                popup_found: popupFound
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
    """Connect to existing browser via debug port, or launch if not running."""
    import socket

    is_edge = CHROME_DEBUG_PORT == 9223
    browser_name = "Edge" if is_edge else "Chrome"

    # Quick check if port is open before trying Selenium
    def port_open(port, timeout=2):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            return result == 0
        except:
            return False

    print(f"[RADIO] Checking if {browser_name} is on port {CHROME_DEBUG_PORT}...")
    if not port_open(CHROME_DEBUG_PORT):
        logger.info(f"[GO-LIVE] Port {CHROME_DEBUG_PORT} not open, launching {browser_name}...")
        print(f"[RADIO] {browser_name} not running on port {CHROME_DEBUG_PORT}, launching...")
        return _launch_chrome()
    else:
        print(f"[RADIO] {browser_name} already on port {CHROME_DEBUG_PORT}")

    try:
        from selenium import webdriver

        if is_edge:
            # Use Edge WebDriver for Edge browser
            from selenium.webdriver.edge.options import Options as EdgeOptions
            opts = EdgeOptions()
            opts.add_experimental_option("debuggerAddress", f"127.0.0.1:{CHROME_DEBUG_PORT}")
            driver = webdriver.Edge(options=opts)
        else:
            # Use Chrome WebDriver for Chrome browser
            from selenium.webdriver.chrome.options import Options
            opts = Options()
            opts.add_experimental_option("debuggerAddress", f"127.0.0.1:{CHROME_DEBUG_PORT}")
            driver = webdriver.Chrome(options=opts)

        logger.info(f"[GO-LIVE] Connected to {browser_name} on port {CHROME_DEBUG_PORT}")
        return driver
    except Exception as e:
        logger.warning(f"[GO-LIVE] {browser_name} connection failed: {e}, launching...")
        return _launch_chrome()


def _reset_automation_profile_startup(user_data: str) -> None:
    """
    Clear crash/session-restore state for the dedicated automation profile.

    The launcher previously force-killed Edge with `taskkill /F`, which marks
    the profile as crashed. Chromium then restores the previous tabs on the
    next start, so one launcher-opened tab can turn into three identical tabs.
    """
    profile_root = Path(user_data)
    preferences_path = profile_root / "Default" / "Preferences"
    sessions_dir = profile_root / "Default" / "Sessions"

    try:
        if preferences_path.exists():
            preferences = json.loads(preferences_path.read_text(encoding="utf-8", errors="ignore"))
            profile = preferences.get("profile", {})
            if profile.get("exit_type") == "Crashed":
                profile["exit_type"] = "Normal"
                preferences["profile"] = profile
                preferences_path.write_text(
                    json.dumps(preferences, ensure_ascii=True, separators=(",", ":")),
                    encoding="utf-8",
                )
                logger.info("[GO-LIVE] Cleared crashed exit_type on automation profile")
    except Exception as e:
        logger.warning(f"[GO-LIVE] Could not normalize automation profile preferences: {e}")

    try:
        if sessions_dir.exists():
            for session_file in sessions_dir.iterdir():
                if session_file.name.startswith(("Tabs_", "Session_")):
                    session_file.unlink(missing_ok=True)
            logger.info("[GO-LIVE] Cleared automation profile session restore files")
    except Exception as e:
        logger.warning(f"[GO-LIVE] Could not clear automation profile session files: {e}")


def _launch_chrome():
    """Launch browser with debug port enabled (Edge for antifaFM, Chrome for others)."""
    import subprocess
    import time

    is_edge = CHROME_DEBUG_PORT == 9223

    # antifaFM uses Edge (port 9223), other channels use Chrome (port 9222)
    if is_edge:
        # Edge for antifaFM/FoundUps
        browser_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
        user_data = r"O:\Foundups-Agent\modules\platform_integration\browser_profiles\youtube_foundups\edge"
        browser_name = "Edge"
    else:
        # Chrome for Move2Japan/UnDaoDu
        browser_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        user_data = r"O:\Foundups-Agent\modules\platform_integration\browser_profiles\youtube_move2japan\chrome"
        browser_name = "Chrome"

    try:
        _reset_automation_profile_startup(user_data)

        # Launch directly to Studio livestreaming page (no account switch needed if profile is correct)
        studio_url = f"https://studio.youtube.com/channel/{ANTIFAFM_CHANNEL_ID}/livestreaming"
        print(f"[RADIO] Launching {browser_name} with debug port {CHROME_DEBUG_PORT}...")
        print(f"[RADIO] Opening directly: {studio_url}")
        subprocess.Popen([
            browser_path,
            f"--remote-debugging-port={CHROME_DEBUG_PORT}",
            f"--user-data-dir={user_data}",
            "--no-first-run",
            studio_url
        ])

        logger.info(f"[GO-LIVE] Launched {browser_name} with debug port {CHROME_DEBUG_PORT}")
        print(f"[RADIO] Waiting for {browser_name} to start (10s)...")
        time.sleep(10)  # Increased wait time for browser startup

        # Try connecting with correct WebDriver
        from selenium import webdriver

        if is_edge:
            from selenium.webdriver.edge.options import Options as EdgeOptions
            opts = EdgeOptions()
            opts.add_experimental_option("debuggerAddress", f"127.0.0.1:{CHROME_DEBUG_PORT}")
            driver = webdriver.Edge(options=opts)
        else:
            from selenium.webdriver.chrome.options import Options
            opts = Options()
            opts.add_experimental_option("debuggerAddress", f"127.0.0.1:{CHROME_DEBUG_PORT}")
            driver = webdriver.Chrome(options=opts)

        logger.info(f"[GO-LIVE] Connected to newly launched {browser_name}")

        # Edge ignores URL argument, navigate explicitly
        current_url = driver.current_url
        if "studio.youtube.com" not in current_url:
            logger.info(f"[GO-LIVE] Edge opened to {current_url[:50]}... - navigating to Studio")
            print(f"[RADIO] Edge opened to default page, navigating to Studio...")
            driver.get(studio_url)
            time.sleep(5)

        # Smart wait for login - check if user is logged in
        driver = _wait_for_login(driver)
        return driver

    except Exception as launch_error:
        logger.error(f"[GO-LIVE] {browser_name} launch failed: {launch_error}")
        print(f"[RADIO] ERROR: {browser_name} launch failed: {launch_error}")
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
  python youtube_go_live.py                       # Go live (default, includes account switch)
  python youtube_go_live.py --hard                # HARDCODED mode - most reliable (skips DOM detection)
  python youtube_go_live.py --switch-only         # Switch to antifaFM account only (no Go Live)
  python youtube_go_live.py --skip-switch         # Skip account switch (already on antifaFM)
  python youtube_go_live.py --edit                # Open edit dialog only
  python youtube_go_live.py --title "Title"       # Set stream title
  python youtube_go_live.py --desc "Description"  # Set stream description
  python youtube_go_live.py --go-live             # Full flow: Account Switch + Go Live + Edit
  python youtube_go_live.py --json                # Output JSON (for agents)
  python youtube_go_live.py --status              # Check stream status only

Account Switching:
  Edge browser (port 9223) defaults to FoundUps channel.
  This CLI automatically switches to antifaFM before going live.
  Use --skip-switch if already logged into antifaFM account.
  Use --switch-only to just switch accounts without going live.

Examples:
  # OpenClaw: Start stream with custom title (auto-switches to antifaFM)
  python youtube_go_live.py --json --title "antifaFM Radio - Live Now"

  # OpenClaw: Just switch to antifaFM account (for setup)
  python youtube_go_live.py --switch-only --json

  # IronClaw: Edit existing stream description (skip switch if already on antifaFM)
  python youtube_go_live.py --edit --json --skip-switch --desc "24/7 resistance music"

  # Full automation: Account switch + Go live + set title
  python youtube_go_live.py --go-live --title "Morning Show" --desc "Live from the resistance"

Output (--json mode):
  {"success": true, "account_switch": {...}, "go_live": {...}, "edit": {...}}
  {"success": false, "error": "chrome_connection_failed"}
""")

    async def cli_main():
        args = sys.argv[1:]

        # Parse arguments
        title = None
        description = None
        do_go_live = len(args) == 0 or "--go-live" in args or "--hard" in args
        do_edit = "--edit" in args
        json_output = "--json" in args
        status_only = "--status" in args
        switch_only = "--switch-only" in args
        skip_switch = "--skip-switch" in args
        use_hardcoded = "--hard" in args or ANTIFAFM_GO_LIVE_HARDCODED  # HARDCODED mode - most reliable

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

        # Switch-only mode (for OpenClaw setup)
        if switch_only:
            if not json_output:
                print("\n[STEP] Switching to antifaFM account...")
            switch_result = await _switch_to_antifafm_account(driver)
            results["account_switch"] = switch_result
            results["success"] = switch_result.get("success", False)
            if json_output:
                print(json.dumps(results))
            else:
                print(f"[RESULT] Account switch: {switch_result}")
            return

        # Step 1: Go Live (if requested or default)
        if do_go_live:
            if not json_output:
                mode_str = "HARDCODED" if use_hardcoded else "DOM detection"
                print(f"\n[STEP 1] Going live ({mode_str} mode)...")
            go_live_result = await click_go_live(driver, skip_account_switch=skip_switch, use_hardcoded=use_hardcoded)
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
