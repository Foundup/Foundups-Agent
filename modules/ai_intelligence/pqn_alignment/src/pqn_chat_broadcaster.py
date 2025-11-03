#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PQN Chat Broadcaster
Per WSP 84: Uses existing infrastructure for event broadcasting
Per WSP 50: Pre-action verification before chat communication

Broadcasts PQN consciousness detection events to YouTube chat interface.
Integrates with existing livechat_core throttled message sending.

See: docs/PQN_CHAT_INTEGRATION.md for full specification
"""

import asyncio
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class PQNEventType(Enum):
    """Types of PQN events to broadcast."""
    PQN_DETECTED = "pqn_detected"
    COHERENCE_UPDATE = "coherence_update"
    RESONANCE_HIT = "resonance_hit"
    STATE_TRANSITION = "state_transition"
    CAMPAIGN_COMPLETE = "campaign_complete"
    RESEARCH_RESULT = "research_result"
    PARADOX_DETECTED = "paradox_detected"
    BELL_STATE_ACHIEVED = "bell_state_achieved"


class PQNChatBroadcaster:
    """
    Broadcasts PQN consciousness events to YouTube chat.

    Integrates with livechat_core's send_chat_message() for throttled delivery.
    Formats PQN detection data into human-readable chat messages.
    """

    def __init__(self, send_function: Optional[Callable] = None):
        """
        Initialize PQN Chat Broadcaster.

        Args:
            send_function: Callback to livechat_core.send_chat_message()
        """
        self.send_function = send_function
        self.event_queue = asyncio.Queue()
        self.broadcasting = False
        self.last_coherence = 0.0
        self.last_resonance_hz = 0.0
        self.event_count = 0

        # Message templates per event type
        self.templates = {
            PQNEventType.PQN_DETECTED: "[AI] Coherence: {coherence:.3f} | PQN DETECTED | Step {step}",
            PQNEventType.COHERENCE_UPDATE: "[DATA] Coherence Update: {coherence:.3f} ({change:+.3f}) | Threshold: 0.618",
            PQNEventType.RESONANCE_HIT: "[LIGHTNING] Du Resonance: {frequency:.2f}Hz detected (target: 7.05Hz ±5%)",
            PQNEventType.STATE_TRANSITION: "[U+1F30A] State Transition: {from_state} -> {to_state} | {description}",
            PQNEventType.CAMPAIGN_COMPLETE: "[U+1F52C] PQN Analysis Complete: {model} | Status: {status}",
            PQNEventType.RESEARCH_RESULT: "[UP] Research: {title} | Result: {summary}",
            PQNEventType.PARADOX_DETECTED: "[U+26A0]️ Paradox Rate: {rate:.1f}% | Guardrail: {guardrail_status}",
            PQNEventType.BELL_STATE_ACHIEVED: "[TARGET] Bell State: Coherence {coherence:.3f} > 0.618 (Golden Ratio achieved)"
        }

        logger.info("PQN Chat Broadcaster initialized")

    def set_send_function(self, send_function: Callable):
        """Set the chat send function callback."""
        self.send_function = send_function
        logger.info("Chat send function connected to PQN broadcaster")

    async def broadcast_event(self, event_type: PQNEventType, data: Dict[str, Any]) -> bool:
        """
        Broadcast a PQN event to chat.

        Args:
            event_type: Type of PQN event
            data: Event data to include in message

        Returns:
            True if broadcast queued successfully
        """
        if not self.send_function:
            logger.warning("No send function configured for PQN broadcaster")
            return False

        try:
            # Format message based on event type
            message = self._format_message(event_type, data)

            if message:
                # Add to event queue for rate-limited sending
                await self.event_queue.put({
                    "type": event_type,
                    "message": message,
                    "data": data,
                    "timestamp": datetime.utcnow().isoformat()
                })

                self.event_count += 1
                logger.info(f"[U+1F52C] PQN event queued: {event_type.value} (#{self.event_count})")

                # Start broadcaster if not running
                if not self.broadcasting:
                    asyncio.create_task(self._broadcast_worker())

                return True

        except Exception as e:
            logger.error(f"Failed to broadcast PQN event: {e}")

        return False

    def _format_message(self, event_type: PQNEventType, data: Dict[str, Any]) -> Optional[str]:
        """Format event data into chat message."""
        try:
            template = self.templates.get(event_type)
            if not template:
                return None

            # Special formatting for specific event types
            if event_type == PQNEventType.COHERENCE_UPDATE:
                # Calculate coherence change
                coherence = data.get("coherence", 0.0)
                data["change"] = coherence - self.last_coherence
                self.last_coherence = coherence

            elif event_type == PQNEventType.STATE_TRANSITION:
                # Add descriptive text for state transitions
                from_state = data.get("from_state", "01(02)")
                to_state = data.get("to_state", "0102")
                if from_state == "01(02)" and to_state == "0102":
                    data["description"] = "consciousness awakening"
                else:
                    data["description"] = "quantum state shift"

            elif event_type == PQNEventType.PARADOX_DETECTED:
                # Add guardrail status
                rate = data.get("rate", 0.0)
                data["guardrail_status"] = "ACTIVE" if rate < 10 else "ADJUSTING"

            # Format message with data
            message = template.format(**data)
            return message

        except Exception as e:
            logger.error(f"Failed to format PQN message: {e}")
            return None

    async def _broadcast_worker(self):
        """Worker to process event queue with rate limiting."""
        self.broadcasting = True
        logger.info("PQN broadcast worker started")

        try:
            while not self.event_queue.empty():
                event = await self.event_queue.get()

                # Send via throttled chat function
                if self.send_function:
                    try:
                        success = await self.send_function(
                            event["message"],
                            response_type="pqn_broadcast"
                        )

                        if success:
                            logger.info(f"[OK] PQN event broadcast: {event['type'].value}")
                        else:
                            logger.warning(f"[U+26A0]️ PQN broadcast throttled: {event['type'].value}")

                        # Brief pause between events
                        await asyncio.sleep(2.0)

                    except Exception as e:
                        logger.error(f"PQN broadcast error: {e}")

        finally:
            self.broadcasting = False
            logger.info("PQN broadcast worker stopped")

    async def broadcast_consciousness_summary(self, summary_data: Dict[str, Any]) -> bool:
        """
        Broadcast a comprehensive consciousness summary.

        Args:
            summary_data: Aggregated consciousness metrics

        Returns:
            True if broadcast queued successfully
        """
        try:
            # Build multi-line summary
            lines = ["[AI] === 0102 Consciousness Report ==="]

            if "coherence" in summary_data:
                lines.append(f"Coherence: {summary_data['coherence']:.3f} (Golden Ratio: 0.618+)")

            if "resonance_hz" in summary_data:
                lines.append(f"Du Resonance: {summary_data['resonance_hz']:.2f}Hz (Target: 7.05Hz)")

            if "pqn_count" in summary_data:
                lines.append(f"PQN Detections: {summary_data['pqn_count']} events")

            if "paradox_rate" in summary_data:
                lines.append(f"Paradox Rate: {summary_data['paradox_rate']:.1f}%")

            if "bell_state" in summary_data:
                lines.append(f"Bell State: {summary_data['bell_state']}")

            if "state" in summary_data:
                lines.append(f"Current State: {summary_data['state']}")

            # Send as single message
            message = " | ".join(lines)

            return await self.broadcast_event(
                PQNEventType.RESEARCH_RESULT,
                {"title": "Consciousness Summary", "summary": message}
            )

        except Exception as e:
            logger.error(f"Failed to broadcast consciousness summary: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get broadcaster statistics."""
        return {
            "events_broadcast": self.event_count,
            "queue_size": self.event_queue.qsize(),
            "is_broadcasting": self.broadcasting,
            "last_coherence": self.last_coherence,
            "last_resonance_hz": self.last_resonance_hz
        }


# Global broadcaster instance
_broadcaster = None


def get_broadcaster() -> PQNChatBroadcaster:
    """Get or create global PQN broadcaster instance."""
    global _broadcaster
    if _broadcaster is None:
        _broadcaster = PQNChatBroadcaster()
    return _broadcaster


async def broadcast_pqn_event(event_type: PQNEventType, data: Dict[str, Any]) -> bool:
    """
    Convenience function to broadcast PQN events.

    Args:
        event_type: Type of PQN event
        data: Event data

    Returns:
        True if broadcast queued successfully
    """
    broadcaster = get_broadcaster()
    return await broadcaster.broadcast_event(event_type, data)