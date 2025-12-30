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
from typing import Optional, Dict, Any, Tuple, List
from selenium.common.exceptions import MoveTargetOutOfBoundsException, StaleElementReferenceException

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

    async def _switch_to_iframe_if_needed(self) -> bool:
        """Switch to iframe if platform requires it with retry logic."""
        if not self.profile.requires_iframe():
            return True

        iframe_selector = self.profile.get_iframe_selector()
        
        # Check if already in the correct iframe
        try:
            current_iframe_id = self.driver.execute_script("return window.frameElement ? window.frameElement.id : 'top';")
            clean_selector = iframe_selector.replace("iframe#", "").replace("#", "")
            if current_iframe_id != 'top' and current_iframe_id in clean_selector:
                self.in_iframe = True
                return True
        except:
            pass

        # Retry logic for switching (3 attempts)
        for attempt in range(3):
            try:
                from selenium.webdriver.common.by import By
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC

                self.driver.switch_to.default_content()
                
                # Wait for iframe to be available (max 5s)
                wait = WebDriverWait(self.driver, 5)
                iframe = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, iframe_selector)))
                
                self.driver.switch_to.frame(iframe)
                self.in_iframe = True
                logger.debug(f"[INTERACTION] Switched to iframe: {iframe_selector} (Attempt {attempt+1})")
                return True
            except Exception as e:
                logger.warning(f"[INTERACTION] Iframe switch attempt {attempt+1} failed: {e}")
                if attempt < 2:
                    await asyncio.sleep(1.0) # Wait before retry

        logger.error(f"[INTERACTION] CRITICAL: Failed to switch to iframe {iframe_selector} after 3 attempts")
        self.in_iframe = False
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

    def _is_safe_element(self, element, x: int, y: int) -> bool:
        """
        [SENTINEL] Check if an element is safe to interact with.
        Prevents clicking on ads or elements outside the intended area.
        """
        if not element:
            return False

        try:
            # Get element details and check forbidden selectors
            forbidden = getattr(self.profile, "safety_bounds", {}).get("forbidden_selectors", [])
            details = self.driver.execute_script(
                """
                const el = arguments[0];
                const forbidden = arguments[1] || [];
                
                let isForbidden = false;
                for (const sel of forbidden) {
                    try {
                        if (el.matches(sel) || el.closest(sel)) {
                            isForbidden = true;
                            break;
                        }
                    } catch(e) {}
                }

                return {
                    tag: el.tagName,
                    id: el.id || "",
                    className: el.className || "",
                    html: el.outerHTML.substring(0, 300),
                    isForbidden: isForbidden
                };
                """,
                element,
                forbidden
            )
        except Exception as e:
            logger.warning(f"[SENTINEL] Failed to get element details: {e}")
            return False

        tag = details['tag'].upper()
        el_id = details['id'].lower()
        el_class = details['className'].lower()
        el_html = details['html'].lower()

        if details.get('isForbidden'):
            logger.warning(f"[SENTINEL] FORBIDDEN ELEMENT! Selector match found. Aborting. ID={el_id}, Class={el_class}")
            return False

        # AD SIGNATURES (Broad sweep)
        ad_keywords = ["ad", "sponsor", "promoted", "yt-ad", "renderer", "overlay"]
        
        # If any keyword is found in ID or Class
        found_keywords = [k for k in ad_keywords if k in el_id or k in el_class]
        
        if found_keywords:
            # Special case for YouTube chat
            if "ad" in el_id or "ad" in el_class or "ad-slot" in el_html:
                # Filter out false positives (words containing 'ad' but are safe)
                safe_words = ["loaded", "header", "shadow", "ready", "reading", "threading", "broadcast", "background"]
                combined = (el_id + " " + el_class).lower()
                
                # Check if it's a false positive or if it's genuinely part of chat/reaction
                is_false_positive = any(word in combined for word in safe_words)
                is_legit_interaction = "chat" in el_class or "reaction" in el_class
                
                if not is_false_positive and not is_legit_interaction:
                    logger.warning(f"[SENTINEL] AD DETECTED! Blocking action. ID={el_id}, Class={el_class}, Keywords={found_keywords}")
                    return False

        # COORDINATE SAFETY (Profile bounds)
        bounds = getattr(self.profile, "safety_bounds", {})
        if bounds:
            x_min = bounds.get("x_min", 0)
            x_max = bounds.get("x_max", 9999)
            y_min = bounds.get("y_min", 0)
            y_max = bounds.get("y_max", 9999)
            
            if not (x_min <= x <= x_max and y_min <= y <= y_max):
                logger.error(f"[SENTINEL] OUT OF BOUNDS! ({x}, {y}) outside [{x_min}-{x_max}, {y_min}-{y_max}]")
                return False

        logger.debug(f"[SENTINEL] Element at ({x}, {y}) passed safety check ({tag}, {el_id}, {el_class})")
        return True

    async def _move_human_like(self, element, pause: bool = True):
        """Move mouse with human behavior if available."""
        if not self.human:
            return
            
        try:
            # Attempt to use the human behavior's move method
            action = self.human.move_to_element_human_like(element, pause_before_click=pause)
            action.perform()
        except AttributeError as e:
            if "last_x" in str(e) or "_last_x" in str(e):
                logger.warning("[INTERACTION] HumanBehavior missing last_x, recovering...")
                # Late-binding initialization if module was hot-swapped
                self.human._last_x = None
                self.human._last_y = None
                action = self.human.move_to_element_human_like(element, pause_before_click=pause)
                action.perform()
            else:
                raise e

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

        # Select the wrong element
        try:
            element = self.driver.execute_script(
                f"return document.elementFromPoint({mistake_x}, {mistake_y});"
            )
            if element:
                if self.human:
                    await self._move_human_like(element)
                self.driver.execute_script("arguments[0].click();", element)
        except Exception as e:
            logger.debug(f"[INTERACTION] Mistake click failed: {e}")

        # Realize mistake (short pause)
        await asyncio.sleep(random.uniform(0.4, 0.8))

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

        # Find element AT START to avoid stale references
        try:
            element = self.driver.execute_script(
                f"return document.elementFromPoint({x}, {y});"
            )
        except Exception:
            element = None

        if not element:
            logger.warning(f"[INTERACTION] No element found at ({x}, {y})")
            return False

        # [SENTINEL] Safety check
        if not self._is_safe_element(element, x, y):
            logger.error(f"[SENTINEL] ABORTING HOVER: Element at ({x}, {y}) is NOT safe (AD detected)")
            return False

        success = False
        
        # TIER 0: Human Bezier Movement
        if self.human:
            try:
                action = self.human.move_to_element_human_like(element, pause_before_click=False)
                action.perform()
                logger.info(f"[INTERACTION] Hovered {action_name} at ({x}, {y}) with Bezier")
                success = True
            except (MoveTargetOutOfBoundsException, StaleElementReferenceException) as e:
                logger.warning(f"[INTERACTION] T0 (Bezier) failed: {type(e).__name__}. Falling back to T1.")
            except Exception as e:
                logger.error(f"[INTERACTION] T0 unexpected error: {e}")

        # TIER 1: Native Selenium Move (Robust fallback)
        if not success:
            try:
                from selenium.webdriver.common.action_chains import ActionChains
                ActionChains(self.driver).move_to_element(element).perform()
                logger.info(f"[INTERACTION] Hovered {action_name} at ({x}, {y}) with T1 (Native)")
                success = True
            except Exception as e:
                logger.warning(f"[INTERACTION] T1 (Native) failed: {e}. Falling back to T2 (JS).")

        # TIER 2: JavaScript Fallback (Absolute fail-safe)
        if not success:
            try:
                self.driver.execute_script(
                    f"""
                    var el = document.elementFromPoint({x}, {y});
                    if (el) {{
                        el.dispatchEvent(new MouseEvent('mouseenter', {{bubbles: true, clientX: {x}, clientY: {y}}}));
                        el.dispatchEvent(new MouseEvent('mouseover', {{bubbles: true, clientX: {x}, clientY: {y}}}));
                    }}
                    """
                )
                logger.info(f"[INTERACTION] Hovered {action_name} at ({x}, {y}) with T2 (JS)")
                success = True
            except Exception as e:
                logger.error(f"[INTERACTION] T2 (JS) failed: {e}")

        # After-hover delay with fatigue
        if success:
            timing = self.profile.get_timing(action_name, "after_hover")
            if timing:
                delay = random.uniform(timing["min"], timing["max"])
                await self._apply_fatigue_delay(delay)
            self.sophistication.increment_action_count()

        return success

    async def click_action(self, action_name: str) -> bool:
        """
        Click action with full anti-detection sophistication.

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

        # Find element AT START
        try:
            element = self.driver.execute_script(
                f"return document.elementFromPoint({x}, {y});"
            )
        except Exception:
            element = None

        if not element:
            logger.warning(f"[INTERACTION] No element found at ({x}, {y})")
            return False

        # [SENTINEL] Safety check (unless bypassed for trusted actions)
        action_config = self.profile.actions.get(action_name, {})
        bypass_sentinel = action_config.get("bypass_sentinel", False)

        if not bypass_sentinel:
            if not self._is_safe_element(element, x, y):
                logger.error(f"[SENTINEL] ABORTING CLICK: Element at ({x}, {y}) is NOT safe (AD detected)")
                return False
        else:
            logger.debug(f"[SENTINEL] Bypassed for trusted action: {action_name}")

        success = False

        # TIER 0: Human Bezier Click
        if self.human:
            try:
                self.human.scroll_to_element(element)
                await asyncio.sleep(self.human.human_delay(0.2, 0.5))
                self.human.human_click(element)
                logger.info(f"[INTERACTION] Clicked {action_name} at ({x}, {y}) with Bezier")
                success = True
            except (MoveTargetOutOfBoundsException, StaleElementReferenceException) as e:
                logger.warning(f"[INTERACTION] T0 (Bezier Click) failed: {type(e).__name__}. Falling back to T1.")
            except Exception as e:
                logger.error(f"[INTERACTION] T0 Click unexpected error: {e}")

        # TIER 1: Native Selenium Click
        if not success:
            try:
                from selenium.webdriver.common.action_chains import ActionChains
                ActionChains(self.driver).move_to_element(element).click().perform()
                logger.info(f"[INTERACTION] Clicked {action_name} at ({x}, {y}) with T1 (Native)")
                success = True
            except Exception as e:
                logger.warning(f"[INTERACTION] T1 (Native Click) failed: {e}. Falling back to T2 (JS).")

        # TIER 2: JavaScript Click
        if not success:
            try:
                self.driver.execute_script("arguments[0].click();", element)
                logger.info(f"[INTERACTION] Clicked {action_name} at ({x}, {y}) with T2 (JS)")
                success = True
            except Exception as e:
                logger.error(f"[INTERACTION] T2 (JS Click) failed: {e}")

        # After-click delay with fatigue
        if success:
            timing = self.profile.get_timing(action_name, "after_click")
            if timing:
                delay = random.uniform(timing["min"], timing["max"])
                await self._apply_fatigue_delay(delay)
            self.sophistication.increment_action_count()

        return success

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
            # Always ensure popup is open/pinned and mouse is at toggle
            logger.debug(f"[INTERACTION] Syncing with toggle position (Action #{i+1})...")
            await self.hover_action("party_toggle")
            await asyncio.sleep(0.8) # Wait for stability
            
            # Perform the reaction click
            success = await self.click_action(action_name)
            
            if success:
                results["success"] += 1
                # User feedback: Always move back to the hover activator position
                logger.debug("[INTERACTION] Returning to activator position...")
                await self.hover_action("party_toggle")
            else:
                results["errors"] += 1
            
            # Small pause between rounds
            await asyncio.sleep(0.5)

            # Progress logging
            if (i + 1) % 10 == 0:
                logger.info(f"[INTERACTION] Progress: {i+1}/{count} ({results['success']} success, {results['errors']} errors)")

        logger.info(
            f"[INTERACTION] Complete! {results['success']}/{count} successful "
            f"({results['errors']} errors, {results['thinking_pauses']} pauses)"
        )

        return results

    async def party_spam(self, reaction_sequence: List[str]) -> Dict[str, int]:
        """
        Specialized hardened party spam - maintains hover to keep menu open.
        
        WSP 49 Hardening:
        - Continuous hover on toggle or reaction area.
        - Slow Bezier movement between reactions (012-like).
        - Random delays to prevent detection.
        - No 'return to toggle' between clicks unless menu closes.
        """
        results = {"success": 0, "errors": 0}
        
        if not await self._switch_to_iframe_if_needed():
            return {"error": "iframe_switch_failed"}

        logger.info(f"[INTERACTION] Starting hardened !party sequence ({len(reaction_sequence)} reactions)...")

        # 1. Initial hover to open menu
        success = await self.hover_action("party_toggle")
        if not success:
            logger.error("[INTERACTION] Failed to trigger reaction menu")
            return {"error": "menu_trigger_failed"}
            
        # Wait for slide-up animation
        await asyncio.sleep(0.8)

        for i, reaction_name in enumerate(reaction_sequence):
            # 2. Get coordinates for this reaction
            action_name = f"reaction_{reaction_name}"
            try:
                x, y = self._get_coordinates_with_variance(action_name)
            except ValueError:
                logger.warning(f"[INTERACTION] Skipping unknown reaction: {reaction_name}")
                continue

            # 3. Find element
            try:
                element = self.driver.execute_script(f"return document.elementFromPoint({x}, {y});")
            except Exception:
                element = None

            if not element:
                logger.warning(f"[INTERACTION] No element found for {reaction_name} at ({x}, {y})")
                results["errors"] += 1
                continue

            # 4. Move SLOWLY (Bezier) to the reaction
            # We use a custom move here to be slower than standard
            if self.human:
                try:
                    # Slow down the curve even more for 012 feel
                    curve_points = self.human.bezier_curve(
                        (self.human.last_x or x, self.human.last_y or y),
                        (x, y)
                    )
                    action = ActionChains(self.driver)
                    last_x, last_y = self.human.last_x or x, self.human.last_y or y
                    
                    for px, py in curve_points:
                        delay = random.uniform(0.04, 0.08) # 2x slower than normal
                        dx, dy = px - last_x, py - last_y
                        if dx != 0 or dy != 0:
                            action.move_by_offset(dx, dy).pause(delay)
                            last_x, last_y = px, py
                    
                    self.human.last_x, self.human.last_y = last_x, last_y
                    action.perform()
                except Exception as e:
                    logger.warning(f"[INTERACTION] Slow Bezier failed: {e}")
                    # Fallback to standard move
                    await self._move_human_like(element, pause=False)
            
            # 5. Click the reaction
            try:
                # Direct JS click is safest for spam to avoid menu closing on missed click
                self.driver.execute_script("arguments[0].click();", element)
                results["success"] += 1
                logger.debug(f"[INTERACTION] Clicked {reaction_name} (#{i+1})")
            except Exception as e:
                logger.warning(f"[INTERACTION] Click failed for {reaction_name}: {e}")
                results["errors"] += 1

            # 6. Random "fanatic" pause
            await asyncio.sleep(random.uniform(0.1, 0.3))
            
            # 7. Periodically re-hover toggle to ensure menu stays open (every 5 clicks)
            if (i + 1) % 5 == 0:
                await self.hover_action("party_toggle")
                await asyncio.sleep(0.4)

        logger.info(f"[INTERACTION] Hardened !party sequence complete: {results}")
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
