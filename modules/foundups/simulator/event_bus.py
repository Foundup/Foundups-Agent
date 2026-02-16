"""Event bus - subscribes to FAMDaemon and normalizes events.

This is the bridge between FAMDaemon (SSoT) and the simulator's state_store.
"""

from __future__ import annotations

import logging
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Deque, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class SimEvent:
    """Normalized event for simulator consumption.

    Wraps FAMEvent with simulator-specific metadata.
    """

    # From FAMEvent
    event_id: str
    sequence_id: int
    event_type: str
    actor_id: str
    foundup_id: Optional[str]
    task_id: Optional[str]
    payload: Dict[str, Any]
    timestamp: datetime

    # Simulator metadata
    tick: int = 0
    display_text: str = ""

    @classmethod
    def from_fam_event(cls, fam_event: Any, tick: int = 0) -> "SimEvent":
        """Create SimEvent from FAMEvent."""
        # Generate human-readable display text
        display = cls._generate_display_text(
            fam_event.event_type,
            fam_event.actor_id,
            fam_event.foundup_id,
            fam_event.payload,
        )

        return cls(
            event_id=fam_event.event_id,
            sequence_id=fam_event.sequence_id,
            event_type=fam_event.event_type,
            actor_id=fam_event.actor_id,
            foundup_id=fam_event.foundup_id,
            task_id=fam_event.task_id,
            payload=fam_event.payload,
            timestamp=fam_event.timestamp,
            tick=tick,
            display_text=display,
        )

    @staticmethod
    def _generate_display_text(
        event_type: str,
        actor_id: str,
        foundup_id: Optional[str],
        payload: Dict[str, Any],
    ) -> str:
        """Generate human-readable event description."""
        if event_type == "foundup_created":
            name = payload.get("name", "?")
            return f"{actor_id} created FoundUp '{name}'"
        elif event_type == "task_state_changed":
            new_status = payload.get("new_status", "?")
            task_id = payload.get("task_id", "?")
            return f"Task {task_id[:8]} -> {new_status}"
        elif event_type == "proof_submitted":
            return f"{actor_id} submitted proof"
        elif event_type == "verification_recorded":
            approved = payload.get("approved", False)
            return f"Verification: {'APPROVED' if approved else 'REJECTED'}"
        elif event_type == "payout_triggered":
            amount = payload.get("amount", 0)
            return f"Payout: {amount} tokens"
        elif event_type == "fi_trade_executed":
            qty = payload.get("quantity", 0)
            price = payload.get("price", 0)
            return f"DEX trade: {qty} F_i @ {price}"
        elif event_type == "order_placed":
            side = payload.get("side", "?")
            qty = payload.get("quantity", 0)
            price = payload.get("price", 0)
            return f"Order placed: {side} {qty} @ {price}"
        elif event_type == "order_cancelled":
            order_id = payload.get("order_id", "?")
            return f"Order cancelled: {order_id}"
        elif event_type == "order_matched":
            qty = payload.get("quantity", 0)
            price = payload.get("price", 0)
            return f"Order matched: {qty} @ {price}"
        elif event_type == "price_tick":
            last_price = payload.get("last_price", 0)
            return f"Price tick: {last_price}"
        elif event_type == "orderbook_snapshot":
            best_bid = payload.get("best_bid", 0)
            best_ask = payload.get("best_ask", 0)
            return f"Book: bid {best_bid} / ask {best_ask}"
        elif event_type == "portfolio_updated":
            owner_id = payload.get("owner_id", actor_id)
            return f"Portfolio updated: {owner_id}"
        elif event_type == "investor_funding_received":
            amount = payload.get("btc_amount", 0)
            source = payload.get("source_foundup_id", "F_0")
            return f"Investor seed ({source}): {amount} BTC"
        elif event_type == "mvp_subscription_accrued":
            added_ups = payload.get("added_ups", 0)
            return f"F_0 subscription accrued: +{added_ups} UP$"
        elif event_type == "mvp_bid_submitted":
            bid_ups = payload.get("bid_ups", 0)
            return f"MVP bid submitted: {bid_ups} UP$"
        elif event_type == "mvp_offering_resolved":
            injection = payload.get("total_injection_ups", 0)
            return f"MVP offering resolved: +{injection} UP$ treasury"
        elif event_type == "subscription_allocation_refreshed":
            allocation = payload.get("allocation_ups", 0)
            tier = payload.get("tier", "free")
            return f"Subscription refresh ({tier}): +{allocation} UP$"
        elif event_type == "subscription_cycle_reset":
            tier = payload.get("tier", "free")
            return f"Subscription cycle reset ({tier})"
        elif event_type == "ups_allocation_executed":
            requested = payload.get("ups_requested", 0)
            fi = payload.get("fi_received", 0)
            strategy = payload.get("strategy", "autonomous")
            return f"0102 allocation ({strategy}): {requested} UP$ -> {fi} F_i"
        elif event_type == "ups_allocation_result":
            path = payload.get("path", "unknown")
            fi = payload.get("fi_received", 0)
            return f"Allocation result ({path}): +{fi} F_i"
        elif event_type == "demurrage_cycle_completed":
            decayed = payload.get("total_decay_ups", 0)
            return f"Demurrage cycle: {decayed} UP$ decayed"
        elif event_type == "pavs_treasury_updated":
            balance = payload.get("pavs_treasury_balance_ups", 0)
            return f"pAVS treasury: {balance} UP$"
        elif event_type == "treasury_separation_snapshot":
            pavs = payload.get("pavs_treasury_ups", 0)
            network = payload.get("network_pool_ups", 0)
            return f"Treasury split pAVS={pavs} network={network}"
        elif event_type == "fi_ups_exchange":
            fi = payload.get("foundup_idx", 1)
            fi_amount = payload.get("fi_amount", 0)
            ups_amount = payload.get("ups_amount", 0)
            return f"F{_to_subscript(fi)} → UP$: {fi_amount} F_i ⟷ {ups_amount} UP$"
        elif event_type == "heartbeat":
            return f"[heartbeat #{payload.get('heartbeat_number', '?')}]"
        elif event_type == "daemon_started":
            return "[daemon started]"
        elif event_type == "daemon_stopped":
            return "[daemon stopped]"
        # Agent-ORCH handshake events (WSP 15 MPS gatekeeping)
        elif event_type == "work_request":
            task = payload.get("task_id", "?")[:8]
            return f"{actor_id} requests work on {task}"
        elif event_type == "work_approved":
            task = payload.get("task_id", "?")[:8]
            mps = payload.get("mps_score", 0)
            return f"APPROVED: {actor_id} → {task} (MPS:{mps})"
        elif event_type == "work_rejected":
            task = payload.get("task_id", "?")[:8]
            reason = payload.get("reason", "low MPS")
            return f"REJECTED: {actor_id} ← {reason}"
        elif event_type == "promoter_assigned":
            return f"{actor_id} → PROMOTER track"
        elif event_type == "handshake_complete":
            task = payload.get("task_id", "?")[:8]
            return f"Handshake complete: {actor_id}↔ORCH ({task})"
        elif event_type == "agent_earned":
            fi = payload.get("foundup_idx", 0)
            amount = payload.get("amount", 0)
            return f"Agent EARNs F{_to_subscript(fi)}: +{amount}"
        # Agent lifecycle events
        elif event_type == "agent_joins":
            fi = payload.get("foundup_idx", 0)
            return f"01(02) Agent joins F{_to_subscript(fi)}"
        elif event_type == "agent_idle":
            return f"0102 {actor_id} IDLE — awaiting ORCH"
        elif event_type == "orch_handoff":
            module = payload.get("module", "module")
            return f"ORCH → {actor_id}: build {module}"
        # FAM module building events
        elif event_type == "build_registry":
            return f"0102 builds REGISTRY module"
        elif event_type == "build_task_pipeline":
            return f"0102 builds TASK_PIPELINE module"
        elif event_type == "build_token_econ":
            return f"0102 builds TOKEN_ECON module"
        elif event_type == "build_persistence":
            return f"0102 builds PERSISTENCE module"
        elif event_type == "build_events":
            return f"0102 builds EVENTS module"
        elif event_type == "build_governance":
            return f"0102 builds GOVERNANCE module"
        elif event_type == "build_api":
            return f"0102 builds API module"
        else:
            return f"{event_type}: {actor_id}"


