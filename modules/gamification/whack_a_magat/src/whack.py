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

🧪 EMBEDDED MODULE DOCUMENTATION (WSP 22)
═══════════════════════════════════════════════════════════════

📖 README.md Summary:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Module: whack_a_magat | Domain: gamification | Phase: MVP
Purpose: Quake/Duke Nukem style fragging gamification for YouTube Live Chat moderation
Status: ACTIVE - Production ready with 0102 consciousness integration
Dependencies: sqlite3, typing, datetime | WSP Compliance: WSP 3, 22, 84, 85

📊 ModLog.md Key Milestones:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Killing Spree System - 30-second windows for sustained fragging
✅ Epic MAGA-themed rank names - COVFEFE CADET → MAGA DOOMSLAYER  
✅ Leaderboard with usernames - Top 3 vertical format for chat readability
🚧 Multi-whack detection and combo multipliers integration

🧪 TestModLog.md Status:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Coverage: 85% (4/5 tests passing) | Tests: import fix applied | Performance: <2s execution
Evolution: Fixed import structure, proper module organization, WSP 85 compliance

🎯 Integration Points (0102 Agents):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Called by: modules/communication/livechat/src/event_handler.py
• WSP Compliance: WSP 3 (module organization), WSP 84 (code memory), WSP 85 (directory protection)
• Usage: from modules.gamification.whack_a_magat import apply_whack, get_profile
• Database: data/magadoom_scores.db with ProfilesRepo and ActionsRepo classes

