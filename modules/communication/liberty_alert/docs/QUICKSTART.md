# Liberty Alert - Quick Start Guide

## What is Liberty Alert?

**Liberty Alert** is an open-source, off-grid mesh alert system that protects communities through real-time P2P notifications - no servers, no tracking, pure freedom.

> "When a van turns onto 38th, communities get a push. Corre por el callejón before sirens even hit. Phones turn into radios, maps breathe danger zones, and AI voices broadcast in Spanish from rooftops or pockets. No store, no track. Pure mesh, pure freedom."

## Core Features

- **Mesh Networking**: Phone-to-phone WebRTC connections (no internet needed)
- **Real-Time Alerts**: Community-reported threats broadcast instantly
- **AI Voice**: Multilingual voice broadcasts (Spanish primary)
- **Live Maps**: Danger zone visualization with safe route calculation
- **Zero Tracking**: No servers, no data storage, E2E encrypted
- **Offline First**: PWA with full offline capability

## Installation

### 1. Install Dependencies
```bash
cd modules/communication/liberty_alert
pip install -r requirements.txt
```

### 2. Run from Main Menu
```bash
python main.py
# Select option 6: Liberty Alert
```

### 3. Or Run Directly
```bash
python main.py --liberty
```

## POC Demo: 2-Phone Mesh Ping

### Run Tests
```bash
# Unit tests
pytest modules/communication/liberty_alert/tests/test_models.py -v

# POC demo test
pytest modules/communication/liberty_alert/tests/test_poc_demo.py -v --asyncio-mode=auto
```

### Run Demo Directly
```python
from modules.communication.liberty_alert.src.liberty_alert_orchestrator import demo_two_phone_mesh
import asyncio

asyncio.run(demo_two_phone_mesh())
```

## Basic Usage

### Create Alert
```python
from modules.communication.liberty_alert.src import (
    LibertyAlertOrchestrator,
    LibertyAlertConfig,
    GeoPoint,
    ThreatType
)
import asyncio

# Configure system
config = LibertyAlertConfig(
    mesh_enabled=True,
    default_language="es",
    voice_enabled=True,
    alert_radius_km=5.0
)

# Start orchestrator
orchestrator = LibertyAlertOrchestrator(config)
await orchestrator.start()

# Create alert
alert = await orchestrator.broadcast_alert(
    location=GeoPoint(34.0522, -118.2437, accuracy=10.0),
    threat_type=ThreatType.SURVEILLANCE_VEHICLE,
    message="Van blanca en 38th - corre por el callejón",
    language="es"
)

print(f"Alert broadcasted: {alert.id}")
```

### Get Active Alerts
```python
# Get all active alerts
alerts = orchestrator.get_active_alerts()

# Get alerts within radius
alerts = orchestrator.get_active_alerts(
    radius_km=10.0,
    location=current_location,
    verified_only=True
)
```

### Check Mesh Status
```python
status = orchestrator.get_mesh_status()
print(f"Connected peers: {status.peer_count}")
print(f"Mesh healthy: {status.is_healthy}")
```

## Configuration

### Basic Config
```python
config = LibertyAlertConfig(
    mesh_enabled=True,          # Enable WebRTC mesh
    voice_enabled=True,          # Enable AI voice
    default_language="es",       # Spanish by default
    alert_radius_km=5.0,        # 5km alert radius
    alert_ttl_hours=1,          # Alerts expire in 1 hour
)
```

### Advanced Config
```python
config = LibertyAlertConfig(
    # Mesh settings
    webrtc_signaling_server="wss://optional-bootstrap.libertyalert.net",
    meshtastic_enabled=False,    # LoRa extension (future)
    auto_discovery=True,          # Auto-discover nearby peers
    max_peers=50,                 # Max peer connections

    # Alert settings
    require_verification=False,   # Multi-source verification

    # Voice settings
    voice_provider="edge-tts",    # or "pyttsx3" for offline

    # Map settings
    map_offline_tiles=True,       # Cache OSM tiles

    # Security
    encryption_enabled=True,      # E2E encryption
)
```

## Threat Types

```python
from modules.communication.liberty_alert.src.models import ThreatType

# Available threat types:
ThreatType.SURVEILLANCE_VEHICLE   # Unmarked vans, ICE vehicles
ThreatType.ICE_RAID              # Immigration raid in progress
ThreatType.CHECKPOINT            # Border checkpoint or roadblock
ThreatType.SUSPICIOUS_ACTIVITY   # Unverified threat
ThreatType.COMMUNITY_VERIFIED    # Multi-source verified threat
ThreatType.ALL_CLEAR            # Safe zone notification
```

## Architecture

### Module Structure (WSP 49 Compliant)
```
modules/communication/liberty_alert/
+-- src/                    # Core implementation
[U+2502]   +-- models.py          # Data models
[U+2502]   +-- mesh_network.py    # WebRTC mesh
[U+2502]   +-- alert_broadcaster.py # Alert system
[U+2502]   +-- liberty_alert_orchestrator.py # Main orchestrator
+-- tests/                  # Test suite
+-- memory/                 # WSP 60 memory architecture
+-- pwa/                   # Progressive Web App (future)
+-- README.md              # Full documentation
+-- INTERFACE.md           # API specification
+-- requirements.txt       # Dependencies
```

### Technology Stack
- **Backend**: Python 3.9+ with aiortc (WebRTC)
- **Voice**: edge-tts (Microsoft Edge TTS) or pyttsx3 (offline)
- **Maps**: Leaflet.js + OpenStreetMap (PWA)
- **Mesh**: WebRTC DataChannels + optional Meshtastic (LoRa)
- **Crypto**: cryptography library for E2E encryption

## Security & Privacy

### What We Protect
- **E2E Encryption**: All mesh messages encrypted
- **No Central Server**: Pure P2P (optional bootstrap only)
- **Ephemeral Data**: Alerts auto-expire (1 hour default)
- **Zero Tracking**: No PII, no analytics, no surveillance
- **Open Source**: Community auditable

### What We Don't Do
- This is a **defensive alert system**, not surveillance
- No tracking of individuals
- No data retention beyond alert TTL
- No offensive capabilities

## Roadmap

### Sprint 1: POC (Current) [OK]
- [x] WSP-compliant module structure
- [x] WebRTC mesh networking
- [x] Alert broadcasting system
- [x] Data models and tests
- [x] Main.py integration

### Sprint 2: Mesh Demo (2 weeks)
- [ ] WebRTC signaling implementation
- [ ] 2-phone mesh connection demo
- [ ] Fake alert propagation test
- [ ] Basic PWA shell

### Sprint 3: Community Alpha (1 month)
- [ ] Real threat detection
- [ ] Multi-device mesh (10+ nodes)
- [ ] Spanish voice broadcasts
- [ ] Leaflet map visualization
- [ ] Neighborhood coverage

### Sprint 4: Production (3 months)
- [ ] Meshtastic integration (LoRa)
- [ ] Advanced mesh routing
- [ ] Community governance
- [ ] Regional scaling

## Contributing

Liberty Alert is open source and community-owned. Contributions welcome!

**License**: MIT (pending legal review for community protection)

## Support

- **Documentation**: See `README.md` and `INTERFACE.md`
- **Issues**: Report bugs or feature requests on GitHub
- **Community**: Join community channels (TBD)

---

**The outcome is protection. The method is solidarity. The technology is liberation.**
