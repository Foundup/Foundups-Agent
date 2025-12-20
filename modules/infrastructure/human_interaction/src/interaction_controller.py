"""
Human Interaction Controller - Unified Anti-Detection Interface
===============================================================

High-level API for human-like platform interactions across ALL platforms.

One module. All platforms. Maximum sophistication.

Features:
- Bezier curve mouse movement (via human_behavior.py)
- Coordinate variance (±8px per click)
- Probabilistic errors (8-13% miss rate)
- Fatigue modeling (1.0x → 1.8x slower)
- Thinking pauses (30% chance, 0.5-2.0s)
- Platform abstraction (YouTube, LinkedIn, X/Twitter)

WSP Compliance: WSP 49 (Platform Integration Safety), WSP 3 (Module Organization)

Example Usage:
    from modules.infrastructure.human_interaction import get_interaction_controller

    interaction = get_interaction_controller(driver, platform="youtube_chat")

    # Hover with Bezier curves
    await interaction.hover_action("party_toggle")

    # Click with full sophistication
    await interaction.click_action("reaction_celebrate")

    # Spam action with errors + fatigue
    results = await interaction.spam_action("reaction_heart", count=30)
"""

import asyncio
import random
import logging
from typing import Optional, Dict, Any, Tuple

logger = logging.getLogger(__name__)


