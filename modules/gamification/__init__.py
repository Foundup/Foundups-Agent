"""Public API for gamification domain.

Expose per-game modules via namespaced imports to keep functional separation.
"""

from .whack_a_magat import (
    apply_whack,
    get_profile,
    classify_behavior,
    get_leaderboard,
    get_user_position,
    BehaviorTier,
    GAME_ID
)

__all__ = [
    "apply_whack",
    "get_profile",
    "classify_behavior",
    "get_leaderboard",
    "get_user_position",
    "BehaviorTier",
    "GAME_ID",
]