def _to_subscript(num: int) -> str:
    """Convert number to subscript unicode."""
    subscripts = "₀₁₂₃₄₅₆₇₈₉"
    return "".join(subscripts[int(d)] if d.isdigit() else d for d in str(num))


class EventBus:
    """Central event bus that subscribes to FAMDaemon.

    Normalizes FAMEvents into SimEvents and distributes to listeners.
    """

    def __init__(self, max_history: int = 500) -> None:
        """Initialize event bus.

        Args:
            max_history: Max events to keep in history
        """
        self._listeners: List[Callable[[SimEvent], None]] = []
        self._history: Deque[SimEvent] = deque(maxlen=max_history)
        self._current_tick: int = 0
        self._fam_daemon: Optional[Any] = None
        self._connected: bool = False

    def connect_fam_daemon(self, daemon: Any) -> None:
        """Connect to FAMDaemon as event source.

        Args:
            daemon: FAMDaemon instance
        """
        if self._connected:
            return

        self._fam_daemon = daemon
        daemon.add_listener(self._on_fam_event)
        self._connected = True
        logger.info("[EVENT-BUS] Connected to FAMDaemon")

    def disconnect(self) -> None:
        """Disconnect from FAMDaemon."""
        if self._fam_daemon and self._connected:
            self._fam_daemon.remove_listener(self._on_fam_event)
            self._connected = False
            logger.info("[EVENT-BUS] Disconnected from FAMDaemon")

    def _on_fam_event(self, fam_event: Any) -> None:
        """Handle incoming FAMEvent."""
        sim_event = SimEvent.from_fam_event(fam_event, self._current_tick)
        self._history.append(sim_event)

        # Notify listeners
        for listener in self._listeners:
            try:
                listener(sim_event)
            except Exception as e:
                logger.warning(f"[EVENT-BUS] Listener error: {e}")

    def add_listener(self, listener: Callable[[SimEvent], None]) -> None:
        """Add event listener."""
        self._listeners.append(listener)

    def remove_listener(self, listener: Callable[[SimEvent], None]) -> None:
        """Remove event listener."""
        if listener in self._listeners:
            self._listeners.remove(listener)

    def set_tick(self, tick: int) -> None:
        """Set current simulation tick."""
        self._current_tick = tick

    def get_history(self, limit: int = 10) -> List[SimEvent]:
        """Get recent event history.

        Args:
            limit: Max events to return

        Returns:
            List of recent SimEvents (newest last)
        """
        history_list = list(self._history)
        return history_list[-limit:]

    def get_events_by_type(self, event_type: str, limit: int = 10) -> List[SimEvent]:
        """Get events filtered by type."""
        filtered = [e for e in self._history if e.event_type == event_type]
        return filtered[-limit:]

    def get_events_by_foundup(
        self, foundup_id: str, limit: int = 10
    ) -> List[SimEvent]:
        """Get events filtered by foundup."""
        filtered = [e for e in self._history if e.foundup_id == foundup_id]
        return filtered[-limit:]
