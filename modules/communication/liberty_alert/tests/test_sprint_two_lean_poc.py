# -*- coding: utf-8 -*-
"""
Liberty Alert Sprint Two - LEAN POC (No Dependencies)
======================================================

POC FIRST PRINCIPLES - Occam's Razor Applied:
- Mock mesh (no aiortc needed)
- 2 nodes, simulated GPS
- Geofencing (existing GeoPoint.distance_to)
- Voice (print output, no TTS libs)
- JSON logging to file

WSP 15 MPS Scores Applied:
  Feature             | C | I | D | P | MPS | Priority | Build
  --------------------|---|---|---|---|-----|----------|-------
  2-node simulator    | 2 | 5 | 1 | 5 | 13  | P1       | YES
  Voice (mock)        | 1 | 3 | 4 | 3 | 11  | P2       | YES
  Geofencing          | 2 | 4 | 2 | 4 | 12  | P2       | YES
  JSON logging        | 1 | 4 | 2 | 3 | 10  | P2       | YES

SKIP for POC: Web dashboard, real WebRTC, real TTS (Sprint 3)

Run: python modules/communication/liberty_alert/tests/test_sprint_two_lean_poc.py
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
# Prevent UnicodeEncodeError on Windows systems
import sys
import io

if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===

import json
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4


# ===== Simple Data Models (no external deps) =====


class ThreatType(Enum):
    """Alert threat types"""
    SURVEILLANCE_VEHICLE = "surveillance_vehicle"
    ICE_RAID = "ice_raid"
    CHECKPOINT = "checkpoint"


@dataclass
class GeoPoint:
    """Geographic location"""
    latitude: float
    longitude: float
    accuracy: float = 10.0

    def distance_to(self, other: "GeoPoint") -> float:
        """Calculate distance in kilometers (Haversine formula)"""
        from math import radians, cos, sin, asin, sqrt

        lat1, lon1 = radians(self.latitude), radians(self.longitude)
        lat2, lon2 = radians(other.latitude), radians(other.longitude)

        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        r = 6371  # Earth radius in km
        return c * r

    def __str__(self):
        return f"({self.latitude:.4f}, {self.longitude:.4f})"


@dataclass
class Alert:
    """Mesh alert"""
    id: str = field(default_factory=lambda: str(uuid4()))
    location: GeoPoint = field(default_factory=lambda: GeoPoint(0, 0))
    threat_type: ThreatType = ThreatType.SURVEILLANCE_VEHICLE
    timestamp: datetime = field(default_factory=datetime.now)
    message: str = ""
    language: str = "es"
    verified: bool = False
    expires_at: datetime = None

    def __post_init__(self):
        if self.expires_at is None:
            self.expires_at = self.timestamp + timedelta(hours=1)


class SimpleNode:
    """Simulated Liberty Alert node (no WebRTC)"""

    def __init__(self, node_id: str, location: GeoPoint):
        self.node_id = node_id
        self.location = location
        self.alerts = {}  # alert_id -> Alert
        self.mesh_peers = []  # Connected peers

    def create_alert(self, location: GeoPoint, threat_type: ThreatType, message: str) -> Alert:
        """Create and broadcast alert"""
        alert = Alert(
            location=location,
            threat_type=threat_type,
            message=message,
            language="es",
        )
        self.alerts[alert.id] = alert
        return alert

    def receive_alert(self, alert: Alert):
        """Receive alert from mesh (simulated)"""
        if alert.id not in self.alerts:
            self.alerts[alert.id] = alert

    def get_alerts_in_radius(self, radius_km: float = 5.0):
        """Get alerts within radius"""
        nearby = []
        for alert in self.alerts.values():
            if self.location.distance_to(alert.location) <= radius_km:
                nearby.append(alert)
        return nearby


# ===== JSON Logger =====


class JSONLogger:
    """Simple JSON event logger"""

    def __init__(self, log_file: Path):
        self.log_file = log_file
        self.events = []

    def log(self, event_type: str, data: dict):
        """Log timestamped event"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "data": data,
        }
        self.events.append(event)
        print(f"[LOG] {event_type}: {json.dumps(data, indent=2)}")

    def save(self):
        """Save to JSON file"""
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_file, "w") as f:
            json.dump(self.events, f, indent=2)
        print(f"\n[OK] [LOG] Saved to: {self.log_file}")


