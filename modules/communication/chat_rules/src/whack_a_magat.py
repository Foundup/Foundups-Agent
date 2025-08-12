#!/usr/bin/env python3
"""
WHACK-A-MAGAt Point System
Gamified moderation tracking with leaderboards and rewards
"""

import json
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class TimeoutDuration(Enum):
    """YouTube timeout durations with point values and anti-gaming rules"""
    # Format: (seconds, base_points, cooldown_minutes, severity_level, description)
    SEC_10 = (10, 5, 2, 1, "Quick warning")           # Minimal points, short cooldown
    SEC_60 = (60, 15, 5, 2, "Standard timeout")       # Low points, prevents spam
    MIN_5 = (300, 30, 15, 3, "Serious violation")     # Moderate points
    MIN_10 = (600, 50, 30, 4, "Major violation")      # Good points
    HOUR_1 = (3600, 100, 120, 5, "Severe violation")  # High points, 2hr cooldown
    HOUR_24 = (86400, 250, 1440, 6, "Ban hammer")     # Max points, 24hr cooldown
    
    def __init__(self, seconds, points, cooldown, severity, desc):
        self.seconds = seconds
        self.base_points = points
        self.cooldown_minutes = cooldown
        self.severity = severity
        self.description = desc

class ActionType(Enum):
    """Point-earning actions"""
    # Timeout actions now use dynamic points based on duration
    TIMEOUT_WARNING = 5         # 10 second timeout (anti-gaming: low points)
    TIMEOUT_STANDARD = 15       # 60 second timeout
    TIMEOUT_SERIOUS = 30        # 5 minute timeout
    TIMEOUT_MAJOR = 50          # 10 minute timeout  
    TIMEOUT_SEVERE = 100        # 1 hour timeout
    TIMEOUT_BAN = 250           # 24 hour timeout
    
    DETECT_SPAM = 25            # Identify spam
    HELP_MEMBER = 50            # Assist a paying member
    ELEVATE_CONSCIOUSNESS = 75  # Help someone reach higher consciousness
    CATCH_RAID = 200            # Detect and stop a raid
    GIFT_MEMBER = 150           # Gift someone a membership
    SUPER_CHAT = 0              # Variable based on amount
    REPORT_VIOLATION = 30       # Report TOS violation
    PERFECT_WEEK = 500          # No false positives for a week
    COMBO_WHACK = 150           # Multiple MAGAs in 60 seconds
    FALSE_POSITIVE = -100       # Penalty for bad timeout (reversed by owner/reported)
    
class WhackLevel(Enum):
    """Moderator levels based on points"""
    ROOKIE = (0, "🥉 Rookie Whacker")
    BRONZE = (100, "🥉 Bronze Defender")
    SILVER = (500, "🥈 Silver Guardian") 
    GOLD = (1000, "🥇 Gold Sentinel")
    PLATINUM = (2500, "💎 Platinum Protector")
    DIAMOND = (5000, "💠 Diamond Defender")
    MASTER = (10000, "🏆 Master of Consciousness")
    LEGEND = (25000, "🌟 Legendary Whacker")
    QUANTUM = (50000, "🌌 Quantum Consciousness Guardian")

