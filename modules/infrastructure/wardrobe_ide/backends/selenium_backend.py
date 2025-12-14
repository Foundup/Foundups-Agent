"""
Selenium Backend - Replay-only backend for Wardrobe Skills

This backend uses Selenium to replay recorded skills.
Recording is handled by Playwright (primary recorder).

Integration note:
Can leverage existing BrowserManager from modules/infrastructure/foundups_selenium
for session management and profile reuse.
"""
import time
from typing import Any

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

from . import WardrobeBackendBase
from ..src.skill import WardrobeSkill
from ..src.config import HEADLESS


class SeleniumBackend(WardrobeBackendBase):
    """
    Selenium-based backend for replaying Wardrobe Skills.

    Recording is NOT implemented (use Playwright for recording).
    """

    def record_session(
        self,
        target_url: str,
        duration_seconds: int = 15
    ) -> list[dict[str, Any]]:
        """
        Recording with Selenium is NOT implemented.

        Use Playwright backend for recording.
        Selenium backend is for replay only.

        TODO: Recording with Selenium will be layered on later if needed.
              Playwright is the primary recorder for now.
        """
        raise NotImplementedError(
            "Recording is not supported with Selenium backend. "
            "Use 'playwright' backend for recording."
        )

    def replay_skill(self, skill: WardrobeSkill) -> None:
        """
        Replay a recorded skill using Selenium.

        Args:
            skill: The WardrobeSkill to replay

        Note:
            Uses standalone ChromeDriver. For integration with existing
            BrowserManager, see TODO below.
        """
        print(f"[REPLAY-SELENIUM] Starting replay of skill '{skill.name}'")
        print(f"[REPLAY-SELENIUM] Steps: {len(skill.steps)}")

        # Setup Chrome options (reuse existing signed-in browser if available)
        chrome_options = Options()
        if HEADLESS:
            chrome_options.add_argument("--headless")

        debug_port = os.getenv("WARDROBE_CHROME_PORT") or os.getenv("FOUNDUPS_CHROME_PORT")
        if debug_port:
            chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{debug_port}")

        user_data_dir = os.getenv("WARDROBE_CHROME_USER_DATA_DIR")
        if user_data_dir:
            chrome_options.add_argument(f"--user-data-dir={user_data_dir}")

        # TODO: Integrate with modules/infrastructure/foundups_selenium/BrowserManager for richer session reuse
        driver = webdriver.Chrome(options=chrome_options)

        try:
            # Navigate to target URL if specified
            target_url = skill.meta.get("target_url")
            if target_url:
                driver.get(target_url)
                print(f"[REPLAY-SELENIUM] Navigated to {target_url}")
            else:
                print("[REPLAY-SELENIUM] Warning: No target_url in skill.meta")

            # Replay each step
            for i, step in enumerate(skill.steps, 1):
                action = step.get("action")
                selector = step.get("selector")

                print(f"[REPLAY-SELENIUM] Step {i}/{len(skill.steps)}: {action} on {selector}")

                try:
                    # Wait for element to be present
                    wait = WebDriverWait(driver, 5)
                    element = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )

                    if action == "click":
                        element.click()
                        print(f"  OK Clicked {selector}")

                    elif action == "type":
                        text = step.get("text", "")
                        element.clear()
                        element.send_keys(text)
                        print(f"  OK Typed '{text}' into {selector}")

                    else:
                        print(f"  ⚠ Unknown action: {action}")

                    # Small delay between actions
                    time.sleep(0.5)

                except Exception as e:
                    print(f"  ERROR executing step: {e}")
                    # Continue with next step

            print(f"[REPLAY-SELENIUM] Replay complete")

            # Keep browser open for 3 seconds to see result
            time.sleep(3)

        finally:
            driver.quit()


# TODO: Integration with existing infrastructure
# - Use modules/infrastructure/foundups_selenium/BrowserManager.get_browser()
# - Leverage existing YouTube profile: chrome_profile_move2japan
# - Reuse browser sessions across skill replays
