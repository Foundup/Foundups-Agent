"""
Event Handler Module - WSP Compliant with MCP Integration
Handles timeout and ban events from YouTube Live Chat
Enhanced with MCP for instant announcements (no buffering!)
Split from message_processor.py for WSP compliance

NAVIGATION: Processes YouTube chat events (timeouts, bans, memberships).
-> Called by: message_processor.py::process_message()
-> Delegates to: timeout_announcer.py, chat_sender.py
-> Related: NAVIGATION.py -> MODULE_GRAPH["core_flows"]["message_processing_flow"]
-> Quick ref: NAVIGATION.py -> NEED_TO["handle timeout"]
"""

import logging
import time
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, List, Optional
from collections import deque
from dataclasses import dataclass
from modules.gamification.whack_a_magat.src.timeout_announcer import TimeoutManager

logger = logging.getLogger(__name__)

# Try to import MCP integration
try:
    from .mcp_youtube_integration import YouTubeMCPIntegration
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    logger.warning("MCP integration not available, using legacy system")


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
        
        # Thread pool for async MCP operations
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.mcp_loop = None
        self.mcp_thread = None
        
        # Initialize MCP if available
        self.mcp_integration = None
        if MCP_AVAILABLE:
            try:
                # Create MCP integration in separate thread with its own event loop
                self._init_mcp_thread()
                logger.info("[ROCKET] MCP integration enabled for instant announcements!")
            except Exception as e:
                logger.error(f"Failed to initialize MCP: {e}")
                self.mcp_integration = None
        
        # Batching system (only used if MCP unavailable)
        self.pending_announcements = deque()
        self.batch_threshold = 3  # Batch when 3+ announcements pending
        self.batch_window = 5.0  # Collect announcements for 5 seconds max
        self.last_batch_time = 0
        self.last_announcement_time = 0
        
        # Statistics
        self.total_batched = 0
        self.total_sent = 0
        
        if self.mcp_integration:
            logger.info("[TARGET] EventHandler initialized with MCP (no buffering!)")
        else:
            logger.info("[TARGET] EventHandler initialized with smart batching (legacy)")
        
    def _init_mcp_thread(self):
        """Initialize MCP in a separate thread with its own event loop"""
        def run_mcp_loop():
            # Create new event loop for this thread
            self.mcp_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.mcp_loop)
            
            # Initialize MCP integration
            self.mcp_integration = YouTubeMCPIntegration()
            
            # Connect to MCP servers
            self.mcp_loop.run_until_complete(self._init_mcp_async())
            
            # Keep loop running for future async calls
            self.mcp_loop.run_forever()
        
        # Start MCP thread
        self.mcp_thread = threading.Thread(target=run_mcp_loop, daemon=True)
        self.mcp_thread.start()
        
        # Wait a moment for initialization
        time.sleep(1)
    
    async def _init_mcp_async(self):
        """Initialize MCP connections asynchronously"""
        try:
            await self.mcp_integration.connect_all()
            logger.info("[OK] MCP servers connected successfully")
        except Exception as e:
            logger.error(f"Failed to connect MCP servers: {e}")
            self.mcp_integration = None
    
    def _call_mcp_async(self, coro):
        """Call an async MCP function from sync context"""
        if self.mcp_loop and self.mcp_integration:
            # Schedule coroutine on MCP event loop
            future = asyncio.run_coroutine_threadsafe(coro, self.mcp_loop)
            try:
                # Wait for result with timeout
                return future.result(timeout=2.0)
            except Exception as e:
                logger.error(f"MCP async call failed: {e}")
                return None
        return None
    
    def cleanup(self):
        """Cleanup MCP thread and resources"""
        # Reset session stats when stream ends
        try:
            from modules.gamification.whack_a_magat.src.whack import reset_all_sessions
            reset_all_sessions()
            logger.info("[OK] Session stats reset for all moderators")
        except Exception as e:
            logger.error(f"Error resetting session stats: {e}")
        
        if self.mcp_loop:
            self.mcp_loop.call_soon_threadsafe(self.mcp_loop.stop)
        if self.mcp_thread:
            self.mcp_thread.join(timeout=2)
        if self.executor:
            self.executor.shutdown(wait=False)
    
    def handle_timeout_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a timeout event and generate announcement."""
        target_name = event.get("target_name", "MAGAT")
        deleted_text = event.get("deleted_text", "")
        published_at = event.get("published_at", "")
        
        # CRITICAL: Filter out old buffered timeout events (>5 minutes old)
        if published_at:
            from datetime import datetime, timezone
            try:
                # Parse YouTube timestamp
                event_time = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                current_time = datetime.now(timezone.utc)
                age_seconds = (current_time - event_time).total_seconds()
                
                # Skip events older than 5 minutes (300 seconds)
                if age_seconds > 300:
                    logger.info(f"⏰ Skipping old buffered timeout event for {target_name} ({int(age_seconds)}s old)")
                    return {"skip": True, "reason": "old_buffered_timeout"}
            except Exception as e:
                logger.debug(f"Could not parse event timestamp: {e}")
                # Continue processing if we can't parse timestamp
        
        # Get moderator info from event
        mod_id = event.get("moderator_id", "owner")
        mod_name = event.get("moderator_name", "Move2Japan")
        
        # Log the timing for debugging multi-whack detection
        current_time = time.time()
        logger.info(f"⏰ TIMEOUT EVENT at {current_time:.2f} for {target_name} by {mod_name}")
        logger.info(f"   Published at: {published_at}")
        
        # Try to get actual duration from event, default to 10 seconds for basic timeout
        duration = event.get("duration_seconds", 10)  # Default 10s for message deletion
        
        # If MCP is available, use it for INSTANT processing
        if self.mcp_integration:
            try:
                # Process through MCP (no buffering!)
                mcp_event = {
                    "moderator_name": mod_name,
                    "moderator_id": mod_id,
                    "target_name": target_name,
                    "target_id": event.get("target_channel_id", ""),
                    "timestamp": event.get("published_at"),  # Pass the actual YouTube event timestamp!
                    "duration": int(duration)
                }
                
                # Call MCP async function using thread-safe method
                mcp_result = self._call_mcp_async(
                    self.mcp_integration.process_timeout_event(mcp_event)
                )
                
                if mcp_result and mcp_result.get("instant"):
                    # Use the announcement from MCP (it should come from timeout_announcer)
                    announcement = mcp_result.get('announcement')
                    
                    # If no announcement from MCP, build a basic one
                    if not announcement:
                        announcement = f"[TARGET] {mod_name} whacked {target_name}! "
                        announcement += f"+{mcp_result['points']} points"
                        
                        if mcp_result.get('combo_multiplier', 1) > 1:
                            announcement += f" (x{mcp_result['combo_multiplier']} combo!)"
                        
                        if mcp_result.get('is_multi_whack'):
                            announcement += f" [U+1F525] MULTI-WHACK x{mcp_result['total_whacks']}!"
                        
                        rank = mcp_result.get('rank')
                        if rank and isinstance(rank, (int, float)) and rank > 0:
                            announcement += f" [Rank #{rank}]"
                        elif rank and isinstance(rank, str):
                            announcement += f" [{rank}]"
                    
                    logger.info(f"[ROCKET] MCP instant announcement: {announcement}")
                    
                    return {
                        "type": "timeout_announcement",
                        "announcement": announcement,
                        "level_up": mcp_result.get('level_up'),
                        "stats": {
                            "points": mcp_result.get('points', 0),
                            "combo_multiplier": mcp_result.get('combo_multiplier', 1),
                            "is_multi_whack": mcp_result.get('is_multi_whack', False)
                        },
                        "skip": False,
                        "instant": True  # Flag for instant MCP processing
                    }
            except Exception as e:
                logger.error(f"MCP processing failed, falling back to legacy: {e}")
        
        # Fall back to legacy processing if MCP unavailable
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
        published_at = event.get("published_at", "")
        
        # CRITICAL: Filter out old buffered ban events (>5 minutes old)
        if published_at:
            from datetime import datetime, timezone
            try:
                # Parse YouTube timestamp
                event_time = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                current_time = datetime.now(timezone.utc)
                age_seconds = (current_time - event_time).total_seconds()
                
                # Skip events older than 5 minutes (300 seconds)
                if age_seconds > 300:
                    logger.info(f"⏰ Skipping old buffered ban event for {target_name} ({int(age_seconds)}s old)")
                    return {"skip": True, "reason": "old_buffered_ban"}
            except Exception as e:
                logger.debug(f"Could not parse event timestamp: {e}")
                # Continue processing if we can't parse timestamp
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
            logger.info(f"[TARGET] Batching mode: {len(self.pending_announcements)} pending, {time_since_last:.1f}s since last")
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
        
        logger.info(f"[U+1F4A5] Force flushing {len(self.pending_announcements)} pending announcements")
        return self._create_batch()
    
    def get_pending_count(self) -> int:
        """Get count of pending announcements."""
        return len(self.pending_announcements)
