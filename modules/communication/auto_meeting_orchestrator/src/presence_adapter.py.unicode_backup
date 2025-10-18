"""
AMO Presence Adapter

Small adapter that subscribes to the Presence Aggregator and feeds
normalized updates into the Auto Meeting Orchestrator.

WSP: Functional distribution preserved. Aggregation stays in
modules/aggregation; AMO consumes normalized events via this thin shim.
"""

import asyncio
import logging
from typing import List

from modules.aggregation.presence_aggregator import (
    PresenceAggregator,
    PresenceStatus as AggStatus,
    Platform as AggPlatform,
    PresenceData,
)

# Import locally to avoid circulars at module import time
from .orchestrator import MeetingOrchestrator, PresenceStatus as AMOStatus


logger = logging.getLogger(__name__)


class PresenceToAMOAdapter:
    """Wire PresenceAggregator events into AMO's update_presence API."""

    def __init__(self, amo: MeetingOrchestrator, aggregator: PresenceAggregator):
        self.amo = amo
        self.aggregator = aggregator

    async def start(self, platforms: List[AggPlatform]) -> None:
        async def _listener(user_id: str, platform: AggPlatform, presence: PresenceData):
            try:
                await self.amo.update_presence(
                    user_id=user_id,
                    platform=platform.value,
                    status=self._map_status(presence.status),
                    confidence=1.0,
                )
            except Exception as exc:
                logger.debug(f"AMO presence update failed: {exc}")

        await self.aggregator.add_presence_listener(_listener)
        await self.aggregator.start_monitoring(platforms)
        logger.info("PresenceToAMOAdapter started")

    async def stop(self) -> None:
        await self.aggregator.stop_monitoring()

    @staticmethod
    def _map_status(status: AggStatus) -> AMOStatus:
        mapping = {
            AggStatus.ONLINE: AMOStatus.ONLINE,
            AggStatus.IDLE: AMOStatus.IDLE,
            AggStatus.BUSY: AMOStatus.BUSY,
            AggStatus.AWAY: AMOStatus.OFFLINE,  # AMO doesn’t model AWAY; treat as not available
            AggStatus.OFFLINE: AMOStatus.OFFLINE,
            AggStatus.UNKNOWN: AMOStatus.UNKNOWN,
        }
        return mapping.get(status, AMOStatus.UNKNOWN)


async def demo_wire_presence_to_amo() -> MeetingOrchestrator:
    """PoC demo: wire aggregator → AMO and run briefly."""
    amo = MeetingOrchestrator()
    aggregator = PresenceAggregator()
    adapter = PresenceToAMOAdapter(amo, aggregator)

    await adapter.start([AggPlatform.DISCORD, AggPlatform.WHATSAPP])
    # Let it run briefly to populate presence
    await asyncio.sleep(5)
    await adapter.stop()
    return amo


if __name__ == "__main__":
    asyncio.run(demo_wire_presence_to_amo())


