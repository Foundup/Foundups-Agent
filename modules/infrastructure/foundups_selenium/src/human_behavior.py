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
        # Explicit initialization with default values
        self._last_x = None
        self._last_y = None

    @property
    def last_x(self):
        return getattr(self, "_last_x", None)

    @last_x.setter
    def last_x(self, value):
        self._last_x = value

    @property
    def last_y(self):
        return getattr(self, "_last_y", None)

    @last_y.setter
    def last_y(self, value):
        self._last_y = value

    def human_delay(self, base: float, variance: float = 0.5) -> float:
        """
        Generate random delay simulating human reaction time.

        Args:
            base: Base delay in seconds (e.g., 1.0)
            variance: Variance percentage (0.5 = 50% variation)

        Returns:
            Random delay between base*(1-variance) and base*(1+variance)
        """
        min_delay = base * (1 - variance)
        max_delay = base * (1 + variance)
        return random.uniform(min_delay, max_delay)

    def bezier_curve(self, start: Tuple[int, int], end: Tuple[int, int],
                     control_points: int = 2) -> List[Tuple[int, int]]:
        """
        Generate Bezier curve points for natural mouse movement.
        """
        x1, y1 = start
        x2, y2 = end

        # Control points create the "wobble" in mouse movement
        cp1_x = x1 + random.randint(-50, 50)
        cp1_y = y1 + random.randint(-50, 50)
        cp2_x = x2 + random.randint(-50, 50)
        cp2_y = y2 + random.randint(-50, 50)

        # Generate points along Bezier curve
        points = []
        steps = random.randint(15, 25)  # Slower movement

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
        """
        viewport_width = self.driver.execute_script("return window.innerWidth")
        viewport_height = self.driver.execute_script("return window.innerHeight")
        
        if self.last_x is None or self.last_y is None:
            current_x = viewport_width // 2
            current_y = viewport_height // 2
        else:
            current_x = self.last_x
            current_y = self.last_y

        location = element.location
        size = element.size

        # Target random point within element
        offset_x = random.randint(-max(1, size['width']//3), max(1, size['width']//3))
        offset_y = random.randint(-max(1, size['height']//3), max(1, size['height']//3))

        target_x = location['x'] + size['width']//2 + offset_x
        target_y = location['y'] + size['height']//2 + offset_y

        # Generate Bezier curve for mouse movement
        curve_points = self.bezier_curve(
            (current_x, current_y),
            (target_x, target_y)
        )

        # Move mouse along curve with variable speed
        action = ActionChains(self.driver)

        # "Prime" the mouse movement
        try:
            action.move_by_offset(0, 0).pause(0.01)
        except:
            pass

        last_x, last_y = current_x, current_y
        for i, (x, y) in enumerate(curve_points):
            # Slow down movement significantly for stability
            delay = random.uniform(0.02, 0.04) 

            dx = x - last_x
            dy = y - last_y

            if dx != 0 or dy != 0:
                action.move_by_offset(dx, dy)
                action.pause(delay)
                last_x, last_y = x, y

        # Track last position
        self.last_x = last_x
        self.last_y = last_y

        # Hover pause before clicking
        if pause_before_click:
            hover_time = self.human_delay(0.4, 0.5)
            action.pause(hover_time)

        return action

    def human_click(self, element):
        """Click element with human-like mouse movement and timing."""
        action = self.move_to_element_human_like(element, pause_before_click=True)
        action.click()
        action.pause(self.human_delay(0.1, 0.8))
        action.perform()
        time.sleep(self.human_delay(0.3, 0.5))

    def human_type(self, element, text: str):
        """Type text with human-like timing and occasional typos."""
        self.human_click(element)
        element.clear()
        time.sleep(self.human_delay(0.2, 0.4))

        for i, char in enumerate(text):
            if char == ' ':
                delay = self.human_delay(0.15, 0.6)
            elif char in '.,!?':
                delay = self.human_delay(0.2, 0.5)
            else:
                delay = self.human_delay(0.08, 0.7)

            if random.random() < 0.05 and i > 0:
                wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz')
                element.send_keys(wrong_char)
                time.sleep(self.human_delay(0.15, 0.5))
                element.send_keys('\b')
                time.sleep(self.human_delay(0.1, 0.4))

            element.send_keys(char)
            time.sleep(delay)

        time.sleep(self.human_delay(0.5, 0.6))

    def scroll_to_element(self, element):
        """Scroll to element with human-like smooth scrolling."""
        y_position = element.location['y']
        current_scroll = self.driver.execute_script("return window.pageYOffset")
        distance = y_position - current_scroll
        steps = random.randint(8, 15)
        step_size = distance / steps

        for i in range(steps):
            self.driver.execute_script(f"window.scrollBy(0, {step_size})")
            time.sleep(self.human_delay(0.02, 0.5))

        time.sleep(self.human_delay(0.3, 0.5))

    def random_micro_movement(self):
        """Add random micro mouse movements."""
        action = ActionChains(self.driver)
        for _ in range(random.randint(2, 5)):
            dx = random.randint(-20, 20)
            dy = random.randint(-20, 20)
            action.move_by_offset(dx, dy)
            action.pause(self.human_delay(0.1, 0.8))
        action.perform()

    def should_perform_action(self, probability: float = 0.85) -> bool:
        """Randomly decide whether to perform action."""
        return random.random() < probability

    def random_pause_thinking(self):
        """Random pause simulating reading/thinking time."""
        time.sleep(self.human_delay(1.5, 0.6))


# Singleton instance
_human_behavior_instance = None

def get_human_behavior(driver):
    """Get or create HumanBehavior singleton."""
    global _human_behavior_instance
    if _human_behavior_instance is None:
        _human_behavior_instance = HumanBehavior(driver)
    return _human_behavior_instance
