#!/usr/bin/env python3
"""
MAGADOOM Killing Spree Tracker
Tracks sustained fragging within 30-second windows for bonus XP and announcements.

Inspired by Unreal Tournament killing sprees:
- KILLING SPREE (3 frags in 30s)
- RAMPAGE (5 frags in 30s)  
- DOMINATING (7 frags in 30s)
- UNSTOPPABLE (10 frags in 30s)
- GODLIKE (15+ frags in 30s)
"""

import time
import os
import sys
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging

# Import activity control system
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))
try:
    from modules.infrastructure.activity_control.src.activity_control import is_enabled
except ImportError:
    # Fallback for testing - default to enabled
    def is_enabled(activity): return True

logger = logging.getLogger(__name__)

@dataclass
class SpreeEvent:
    """Represents a single frag in a spree"""
    mod_id: str
    target_id: str
    timestamp: float
    points: int

@dataclass 
class KillingSpree:
    """Tracks an active killing spree"""
    mod_id: str
    mod_name: str
    start_time: float
    last_frag_time: float
    frag_count: int = 0
    total_points: int = 0
    events: List[SpreeEvent] = field(default_factory=list)
    
    def is_active(self, current_time: float, window: float = 30.0) -> bool:
        """Check if spree is still active within window"""
        return (current_time - self.last_frag_time) <= window
    
    def add_frag(self, target_id: str, points: int, current_time: float):
        """Add a frag to the spree"""
        self.events.append(SpreeEvent(
            mod_id=self.mod_id,
            target_id=target_id,
            timestamp=current_time,
            points=points
        ))
        self.frag_count += 1
        self.total_points += points
        self.last_frag_time = current_time
    
    def get_spree_level(self) -> Tuple[str, int]:
        """Get current spree level name and bonus XP"""
        if self.frag_count >= 15:
            return "GODLIKE", 500
        elif self.frag_count >= 10:
            return "UNSTOPPABLE", 300
        elif self.frag_count >= 7:
            return "DOMINATING", 200
        elif self.frag_count >= 5:
            return "RAMPAGE", 100
        elif self.frag_count >= 3:
            return "KILLING SPREE", 50
        else:
            return None, 0


