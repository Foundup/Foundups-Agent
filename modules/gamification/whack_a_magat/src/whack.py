"""
Whack Gamification Foundation

Scope-limited, platform-agnostic implementation per WSP guidance.

Public API (exported via modules.gamification.__init__):
- apply_whack(moderator_id, target_id, duration_sec, now)
- get_profile(user_id)
- classify_behavior(duration_sec, repeats)

Constraints:
- No external dependencies; stdlib only
- In-memory repositories, persistence-agnostic
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from math import floor
from typing import Dict, List, Optional, Tuple
import sqlite3
import os


GAME_ID = "whack_a_magat"


class BehaviorTier(Enum):
    CAT_PLAY = "CAT_PLAY"
    BRUTAL_HAMMER = "BRUTAL_HAMMER"
    GENTLE_TOUCH = "GENTLE_TOUCH"
    OBSERVER = "OBSERVER"


@dataclass
class UserProfile:
    user_id: str
    username: str = "Unknown"  # Display name for leaderboard
    score: int = 0  # Total XP from frags
    rank: str = "Grunt"  # Quake-style rank
    level: int = 1
    frag_count: int = 0  # Total timeout/ban count


@dataclass
class TimeoutAction:
    moderator_id: str
    target_id: str
    duration_sec: int
    ts: datetime
    points: int


class ProfilesRepo:
    """Repository for profiles with optional SQLite persistence."""

    def __init__(self, persist: bool = True) -> None:
        self._profiles: Dict[str, UserProfile] = {}
        self.persist = persist
        # WSP-compliant: Store data within module directory
        module_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.db_path = os.path.join(module_dir, "data", "magadoom_scores.db") if persist else None
        
        if self.persist:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            self._init_db()
            self._load_from_db()

    def _init_db(self) -> None:
        """Initialize SQLite database tables."""
        if not self.persist:
            return
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                user_id TEXT PRIMARY KEY,
                username TEXT DEFAULT 'Unknown',
                score INTEGER DEFAULT 0,
                rank TEXT DEFAULT 'Grunt',
                level INTEGER DEFAULT 1,
                frag_count INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def _load_from_db(self) -> None:
        """Load profiles from database into memory."""
        if not self.persist:
            return
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if new columns exist and add them if not
        cursor.execute("PRAGMA table_info(profiles)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'frag_count' not in columns:
            cursor.execute("ALTER TABLE profiles ADD COLUMN frag_count INTEGER DEFAULT 0")
            conn.commit()
        if 'username' not in columns:
            cursor.execute("ALTER TABLE profiles ADD COLUMN username TEXT DEFAULT 'Unknown'")
            conn.commit()
        
        cursor.execute("SELECT user_id, score, rank, level, frag_count, username FROM profiles")
        for row in cursor.fetchall():
            self._profiles[row[0]] = UserProfile(
                user_id=row[0],
                score=row[1],
                rank=row[2],
                level=row[3],
                frag_count=row[4] if len(row) > 4 else 0,
                username=row[5] if len(row) > 5 else "Unknown"
            )
        conn.close()

    def get_or_create(self, user_id: str, username: str = "Unknown") -> UserProfile:
        profile = self._profiles.get(user_id)
        if profile is None:
            profile = UserProfile(user_id=user_id, username=username)
            self._profiles[user_id] = profile
            if self.persist:
                self._save_to_db(profile)
        elif profile.username == "Unknown" and username != "Unknown":
            # Update username if we have a better one
            profile.username = username
            if self.persist:
                self._save_to_db(profile)
        return profile

    def save(self, profile: UserProfile) -> None:
        self._profiles[profile.user_id] = profile
        if self.persist:
            self._save_to_db(profile)

    def _save_to_db(self, profile: UserProfile) -> None:
        """Save profile to database."""
        if not self.persist:
            return
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO profiles (user_id, username, score, rank, level, frag_count, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (profile.user_id, profile.username, profile.score, profile.rank, profile.level, profile.frag_count))
        conn.commit()
        conn.close()

    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get top players by score."""
        sorted_profiles = sorted(
            self._profiles.values(),
            key=lambda p: p.score,
            reverse=True
        )[:limit]
        
        return [
            {
                'position': i + 1,
                'user_id': p.user_id,
                'username': p.username,
                'score': p.score,
                'rank': p.rank,
                'level': p.level,
                'frag_count': p.frag_count
            }
            for i, p in enumerate(sorted_profiles)
        ]

    def get_user_position(self, user_id: str) -> Tuple[int, int]:
        """Get user's position and total player count."""
        sorted_profiles = sorted(
            self._profiles.values(),
            key=lambda p: p.score,
            reverse=True
        )
        
        total_count = len(sorted_profiles)
        for i, profile in enumerate(sorted_profiles):
            if profile.user_id == user_id:
                return i + 1, total_count
        
        return 0, total_count

    # Testing utility
    def _reset(self) -> None:
        self._profiles.clear()
        if self.persist and os.path.exists(self.db_path):
            os.remove(self.db_path)