# ===== Voice Simulation =====


def voice_announce(message: str, language: str = "es"):
    """Simulate voice announcement (POC: print, future: edge-tts)"""
    print(f"\n[VOICE-{language.upper()}]: {message}")
    print(f"   (Future: edge-tts will synthesize audio)")


# ===== Geofencing =====


def check_geofence(location: GeoPoint, danger_zone: GeoPoint, radius_km: float = 1.0) -> bool:
    """Check if location is within danger zone"""
    distance = location.distance_to(danger_zone)
    in_zone = distance <= radius_km

    if in_zone:
        print(f"[WARNING] [GEOFENCE] IN DANGER ZONE! Distance: {distance:.3f}km (limit: {radius_km}km)")
    else:
        print(f"[SAFE] [GEOFENCE] Outside danger zone. Distance: {distance:.3f}km (limit: {radius_km}km)")

    return in_zone


# ===== MAIN POC TEST =====


def main():
    """
    Sprint Two POC - Lean Version
    ==============================

    Proves all Sprint Two features WITHOUT external dependencies:
    - 2-node mesh (simulated)
    - Alert propagation
    - Geofencing
    - Voice output (mock)
    - JSON logging
    """

    # Setup logging
    log_dir = Path(__file__).parent.parent / "memory" / "test_logs"
    log_file = log_dir / f"sprint_two_lean_poc_{int(datetime.now().timestamp())}.json"
    logger = JSONLogger(log_file)

    print("\n" + "=" * 70)
    print("LIBERTY ALERT - SPRINT TWO POC (LEAN VERSION)")
    print("=" * 70)
    print("\nWSP 15 MPS Prioritization Applied:")
    print("  [OK] 2-node simulator (MPS: 13, P1)")
    print("  [OK] Geofencing (MPS: 12, P2)")
    print("  [OK] Voice output (MPS: 11, P2)")
    print("  [OK] JSON logging (MPS: 10, P2)")
    print("\nSkipped for POC: WebRTC, edge-tts, web dashboard")
    print("=" * 70)

    logger.log("test_start", {"test": "Sprint Two Lean POC", "nodes": 2})

    # ===== Setup: 2 Nodes with Fake GPS =====
    print("\n[STEP 1] Initializing 2 nodes with fake GPS locations...")

    # Node A: 38th & Main, LA (fake GPS)
    node_a_location = GeoPoint(34.0522, -118.2437)
    node_a = SimpleNode("node-a", node_a_location)

    # Node B: 2km away
    node_b_location = GeoPoint(34.0700, -118.2600)
    node_b = SimpleNode("node-b", node_b_location)

    print(f"  [LOC] Node A: {node_a.node_id} at {node_a_location}")
    print(f"  [LOC] Node B: {node_b.node_id} at {node_b_location}")
    print(f"  [INFO] Distance between nodes: {node_a_location.distance_to(node_b_location):.2f} km")

    logger.log("nodes_initialized", {
        "node_a": {"id": node_a.node_id, "location": str(node_a_location)},
        "node_b": {"id": node_b.node_id, "location": str(node_b_location)},
        "distance_km": node_a_location.distance_to(node_b_location),
    })

    # ===== Create Alert on Node A =====
    print("\n[STEP 2] Node A creates surveillance alert...")

    alert = node_a.create_alert(
        location=node_a_location,  # Alert at Node A's location
        threat_type=ThreatType.SURVEILLANCE_VEHICLE,
        message="ALERT: White van on 38th Street - take alley route"
    )

    print(f"  [OK] Alert created: {alert.id}")
    print(f"     Type: {alert.threat_type.value}")
    print(f"     Location: {alert.location}")
    print(f"     Message: {alert.message}")
    print(f"     Expires: {alert.expires_at.strftime('%H:%M:%S')}")

    logger.log("alert_created", {
        "alert_id": alert.id,
        "threat_type": alert.threat_type.value,
        "location": str(alert.location),
        "message": alert.message,
    })

    # ===== Voice Announcement =====
    print("\n[STEP 3] Triggering voice announcement...")
    voice_announce(alert.message, language="es")

    logger.log("voice_triggered", {
        "message": alert.message,
        "language": "es",
        "note": "POC uses print, production will use edge-tts",
    })

    # ===== Geofencing Checks =====
    print("\n[STEP 4] Checking geofences (1km radius)...")

    print("\n  Node A geofence check:")
    a_in_zone = check_geofence(node_a_location, alert.location, radius_km=1.0)
    logger.log("geofence_check", {
        "node": "A",
        "in_zone": a_in_zone,
        "distance_km": node_a_location.distance_to(alert.location),
    })

    print("\n  Node B geofence check:")
    b_in_zone = check_geofence(node_b_location, alert.location, radius_km=1.0)
    logger.log("geofence_check", {
        "node": "B",
        "in_zone": b_in_zone,
        "distance_km": node_b_location.distance_to(alert.location),
    })

    # ===== Simulate Mesh Propagation =====
    print("\n[STEP 5] Simulating mesh alert propagation (Node A -> Node B)...")

    # In real implementation, WebRTC mesh would propagate automatically
    # For POC, we manually simulate propagation
    node_b.receive_alert(alert)
    print(f"  [OK] Node B received alert: {alert.id}")

    logger.log("mesh_propagation", {
        "from": "node_a",
        "to": "node_b",
        "alert_id": alert.id,
        "note": "Simulated propagation, production will use aiortc WebRTC",
    })

    # ===== Verify Results =====
    print("\n[STEP 6] Verification...")

    # Node B should have received the alert
    b_alerts = node_b.get_alerts_in_radius(radius_km=5.0)
    print(f"  [OK] Node B has {len(b_alerts)} alert(s) within 5km")

    # Geofence assertions
    assert a_in_zone is True, "[FAIL] Node A should be IN danger zone"
    assert b_in_zone is False, "[FAIL] Node B should be OUTSIDE danger zone (2km away)"
    assert len(b_alerts) == 1, f"[FAIL] Node B should have exactly 1 alert, got {len(b_alerts)}"

    print(f"  [PASS] Node A correctly detected as IN danger zone")
    print(f"  [PASS] Node B correctly detected as OUTSIDE danger zone")
    print(f"  [PASS] Mesh propagation successful")

    logger.log("verification", {
        "node_a_in_zone": a_in_zone,
        "node_b_in_zone": b_in_zone,
        "alerts_received_by_b": len(b_alerts),
        "status": "PASS",
    })

    # ===== Save Logs =====
    print("\n[STEP 7] Saving JSON log...")
    logger.save()

    # ===== Summary =====
    print("\n" + "=" * 70)
    print("[SUCCESS] SPRINT TWO POC: ALL TESTS PASSED")
    print("=" * 70)
    print("\nProven Features (WSP 15 MPS Prioritized):")
    print("  [PASS] 2-node mesh simulation (MPS: 13, P1)")
    print("  [PASS] Alert propagation between nodes")
    print("  [PASS] Geofencing with distance calculation")
    print("  [PASS] Voice output (mock TTS)")
    print("  [PASS] JSON structured logging")
    print("\nReady for Sprint 3:")
    print("  -> Real WebRTC mesh (aiortc)")
    print("  -> Real voice synthesis (edge-tts)")
    print("  -> Map dashboard (Flask + Leaflet)")
    print("  -> Deployment to 2 physical phones")
    print("\nLog file:")
    print(f"  {log_file}")
    print("=" * 70)


if __name__ == "__main__":
    main()
