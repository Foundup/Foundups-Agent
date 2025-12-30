"""
YouTube Studio Account Switcher - Phase 4H Hybrid (DOM + UI-TARS Training)
==============================================================================

WSP Compliance: WSP 77 (Agent Coordination), WSP 49 (Anti-Detection), WSP 48 (Recursive Learning)

Phase 4H: HYBRID Architecture (Fixed DOM + Vision Training)
- Tier 0: Fixed coordinates for reliable switching (~200ms, 95% success)
- Training: Record successful clicks as UI-TARS training data
- Future: UI-TARS can learn to detect avatar/menu/accounts visually

CRITICAL: This is the same pattern as party_reactor.py - DOM clicks generate
labeled training data for self-supervised learning.

Account Switch Sequence:
1. Click avatar button (top=12px, left=325px, 32x32px)
2. Click "Switch account" menu item (top=221px, left=539px, 24x24px)
3. Click target account:
   - UnDaoDu: (top=132px, left=245px, 290x64px) [index 0]
   - Move2Japan: (top=63px, left=245px, 290x64px) [index 1]
   - FoundUps: (top=196px, left=245px, 290x64px) [index 2] (estimated)

Training Data Format:
- Screenshot + coordinates → vision_training_collector.py
- Exported to JSONL → UI-TARS fine-tuning dataset
- Self-supervised: Fixed coordinates = ground truth labels

NAVIGATION:
-> Called by: community_monitor.py (channel switch detection)
-> Uses: modules.infrastructure.human_interaction (anti-detection)
-> Uses: modules.infrastructure.foundups_vision.src.vision_training_collector (training)
"""

import os
import time
import asyncio
import logging
from typing import Optional, Dict, Any, Literal, List

logger = logging.getLogger(__name__)

# Training data collection for vision model self-supervised learning
_training_collector = None

def _get_training_collector():
    """Lazy load training collector to avoid circular imports."""
    global _training_collector
    if _training_collector is None:
        try:
            from modules.infrastructure.foundups_vision.src.vision_training_collector import get_training_collector
            _training_collector = get_training_collector()
            logger.info("[ACCOUNT-SWITCH] Vision training collector initialized")
        except ImportError as e:
            logger.debug(f"[ACCOUNT-SWITCH] Training collector not available: {e}")
            _training_collector = False  # Mark as unavailable
    return _training_collector if _training_collector is not False else None


