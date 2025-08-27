"""
Whack-a-MAGA Gamification Module
WSP-Compliant: All gamification logic for timeout/ban tracking

This module contains:
- TimeoutManager: Duke Nukem/Quake announcer system
- TimeoutTracker: Deduplication and frag tracking
- Whack functions: Points and leveling system
"""

# Only export whack functions to avoid circular imports
# TimeoutManager and TimeoutTracker should be imported directly when needed
from modules.gamification.whack_a_magat.src.whack import (
    apply_whack,
    get_profile,
    classify_behavior,
    BehaviorTier
)

__all__ = [
    'apply_whack',
    'get_profile',
    'classify_behavior',
    'BehaviorTier'
]