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

logger = logging.getLogger(__name__)

class TarsAccountSwapper:
    """
    Handles account swapping between Move2Japan and UnDaoDu (SAME Google account).
    Uses text-based DOM search (not fixed indices) since account order varies.

    NOTE: FoundUps is on a DIFFERENT Google account and cannot be switched via
    YouTube's account picker. FoundUps requires a separate browser (Edge on port 9223).
    """

    # Channel Configuration (SAME Google account only)
    # FoundUps is on a different Google account - requires Edge browser
    # Channel Configuration (SAME Google account only)
    # Move2Japan and UnDaoDu IDs are read from .env for consistency
    @property
    def CHANNELS(self) -> Dict[str, Any]:
        m2j_id = os.getenv("MOVE2JAPAN_CHANNEL_ID", "UC-LSSlOZwpGIRIYihaz8zCw")
        undaodu_id = os.getenv("UNDAODU_CHANNEL_ID", "UCfHM9Fw9HD-NwiS0seD_oIA")
        return {
            "Move2Japan": {
                "id": m2j_id,
                "url": f"https://studio.youtube.com/channel/{m2j_id}/comments/inbox"
            },
            "UnDaoDu": {
                "id": undaodu_id,
                "url": f"https://studio.youtube.com/channel/{undaodu_id}/comments/inbox"
            }
        }

    def __init__(self, driver):
        self.driver = driver
        self.human = get_human_behavior(driver)
        logger.info("[TARS-SWAP] Initialized Improved Account Swapper")

    async def sleep_human(self, base=1.0, std=0.2):
        """Human-like delay."""
        delay = self.human.human_delay(base, std)
        await asyncio.sleep(delay)

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
            # Explicit path from user for reliability or fallback to text search
            success = self.driver.execute_script("""
                // Explicit path from user for reliability
                const switchBtn = document.querySelector('ytd-multi-page-menu-section-renderer:nth-of-type(1) ytd-compact-link-renderer:nth-of-type(2) a#endpoint');
                if (switchBtn) {
                    switchBtn.click();
                    return true;
                }
                
                // Fallback to text search
                const items = document.querySelectorAll('tp-yt-paper-item, ytcp-ve, ytd-compact-link-renderer');
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

    async def select_account(self, target_name: str) -> bool:
        """Step 3: Select the target account by name (UnDaoDu, Move2Japan, or FoundUps)."""
        logger.info(f"[TARS-SWAP] Selecting account: {target_name}...")
        try:
            # Text-based search is most reliable since account order varies
            success = self.driver.execute_script("""
                const target = arguments[0].toLowerCase();

                // Search all account item renderers by text content
                const items = document.querySelectorAll('ytd-account-item-renderer, ytcp-account-item-renderer, tp-yt-paper-icon-item');
                for (const item of items) {
                    const text = item.textContent.toLowerCase();
                    if (text.includes(target)) {
                        item.click();
                        return true;
                    }
                }

                // Fallback: Try paper-item elements in account picker
                const paperItems = document.querySelectorAll('tp-yt-paper-item');
                for (const item of paperItems) {
                    const text = item.textContent.toLowerCase();
                    if (text.includes(target)) {
                        item.click();
                        return true;
                    }
                }
                return false;
            """, target_name)
            return success
        except Exception as e:
            logger.error(f"[TARS-SWAP] Failed to select account {target_name}: {e}")
            return False

    async def swap_to(self, target: str) -> bool:
        """
        Improved swap sequence with direct Studio navigation.
        target: 'UnDaoDu', 'Move2Japan', or 'FoundUps'
        """
        logger.info(f"[TARS-SWAP] STARTING IMPROVED SWAP TO {target}")

        if target not in self.CHANNELS:
            logger.error(f"[TARS-SWAP] Unknown target account: {target}")
            return False

        # FAST PATH: Check ID from current state (no navigation needed)
        current_id = await self._detect_current_channel_id()
        target_id = self.CHANNELS[target]["id"]
        
        if current_id == target_id:
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

        if not await self.click_avatar():
            logger.error("[TARS-SWAP] ❌ Step 1 FAILED")
            return False
        await self.sleep_human(1.5, 0.4)

        if not await self.click_switch_account():
            logger.error("[TARS-SWAP] ❌ Step 2 FAILED")
            return False
        await self.sleep_human(2.0, 0.5)

        if not await self.select_account(target):
            logger.error("[TARS-SWAP] ❌ Step 3 FAILED")
            return False
        
        # Wait for global switch to settle
        logger.info(f"[TARS-SWAP] ✅ Account switch selected. Waiting for session update...")
        await asyncio.sleep(5) 

        # FINAL STEP: Navigate directly to the target comments URL
        await self.navigate_to_comments(target)

        # Verify access; retry once if permission error detected
        if not await self._ensure_target_access(target):
            logger.warning(f"[TARS-SWAP] Access mismatch after switch; attempting recovery for {target}")
            if self._is_permission_error() and self._click_permission_switch():
                await self.sleep_human(2.0, 0.5)
                if await self.select_account(target):
                    await asyncio.sleep(3)
                    await self.navigate_to_comments(target)

            if not await self._ensure_target_access(target):
                logger.error(f"[TARS-SWAP] Failed to reach {target} comments page with access")
                return False
        
        logger.info(f"[TARS-SWAP] 🚀 Successfully transitioned to {target} comments.")
        return True

async def main():
    # This is a placeholder for standalone testing
    print("Tars Account Swapper - Standalone Script")

if __name__ == "__main__":
    asyncio.run(main())
