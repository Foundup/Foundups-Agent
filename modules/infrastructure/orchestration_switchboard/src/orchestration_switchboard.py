# -*- coding: utf-8 -*-
"""
Orchestration Switchboard - Unified DAE Coordination Gate

Module: infrastructure/orchestration_switchboard
WSP Reference: WSP 77 (Agent Coordination), WSP 15 (MPS Priority), WSP 48 (Recursive Self-Improvement)
Status: Production

Architecture:
    All DAE Signals → OrchestrationSwitchboard (HOLD or EXECUTE) → Coordinated Execution → WRE Learning

    The switchboard receives "pings" from all DAEs and decides whether to:
    1. HOLD: Queue the signal for later execution (higher priority active)
    2. EXECUTE: Route to AI_Overseer for WSP 77 4-phase coordination

Signal Priority (WSP 15 MPS):
    P0 (Critical): oauth_reauth, live_stream_started
    P1 (High): rotation_complete, comment_processing
    P2 (Medium): linkedin_notification, tweet_trigger, shorts_scheduling
    P3 (Low): video_indexing, maintenance

WRE Integration (WSP 48):
    - Every signal execution stores outcome in PatternMemory
    - Successful patterns are recalled for future similar signals
    - Failed patterns trigger learning for improvement
"""

import sys
import io
import os
import logging
from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

# === UTF-8 ENFORCEMENT (WSP 90) ===
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        pass
# === END UTF-8 ENFORCEMENT ===


class SignalPriority(Enum):
    """WSP 15 MPS Priority Levels"""
    P0_CRITICAL = 0   # OAuth, live stream - ALWAYS wins
    P1_HIGH = 1       # Comment processing, rotation
    P2_MEDIUM = 2     # Social notifications, scheduling
    P3_LOW = 3        # Indexing, maintenance
    P4_IDLE = 4       # Background tasks


class SignalAction(Enum):
    """Switchboard decision actions"""
    EXECUTE = "execute"       # Proceed with signal
    HOLD = "hold"             # Queue for later
    ESCALATE = "escalate"     # Requires 0102 attention
    DROP = "drop"             # Signal superseded or invalid


@dataclass
class Signal:
    """Incoming signal from any DAE"""
    signal_type: str
    source_dae: str
    priority: SignalPriority
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    execution_id: str = field(default_factory=lambda: f"sig_{datetime.now().strftime('%Y%m%d%H%M%S%f')}")


@dataclass
class SwitchboardDecision:
    """Result of switchboard evaluation"""
    action: SignalAction
    signal: Signal
    reason: str
    recommended_browser: Optional[str] = None
    queue_position: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


# Signal type to priority mapping (WSP 15 compliant)
SIGNAL_PRIORITIES = {
    # P0 Critical - Always execute immediately
    "oauth_reauth": SignalPriority.P0_CRITICAL,
    "oauth_invalid_grant": SignalPriority.P0_CRITICAL,
    "live_stream_started": SignalPriority.P0_CRITICAL,
    "emergency_shutdown": SignalPriority.P0_CRITICAL,

    # P1 High - Core activity flow
    "rotation_complete": SignalPriority.P1_HIGH,
    "comment_processing": SignalPriority.P1_HIGH,
    "browser_available": SignalPriority.P1_HIGH,
    "oops_page_detected": SignalPriority.P1_HIGH,      # 2026-02-03: OOPS blocks browser activity
    "oops_page_recovered": SignalPriority.P1_HIGH,      # 2026-02-03: Browser available after OOPS recovery

    # P2 Medium - Social and scheduling
    "linkedin_notification": SignalPriority.P2_MEDIUM,
    "tweet_trigger": SignalPriority.P2_MEDIUM,
    "shorts_scheduling": SignalPriority.P2_MEDIUM,
    "shorts_scheduling_complete": SignalPriority.P2_MEDIUM,
    "party_requested": SignalPriority.P2_MEDIUM,
    "git_push_requested": SignalPriority.P2_MEDIUM,

    # P3 Low - Learning and indexing
    "video_indexing": SignalPriority.P3_LOW,
    "digital_twin_learning": SignalPriority.P3_LOW,
    "pattern_learning": SignalPriority.P3_LOW,

    # P4 Idle - Background maintenance
    "maintenance": SignalPriority.P4_IDLE,
    "cleanup": SignalPriority.P4_IDLE,
    "health_check": SignalPriority.P4_IDLE,
}


