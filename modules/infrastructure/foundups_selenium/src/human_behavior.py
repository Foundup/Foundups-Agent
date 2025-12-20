"""
Human Behavior Simulation
========================

Mimics human-like browser interaction patterns to evade automation detection.

WSP References: WSP 77 (AI Coordination), WSP 91 (Observability)
"""

import random
import time
import math
from typing import Tuple, List
from selenium.webdriver.common.action_chains import ActionChains


class HumanBehavior:
    """Simulates human-like browser interactions."""

    def __init__(self, driver):
        self.driver = driver

    def human_delay(self, base: float, variance: float = 0.5) -> float:
        """
        Generate random delay simulating human reaction time.

        Args:
            base: Base delay in seconds (e.g., 1.0)
            variance: Variance percentage (0.5 = 50% variation)

        Returns:
            Random delay between base*(1-variance) and base*(1+variance)

        Example:
            human_delay(1.0, 0.5) → 0.5s to 1.5s random
        """
        min_delay = base * (1 - variance)
        max_delay = base * (1 + variance)
        return random.uniform(min_delay, max_delay)

    def bezier_curve(self, start: Tuple[int, int], end: Tuple[int, int],
                     control_points: int = 2) -> List[Tuple[int, int]]:
        """
        Generate Bezier curve points for natural mouse movement.

        Humans don't move mouse in straight lines - they follow curved paths
        with acceleration and deceleration.

        Args:
            start: (x, y) starting position
            end: (x, y) ending position
            control_points: Number of control points (2 = cubic Bezier)

        Returns:
            List of (x, y) coordinates along curve
        """
        # Generate random control points for natural curve
        x1, y1 = start
        x2, y2 = end

        # Control points create the "wobble" in mouse movement
        cp1_x = x1 + random.randint(-50, 50)
        cp1_y = y1 + random.randint(-50, 50)
        cp2_x = x2 + random.randint(-50, 50)
        cp2_y = y2 + random.randint(-50, 50)

        # Generate points along Bezier curve
        points = []
        steps = random.randint(10, 20)  # Variable movement speed

        for i in range(steps + 1):
            t = i / steps

            # Cubic Bezier formula
            x = (
                (1 - t)**3 * x1 +
                3 * (1 - t)**2 * t * cp1_x +
                3 * (1 - t) * t**2 * cp2_x +
                t**3 * x2
            )
            y = (
                (1 - t)**3 * y1 +
                3 * (1 - t)**2 * t * cp1_y +
                3 * (1 - t) * t**2 * cp2_y +
                t**3 * y2
            )

            points.append((int(x), int(y)))

        return points

    def move_to_element_human_like(self, element, pause_before_click: bool = True):
        """
        Move mouse to element with human-like Bezier curve path.

        Args:
            element: Selenium WebElement to move to
            pause_before_click: Add random hover pause before clicking

        Returns:
            ActionChains object ready for click
        """
        # Get current mouse position (approximate center of viewport)
        viewport_width = self.driver.execute_script("return window.innerWidth")
        viewport_height = self.driver.execute_script("return window.innerHeight")
        current_x = viewport_width // 2
        current_y = viewport_height // 2

        # Get element location and size
        location = element.location
        size = element.size

        # Target random point within element (humans don't click exact center)
        offset_x = random.randint(-size['width']//3, size['width']//3)
        offset_y = random.randint(-size['height']//3, size['height']//3)

        target_x = location['x'] + size['width']//2 + offset_x
        target_y = location['y'] + size['height']//2 + offset_y

        # Generate Bezier curve for mouse movement
        curve_points = self.bezier_curve(
            (current_x, current_y),
            (target_x, target_y)
        )

        # Move mouse along curve with variable speed
        action = ActionChains(self.driver)

        for i, (x, y) in enumerate(curve_points):
            # Variable speed (accelerate, then decelerate)
            if i < len(curve_points) // 3:
                delay = 0.01  # Fast at start
            elif i < 2 * len(curve_points) // 3:
                delay = 0.005  # Faster in middle
            else:
                delay = 0.015  # Slow near target

            action.move_by_offset(x - current_x, y - current_y)
            action.pause(delay)
            current_x, current_y = x, y

        # Hover pause before clicking (humans don't instant-click)
        if pause_before_click:
            hover_time = self.human_delay(0.2, 0.6)  # 0.08s-0.32s
            action.pause(hover_time)

        return action

    def human_click(self, element):
        """
        Click element with human-like mouse movement and timing.

        This replaces driver.execute_script("element.click()") which is
        easily detected by YouTube.

        Args:
            element: Selenium WebElement to click
        """
        # Move to element with Bezier curve
        action = self.move_to_element_human_like(element, pause_before_click=True)

        # Click with slight randomization (humans don't have perfect timing)
        action.click()

        # Post-click micro-pause (mouse stays on element briefly)
        action.pause(self.human_delay(0.1, 0.8))  # 0.02s-0.18s

        # Execute all actions
        action.perform()

        # Additional delay after click (reaction time to see result)
        time.sleep(self.human_delay(0.3, 0.5))  # 0.15s-0.45s

    def human_type(self, element, text: str):
        """
        Type text with human-like timing and occasional typos.

        Args:
            element: Selenium WebElement (input field)
            text: Text to type
        """
        # Focus element first (humans click before typing)
        self.human_click(element)

        # Clear existing text
        element.clear()
        time.sleep(self.human_delay(0.2, 0.4))  # 0.12s-0.28s

        # Type character by character with variable speed
        for i, char in enumerate(text):
            # Variable typing speed (humans aren't consistent)
            if char == ' ':
                delay = self.human_delay(0.15, 0.6)  # Slower for spaces
            elif char in '.,!?':
                delay = self.human_delay(0.2, 0.5)  # Pause at punctuation
            else:
                delay = self.human_delay(0.08, 0.7)  # Normal typing

            # Occasional "typo" then backspace (5% chance)
            if random.random() < 0.05 and i > 0:
                wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz')
                element.send_keys(wrong_char)
                time.sleep(self.human_delay(0.15, 0.5))
                element.send_keys('\b')  # Backspace
                time.sleep(self.human_delay(0.1, 0.4))

            element.send_keys(char)
            time.sleep(delay)

        # Final pause (review before submitting)
        time.sleep(self.human_delay(0.5, 0.6))  # 0.2s-0.8s

    def scroll_to_element(self, element):
        """
        Scroll to element with human-like smooth scrolling.

        Args:
            element: Selenium WebElement to scroll to
        """
        # Get element position
        y_position = element.location['y']

        # Scroll in chunks (humans don't instant-scroll)
        current_scroll = self.driver.execute_script("return window.pageYOffset")
        distance = y_position - current_scroll

        # Number of scroll steps (more steps = smoother)
        steps = random.randint(8, 15)
        step_size = distance / steps

        for i in range(steps):
            self.driver.execute_script(f"window.scrollBy(0, {step_size})")
            time.sleep(self.human_delay(0.02, 0.5))  # 0.01s-0.03s per step

        # Final adjustment pause
        time.sleep(self.human_delay(0.3, 0.5))  # 0.15s-0.45s

    def random_micro_movement(self):
        """
        Add random micro mouse movements (humans fidget).

        Call this periodically during page interaction to simulate
        natural mouse movement when reading/thinking.
        """
        action = ActionChains(self.driver)

        # Small random movements
        for _ in range(random.randint(2, 5)):
            dx = random.randint(-20, 20)
            dy = random.randint(-20, 20)
            action.move_by_offset(dx, dy)
            action.pause(self.human_delay(0.1, 0.8))

        action.perform()

    def should_perform_action(self, probability: float = 0.85) -> bool:
        """
        Randomly decide whether to perform action (simulates human selectivity).

        Args:
            probability: Chance of performing action (0.85 = 85%)

        Returns:
            True if action should be performed

        Example:
            # 85% chance to like (humans don't like EVERY comment)
            if human.should_perform_action(0.85):
                human.human_click(like_button)
        """
        return random.random() < probability

    def random_pause_thinking(self):
        """
        Random pause simulating reading/thinking time.

        Call this between actions to simulate human comprehension time.
        """
        # Humans pause to read comments before acting
        time.sleep(self.human_delay(1.5, 0.6))  # 0.6s-2.4s


# Singleton instance
_human_behavior_instance = None

def get_human_behavior(driver):
    """Get or create HumanBehavior singleton."""
    global _human_behavior_instance
    if _human_behavior_instance is None:
        _human_behavior_instance = HumanBehavior(driver)
    return _human_behavior_instance
