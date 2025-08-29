"""
MAGADOOM Status Announcer
Posts periodic updates about fragging activity and leaderboard
WSP-Compliant: Under 500 lines
"""

import logging
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from modules.gamification.whack_a_magat.src.whack import get_leaderboard, get_profile

logger = logging.getLogger(__name__)

class StatusAnnouncer:
    """Manages periodic MAGADOOM status updates"""
    
    def __init__(self, update_interval: int = 600):  # 10 minutes default
        """
        Initialize status announcer.
        
        Args:
            update_interval: Seconds between status updates (default 600 = 10 min)
        """
        self.update_interval = update_interval
        self.last_update = 0
        self.update_count = 0
        self.session_start = time.time()
        
        # Track session statistics
        self.session_stats = {
            "total_frags": 0,
            "unique_fraggers": set(),
            "top_fragger": None,
            "biggest_timeout": 0,
            "multi_whacks": 0,
            "milestones_reached": []
        }
        
        logger.info(f"StatusAnnouncer initialized with {update_interval}s interval")
        
    def should_post_update(self) -> bool:
        """Check if it's time to post an update"""
        current_time = time.time()
        if current_time - self.last_update >= self.update_interval:
            return True
        return False
        
    def record_frag(self, mod_id: str, duration: int, points: int):
        """Record a frag for statistics"""
        self.session_stats["total_frags"] += 1
        self.session_stats["unique_fraggers"].add(mod_id)
        
        if duration > self.session_stats["biggest_timeout"]:
            self.session_stats["biggest_timeout"] = duration
            
    def record_multi_whack(self, level: str):
        """Record a multi-whack achievement"""
        self.session_stats["multi_whacks"] += 1
        
    def record_milestone(self, mod_name: str, milestone: int):
        """Record a milestone achievement"""
        self.session_stats["milestones_reached"].append((mod_name, milestone))
        
    def generate_status_update(self) -> str:
        """
        Generate a MAGADOOM status update message.
        
        Returns:
            Status update string or None if no activity
        """
        self.update_count += 1
        self.last_update = time.time()
        
        # Get current leaderboard
        leaderboard = get_leaderboard(limit=5)
        
        # Calculate session duration
        session_minutes = int((time.time() - self.session_start) / 60)
        
        # Choose update style
        update_style = random.choice(["stats", "leaderboard", "hype", "milestone"])
        
        if update_style == "stats" and self.session_stats["total_frags"] > 0:
            return self._generate_stats_update(session_minutes)
            
        elif update_style == "leaderboard" and leaderboard:
            return self._generate_leaderboard_update(leaderboard)
            
        elif update_style == "milestone" and self.session_stats["milestones_reached"]:
            return self._generate_milestone_update()
            
        else:  # hype or fallback
            return self._generate_hype_update(session_minutes)
            
    def _generate_stats_update(self, session_minutes: int) -> str:
        """Generate statistics-focused update"""
        frags = self.session_stats["total_frags"]
        fraggers = len(self.session_stats["unique_fraggers"])
        
        updates = [
            f"💀🔥 MAGADOOM CARNAGE REPORT 🔥💀 {frags} Nazi Jefferies OBLITERATED by {fraggers} FRAGGERS in {session_minutes} min! RIP AND TEAR!",
            f"👹 FRAGFEST STATUS 👹 {frags} MAGAt scum TERMINATED! {fraggers} DOOM SLAYERS active! THE PURGE CONTINUES!",
            f"🩸 MAGADOOM KILLCOUNT 🩸 Time: {session_minutes}min | Bodies: {frags} | Slayers: {fraggers} | Status: ULTRA-VIOLENCE MODE!"
        ]
        
        if self.session_stats["multi_whacks"] > 0:
            updates.append(
                f"🔥 KILLING SPREE ALERT | {self.session_stats['multi_whacks']} multi-whacks this session! "
                f"{frags} total frags by {fraggers} fraggers!"
            )
            
        return random.choice(updates)
        
    def _generate_leaderboard_update(self, leaderboard: List[Dict]) -> str:
        """Generate leaderboard-focused update"""
        if not leaderboard:
            return "🏆 MAGADOOM LEADERBOARD | Empty! Start fragging to claim the throne!"
            
        # Get top 3
        top3 = []
        for i, entry in enumerate(leaderboard[:3]):
            if i == 0:
                top3.append(f"🥇{entry['user_id'][:10]}")
            elif i == 1:
                top3.append(f"🥈{entry['user_id'][:10]}")
            elif i == 2:
                top3.append(f"🥉{entry['user_id'][:10]}")
                
        leader = leaderboard[0]
        leader_name = leader['user_id'][:15]
        leader_score = leader['score']
        
        updates = [
            f"🏆 MAGADOOM LEADERS | {' '.join(top3)} | {leader_name} DOMINATES with {leader_score} XP!",
            f"👑 CURRENT CHAMPION: {leader_name} ({leader_score} XP) | Can anyone dethrone the king?",
            f"🎯 TOP WHACKERS | {' '.join(top3)} | Total carnage: {sum(e['score'] for e in leaderboard[:3])} XP!"
        ]
        
        return random.choice(updates)
        
    def _generate_milestone_update(self) -> str:
        """Generate milestone-focused update"""
        recent = self.session_stats["milestones_reached"][-1]
        mod_name, milestone = recent
        
        if milestone >= 1000:
            return f"🌋 LEGENDARY STATUS | {mod_name} has fragged {milestone} MAGAts! BOW TO THE FRAGLORD!"
        elif milestone >= 500:
            return f"💀 MILESTONE ALERT | {mod_name} reaches {milestone} frags! UNSTOPPABLE FORCE!"
        else:
            return f"🎯 ACHIEVEMENT UNLOCKED | {mod_name} hits {milestone} total whacks! Rising through the ranks!"
            
    def _generate_hype_update(self, session_minutes: int) -> str:
        """Generate hype/motivation update"""
        hype_messages = [
            "💀 MAGADOOM ACTIVE | RIP AND TEAR! Type /score to check your frags!",
            "🔥 THE FRAGGING CONTINUES | Who will be today's champion? /leaderboard to see rankings!",
            "👹 MAGADOOM ENGAGED | Timeouts = XP! Climb the ranks! /help for commands!",
            f"🎮 SESSION TIME: {session_minutes} MIN | Keep fragging MAGAts! Check /rank for your position!",
            "⚡ DOUBLE WHACK WINDOW: 5 SECONDS | Chain those timeouts for bonus glory!",
            "🏆 COMPETE FOR #1 | Every timeout counts! /score to track your progress!"
        ]
        
        # Add stream-specific callouts
        if session_minutes > 60:
            hype_messages.append(
                f"🔥 {session_minutes} MINUTES OF FRAGGING | Marathon moderation session! Who's still standing?"
            )
            
        return random.choice(hype_messages)
        
    def get_quick_stats(self) -> Dict:
        """Get quick statistics for other modules"""
        return {
            "session_frags": self.session_stats["total_frags"],
            "active_mods": len(self.session_stats["unique_fraggers"]),
            "multi_whacks": self.session_stats["multi_whacks"],
            "session_minutes": int((time.time() - self.session_start) / 60)
        }

# Singleton instance
status_announcer = StatusAnnouncer(update_interval=600)  # 10 minutes

def get_status_update() -> Optional[str]:
    """
    Main entry point for getting status updates.
    
    Returns:
        Status message if it's time, None otherwise
    """
    if status_announcer.should_post_update():
        return status_announcer.generate_status_update()
    return None
    
def record_activity(mod_id: str, duration: int, points: int):
    """Record fragging activity for statistics"""
    status_announcer.record_frag(mod_id, duration, points)
    
def check_forced_update(command: str) -> Optional[str]:
    """
    Check if user is requesting immediate status update.
    
    Args:
        command: User command text
        
    Returns:
        Status update if requested, None otherwise
    """
    if command.lower() in ['/status', '/update', '/stats']:
        return status_announcer.generate_status_update()
    return None