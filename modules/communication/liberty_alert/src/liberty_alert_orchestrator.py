"""
Liberty Alert Orchestrator
==========================

Main coordination class for Liberty Alert mesh alert system.

Coordinates:
- Mesh networking (WebRTC P2P)
- Alert broadcasting and verification
- Voice synthesis (future)
- Map visualization (future)
"""

import asyncio
import logging
from typing import Optional, Callable

from .models import (
    Alert,
    GeoPoint,
    ThreatType,
    LibertyAlertConfig,
    MeshStatus,
    MessageType,
)
from .mesh_network import MeshNetwork
from .alert_broadcaster import AlertBroadcaster

logger = logging.getLogger(__name__)


class LibertyAlertOrchestrator:
    """
    Liberty Alert System Orchestrator

    Central coordination for mesh alert system.
    Integrates mesh networking, alerts, voice, and maps.
    """

    def __init__(self, config: LibertyAlertConfig):
        """
        Initialize Liberty Alert orchestrator

        Args:
            config: System configuration
        """
        self.config = config

        # Initialize mesh network
        self.mesh = MeshNetwork(
            peer_id=None,  # Auto-generate
            signaling_server=config.webrtc_signaling_server,
            auto_discovery=config.auto_discovery,
            max_peers=config.max_peers,
        )

        # Initialize alert broadcaster
        self.alert_broadcaster = AlertBroadcaster(
            mesh_network=self.mesh,
            require_verification=config.require_verification,
            alert_ttl_hours=config.alert_ttl_hours,
            alert_radius_km=config.alert_radius_km,
        )

        # Voice synthesizer (future)
        self.voice_synthesizer = None

        # Map renderer (future)
        self.map_renderer = None

        # System state
        self.is_running = False
        self.event_handlers = {}

        logger.info(f"[LIBERTY ALERT] Orchestrator initialized (peer: {self.mesh.peer_id})")

    async def start(self) -> bool:
        """
        Start all Evade.Net subsystems

        Returns:
            bool: True if all subsystems started successfully
        """
        try:
            logger.info("[LIBERTY ALERT] Starting all subsystems...")

            # Start mesh network
            if not await self.mesh.start():
                logger.error("[LIBERTY ALERT] Failed to start mesh network")
                return False

            # Start alert broadcaster
            if not await self.alert_broadcaster.start():
                logger.error("[LIBERTY ALERT] Failed to start alert broadcaster")
                await self.mesh.stop()
                return False

            self.is_running = True
            logger.info("[LIBERTY ALERT] All subsystems started successfully")
            return True

        except Exception as e:
            logger.error(f"[LIBERTY ALERT] Failed to start: {e}")
            await self.stop()
            return False

    async def stop(self) -> bool:
        """
        Gracefully shutdown all subsystems

        Returns:
            bool: True if shutdown successful
        """
        try:
            logger.info("[LIBERTY ALERT] Shutting down all subsystems...")

            self.is_running = False

            # Stop alert broadcaster
            await self.alert_broadcaster.stop()

            # Stop mesh network
            await self.mesh.stop()

            logger.info("[LIBERTY ALERT] All subsystems stopped successfully")
            return True

        except Exception as e:
            logger.error(f"[LIBERTY ALERT] Failed to stop: {e}")
            return False

    async def broadcast_alert(
        self,
        location: GeoPoint,
        threat_type: ThreatType,
        message: str,
        language: str = "es",
    ) -> Alert:
        """
        Create and broadcast alert through mesh network

        Args:
            location: Alert location
            threat_type: Type of threat
            message: Alert message text
            language: Message language (default: Spanish)

        Returns:
            Alert: Created alert with ID for tracking
        """
        try:
            alert = await self.alert_broadcaster.create_alert(
                location=location,
                threat_type=threat_type,
                message=message,
                language=language,
            )

            logger.info(f"[LIBERTY ALERT] Alert broadcasted: {alert.id}")

            # Emit event
            await self._emit_event("alert_created", alert)

            # Trigger voice broadcast (if enabled)
            if self.config.voice_enabled and self.voice_synthesizer:
                # TODO: Synthesize and broadcast voice
                pass

            return alert

        except Exception as e:
            logger.error(f"[LIBERTY ALERT] Failed to broadcast alert: {e}")
            raise

    def get_mesh_status(self) -> MeshStatus:
        """
        Get current mesh network status

        Returns:
            MeshStatus: Network health and metrics
        """
        return self.mesh.get_mesh_status()

    def get_active_alerts(
        self,
        radius_km: Optional[float] = None,
        location: Optional[GeoPoint] = None,
        verified_only: bool = False,
    ) -> list:
        """
        Get active alerts

        Args:
            radius_km: Search radius
            location: Center point
            verified_only: Only verified alerts

        Returns:
            list: Active alerts matching criteria
        """
        return self.alert_broadcaster.get_active_alerts(
            radius_km=radius_km,
            location=location,
            verified_only=verified_only,
        )

    def on(self, event: str, handler: Callable) -> None:
        """
        Register event handler

        Args:
            event: Event name (e.g., "alert_created", "peer_connected")
            handler: Async callback function
        """
        if event not in self.event_handlers:
            self.event_handlers[event] = []

        self.event_handlers[event].append(handler)
        logger.debug(f"[LIBERTY ALERT] Registered handler for '{event}'")

    async def run(self) -> None:
        """
        Run main event loop

        Keeps orchestrator running until stopped.
        """
        try:
            logger.info("[LIBERTY ALERT] Event loop started")

            while self.is_running:
                # Main loop - handle system events
                await asyncio.sleep(1)

                # TODO: Periodic health checks
                # TODO: Mesh optimization
                # TODO: Alert cleanup coordination

        except asyncio.CancelledError:
            logger.info("[LIBERTY ALERT] Event loop cancelled")
        except Exception as e:
            logger.error(f"[LIBERTY ALERT] Event loop error: {e}")
        finally:
            await self.stop()

    async def _emit_event(self, event: str, *args, **kwargs) -> None:
        """Emit event to registered handlers"""
        if event in self.event_handlers:
            for handler in self.event_handlers[event]:
                try:
                    await handler(*args, **kwargs)
                except Exception as e:
                    logger.error(f"[LIBERTY ALERT] Event handler error for '{event}': {e}")

    def get_system_stats(self) -> dict:
        """
        Get comprehensive system statistics

        Returns:
            dict: System metrics
        """
        mesh_status = self.get_mesh_status()
        alert_stats = self.alert_broadcaster.get_alert_stats()

        return {
            "peer_id": self.mesh.peer_id,
            "is_running": self.is_running,
            "mesh": {
                "peer_count": mesh_status.peer_count,
                "coverage_km2": mesh_status.coverage_km2,
                "avg_latency_ms": mesh_status.avg_latency_ms,
                "message_count": mesh_status.message_count,
                "is_healthy": mesh_status.is_healthy,
            },
            "alerts": alert_stats,
            "config": {
                "mesh_enabled": self.config.mesh_enabled,
                "voice_enabled": self.config.voice_enabled,
                "default_language": self.config.default_language,
                "alert_radius_km": self.config.alert_radius_km,
            },
        }


