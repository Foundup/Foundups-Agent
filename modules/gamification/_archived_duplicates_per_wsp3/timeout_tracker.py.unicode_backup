"""
Timeout Tracker Module - Whack-a-MAGA Deduplication and Tracking
WSP-Compliant: Handles ban/timeout deduplication and frag tracking

This module belongs in whack_a_magat as it's part of the gamification system.
Separates concerns: chat_poller detects events, this module tracks them.
"""

import time
import logging
from typing import Dict, Set, Optional, Tuple
from collections import defaultdict

logger = logging.getLogger(__name__)


class TimeoutTracker:
    """Tracks timeouts/bans with deduplication and multi-whack detection."""
    
    def __init__(self):
        # Deduplication tracking
        self.seen_event_ids: Set[str] = set()
        self.event_dedup_window: Dict[str, float] = {}
        self.dedup_window_seconds = 2  # Duplicates within 2 seconds
        
        # Multi-whack tracking (for detecting spam bans)
        self.recent_targets: Dict[str, Set[str]] = {}  # mod_key -> set of target names
        self.multi_whack_window = 10  # Track frags within 10-second windows
        
        # Frag statistics
        self.mod_frag_counts: Dict[str, int] = defaultdict(int)
        self.mod_names: Dict[str, str] = {}  # mod_id -> display name
        
        logger.info("TimeoutTracker initialized for whack-a-MAGA gamification")
    
    def process_ban_event(self, 
                         event_id: str,
                         mod_id: str, 
                         mod_name: str,
                         target_id: str,
                         target_name: str,
                         timestamp: str,
                         duration_seconds: int = 0,
                         is_permanent: bool = False) -> Tuple[bool, Optional[Dict]]:
        """
        Process a ban/timeout event with deduplication.
        
        Returns:
            Tuple of (is_valid_frag, event_info)
            - is_valid_frag: True if this is a new frag (not duplicate)
            - event_info: Dict with processed event details or None if duplicate
        """
        current_time = time.time()
        
        # Check for duplicate by event ID
        if event_id and event_id in self.seen_event_ids:
            logger.debug(f"⏭️ Duplicate event ID: {event_id}")
            return False, None
        
        # Create deduplication key (mod:target:timestamp)
        dedup_key = f"{mod_id}:{target_id}:{timestamp}"
        
        # Check for duplicate by key (same mod/target/time within window)
        if dedup_key in self.event_dedup_window:
            time_diff = current_time - self.event_dedup_window[dedup_key]
            if time_diff < self.dedup_window_seconds:
                logger.debug(f"⏭️ Duplicate ban within {time_diff:.1f}s: {mod_name} → {target_name}")
                return False, None
        
        # This is a valid new frag!
        if event_id:
            self.seen_event_ids.add(event_id)
        self.event_dedup_window[dedup_key] = current_time
        
        # Clean old dedup entries (older than 60 seconds)
        self.event_dedup_window = {
            k: v for k, v in self.event_dedup_window.items() 
            if current_time - v < 60
        }
        
        # Track moderator name
        self.mod_names[mod_id] = mod_name
        
        # Increment frag count
        self.mod_frag_counts[mod_id] += 1
        
        # Track for multi-whack detection
        window_key = f"{mod_id}:{int(current_time // self.multi_whack_window)}"
        if window_key not in self.recent_targets:
            self.recent_targets[window_key] = set()
        self.recent_targets[window_key].add(target_name)
        
        # Clean old multi-whack windows
        cutoff_window = int((current_time - 60) // self.multi_whack_window)
        self.recent_targets = {
            k: v for k, v in self.recent_targets.items()
            if int(k.split(':')[1]) > cutoff_window
        }
        
        # Determine ban type
        if is_permanent:
            ban_type = "PERMABAN"
        elif duration_seconds >= 86400:
            ban_type = f"{duration_seconds//86400}d ban"
        elif duration_seconds >= 3600:
            ban_type = f"{duration_seconds//3600}h ban"
        elif duration_seconds >= 60:
            ban_type = f"{duration_seconds//60}m timeout"
        else:
            ban_type = f"{duration_seconds}s timeout"
        
        # Check if this is part of a multi-whack
        unique_targets = len(self.recent_targets[window_key])
        is_multi_whack = unique_targets > 1
        
        # Log the frag
        frag_msg = f"🎯 FRAG #{self.mod_frag_counts[mod_id]}: {mod_name} → {target_name} ({ban_type})"
        if is_multi_whack:
            frag_msg += f" | 🔥 MULTI-WHACK x{unique_targets}!"
        logger.info(frag_msg)
        
        # Debug: Show all moderator frag counts
        mod_summary = []
        for mid, count in self.mod_frag_counts.items():
            name = self.mod_names.get(mid, mid[:8])
            mod_summary.append(f"{name}:{count}")
        if mod_summary:
            logger.info(f"📊 Leaderboard: {' | '.join(mod_summary)}")
        
        return True, {
            "mod_id": mod_id,
            "mod_name": mod_name,
            "target_id": target_id,
            "target_name": target_name,
            "duration": duration_seconds,
            "is_permanent": is_permanent,
            "ban_type": ban_type,
            "frag_count": self.mod_frag_counts[mod_id],
            "is_multi_whack": is_multi_whack,
            "multi_whack_count": unique_targets if is_multi_whack else 1
        }
    
    def get_mod_stats(self, mod_id: str) -> Dict:
        """Get statistics for a specific moderator."""
        return {
            "mod_id": mod_id,
            "mod_name": self.mod_names.get(mod_id, "Unknown"),
            "frag_count": self.mod_frag_counts.get(mod_id, 0)
        }
    
    def get_leaderboard(self) -> list:
        """Get frag leaderboard for all moderators."""
        leaderboard = []
        for mod_id, frag_count in self.mod_frag_counts.items():
            leaderboard.append({
                "mod_id": mod_id,
                "mod_name": self.mod_names.get(mod_id, "Unknown"),
                "frag_count": frag_count
            })
        
        # Sort by frag count descending
        leaderboard.sort(key=lambda x: x["frag_count"], reverse=True)
        return leaderboard
    
    def reset_stats(self):
        """Reset all tracking statistics (for testing)."""
        self.seen_event_ids.clear()
        self.event_dedup_window.clear()
        self.recent_targets.clear()
        self.mod_frag_counts.clear()
        logger.info("TimeoutTracker stats reset")