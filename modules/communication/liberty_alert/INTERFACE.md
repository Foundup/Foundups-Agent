# Liberty Alert Interface Specification (WSP 11)

**Module**: liberty_alert
**Domain**: communication
**Version**: 0.1.0-POC
**Status**: Development

## Public API

### LibertyAlertOrchestrator

Main coordination class for the entire Liberty Alert system.

```python
class LibertyAlertOrchestrator:
    """
    Central orchestrator for Liberty Alert mesh alert system.
    Coordinates mesh networking, alerts, voice, and map visualization.
    """

    def __init__(self, config: LibertyAlertConfig):
        """
        Initialize Liberty Alert orchestrator

        Args:
            config: LibertyAlertConfig object with system configuration
        """

    async def start(self) -> bool:
        """
        Start all Liberty Alert subsystems

        Returns:
            bool: True if all subsystems started successfully
        """

    async def stop(self) -> bool:
        """
        Gracefully shutdown all subsystems

        Returns:
            bool: True if shutdown successful
        """

    async def broadcast_alert(self, alert: Alert) -> str:
        """
        Broadcast alert through mesh network

        Args:
            alert: Alert object containing threat information

        Returns:
            str: Alert ID for tracking
        """

    def get_mesh_status(self) -> MeshStatus:
        """
        Get current mesh network status

        Returns:
            MeshStatus: Current mesh health and node count
        """
```

### MeshNetwork

Handles WebRTC mesh networking between devices.

```python
class MeshNetwork:
    """WebRTC-based P2P mesh networking"""

    async def connect_peer(self, peer_id: str) -> bool:
        """Establish connection with peer device"""

    async def send_message(self, message: MeshMessage) -> bool:
        """Send message through mesh network"""

    def get_connected_peers(self) -> List[str]:
        """Get list of connected peer IDs"""

    async def enable_discovery(self) -> bool:
        """Enable auto-discovery of nearby peers"""
```

### AlertBroadcaster

Manages alert creation and distribution.

```python
class AlertBroadcaster:
    """Alert broadcast and management system"""

    async def create_alert(
        self,
        location: GeoPoint,
        threat_type: ThreatType,
        message: str,
        language: str = "es"
    ) -> Alert:
        """Create new alert"""

    async def verify_alert(self, alert_id: str) -> bool:
        """Verify alert authenticity (multi-source)"""

    def get_active_alerts(self, radius_km: float = 5.0) -> List[Alert]:
        """Get active alerts within radius"""
```

### VoiceSynthesizer

AI voice generation for alert broadcasts.

```python
class VoiceSynthesizer:
    """AI-powered multilingual voice synthesis"""

    async def synthesize(
        self,
        text: str,
        language: str = "es",
        voice_profile: str = "default"
    ) -> bytes:
        """Generate voice audio from text"""

    async def broadcast_voice(self, alert: Alert) -> bool:
        """Synthesize and broadcast alert via audio"""
```

### MapRenderer

PWA map visualization with danger zones.

```python
class MapRenderer:
    """Leaflet + OSM map rendering for PWA"""

    def render_danger_zones(self, alerts: List[Alert]) -> str:
        """Render danger zone overlays on map"""

    def calculate_safe_route(
        self,
        start: GeoPoint,
        end: GeoPoint,
        avoid_zones: List[Alert]
    ) -> Route:
        """Calculate safest route avoiding danger zones"""

    def get_current_location(self) -> GeoPoint:
        """Get device GPS location"""
```

## Data Models

### Alert

```python
@dataclass
class Alert:
    id: str
    location: GeoPoint
    threat_type: ThreatType
    timestamp: datetime
    message: str
    language: str
    verified: bool
    expires_at: datetime
    source_count: int  # Number of sources reporting
```

### GeoPoint

```python
@dataclass
class GeoPoint:
    latitude: float
    longitude: float
    accuracy: float  # meters
```

### ThreatType

```python
class ThreatType(Enum):
    SURVEILLANCE_VEHICLE = "surveillance_vehicle"
    ICE_RAID = "ice_raid"
    CHECKPOINT = "checkpoint"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    COMMUNITY_VERIFIED = "community_verified"
```

### MeshMessage

```python
@dataclass
class MeshMessage:
    id: str
    type: MessageType
    payload: dict
    sender_id: str
    timestamp: datetime
    ttl: int  # Time to live (hops)
```

### EvadeNetConfig

```python
@dataclass
class EvadeNetConfig:
    mesh_enabled: bool = True
    webrtc_signaling_server: Optional[str] = None  # Optional bootstrap
    meshtastic_enabled: bool = False
    default_language: str = "es"
    alert_radius_km: float = 5.0
    voice_enabled: bool = True
    map_offline_tiles: bool = True
    encryption_key: Optional[bytes] = None
```

## Events

### Event System

