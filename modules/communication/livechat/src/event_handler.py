"""
Event Handler Module - WSP Compliant
Handles timeout and ban events from YouTube Live Chat
Split from message_processor.py for WSP compliance
Includes smart batching for high-activity streams
"""

import logging
import time
from typing import Dict, Any, List, Optional
from collections import deque
from dataclasses import dataclass
from modules.gamification.whack_a_magat.src.timeout_announcer import TimeoutManager

logger = logging.getLogger(__name__)


@dataclass
class PendingAnnouncement:
    """Represents a pending timeout announcement."""
    moderator_name: str
    target_name: str
    points: int
    announcement: str
    timestamp: float
    combo_multiplier: int = 1


class EventHandler:
    """Handles moderation events (timeouts, bans) and generates announcements with smart batching."""
    
    def __init__(self, memory_dir: str = "memory"):
        self.timeout_manager = TimeoutManager(memory_dir)
        
        # Batching system for high-activity streams
        self.pending_announcements = deque()
        self.batch_threshold = 3  # Batch when 3+ announcements pending
        self.batch_window = 5.0  # Collect announcements for 5 seconds max
        self.last_batch_time = 0
        self.last_announcement_time = 0
        
        # Statistics
        self.total_batched = 0
        self.total_sent = 0
        
        logger.info("🎯 EventHandler initialized with smart batching")
        
    def handle_timeout_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a timeout event and generate announcement."""
        target_name = event.get("target_name", "MAGAT")
        deleted_text = event.get("deleted_text", "")
        published_at = event.get("published_at", "")
        
        # Get moderator info from event
        mod_id = event.get("moderator_id", "owner")
        mod_name = event.get("moderator_name", "Move2Japan")
        
        # Log the timing for debugging multi-whack detection
        current_time = time.time()
        logger.info(f"⏰ TIMEOUT EVENT at {current_time:.2f} for {target_name} by {mod_name}")
        logger.info(f"   Published at: {published_at}")
        
        # Try to get actual duration from event, default to 10 seconds for basic timeout
        duration = event.get("duration_seconds", 10)  # Default 10s for message deletion
        
        # Record the timeout and get announcement
        result = self.timeout_manager.record_timeout(
            mod_id=mod_id,
            mod_name=mod_name,
            target_id=event.get("target_channel_id", ""),
            target_name=target_name,
            duration=int(duration),  # Ensure it's an int
            reason="Message deleted",
            timestamp=published_at  # Pass the actual event timestamp for accurate multi-whack detection
        )
        
        # Check if we should batch announcements
        if self._should_batch():
            # Add to pending queue
            self.pending_announcements.append(PendingAnnouncement(
                moderator_name=mod_name,
                target_name=target_name,
                points=result.get("points_gained", 0),
                announcement=result.get("announcement"),
                timestamp=current_time,
                combo_multiplier=result.get("stats", {}).get("combo_multiplier", 1)
            ))
            
            # Get batched announcement if ready
            batched = self._get_batched_announcement()
            if batched:
                return {
                    "type": "timeout_announcement",
                    "announcement": batched,
                    "level_up": None,  # Skip individual level ups in batch
                    "stats": result.get("stats"),
                    "skip": False,
                    "is_batched": True
                }
            else:
                # Not ready to batch yet - skip this one for now
                return {
                    "type": "timeout_announcement",
                    "announcement": None,  # Don't send yet
                    "skip": True,
                    "queued": True
                }
        
        # Normal single announcement
        self.last_announcement_time = current_time
        return {
            "type": "timeout_announcement",
            "announcement": result.get("announcement"),
            "level_up": result.get("level_up"),
            "stats": result.get("stats"),
            "skip": False
        }
    
    def handle_ban_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a ban event and generate announcement."""
        target_name = event.get("target_name", "MAGAT")
        is_permanent = event.get("is_permanent", False)
        duration = event.get("duration_seconds", 0)
        published_at = event.get("published_at", "")
        
        # Ensure duration is an integer
        try:
            duration = int(duration) if duration else 0
        except (ValueError, TypeError):
            duration = 300  # Default 5 minutes
        
        # Get moderator info from event
        mod_id = event.get("moderator_id", "owner")
        mod_name = event.get("moderator_name", "Move2Japan")
        
        # Record the timeout/ban
        result = self.timeout_manager.record_timeout(
            mod_id=mod_id,
            mod_name=mod_name,
            target_id=event.get("target_channel_id", ""),
            target_name=target_name,
            duration=duration if not is_permanent else 86400,  # 24h for permanent
            reason="Banned" if is_permanent else "Timed out",
            timestamp=published_at  # Pass the actual event timestamp for accurate multi-whack detection
        )
        
        current_time = time.time()
        
        # Check if we should batch announcements (same logic as timeout)
        if self._should_batch():
            # Add to pending queue
            self.pending_announcements.append(PendingAnnouncement(
                moderator_name=mod_name,
                target_name=target_name,
                points=result.get("points_gained", 0),
                announcement=result.get("announcement"),
                timestamp=current_time,
                combo_multiplier=result.get("stats", {}).get("combo_multiplier", 1)
            ))
            
            # Get batched announcement if ready
            batched = self._get_batched_announcement()
            if batched:
                return {
                    "type": "ban_announcement",
                    "announcement": batched,
                    "level_up": None,  # Skip individual level ups in batch
                    "stats": result.get("stats"),
                    "skip": False,
                    "is_batched": True
                }
            else:
                # Not ready to batch yet - skip this one for now
                return {
                    "type": "ban_announcement",
                    "announcement": None,  # Don't send yet
                    "skip": True,
                    "queued": True
                }
        
        # Normal single announcement
        self.last_announcement_time = current_time
        return {
            "type": "ban_announcement",
            "announcement": result.get("announcement"),
            "level_up": result.get("level_up"),
            "stats": result.get("stats"),
            "skip": False
        }
    
    def get_timeout_manager(self) -> TimeoutManager:
        """Get the timeout manager instance for command handling."""
        return self.timeout_manager
    
    def _should_batch(self) -> bool:
        """Determine if we should batch announcements based on activity."""
        current_time = time.time()
        
        # Check if we're falling behind
        time_since_last = current_time - self.last_announcement_time
        
        # Start batching if:
        # 1. We have pending announcements already
        # 2. Or events are coming in faster than 1 per second
        if len(self.pending_announcements) > 0 or time_since_last < 1.0:
            logger.info(f"🎯 Batching mode: {len(self.pending_announcements)} pending, {time_since_last:.1f}s since last")
            return True
        
        return False
    
    def _get_batched_announcement(self) -> Optional[str]:
        """Get a batched announcement if ready."""
        current_time = time.time()
        queue_size = len(self.pending_announcements)
        
        # Don't batch if queue is too small (unless timeout exceeded)
        if queue_size < self.batch_threshold:
            # Check if oldest announcement is getting stale
            if queue_size > 0:
                oldest = self.pending_announcements[0]
                if current_time - oldest.timestamp > self.batch_window:
                    # Force batch due to timeout
                    logger.info(f"⏱️ Forcing batch due to timeout ({current_time - oldest.timestamp:.1f}s)")
                    return self._create_batch()
            return None
        
        # Queue is large enough - create batch
        return self._create_batch()
    
    def _create_batch(self) -> str:
        """Create a batched announcement from pending queue."""
        if not self.pending_announcements:
            return None
        
        # Take up to 10 announcements
        batch = []
        for _ in range(min(10, len(self.pending_announcements))):
            batch.append(self.pending_announcements.popleft())
        
        # Update stats
        self.total_batched += len(batch)
        self.total_sent += 1
        self.last_batch_time = time.time()
        
        # Single announcement - return as-is
        if len(batch) == 1:
            return batch[0].announcement
        
        # Multiple - create summary
        return self._format_batch(batch)
    
    def _format_batch(self, batch: List[PendingAnnouncement]) -> str:
        """Format multiple announcements into a single message."""
        # Group by moderator
        mod_frags = {}
        total_points = 0
        max_combo = 1
        
        for ann in batch:
            mod = ann.moderator_name
            if mod not in mod_frags:
                mod_frags[mod] = []
            mod_frags[mod].append(ann.target_name)
            total_points += ann.points
            max_combo = max(max_combo, ann.combo_multiplier)
        
        # Build summary
        if len(mod_frags) == 1:
            # Single moderator
            mod_name = list(mod_frags.keys())[0]
            targets = mod_frags[mod_name]
            
            if len(targets) <= 3:
                target_list = ", ".join(targets)
                if max_combo > 1:
                    return f"012 MEGA COMBO x{max_combo}! {mod_name} DEMOLISHED: {target_list} [+{total_points} pts]"
                else:
                    return f"012 RAMPAGE! {mod_name} fragged: {target_list} [+{total_points} pts]"
            else:
                return f"012 MASSACRE! {mod_name} fragged {len(targets)} MAGAts! [+{total_points} pts]"
        else:
            # Multiple moderators
            total_frags = sum(len(targets) for targets in mod_frags.values())
            mod_names = " & ".join(list(mod_frags.keys())[:3])  # Show first 3 mods
            
            if len(mod_frags) <= 3:
                return f"012 TEAM FRAG FEST! {mod_names} eliminated {total_frags} MAGAts! [+{total_points} pts total]"
            else:
                return f"012 MODERATION MAYHEM! {len(mod_frags)} mods fragged {total_frags} MAGAts! [+{total_points} pts total]"
    
    def force_flush(self) -> Optional[str]:
        """Force flush all pending announcements as a batch."""
        if not self.pending_announcements:
            return None
        
        logger.info(f"💥 Force flushing {len(self.pending_announcements)} pending announcements")
        return self._create_batch()
    
    def get_pending_count(self) -> int:
        """Get count of pending announcements."""
        return len(self.pending_announcements)