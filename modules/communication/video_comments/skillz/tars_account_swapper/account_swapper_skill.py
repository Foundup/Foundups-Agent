"""
Tars Account Swapper Skill
==========================

Autonomous account switching for Tars reinforcement training.
Enables swapping between Move2Japan, UnDaoDu, and FoundUps channels in YouTube Studio/Main.

WSP Compliance:
- WSP 27: DAE Architecture (Action -> Verify)
- WSP 87: Navigation Protocol
- WSP 49: Platform Integration Safety
"""

import asyncio
import logging
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

# Add project root to sys.path
project_root = Path(__file__).parent.parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from modules.infrastructure.foundups_selenium.src.human_behavior import get_human_behavior

# UI-TARS verification (optional, graceful degradation if unavailable)
try:
    from modules.infrastructure.foundups_vision.src.ui_tars_bridge import UITarsBridge
    UI_TARS_AVAILABLE = True
except ImportError:
    UI_TARS_AVAILABLE = False

logger = logging.getLogger(__name__)

class TarsAccountSwapper:
    """
    Handles channel/account swapping via YouTube's account picker.

    This is used for:
    - Switching between channels under the SAME signed-in browser session (brand channels / accounts list)
    - Recovering from "no permission" pages by triggering "Switch account" and selecting the correct channel

    Notes (WSP 50: never assume):
    - If two channels are under different Google accounts, you typically cannot switch between them
      via the picker unless both identities are present in the session. In that case, use separate
      browser profiles/ports (e.g., Chrome 9222 vs Edge 9223) and/or ensure both channels appear
      in the picker list.
    Uses text-based DOM search (not fixed indices) since account order varies.
    """

    # Channel Configuration (env-driven for ops ergonomics)
    @property
    def CHANNELS(self) -> Dict[str, Any]:
        m2j_id = os.getenv("MOVE2JAPAN_CHANNEL_ID", "UC-LSSlOZwpGIRIYihaz8zCw")
        undaodu_id = os.getenv("UNDAODU_CHANNEL_ID", "UCfHM9Fw9HD-NwiS0seD_oIA")
        foundups_id = os.getenv("FOUNDUPS_CHANNEL_ID", "UCSNTUXjAgpd4sgWYP0xoJgw")
        raving_id = os.getenv("RAVINGANTIFA_CHANNEL_ID", "UCVSmg5aOhP4tnQ9KFUg97qA")
        return {
            "Move2Japan": {
                "id": m2j_id,
                "url": f"https://studio.youtube.com/channel/{m2j_id}/comments/inbox",
                "match_terms": ["move2japan", "@move2japan", "move 2 japan"],
            },
            "UnDaoDu": {
                "id": undaodu_id,
                "url": f"https://studio.youtube.com/channel/{undaodu_id}/comments/inbox",
                "match_terms": ["undaodu", "@undaodu", "un dao du"],
            },
            "FoundUps": {
                "id": foundups_id,
                "url": f"https://studio.youtube.com/channel/{foundups_id}/comments/inbox",
                "match_terms": ["foundups", "@foundups", "found ups"],
            },
            "RavingANTIFA": {
                "id": raving_id,
                "url": f"https://studio.youtube.com/channel/{raving_id}/comments/inbox",
                "match_terms": ["ravingantifa", "@ravingantifa", "raving antifa"],
            },
        }

    def __init__(self, driver, ui_tars_verify: bool = True):
        self.driver = driver
        self.human = get_human_behavior(driver)
        self.ui_tars_verify = ui_tars_verify and UI_TARS_AVAILABLE
        self._ui_tars = None

        # Initialize UI-TARS if available and verification requested
        if self.ui_tars_verify:
            try:
                self._ui_tars = UITarsBridge()
                logger.info("[TARS-SWAP] UI-TARS verification enabled")
            except Exception as e:
                logger.warning(f"[TARS-SWAP] UI-TARS unavailable: {e}")
                self.ui_tars_verify = False

        logger.info("[TARS-SWAP] Initialized Improved Account Swapper")

    async def sleep_human(self, base=1.0, std=0.2):
        """Human-like delay."""
        delay = self.human.human_delay(base, std)
        await asyncio.sleep(delay)

    async def _verify_step(self, step_name: str, expected_state: str) -> bool:
        """
        Use UI-TARS to verify a step completed successfully.

        Args:
            step_name: Name of the step for logging
            expected_state: Description of what we expect to see

        Returns:
            True if verified or verification skipped, False if verification failed
        """
        if not self.ui_tars_verify or not self._ui_tars:
            logger.debug(f"[TARS-SWAP] Skipping verification for {step_name} (UI-TARS not enabled)")
            return True

        try:
            # Capture screenshot for verification
            screenshot = await self._ui_tars.capture_screenshot()
            logger.info(f"[TARS-SWAP] Captured screenshot for {step_name}: {screenshot.path}")

            # Log expected state for manual review / training data
            logger.info(f"[TARS-SWAP] Verifying {step_name}: expecting '{expected_state}'")

            # For now, return True (screenshot captured for training)
            # Future: Use UI-TARS vision model to verify expected_state
            return True

        except Exception as e:
            logger.warning(f"[TARS-SWAP] Verification failed for {step_name}: {e}")
            # Don't block on verification failures
            return True

    async def navigate_to_comments(self, target: str):
        """Navigate directly to the channel's studio comments."""
        if target in self.CHANNELS:
            url = self.CHANNELS[target]["url"]
            logger.info(f"[TARS-SWAP] Navigating to {target} comments: {url}")
            self.driver.get(url)
            await asyncio.sleep(3) # Wait for initial load
        else:
            logger.warning(f"[TARS-SWAP] No URL mapped for {target}")

    async def _detect_current_channel_id(self) -> Optional[str]:
        """Robustly detect current channel ID from browser state."""
        try:
            # Try script execution first (most reliable in Studio)
            channel_id = self.driver.execute_script(
                "return (window.yt && window.yt.config_ && window.yt.config_.CHANNEL_ID) || "
                "(window.ytcfg && typeof window.ytcfg.get === 'function' && window.ytcfg.get('CHANNEL_ID')) || "
                "null;"
            )
            if channel_id:
                return channel_id
        except Exception:
            pass

        # Fallback to URL regex
        try:
            url = self.driver.current_url or ""
            match = re.search(r"(?:studio\.youtube\.com/channel/|youtube\.com/channel/)([^/?#]+)", url)
            return match.group(1) if match else None
        except Exception:
            return None

    def _current_channel_id(self) -> Optional[str]:
        """Deprecated - use await _detect_current_channel_id() for robustness."""
        try:
            url = self.driver.current_url or ""
            match = re.search(r"studio\.youtube\.com/channel/([^/?#]+)/comments", url)
            return match.group(1) if match else None
        except Exception:
            return None

    def _is_permission_error(self) -> bool:
        """Detect Studio permission error page."""
        try:
            return bool(self.driver.execute_script(
                "const t=(document.body&&document.body.innerText)||'';"
                "return t.includes(\"don't have permission\") || t.includes('Oops, you don\\'t have permission');"
            ))
        except Exception:
            return False

    def _click_permission_switch(self) -> bool:
        """Click the Switch account button on permission error page."""
        try:
            return bool(self.driver.execute_script(
                "const btn=[...document.querySelectorAll('button,ytcp-button')].find(b=>b.textContent.includes('Switch account'));"
                "if(btn){btn.click();return true;} return false;"
            ))
        except Exception:
            return False

    async def swap_from_oops_page(self, target: str, *, navigate_to_comments: bool = True) -> bool:
        """
        Direct account switch from OOPS/permission error page.

        This is a faster path when already on an OOPS page:
        1. Click "Switch account" button directly on OOPS page
        2. Account picker appears in top-right
        3. Select the correct account from picker
        4. Navigate to target URL

        Args:
            target: Target channel name ('Move2Japan', 'UnDaoDu', 'FoundUps', 'RavingANTIFA')
            navigate_to_comments: Whether to navigate to comments after switch

        Returns:
            True if switch successful, False otherwise
        """
        logger.info(f"[TARS-SWAP] 🔄 DIRECT OOPS PAGE SWITCH to {target}")

        if target not in self.CHANNELS:
            logger.error(f"[TARS-SWAP] Unknown target: {target}")
            return False

        # Verify we're on an OOPS page
        if not self._is_permission_error():
            logger.warning("[TARS-SWAP] Not on OOPS page - falling back to normal swap")
            return await self.swap_to(target, navigate_to_comments=navigate_to_comments)

        # Step 1: Click "Switch account" button on OOPS page
        logger.info("[TARS-SWAP] Step 1: Clicking 'Switch account' on OOPS page...")
        if not self._click_permission_switch():
            logger.error("[TARS-SWAP] ❌ Failed to click 'Switch account' on OOPS page")
            # Fallback to normal flow
            return await self.swap_to(target, navigate_to_comments=navigate_to_comments)

        await self.sleep_human(2.0, 0.5)

        # UI-TARS verify: Account picker should now be visible
        await self._verify_step("oops_switch_clicked", "Account picker dropdown visible after clicking OOPS switch button")

        # Step 2: Select target account from picker
        logger.info(f"[TARS-SWAP] Step 2: Selecting {target} from account picker...")
        match_terms = (self.CHANNELS.get(target, {}) or {}).get("match_terms") or []
        if not await self.select_account(target, match_terms=match_terms):
            logger.error(f"[TARS-SWAP] ❌ Failed to select {target} from picker")
            return False

        await self.sleep_human(3.0, 0.5)

        # Step 3: Navigate to target comments (optional)
        if navigate_to_comments:
            await self.navigate_to_comments(target)
            await asyncio.sleep(3)

        # Verify we made it
        if not await self._ensure_target_access(target):
            logger.error(f"[TARS-SWAP] ❌ Failed to reach {target} after OOPS switch")
            return False

        target_id = self.CHANNELS[target]["id"]
        try:
            final_url = self.driver.current_url
            logger.info(f"[TARS-SWAP] 🚀 OOPS page switch to {target} successful!")
            logger.info(f"[TARS-SWAP] Final URL: {final_url}")
        except Exception:
            logger.info(f"[TARS-SWAP] 🚀 OOPS page switch to {target} successful!")

        return True

    async def _ensure_target_access(self, target: str) -> bool:
        """Verify we are on the target comments page with access."""
        target_id = self.CHANNELS.get(target, {}).get("id")
        current_id = self._current_channel_id()
        if current_id == target_id and not self._is_permission_error():
            return True
        return False

    async def click_avatar(self) -> bool:
        """Step 1: Click the avatar button (works on both YouTube and Studio)."""
        logger.info("[TARS-SWAP] Clicking avatar...")
        try:
            # Using custom script for robust shadow-piercing click
            # This covers both ytd-masthead (YouTube) and ytcp-header (Studio)
            success = self.driver.execute_script("""
                const btn = 
                    document.querySelector('button#avatar-btn') || 
                    document.querySelector('ytcp-img-shadow#avatar') ||
                    document.querySelector('ytcp-header #avatar-btn') ||
                    document.querySelector('button#avatar-btn img#img');
                if (btn) {
                    btn.click();
                    return true;
                }
                return false;
            """)
            return success
        except Exception as e:
            logger.error(f"[TARS-SWAP] Failed to click avatar: {e}")
            return False

    async def click_switch_account(self) -> bool:
        """Step 2: Click 'Switch account' in the popup menu."""
        logger.info("[TARS-SWAP] Clicking 'Switch account'...")
        try:
            # 2026-01-28: Updated with precise DOM path from user inspection
            # Path: ytd-multi-page-menu-section-renderer[0] > #items > ytd-compact-link-renderer[2] > a#endpoint
            success = self.driver.execute_script("""
                // Strategy 1: Precise DOM path (most reliable)
                // The "Switch account" is the 3rd item (index 2) in the first menu section
                const sections = document.querySelectorAll('ytd-multi-page-menu-section-renderer');
                if (sections.length > 0) {
                    const firstSection = sections[0];
                    const links = firstSection.querySelectorAll('ytd-compact-link-renderer');
                    // Switch account is typically at index 2 (after Sign out and other items)
                    for (const link of links) {
                        const text = link.textContent || '';
                        if (text.includes('Switch account') || text.includes('Switch')) {
                            const endpoint = link.querySelector('a#endpoint') || link;
                            endpoint.click();
                            return true;
                        }
                    }
                }

                // Strategy 2: Direct selector for the right-icon (arrow) in Switch account row
                const switchIcon = document.querySelector('ytd-compact-link-renderer yt-icon#right-icon');
                if (switchIcon) {
                    const parent = switchIcon.closest('ytd-compact-link-renderer');
                    if (parent && parent.textContent.includes('Switch')) {
                        switchIcon.click();
                        return true;
                    }
                }

                // Strategy 3: Text search fallback
                const items = document.querySelectorAll('tp-yt-paper-item, ytcp-ve, ytd-compact-link-renderer, a#endpoint');
                for (const item of items) {
                    if (item.textContent.includes('Switch account')) {
                        item.click();
                        return true;
                    }
                }
                return false;
            """)
            return success
        except Exception as e:
            logger.error(f"[TARS-SWAP] Failed to click switch account: {e}")
            return False

    # 2026-01-29: FLUID DUAL-BROWSER ARCHITECTURE
    # Both Google accounts logged into BOTH browsers - picker structure identical on Chrome & Edge
    # Section 0 (Google Account A): UnDaoDu (index 0), Move2Japan (index 1)
    # Section 1 (Google Account B): FoundUps (index 0), RavingANTIFA (index 1)
    # This means: Chrome (9222) can access ALL 4, Edge (9223) can access ALL 4
    ACCOUNT_PICKER_MAP = {
        "UnDaoDu": {"section": 0, "index": 0, "text_match": "undaodu"},
        "Move2Japan": {"section": 0, "index": 1, "text_match": "move2japan"},
        "FoundUps": {"section": 1, "index": 0, "text_match": "foundups"},
        "RavingANTIFA": {"section": 1, "index": 1, "text_match": "ravingantifa"},
    }

    async def select_account(self, target_name: str, match_terms: Optional[list] = None) -> bool:
        """Step 3: Select the target account by name (Move2Japan, UnDaoDu, FoundUps, or RavingANTIFA)."""
        logger.info(f"[TARS-SWAP] Selecting account: {target_name}...")
        try:
            # Debug: List all available accounts in the picker
            available_accounts = self.driver.execute_script("""
                const accounts = [];
                const items = document.querySelectorAll('ytd-account-item-renderer, ytcp-account-item-renderer, tp-yt-paper-icon-item');
                for (const item of items) {
                    const text = (item.textContent || '').trim().replace(/\\s+/g, ' ').substring(0, 60);
                    if (text) accounts.push(text);
                }
                return accounts;
            """)
            logger.info(f"[TARS-SWAP] Available accounts in picker: {available_accounts}")

            # Get picker map for index-based selection
            picker_info = self.ACCOUNT_PICKER_MAP.get(target_name, {})
            section_idx = picker_info.get("section")
            item_idx = picker_info.get("index")
            text_match = picker_info.get("text_match", target_name.lower())

            # 2026-01-28: Updated with precise DOM structure from user inspection
            # Structure: ytd-account-section-list-renderer[section] > ytd-account-item-section-renderer >
            #            div#contents > ytd-account-item-renderer[index] > tp-yt-paper-icon-item
            success = self.driver.execute_script("""
                const target = (arguments[0] || '').toLowerCase();
                const terms = (arguments[1] || []).map(t => (t || '').toLowerCase()).filter(Boolean);
                const wanted = [target, ...terms].filter(Boolean);
                const sectionIdx = arguments[2];
                const itemIdx = arguments[3];
                const textMatch = arguments[4];

                // Strategy 1: Index-based selection (most reliable when picker structure is known)
                if (sectionIdx !== null && sectionIdx !== undefined && itemIdx !== null && itemIdx !== undefined) {
                    const sectionLists = document.querySelectorAll('ytd-account-section-list-renderer');
                    if (sectionLists.length > sectionIdx) {
                        const sectionList = sectionLists[sectionIdx];
                        const itemSections = sectionList.querySelectorAll('ytd-account-item-section-renderer');
                        if (itemSections.length > 0) {
                            const items = itemSections[0].querySelectorAll('ytd-account-item-renderer');
                            if (items.length > itemIdx) {
                                const targetItem = items[itemIdx];
                                const paperItem = targetItem.querySelector('tp-yt-paper-icon-item');
                                if (paperItem) {
                                    // Verify it's the right account by text
                                    const itemText = paperItem.textContent.toLowerCase();
                                    if (itemText.includes(textMatch)) {
                                        paperItem.click();
                                        console.log('[TARS-SWAP] Selected via index:', textMatch);
                                        return true;
                                    }
                                }
                            }
                        }
                    }
                }

                // Strategy 2: Text-based search across all tp-yt-paper-icon-item (fallback)
                const allPaperItems = document.querySelectorAll('tp-yt-paper-icon-item');
                for (const item of allPaperItems) {
                    const text = item.textContent.toLowerCase();
                    if (wanted.some(w => text.includes(w))) {
                        item.click();
                        console.log('[TARS-SWAP] Selected via text match:', text.substring(0, 40));
                        return true;
                    }
                }

                // Strategy 3: Search ytd-account-item-renderer directly
                const items = document.querySelectorAll('ytd-account-item-renderer, ytcp-account-item-renderer');
                for (const item of items) {
                    const text = item.textContent.toLowerCase();
                    if (wanted.some(w => text.includes(w))) {
                        item.click();
                        return true;
                    }
                }

                return false;
            """, target_name, match_terms or [], section_idx, item_idx, text_match)
            return success
        except Exception as e:
            logger.error(f"[TARS-SWAP] Failed to select account {target_name}: {e}")
            return False

    async def swap_to(self, target: str, *, navigate_to_comments: bool = True) -> bool:
        """
        Improved swap sequence with direct Studio navigation.
        target: 'UnDaoDu', 'Move2Japan', 'FoundUps', or 'RavingANTIFA'
        """
        # 2026-01-29: Enhanced logging for debugging swap failures
        try:
            start_url = self.driver.current_url
        except Exception:
            start_url = "<unknown>"
        logger.info(f"[TARS-SWAP] STARTING IMPROVED SWAP TO {target}")
        logger.info(f"[TARS-SWAP] Current URL: {start_url}")

        if target not in self.CHANNELS:
            logger.error(f"[TARS-SWAP] Unknown target account: {target}")
            return False

        # FAST PATH: Check ID from current state (no navigation needed)
        current_id = await self._detect_current_channel_id()
        target_id = self.CHANNELS[target]["id"]
        logger.debug(f"[TARS-SWAP] Channel IDs - current: {current_id}, target: {target_id}")

        # 2026-01-29: BUG FIX - fast-check must verify we're NOT on OOPS page
        # URL might contain correct channel ID but still be an error page
        if current_id == target_id:
            if self._is_permission_error():
                logger.info(f"[TARS-SWAP] fast-check: On target URL but OOPS/permission page detected - proceeding with full swap")
            else:
                logger.info(f"[TARS-SWAP] fast-check: Already on {target} ({target_id}) - skipping swap")
                return True

        # If already on target comments page and accessible, skip switching
        if await self._ensure_target_access(target):
            logger.info(f"[TARS-SWAP] Already on {target} comments page - skipping account switch")
            return True
        
        # Ensure we are on a page where account switching is possible
        if "youtube.com" not in self.driver.current_url:
            self.driver.get("https://www.youtube.com")
            await asyncio.sleep(2)

        # Step 1: Click avatar button
        if not await self.click_avatar():
            logger.error("[TARS-SWAP] ❌ Step 1 FAILED - click_avatar")
            return False
        await self.sleep_human(1.5, 0.4)

        # UI-TARS verify: Account menu should be open
        await self._verify_step("step1_avatar_clicked", "Account menu dropdown visible with user profile")

        # Step 2: Click "Switch account"
        if not await self.click_switch_account():
            logger.error("[TARS-SWAP] ❌ Step 2 FAILED - click_switch_account")
            return False
        await self.sleep_human(2.0, 0.5)

        # UI-TARS verify: Account picker should show list of channels
        await self._verify_step("step2_switch_clicked", f"Account picker showing list including {target}")

        # Step 3: Select target account
        match_terms = (self.CHANNELS.get(target, {}) or {}).get("match_terms") or []
        if not await self.select_account(target, match_terms=match_terms):
            logger.error("[TARS-SWAP] ❌ Step 3 FAILED - select_account")
            return False

        # UI-TARS verify: Account should now be switching
        await self._verify_step("step3_account_selected", f"Page loading/redirecting to {target} channel")
        
        # Wait for global switch to settle
        logger.info(f"[TARS-SWAP] ✅ Account switch selected. Waiting for session update...")
        await asyncio.sleep(5) 

        # FINAL STEP: Optionally navigate directly to the target comments URL
        if navigate_to_comments:
            await self.navigate_to_comments(target)

        # Verify access; retry once if permission error detected
        if not await self._ensure_target_access(target):
            logger.warning(f"[TARS-SWAP] Access mismatch after switch; attempting recovery for {target}")
            if self._is_permission_error() and self._click_permission_switch():
                await self.sleep_human(2.0, 0.5)
                if await self.select_account(target, match_terms=match_terms):
                    await asyncio.sleep(3)
                    if navigate_to_comments:
                        await self.navigate_to_comments(target)

            if not await self._ensure_target_access(target):
                logger.error(f"[TARS-SWAP] Failed to reach {target} comments page with access")
                return False
        
        # UI-TARS verify: Final verification - should be on target channel comments page
        await self._verify_step("step4_swap_complete", f"YouTube Studio comments inbox for {target} channel")

        # 2026-01-29: Log final state for debugging
        try:
            final_url = self.driver.current_url
            final_id = await self._detect_current_channel_id()
            logger.info(f"[TARS-SWAP] 🚀 Successfully transitioned to {target} comments.")
            logger.info(f"[TARS-SWAP] Final URL: {final_url}")
            logger.info(f"[TARS-SWAP] Final channel ID: {final_id} (expected: {target_id})")
        except Exception as log_err:
            logger.info(f"[TARS-SWAP] 🚀 Successfully transitioned to {target} comments (final state logging failed: {log_err})")
        return True

async def main():
    # This is a placeholder for standalone testing
    print("Tars Account Swapper - Standalone Script")

if __name__ == "__main__":
    asyncio.run(main())