```python
class EvadeNetEvents:
    """Event types emitted by system"""

    # Mesh events
    PEER_CONNECTED = "peer_connected"
    PEER_DISCONNECTED = "peer_disconnected"
    MESH_HEALTH_CHANGED = "mesh_health_changed"

    # Alert events
    ALERT_RECEIVED = "alert_received"
    ALERT_VERIFIED = "alert_verified"
    ALERT_EXPIRED = "alert_expired"

    # Voice events
    VOICE_BROADCAST_STARTED = "voice_broadcast_started"
    VOICE_BROADCAST_COMPLETED = "voice_broadcast_completed"

    # Map events
    DANGER_ZONE_ENTERED = "danger_zone_entered"
    DANGER_ZONE_EXITED = "danger_zone_exited"
```

### Event Subscription

```python
orchestrator = LibertyAlertOrchestrator(config)

@orchestrator.on(EvadeNetEvents.ALERT_RECEIVED)
async def handle_alert(alert: Alert):
    print(f"Alert received: {alert.message}")

@orchestrator.on(EvadeNetEvents.PEER_CONNECTED)
async def handle_peer(peer_id: str):
    print(f"New peer connected: {peer_id}")
```

## Usage Examples

### Basic Setup (POC)

```python
from modules.communication.liberty_alert import LibertyAlertOrchestrator, LibertyAlertConfig

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

# Create and broadcast alert
alert = await orchestrator.broadcast_alert(Alert(
    location=GeoPoint(34.0522, -118.2437, accuracy=10.0),
    threat_type=ThreatType.SURVEILLANCE_VEHICLE,
    message="Van blanca en 38th - corre por el callejón",
    language="es"
))

print(f"Alert broadcasted: {alert.id}")
```

### Mesh Status Monitoring

```python
# Check mesh health
status = orchestrator.get_mesh_status()
print(f"Connected peers: {status.peer_count}")
print(f"Mesh coverage: {status.coverage_km2} km²")
print(f"Message latency: {status.avg_latency_ms}ms")
```

### Safe Route Calculation

```python
from modules.platform_integration.liberty_maps import MapRenderer

renderer = MapRenderer()

# Get current location
current = renderer.get_current_location()

# Get active alerts
alerts = orchestrator.alert_broadcaster.get_active_alerts(radius_km=10.0)

# Calculate safe route
safe_route = renderer.calculate_safe_route(
    start=current,
    end=GeoPoint(34.0522, -118.2437, accuracy=5.0),
    avoid_zones=alerts
)

print(f"Safe route distance: {safe_route.distance_km} km")
print(f"Avoiding {len(safe_route.avoided_zones)} danger zones")
```

## Integration Points

### main.py Integration

```python
# In main.py
from modules.communication.evade_net import LibertyAlertOrchestrator

evade_net = LibertyAlertOrchestrator(config=load_config())
await evade_net.start()

# Run event loop for mesh coordination
await evade_net.run()
```

### PWA Frontend Integration

```javascript
// PWA frontend connects to WebRTC mesh
const mesh = new EvadeNetMesh({
    signaling: 'wss://optional-bootstrap.evade.net',
    autoDiscovery: true
});

// Listen for alerts
mesh.on('alert', (alert) => {
    showDangerZone(alert.location, alert.message);
    playVoiceAlert(alert.voice_url);
});

// Broadcast alert (community report)
mesh.broadcast({
    type: 'alert',
    location: getCurrentLocation(),
    message: 'Van en 38th y Main'
});
```

## Dependencies

### Python Dependencies
```
webrtc-python>=0.5.0
aiohttp>=3.8.0
geopy>=2.3.0
cryptography>=41.0.0
```

### Frontend Dependencies
```
leaflet>=1.9.0
workbox-sw>=7.0.0  # PWA service worker
simple-peer>=9.11.0  # WebRTC
```

## Security Considerations

### Encryption
- All mesh messages E2E encrypted using shared keys
- Alert signatures to prevent spoofing
- No PII stored or transmitted

### Privacy
- No central server required (optional bootstrap only)
- Ephemeral alert data (auto-expires)
- Zero tracking or analytics
- Open source for community audit

## Testing

### Unit Tests
```python
pytest tests/test_mesh_network.py
pytest tests/test_alert_broadcaster.py
pytest tests/test_voice_synthesizer.py
```

### Integration Tests
```python
# 2-phone mesh test
pytest tests/integration/test_two_phone_mesh.py

# Alert propagation test
pytest tests/integration/test_alert_propagation.py
```

### PWA Tests
```bash
# Service worker offline test
npm test -- pwa/offline-functionality.test.js
```

## Performance Targets

- **Mesh Latency**: <500ms for local mesh hops
- **Alert Propagation**: <2 seconds to reach 10 nodes
- **Voice Synthesis**: <1 second for Spanish audio
- **Map Rendering**: <100ms for danger zone updates
- **Offline Support**: Full functionality without internet

---

**Status**: POC Development - Interfaces subject to change
**Next Review**: After Sprint 1 completion