@dataclass
class ModeratorProfile:
    """Track moderator statistics and points"""
    user_id: str
    display_name: str
    total_points: int = 0
    whacks_count: int = 0
    maga_timeouts: int = 0
    spam_caught: int = 0
    members_helped: int = 0
    raids_stopped: int = 0
    gifts_given: int = 0
    false_positives: int = 0
    streak_days: int = 0
    last_action: Optional[datetime] = None
    achievements: List[str] = field(default_factory=list)
    combo_multiplier: float = 1.0
    level: WhackLevel = WhackLevel.ROOKIE
    
    # Anti-gaming tracking
    timeout_history: Dict[str, List[datetime]] = field(default_factory=dict)  # user_id -> [timeout times]
    last_timeout_per_user: Dict[str, datetime] = field(default_factory=dict)  # user_id -> last timeout
    timeout_cooldowns: Dict[str, datetime] = field(default_factory=dict)  # severity -> cooldown expiry
    daily_timeout_count: int = 0
    daily_reset_time: Optional[datetime] = None
    
    # Detailed timeout stats
    timeouts_10s: int = 0
    timeouts_60s: int = 0
    timeouts_5m: int = 0
    timeouts_10m: int = 0
    timeouts_1h: int = 0
    timeouts_24h: int = 0
    
    def add_points(self, points: int, action: ActionType, details: str = "") -> Tuple[int, List[str]]:
        """Add points and check for level ups and achievements"""
        actual_points = int(points * self.combo_multiplier)
        self.total_points += actual_points
        self.last_action = datetime.now()
        
        # Track specific actions
        if action == ActionType.WHACK_MAGA:
            self.maga_timeouts += 1
            self.whacks_count += 1
        elif action == ActionType.DETECT_SPAM:
            self.spam_caught += 1
        elif action == ActionType.HELP_MEMBER:
            self.members_helped += 1
        elif action == ActionType.CATCH_RAID:
            self.raids_stopped += 1
        elif action == ActionType.GIFT_MEMBER:
            self.gifts_given += 1
            
        # Check for achievements
        new_achievements = self._check_achievements()
        
        # Check for level up
        old_level = self.level
        self._update_level()
        
        if self.level != old_level:
            new_achievements.append(f"LEVEL UP: {self.level.value[1]}")
            
        logger.info(f"{self.display_name} earned {actual_points} points for {action.name}")
        
        return actual_points, new_achievements
    
    def _update_level(self):
        """Update moderator level based on points"""
        for level in reversed(WhackLevel):
            if self.total_points >= level.value[0]:
                self.level = level
                break
    
    def _check_achievements(self) -> List[str]:
        """Check for new achievements"""
        new_achievements = []
        
        # First MAGA whack
        if self.maga_timeouts == 1 and "First Blood" not in self.achievements:
            self.achievements.append("First Blood")
            new_achievements.append("🎯 First Blood - First MAGA Whacked!")
            self.total_points += 50
            
        # 10 MAGA streak
        if self.maga_timeouts == 10 and "Decimator" not in self.achievements:
            self.achievements.append("Decimator")
            new_achievements.append("💥 Decimator - 10 MAGAs Whacked!")
            self.total_points += 100
            
        # 50 MAGA milestone
        if self.maga_timeouts == 50 and "Consciousness Defender" not in self.achievements:
            self.achievements.append("Consciousness Defender")
            new_achievements.append("🛡️ Consciousness Defender - 50 MAGAs Defeated!")
            self.total_points += 500
            
        # 100 MAGA milestone
        if self.maga_timeouts == 100 and "Centurion" not in self.achievements:
            self.achievements.append("Centurion") 
            new_achievements.append("⚔️ Centurion - 100 MAGAs Vanquished!")
            self.total_points += 1000
            
        # Raid stopper
        if self.raids_stopped >= 5 and "Raid Boss" not in self.achievements:
            self.achievements.append("Raid Boss")
            new_achievements.append("🚫 Raid Boss - Stopped 5 Raids!")
            self.total_points += 750
            
        # Generous gifter
        if self.gifts_given >= 10 and "Philanthropist" not in self.achievements:
            self.achievements.append("Philanthropist")
            new_achievements.append("🎁 Philanthropist - Gifted 10 Memberships!")
            self.total_points += 1500
            
        return new_achievements