class ActionsRepo:
    """In-memory repository for timeout actions (replaceable later)."""

    def __init__(self) -> None:
        self._actions: List[TimeoutAction] = []

    def add(self, action: TimeoutAction) -> None:
        self._actions.append(action)

    def list_recent_by_moderator_and_target(
        self, moderator_id: str, target_id: str, within_hours: int, now: Optional[datetime] = None
    ) -> List[TimeoutAction]:
        reference = now or datetime.utcnow()
        cutoff = reference - timedelta(hours=within_hours)
        return [
            a
            for a in self._actions
            if a.moderator_id == moderator_id and a.target_id == target_id and a.ts >= cutoff
        ]

    def list_recent_by_moderator(
        self, moderator_id: str, within_hours: int, now: Optional[datetime] = None
    ) -> List[TimeoutAction]:
        reference = now or datetime.utcnow()
        cutoff = reference - timedelta(hours=within_hours)
        return [a for a in self._actions if a.moderator_id == moderator_id and a.ts >= cutoff]

    # Testing utility
    def _reset(self) -> None:
        self._actions.clear()


# Module-level singletons for simple usage (with persistence by default)
_profiles_repo = ProfilesRepo(persist=True)
_actions_repo = ActionsRepo()


def _update_rank_and_level(profile: UserProfile) -> None:
    """Update rank and level from score - MAGADOOM style."""
    score = profile.score
    
    # Simple level calculation (100 XP per level)
    profile.level = 1 + (score // 100)
    
    # MAGADOOM epic ranks - MAGA troll fragging themed
    if score < 100:
        profile.rank = "COVFEFE CADET"  # Just learning to frag MAGAts
    elif score < 300:
        profile.rank = "QANON QUASHER"  # Starting to silence the conspiracy nuts
    elif score < 600:
        profile.rank = "MAGA MAULER"  # Tearing through red hats
    elif score < 1000:
        profile.rank = "TROLL TERMINATOR"  # No mercy for trolls
    elif score < 1500:
        profile.rank = "REDHAT RIPPER"  # Shredding the MAGA brigade
    elif score < 2500:
        profile.rank = "COUP CRUSHER"  # Stomping insurrectionists
    elif score < 5000:
        profile.rank = "PATRIOT PULVERIZER"  # Demolishing fake patriots
    elif score < 10000:
        profile.rank = "FASCIST FRAGGER"  # Ultimate anti-fascist warrior
    elif score < 20000:
        profile.rank = "ORANGE OBLITERATOR"  # The ultimate Trump troll destroyer
    elif score < 50000:
        profile.rank = "MAGA DOOMSLAYER"  # Rip and tear through the cult
    else:
        profile.rank = "DEMOCRACY DEFENDER"  # Eternal guardian against tyranny


def get_profile(user_id: str, username: str = "Unknown") -> UserProfile:
    """Retrieve (or create) the user profile for the given ID."""
    return _profiles_repo.get_or_create(user_id, username)


def compute_points(duration_sec: int, repeat_on_same_target: int) -> int:
    """Compute base points with diminishing returns for repeats on same target.

    Diminishing factors (within 24h):
    - 0 repeats → 100%
    - 1 repeat  → 60%
    - 2 repeats → 30%
    - 3+ repeats → 10%
    """
    # Base points for YouTube's exact timeout durations
    base = 0
    if duration_sec == 10:
        base = 1  # 10 seconds: 1 point (minimal, but not zero)
    elif duration_sec < 10:
        base = 0  # Less than 10 seconds: Anti-farming protection
    elif duration_sec == 60:
        base = 1  # 1 minute: 1 point
    elif duration_sec == 300:
        base = 5  # 5 minutes: 5 points
    elif duration_sec == 600:
        base = 10  # 10 minutes: 10 points  
    elif duration_sec == 1800:
        base = 30  # 30 minutes: 30 points
    elif duration_sec >= 86400:
        base = 144  # 24 hours (permanent): 144 points (1 day = 144 * 10min blocks)
    else:
        # Fallback for any custom durations
        base = max(1, duration_sec // 60)  # 1 point per minute

    # Diminishing returns factor
    if repeat_on_same_target <= 0:
        factor = 1.0
    elif repeat_on_same_target == 1:
        factor = 0.6
    elif repeat_on_same_target == 2:
        factor = 0.3
    else:
        factor = 0.1

    return int(base * factor)


def classify_behavior(duration_sec: int, repeats: int) -> BehaviorTier:
    """Classify moderator behavior heuristically (v0).

    - CAT_PLAY: multiple short (≤60s) timeouts with repeats ≥ 2 in 24h
    - BRUTAL_HAMMER: duration ≥ 12h or exactly 24h
    - GENTLE_TOUCH: 1–15 min with no repeats
    - OBSERVER: no actions in last 7 days (not inferable here; treated as fallback if duration==0)
    """
    if duration_sec <= 60 and repeats >= 2:
        return BehaviorTier.CAT_PLAY

    if duration_sec >= 12 * 60 * 60 or duration_sec == 24 * 60 * 60:
        return BehaviorTier.BRUTAL_HAMMER

    if 60 <= duration_sec <= 15 * 60 and repeats == 0:
        return BehaviorTier.GENTLE_TOUCH

    if duration_sec <= 0:
        return BehaviorTier.OBSERVER

    # Default: choose gentleness for short actions without strong indicators
    return BehaviorTier.GENTLE_TOUCH if duration_sec <= 15 * 60 else BehaviorTier.CAT_PLAY


def _apply_daily_cap(current_points: int, moderator_id: str, now: datetime) -> int:
    """NO DAILY CAP - Stream owner (Move2Japan) requested unlimited whacks!"""
    # Daily cap removed per user request - mods can whack freely!
    # This prevents the "[Daily cap reached]" message from appearing
    return current_points


def apply_whack(moderator_id: str, target_id: str, duration_sec: int, now: datetime, moderator_name: str = "Unknown") -> TimeoutAction:
    """Apply a timeout action as a 'whack' and award points under anti-abuse rules.

    Steps:
    a) count repeats on same target in past 24h
    b) points = compute_points(duration_sec, repeats)
    c) persist TimeoutAction
    d) increment moderator's score; update rank/level (with daily cap)
    e) return saved TimeoutAction
    """
    recent_same_target = _actions_repo.list_recent_by_moderator_and_target(
        moderator_id, target_id, within_hours=24, now=now
    )
    repeats = len(recent_same_target)

    base_points = compute_points(duration_sec, repeats)
    awarded_points = _apply_daily_cap(base_points, moderator_id, now)
    
    # Get profile and increment frag count
    profile = _profiles_repo.get_or_create(moderator_id, moderator_name)

    action = TimeoutAction(
        moderator_id=moderator_id,
        target_id=target_id,
        duration_sec=duration_sec,
        ts=now,
        points=awarded_points,
    )
    _actions_repo.add(action)

    # Update moderator profile
    profile.score += awarded_points
    profile.frag_count += 1  # Increment frag count
    _update_rank_and_level(profile)
    _profiles_repo.save(profile)

    return action


def get_leaderboard(limit: int = 10) -> List[Dict]:
    """Get the top players by score.
    
    Returns:
        List of player dicts with position, user_id, score, rank, level
    """
    return _profiles_repo.get_leaderboard(limit)


def get_user_position(user_id: str) -> Tuple[int, int]:
    """Get a user's leaderboard position and total player count.
    
    Returns:
        Tuple of (position, total_players)
    """
    return _profiles_repo.get_user_position(user_id)


# Testing helpers (not exported via public API)
def _reset_state_for_tests() -> None:
    _profiles_repo._reset()
    _actions_repo._reset()