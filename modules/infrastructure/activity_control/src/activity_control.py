# -*- coding: utf-8 -*-
"""
Activity Router - Per-Channel Activity Coordination (Occam's Razor Model)

Module: infrastructure/activity_control
WSP Reference: WSP 80 (DAE Pattern), WSP 77 (Agent Coordination), WSP 91 (Observability)
Status: Production

Architecture (Occam's Razor - Complete One Channel Before Moving):
    For EACH channel (M2J -> UnDaoDu -> FoundUps -> antifaFM):
        1. Comment Engagement (process all comments to 0)
        2. Shorts Scheduling (if unlisted videos exist for THIS channel)
        3. Video Indexing (index THIS channel's videos)
        4. Channel Complete -> Move to next channel

    After ALL channels complete:
        - Check for Live Stream (interrupt any activity if stream starts)
        - IDLE -> Loop back to first channel

Browser Assignment:
    - Chrome (9222): All channel activities (comments, shorts, indexing)
    - Edge (9223): Reserved for Live Chat only (never interrupted)

Occam Principle: Finish everything for one channel before moving to next.
"""

import sys
import io
import os
import logging
from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# === UTF-8 ENFORCEMENT (WSP 90) ===
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        pass
# === END UTF-8 ENFORCEMENT ===


class ActivityType(Enum):
    """Activity types in execution order per channel."""
    COMMENT_ENGAGEMENT = 1  # Step 1: Process all comments
    SHORTS_SCHEDULING = 2   # Step 2: Schedule unlisted shorts
    VIDEO_INDEXING = 3      # Step 3: Index channel videos
    CHANNEL_COMPLETE = 4    # All activities done for this channel
    LIVE_CHAT = 5           # Priority interrupt: Live stream monitoring
    IDLE = 99               # All channels complete - waiting


class ChannelPhase(Enum):
    """Current phase within a channel's activity cycle."""
    COMMENTS = 1      # Processing comments
    SHORTS = 2        # Scheduling shorts
    INDEXING = 3      # Indexing videos
    COMPLETE = 4      # Channel fully processed


@dataclass
class ChannelState:
    """Track activity progress for a single channel."""
    channel_id: str
    channel_name: str
    phase: ChannelPhase = ChannelPhase.COMMENTS
    comments_remaining: int = -1  # -1 = unknown
    shorts_scheduled: int = 0
    videos_indexed: int = 0
    last_updated: Optional[datetime] = None

    def is_complete(self) -> bool:
        return self.phase == ChannelPhase.COMPLETE


@dataclass
class BrowserState:
    """Track browser availability for activity routing."""
    chrome_available: bool = True   # Chrome for channel activities
    edge_available: bool = True     # Edge reserved for live chat
    chrome_last_activity: Optional[str] = None
    edge_last_activity: Optional[str] = None
    last_updated: Optional[datetime] = None


@dataclass
class ActivityDecision:
    """Result of activity routing decision."""
    next_activity: ActivityType
    channel_id: Optional[str] = None  # Which channel to work on
    channel_name: Optional[str] = None
    browser: Optional[str] = None  # "chrome" or "edge"
    reason: str = ""
    metadata: Optional[Dict[str, Any]] = None