class WhackAMAGAtSystem:
    """Main point tracking and leaderboard system"""
    
    def __init__(self, config_path: str = None):
        import os
        self.moderators: Dict[str, ModeratorProfile] = {}
        
        # WSP-compliant data location
        if config_path is None:
            module_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_dir = os.path.join(module_dir, "data")
            os.makedirs(data_dir, exist_ok=True)
            self.config_path = os.path.join(data_dir, "whack_config.json")
        else:
            self.config_path = config_path
            
        self.combo_window = 60  # seconds for combo multiplier
        self.last_whack_time: Dict[str, datetime] = {}
        self.load_data()
        
    def load_data(self):
        """Load moderator data from storage"""
        try:
            with open(self.config_path, 'r') as f:
                data = json.load(f)
                for user_id, mod_data in data.get('moderators', {}).items():
                    self.moderators[user_id] = ModeratorProfile(**mod_data)
        except FileNotFoundError:
            logger.info("No existing data found, starting fresh")
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
    
    def save_data(self):
        """Save moderator data to storage"""
        try:
            data = {
                'moderators': {
                    uid: {
                        'user_id': mod.user_id,
                        'display_name': mod.display_name,
                        'total_points': mod.total_points,
                        'whacks_count': mod.whacks_count,
                        'maga_timeouts': mod.maga_timeouts,
                        'spam_caught': mod.spam_caught,
                        'members_helped': mod.members_helped,
                        'raids_stopped': mod.raids_stopped,
                        'gifts_given': mod.gifts_given,
                        'false_positives': mod.false_positives,
                        'streak_days': mod.streak_days,
                        'achievements': mod.achievements,
                        'level': mod.level.name if hasattr(mod.level, 'name') else str(mod.level)
                    }
                    for uid, mod in self.moderators.items()
                }
            }
            with open(self.config_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save data: {e}")
    
    def record_timeout(self, mod_id: str, mod_name: str, target_id: str, target_name: str, duration_seconds: int, reason: str) -> str:
        """
        Record a timeout with anti-gaming mechanics
        
        Args:
            mod_id: Moderator ID
            mod_name: Moderator display name
            target_id: Target user ID being timed out
            target_name: Target display name
            duration_seconds: Timeout duration in seconds
            reason: Reason for timeout
            
        Returns:
            Response message with points earned
        """
        mod = self._get_or_create_moderator(mod_id, mod_name)
        now = datetime.now()
        
        # Reset daily count if needed
        if mod.daily_reset_time is None or (now - mod.daily_reset_time).days >= 1:
            mod.daily_timeout_count = 0
            mod.daily_reset_time = now
        
        # Find matching timeout duration
        timeout_tier = None
        for tier in TimeoutDuration:
            if tier.seconds == duration_seconds:
                timeout_tier = tier
                break
        
        if not timeout_tier:
            # Unknown duration, use closest match
            if duration_seconds <= 10:
                timeout_tier = TimeoutDuration.SEC_10
            elif duration_seconds <= 60:
                timeout_tier = TimeoutDuration.SEC_60
            elif duration_seconds <= 300:
                timeout_tier = TimeoutDuration.MIN_5
            elif duration_seconds <= 600:
                timeout_tier = TimeoutDuration.MIN_10
            elif duration_seconds <= 3600:
                timeout_tier = TimeoutDuration.HOUR_1
            else:
                timeout_tier = TimeoutDuration.HOUR_24
        
        # Check for gaming attempts
        gaming_penalty = 0
        gaming_reasons = []
        
        # 1. Check if same user was timed out recently (prevent farming same user)
        if target_id in mod.last_timeout_per_user:
            time_since_last = (now - mod.last_timeout_per_user[target_id]).total_seconds() / 60
            if time_since_last < 30:  # Within 30 minutes
                gaming_penalty += 0.5
                gaming_reasons.append(f"Same user timeout within {int(time_since_last)}m")
        
        # 2. Check severity cooldown (can't use same severity too often)
        severity_key = str(timeout_tier.severity)
        if severity_key in mod.timeout_cooldowns:
            if now < mod.timeout_cooldowns[severity_key]:
                remaining = int((mod.timeout_cooldowns[severity_key] - now).total_seconds() / 60)
                gaming_penalty += 0.7
                gaming_reasons.append(f"Severity {timeout_tier.severity} on cooldown ({remaining}m left)")
        
        # 3. Check for 10-second spam (more than 5 in 10 minutes)
        if timeout_tier == TimeoutDuration.SEC_10:
            recent_10s = [t for t in mod.timeout_history.get('10s', []) 
                         if (now - t).total_seconds() < 600]
            if len(recent_10s) >= 5:
                gaming_penalty += 0.8
                gaming_reasons.append(f"Too many 10s timeouts ({len(recent_10s)} in 10m)")
        
        # 4. Daily limit check (soft cap at 50 timeouts/day)
        if mod.daily_timeout_count >= 50:
            gaming_penalty += 0.9
            gaming_reasons.append(f"Daily limit reached ({mod.daily_timeout_count} timeouts)")
        
        # Calculate points with penalties
        base_points = timeout_tier.base_points
        
        # Bonus for higher severity (encourages proper moderation)
        severity_bonus = 1.0 + (timeout_tier.severity - 1) * 0.1
        
        # Apply gaming penalty
        final_multiplier = max(0.1, severity_bonus - gaming_penalty)
        
        # Apply combo multiplier if not gaming
        if gaming_penalty < 0.5:
            # Check for combo
            if mod_id in self.last_whack_time:
                time_diff = (now - self.last_whack_time[mod_id]).total_seconds()
                if time_diff <= self.combo_window:
                    mod.combo_multiplier = min(mod.combo_multiplier + 0.2, 2.0)
                else:
                    mod.combo_multiplier = 1.0
            else:
                mod.combo_multiplier = 1.0
        else:
            mod.combo_multiplier = 1.0  # No combo when gaming detected
        
        final_points = int(base_points * final_multiplier * mod.combo_multiplier)
        
        # Update tracking
        mod.last_timeout_per_user[target_id] = now
        mod.timeout_cooldowns[severity_key] = now + timedelta(minutes=timeout_tier.cooldown_minutes)
        mod.daily_timeout_count += 1
        self.last_whack_time[mod_id] = now
        
        # Track timeout history
        timeout_key = f"{duration_seconds}s"
        if timeout_key not in mod.timeout_history:
            mod.timeout_history[timeout_key] = []
        mod.timeout_history[timeout_key].append(now)
        
        # Update specific timeout counters
        if timeout_tier == TimeoutDuration.SEC_10:
            mod.timeouts_10s += 1
        elif timeout_tier == TimeoutDuration.SEC_60:
            mod.timeouts_60s += 1
        elif timeout_tier == TimeoutDuration.MIN_5:
            mod.timeouts_5m += 1
        elif timeout_tier == TimeoutDuration.MIN_10:
            mod.timeouts_10m += 1
        elif timeout_tier == TimeoutDuration.HOUR_1:
            mod.timeouts_1h += 1
        elif timeout_tier == TimeoutDuration.HOUR_24:
            mod.timeouts_24h += 1
        
        mod.whacks_count += 1
        mod.total_points += final_points
        mod.last_action = now
        
        # Check achievements
        new_achievements = mod._check_achievements()
        
        # Update level
        old_level = mod.level
        mod._update_level()
        if mod.level != old_level:
            new_achievements.append(f"LEVEL UP: {mod.level.value[1]}")
        
        # Build response
        response = f"🔨 TIMEOUT! {mod_name} → {target_name} ({timeout_tier.description})"
        response += f"\n⏱️ Duration: {duration_seconds}s | Points: {final_points}"
        
        if gaming_penalty > 0:
            response += f"\n⚠️ Reduced points: {', '.join(gaming_reasons)}"
        
        if mod.combo_multiplier > 1:
            response += f"\n🔥 COMBO x{mod.combo_multiplier:.1f}!"
        
        response += f"\n📊 Total: {mod.total_points} | Level: {mod.level.value[1]}"
        
        for achievement in new_achievements:
            response += f"\n🏆 {achievement}"
        
        self.save_data()
        return response
    
    def record_whack(self, mod_id: str, mod_name: str, target: str, reason: str) -> str:
        """Record a MAGA whack and calculate points"""
        mod = self._get_or_create_moderator(mod_id, mod_name)
        
        # Check for combo multiplier
        now = datetime.now()
        if mod_id in self.last_whack_time:
            time_diff = (now - self.last_whack_time[mod_id]).total_seconds()
            if time_diff <= self.combo_window:
                mod.combo_multiplier = min(mod.combo_multiplier + 0.5, 3.0)
            else:
                mod.combo_multiplier = 1.0
        else:
            mod.combo_multiplier = 1.0
            
        self.last_whack_time[mod_id] = now
        
        # Award points
        base_points = ActionType.WHACK_MAGA.value
        points, achievements = mod.add_points(base_points, ActionType.WHACK_MAGA, f"Whacked {target}: {reason}")
        
        # Build response
        response = f"🔨 WHACK! {mod_name} scored {points} points!"
        if mod.combo_multiplier > 1:
            response += f" (x{mod.combo_multiplier:.1f} COMBO!)"
        
        response += f"\n📊 Total: {mod.total_points} | Level: {mod.level.value[1]}"
        
        for achievement in achievements:
            response += f"\n🏆 {achievement}"
            
        self.save_data()
        return response
    
    def record_action(self, mod_id: str, mod_name: str, action: ActionType, details: str = "", amount: float = 0) -> str:
        """Record any point-earning action"""
        mod = self._get_or_create_moderator(mod_id, mod_name)
        
        # Calculate points based on action
        if action == ActionType.SUPER_CHAT:
            points = int(amount * 10)  # 10 points per dollar
        else:
            points = action.value
            
        earned_points, achievements = mod.add_points(points, action, details)
        
        # Build response
        response = f"✨ {mod_name} earned {earned_points} points for {action.name}!"
        response += f"\n📊 Total: {mod.total_points} | Level: {mod.level.value[1]}"
        
        for achievement in achievements:
            response += f"\n🏆 {achievement}"
            
        self.save_data()
        return response
    
    def get_leaderboard(self, limit: int = 10) -> str:
        """Get current leaderboard"""
        sorted_mods = sorted(self.moderators.values(), key=lambda x: x.total_points, reverse=True)
        
        leaderboard = "🏆 **WHACK-A-MAGAt LEADERBOARD** 🏆\n"
        leaderboard += "=" * 40 + "\n"
        
        for i, mod in enumerate(sorted_mods[:limit], 1):
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            leaderboard += f"{emoji} {mod.display_name}\n"
            leaderboard += f"   {mod.level.value[1]}\n"
            leaderboard += f"   Points: {mod.total_points:,} | Whacks: {mod.maga_timeouts}\n"
            if mod.achievements:
                leaderboard += f"   🏅 {len(mod.achievements)} achievements\n"
            leaderboard += "\n"
            
        return leaderboard
    
    def get_stats(self, mod_id: str) -> Optional[str]:
        """Get detailed stats for a moderator"""
        if mod_id not in self.moderators:
            return None
            
        mod = self.moderators[mod_id]
        
        stats = f"📊 **{mod.display_name}'s Stats**\n"
        stats += f"Level: {mod.level.value[1]}\n"
        stats += f"Total Points: {mod.total_points:,}\n"
        stats += f"MAGA Timeouts: {mod.maga_timeouts}\n"
        stats += f"Spam Caught: {mod.spam_caught}\n"
        stats += f"Members Helped: {mod.members_helped}\n"
        stats += f"Raids Stopped: {mod.raids_stopped}\n"
        stats += f"Gifts Given: {mod.gifts_given}\n"
        
        if mod.achievements:
            stats += f"\n🏆 Achievements ({len(mod.achievements)}):\n"
            for achievement in mod.achievements:
                stats += f"  • {achievement}\n"
                
        return stats
    
    def _get_or_create_moderator(self, mod_id: str, mod_name: str) -> ModeratorProfile:
        """Get existing moderator or create new profile"""
        if mod_id not in self.moderators:
            self.moderators[mod_id] = ModeratorProfile(
                user_id=mod_id,
                display_name=mod_name
            )
        return self.moderators[mod_id]
    
    def daily_bonus(self, mod_id: str, mod_name: str) -> str:
        """Award daily login bonus"""
        mod = self._get_or_create_moderator(mod_id, mod_name)
        
        # Check if already claimed today
        if mod.last_action and mod.last_action.date() == datetime.now().date():
            return f"❌ {mod_name}, you already claimed your daily bonus!"
            
        # Award streak bonus
        if mod.last_action and (datetime.now() - mod.last_action).days == 1:
            mod.streak_days += 1
        else:
            mod.streak_days = 1
            
        bonus = 50 * mod.streak_days
        mod.total_points += bonus
        mod.last_action = datetime.now()
        
        self.save_data()
        
        return f"📅 Daily Bonus! {mod_name} earned {bonus} points (Day {mod.streak_days} streak)"
    
    def challenge_mode(self, description: str, points: int, duration_hours: int = 24):
        """Create a time-limited challenge"""
        # This would create special challenges like:
        # - "Double points for MAGA whacks for next 2 hours"
        # - "First to whack 10 MAGAs gets 1000 bonus points"
        # - "Team challenge: Collective 100 whacks = everyone gets 500 points"
        pass


# --- WSP Enhancement: Scoring Engine with Archetypes & Anti-Exploit ---
from modules.communication.chat_rules.src.database import ChatRulesDB

_BASE_POINTS = {
    10: 0,
    30: 1,
    120: 2,
    300: 4,
    900: 7,
    3600: 12,
    21600: 18,
    86400: 26,
}

def _nearest_tier(seconds: int) -> int:
    tiers = sorted(_BASE_POINTS.keys())
    for t in tiers:
        if seconds <= t:
            return t
    return tiers[-1]

class WhackScoringEngine:
    """
    WSP-compliant scoring engine implementing tiers, bonuses, and anti-exploit rules.
    Uses ChatRulesDB for persistence and leaderboards.
    """
    def __init__(self, db: Optional[ChatRulesDB] = None):
        self.db = db or ChatRulesDB()
        # in-memory combo tracking
        self._last_action_at: Dict[str, datetime] = {}

    def _room_activity_gate(self, room_activity_rate: float) -> bool:
        # Enabled only if activity >= 30 msgs / 5min
        return room_activity_rate >= 30.0

    def _variety_bonus(self, mod_id: str) -> float:
        with self.db.get_connection() as conn:
            cur = conn.execute(
                """
                SELECT COUNT(DISTINCT target_id) AS c
                FROM timeout_history
                WHERE mod_id=? AND timestamp > datetime('now','-15 minutes')
                """,
                (mod_id,),
            )
            c = cur.fetchone()[0] if cur.fetchone() is not None else 0
        if c >= 8:
            return 1.20
        if c >= 4:
            return 1.10
        return 1.0

    def _per_target_caps(self, mod_id: str, target_id: str) -> Tuple[bool, float]:
        # DR: −40% per additional hit on same user within 10 min (min 0 after 3rd)
        with self.db.get_connection() as conn:
            cur = conn.execute(
                """
                SELECT COUNT(*) FROM timeout_history
                WHERE target_id=? AND timestamp > datetime('now','-10 minutes')
                """,
                (target_id,),
            )
            hits10 = cur.fetchone()[0]

            cur = conn.execute(
                """
                SELECT COUNT(*) FROM timeout_history
                WHERE mod_id=? AND target_id=? AND timestamp > datetime('now','-60 minutes')
                """,
                (mod_id, target_id),
            )
            per_hour = cur.fetchone()[0]

        if per_hour >= 2:
            return False, 0.0  # no scoring beyond 2 per hour per target

        dr = max(0.0, 1.0 - max(0, hits10 - 1) * 0.4)  # 1st full, 2nd -40%, 3rd 0
        return True, dr

    def _per_mod_rate_limit(self, mod_id: str) -> float:
        with self.db.get_connection() as conn:
            cur = conn.execute(
                """
                SELECT COUNT(*) FROM timeout_history
                WHERE mod_id=? AND timestamp > datetime('now','-15 minutes')
                """,
                (mod_id,),
            )
            count15 = cur.fetchone()[0]
        return 0.5 if count15 > 12 else 1.0

    def _combo_multiplier(self, mod_id: str, now: datetime) -> float:
        last = self._last_action_at.get(mod_id)
        if last is None:
            self._last_action_at[mod_id] = now
            return 1.0
        gap = (now - last).total_seconds()
        self._last_action_at[mod_id] = now
        if gap > 120:
            return 1.0  # idle reset after 2m
        # +5% per consecutive valid action within 90s (max +25%)
        if gap <= 90:
            # We do not track streak length precisely here; approximate +5% per action up to 25%
            return 1.05
        return 1.0

    def _cross_mod_collision(self, mod_id: str, target_id: str) -> bool:
        with self.db.get_connection() as conn:
            cur = conn.execute(
                """
                SELECT mod_id FROM timeout_history
                WHERE target_id=? AND timestamp > datetime('now','-10 seconds')
                ORDER BY timestamp ASC LIMIT 1
                """,
                (target_id,),
            )
            row = cur.fetchone()
        if not row:
            return False
        first_mod = row[0]
        return first_mod != mod_id

    def process_whack_event(
        self,
        *,
        mod_id: str,
        mod_name: str,
        target_id: str,
        target_name: str,
        duration_seconds: int,
        room_activity_rate: float,
        reason: str = "",
    ) -> int:
        """Compute points, enforce caps, record event, and update leaderboard."""
        if not self._room_activity_gate(room_activity_rate):
            points = 0
        else:
            # Cross-mod collision: only earlier action scores
            if self._cross_mod_collision(mod_id, target_id):
                points = 0
            else:
                tier = _nearest_tier(duration_seconds)
                base = _BASE_POINTS.get(tier, 0)
                # Anti-exploit: No points for 10s
                if tier == 10:
                    base = 0

                eligible, dr = self._per_target_caps(mod_id, target_id)
                if not eligible:
                    points = 0
                else:
                    now = datetime.now()
                    combo = self._combo_multiplier(mod_id, now)
                    variety = self._variety_bonus(mod_id)
                    rate_lim = self._per_mod_rate_limit(mod_id)
                    # Escalation bonus approximate (we lack per-target last tier table): apply when jumping >=2 tiers
                    escalation = 1.0
                    # Sheriff/Sniper ribbons depend on longer stats; omitted in v1 minimal implementation
                    points = int(base * dr * combo * variety * rate_lim * escalation)

        # Persist event and update moderator totals
        self.db.get_or_create_moderator(mod_id, mod_name)
        self.db.record_timeout(
            mod_id=mod_id,
            target_id=target_id,
            target_name=target_name,
            duration_seconds=duration_seconds,
            points_earned=points,
            reason=reason,
        )
        # Increment totals
        leaderboard = self.db.get_leaderboard(limit=1000)
        current = next((m for m in leaderboard if m["user_id"] == mod_id), None)
        total = (current["total_points"] if current else 0) + points
        self.db.update_moderator_points(mod_id, total)
        self.db.increment_daily_count(mod_id)
        return points

    def generate_leaderboard(self, limit: int = 10) -> List[Tuple[str, int]]:
        rows = self.db.get_leaderboard(limit=limit)
        return [(r["display_name"], r["total_points"]) for r in rows]



# Integration example
if __name__ == "__main__":
    # Initialize the system
    whack_system = WhackAMAGAtSystem()
    
    # Moderator whacks a MAGA
    result = whack_system.record_whack(
        mod_id="mod123",
        mod_name="SuperMod",
        target="MAGATroll42",
        reason="MAGA spam detected"
    )
    print(result)
    
    # Moderator helps a member
    result = whack_system.record_action(
        mod_id="mod123",
        mod_name="SuperMod",
        action=ActionType.HELP_MEMBER,
        details="Helped member with consciousness elevation"
    )
    print(result)
    
    # Show leaderboard
    print(whack_system.get_leaderboard())
    
    # Get mod stats
    print(whack_system.get_stats("mod123"))