class SpreeTracker:
    """Manages killing sprees for all moderators"""
    
    def __init__(self, spree_window: float = 30.0):
        """
        Initialize spree tracker
        
        Args:
            spree_window: Time window in seconds for maintaining a spree (default 30s)
        """
        self.spree_window = spree_window
        self.active_sprees: Dict[str, KillingSpree] = {}
        self.spree_history: List[Dict] = []
        self.announcements: List[str] = []
        
        logger.info(f"🎯 SpreeTracker initialized with {spree_window}s window")
    
    def record_frag(self, mod_id: str, mod_name: str, target_id: str, 
                    points: int) -> Optional[Dict]:
        """
        Record a frag and check for spree status
        
        Returns:
            Dict with spree info if milestone reached, None otherwise
        """
        current_time = time.time()
        
        # Check for existing spree
        if mod_id in self.active_sprees:
            spree = self.active_sprees[mod_id]
            
            if spree.is_active(current_time, self.spree_window):
                # Continue the spree
                old_level, _ = spree.get_spree_level()
                spree.add_frag(target_id, points, current_time)
                new_level, bonus_xp = spree.get_spree_level()
                
                # Check if we hit a new milestone
                if new_level and new_level != old_level:
                    logger.info(f"🔥 {mod_name} achieved {new_level}! ({spree.frag_count} frags)")
                    
                    # Check if spree announcements are enabled
                    announcement = None
                    if is_enabled("gamification.whack_a_magat.spree_announcements"):
                        announcement = self._generate_announcement(mod_name, new_level, spree.frag_count)
                    
                    return {
                        "type": "spree_milestone",
                        "mod_id": mod_id,
                        "mod_name": mod_name,
                        "spree_level": new_level,
                        "frag_count": spree.frag_count,
                        "bonus_xp": bonus_xp,
                        "announcement": announcement
                    }
            else:
                # Spree ended, archive it
                self._archive_spree(spree)
                # Start new spree
                self._start_new_spree(mod_id, mod_name, target_id, points, current_time)
        else:
            # Start new spree
            self._start_new_spree(mod_id, mod_name, target_id, points, current_time)
        
        return None
    
    def _start_new_spree(self, mod_id: str, mod_name: str, target_id: str, 
                         points: int, current_time: float):
        """Start a new killing spree"""
        spree = KillingSpree(
            mod_id=mod_id,
            mod_name=mod_name,
            start_time=current_time,
            last_frag_time=current_time
        )
        spree.add_frag(target_id, points, current_time)
        self.active_sprees[mod_id] = spree
        logger.debug(f"🎯 Started new spree for {mod_name}")
    
    def _archive_spree(self, spree: KillingSpree):
        """Archive a completed spree"""
        if spree.frag_count >= 3:  # Only archive significant sprees
            level, bonus = spree.get_spree_level()
            self.spree_history.append({
                "mod_id": spree.mod_id,
                "mod_name": spree.mod_name,
                "start_time": spree.start_time,
                "end_time": spree.last_frag_time,
                "duration": spree.last_frag_time - spree.start_time,
                "frag_count": spree.frag_count,
                "total_points": spree.total_points,
                "spree_level": level,
                "bonus_xp": bonus
            })
            logger.info(f"📊 Archived {level} spree: {spree.mod_name} ({spree.frag_count} frags)")
    
    def _generate_announcement(self, mod_name: str, level: str, frag_count: int) -> str:
        """Generate spree announcement message"""
        announcements = {
            "KILLING SPREE": [
                f"🔥 {mod_name} is on a KILLING SPREE! {frag_count} MAGAts fragged!",
                f"💀 {mod_name} goes BERSERK! KILLING SPREE achieved!",
                f"🎯 {mod_name} can't be stopped! KILLING SPREE!"
            ],
            "RAMPAGE": [
                f"⚡ {mod_name} is on a RAMPAGE! {frag_count} frags and counting!",
                f"🔥🔥 {mod_name} goes NUCLEAR! RAMPAGE MODE ACTIVATED!",
                f"💥 RAMPAGE! {mod_name} is destroying MAGAts!"
            ],
            "DOMINATING": [
                f"👑 {mod_name} is DOMINATING! {frag_count} trolls silenced!",
                f"🏆 TOTAL DOMINATION by {mod_name}!",
                f"⚔️ {mod_name} DOMINATES the battlefield!"
            ],
            "UNSTOPPABLE": [
                f"🚀 {mod_name} is UNSTOPPABLE! {frag_count} frags!",
                f"🌟 UNSTOPPABLE FORCE! {mod_name} can't be contained!",
                f"💀💀💀 {mod_name} is an UNSTOPPABLE fragging machine!"
            ],
            "GODLIKE": [
                f"🌟🌟🌟 {mod_name} is GODLIKE! {frag_count} FRAGS! BOW DOWN!",
                f"⚡⚡⚡ GODLIKE! {mod_name} transcends mortality!",
                f"🔥🔥🔥 {mod_name} achieves GODLIKE STATUS! LEGENDARY!"
            ]
        }
        
        import random
        messages = announcements.get(level, [f"{mod_name} achieved {level}!"])
        return random.choice(messages)
    
    def get_active_sprees(self) -> List[Dict]:
        """Get all currently active sprees"""
        current_time = time.time()
        active = []
        
        for mod_id, spree in list(self.active_sprees.items()):
            if spree.is_active(current_time, self.spree_window):
                level, bonus = spree.get_spree_level()
                active.append({
                    "mod_id": mod_id,
                    "mod_name": spree.mod_name,
                    "frag_count": spree.frag_count,
                    "spree_level": level,
                    "time_remaining": self.spree_window - (current_time - spree.last_frag_time)
                })
            else:
                # Clean up expired sprees
                self._archive_spree(spree)
                del self.active_sprees[mod_id]
        
        return active
    
    def get_best_sprees(self, limit: int = 5) -> List[Dict]:
        """Get top sprees from history"""
        sorted_sprees = sorted(
            self.spree_history,
            key=lambda x: x['frag_count'],
            reverse=True
        )
        return sorted_sprees[:limit]


# Module-level singleton
_spree_tracker = SpreeTracker()

def track_frag(mod_id: str, mod_name: str, target_id: str, points: int) -> Optional[Dict]:
    """Track a frag for spree detection"""
    return _spree_tracker.record_frag(mod_id, mod_name, target_id, points)

def get_active_sprees() -> List[Dict]:
    """Get all active killing sprees"""
    return _spree_tracker.get_active_sprees()

def get_best_sprees(limit: int = 5) -> List[Dict]:
    """Get top killing sprees from history"""
    return _spree_tracker.get_best_sprees(limit)