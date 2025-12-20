# -*- coding: utf-8 -*-
"""
Timeout Manager - Whack-a-MAGA System Integration
WSP-Compliant: Integrates with gamification.whack for points/XP
WSP 90 Compliant: UTF-8 encoding enforced

Features:
- Integrates with whack.py for gamification
- Duke Nukem/Quake announcer
- D&D-style level names based on whack ranks
- Uses whack's anti-farming protection
"""

import logging
import json
import os
import time
import random
import sqlite3
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from collections import defaultdict

# Import whack gamification from same module
from modules.gamification.whack_a_magat.src.whack import apply_whack, get_profile, classify_behavior, BehaviorTier
# Import the deduplication tracker
from modules.gamification.whack_a_magat.src.timeout_tracker import TimeoutTracker
# Import spree tracking for killing sprees
from modules.gamification.whack_a_magat.src.spree_tracker import track_frag, get_active_sprees
# Import self-improvement for learning
from modules.gamification.whack_a_magat.src.self_improvement import (
    observe_timeout, observe_spree, get_optimized_thresholds
)
# Import terminology enforcer to ensure consistent MAGADOOM theme
from modules.gamification.whack_a_magat.src.terminology_enforcer import enforce_terminology
# Removed ChatDatabase import to avoid circular dependency
# Will initialize lazily if needed

logger = logging.getLogger(__name__)