class OrchestrationSwitchboard:
    """
    Unified DAE Coordination Gate - "Ping and decide: HOLD or EXECUTE"

    Wires together:
        - BreadcrumbTelemetry (persistent state storage)
        - ActivityRouter (WSP 15 priority routing)
        - AIIntelligenceOverseer (WSP 77 4-phase coordination)
        - WREMasterOrchestrator (WSP 48 recursive self-improvement)

    Usage:
        switchboard = OrchestrationSwitchboard()

        # Any DAE can send signals
        decision = switchboard.receive_signal(
            signal_type="rotation_complete",
            source_dae="comment_engagement",
            metadata={"browser": "chrome", "channels_processed": 2}
        )

        if decision.action == SignalAction.EXECUTE:
            # Proceed with coordinated execution
            result = switchboard.execute_signal(decision.signal)
        elif decision.action == SignalAction.HOLD:
            # Signal queued, will be processed when priority allows
            print(f"Queued at position {decision.queue_position}")
    """

    def __init__(self, repo_root: Optional[Path] = None):
        """Initialize switchboard with all coordination components."""
        self.repo_root = repo_root or Path("O:/Foundups-Agent")
        self._telemetry = None
        self._router = None
        self._overseer = None
        self._wre = None

        # Signal queue for HOLD signals (priority queue)
        self.pending_queue: List[Signal] = []

        # Current active signal (only one at a time per priority level)
        self.active_signals: Dict[SignalPriority, Signal] = {}

        # Execution history for WRE learning
        self.execution_history: List[Dict[str, Any]] = []

        logger.info("[SWITCHBOARD] Initialized")

    @property
    def telemetry(self):
        """Lazy-load BreadcrumbTelemetry."""
        if self._telemetry is None:
            try:
                from modules.communication.livechat.src.breadcrumb_telemetry import get_breadcrumb_telemetry
                self._telemetry = get_breadcrumb_telemetry()
            except ImportError:
                logger.warning("[SWITCHBOARD] BreadcrumbTelemetry not available")
        return self._telemetry

    @property
    def router(self):
        """Lazy-load ActivityRouter."""
        if self._router is None:
            try:
                from modules.infrastructure.activity_control.src.activity_control import get_activity_router
                self._router = get_activity_router()
            except ImportError:
                logger.warning("[SWITCHBOARD] ActivityRouter not available")
        return self._router

    @property
    def overseer(self):
        """Lazy-load AIIntelligenceOverseer."""
        if self._overseer is None:
            try:
                from modules.ai_intelligence.ai_overseer.src.ai_overseer import AIIntelligenceOverseer
                self._overseer = AIIntelligenceOverseer(self.repo_root)
            except ImportError:
                logger.warning("[SWITCHBOARD] AIIntelligenceOverseer not available")
        return self._overseer

    @property
    def wre(self):
        """Lazy-load WREMasterOrchestrator."""
        if self._wre is None:
            try:
                from modules.infrastructure.wre_core.wre_master_orchestrator.src.wre_master_orchestrator import WREMasterOrchestrator
                self._wre = WREMasterOrchestrator()
            except ImportError:
                logger.warning("[SWITCHBOARD] WREMasterOrchestrator not available")
        return self._wre

    def receive_signal(
        self,
        signal_type: str,
        source_dae: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SwitchboardDecision:
        """
        Receive incoming signal from any DAE and decide: HOLD or EXECUTE.

        Args:
            signal_type: Type of signal (e.g., "rotation_complete", "party_requested")
            source_dae: Source DAE name (e.g., "comment_engagement", "livechat")
            metadata: Optional context data

        Returns:
            SwitchboardDecision with action (EXECUTE, HOLD, ESCALATE, DROP)
        """
        # Get signal priority
        priority = SIGNAL_PRIORITIES.get(signal_type, SignalPriority.P3_LOW)

        # Create signal object
        signal = Signal(
            signal_type=signal_type,
            source_dae=source_dae,
            priority=priority,
            metadata=metadata or {}
        )

        # Store breadcrumb for observability
        if self.telemetry:
            self.telemetry.store_breadcrumb(
                source_dae=source_dae,
                event_type=f"signal_received_{signal_type}",
                message=f"Signal received: {signal_type} from {source_dae}",
                phase="SWITCHBOARD",
                metadata={"priority": priority.name, **signal.metadata}
            )

        logger.info(f"[SWITCHBOARD] Received: {signal_type} from {source_dae} (Priority: {priority.name})")

        # P0 Critical signals ALWAYS execute immediately
        if priority == SignalPriority.P0_CRITICAL:
            return self._create_execute_decision(signal, "P0 Critical - immediate execution")

        # Check if higher priority signal is active
        for active_priority, active_signal in self.active_signals.items():
            if active_priority.value < priority.value:
                # Higher priority active - HOLD this signal
                self.pending_queue.append(signal)
                self.pending_queue.sort(key=lambda s: s.priority.value)
                queue_pos = self.pending_queue.index(signal) + 1

                return SwitchboardDecision(
                    action=SignalAction.HOLD,
                    signal=signal,
                    reason=f"Higher priority ({active_priority.name}) active: {active_signal.signal_type}",
                    queue_position=queue_pos,
                    metadata={"blocking_signal": active_signal.signal_type}
                )

        # Check ActivityRouter for additional routing logic
        if self.router:
            router_decision = self.router.get_next_activity()
            if router_decision.next_activity.name != "IDLE":
                # Router has a preferred next activity
                signal.metadata["router_recommendation"] = router_decision.next_activity.name
                signal.metadata["recommended_browser"] = router_decision.browser

        # No higher priority active - EXECUTE
        return self._create_execute_decision(signal, "No blocking signals - execute")

    def _create_execute_decision(self, signal: Signal, reason: str) -> SwitchboardDecision:
        """Create EXECUTE decision and mark signal as active."""
        self.active_signals[signal.priority] = signal

        # Get browser recommendation from router
        browser = None
        if self.router:
            decision = self.router.get_next_activity()
            browser = decision.browser

        return SwitchboardDecision(
            action=SignalAction.EXECUTE,
            signal=signal,
            reason=reason,
            recommended_browser=browser or signal.metadata.get("recommended_browser"),
            metadata={"execution_id": signal.execution_id}
        )

    def execute_signal(self, signal: Signal) -> Dict[str, Any]:
        """
        Execute signal via AI_Overseer with WRE learning.

        This is the core coordination method that:
        1. Maps signal to MissionType
        2. Coordinates via AI_Overseer (WSP 77 4-phase)
        3. Stores outcome in WRE for recursive learning

        Args:
            signal: Signal to execute

        Returns:
            Execution result with outcome data
        """
        start_time = datetime.now()
        result = {
            "execution_id": signal.execution_id,
            "signal_type": signal.signal_type,
            "source_dae": signal.source_dae,
            "started_at": start_time.isoformat(),
            "success": False,
            "outcome": None,
            "error": None
        }

        try:
            # Route to appropriate handler based on signal type
            handler_method = getattr(self, f"_handle_{signal.signal_type}", None)

            if handler_method:
                # Use specialized handler
                outcome = handler_method(signal)
            else:
                # Use generic AI_Overseer coordination
                outcome = self._handle_generic(signal)

            result["success"] = True
            result["outcome"] = outcome

        except Exception as e:
            result["error"] = str(e)
            logger.error(f"[SWITCHBOARD] Execution failed: {e}")

        finally:
            # Clear active signal
            if signal.priority in self.active_signals:
                del self.active_signals[signal.priority]

            # Calculate duration
            end_time = datetime.now()
            result["duration_ms"] = (end_time - start_time).total_seconds() * 1000
            result["completed_at"] = end_time.isoformat()

            # Store outcome for WRE learning (WSP 48)
            self._store_learning_outcome(signal, result)

            # Process pending queue
            self._process_pending_queue()

            # Store completion breadcrumb
            if self.telemetry:
                self.telemetry.store_breadcrumb(
                    source_dae="switchboard",
                    event_type=f"signal_executed_{signal.signal_type}",
                    message=f"Signal executed: {signal.signal_type} - {'SUCCESS' if result['success'] else 'FAILED'}",
                    phase="SWITCHBOARD",
                    metadata=result
                )

        return result

    def _handle_generic(self, signal: Signal) -> Dict[str, Any]:
        """Generic signal handler using AI_Overseer."""
        if not self.overseer:
            return {"status": "no_overseer", "message": "AI_Overseer not available"}

        # Map signal type to MissionType
        mission_type_map = {
            "rotation_complete": "ACTIVITY_ROUTING",
            "comment_processing": "COMMENT_PROCESSING",
            "linkedin_notification": "SOCIAL_MEDIA",
            "tweet_trigger": "SOCIAL_MEDIA",
            "shorts_scheduling": "SCHEDULING",
            "video_indexing": "VIDEO_INDEXING",
            "party_requested": "LIVE_STREAM",
            "git_push_requested": "GIT_PUSH",
            "oops_page_detected": "BROWSER_NAVIGATION",
            "oops_page_recovered": "ACTIVITY_ROUTING",
        }

        mission_type = mission_type_map.get(signal.signal_type, "CUSTOM")

        # TODO: Integrate with AI_Overseer.coordinate_mission() when method is available
        # For now, return acknowledgment
        return {
            "status": "acknowledged",
            "mission_type": mission_type,
            "signal": signal.signal_type,
            "metadata": signal.metadata
        }

    def _handle_oauth_reauth(self, signal: Signal) -> Dict[str, Any]:
        """Handle OAuth re-authentication signal."""
        credential_set = signal.metadata.get("credential_set", 1)
        browser = "chrome" if credential_set in [1, 2, 3, 4, 5] else "edge"

        return {
            "status": "oauth_reauth_triggered",
            "credential_set": credential_set,
            "browser": browser,
            "action": "Launch browser for OAuth consent"
        }

    def _handle_rotation_complete(self, signal: Signal) -> Dict[str, Any]:
        """Handle comment rotation complete signal."""
        # Signal browser availability to router
        browser = signal.metadata.get("browser", "chrome")
        if self.router:
            self.router.signal_browser_available(browser, "comment_engagement")

        # Check for next activity
        if self.router:
            next_activity = self.router.get_next_activity()
            return {
                "status": "rotation_processed",
                "browser_available": browser,
                "next_activity": next_activity.next_activity.name,
                "next_browser": next_activity.browser
            }

        return {"status": "rotation_processed", "browser_available": browser}

    def _handle_party_requested(self, signal: Signal) -> Dict[str, Any]:
        """Handle !party command signal from livechat."""
        user = signal.metadata.get("user", "unknown")
        click_count = signal.metadata.get("click_count", 10)

        return {
            "status": "party_queued",
            "user": user,
            "click_count": click_count,
            "action": "Execute party_reactor clicks"
        }

    def _handle_shorts_scheduling(self, signal: Signal) -> Dict[str, Any]:
        """Handle shorts scheduling signal."""
        channel_key = signal.metadata.get("channel_key", "move2japan")
        mode = signal.metadata.get("mode", "enhance")
        batch = signal.metadata.get("batch", False)

        # Determine browser based on channel
        # Chrome (9222): move2japan, undaodu
        # Edge (9223): foundups, ravingantifa
        if channel_key.lower() in ["move2japan", "undaodu"]:
            browser = "chrome"
            port = 9222
        else:
            browser = "edge"
            port = 9223

        return {
            "status": "shorts_scheduling_triggered",
            "channel_key": channel_key,
            "mode": mode,
            "batch": batch,
            "browser": browser,
            "port": port,
            "action": f"Run shorts scheduler for {channel_key} on {browser}:{port}"
        }

    def _handle_oops_page_detected(self, signal: Signal) -> Dict[str, Any]:
        """
        Handle OOPS page detection signal.

        2026-02-03: Intelligent OOPS page response.
        The switchboard tracks which browsers/channels are OOPS-blocked and
        recommends recovery strategy based on pattern history.

        Metadata expected:
            browser: "chrome" or "edge"
            channel_name: Target channel name
            channel_id: Target channel ID
            url: URL that triggered OOPS
            recovery_method: How the caller plans to recover
            attempt_count: Number of attempts so far
        """
        browser = signal.metadata.get("browser", "unknown")
        channel = signal.metadata.get("channel_name", "unknown")
        attempt = signal.metadata.get("attempt_count", 1)

        # Check WRE for historical OOPS patterns on this channel
        oops_history_count = 0
        if self.telemetry:
            oops_history_count = self.telemetry.get_event_count(
                "signal_received_oops_page_detected",
                minutes=60,
                source_dae=signal.source_dae,
            )

        # Intelligent decision: if OOPS happens repeatedly, recommend alternate browser
        recommendation = "account_switch"  # Default: try account switch
        if oops_history_count >= 3 and attempt >= 2:
            # Repeated OOPS on same browser - suggest alternate browser
            alt_browser = "edge" if browser == "chrome" else "chrome"
            recommendation = f"use_alternate_browser:{alt_browser}"
            logger.warning(
                f"[SWITCHBOARD] OOPS pattern detected: {channel} failed {oops_history_count}x "
                f"on {browser} in last hour - recommending {alt_browser}"
            )
        elif attempt >= 2:
            recommendation = "skip_channel"
            logger.warning(
                f"[SWITCHBOARD] OOPS recovery failed {attempt}x for {channel} on {browser} - recommending skip"
            )

        return {
            "status": "oops_detected",
            "browser": browser,
            "channel": channel,
            "attempt_count": attempt,
            "oops_history_count": oops_history_count,
            "recommendation": recommendation,
            "action": f"OOPS on {browser} for {channel} - recommend: {recommendation}"
        }

    def _handle_oops_page_recovered(self, signal: Signal) -> Dict[str, Any]:
        """
        Handle OOPS page recovery signal.

        2026-02-03: Signals browser is available again after OOPS recovery.
        Routes to activity router to determine next activity.
        """
        browser = signal.metadata.get("browser", "unknown")
        channel = signal.metadata.get("channel_name", "unknown")
        recovery_method = signal.metadata.get("recovery_method", "unknown")

        # Signal browser availability
        if self.router:
            self.router.signal_browser_available(browser, "oops_recovery")

        # Get next activity
        next_activity = None
        if self.router:
            decision = self.router.get_next_activity()
            next_activity = decision.next_activity.name

        logger.info(
            f"[SWITCHBOARD] OOPS recovered: {channel} on {browser} via {recovery_method} "
            f"- next activity: {next_activity}"
        )

        return {
            "status": "oops_recovered",
            "browser": browser,
            "channel": channel,
            "recovery_method": recovery_method,
            "browser_available": browser,
            "next_activity": next_activity,
        }

    def _handle_shorts_scheduling_complete(self, signal: Signal) -> Dict[str, Any]:
        """Handle shorts scheduling completion signal."""
        channel_key = signal.metadata.get("channel_key", "unknown")
        videos_processed = signal.metadata.get("videos_processed", 0)
        videos_scheduled = signal.metadata.get("videos_scheduled", 0)

        # Signal browser availability for next activity
        browser = signal.metadata.get("browser", "chrome")
        if self.router:
            self.router.signal_browser_available(browser, "shorts_scheduling")

        return {
            "status": "shorts_scheduling_complete",
            "channel_key": channel_key,
            "videos_processed": videos_processed,
            "videos_scheduled": videos_scheduled,
            "browser_available": browser
        }

    def _store_learning_outcome(self, signal: Signal, result: Dict[str, Any]) -> None:
        """Store execution outcome in WRE for recursive self-improvement (WSP 48)."""
        # Store in execution history
        self.execution_history.append({
            "signal_type": signal.signal_type,
            "source_dae": signal.source_dae,
            "priority": signal.priority.name,
            "success": result.get("success", False),
            "duration_ms": result.get("duration_ms", 0),
            "timestamp": signal.timestamp.isoformat()
        })

        # Limit history to last 1000 entries
        if len(self.execution_history) > 1000:
            self.execution_history = self.execution_history[-1000:]

        # Store in WRE PatternMemory if available
        if self.wre and hasattr(self.wre, 'sqlite_memory') and self.wre.sqlite_memory:
            try:
                import json
                from modules.infrastructure.wre_core.src.pattern_memory import SkillOutcome
                outcome = SkillOutcome(
                    execution_id=signal.execution_id,
                    skill_name=f"signal_{signal.signal_type}",
                    agent="switchboard",
                    timestamp=signal.timestamp.isoformat(),
                    input_context=json.dumps(signal.metadata),
                    output_result=json.dumps(result.get("outcome", {})),
                    success=result.get("success", False),
                    pattern_fidelity=1.0 if result.get("success") else 0.0,
                    outcome_quality=1.0 if result.get("success") else 0.0,
                    execution_time_ms=int(result.get("duration_ms", 0)),
                    step_count=1  # Switchboard signals are single-step
                )
                self.wre.sqlite_memory.store_outcome(outcome)
                logger.debug(f"[SWITCHBOARD] Stored learning outcome for {signal.signal_type}")
            except Exception as e:
                logger.warning(f"[SWITCHBOARD] Failed to store WRE outcome: {e}")

    def _process_pending_queue(self) -> None:
        """Process pending queue after signal completion."""
        if not self.pending_queue:
            return

        # Get highest priority pending signal
        next_signal = self.pending_queue[0]

        # Check if we can execute it now
        can_execute = True
        for active_priority in self.active_signals.keys():
            if active_priority.value < next_signal.priority.value:
                can_execute = False
                break

        if can_execute:
            self.pending_queue.pop(0)
            logger.info(f"[SWITCHBOARD] Auto-executing queued signal: {next_signal.signal_type}")
            self.execute_signal(next_signal)

    def get_status(self) -> Dict[str, Any]:
        """Get current switchboard status for observability."""
        return {
            "active_signals": {
                p.name: s.signal_type for p, s in self.active_signals.items()
            },
            "pending_queue": [
                {"type": s.signal_type, "priority": s.priority.name}
                for s in self.pending_queue
            ],
            "execution_history_count": len(self.execution_history),
            "components": {
                "telemetry": self._telemetry is not None,
                "router": self._router is not None,
                "overseer": self._overseer is not None,
                "wre": self._wre is not None
            }
        }

    def get_learning_stats(self) -> Dict[str, Any]:
        """Get WRE learning statistics for self-improvement tracking."""
        if not self.execution_history:
            return {"total_executions": 0, "success_rate": 0.0}

        total = len(self.execution_history)
        successes = sum(1 for e in self.execution_history if e.get("success", False))

        # Group by signal type
        by_type = {}
        for entry in self.execution_history:
            sig_type = entry.get("signal_type", "unknown")
            if sig_type not in by_type:
                by_type[sig_type] = {"total": 0, "success": 0, "avg_duration_ms": 0}
            by_type[sig_type]["total"] += 1
            if entry.get("success"):
                by_type[sig_type]["success"] += 1
            by_type[sig_type]["avg_duration_ms"] += entry.get("duration_ms", 0)

        # Calculate averages
        for sig_type in by_type:
            if by_type[sig_type]["total"] > 0:
                by_type[sig_type]["avg_duration_ms"] /= by_type[sig_type]["total"]
                by_type[sig_type]["success_rate"] = (
                    by_type[sig_type]["success"] / by_type[sig_type]["total"]
                )

        return {
            "total_executions": total,
            "success_rate": successes / total if total > 0 else 0.0,
            "by_signal_type": by_type
        }


# Singleton instance
_switchboard_instance = None


def get_orchestration_switchboard() -> OrchestrationSwitchboard:
    """Get or create singleton OrchestrationSwitchboard instance."""
    global _switchboard_instance
    if _switchboard_instance is None:
        _switchboard_instance = OrchestrationSwitchboard()
    return _switchboard_instance


# CLI test interface
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("\n=== Orchestration Switchboard Test ===\n")

    switchboard = OrchestrationSwitchboard()

    # Test 1: Receive P1 signal
    print("1. Receiving rotation_complete signal (P1)...")
    decision = switchboard.receive_signal(
        signal_type="rotation_complete",
        source_dae="comment_engagement",
        metadata={"browser": "chrome", "channels": ["undaodu", "move2japan"]}
    )
    print(f"   Decision: {decision.action.value}")
    print(f"   Reason: {decision.reason}")

    # Test 2: Receive P2 signal while P1 active (should HOLD)
    print("\n2. Receiving linkedin_notification signal (P2) while P1 active...")
    decision2 = switchboard.receive_signal(
        signal_type="linkedin_notification",
        source_dae="stream_discovery",
        metadata={"stream_url": "https://youtube.com/live/..."}
    )
    print(f"   Decision: {decision2.action.value}")
    print(f"   Reason: {decision2.reason}")
    if decision2.queue_position:
        print(f"   Queue position: {decision2.queue_position}")

    # Test 3: P0 Critical signal (should ALWAYS execute)
    print("\n3. Receiving oauth_reauth signal (P0 Critical)...")
    decision3 = switchboard.receive_signal(
        signal_type="oauth_reauth",
        source_dae="youtube_auth",
        metadata={"credential_set": 1}
    )
    print(f"   Decision: {decision3.action.value}")
    print(f"   Reason: {decision3.reason}")

    # Test 4: Get status
    print("\n4. Switchboard Status:")
    status = switchboard.get_status()
    print(f"   Active signals: {status['active_signals']}")
    print(f"   Pending queue: {len(status['pending_queue'])} signals")
    print(f"   Components: {status['components']}")

    print("\n=== Test Complete ===")