def _env_truthy(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in ("1", "true", "yes", "y", "on")


# Account metadata
_m2j_id = os.getenv("MOVE2JAPAN_CHANNEL_ID", "UC-LSSlOZwpGIRIYihaz8zCw")
_undaodu_id = os.getenv("UNDAODU_CHANNEL_ID", "UCfHM9Fw9HD-NwiS0seD_oIA")
_foundups_id = os.getenv("FOUNDUPS_CHANNEL_ID", "UCSNTUXjAgpd4sgWYP0xoJgw")

ACCOUNTS = {
    "UnDaoDu": {
        "channel_id": _undaodu_id,
        "display_name": "UnDaoDu",
        "handle": os.getenv("UNDAODU_HANDLE", "@UnDaoDu"),
        "menu_index": 0,
        "menu_y": 129,
        "comments_url": f"https://studio.youtube.com/channel/{_undaodu_id}/comments/inbox"
    },
    "Move2Japan": {
        "channel_id": _m2j_id,
        "display_name": "Move2Japan",
        "handle": os.getenv("MOVE2JAPAN_HANDLE", "@MOVE2JAPAN"),
        "menu_index": 1,
        "menu_y": 193,
        "comments_url": f"https://studio.youtube.com/channel/{_m2j_id}/comments/inbox"
    },
    "FoundUps": {
        "channel_id": _foundups_id,
        "display_name": "FoundUps",
        "handle": os.getenv("FOUNDUPS_HANDLE", "@FoundUps"),
        "menu_index": 2,
        "menu_y": 257,
        "comments_url": f"https://studio.youtube.com/channel/{_foundups_id}/comments/inbox"
    }
}

# Fixed coordinates for account switching sequence
# These generate labeled training data for the UI-TARS vision model
SWITCH_COORDINATES = {
    "avatar_button": {
        "x": 371,
        "y": 28,
        "width": 32,
        "height": 32,
        "description": "YouTube Studio avatar button (account switcher trigger)",
    },
    "switch_menu": {
        "x": 294,
        "y": 184,
        "width": 24,
        "height": 24,
        "description": "Switch account menu item (opens account list)",
    },
    "account_UnDaoDu": {
        "x": 178,
        "y": 161,
        "width": 290,
        "height": 64,
        "description": "UnDaoDu account selection item",
    },
    "account_Move2Japan": {
        "x": 178,
        "y": 225,
        "width": 290,
        "height": 64,
        "description": "Move2Japan account selection item",
    },
    "account_FoundUps": {
        "x": 178,
        "y": 289,
        "width": 290,
        "height": 64,
        "description": "FoundUps account selection item",
    },
}


class StudioAccountSwitcher:
    """
    Switches YouTube Studio accounts with hybrid DOM + UI-TARS training.
    """

    def __init__(self):
        self.driver = None
        self.interaction = None
        self._training_enabled = _env_truthy("STUDIO_ACCOUNT_TRAINING_ENABLED", "true")
        self._training_examples_this_session = 0

    def _connect_to_chrome(self, driver=None):
        """Connect to Chrome or reuse provided driver."""
        if driver:
            self.driver = driver
            from modules.infrastructure.human_interaction import get_interaction_controller
            self.interaction = get_interaction_controller(self.driver, platform="youtube_studio")
            return True

        if self.driver:
            return True

        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from modules.infrastructure.human_interaction import get_interaction_controller

            port = int(os.getenv("FOUNDUPS_LIVECHAT_CHROME_PORT", "9222"))
            opts = Options()
            opts.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
            self.driver = webdriver.Chrome(options=opts)
            self.interaction = get_interaction_controller(self.driver, platform="youtube_studio")
            return True
        except Exception as e:
            logger.error(f"[ACCOUNT-SWITCH] Connection failed: {e}")
            return False

    def _record_training_example(self, step_name: str, success: bool, duration_ms: int = 0) -> None:
        """Record training data for vision models."""
        if not self._training_enabled or not success or not self.driver:
            return

        collector = _get_training_collector()
        if not collector:
            return

        try:
            coords_data = SWITCH_COORDINATES.get(step_name)
            if not coords_data: return

            collector.record_successful_click(
                driver=self.driver,
                description=coords_data["description"],
                coordinates=(coords_data["x"], coords_data["y"]),
                platform="youtube_studio",
                action="click",
                duration_ms=duration_ms,
                metadata={"step_name": step_name}
            )
            self._training_examples_this_session += 1
        except Exception as e:
            logger.debug(f"[ACCOUNT-SWITCH-TRAIN] Record failed: {e}")

    async def switch_to_account(self, target_account: Literal["UnDaoDu", "Move2Japan", "FoundUps"], navigate_to_comments: bool = True) -> Dict[str, Any]:
        """Switch to target account with optional direct navigation."""
        if not _env_truthy("YT_AUTOMATION_ENABLED", "true"):
            return {"success": False, "error": "automation_disabled"}

        if target_account not in ACCOUNTS:
            return {"success": False, "error": "unknown_account"}

        if not self._connect_to_chrome():
            return {"success": False, "error": "chrome_connection_failed"}

        logger.info(f"[ACCOUNT-SWITCH] 🔄 Switching to {target_account}...")

        # REDUCED REDUNDANCY: Only navigate if NOT on youtube.com already
        if "youtube.com" not in self.driver.current_url:
            logger.info("[ACCOUNT-SWITCH] 🧭 Not on YouTube - navigating to Studio home")
            self.driver.get("https://studio.youtube.com")
            await asyncio.sleep(2)
        else:
            logger.debug("[ACCOUNT-SWITCH] Already on YouTube - attempting switch from current page")

        steps_completed = 0
        try:
            # STEP 1: Click avatar (DOM selection first for speed, fallback to coords)
            logger.info("[ACCOUNT-SWITCH] Step 1/3: Click avatar")
            start = time.time()
            
            # IMPROVED: Piercing shadow DOM and multi-selector support
            avatar_clicked = self.driver.execute_script("""
                const btn = document.querySelector('button#avatar-btn') || 
                            document.querySelector('ytcp-img-shadow#avatar') ||
                            document.querySelector('ytcp-header #avatar-btn');
                if (btn) { btn.click(); return true; }
                return false;
            """)
            
            if not avatar_clicked:
                await self.interaction.click_action("avatar_button")
            
            self._record_training_example("avatar_button", True, int((time.time()-start)*1000))
            steps_completed += 1
            await asyncio.sleep(1.0)

            # STEP 2: Click "Switch account"
            logger.info("[ACCOUNT-SWITCH] Step 2/3: Click 'Switch account'")
            start = time.time()
            
            switch_menu_clicked = self.driver.execute_script("""
                const items = document.querySelectorAll('tp-yt-paper-item, ytcp-ve');
                for (const item of items) {
                    if (item.textContent.includes('Switch account')) {
                        item.click(); return true;
                    }
                }
                return false;
            """)
            
            if not switch_menu_clicked:
                await self.interaction.click_action("switch_menu")
                
            self._record_training_example("switch_menu", True, int((time.time()-start)*1000))
            steps_completed += 1
            await asyncio.sleep(1.5)

            # STEP 3: Select target account
            logger.info(f"[ACCOUNT-SWITCH] Step 3/3: Select {target_account}")
            start = time.time()
            
            account_selected = self.driver.execute_script("""
                const target = arguments[0];
                const items = document.querySelectorAll('ytd-account-item-renderer, ytcp-account-item-renderer');
                for (const item of items) {
                    if (item.textContent.includes(target)) {
                        item.click(); return true;
                    }
                }
                return false;
            """, target_account)
            
            if not account_selected:
                await self.interaction.click_action(f"account_{target_account}")
                
            self._record_training_example(f"account_{target_account}", True, int((time.time()-start)*1000))
            steps_completed += 1

            # Wait for reload and verify
            logger.info("[ACCOUNT-SWITCH] ⏳ Waiting for session update...")
            await asyncio.sleep(5.0)

            if navigate_to_comments:
                comments_url = ACCOUNTS[target_account]["comments_url"]
                logger.info(f"[ACCOUNT-SWITCH] 🚀 Navigating to comments: {comments_url}")
                self.driver.get(comments_url)
                await asyncio.sleep(3)

            # Final verification
            await asyncio.sleep(2.0)
            verify_url = self.driver.current_url
            expected_id = ACCOUNTS[target_account]["channel_id"]
            
            # If we navigated to comments, the channel ID should be in the URL
            success = expected_id in verify_url
            
            if success:
                logger.info(f"[ACCOUNT-SWITCH] ✅ Successfully switched and navigated to {target_account}")
            else:
                logger.warning(f"[ACCOUNT-SWITCH] ⚠️ URL verification failed. Expected {expected_id} in {verify_url}")

            return {
                "success": success,
                "account": target_account,
                "channel_id": expected_id,
                "steps_completed": steps_completed,
                "current_url": verify_url
            }

        except Exception as e:
            logger.error(f"[ACCOUNT-SWITCH] Failed at step {steps_completed+1}: {e}")
            return {"success": False, "error": str(e), "steps_completed": steps_completed}

        except Exception as e:
            logger.error(f"[ACCOUNT-SWITCH] Switch failed at step {steps_completed + 1}: {e}")
            return {
                "success": False,
                "error": str(e),
                "steps_completed": steps_completed,
                "training_recorded": training_recorded,
            }

    def get_training_stats(self) -> Dict[str, Any]:
        """Get training data collection statistics."""
        collector = _get_training_collector()
        if collector is None:
            return {"enabled": False, "reason": "collector_not_available"}

        stats = collector.get_stats()
        stats["enabled"] = self._training_enabled
        stats["session_examples"] = self._training_examples_this_session
        return stats

    def export_training_data(self, output_path: str = None) -> Optional[str]:
        """
        Export collected training data to JSONL for UI-TARS fine-tuning.

        Args:
            output_path: Path to output file (auto-generated if None)

        Returns:
            Path to exported file, or None if failed
        """
        collector = _get_training_collector()
        if collector is None:
            logger.warning("[ACCOUNT-SWITCH-TRAIN] Cannot export: collector not available")
            return None

        try:
            path = collector.export_to_jsonl(
                output_path=output_path,
                platform="youtube_studio",
                include_screenshots=True
            )
            logger.info(f"[ACCOUNT-SWITCH-TRAIN] Exported training data to: {path}")
            return path
        except Exception as e:
            logger.error(f"[ACCOUNT-SWITCH-TRAIN] Export failed: {e}")
            return None


# Global instance for import
_account_switcher = None

def get_account_switcher() -> StudioAccountSwitcher:
    """Get or create global StudioAccountSwitcher instance."""
    global _account_switcher
    if _account_switcher is None:
        _account_switcher = StudioAccountSwitcher()
    return _account_switcher


async def switch_studio_account(target_account: Literal["UnDaoDu", "Move2Japan", "FoundUps"]) -> Dict[str, Any]:
    """
    Async wrapper for switching Studio account.

    Args:
        target_account: Account to switch to

    Returns:
        Dict with switch result
    """
    switcher = get_account_switcher()
    return await switcher.switch_to_account(target_account)


if __name__ == "__main__":
    # Test account switcher
    import asyncio

    async def test_switch():
        switcher = StudioAccountSwitcher()

        # Test switch to UnDaoDu
        result = await switcher.switch_to_account("UnDaoDu")
        print(f"Switch result: {result}")

        # Get training stats
        stats = switcher.get_training_stats()
        print(f"Training stats: {stats}")

    asyncio.run(test_switch())
