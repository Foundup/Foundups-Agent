"""Whack-a-Magat game module public API."""

# Core whack functionality
from .src.whack import (
    apply_whack,
    get_profile,
    classify_behavior,
    get_leaderboard,
    get_user_position,
    BehaviorTier,
    GAME_ID
)

# Timeout tracking and announcing
from .src.timeout_tracker import TimeoutTracker
from .src.timeout_announcer import TimeoutManager as TimeoutAnnouncer

# Educational quiz system
from .src.quiz_engine import (
    QuizEngine,
    QuizQuestion,
    FScaleQuestion,
    QuizSession
)

# Historical facts provider
from .src.historical_facts import HistoricalFacts, get_random_fact, get_parallel, get_warning

# Game commands system - commented out due to circular dependencies
# from .src.game_commands import GameCommandSystem, CommandType, CommandContext

# RPG leveling system - commented out due to ChatRulesDB dependency  
# from .src.rpg_leveling_system import RPGCommands

__all__ = [
    # Core whack
    "apply_whack",
    "get_profile",
    "classify_behavior",
    "get_leaderboard",
    "get_user_position",
    "BehaviorTier",
    "GAME_ID",
    # Timeout system
    "TimeoutTracker",
    "TimeoutAnnouncer",
    # Quiz modules
    "QuizEngine",
    "QuizQuestion",
    "FScaleQuestion",
    "QuizSession",
    "HistoricalFacts",
    "get_random_fact",
    "get_parallel",
    "get_warning"
]


