# -*- coding: utf-8 -*-
import io


"""
# === UTF-8 ENFORCEMENT (WSP 90) ===
# Prevent UnicodeEncodeError on Windows systems
# Only apply when running as main script, not during import
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===

Liberty Alert Sprint Two - POC Test
====================================

Proves concept with MINIMUM code:
- 2 simulated nodes (not 5)
- Fake GPS coordinates
- Mesh alert propagation
- Basic geofencing (distance check)
- Voice output (print for now, TTS later)
- JSON logging to file

Run: pytest modules/communication/liberty_alert/tests/test_sprint_two_poc.py -v
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path

import sys
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from modules.communication.liberty_alert.src.models import (
    Alert,
    GeoPoint,
    ThreatType,
    LibertyAlertConfig,
)
from modules.communication.liberty_alert.src.liberty_alert_orchestrator import (
    LibertyAlertOrchestrator,
)


# Setup JSON logging
LOG_DIR = Path(__file__).parent.parent / "memory" / "test_logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / f"sprint_two_poc_{int(datetime.now().timestamp())}.json"


class JSONLogger:
    """Simple JSON logger for POC"""

    def __init__(self, log_file: Path):
        self.log_file = log_file
        self.events = []

    def log(self, event_type: str, data: dict):
        """Log event with timestamp"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "data": data,
        }
        self.events.append(event)
        print(f"[LOG] {event_type}: {data}")

    def save(self):
        """Save logs to file"""
        with open(self.log_file, "w") as f:
            json.dump(self.events, f, indent=2)
        print(f"\n[LOG] Saved to: {self.log_file}")


# Voice output simulation (TTS placeholder)
def voice_announce(message: str, language: str = "es"):
    """
    Simulate voice announcement.
    POC: Just print. Future: edge-tts integration.
    """
    print(f"\n[U+1F50A] [VOICE-{language.upper()}]: {message}")
    # TODO: Add edge-tts here:
    # import edge_tts
    # await edge_tts.Communicate(message, "es-MX-DaliaNeural").save("alert.mp3")


# Geofencing simulation
def check_geofence(location: GeoPoint, danger_zone: GeoPoint, radius_km: float = 1.0) -> bool:
    """
    Check if location is within danger zone.
    Uses existing GeoPoint.distance_to() method.
    """
    distance = location.distance_to(danger_zone)
    in_zone = distance <= radius_km
    if in_zone:
        print(f"[U+26A0]️  [GEOFENCE] Within danger zone! Distance: {distance:.2f}km")
    return in_zone