# POC Demo Function
async def demo_two_phone_mesh():
    """
    POC Demo: 2-Phone Mesh Ping

    Demonstrates basic mesh connectivity and alert propagation.
    """
    print("[DEMO] Starting 2-Phone Mesh Ping Demo...")

    # Create two orchestrators (simulating two phones)
    config_a = LibertyAlertConfig(
        mesh_enabled=True,
        default_language="es",
        voice_enabled=False,  # Disabled for POC
    )

    config_b = LibertyAlertConfig(
        mesh_enabled=True,
        default_language="es",
        voice_enabled=False,
    )

    phone_a = LibertyAlertOrchestrator(config_a)
    phone_b = LibertyAlertOrchestrator(config_b)

    # Start both phones
    await phone_a.start()
    await phone_b.start()

    # Simulate mesh connection (in real scenario, handled by signaling/discovery)
    # TODO: Implement WebRTC offer/answer exchange

    # Phone A creates alert
    alert_location = GeoPoint(34.0522, -118.2437, accuracy=10.0)
    alert = await phone_a.broadcast_alert(
        location=alert_location,
        threat_type=ThreatType.SURVEILLANCE_VEHICLE,
        message="Van blanca en 38th - corre por el callejón",
        language="es",
    )

    print(f"[DEMO] Phone A broadcasted alert: {alert.id}")

    # Wait for propagation
    await asyncio.sleep(2)

    # Phone B checks for alerts
    alerts_on_b = phone_b.get_active_alerts()
    print(f"[DEMO] Phone B received {len(alerts_on_b)} alerts")

    if alerts_on_b:
        print(f"[DEMO] Alert content: {alerts_on_b[0].message}")

    # Cleanup
    await phone_a.stop()
    await phone_b.stop()

    print("[DEMO] Demo complete")


if __name__ == "__main__":
    # Run POC demo
    asyncio.run(demo_two_phone_mesh())
