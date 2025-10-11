"""
Alert Broadcaster
================

Alert creation, verification, and broadcast system for Evade.Net.

Handles:
- Alert creation and validation
- Multi-source verification
- Alert expiration and cleanup
- Geographic filtering
"""

import asyncio
import logging
from typing import List, Optional, Dict, Set
from datetime import datetime, timedelta
from uuid import uuid4

from .models import Alert, GeoPoint, ThreatType, MeshMessage, MessageType
from .mesh_network import MeshNetwork

logger = logging.getLogger(__name__)


class AlertBroadcaster:
    """
    Alert Broadcast and Management System

    Manages alert lifecycle:
    1. Creation and validation
    2. Mesh broadcast
    3. Multi-source verification
    4. Geographic filtering
    5. Automatic expiration
    """

    def __init__(
        self,
        mesh_network: MeshNetwork,
        require_verification: bool = False,
        alert_ttl_hours: int = 1,
        alert_radius_km: float = 5.0,
    ):
        """
        Initialize alert broadcaster

        Args:
            mesh_network: Mesh network for alert propagation
            require_verification: Require multi-source verification
            alert_ttl_hours: Alert time-to-live in hours
            alert_radius_km: Default alert radius in kilometers
        """
        self.mesh = mesh_network
        self.require_verification = require_verification
        self.alert_ttl_hours = alert_ttl_hours
        self.alert_radius_km = alert_radius_km

        # Alert storage
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_sources: Dict[str, Set[str]] = {}  # alert_id -> set of source peer_ids

        # Register mesh handlers
        self.mesh.on(MessageType.ALERT, self._handle_alert_message)

        # Start cleanup task
        self._cleanup_task = None

        logger.info("[ALERT] Alert broadcaster initialized")

    async def start(self) -> bool:
        """
        Start alert broadcaster

        Returns:
            bool: True if started successfully
        """
        try:
            # Start cleanup loop
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            logger.info("[ALERT] Alert broadcaster started")
            return True

        except Exception as e:
            logger.error(f"[ALERT] Failed to start: {e}")
            return False

    async def stop(self) -> bool:
        """
        Stop alert broadcaster

        Returns:
            bool: True if stopped successfully
        """
        try:
            if self._cleanup_task:
                self._cleanup_task.cancel()
                try:
                    await self._cleanup_task
                except asyncio.CancelledError:
                    pass

            logger.info("[ALERT] Alert broadcaster stopped")
            return True

        except Exception as e:
            logger.error(f"[ALERT] Failed to stop: {e}")
            return False

    async def create_alert(
        self,
        location: GeoPoint,
        threat_type: ThreatType,
        message: str,
        language: str = "es",
        metadata: Optional[Dict] = None,
    ) -> Alert:
        """
        Create new alert

        Args:
            location: Alert location
            threat_type: Type of threat
            message: Alert message text
            language: Message language (default: Spanish)
            metadata: Optional additional data

        Returns:
            Alert: Created alert
        """
        try:
            # Create alert
            alert = Alert(
                id=str(uuid4()),
                location=location,
                threat_type=threat_type,
                timestamp=datetime.now(),
                message=message,
                language=language,
                verified=not self.require_verification,  # Auto-verify if not required
                expires_at=datetime.now() + timedelta(hours=self.alert_ttl_hours),
                source_count=1,
                metadata=metadata or {},
            )

            # Store alert
            self.active_alerts[alert.id] = alert
            self.alert_sources[alert.id] = {self.mesh.peer_id}

            # Broadcast to mesh
            await self._broadcast_alert(alert)

            logger.info(
                f"[ALERT] Created alert {alert.id}: {threat_type.value} at {location}"
            )
            return alert

        except Exception as e:
            logger.error(f"[ALERT] Failed to create alert: {e}")
            raise

    async def verify_alert(self, alert_id: str) -> bool:
        """
        Verify alert authenticity (multi-source)

        Args:
            alert_id: Alert to verify

        Returns:
            bool: True if verified
        """
        if alert_id not in self.active_alerts:
            logger.warning(f"[ALERT] Alert {alert_id} not found for verification")
            return False

        alert = self.active_alerts[alert_id]
        source_count = len(self.alert_sources.get(alert_id, set()))

        # Require 2+ sources for verification
        if source_count >= 2:
            alert.verified = True
            alert.source_count = source_count
            logger.info(f"[ALERT] Alert {alert_id} verified ({source_count} sources)")
            return True

        logger.debug(
            f"[ALERT] Alert {alert_id} not verified ({source_count}/2 sources)"
        )
        return False

    def get_active_alerts(
        self,
        radius_km: Optional[float] = None,
        location: Optional[GeoPoint] = None,
        verified_only: bool = False,
    ) -> List[Alert]:
        """
        Get active alerts within radius

        Args:
            radius_km: Search radius (default: configured radius)
            location: Center point (default: all alerts)
            verified_only: Return only verified alerts

        Returns:
            List[Alert]: Active alerts matching criteria
        """
        radius = radius_km or self.alert_radius_km
        now = datetime.now()

        alerts = []
        for alert in self.active_alerts.values():
            # Check expiration
            if alert.expires_at and alert.expires_at < now:
                continue

            # Check verification
            if verified_only and not alert.verified:
                continue

            # Check location
            if location and not alert.is_near(location, radius):
                continue

            alerts.append(alert)

        # Sort by timestamp (most recent first)
        alerts.sort(key=lambda a: a.timestamp, reverse=True)

        logger.debug(f"[ALERT] Retrieved {len(alerts)} active alerts")
        return alerts

    def get_alert(self, alert_id: str) -> Optional[Alert]:
        """
        Get specific alert by ID

        Args:
            alert_id: Alert ID

        Returns:
            Optional[Alert]: Alert if found
        """
        return self.active_alerts.get(alert_id)

    async def _broadcast_alert(self, alert: Alert) -> None:
        """Broadcast alert through mesh network"""
        try:
            message = MeshMessage(
                type=MessageType.ALERT,
                payload=alert.to_dict(),
                sender_id=self.mesh.peer_id,
                ttl=10,  # Max 10 hops
            )

            success = await self.mesh.send_message(message)
            if success:
                logger.info(f"[ALERT] Broadcast alert {alert.id} to mesh")
            else:
                logger.warning(f"[ALERT] Failed to broadcast alert {alert.id}")

        except Exception as e:
            logger.error(f"[ALERT] Failed to broadcast alert: {e}")

    async def _handle_alert_message(
        self, message: MeshMessage, from_peer: str
    ) -> None:
        """Handle received alert message from mesh"""
        try:
            # Deserialize alert
            alert_data = message.payload
            alert = Alert.from_dict(alert_data)

            # Check if we already have this alert
            if alert.id in self.active_alerts:
                # Add peer as additional source
                if alert.id not in self.alert_sources:
                    self.alert_sources[alert.id] = set()

                self.alert_sources[alert.id].add(from_peer)

                # Try to verify
                await self.verify_alert(alert.id)

                logger.debug(
                    f"[ALERT] Added source for alert {alert.id} ({len(self.alert_sources[alert.id])} sources)"
                )
            else:
                # New alert
                self.active_alerts[alert.id] = alert
                self.alert_sources[alert.id] = {from_peer}

                logger.info(
                    f"[ALERT] Received new alert {alert.id} from {from_peer}: {alert.threat_type.value}"
                )

                # Broadcast to other peers (mesh routing handled by MeshNetwork)

        except Exception as e:
            logger.error(f"[ALERT] Failed to handle alert message: {e}")

    async def _cleanup_loop(self) -> None:
        """Periodic cleanup of expired alerts"""
        while True:
            try:
                await asyncio.sleep(60)  # Cleanup every minute

                now = datetime.now()
                expired = []

                for alert_id, alert in self.active_alerts.items():
                    if alert.expires_at and alert.expires_at < now:
                        expired.append(alert_id)

                # Remove expired alerts
                for alert_id in expired:
                    del self.active_alerts[alert_id]
                    if alert_id in self.alert_sources:
                        del self.alert_sources[alert_id]

                    logger.debug(f"[ALERT] Cleaned up expired alert {alert_id}")

                if expired:
                    logger.info(f"[ALERT] Cleaned up {len(expired)} expired alerts")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[ALERT] Cleanup loop error: {e}")
                await asyncio.sleep(60)

    def get_alert_stats(self) -> dict:
        """
        Get alert statistics

        Returns:
            dict: Alert metrics
        """
        now = datetime.now()
        active_count = len(self.active_alerts)
        verified_count = sum(1 for a in self.active_alerts.values() if a.verified)

        threat_counts = {}
        for alert in self.active_alerts.values():
            threat_type = alert.threat_type.value
            threat_counts[threat_type] = threat_counts.get(threat_type, 0) + 1

        return {
            "active_alerts": active_count,
            "verified_alerts": verified_count,
            "threat_breakdown": threat_counts,
            "average_sources": sum(len(sources) for sources in self.alert_sources.values())
            / len(self.alert_sources)
            if self.alert_sources
            else 0,
        }