class InteractionController:
    """
    Unified human-like interaction controller for all platforms.

    Automatically applies anti-detection measures to every action:
    - Bezier curves for mouse movement
    - Coordinate variance (humans don't click exact pixels)
    - Random delays with fatigue modeling
    - Probabilistic errors (occasional mistakes)
    - Thinking pauses (hesitation)
    """

    def __init__(self, driver, platform: str = "youtube_chat"):
        """
        Args:
            driver: Selenium WebDriver instance
            platform: Platform name (e.g., "youtube_chat", "linkedin", "twitter")
        """
        self.driver = driver
        self.platform_name = platform

        # Load platform profile
        from .platform_profiles import load_platform_profile
        self.profile = load_platform_profile(platform)
        logger.info(f"[INTERACTION] Loaded platform profile: {platform}")

        # Initialize human behavior (Bezier curves, delays)
        try:
            from modules.infrastructure.foundups_selenium.src.human_behavior import get_human_behavior
            self.human = get_human_behavior(driver)
            self.human_available = True
            logger.info("[INTERACTION] Human behavior simulation loaded")
        except ImportError as e:
            logger.warning(f"[INTERACTION] Human behavior not available: {e}")
            self.human = None
            self.human_available = False

        # Initialize sophistication engine (errors, fatigue, thinking)
        from .sophistication_engine import SophisticationEngine
        error_config = self.profile.error_simulation
        timing_config = self.profile.global_timing

        self.sophistication = SophisticationEngine(
            base_error_rate=error_config.get("base_rate", 0.08),
            fatigue_threshold=timing_config.get("fatigue_threshold", 20),
            thinking_probability=timing_config.get("thinking_pause", {}).get("probability", 0.30)
        )

        self.in_iframe = False

    def _switch_to_iframe_if_needed(self) -> bool:
        """Switch to iframe if platform requires it."""
        if not self.profile.requires_iframe():
            return True

        if self.in_iframe:
            return True

        try:
            from selenium.webdriver.common.by import By

            self.driver.switch_to.default_content()
            iframe_selector = self.profile.get_iframe_selector()
            iframe = self.driver.find_element(By.CSS_SELECTOR, iframe_selector)
            self.driver.switch_to.frame(iframe)
            self.in_iframe = True
            logger.info(f"[INTERACTION] Switched to iframe: {iframe_selector}")
            return True
        except Exception as e:
            logger.warning(f"[INTERACTION] Failed to switch to iframe: {e}")
            return False

    def _get_coordinates_with_variance(self, action_name: str) -> Tuple[int, int]:
        """
        Get coordinates with human-like variance.

        Humans don't click exact same pixel - add ±8px variance.
        """
        base_coords = self.profile.get_coordinates(action_name)
        variance = self.profile.get_variance(action_name)

        if not base_coords:
            raise ValueError(f"Action not found in profile: {action_name}")

        x_base, y_base = base_coords
        x_var, y_var = variance

        # Add random variance
        x = x_base + random.randint(-x_var, x_var)
        y = y_base + random.randint(-y_var, y_var)

        return (x, y)

    async def _thinking_pause(self):
        """Pause to simulate thinking/hesitation."""
        duration = self.sophistication.get_thinking_duration()
        logger.info(f"[INTERACTION] Thinking pause ({duration:.2f}s)...")
        await asyncio.sleep(duration)

    async def _apply_fatigue_delay(self, base_delay: float) -> float:
        """Apply fatigue multiplier to delay."""
        multiplier = self.sophistication.get_fatigue_multiplier()
        final_delay = base_delay * multiplier
        await asyncio.sleep(final_delay)
        return final_delay

    async def _make_mistake(self, target_x: int, target_y: int) -> bool:
        """
        Simulate a mistake (click misses target).

        Returns:
            True (mistake was made)
        """
        x_offset, y_offset = self.sophistication.generate_mistake_offset()
        mistake_x = target_x + x_offset
        mistake_y = target_y + y_offset

        logger.info(f"[INTERACTION] Oops! Clicked ({mistake_x}, {mistake_y}) instead of ({target_x}, {target_y})")

        # Click the wrong spot
        element = self.driver.execute_script(
            f"return document.elementFromPoint({mistake_x}, {mistake_y});"
        )

        if element and self.human:
            # Use Bezier curves even for mistakes!
            try:
                self.human.human_click(element)
            except:
                # Fallback to JavaScript click
                self.driver.execute_script("arguments[0].click();", element)

        # Realize mistake (short pause)
        await asyncio.sleep(random.uniform(0.2, 0.4))

        return True  # Mistake was made

    async def hover_action(self, action_name: str) -> bool:
        """
        Hover at action coordinates with Bezier curve movement.

        Args:
            action_name: Action name from platform profile

        Returns:
            True if successful, False otherwise
        """
        if not self._switch_to_iframe_if_needed():
            return False

        # Thinking pause (30% chance)
        if self.sophistication.should_pause_to_think():
            await self._thinking_pause()

        # Get coordinates with variance
        x, y = self._get_coordinates_with_variance(action_name)

        # Find element at coordinates
        element = self.driver.execute_script(
            f"return document.elementFromPoint({x}, {y});"
        )

        if not element:
            logger.warning(f"[INTERACTION] No element found at ({x}, {y})")
            return False

        # Hover with Bezier curve movement
        if self.human:
            action = self.human.move_to_element_human_like(element, pause_before_click=False)
            action.perform()
            logger.info(f"[INTERACTION] Hovered {action_name} at ({x}, {y}) with Bezier")
        else:
            # Fallback to JavaScript
            self.driver.execute_script(
                f"""
                var el = document.elementFromPoint({x}, {y});
                if (el) {{
                    el.dispatchEvent(new MouseEvent('mouseenter', {{bubbles: true, clientX: {x}, clientY: {y}}}));
                    el.dispatchEvent(new MouseEvent('mouseover', {{bubbles: true, clientX: {x}, clientY: {y}}}));
                }}
                """
            )
            logger.info(f"[INTERACTION] Hovered {action_name} at ({x}, {y}) with JavaScript")

        # After-hover delay with fatigue
        timing = self.profile.get_timing(action_name, "after_hover")
        if timing:
            delay = random.uniform(timing["min"], timing["max"])
            await self._apply_fatigue_delay(delay)

        self.sophistication.increment_action_count()
        return True

    async def click_action(self, action_name: str) -> bool:
        """
        Click action with full anti-detection sophistication.

        Automatically includes:
        - Thinking pause (30% chance)
        - Bezier curve mouse movement
        - Coordinate variance (±8px)
        - Probabilistic errors (8-13% miss rate)
        - Fatigue modeling (slower over time)

        Args:
            action_name: Action name from platform profile

        Returns:
            True if successful, False if error/mistake
        """
        if not self._switch_to_iframe_if_needed():
            return False

        # Thinking pause (30% chance)
        if self.sophistication.should_pause_to_think():
            await self._thinking_pause()

        # Get coordinates with variance
        x, y = self._get_coordinates_with_variance(action_name)

        # Probabilistic error (mistake)
        if self.sophistication.should_make_mistake():
            await self._make_mistake(x, y)
            self.sophistication.increment_action_count()
            return False  # Mistake made, action failed

        # Find element at coordinates
        element = self.driver.execute_script(
            f"return document.elementFromPoint({x}, {y});"
        )

        if not element:
            logger.warning(f"[INTERACTION] No element found at ({x}, {y})")
            return False

        # Click with Bezier curve movement
        if self.human:
            try:
                self.human.scroll_to_element(element)
                await asyncio.sleep(self.human.human_delay(0.2, 0.5))
                self.human.human_click(element)
                logger.info(f"[INTERACTION] Clicked {action_name} at ({x}, {y}) with Bezier")
            except Exception as e:
                logger.warning(f"[INTERACTION] Bezier click failed: {e}, falling back to JavaScript")
                self.driver.execute_script("arguments[0].click();", element)
        else:
            # Fallback to JavaScript
            self.driver.execute_script("arguments[0].click();", element)
            logger.info(f"[INTERACTION] Clicked {action_name} at ({x}, {y}) with JavaScript")

        # After-click delay with fatigue
        timing = self.profile.get_timing(action_name, "after_click")
        if timing:
            delay = random.uniform(timing["min"], timing["max"])
            await self._apply_fatigue_delay(delay)

        self.sophistication.increment_action_count()
        return True

    async def spam_action(self, action_name: str, count: int = 30) -> Dict[str, int]:
        """
        Spam action multiple times with full sophistication.

        Automatically handles:
        - Popup re-opening (every 3 clicks for YouTube)
        - Errors and fatigue
        - Progress logging

        Args:
            action_name: Action to spam
            count: Number of times to perform action

        Returns:
            Dictionary with success/error counts
        """
        results = {"success": 0, "errors": 0, "thinking_pauses": 0}

        popup_interval = self.profile.global_timing.get("popup_reopen_interval", 3)

        logger.info(f"[INTERACTION] Spamming {action_name} {count} times...")

        for i in range(count):
            # Re-open popup every N clicks (for YouTube reactions)
            if i % popup_interval == 0 and "party_toggle" in self.profile.actions:
                await self.hover_action("party_toggle")

            # Perform action
            success = await self.click_action(action_name)

            if success:
                results["success"] += 1
            else:
                results["errors"] += 1

            # Progress logging
            if (i + 1) % 10 == 0:
                logger.info(f"[INTERACTION] Progress: {i+1}/{count} ({results['success']} success, {results['errors']} errors)")

        logger.info(
            f"[INTERACTION] Complete! {results['success']}/{count} successful "
            f"({results['errors']} errors, {results['thinking_pauses']} pauses)"
        )

        return results

    def get_stats(self) -> Dict[str, Any]:
        """Get current interaction statistics."""
        return {
            "platform": self.platform_name,
            "sophistication": self.sophistication.get_stats(),
            "human_behavior_available": self.human_available,
            "in_iframe": self.in_iframe
        }

    def reset_sophistication(self):
        """Reset sophistication engine (e.g., after long break)."""
        self.sophistication.reset()


# Global registry of controllers (one per driver+platform)
_controllers = {}

def get_interaction_controller(driver, platform: str = "youtube_chat") -> InteractionController:
    """
    Get or create interaction controller for a platform.

    Args:
        driver: Selenium WebDriver instance
        platform: Platform name

    Returns:
        InteractionController instance
    """
    key = (id(driver), platform)

    if key not in _controllers:
        _controllers[key] = InteractionController(driver, platform)
        logger.info(f"[INTERACTION] Created controller for platform: {platform}")

    return _controllers[key]