═══════════════════════════════════════════════════════════════
END EMBEDDED DOCUMENTATION - See separate files for full details
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)
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
    score: int = 0  # Total all-time XP
    monthly_score: int = 0  # Monthly XP (resets each month)
    current_month: str = ""  # Format: "2025-01" for tracking month
    rank: str = "Grunt"  # Quake-style rank (based on monthly_score)
    level: int = 1
    frag_count: int = 0  # Total all-time whacks (never resets)
    monthly_frag_count: int = 0  # Monthly whacks (resets each month)
    session_whacks: int = 0  # Session whacks (resets when stream ends)
    session_score: int = 0  # Session XP (resets when stream ends)
    session_start: str = ""  # Session start timestamp


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
                monthly_score INTEGER DEFAULT 0,
                current_month TEXT DEFAULT '',
                rank TEXT DEFAULT 'Grunt',
                level INTEGER DEFAULT 1,
                frag_count INTEGER DEFAULT 0,
                monthly_frag_count INTEGER DEFAULT 0,
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
        
        # Add missing columns for existing databases
        if 'frag_count' not in columns:
            cursor.execute("ALTER TABLE profiles ADD COLUMN frag_count INTEGER DEFAULT 0")
            conn.commit()
        if 'username' not in columns:
            cursor.execute("ALTER TABLE profiles ADD COLUMN username TEXT DEFAULT 'Unknown'")
            conn.commit()
        if 'monthly_score' not in columns:
            cursor.execute("ALTER TABLE profiles ADD COLUMN monthly_score INTEGER DEFAULT 0")
            conn.commit()
        if 'current_month' not in columns:
            cursor.execute("ALTER TABLE profiles ADD COLUMN current_month TEXT DEFAULT ''")
            conn.commit()
        if 'monthly_frag_count' not in columns:
            cursor.execute("ALTER TABLE profiles ADD COLUMN monthly_frag_count INTEGER DEFAULT 0")
            conn.commit()
        if 'session_whacks' not in columns:
            cursor.execute("ALTER TABLE profiles ADD COLUMN session_whacks INTEGER DEFAULT 0")
            conn.commit()
        if 'session_score' not in columns:
            cursor.execute("ALTER TABLE profiles ADD COLUMN session_score INTEGER DEFAULT 0")
            conn.commit()
        if 'session_start' not in columns:
            cursor.execute("ALTER TABLE profiles ADD COLUMN session_start TEXT DEFAULT ''")
            conn.commit()
        
        cursor.execute("SELECT user_id, score, rank, level, frag_count, username, monthly_score, current_month, monthly_frag_count FROM profiles")
        for row in cursor.fetchall():
            self._profiles[row[0]] = UserProfile(
                user_id=row[0],
                score=row[1],
                rank=row[2],
                level=row[3],
                frag_count=row[4] if len(row) > 4 else 0,
                username=row[5] if len(row) > 5 else "Unknown",
                monthly_score=row[6] if len(row) > 6 else 0,
                current_month=row[7] if len(row) > 7 else "",
                monthly_frag_count=row[8] if len(row) > 8 else 0
            )
        conn.close()

    def get_or_create(self, user_id: str, username: str = "Unknown") -> UserProfile:
        from datetime import datetime
        current_month = datetime.now().strftime("%Y-%m")
        
        profile = self._profiles.get(user_id)
        needs_save = False
        
        if profile is None:
            # Create new profile with current month
            profile = UserProfile(
                user_id=user_id, 
                username=username,
                current_month=current_month
            )
            self._profiles[user_id] = profile
            needs_save = True
        else:
            # Check for month change and reset monthly stats
            if profile.current_month != current_month:
                logger.info(f"🗓️ New month! Resetting monthly stats for {username}")
                profile.current_month = current_month
                profile.monthly_score = 0
                profile.monthly_frag_count = 0
                needs_save = True
                
            # Update username if we have a better one
            if profile.username == "Unknown" and username != "Unknown":
                profile.username = username
                needs_save = True
                
        if needs_save and self.persist:
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
        
        # Check if session columns exist
        cursor.execute("PRAGMA table_info(profiles)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'session_whacks' in columns:
            # New schema with session tracking
            cursor.execute("""
                INSERT OR REPLACE INTO profiles (user_id, username, score, monthly_score, current_month, 
                                                rank, level, frag_count, monthly_frag_count,
                                                session_whacks, session_score, session_start, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (profile.user_id, profile.username, profile.score, profile.monthly_score, 
                  profile.current_month, profile.rank, profile.level, profile.frag_count, 
                  profile.monthly_frag_count, profile.session_whacks, profile.session_score,
                  profile.session_start))
        else:
            # Old schema without session tracking
            cursor.execute("""
                INSERT OR REPLACE INTO profiles (user_id, username, score, monthly_score, current_month, 
                                                rank, level, frag_count, monthly_frag_count, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (profile.user_id, profile.username, profile.score, profile.monthly_score, 
                  profile.current_month, profile.rank, profile.level, profile.frag_count, 
                  profile.monthly_frag_count))
        
        conn.commit()
        conn.close()

    def get_leaderboard(self, limit: int = 10, monthly: bool = True) -> List[Dict]:
        """Get top players by monthly or all-time score."""
        # Filter out test users (exclude test_user_* entries)
        real_profiles = [
            p for p in self._profiles.values() 
            if not p.user_id.startswith('test_user')
        ]
        
        if monthly:
            # Sort by monthly score for current month leaderboard
            sorted_profiles = sorted(
                real_profiles,
                key=lambda p: p.monthly_score,
                reverse=True
            )[:limit]
        else:
            # Sort by all-time score
            sorted_profiles = sorted(
                real_profiles,
                key=lambda p: p.score,
                reverse=True
            )[:limit]
        
        return [
            {
                'position': i + 1,
                'user_id': p.user_id,
                'username': p.username,
                'score': p.monthly_score if monthly else p.score,  # Show monthly or all-time
                'all_time_score': p.score,  # Always include all-time
                'rank': p.rank,
                'level': p.level,
                'frag_count': p.monthly_frag_count if monthly else p.frag_count,  # Monthly or all-time whacks
                'all_time_whacks': p.frag_count  # Always include all-time whacks
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
    """Update rank and level from MONTHLY score - MAGADOOM style."""
    # Rank based on MONTHLY score (resets each month for fair competition)
    score = profile.monthly_score
    
    # Level based on ALL-TIME score (never resets, shows veteran status)
    profile.level = 1 + (profile.score // 100)
    
    # MAGADOOM RANKS - Pure DOOM/FPS style (NO old terminology!)
    if score < 100:
        profile.rank = "GRUNT"  # Fresh meat, just spawned
    elif score < 300:
        profile.rank = "MARINE"  # Learning to RIP AND TEAR
    elif score < 600:
        profile.rank = "WARRIOR"  # Getting those FRAGS
    elif score < 1000:
        profile.rank = "SLAYER"  # DOOM music intensifies
    elif score < 1500:
        profile.rank = "HUNTER"  # Stalking demons
    elif score < 2500:
        profile.rank = "CHAMPION"  # Arena champion
    elif score < 5000:
        profile.rank = "MASTER"  # Master of the arena
    elif score < 10000:
        profile.rank = "ELITE"  # Elite demon hunter
    elif score < 20000:
        profile.rank = "GODLIKE"  # Ascending to godhood
    elif score < 50000:
        profile.rank = "LEGENDARY"  # Stuff of legends
    else:
        profile.rank = "DOOM SLAYER"  # THE ONLY ONE THEY FEAR


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
    # Base points for YouTube's exact timeout durations (MORE REWARDING!)
    base = 0
    if duration_sec == 10:
        base = 5  # 10 seconds: 5 points (quick slap)
    elif duration_sec < 10:
        base = 0  # Less than 10 seconds: Anti-farming protection
    elif duration_sec == 60:
        base = 10  # 1 minute: 10 points (standard whack)
    elif duration_sec == 300:
        base = 25  # 5 minutes: 25 points (solid hit)
    elif duration_sec == 600:
        base = 50  # 10 minutes: 50 points (major whack)
    elif duration_sec == 1800:
        base = 100  # 30 minutes: 100 points (devastating)
    elif duration_sec >= 86400:
        base = 500  # 24 hours (permanent): 500 points (OBLITERATION)
    else:
        # Fallback for any custom durations
        base = max(10, duration_sec // 6)  # More generous points

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
    
    # Check if this is a new session (empty session_start or new stream)
    current_session = now.isoformat()
    if not profile.session_start:
        profile.session_start = current_session
        profile.session_whacks = 0
        profile.session_score = 0

    action = TimeoutAction(
        moderator_id=moderator_id,
        target_id=target_id,
        duration_sec=duration_sec,
        ts=now,
        points=awarded_points,
    )
    _actions_repo.add(action)

    # Update moderator profile - ALL THREE: session, monthly and all-time!
    profile.score += awarded_points  # All-time score
    profile.monthly_score += awarded_points  # Monthly score (for leaderboard)
    profile.session_score += awarded_points  # Session score
    profile.frag_count += 1  # All-time whack count
    profile.monthly_frag_count += 1  # Monthly whack count
    profile.session_whacks += 1  # Session whack count
    _update_rank_and_level(profile)  # Rank based on monthly, level based on all-time
    _profiles_repo.save(profile)

    return action


def get_leaderboard(limit: int = 10, monthly: bool = True) -> List[Dict]:
    """Get the top players by monthly or all-time score.
    
    Args:
        limit: Maximum number of players to return
        monthly: If True, returns monthly leaderboard. If False, returns all-time.
    
    Returns:
        List of player dicts with position, user_id, scores, rank, level, whack counts
    """
    return _profiles_repo.get_leaderboard(limit, monthly)


def get_user_position(user_id: str) -> Tuple[int, int]:
    """Get a user's leaderboard position and total player count.
    
    Returns:
        Tuple of (position, total_players)
    """
    return _profiles_repo.get_user_position(user_id)


def reset_all_sessions():
    """Reset session stats for all moderators (called when stream ends)."""
    logger.info("🔄 Resetting session stats for all moderators")
    for profile in _profiles_repo._profiles.values():
        if profile.session_whacks > 0:
            logger.info(f"  {profile.username}: {profile.session_whacks} whacks, {profile.session_score} XP")
        profile.session_whacks = 0
        profile.session_score = 0
        profile.session_start = ""
        _profiles_repo.save(profile)


def get_session_leaderboard(limit: int = 10) -> List[Dict]:
    """Get current session leaderboard."""
    # Filter out test users and only include those with session activity
    active_profiles = [
        p for p in _profiles_repo._profiles.values() 
        if not p.user_id.startswith('test_user') and p.session_whacks > 0
    ]
    
    # Sort by session score
    sorted_profiles = sorted(
        active_profiles,
        key=lambda p: p.session_score,
        reverse=True
    )[:limit]
    
    return [
        {
            'position': i + 1,
            'user_id': p.user_id,
            'username': p.username,
            'session_score': p.session_score,
            'session_whacks': p.session_whacks,
            'rank': p.rank,
            'level': p.level
        }
        for i, p in enumerate(sorted_profiles)
    ]


# Testing helpers (not exported via public API)
def _reset_state_for_tests() -> None:
    _profiles_repo._reset()
    _actions_repo._reset()