"""
Sophistication Engine - Human Imperfection Simulation
=====================================================

Adds human-like imperfections to automated interactions:
- Probabilistic errors (mistakes)
- Fatigue modeling (slower over time)
- Thinking pauses (hesitation before actions)

WSP Compliance: WSP 49 (Platform Integration Safety)
"""

import random
import logging
from typing import Tuple

logger = logging.getLogger(__name__)


class SophisticationEngine:
    """
    Simulates human imperfections to evade automation detection.

    Key Behaviors:
    - Errors: 8% base rate → 13% with fatigue
    - Fatigue: Actions slow down 1.0x → 1.8x after threshold
    - Thinking: 30% chance of 0.5-2.0s pause before action
    """

    def __init__(
        self,
        base_error_rate: float = 0.08,
        fatigue_threshold: int = 20,
        thinking_probability: float = 0.30
    ):
        """
        Args:
            base_error_rate: Base probability of making a mistake (default 8%)
            fatigue_threshold: Actions before fatigue kicks in (default 20)
            thinking_probability: Chance of pausing to think (default 30%)
        """
        self.base_error_rate = base_error_rate
        self.fatigue_threshold = fatigue_threshold
        self.thinking_probability = thinking_probability
        self.action_count = 0

    def should_make_mistake(self) -> bool:
        """
        Determine if current action should be a mistake.

        Error rate increases with fatigue:
        - Actions 0-20: 8% error rate
        - Actions 21-50: 8% → 13% (linear increase)
        - Actions 50+: 13% max error rate

        Returns:
            True if should make a mistake, False otherwise
        """
        # Calculate fatigue factor (0.0 to 1.0)
        if self.action_count < self.fatigue_threshold:
            fatigue_factor = 0.0
        else:
            excess = self.action_count - self.fatigue_threshold
            fatigue_factor = min(excess / 30.0, 1.0)  # Cap at 1.0

        # Calculate current error rate
        fatigue_increase = 0.05  # Max 5% increase
        current_error_rate = self.base_error_rate + (fatigue_factor * fatigue_increase)

        # Probabilistic check
        will_error = random.random() < current_error_rate

        if will_error:
            logger.info(
                f"[SOPHISTICATION] Making mistake (action #{self.action_count}, "
                f"error_rate={current_error_rate:.1%})"
            )

        return will_error

    def get_fatigue_multiplier(self) -> float:
        """
        Get delay multiplier based on fatigue.

        Delays increase with action count:
        - Actions 0-20: 1.0x (normal speed)
        - Actions 21-50: 1.0x → 1.8x (linear slowdown)
        - Actions 50+: 1.8x (max slowdown)

        Returns:
            Multiplier for delays (1.0 to 1.8)
        """
        if self.action_count < self.fatigue_threshold:
            return 1.0

        excess = self.action_count - self.fatigue_threshold
        fatigue_slowdown = min(excess / 30.0, 0.8)  # Max 0.8 additional

        multiplier = 1.0 + fatigue_slowdown

        if self.action_count % 10 == 0 and self.action_count >= self.fatigue_threshold:
            logger.info(
                f"[SOPHISTICATION] Fatigue kicking in (action #{self.action_count}, "
                f"slowdown={multiplier:.2f}x)"
            )

        return multiplier

    def should_pause_to_think(self) -> bool:
        """
        Determine if should pause before action (simulate thinking/hesitation).

        Returns:
            True if should pause, False otherwise
        """
        return random.random() < self.thinking_probability

    def get_thinking_duration(self) -> float:
        """
        Get random thinking pause duration.

        Returns:
            Duration in seconds (0.5 to 2.0)
        """
        return random.uniform(0.5, 2.0)

    def generate_mistake_offset(self, max_offset: int = 50) -> Tuple[int, int]:
        """
        Generate coordinate offset for a mistake click.

        Mistakes click near the target but miss:
        - 70% chance: Small miss (10-30px off)
        - 30% chance: Big miss (30-50px off)

        Args:
            max_offset: Maximum pixel offset (default 50px)

        Returns:
            (x_offset, y_offset) tuple
        """
        # Determine mistake severity
        if random.random() < 0.7:
            # Small miss
            offset_range = (10, 30)
        else:
            # Big miss
            offset_range = (30, max_offset)

        # Random direction
        x_offset = random.randint(offset_range[0], offset_range[1])
        y_offset = random.randint(offset_range[0], offset_range[1])

        # Randomize sign (positive or negative)
        if random.random() < 0.5:
            x_offset = -x_offset
        if random.random() < 0.5:
            y_offset = -y_offset

        logger.debug(f"[SOPHISTICATION] Mistake offset: ({x_offset}, {y_offset})")
        return (x_offset, y_offset)

    def increment_action_count(self):
        """Increment action counter (called after each action)."""
        self.action_count += 1

    def reset(self):
        """Reset action counter (e.g., after long pause or new session)."""
        logger.info(f"[SOPHISTICATION] Resetting (completed {self.action_count} actions)")
        self.action_count = 0

    def get_stats(self) -> dict:
        """
        Get current sophistication stats.

        Returns:
            Dictionary with current state metrics
        """
        error_rate = self.base_error_rate
        if self.action_count >= self.fatigue_threshold:
            excess = self.action_count - self.fatigue_threshold
            fatigue_factor = min(excess / 30.0, 1.0)
            error_rate += fatigue_factor * 0.05

        return {
            "action_count": self.action_count,
            "current_error_rate": error_rate,
            "fatigue_multiplier": self.get_fatigue_multiplier(),
            "is_fatigued": self.action_count >= self.fatigue_threshold
        }