class TimeoutManager:
    """Manages timeouts with Duke Nukem announcer and whack.py gamification"""
    
    def __init__(self, memory_dir: str = None):
        if memory_dir is None:
            # Use absolute path for the memory directory
            memory_dir = os.path.join(os.path.dirname(__file__), "..", "memory")
        self.memory_dir = os.path.abspath(memory_dir)
        self.stats_file = os.path.join(self.memory_dir, "timeout_announcer.json")
        
        # Lazy initialize database to avoid circular import
        self.db = None
        self.db_path = os.path.join(self.memory_dir, "auto_moderator.db")
        
        # MAGADOOM RANKS - Pure DOOM/FPS style (NO old terminology!)
        self.rank_titles = {
            "GRUNT": ["Fresh Meat", "Boot Camp", "Cannon Fodder"],
            "MARINE": ["RIP AND TEAR", "Shotgun Ready", "Learning to Frag"],
            "WARRIOR": ["Battle Hardened", "Frag Master", "Arena Fighter"],
            "SLAYER": ["DOOM Music Intensifies", "Demon Hunter", "Hell Walker"],
            "HUNTER": ["Stalking Prey", "Silent Death", "Shadow Warrior"],
            "CHAMPION": ["Arena Champion", "Crowd Favorite", "Unstoppable Force"],
            "MASTER": ["Master of Arena", "Death Incarnate", "Legend in Making"],
            "ELITE": ["Elite Demon Hunter", "Fear Incarnate", "Nightmare Mode"],
            "GODLIKE": ["Ascending to Godhood", "Divine Punishment", "Apocalypse Bringer"],
            "LEGENDARY": ["Stuff of Legends", "Myth Made Real", "Eternal Glory"],
            "DOOM SLAYER": ["THE ONLY ONE THEY FEAR", "RIP AND TEAR UNTIL IT IS DONE", "MAGADOOM INCARNATE"]
        }
        
        # Kill streak tracking for Duke Nukem announcer
        self.kill_streaks = {}  # mod_id -> current streak
        self.last_kill_time = {}  # mod_id -> timestamp
        self.announced_milestones = {}  # mod_id -> set of milestones already announced this session
        self.streak_window = 15  # seconds to maintain streak
        
        # Moderator name tracking (for displaying leaderboard)
        self.mod_names = {}  # mod_id -> display name
        
        # Multi-whack tracking for Quake-style announcements
        self.multi_whack_count = {}  # mod_id -> count of rapid whacks
        self.multi_whack_time = {}  # mod_id -> last whack time for multi tracking
        
        # Stream session tracking for join announcements (once per stream)
        self.announced_joins = set()  # Set of user_ids who have been announced this stream
        self.stream_start_time = time.time()  # Reset when stream restarts
        
        # NBA JAM session-wide milestone tracking (total timeouts in stream)
        self.session_total_whacks = 0  # Total whacks this stream session
        self.session_milestones_announced = set()  # Which milestones we've announced
        
        # Quake-style multi-kill windows (increased for YouTube chat timing)
        self.multi_whack_window = 10  # 10 seconds for DOUBLE WHACK (as requested)
        self.min_time_between_whacks = 1.0  # Minimum time between whacks to count
        
        # Dynamic density tracking
        self.recent_timeout_times = []  # Track recent timeouts for density calculation
        self.density_window = 60  # Track timeouts in last 60 seconds
        self.last_announcement_time = 0  # Anti-spam tracking
        self.min_announcement_gap = 2  # Minimum seconds between announcements
        
        # Achievement tracking - learn what mods can actually do
        self.achieved_multi_whacks = []  # Track successful multi-whack times
        self.optimal_window = 60  # Will adjust based on actual performance
        
        # Initialize timeout tracker for deduplication and frag counting
        self.tracker = TimeoutTracker()
        
        # Ensure memory directory exists
        os.makedirs(self.memory_dir, exist_ok=True)
        # Load announcer stats
        self.load_stats()
        
        # Clear any cached announcements on init
        self._clear_announcement_cache()
        logger.info("TimeoutManager initialized with whack.py integration and Duke Nukem announcer")
    
    def load_stats(self):
        """Load saved announcer statistics"""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r') as f:
                    data = json.load(f)
                    self.kill_streaks = data.get("kill_streaks", {})
                    # Don't load old timestamps as they're stale
                    logger.info(f"Loaded announcer stats")
            except Exception as e:
                logger.error(f"Error loading announcer stats: {e}")
    
    def _clear_announcement_cache(self):
        """Clear cached announcements to ensure fresh terminology."""
        # Reset all cached state
        self.announced_milestones = {}
        self.multi_whack_count = {}
        self.multi_whack_time = {}
        self.kill_streaks = {}
        logger.info("[REFRESH] Announcement cache cleared - MAGADOOM terminology enforced")
    
    def save_stats(self):
        """Save announcer statistics"""
        try:
            data = {
                "kill_streaks": self.kill_streaks,
                "last_save": datetime.now().isoformat()
            }
            with open(self.stats_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving announcer stats: {e}")
    
    def calculate_stream_density(self) -> str:
        """Calculate current stream density based on recent timeout frequency"""
        current_time = time.time()
        
        # Clean old entries
        self.recent_timeout_times = [
            t for t in self.recent_timeout_times 
            if current_time - t <= self.density_window
        ]
        
        # Calculate timeouts per minute
        timeouts_per_minute = len(self.recent_timeout_times) * (60 / self.density_window)
        
        # Determine density level
        if timeouts_per_minute < 2:
            return "LOW"  # Chill stream
        elif timeouts_per_minute < 5:
            return "MEDIUM"  # Active stream
        elif timeouts_per_minute < 10:
            return "HIGH"  # Busy stream
        else:
            return "EXTREME"  # Raid or massive stream
    
    def learn_from_achievement(self, time_between_whacks: float):
        """Learn from successful multi-whacks to optimize window"""
        if time_between_whacks >= self.min_time_between_whacks:  # Valid achievement
            self.achieved_multi_whacks.append(time_between_whacks)
            
            # Keep last 20 achievements
            if len(self.achieved_multi_whacks) > 20:
                self.achieved_multi_whacks.pop(0)
            
            # Calculate optimal window (95th percentile of achievements)
            if len(self.achieved_multi_whacks) >= 5:
                sorted_times = sorted(self.achieved_multi_whacks)
                percentile_95 = sorted_times[int(len(sorted_times) * 0.95)]
                
                # Gradually adjust window toward optimal (max 10s for Quake-style)
                self.optimal_window = min(10, percentile_95 * 1.2)  # 20% buffer, max 10s
                logger.info(f"[TARGET] Learned optimal multi-whack window: {self.optimal_window:.1f}s")
    
    def adjust_thresholds(self):
        """Dynamically adjust based on stream density AND mod capabilities"""
        density = self.calculate_stream_density()
        
        # FIXED 10-second window as requested by user for multi-kill ramp-up
        base_window = 10  # Always 10 seconds for multi-kills
        
        # Adjust announcement gaps based on density
        if density == "LOW":
            self.min_announcement_gap = 1
            announcement_chance = 1.0
        elif density == "MEDIUM":
            self.min_announcement_gap = 2
            announcement_chance = 0.9
        elif density == "HIGH":
            self.min_announcement_gap = 3
            announcement_chance = 0.7
        else:  # EXTREME
            self.min_announcement_gap = 2  # Keep it fast for mockery
            announcement_chance = 0.4  # Still show some regular, rest become mockery
        
        # Always use 10 second window as requested
        self.multi_whack_window = base_window
        
        logger.debug(f"[GAME] Stream density: {density} | Multi-whack window: {self.multi_whack_window:.1f}s")
        return announcement_chance
    
    def get_title_for_profile(self, profile) -> str:
        """Get D&D title based on whack.py rank and level"""
        rank = profile.rank
        level = profile.level
        
        if rank not in self.rank_titles:
            # Trollish fallback for unknown ranks
            return "UNRANKED SCRUB"
        
        titles = self.rank_titles[rank]
        # Pick title based on level within rank
        if rank == "Bronze":
            index = min(level - 1, len(titles) - 1)
        elif rank == "Silver":
            index = min((level - 2) % 3, len(titles) - 1)  
        elif rank == "Gold":
            index = min((level - 4) % 3, len(titles) - 1)
        else:  # Platinum
            index = min(level - 6, len(titles) - 1)
        
        title = titles[max(0, index)]
        # Enforce MAGADOOM terminology on title
        return enforce_terminology(title)
    
    def record_timeout(self, mod_id: str, mod_name: str, target_id: str, target_name: str,
                      duration: int, reason: str = "MAGA", timestamp: str = None) -> Dict[str, Any]:
        """
        Record a timeout using whack.py and generate announcements

        Args:
            timestamp: Optional ISO timestamp from YouTube event for accurate multi-whack detection

        Returns:
            Dict with 'announcement', 'level_up', 'stats', 'behavior'
        """
        # FIX: Validate target_name to prevent truncated/empty usernames
        # YouTube API sometimes returns partial display names
        if not target_name or len(target_name) <= 2 or target_name.strip() in ["", "t!", "!"]:
            logger.warning(f"[U+26A0]️ Invalid/truncated target_name detected: '{target_name}' - using fallback")
            target_name = "MAGAT"  # Fallback for truncated/empty names

        # Use provided timestamp if available, otherwise current time
        if timestamp:
            # Parse ISO timestamp to Unix time
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                current_time = dt.timestamp()
                logger.info(f"📅 Using event timestamp: {timestamp} -> {current_time:.2f}")
            except:
                current_time = time.time()
                logger.warning(f"[U+26A0]️ Failed to parse timestamp '{timestamp}', using current time")
        else:
            current_time = time.time()
        
        # Track timeout for density calculation
        self.recent_timeout_times.append(current_time)
        
        # Adjust thresholds based on current stream density
        announcement_chance = self.adjust_thresholds()
        
        result = {
            "announcement": None,
            "level_up": None,
            "stats": None,
            "points_gained": 0,
            "behavior": None,
            "density": self.calculate_stream_density()
        }
        
        # Store moderator name for leaderboard display
        self.mod_names[mod_id] = mod_name
        
        # === DETECT MULTI-WHACK FIRST (before applying points!) ===
        # This MUST happen before apply_whack so the multiplier is ready
        self._detect_multi_whack(mod_id, mod_name, target_name, current_time)
        
        # Get current profile for comparison
        old_profile = get_profile(mod_id, mod_name)
        old_score = old_profile.score
        old_rank = old_profile.rank
        old_level = old_profile.level
        
        # Apply the whack (handles all gamification logic)
        action = apply_whack(
            moderator_id=mod_id,
            target_id=target_id,
            duration_sec=int(duration),  # Ensure it's an int
            now=datetime.now(),
            moderator_name=mod_name
        )
        
        # Increment session total whacks for NBA JAM milestones
        self.session_total_whacks += 1
        
        # Track this timeout/ban for frag counting
        is_valid, event_info = self.tracker.process_ban_event(
            event_id=f"{mod_id}_{target_id}_{int(time.time())}",  # Generate unique ID
            mod_id=mod_id,
            mod_name=mod_name,
            target_id=target_id,
            target_name=target_name,
            timestamp=datetime.now().isoformat(),
            duration_seconds=duration,
            is_permanent=(duration >= 86400)  # 24h+ is considered permanent
        )
        
        if is_valid:
            logger.info(f"[TARGET] Tracked whack: {mod_name} -> {target_name} (Total: {self.tracker.get_mod_stats(mod_id).get('frag_count', 0)})")

            # PHASE 3O-3R: Record whacked user for 0/1/2 classification
            try:
                from modules.gamification.whack_a_magat.src.whack import get_profile_store
                profile_store = get_profile_store()
                profile_store.record_whacked_user(target_id, target_name, mod_id)
            except Exception as e:
                logger.error(f"[WHACK-DB] Failed to record whacked user: {e}")

        # Persist to database
        if self.db:
            try:
                self.db.log_timeout(target_id, target_name, reason, duration)
                logger.debug(f"Persisted timeout to DB: {target_name} for {duration}s")
            except Exception as e:
                logger.error(f"Failed to persist timeout: {e}")
        
        # Get updated profile
        new_profile = get_profile(mod_id, mod_name)
        base_points = action.points
        
        # Apply consecutive multiplier bonus for rapid moderation (different targets only)
        multi_count = self.multi_whack_count.get(mod_id, 1)
        multiplier = 1
        if multi_count > 1:
            # Multiplier: 1x, 2x, 3x, 4x, 5x (capped at 5x)
            multiplier = min(multi_count, 5)
            bonus_points = base_points * (multiplier - 1)  # Extra points beyond base
            if bonus_points > 0:
                logger.info(f"🎰 COMBO MULTIPLIER x{multiplier}! Base: {base_points} + Bonus: {bonus_points} = Total: {base_points * multiplier}")
                new_profile.score += bonus_points
                from modules.gamification.whack_a_magat.src.whack import _update_rank_and_level, _profiles_repo
                _update_rank_and_level(new_profile)
                _profiles_repo.save(new_profile)
        
        # Calculate total points for display
        points_gained = base_points * multiplier
        
        # Track for killing sprees
        spree_result = track_frag(mod_id, mod_name, target_id, points_gained)
        if spree_result:
            # We hit a spree milestone!
            result["spree"] = spree_result
            result["spree_announcement"] = spree_result["announcement"]
            # Add bonus XP for the spree
            if spree_result["bonus_xp"] > 0:
                old_score = new_profile.score
                new_profile.score += spree_result["bonus_xp"]
                from modules.gamification.whack_a_magat.src.whack import _update_rank_and_level, _profiles_repo
                _update_rank_and_level(new_profile)
                _profiles_repo.save(new_profile)
                logger.info(f"[TARGET] Spree bonus: {mod_name} gained +{spree_result['bonus_xp']} XP for {spree_result['spree_level']}")
                # Observe for self-improvement
                observe_spree(mod_id, spree_result["spree_level"], spree_result["frag_count"])
        
        # Check for rank/level up
        if new_profile.rank != old_rank or new_profile.level != old_level:
            new_title = self.get_title_for_profile(new_profile)
            if new_profile.rank != old_rank:
                result["level_up"] = f"🏆 {mod_name} RANKED UP to {new_profile.rank}! Now: {new_title}!"
            else:
                result["level_up"] = f"🎉 {mod_name} LEVELED UP to {new_title}! (Level {new_profile.level})"
        
        # Classify behavior for flavor text
        recent_actions = self._count_recent_actions_on_target(mod_id, target_id)
        behavior = classify_behavior(duration, recent_actions)
        result["behavior"] = behavior.value
        
        # Observe timeout for self-improvement
        observe_timeout(mod_id, duration, result["density"])
        
        # Store duration for HUMILIATION detection
        self._last_duration = duration
        
        # Get current streak for anti-spam logic
        streak = self.kill_streaks.get(mod_id, 0)
        
        # Generate Quake/Duke Nukem announcement (pass the event timestamp for accurate multi-whack detection)
        duke_announcement = self._get_timeout_announcement(mod_id, mod_name, target_name, current_time)
        
        # Get multi-count for anti-spam logic
        multi_count = self.multi_whack_count.get(mod_id, 1)
        
        # MAGADOOM TROLL MOCKERY - Enhanced for raids and rapid-fire!
        if duke_announcement:
            time_since_last = current_time - self.last_announcement_time
            
            # Check if this is an epic multi-whack announcement (always send these!)
            is_epic = any(keyword in duke_announcement for keyword in 
                         ["MONSTER", "LUDICROUS", "HOLY SHIT", "GODLIKE", "CENTURY", "MULTI", "MEGA", "ULTRA", 
                          "DOUBLE WHACK", "MULTI WHACK", "KILLING SPREE", "RAMPAGE"])
            
            # Rapid-fire detection - but ONLY convert to mockery if NOT a multi-whack
            if time_since_last < self.min_announcement_gap and self.last_announcement_time > 0:
                if not is_epic:
                    # Too rapid and not epic - convert to MAGA mockery
                    mockery_options = [
                        f"😂 {mod_name} SPEEDRUN BANS {target_name}! Any%!",
                        f"🎪 {target_name} joins {mod_name}'s CLOWN FIESTA!",
                        f"🗑️ {mod_name} tosses another one on the TRASH PILE!",
                        f"💨 {mod_name} YEETS {target_name}!",
                        f"🚮 {mod_name} taking out the GARBAGE!",
                        f"🤡 {mod_name} identifies {target_name} = MAGA NPC #9999",
                        f"🎯 {mod_name} FRAGGED {target_name}! Next!",
                        f"💥 {mod_name} DELETED {target_name}! Who's next?"
                    ]
                    duke_announcement = random.choice(mockery_options)
                    logger.info(f"🤡 Rapid-fire mockery activated!")
                else:
                    # Epic announcements ALWAYS go through
                    logger.info(f"🔥 EPIC ANNOUNCEMENT DETECTED - SENDING!")
            
            # EXTREME DENSITY (raid mode) - enhance ALL announcements
            if result['density'] == 'EXTREME':
                if multi_count >= 5:
                    # GODLIKE performance during raid
                    duke_announcement = f"🌊💀🔥 RAID OBLITERATOR! {duke_announcement} 🔥💀🌊"
                elif multi_count >= 3:
                    # Multi-whack during raid
                    duke_announcement = f"🎯 RAID DEFENSE MODE! {duke_announcement}"
                elif random.random() > announcement_chance and not is_epic:
                    # Random raid mockery (but not for epic announcements)
                    raid_mockery = [
                        f"🌊 MAGA WAVE DETECTED - {mod_name} SURFING!",
                        f"🎯 {mod_name} - TARGET RICH ENVIRONMENT!",
                        f"🔫 IT'S RAINING TROLLS! HALLELUJAH!",
                        f"🎮 {mod_name} farming XP like it's 1999!",
                        f"🚜 {mod_name} HARVESTING THE MAGA CROP!",
                        f"⚡ RAID BOSS {mod_name} AOE DAMAGE!"
                    ]
                    duke_announcement = random.choice(raid_mockery)
                    logger.info(f"🌊 Raid mockery activated!")
            
            logger.info(f"📢 Final announcement: {duke_announcement[:80]}...")
            # Always update time when we have an announcement
            self.last_announcement_time = current_time
        
        # Add behavior-specific flavor
        behavior_flavor = self._get_behavior_flavor(behavior, mod_name, target_name, duration)
        
        # Combine announcements - always show something!
        announcements = []
        if duke_announcement:
            announcements.append(duke_announcement)
        elif behavior_flavor:
            announcements.append(behavior_flavor)
        else:
            # Default announcement
            announcements.append(f"💥 {mod_name} WHACKS {target_name}!")
        
        # Add points info - points_gained already includes multiplier
        if points_gained > 0:
            multi_count = self.multi_whack_count.get(mod_id, 1)
            if multi_count > 1:
                multiplier = min(multi_count, 5)
                # Show total points with multiplier indicator
                announcements.append(f"[+{points_gained} pts! (x{multiplier} COMBO)]")
            else:
                announcements.append(f"[+{points_gained} pts]")
        # Daily cap removed - no need to show cap message
        
        # Check NBA JAM session milestones (stream-wide, not individual)
        nba_milestone = self._check_nba_session_milestone()
        if nba_milestone:
            # NBA JAM milestone takes priority - it's about the stream heating up!
            announcements.insert(0, nba_milestone)
        
        # Enforce MAGADOOM terminology on final announcement
        final_announcement = " ".join(announcements) if announcements else None
        if final_announcement:
            final_announcement = enforce_terminology(final_announcement)
        
        result["announcement"] = final_announcement
        result["points_gained"] = points_gained
        result["stats"] = {
            "score": new_profile.score,
            "rank": new_profile.rank,
            "level": new_profile.level,
            "title": self.get_title_for_profile(new_profile)
        }
        
        # Save announcer stats
        self.save_stats()
        
        return result
    
    def _detect_multi_whack(self, mod_id: str, mod_name: str, target_name: str, current_time: float):
        """
        Detect and track multi-whack combos BEFORE applying points.
        This must run before apply_whack() so the multiplier is ready.
        """
        # Check for multi-whacks (respecting YouTube cooldown)
        if mod_id in self.multi_whack_time:
            time_since_last = current_time - self.multi_whack_time[mod_id]
            logger.info(f"⏱️ Time since last whack: {time_since_last:.2f}s (window: {self.multi_whack_window}s)")
            
            # Learn from successful multi-whacks
            if time_since_last >= self.min_time_between_whacks and time_since_last <= self.multi_whack_window:
                self.learn_from_achievement(time_since_last)
            
            if time_since_last <= self.multi_whack_window:
                # Check if this is the same target as last time (prevent gaming)
                last_target = self.last_whack_target.get(mod_id) if hasattr(self, 'last_whack_target') else None
                if last_target == target_name:
                    # Same target - don't increment multi-whack (prevent farming)
                    logger.info(f"[FORBIDDEN] Same target whacked - no multi-whack bonus (anti-farming)")
                    # Reset the count since they're farming
                    self.multi_whack_count[mod_id] = 1
                else:
                    # Different target - this is a legitimate multi-whack!
                    self.multi_whack_count[mod_id] = self.multi_whack_count.get(mod_id, 1) + 1
                    logger.info(f"🔥 MULTI-WHACK INCREMENT! {mod_name} now at {self.multi_whack_count[mod_id]} whacks!")
                    logger.info(f"   Different targets within {self.multi_whack_window}s window!")
            else:
                # Window expired - reset to 1
                logger.info(f"⏰ Multi-whack window expired ({time_since_last:.2f}s > {self.multi_whack_window}s), resetting count")
                self.multi_whack_count[mod_id] = 1
        else:
            # First whack
            logger.info(f"[TARGET] First whack for {mod_name}")
            self.multi_whack_count[mod_id] = 1
        
        # Track the last target for anti-gaming logic
        if not hasattr(self, 'last_whack_target'):
            self.last_whack_target = {}
        self.last_whack_target[mod_id] = target_name
        
        self.multi_whack_time[mod_id] = current_time
        multi_count = self.multi_whack_count[mod_id]
        
        # Debug logging
        logger.info(f"🎮 MULTI-WHACK CHECK: {mod_name} count={multi_count} (window: {self.multi_whack_window}s)")
        if multi_count > 1:
            logger.info(f"🔥 MULTI-WHACK DETECTED! Count: {multi_count} for {mod_name}")
    
    def _check_nba_session_milestone(self) -> Optional[str]:
        """Check for NBA JAM style session milestones - the stream heating up!"""
        total = self.session_total_whacks
        
        # NBA JAM MAGADOOM milestones (session-wide, not per mod)
        milestones = {
            25: "🏀 THE STREAM IS HEATING UP! 25 MAGA TROLLS WHACKED!",
            35: "🔥 THE CHAT IS ON FIRE!!! 35 MAGATS DESTROYED! (He's ON FIRE!!!)",
            50: "⚡ BOOMSHAKALAKA! 50 FASCISTS ELIMINATED! THE STREAM IS LIT!",
            75: "💥 FROM DOWNTOWN! 75 RED HATS CRUSHED! (Is it the shoes?!)",
            100: "🌟 RAZZLE DAZZLE! 100 WHACKS! CENTURY OF MAGA TEARS!",
            150: "🎆 HE'S UNCONSCIOUS! 150 TROLLS DELETED! (Puts up a brick!)",
            200: "💀 WITH NO REGARD FOR HUMAN LIFE! 200 MAGATS DEMOLISHED!",
            250: "🔥 CAN'T BUY A BUCKET! 250 FASCISTS FAILING! STREAM DOMINATION!",
            300: "⚡ MONSTER JAM! 300 WHACKS! THE COUP ATTEMPT IS OVER!",
            400: "🏆 JAMS IT IN! 400 MAGA DREAMS SHATTERED!",
            500: "🌋 WELCOME TO THE JAM! HALF A THOUSAND TROLLS TERMINATED!"
        }
        
        # Check if we've hit a new milestone
        for milestone_count, message in milestones.items():
            if total == milestone_count and milestone_count not in self.session_milestones_announced:
                self.session_milestones_announced.add(milestone_count)
                logger.info(f"[U+1F3C0] NBA JAM SESSION MILESTONE: {total} total whacks!")
                return message
        
        # Special every 100 after 500
        if total > 500 and total % 100 == 0 and total not in self.session_milestones_announced:
            self.session_milestones_announced.add(total)
            return f"[U+1F31F] LEGENDARY JAM! {total} MAGA NIGHTMARES! THE STREAM IS UNSTOPPABLE!"
        
        return None
    
    def _count_recent_actions_on_target(self, mod_id: str, target_id: str) -> int:
        """Count recent actions on same target (for behavior classification)"""
        # This would need access to whack's internal repo, so we estimate
        # For now, return 0 (will be handled by whack.py internally)
        return 0
    
    def _get_behavior_flavor(self, behavior: BehaviorTier, mod_name: str, target_name: str, duration: int) -> str:
        """Get flavor text based on behavior classification"""
        if behavior == BehaviorTier.CAT_PLAY:
            return f"🐱 {mod_name} is toying with {target_name} like a cat with a mouse!"
        elif behavior == BehaviorTier.BRUTAL_HAMMER:
            timeout_duration = f"{duration//3600}h" if duration >= 3600 else f"{duration//60}m"
            return f"🔨 {mod_name} brings down the BRUTAL HAMMER on {target_name}! ({timeout_duration})"
        elif behavior == BehaviorTier.GENTLE_TOUCH:
            return f"💥 {mod_name} WHACKS {target_name}!"
        else:
            return None
    
    def _get_timeout_announcement(self, mod_id: str, mod_name: str, target_name: str, event_time: float = None) -> Optional[str]:
        """Generate Quake 3 Arena style multi-whack or Duke Nukem milestone announcements
        
        NOTE: YouTube API limitation - all timeouts appear to come from the stream owner,
        even when performed by moderators. The API doesn't expose who performed the action.
        
        Args:
            event_time: Optional timestamp of the actual event for accurate multi-whack detection
        """
        current_time = event_time if event_time else time.time()
        
        # === MULTI-WHACK DETECTION NOW HAPPENS EARLIER ===
        # Detection moved to _detect_multi_whack() which is called BEFORE apply_whack()
        # This ensures the multiplier is ready when points are calculated
        multi_count = self.multi_whack_count.get(mod_id, 1)
        logger.info(f"[GAME] Using multi-whack count: {multi_count} for {mod_name}")
        
        # === DUKE NUKEM STYLE: Track overall kill streak ===
        if mod_id in self.last_kill_time:
            if current_time - self.last_kill_time[mod_id] > self.streak_window:
                # Streak expired, reset
                self.kill_streaks[mod_id] = 0
        
        self.kill_streaks[mod_id] = self.kill_streaks.get(mod_id, 0) + 1
        self.last_kill_time[mod_id] = current_time
        streak = self.kill_streaks[mod_id]
        
        # === CHECK MILESTONES (only announce when EXACTLY hitting them) ===
        duke_milestones = {
            5: f"[TARGET] WHACKING SPREE! {mod_name} - 5 WHACKS! 'Come get some!'",
            10: f"[LIGHTNING] RAMPAGE! {mod_name} - 10 WHACKS! 'Hail to the king, baby!'",
            15: f"[U+1F525] DOMINATING! {mod_name} - 15 WHACKS! 'It's time to kick ass and chew bubblegum!'",
            20: f"[U+2B50] UNSTOPPABLE! {mod_name} - 20 WHACKS! 'Damn, I'm good!'",
            25: f"[U+2620]️ GODLIKE! {mod_name} - 25 WHACKS! 'Rest in pieces!'",
            30: f"[U+1F451] WICKED SICK! {mod_name} - 30 WHACKS! 'Groovy!'",
            40: f"[U+1F31F] LEGENDARY! {mod_name} - 40 WHACKS! 'I've got balls of steel!'",
            50: f"[U+1F386] HOLY SHIT! {mod_name} - 50 WHACKS! 'Blow it out your ass!'",
            69: f"[U+1F480] NICE! {mod_name} - 69 WHACKS! 'Shake it baby!'",
            100: f"[U+1F3C6] CENTURY WHACK! {mod_name} - 100 WHACKS! 'ALL HAIL THE KING!'"
        }
        
        # Only announce milestones when EXACTLY hitting them AND not already announced
        if streak in duke_milestones:
            # Check if we've already announced this milestone this session
            if mod_id not in self.announced_milestones:
                self.announced_milestones[mod_id] = set()
            
            if streak not in self.announced_milestones[mod_id]:
                # New milestone! Announce it!
                self.announced_milestones[mod_id].add(streak)
                logger.info(f"🏆 NEW MILESTONE HIT: {mod_name} streak = {streak}")
                return duke_milestones[streak]
            else:
                logger.debug(f"[DATA] {mod_name} continuing streak at {streak} (milestone already announced)")
        elif streak > 100:
            return f"🎮🔥 {mod_name} LEGENDARY {streak} WHACK STREAK! 'I'M GONNA RIP OFF YOUR HEAD AND SHIT DOWN YOUR NECK!'"
        
        # === QUAKE STYLE MULTI-WHACK ANNOUNCEMENTS (rapid succession) ===
        if multi_count >= 2:
            # Primary QUAKE announcements
            multi_whack_messages = {
                2: f"💀💀 DOUBLE WHACK!! {mod_name} is WHACKING HARD! 🎯",
                3: f"🔥🔥🔥 MULTI WHACK!!! {mod_name} is ON FIRE! 🔥🔥🔥",
                4: f"⚡💥 MEGA WHACK!!!! {mod_name} is DOMINATING! ⚡💥",
                5: f"☠️💀 ULTRA WHACK!!!!! {mod_name} is UNSTOPPABLE! ☠️💀",
                6: f"🌟💥 MONSTER WHACK!!!!!! {mod_name} = WHACKING MACHINE! 🌟💥",
                7: f"🎆👹 LUDICROUS WHACK!!!!!!! {mod_name} is GODLIKE! 🎆👹",
                8: f"💀🔥 HOLY SHIT!!!!!!!! {mod_name} is BEYOND GODLIKE! 💀🔥"
            }
            
            # NBA JAM flavor text (randomly add as bonus)
            nba_jam_flavor = {
                2: "(Heating up!)",
                3: "(He's ON FIRE!!!)",
                4: "(BOOMSHAKALAKA!)",
                5: "(Is it the shoes?!)",
                6: "(FROM DOWNTOWN!)",
                7: "(RAZZLE DAZZLE!)",
                8: "(WITH NO REGARD FOR HUMAN LIFE!)"
            }
            
            if multi_count in multi_whack_messages:
                announcement = multi_whack_messages[multi_count]
                # Randomly add NBA JAM flavor (30% chance)
                if multi_count in nba_jam_flavor and random.random() < 0.3:
                    announcement += f" {nba_jam_flavor[multi_count]}"
                logger.info(f"[TARGET] MULTI-WHACK ANNOUNCEMENT: {announcement}")
                return announcement
            elif multi_count > 8:
                announcement = f"🎆🎆🎆 {mod_name} {multi_count}x WHACK COMBO!!! M-M-M-MONSTER WHACK!!! (WITH NO REGARD FOR HUMAN LIFE!)"
                logger.info(f"🎯 MEGA COMBO ANNOUNCEMENT: {announcement}")
                return announcement
        
        # === ONLY USE DURATION ANNOUNCEMENTS IF NO MULTI-KILL ===
        # Single timeout with no combo? Use duration-based announcement
        if multi_count == 1 and hasattr(self, '_last_duration'):
            duration = self._last_duration
            
            # YouTube's exact timeout durations (no ranges!)
            timeout_announcements = {
                10: f"👋 SLAP! {mod_name} slapped {target_name}! 'Behave!'",
                60: f"🔫 SHOTGUN BLAST! {mod_name} blasted {target_name}! 'Groovy!'",
                300: f"⚡ TACTICAL NUKE! {mod_name} nuked {target_name}! 'Boom baby!'",
                1800: f"💣 DEVASTATOR! {mod_name} OBLITERATED {target_name}! 'Eat shit and die!'",
                3600: f"🔥 MEGA PUNISHMENT! {mod_name} sent {target_name} to the shadow realm! 'Burn baby burn!'",
                86400: f"🌋 APOCALYPSE! {mod_name} BANISHED {target_name} for 24 HOURS! 'See you in hell!'"
            }
            
            # Check for exact match
            if duration in timeout_announcements:
                return timeout_announcements[duration]
            # Hide user (permanent) is usually a very large number
            elif duration >= 999999:
                return f"☠️💀 BFG 9000!!! {mod_name} HIDDEN {target_name} FROM CHAT! 'Get the fuck outta here!'"
            # Unknown duration (shouldn't happen with YouTube)
            else:
                return f"💥 {mod_name} WHACKS {target_name}!"
        
        # First whack
        if streak == 1:
            # Energetic Quake-style first frag announcements
            # QUAKE/DOOM style announcements  
            first_whack = [
                f"💥 FIRST BLOOD! {mod_name} WHACKED {target_name}!",
                f"🎯 {mod_name} SCORES! {target_name} ELIMINATED!",
                f"⚔️ {mod_name} WHACKS {target_name}! 'Excellent!'",
                f"🔫 {mod_name} WASTES {target_name}! 'Impressive!'",
                f"💀 {mod_name} DESTROYS {target_name}! 'Denied!'",
                f"🎮 {mod_name} PWNS {target_name}! 'Headshot!'"
            ]
            
            # NBA JAM side flavor (occasionally add for spice)
            nba_flavor = ["(REJECTED!)", "(NO GOOD!)", "(GET THAT OUTTA HERE!)"]
            announcement = random.choice(first_whack)
            if random.random() < 0.2:  # 20% chance for NBA JAM flavor
                announcement += f" {random.choice(nba_flavor)}"
            return announcement
        
        # Continuing streak (not at a milestone) - use Duke/Quake taunts
        if streak > 1:
            streak_continues = [
                f"💀 {mod_name} WHACKS {target_name}! Streak: {streak}! 'Get some!'",
                f"🔥 {mod_name} ELIMINATES {target_name}! {streak} IN A ROW!",
                f"⚡ {mod_name} DESTROYS {target_name}! STREAK: {streak}!",
                f"🎯 {mod_name} WASTES {target_name}! {streak} WHACKS AND COUNTING!",
                f"💥 {mod_name} OBLITERATES {target_name}! STREAK CONTINUES: {streak}!"
            ]
            return random.choice(streak_continues)
        
        # Fallback (shouldn't happen)
        return f"💥 {mod_name} WHACKS {target_name}!"
    
    def get_player_stats(self, mod_id: str) -> Optional[Dict[str, Any]]:
        """Get stats for a specific player from whack.py"""
        profile = get_profile(mod_id)
        if not profile:
            return None
        
        return {
            "score": profile.score,
            "rank": profile.rank,
            "level": profile.level,
            "title": self.get_title_for_profile(profile),
            "user_id": profile.user_id
        }
    
    def format_stats(self, mod_id: str) -> str:
        """Format player stats for chat display"""
        stats = self.get_player_stats(mod_id)
        if not stats:
            return "No stats yet!"
        
        return f"[DATA] Stats: {stats['title']} | Rank: {stats['rank']} | Level: {stats['level']} | Score: {stats['score']}"
    
    def get_all_mod_stats(self) -> List[Dict[str, Any]]:
        """Get stats for all moderators who have performed timeouts."""
        all_stats = []
        
        # This would need to query the whack.py database for all users
        # For now, return stats for known moderators in memory
        for mod_id in self.kill_streaks.keys():
            profile = get_profile(mod_id)
            if profile and profile.score > 0:
                all_stats.append({
                    "user_id": mod_id,
                    "name": self.mod_names.get(mod_id, "Unknown"),
                    "score": profile.score,
                    "rank": profile.rank,
                    "level": profile.level,
                    "title": self.get_title_for_profile(profile),
                    "current_streak": self.kill_streaks.get(mod_id, 0)
                })
        
        # Sort by score descending
        all_stats.sort(key=lambda x: x["score"], reverse=True)
        return all_stats
    
    def handle_chat_command(self, command: str, user_id: str, username: str, is_mod: bool) -> Optional[str]:
        """
        Handle chat commands related to timeout/whack system
        
        Commands:
        - /level - Show your current level
        - /stats - Show your stats
        - /smacks - Show how many timeouts you've given
        - /frags - Show all moderators' frag counts
        """
        if command == "/level" or command == "/stats":
            if not is_mod:
                return None  # Only mods can check stats
            
            stats = self.get_player_stats(user_id)
            if not stats:
                return f"@{username} No whack stats yet! Start timing out some trolls!"
            
            return f"@{username} {stats['title']} | {stats['rank']} Rank | Level {stats['level']} | {stats['score']} points"
        
        elif command == "/smacks":
            if not is_mod:
                return None
            
            # Get current streak if any
            streak = self.kill_streaks.get(user_id, 0)
            streak_text = f" | Current streak: {streak}" if streak > 0 else ""
            
            stats = self.get_player_stats(user_id)
            if stats:
                return f"@{username} Total score: {stats['score']} points{streak_text}"
            else:
                return f"@{username} No smacks yet!{streak_text}"
        
        elif command == "/frags":
            # Show leaderboard of all moderators
            all_stats = self.get_all_mod_stats()
            if not all_stats:
                return "No frags recorded yet!"
            
            # Format leaderboard
            lines = ["🏆 FRAG LEADERBOARD:"]
            for i, stat in enumerate(all_stats[:5]):  # Top 5
                emoji = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][i]
                streak_info = f" [streak: {stat['current_streak']}]" if stat['current_streak'] > 0 else ""
                lines.append(f"{emoji} {stat['name']}: {stat['score']} frags{streak_info}")
            
            return " | ".join(lines)
        
        return None