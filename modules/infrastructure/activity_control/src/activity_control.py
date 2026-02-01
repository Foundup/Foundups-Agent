# -*- coding: utf-8 -*-
"""
Activity Router - Coordinates activity flow between DAEs based on breadcrumb signals.

Module: infrastructure/activity_control
WSP Reference: WSP 80 (DAE Pattern), WSP 77 (Agent Coordination), WSP 91 (Observability)
Status: Production

Architecture:
    1. Comment Engagement (base activity)
       ↓ rotation_complete breadcrumb
    2. Shorts Scheduling (if unlisted videos exist)
       ↓ scheduling_complete breadcrumb
    3. Video Indexing (Digital Twin learning)
       ↓ indexing_complete breadcrumb
    4. Live Chat Monitoring (if stream active)
       ↓ chat_idle breadcrumb → Return to 1.

Browser Availability:
    - Chrome (9222): Available when Move2Japan + UnDaoDu comments done
    - Edge (9223): Available when FoundUps + RavingANTIFA comments done
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
    """Activity types in priority order (lower = higher priority)."""
    COMMENT_ENGAGEMENT = 1  # Base activity
    SHORTS_SCHEDULING = 2   # Process unlisted shorts
    VIDEO_INDEXING = 3      # Digital Twin learning
    LIVE_CHAT = 4           # Stream monitoring
    IDLE = 99               # No pending activities


@dataclass
class BrowserState:
    """Track browser availability for activity routing."""
    chrome_available: bool = False
    edge_available: bool = False
    chrome_last_activity: Optional[str] = None
    edge_last_activity: Optional[str] = None
    last_updated: Optional[datetime] = None


@dataclass
class ActivityDecision:
    """Result of activity routing decision."""
    next_activity: ActivityType
    browser: Optional[str] = None  # "chrome" or "edge" or None
    reason: str = ""
    metadata: Optional[Dict[str, Any]] = None


class ActivityRouter:
    """
    Routes between activities based on breadcrumb signals and browser availability.

    Usage:
        router = ActivityRouter()
        decision = router.get_next_activity()

        if decision.next_activity == ActivityType.SHORTS_SCHEDULING:
            # Run shorts scheduler on decision.browser
            pass
    """

    def __init__(self):
        """Initialize activity router."""
        self.browser_state = BrowserState()
        self._telemetry = None
        logger.info("[ACTIVITY-ROUTER] Initialized")

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

    def check_rotation_complete(self, minutes: int = 5) -> bool:
        """
        Check if comment rotation completed recently.

        Args:
            minutes: Time window to check for rotation_complete breadcrumb

        Returns:
            True if rotation completed within time window
        """
        if not self.telemetry:
            return False

        try:
            recent = self.telemetry.get_recent_breadcrumbs(
                minutes=minutes,
                event_type="rotation_complete"
            )
            if recent:
                # Update browser availability from metadata
                metadata = recent[0].get("metadata", {})
                self.browser_state.chrome_available = metadata.get("browser_chrome_available", False)
                self.browser_state.edge_available = metadata.get("browser_edge_available", False)
                self.browser_state.last_updated = datetime.now()
                logger.info(f"[ACTIVITY-ROUTER] Rotation complete detected - Chrome: {self.browser_state.chrome_available}, Edge: {self.browser_state.edge_available}")
                return True
        except Exception as e:
            logger.warning(f"[ACTIVITY-ROUTER] Failed to check rotation: {e}")

        return False

    def check_shorts_pending(self) -> bool:
        """
        Check if there are unlisted shorts pending scheduling.

        Returns:
            True if shorts scheduling is enabled and videos may be pending
        """
        enabled = os.getenv("YT_SHORTS_SCHEDULING_ENABLED", "false").lower() in ("1", "true", "yes")
        if not enabled:
            return False

        # TODO: Check actual unlisted video count from scheduler
        # For now, return True if enabled to allow scheduling attempt
        return True

    def check_indexing_pending(self) -> bool:
        """
        Check if video indexing should run.

        Returns:
            True if indexing is enabled
        """
        return os.getenv("YT_VIDEO_INDEXING_ENABLED", "false").lower() in ("1", "true", "yes")

    def check_live_stream_active(self) -> bool:
        """
        Check if a live stream is currently active.

        Returns:
            True if live stream needs monitoring
        """
        # Check breadcrumb for live stream start
        if not self.telemetry:
            return False

        try:
            recent = self.telemetry.get_recent_breadcrumbs(
                minutes=30,  # Streams can be long
                event_type="live_stream_started"
            )
            if recent:
                # Check if stream ended
                ended = self.telemetry.get_recent_breadcrumbs(
                    minutes=30,
                    event_type="live_stream_ended"
                )
                # If started but not ended, stream is active
                if recent and not ended:
                    return True
                # If ended after started, stream is done
                if ended and recent:
                    # Compare timestamps
                    start_time = recent[0].get("timestamp", "")
                    end_time = ended[0].get("timestamp", "")
                    return start_time > end_time  # Active if started after last end
        except Exception as e:
            logger.warning(f"[ACTIVITY-ROUTER] Failed to check live stream: {e}")

        return False

    def get_next_activity(self) -> ActivityDecision:
        """
        Determine next activity based on breadcrumbs and browser availability.

        Priority order:
        1. Comments (base) - always returns here eventually
        2. Shorts Scheduling - if unlisted videos pending
        3. Video Indexing - Digital Twin learning
        4. Live Chat - if stream active

        Returns:
            ActivityDecision with next activity and recommended browser
        """
        # Check if rotation just completed
        rotation_done = self.check_rotation_complete()

        if not rotation_done:
            # Rotation not complete - continue with comments
            return ActivityDecision(
                next_activity=ActivityType.COMMENT_ENGAGEMENT,
                reason="Rotation not complete - continue comment processing",
                metadata={"rotation_complete": False}
            )

        # Rotation complete - check priority activities

        # Priority 2: Shorts Scheduling
        if self.check_shorts_pending():
            browser = "chrome" if self.browser_state.chrome_available else "edge"
            return ActivityDecision(
                next_activity=ActivityType.SHORTS_SCHEDULING,
                browser=browser,
                reason="Unlisted shorts may be pending scheduling",
                metadata={"browser_available": browser}
            )

        # Priority 3: Video Indexing
        if self.check_indexing_pending():
            browser = "chrome" if self.browser_state.chrome_available else "edge"
            return ActivityDecision(
                next_activity=ActivityType.VIDEO_INDEXING,
                browser=browser,
                reason="Video indexing enabled for Digital Twin learning",
                metadata={"browser_available": browser}
            )

        # Priority 4: Live Chat
        if self.check_live_stream_active():
            # Live chat should use Edge (FoundUps primary stream)
            return ActivityDecision(
                next_activity=ActivityType.LIVE_CHAT,
                browser="edge",
                reason="Live stream active - monitor chat",
                metadata={"stream_active": True}
            )

        # Nothing pending - return to idle (will cycle back to comments)
        return ActivityDecision(
            next_activity=ActivityType.IDLE,
            reason="All activities complete - cycle will restart",
            metadata={"all_complete": True}
        )

    def signal_browser_available(self, browser: str, activity: str = "unknown") -> None:
        """
        Signal that a browser is available after an activity completes.

        Args:
            browser: "chrome" or "edge"
            activity: Activity that just completed
        """
        if browser == "chrome":
            self.browser_state.chrome_available = True
            self.browser_state.chrome_last_activity = activity
        elif browser == "edge":
            self.browser_state.edge_available = True
            self.browser_state.edge_last_activity = activity

        self.browser_state.last_updated = datetime.now()

        # Emit breadcrumb for observability
        if self.telemetry:
            try:
                self.telemetry.store_breadcrumb(
                    source_dae="activity_router",
                    event_type="browser_available",
                    message=f"{browser} browser available after {activity}",
                    phase="ACTIVITY-ROUTING",
                    metadata={
                        "browser": browser,
                        "last_activity": activity,
                        "chrome_available": self.browser_state.chrome_available,
                        "edge_available": self.browser_state.edge_available,
                    }
                )
            except Exception as e:
                logger.warning(f"[ACTIVITY-ROUTER] Failed to emit browser_available: {e}")

        logger.info(f"[ACTIVITY-ROUTER] {browser} available after {activity}")

    def signal_activity_complete(self, activity: ActivityType, metadata: Optional[Dict] = None) -> None:
        """
        Signal that an activity has completed.

        Args:
            activity: Activity that completed
            metadata: Optional context about completion
        """
        event_type = f"{activity.name.lower()}_complete"

        if self.telemetry:
            try:
                self.telemetry.store_breadcrumb(
                    source_dae="activity_router",
                    event_type=event_type,
                    message=f"{activity.name} completed",
                    phase="ACTIVITY-ROUTING",
                    metadata=metadata or {}
                )
            except Exception as e:
                logger.warning(f"[ACTIVITY-ROUTER] Failed to emit {event_type}: {e}")

        logger.info(f"[ACTIVITY-ROUTER] {activity.name} complete")


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
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("\n=== Activity Router Test ===\n")

    router = ActivityRouter()

    # Test get_next_activity
    print("1. Checking next activity...")
    decision = router.get_next_activity()
    print(f"   Next: {decision.next_activity.name}")
    print(f"   Browser: {decision.browser}")
    print(f"   Reason: {decision.reason}")

    # Test browser signaling
    print("\n2. Signaling Chrome available...")
    router.signal_browser_available("chrome", "comment_engagement")

    print("\n3. Signaling Edge available...")
    router.signal_browser_available("edge", "comment_engagement")

    # Check decision again
    print("\n4. Checking next activity after browser signals...")
    decision = router.get_next_activity()
    print(f"   Next: {decision.next_activity.name}")
    print(f"   Browser: {decision.browser}")
    print(f"   Reason: {decision.reason}")

    print("\n=== Test Complete ===")
