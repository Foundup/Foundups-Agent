"""F_i Rating Engine - Color Temperature Gradient Rating System.

CABR/PoB Paradigm - Protocol Participation, Not Investment

Rating dimensions capture 0102/012 response to a FoundUp:
- velocity: Agent execution rate (0102 work output per epoch)
- traction: Market response (012 engagement, subscriptions)
- health: Operational state (build completeness, test coverage)
- potential: Founder conviction score (anonymous track record + 012 signals)

COLOR TEMPERATURE GRADIENT (scientific, not cartoon):
- 0.0 = VIOLET (cold start, idea phase)
- 0.2 = BLUE (early scaffold)
- 0.4 = CYAN (building momentum)
- 0.5 = GREEN (neutral/baseline)
- 0.6 = YELLOW (warming up)
- 0.8 = ORANGE (gaining heat)
- 1.0 = RED (red hot - exceptional performance)

The key border in the animation changes color based on F_i composite rating.

WSP References:
- WSP 26: Token economics (F_i distribution)
- WSP 29: CABR 3V engine (V3 valuation score)
- WSP 22: ModLog documentation
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple
import math


class ColorTemperature(Enum):
    """Color temperature gradient tiers (cool to hot)."""
    VIOLET = 0.0   # Cold start
    BLUE = 0.2     # Early stage
    CYAN = 0.4     # Building
    GREEN = 0.5    # Neutral baseline
    YELLOW = 0.6   # Warming
    ORANGE = 0.8   # Hot
    RED = 1.0      # Red hot


# Color hex values for gradient interpolation
COLOR_GRADIENT = [
    (0.0, "#8B00FF"),   # Violet
    (0.2, "#0066FF"),   # Blue
    (0.4, "#00E5D0"),   # Cyan
    (0.5, "#00B341"),   # Green
    (0.6, "#FFD700"),   # Yellow
    (0.8, "#FF8C00"),   # Orange
    (1.0, "#FF2D2D"),   # Red
]


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    """Convert RGB tuple to hex color."""
    return '#{:02x}{:02x}{:02x}'.format(*rgb)


def interpolate_color(rating: float) -> str:
    """Interpolate color from gradient based on rating (0.0-1.0).

    Returns hex color string for use in CSS/Canvas.
    """
    rating = max(0.0, min(1.0, rating))  # Clamp to 0-1

    # Find the two colors to interpolate between
    lower_stop = COLOR_GRADIENT[0]
    upper_stop = COLOR_GRADIENT[-1]

    for i, (stop, color) in enumerate(COLOR_GRADIENT):
        if stop <= rating:
            lower_stop = (stop, color)
        if stop >= rating:
            upper_stop = (stop, color)
            break

    # Calculate interpolation factor
    if upper_stop[0] == lower_stop[0]:
        t = 0.0
    else:
        t = (rating - lower_stop[0]) / (upper_stop[0] - lower_stop[0])

    # Interpolate RGB values
    lower_rgb = hex_to_rgb(lower_stop[1])
    upper_rgb = hex_to_rgb(upper_stop[1])

    result_rgb = tuple(
        int(lower_rgb[i] + t * (upper_rgb[i] - lower_rgb[i]))
        for i in range(3)
    )

    return rgb_to_hex(result_rgb)


@dataclass
class FounderTrackRecord:
    """Anonymous founder performance history.

    Founders are anonymous but their track record is transparent:
    - Total FoundUps participated in
    - Count at each color tier (how many reached RED/ORANGE/etc.)
    - Weighted score based on outcomes

    Key insight: A founder with 3 RED HOT outcomes is highly attractive
    even if anonymous - the protocol tracks performance, not identity.
    """
    total_foundups: int = 0
    tier_counts: Dict[str, int] = field(default_factory=lambda: {
        "red": 0,      # Red hot (1.0) - exceptional
        "orange": 0,   # Hot (0.8) - strong performer
        "yellow": 0,   # Warming (0.6) - solid
        "green": 0,    # Baseline (0.5) - neutral
        "cyan": 0,     # Building (0.4) - early
        "blue": 0,     # Early (0.2) - nascent
        "violet": 0,   # Cold (0.0) - failed/abandoned
    })
    is_influencer: bool = False  # Social proof amplifier
    community_size: int = 0      # Follower count proxy

    @property
    def weighted_score(self) -> float:
        """Calculate weighted founder score (0.0-1.0).

        Weights favor successful outcomes heavily:
        - RED = 1.0 (10x weight)
        - ORANGE = 0.8 (5x weight)
        - YELLOW = 0.6 (2x weight)
        - GREEN = 0.5 (1x weight - neutral)
        - Below GREEN = negative weight (drags down score)
        """
        if self.total_foundups == 0:
            return 0.5  # No track record = neutral

        weights = {
            "red": 10.0,
            "orange": 5.0,
            "yellow": 2.0,
            "green": 1.0,
            "cyan": 0.5,
            "blue": 0.2,
            "violet": -0.5,  # Negative for abandoned
        }

        total_weight = sum(
            self.tier_counts.get(tier, 0) * weight
            for tier, weight in weights.items()
        )

        # Normalize to 0-1 range
        # Max theoretical per FoundUp = 10.0 (all RED)
        # Baseline per FoundUp = 1.0 (all GREEN)
        max_score = self.total_foundups * 10.0
        baseline_score = self.total_foundups * 1.0

        # Score relative to baseline, clamped to 0-1
        if max_score == 0:
            return 0.5

        # Influencer bonus: up to 10% boost
        influencer_bonus = 0.0
        if self.is_influencer:
            # Logarithmic scaling for community size
            influencer_bonus = min(0.1, math.log10(max(1, self.community_size)) / 60)

        raw_score = (total_weight / max_score) + influencer_bonus
        return max(0.0, min(1.0, raw_score))

    def to_1_7_scale(self) -> int:
        """Convert to 1-7 founder rating scale.

        1 = Untested (no track record)
        2 = Risky (mostly failures)
        3 = Below average
        4 = Average (GREEN tier)
        5 = Above average (YELLOW tier)
        6 = Strong (ORANGE tier)
        7 = Exceptional (RED tier track record)
        """
        score = self.weighted_score

        if self.total_foundups == 0:
            return 1  # Untested

        # Map 0-1 score to 1-7 scale
        if score < 0.2:
            return 2
        elif score < 0.35:
            return 3
        elif score < 0.5:
            return 4
        elif score < 0.65:
            return 5
        elif score < 0.8:
            return 6
        else:
            return 7


@dataclass
class FiRating:
    """F_i rating for a single FoundUp.

    Composite of 4 dimensions weighted for protocol health:
    - velocity (30%): How fast is 0102 executing?
    - traction (30%): How are 012 responding?
    - health (20%): Is the build solid?
    - potential (20%): What's the founder conviction?

    Each dimension is 0.0-1.0, composite is also 0.0-1.0.
    """
    velocity: float = 0.0      # Agent work rate (0102 execution per epoch)
    traction: float = 0.0      # Market response (012 engagement)
    health: float = 0.0        # Operational state (build completeness)
    potential: float = 0.0     # Founder conviction (track record + signals)

    # Weights sum to 1.0
    VELOCITY_WEIGHT = 0.30
    TRACTION_WEIGHT = 0.30
    HEALTH_WEIGHT = 0.20
    POTENTIAL_WEIGHT = 0.20

    @property
    def composite(self) -> float:
        """Calculate composite rating (0.0-1.0).

        Returns value for color temperature gradient mapping.
        """
        return (
            self.velocity * self.VELOCITY_WEIGHT +
            self.traction * self.TRACTION_WEIGHT +
            self.health * self.HEALTH_WEIGHT +
            self.potential * self.POTENTIAL_WEIGHT
        )

    @property
    def color(self) -> str:
        """Get interpolated color for this rating."""
        return interpolate_color(self.composite)

    @property
    def temperature_tier(self) -> ColorTemperature:
        """Get the color temperature tier."""
        composite = self.composite

        if composite >= 0.9:
            return ColorTemperature.RED
        elif composite >= 0.7:
            return ColorTemperature.ORANGE
        elif composite >= 0.55:
            return ColorTemperature.YELLOW
        elif composite >= 0.45:
            return ColorTemperature.GREEN
        elif composite >= 0.3:
            return ColorTemperature.CYAN
        elif composite >= 0.1:
            return ColorTemperature.BLUE
        else:
            return ColorTemperature.VIOLET

    def to_dict(self) -> Dict:
        """Export for SSE/API transmission."""
        return {
            "velocity": round(self.velocity, 3),
            "traction": round(self.traction, 3),
            "health": round(self.health, 3),
            "potential": round(self.potential, 3),
            "composite": round(self.composite, 3),
            "color": self.color,
            "tier": self.temperature_tier.name,
        }


@dataclass
class AgentProfile:
    """Agent performance profile affecting F_i velocity.

    Each agent type contributes differently to velocity:
    - opus: Strategic tasks (10x compute weight)
    - sonnet: Standard tasks (3x compute weight)
    - haiku: Quick tasks (1x compute weight)
    - gemma/qwen: Local inference (0.5x compute weight)
    """
    agent_id: str
    agent_type: str = "sonnet"  # opus, sonnet, haiku, gemma, qwen
    tasks_completed: int = 0
    tokens_used: int = 0
    v3_scores: List[float] = field(default_factory=list)

    COMPUTE_WEIGHTS = {
        "opus": 10.0,
        "sonnet": 3.0,
        "haiku": 1.0,
        "gemma": 0.5,
        "qwen": 0.5,
    }

    @property
    def compute_weight(self) -> float:
        """Get compute weight for this agent type."""
        return self.COMPUTE_WEIGHTS.get(self.agent_type, 1.0)

    @property
    def weighted_work(self) -> float:
        """Calculate weighted work output.

        work = (tokens / 1000) * compute_weight * avg_v3_score
        """
        avg_v3 = sum(self.v3_scores) / len(self.v3_scores) if self.v3_scores else 0.5
        return (self.tokens_used / 1000) * self.compute_weight * avg_v3

    def record_task(self, tokens: int, v3_score: float) -> None:
        """Record a completed task."""
        self.tasks_completed += 1
        self.tokens_used += tokens
        self.v3_scores.append(v3_score)
        # Keep last 100 scores for rolling average
        if len(self.v3_scores) > 100:
            self.v3_scores = self.v3_scores[-100:]


class FiRatingEngine:
    """Engine for calculating and tracking F_i ratings.

    Integrates with:
    - FAMDaemon (event source for velocity/traction)
    - Mesa model (simulation data)
    - SSE server (animation integration)
    """

    def __init__(self):
        self.foundups: Dict[str, FiRating] = {}
        self.founders: Dict[str, FounderTrackRecord] = {}
        self.agents: Dict[str, AgentProfile] = {}

    def get_or_create_rating(self, foundup_id: str) -> FiRating:
        """Get or create F_i rating for a FoundUp."""
        if foundup_id not in self.foundups:
            self.foundups[foundup_id] = FiRating()
        return self.foundups[foundup_id]

    def get_or_create_founder(self, founder_id: str) -> FounderTrackRecord:
        """Get or create founder track record."""
        if founder_id not in self.founders:
            self.founders[founder_id] = FounderTrackRecord()
        return self.founders[founder_id]

    def update_velocity(self, foundup_id: str, agent_work: float) -> None:
        """Update velocity based on agent work output.

        Velocity is normalized to 0-1 based on expected work per epoch.
        Expected: ~1000 weighted work units per epoch = 1.0 velocity
        """
        rating = self.get_or_create_rating(foundup_id)
        # Sigmoid normalization: asymptotic to 1.0
        normalized = 2 / (1 + math.exp(-agent_work / 500)) - 1
        rating.velocity = max(0.0, min(1.0, normalized))

    def update_traction(self, foundup_id: str,
                        subscriptions: int = 0,
                        engagements: int = 0,
                        cube_clicks: int = 0) -> None:
        """Update traction based on 012 engagement metrics.

        Traction formula:
        - subscriptions: 10 points each
        - engagements (likes, comments): 1 point each
        - cube_clicks: 0.5 points each (direct interaction)

        Normalized to 0-1 (1000 points = 1.0)
        """
        rating = self.get_or_create_rating(foundup_id)
        points = (subscriptions * 10) + engagements + (cube_clicks * 0.5)
        # Sigmoid normalization
        normalized = 2 / (1 + math.exp(-points / 500)) - 1
        rating.traction = max(0.0, min(1.0, normalized))

    def update_health(self, foundup_id: str,
                      build_progress: float = 0.0,
                      test_coverage: float = 0.0,
                      security_score: float = 0.0) -> None:
        """Update health based on operational metrics.

        Health = weighted average of:
        - build_progress (40%): How complete is the build?
        - test_coverage (35%): How well tested?
        - security_score (25%): WSP 71 compliance
        """
        rating = self.get_or_create_rating(foundup_id)
        rating.health = (
            build_progress * 0.40 +
            test_coverage * 0.35 +
            security_score * 0.25
        )

    def update_potential(self, foundup_id: str,
                         founder_id: str,
                         founder_rating_1_7: Optional[int] = None) -> None:
        """Update potential based on founder conviction.

        If founder_rating_1_7 is provided (012 direct input), use it.
        Otherwise, calculate from founder's track record.
        """
        rating = self.get_or_create_rating(foundup_id)

        if founder_rating_1_7 is not None:
            # 012 direct input: 1-7 scale to 0-1
            rating.potential = (founder_rating_1_7 - 1) / 6.0
        else:
            # Calculate from track record
            founder = self.get_or_create_founder(founder_id)
            rating.potential = founder.weighted_score

    def record_foundup_outcome(self, founder_id: str, final_rating: float) -> None:
        """Record FoundUp outcome to founder's track record.

        Called when a FoundUp reaches LAUNCH or is abandoned.
        Updates founder's tier_counts based on final rating.
        """
        founder = self.get_or_create_founder(founder_id)
        founder.total_foundups += 1

        # Determine tier from final rating
        if final_rating >= 0.9:
            founder.tier_counts["red"] += 1
        elif final_rating >= 0.7:
            founder.tier_counts["orange"] += 1
        elif final_rating >= 0.55:
            founder.tier_counts["yellow"] += 1
        elif final_rating >= 0.45:
            founder.tier_counts["green"] += 1
        elif final_rating >= 0.3:
            founder.tier_counts["cyan"] += 1
        elif final_rating >= 0.1:
            founder.tier_counts["blue"] += 1
        else:
            founder.tier_counts["violet"] += 1

    def get_animation_data(self, foundup_id: str) -> Dict:
        """Get rating data formatted for SSE/animation consumption.

        Returns dict with all fields needed by foundup-cube.js
        """
        rating = self.get_or_create_rating(foundup_id)
        return {
            "foundup_id": foundup_id,
            "rating": rating.to_dict(),
            "border_color": rating.color,
            "tier_name": rating.temperature_tier.name,
        }


# Singleton instance
_rating_engine: Optional[FiRatingEngine] = None


def get_rating_engine() -> FiRatingEngine:
    """Get singleton rating engine instance."""
    global _rating_engine
    if _rating_engine is None:
        _rating_engine = FiRatingEngine()
    return _rating_engine


def reset_rating_engine() -> None:
    """Reset rating engine (for testing)."""
    global _rating_engine
    _rating_engine = None


# Export color interpolation for direct use
__all__ = [
    "ColorTemperature",
    "COLOR_GRADIENT",
    "interpolate_color",
    "FounderTrackRecord",
    "FiRating",
    "AgentProfile",
    "FiRatingEngine",
    "get_rating_engine",
    "reset_rating_engine",
]