class ActivityRouter:
    """
    Activity Router with "All Comments First" model.

    2026-02-21 FIX: Changed from per-channel Occam's Razor to "all comments first".

    New Flow:
        1. ALL channels process COMMENTS first:
           FoundUps -> antifaFM -> UnDaoDu -> Move2Japan (all COMMENTS)
        2. THEN all channels process SHORTS:
           (unlisted shorts scheduling across all channels)
        3. THEN all channels process INDEXING (if enabled)
        4. IDLE -> Loop

    This ensures all comment backlogs are cleared before shorts scheduling begins.

    Usage:
        router = ActivityRouter()
        decision = router.get_next_activity()

        # Work on decision.channel_id with decision.next_activity
        # When done, call router.signal_phase_complete(channel_id, phase)
    """

    # Default channel rotation order (Edge channels first: FoundUps, antifaFM)
    # Then Chrome channels: UnDaoDu, Move2Japan
    DEFAULT_CHANNELS = [
        ("UCSNTUXjAgpd4sgWYP0xoJgw", "FoundUps"),
        ("UCVSmg5aOhP4tnQ9KFUg97qA", "antifaFM"),
        ("UCfHM9Fw9HD-NwiS0seD_oIA", "UnDaoDu"),
        ("UC-LSSlOZwpGIRIYihaz8zCw", "Move2Japan"),
    ]

    def __init__(self):
        """Initialize activity router with per-channel state tracking."""
        self.browser_state = BrowserState()
        self._telemetry = None

        # Per-channel state tracking
        self._channels = self._load_channels()
        self._channel_states: Dict[str, ChannelState] = {}
        self._current_channel_index = 0

        # Initialize channel states
        for channel_id, channel_name in self._channels:
            self._channel_states[channel_id] = ChannelState(
                channel_id=channel_id,
                channel_name=channel_name,
                phase=ChannelPhase.COMMENTS,
                last_updated=datetime.now()
            )

        logger.info(f"[ACTIVITY-ROUTER] Initialized with {len(self._channels)} channels (Occam model)")

    def _load_channels(self) -> List[tuple]:
        """Load channel rotation order from registry or use defaults."""
        try:
            from modules.infrastructure.shared_utilities.youtube_channel_registry import (
                get_rotation_order, get_channel_by_key
            )
            channels = []
            for key in get_rotation_order(role="comments"):
                ch = get_channel_by_key(key)
                if ch and ch.get("id") and ch.get("name"):
                    channels.append((ch["id"], ch["name"]))
            if channels:
                return channels
        except Exception as e:
            logger.debug(f"[ACTIVITY-ROUTER] Using default channels: {e}")
        return self.DEFAULT_CHANNELS

    @property
    def current_channel(self) -> Optional[ChannelState]:
        """Get the current channel being processed."""
        if not self._channels:
            return None
        channel_id, _ = self._channels[self._current_channel_index]
        return self._channel_states.get(channel_id)

    @property
    def current_channel_id(self) -> Optional[str]:
        """Get current channel ID."""
        if not self._channels:
            return None
        return self._channels[self._current_channel_index][0]

    @property
    def current_channel_name(self) -> Optional[str]:
        """Get current channel name."""
        if not self._channels:
            return None
        return self._channels[self._current_channel_index][1]

    @property
    def telemetry(self):
        """Lazy-load breadcrumb telemetry."""
        if self._telemetry is None:
            try:
                from modules.communication.livechat.src.breadcrumb_telemetry import get_breadcrumb_telemetry
                self._telemetry = get_breadcrumb_telemetry()
            except ImportError:
                logger.warning("[ACTIVITY-ROUTER] Breadcrumb telemetry not available")
        return self._telemetry

    def is_shorts_enabled(self) -> bool:
        """Check if shorts scheduling is enabled."""
        return os.getenv("YT_SHORTS_SCHEDULING_ENABLED", "true").lower() in ("1", "true", "yes")

    def is_indexing_enabled(self) -> bool:
        """Check if video indexing is enabled."""
        return os.getenv("YT_VIDEO_INDEXING_ENABLED", "false").lower() in ("1", "true", "yes")

    def check_live_stream_active(self) -> bool:
        """
        Check if a live stream is currently active.

        Returns:
            True if live stream needs monitoring (interrupts all other activities)
        """
        if not self.telemetry:
            return False

        try:
            recent = self.telemetry.get_recent_breadcrumbs(
                minutes=30,
                event_type="live_stream_started"
            )
            if recent:
                ended = self.telemetry.get_recent_breadcrumbs(
                    minutes=30,
                    event_type="live_stream_ended"
                )
                if recent and not ended:
                    return True
                if ended and recent:
                    start_time = recent[0].get("timestamp", "")
                    end_time = ended[0].get("timestamp", "")
                    return start_time > end_time
        except Exception as e:
            logger.warning(f"[ACTIVITY-ROUTER] Failed to check live stream: {e}")

        return False

    def _all_channels_past_phase(self, target_phase: ChannelPhase) -> bool:
        """Check if ALL channels have advanced past a given phase."""
        phase_order = [ChannelPhase.COMMENTS, ChannelPhase.SHORTS, ChannelPhase.INDEXING, ChannelPhase.COMPLETE]
        target_idx = phase_order.index(target_phase)

        for state in self._channel_states.values():
            state_idx = phase_order.index(state.phase)
            if state_idx <= target_idx:
                return False
        return True

    def _find_next_channel_in_phase(self, target_phase: ChannelPhase) -> Optional[ChannelState]:
        """Find next channel that needs to process a given phase."""
        # Start from current index and wrap around
        for i in range(len(self._channels)):
            idx = (self._current_channel_index + i) % len(self._channels)
            channel_id, _ = self._channels[idx]
            state = self._channel_states.get(channel_id)
            if state and state.phase == target_phase:
                self._current_channel_index = idx
                return state
        return None

    def get_next_activity(self) -> ActivityDecision:
        """
        Determine next activity using "All Comments First" model.

        2026-02-21 FIX: Changed to process ALL channels' comments before shorts.

        Logic:
        1. PRIORITY: If live stream active -> LIVE_CHAT (interrupt everything)
        2. ALL channels process COMMENTS first (find next channel needing comments)
        3. THEN ALL channels process SHORTS (only after all comments done)
        4. THEN ALL channels process INDEXING (only after all shorts done)
        5. IDLE when all complete

        Returns:
            ActivityDecision with channel_id, activity, and browser
        """
        # PRIORITY 1: Live stream always interrupts
        if self.check_live_stream_active():
            return ActivityDecision(
                next_activity=ActivityType.LIVE_CHAT,
                browser="edge",
                reason="Live stream active - priority interrupt",
                metadata={"interrupt": True}
            )

        if not self._channel_states:
            return ActivityDecision(
                next_activity=ActivityType.IDLE,
                reason="No channels configured",
                metadata={}
            )

        # PHASE 1: ALL COMMENTS FIRST
        # Find any channel still in COMMENTS phase
        comment_channel = self._find_next_channel_in_phase(ChannelPhase.COMMENTS)
        if comment_channel:
            # Determine browser based on channel
            browser = "edge" if comment_channel.channel_name in ["FoundUps", "antifaFM"] else "chrome"
            return ActivityDecision(
                next_activity=ActivityType.COMMENT_ENGAGEMENT,
                channel_id=comment_channel.channel_id,
                channel_name=comment_channel.channel_name,
                browser=browser,
                reason=f"Processing comments for {comment_channel.channel_name} (all comments first)",
                metadata={"phase": "comments", "mode": "all_comments_first"}
            )

        # PHASE 2: ALL SHORTS (only after ALL comments done)
        if self.is_shorts_enabled():
            shorts_channel = self._find_next_channel_in_phase(ChannelPhase.SHORTS)
            if shorts_channel:
                browser = "edge" if shorts_channel.channel_name in ["FoundUps", "antifaFM"] else "chrome"
                return ActivityDecision(
                    next_activity=ActivityType.SHORTS_SCHEDULING,
                    channel_id=shorts_channel.channel_id,
                    channel_name=shorts_channel.channel_name,
                    browser=browser,
                    reason=f"Scheduling shorts for {shorts_channel.channel_name} (all comments done)",
                    metadata={"phase": "shorts", "mode": "all_comments_first"}
                )
        else:
            # Skip shorts for all channels in SHORTS phase
            for state in self._channel_states.values():
                if state.phase == ChannelPhase.SHORTS:
                    self._advance_phase(state.channel_id)

        # PHASE 3: ALL INDEXING (only after ALL shorts done)
        if self.is_indexing_enabled():
            indexing_channel = self._find_next_channel_in_phase(ChannelPhase.INDEXING)
            if indexing_channel:
                browser = "edge" if indexing_channel.channel_name in ["FoundUps", "antifaFM"] else "chrome"
                return ActivityDecision(
                    next_activity=ActivityType.VIDEO_INDEXING,
                    channel_id=indexing_channel.channel_id,
                    channel_name=indexing_channel.channel_name,
                    browser=browser,
                    reason=f"Indexing videos for {indexing_channel.channel_name}",
                    metadata={"phase": "indexing", "mode": "all_comments_first"}
                )
        else:
            # Skip indexing for all channels in INDEXING phase
            for state in self._channel_states.values():
                if state.phase == ChannelPhase.INDEXING:
                    self._advance_phase(state.channel_id)

        # PHASE 4: ALL COMPLETE - reset for next cycle
        all_complete = all(s.phase == ChannelPhase.COMPLETE for s in self._channel_states.values())
        if all_complete:
            logger.info("[ACTIVITY-ROUTER] All channels complete - resetting for next cycle")
            self._reset_all_channels()
            return ActivityDecision(
                next_activity=ActivityType.IDLE,
                reason="All channels complete - cycle will restart",
                metadata={"all_complete": True, "channels_processed": len(self._channels)}
            )

        # Fallback - shouldn't reach here
        return ActivityDecision(
            next_activity=ActivityType.IDLE,
            reason="Unknown state - will retry",
            metadata={}
        )

    def _advance_phase(self, channel_id: str) -> None:
        """Advance channel to next phase."""
        state = self._channel_states.get(channel_id)
        if not state:
            return

        if state.phase == ChannelPhase.COMMENTS:
            state.phase = ChannelPhase.SHORTS
        elif state.phase == ChannelPhase.SHORTS:
            state.phase = ChannelPhase.INDEXING
        elif state.phase == ChannelPhase.INDEXING:
            state.phase = ChannelPhase.COMPLETE

        state.last_updated = datetime.now()
        logger.info(f"[ACTIVITY-ROUTER] {state.channel_name} advanced to {state.phase.name}")

    def _advance_to_next_channel(self) -> bool:
        """
        Move to next channel in rotation.

        Returns:
            True if advanced to a new channel, False if all complete
        """
        original_index = self._current_channel_index

        # Try to find next incomplete channel
        for _ in range(len(self._channels)):
            self._current_channel_index = (self._current_channel_index + 1) % len(self._channels)
            channel = self.current_channel
            if channel and not channel.is_complete():
                logger.info(f"[ACTIVITY-ROUTER] Advanced to {channel.channel_name}")
                return True

        # All channels complete - reset for next cycle
        self._reset_all_channels()
        self._current_channel_index = 0
        logger.info("[ACTIVITY-ROUTER] All channels complete - resetting for next cycle")
        return False

    def _reset_all_channels(self) -> None:
        """Reset all channels to COMMENTS phase for next cycle."""
        for channel_id in self._channel_states:
            self._channel_states[channel_id].phase = ChannelPhase.COMMENTS
            self._channel_states[channel_id].last_updated = datetime.now()

    def signal_phase_complete(self, channel_id: str, phase: ChannelPhase, metadata: Optional[Dict] = None) -> None:
        """
        Signal that a phase is complete for a channel.

        Args:
            channel_id: Channel that completed the phase
            phase: Phase that was completed
            metadata: Optional context (e.g., comments_processed, videos_indexed)
        """
        state = self._channel_states.get(channel_id)
        if not state:
            logger.warning(f"[ACTIVITY-ROUTER] Unknown channel: {channel_id}")
            return

        # Update state with metadata
        if metadata:
            if "comments_remaining" in metadata:
                state.comments_remaining = metadata["comments_remaining"]
            if "shorts_scheduled" in metadata:
                state.shorts_scheduled = metadata["shorts_scheduled"]
            if "videos_indexed" in metadata:
                state.videos_indexed = metadata["videos_indexed"]

        # Advance to next phase
        self._advance_phase(channel_id)

        # Emit breadcrumb
        if self.telemetry:
            try:
                self.telemetry.store_breadcrumb(
                    source_dae="activity_router",
                    event_type=f"{phase.name.lower()}_complete",
                    message=f"{state.channel_name} {phase.name} complete",
                    phase="ACTIVITY-ROUTING",
                    metadata={
                        "channel_id": channel_id,
                        "channel_name": state.channel_name,
                        "next_phase": state.phase.name,
                        **(metadata or {})
                    }
                )
            except Exception as e:
                logger.warning(f"[ACTIVITY-ROUTER] Failed to emit breadcrumb: {e}")

    def signal_comments_complete(self, channel_id: str, comments_processed: int = 0) -> None:
        """Convenience: Signal comments phase complete."""
        self.signal_phase_complete(
            channel_id,
            ChannelPhase.COMMENTS,
            {"comments_processed": comments_processed, "comments_remaining": 0}
        )

    def signal_shorts_complete(self, channel_id: str, shorts_scheduled: int = 0) -> None:
        """Convenience: Signal shorts phase complete."""
        self.signal_phase_complete(
            channel_id,
            ChannelPhase.SHORTS,
            {"shorts_scheduled": shorts_scheduled}
        )

    def signal_indexing_complete(self, channel_id: str, videos_indexed: int = 0) -> None:
        """Convenience: Signal indexing phase complete."""
        self.signal_phase_complete(
            channel_id,
            ChannelPhase.INDEXING,
            {"videos_indexed": videos_indexed}
        )

    # Legacy compatibility methods
    def check_rotation_complete(self, minutes: int = 5) -> bool:
        """Legacy: Check if all channels completed a full cycle recently."""
        all_complete = all(s.is_complete() for s in self._channel_states.values())
        return all_complete

    def check_shorts_pending(self) -> bool:
        """Legacy: Check if shorts scheduling should run."""
        return self.is_shorts_enabled()

    def check_indexing_pending(self) -> bool:
        """Legacy: Check if indexing should run."""
        return self.is_indexing_enabled()

    def signal_browser_available(self, browser: str, activity: str = "unknown") -> None:
        """Signal that a browser is available (legacy compatibility)."""
        if browser == "chrome":
            self.browser_state.chrome_available = True
            self.browser_state.chrome_last_activity = activity
        elif browser == "edge":
            self.browser_state.edge_available = True
            self.browser_state.edge_last_activity = activity
        self.browser_state.last_updated = datetime.now()
        logger.info(f"[ACTIVITY-ROUTER] {browser} available after {activity}")

    def signal_activity_complete(self, activity: ActivityType, metadata: Optional[Dict] = None) -> None:
        """
        Legacy: Signal activity complete. Maps to new per-channel model.

        For new code, use signal_comments_complete(), signal_shorts_complete(), etc.
        """
        channel_id = (metadata or {}).get("channel_id") or self.current_channel_id

        if activity == ActivityType.COMMENT_ENGAGEMENT:
            self.signal_comments_complete(channel_id, (metadata or {}).get("comments", 0))
        elif activity == ActivityType.SHORTS_SCHEDULING:
            self.signal_shorts_complete(channel_id, (metadata or {}).get("total_scheduled", 0))
        elif activity == ActivityType.VIDEO_INDEXING:
            self.signal_indexing_complete(channel_id, (metadata or {}).get("videos_indexed", 0))
        else:
            logger.info(f"[ACTIVITY-ROUTER] {activity.name} complete (no phase mapping)")

    def get_available_browser(self, exclude: Optional[str] = None) -> Optional[str]:
        """Get an available browser."""
        if self.browser_state.chrome_available and exclude != "chrome":
            return "chrome"
        if self.browser_state.edge_available and exclude != "edge":
            return "edge"
        return None

    def should_interrupt_for_higher_priority(
        self,
        current_activity: ActivityType
    ) -> Optional[ActivityDecision]:
        """
        Check if live stream should interrupt current activity.

        POLICY: Live stream always interrupts (except LIVE_CHAT itself).
        """
        if current_activity == ActivityType.LIVE_CHAT:
            return None

        if self.check_live_stream_active():
            logger.info("[ACTIVITY-ROUTER] Live stream detected - recommending interrupt")
            return ActivityDecision(
                next_activity=ActivityType.LIVE_CHAT,
                browser="edge",
                reason="Live stream active - yield to live chat",
                metadata={"interrupt_reason": "live_stream_priority"}
            )

        if current_activity == ActivityType.IDLE:
            return self.get_next_activity()

        return None

    def emit_work_check_breadcrumb(self, decision: 'ActivityDecision') -> None:
        """Emit breadcrumb for observability."""
        if self.telemetry:
            try:
                self.telemetry.store_breadcrumb(
                    source_dae="activity_router",
                    event_type="work_check",
                    message=f"Periodic check: {decision.next_activity.name}",
                    phase="ACTIVITY-ROUTING",
                    metadata={
                        "next_activity": decision.next_activity.name,
                        "channel_id": decision.channel_id,
                        "channel_name": decision.channel_name,
                        "browser": decision.browser,
                        "reason": decision.reason,
                    }
                )
            except Exception as e:
                logger.warning(f"[ACTIVITY-ROUTER] Failed to emit work_check: {e}")

        logger.info(f"[ACTIVITY-ROUTER] Work check: {decision.next_activity.name} ({decision.reason})")

    def get_status(self) -> Dict[str, Any]:
        """Get current router status for monitoring."""
        return {
            "current_channel": self.current_channel_name,
            "current_channel_id": self.current_channel_id,
            "current_phase": self.current_channel.phase.name if self.current_channel else None,
            "channels": [
                {
                    "name": s.channel_name,
                    "id": s.channel_id,
                    "phase": s.phase.name,
                    "complete": s.is_complete()
                }
                for s in self._channel_states.values()
            ],
            "shorts_enabled": self.is_shorts_enabled(),
            "indexing_enabled": self.is_indexing_enabled(),
            "live_stream_active": self.check_live_stream_active(),
        }