@pytest.mark.asyncio
async def test_sprint_two_poc():
    """
    Sprint Two POC Test
    ====================

    Simulates:
    1. Two nodes at different LA locations
    2. Node A creates alert with geofence
    3. Node B receives alert (simulated mesh)
    4. Voice announcement triggered
    5. All events logged to JSON
    """

    logger = JSONLogger(LOG_FILE)
    logger.log("test_start", {"test": "Sprint Two POC", "nodes": 2})

    # ===== Setup: 2 Nodes with Fake GPS =====
    print("\n" + "=" * 60)
    print("LIBERTY ALERT - SPRINT TWO POC")
    print("=" * 60)

    # Node A: 38th & Main (fake GPS)
    node_a_location = GeoPoint(34.0522, -118.2437, accuracy=10.0)
    config_a = LibertyAlertConfig(
        mesh_enabled=True,
        voice_enabled=True,
        default_language="es",
    )
    node_a = LibertyAlertOrchestrator(config_a)

    # Node B: 2km away
    node_b_location = GeoPoint(34.0700, -118.2600, accuracy=10.0)
    config_b = LibertyAlertConfig(
        mesh_enabled=True,
        voice_enabled=True,
        default_language="es",
    )
    node_b = LibertyAlertOrchestrator(config_b)

    logger.log(
        "nodes_initialized",
        {
            "node_a": {"id": node_a.mesh.peer_id, "location": str(node_a_location)},
            "node_b": {"id": node_b.mesh.peer_id, "location": str(node_b_location)},
        },
    )

    print(f"\n[PIN] Node A: {node_a.mesh.peer_id} at {node_a_location}")
    print(f"[PIN] Node B: {node_b.mesh.peer_id} at {node_b_location}")

    # ===== Start Both Nodes =====
    print("\n[STEP 1] Starting mesh nodes...")
    await node_a.start()
    await node_b.start()
    logger.log("nodes_started", {"status": "mesh active"})

    # ===== Node A: Create Alert with Geofence =====
    print("\n[STEP 2] Node A creates alert...")

    alert_location = GeoPoint(34.0522, -118.2437, accuracy=10.0)  # Same as Node A
    alert = await node_a.broadcast_alert(
        location=alert_location,
        threat_type=ThreatType.SURVEILLANCE_VEHICLE,
        message="¡Alerta! Van blanca en calle 38 - corre por el callejón",
        language="es",
    )

    logger.log(
        "alert_created",
        {
            "alert_id": alert.id,
            "location": str(alert_location),
            "threat": alert.threat_type.value,
            "message": alert.message,
        },
    )

    print(f"[OK] Alert created: {alert.id}")
    print(f"   Message: {alert.message}")

    # ===== Voice Announcement =====
    print("\n[STEP 3] Triggering voice announcement...")
    voice_announce(alert.message, language="es")
    logger.log("voice_triggered", {"message": alert.message, "language": "es"})

    # ===== Geofencing Check =====
    print("\n[STEP 4] Checking geofences...")

    # Node A: Should be IN danger zone
    a_in_zone = check_geofence(node_a_location, alert_location, radius_km=1.0)
    logger.log(
        "geofence_check",
        {"node": "A", "in_zone": a_in_zone, "distance_km": node_a_location.distance_to(alert_location)},
    )

    # Node B: Should be OUTSIDE danger zone (2km away)
    b_in_zone = check_geofence(node_b_location, alert_location, radius_km=1.0)
    logger.log(
        "geofence_check",
        {"node": "B", "in_zone": b_in_zone, "distance_km": node_b_location.distance_to(alert_location)},
    )

    # ===== Simulate Mesh Propagation =====
    print("\n[STEP 5] Simulating mesh alert propagation...")
    # In real implementation, mesh would propagate automatically
    # For POC, we manually add alert to Node B
    node_b.alert_broadcaster.active_alerts[alert.id] = alert
    logger.log("mesh_propagation", {"from": "Node A", "to": "Node B", "alert_id": alert.id})

    # Node B checks for nearby alerts
    node_b_alerts = node_b.get_active_alerts(location=node_b_location, radius_km=5.0)
    print(f"[OK] Node B received {len(node_b_alerts)} alerts")

    # ===== Verify Results =====
    print("\n[STEP 6] Verification...")
    assert len(node_b_alerts) == 1, "Node B should have received 1 alert"
    assert node_b_alerts[0].id == alert.id, "Alert IDs should match"
    assert a_in_zone is True, "Node A should be inside danger zone"
    assert b_in_zone is False, "Node B should be outside danger zone"

    logger.log(
        "verification",
        {
            "alerts_received": len(node_b_alerts),
            "geofence_a": a_in_zone,
            "geofence_b": b_in_zone,
            "status": "PASS",
        },
    )

    # ===== Cleanup =====
    await node_a.stop()
    await node_b.stop()
    logger.log("nodes_stopped", {"status": "cleanup complete"})

    # ===== Save Logs =====
    logger.save()

    print("\n" + "=" * 60)
    print("[OK] SPRINT TWO POC: SUCCESS")
    print("=" * 60)
    print(f"\nProof of Concept Verified:")
    print(f"  [OK] 2-node mesh simulation")
    print(f"  [OK] Alert propagation (simulated)")
    print(f"  [OK] Geofencing (distance-based)")
    print(f"  [OK] Voice output (placeholder)")
    print(f"  [OK] JSON logging: {LOG_FILE}")
    print(f"\nReady for:")
    print(f"  -> Real WebRTC mesh (aiortc)")
    print(f"  -> Real voice (edge-tts)")
    print(f"  -> Map dashboard (Flask + Leaflet)")


if __name__ == "__main__":
    # Run POC directly
    asyncio.run(test_sprint_two_poc())