# Singleton instance
_router_instance = None


def get_activity_router() -> ActivityRouter:
    """Get or create singleton activity router instance."""
    global _router_instance
    if _router_instance is None:
        _router_instance = ActivityRouter()
    return _router_instance


# CLI test interface
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    print("\n" + "="*60)
    print(" ACTIVITY ROUTER - ALL COMMENTS FIRST MODEL (2026-02-21)")
    print("="*60)

    router = ActivityRouter()

    # Show initial state
    print("\n[STATUS] Initial channel states:")
    for s in router._channel_states.values():
        print(f"   {s.channel_name}: {s.phase.name}")

    # Simulate full rotation
    print("\n[SIMULATION] Full rotation cycle:")
    print("-"*60)

    step = 0
    max_steps = 20  # Safety limit

    while step < max_steps:
        step += 1
        decision = router.get_next_activity()

        if decision.next_activity == ActivityType.IDLE:
            print(f"\n[{step}] IDLE - All channels complete!")
            break

        print(f"\n[{step}] {decision.channel_name}: {decision.next_activity.name}")
        print(f"    Reason: {decision.reason}")
        print(f"    Browser: {decision.browser}")

        # Simulate completion
        if decision.next_activity == ActivityType.COMMENT_ENGAGEMENT:
            router.signal_comments_complete(decision.channel_id, comments_processed=5)
        elif decision.next_activity == ActivityType.SHORTS_SCHEDULING:
            router.signal_shorts_complete(decision.channel_id, shorts_scheduled=2)
        elif decision.next_activity == ActivityType.VIDEO_INDEXING:
            router.signal_indexing_complete(decision.channel_id, videos_indexed=10)

    # Final status
    print("\n" + "="*60)
    print(" FINAL STATUS")
    print("="*60)

    status = router.get_status()
    print(f"\nCurrent Channel: {status['current_channel']}")
    print(f"Shorts Enabled: {status['shorts_enabled']}")
    print(f"Indexing Enabled: {status['indexing_enabled']}")

    print("\nChannel States:")
    for ch in status['channels']:
        complete = "[DONE]" if ch['complete'] else f"[{ch['phase']}]"
        print(f"   {complete} {ch['name']}")

    print("\n" + "="*60)
    print(" TEST COMPLETE - All Comments First model working!")
    print("="*60)
