"""
Liberty Alert Data Models
=========================

Core data structures for mesh alert system.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, List, Dict, Any
from uuid import uuid4


class ThreatType(Enum):
    """Types of threats tracked by the system"""

    SURVEILLANCE_VEHICLE = "surveillance_vehicle"
    ICE_RAID = "ice_raid"
    CHECKPOINT = "checkpoint"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    COMMUNITY_VERIFIED = "community_verified"
    ALL_CLEAR = "all_clear"


class MessageType(Enum):
    """Mesh message types"""

    ALERT = "alert"
    PING = "ping"
    PONG = "pong"
    DISCOVERY = "discovery"
    VOICE = "voice"
    STATUS = "status"


@dataclass
class GeoPoint:
    """Geographic location with accuracy"""

    latitude: float
    longitude: float
    accuracy: float = 10.0  # meters

    def __str__(self) -> str:
        return f"({self.latitude:.6f}, {self.longitude:.6f})"

    def distance_to(self, other: "GeoPoint") -> float:
        """
        Calculate distance to another point in kilometers.
        Uses Haversine formula.
        """
        from math import radians, cos, sin, asin, sqrt

        # Convert to radians
        lat1, lon1 = radians(self.latitude), radians(self.longitude)
        lat2, lon2 = radians(other.latitude), radians(other.longitude)

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))

        # Radius of earth in kilometers
        r = 6371

        return c * r


@dataclass
class Alert:
    """Alert broadcast through mesh network"""

    id: str = field(default_factory=lambda: str(uuid4()))
    location: GeoPoint = field(default_factory=lambda: GeoPoint(0.0, 0.0))
    threat_type: ThreatType = ThreatType.SUSPICIOUS_ACTIVITY
    timestamp: datetime = field(default_factory=datetime.now)
    message: str = ""
    language: str = "es"
    verified: bool = False
    expires_at: Optional[datetime] = None
    source_count: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Set expiration if not provided (default 1 hour)"""
        if self.expires_at is None:
            self.expires_at = self.timestamp + timedelta(hours=1)

    def is_expired(self) -> bool:
        """Check if alert has expired"""
        return datetime.now() > self.expires_at

    def is_near(self, location: GeoPoint, radius_km: float = 5.0) -> bool:
        """Check if alert is within radius of location"""
        return self.location.distance_to(location) <= radius_km

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "location": {
                "latitude": self.location.latitude,
                "longitude": self.location.longitude,
                "accuracy": self.location.accuracy,
            },
            "threat_type": self.threat_type.value,
            "timestamp": self.timestamp.isoformat(),
            "message": self.message,
            "language": self.language,
            "verified": self.verified,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "source_count": self.source_count,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Alert":
        """Create Alert from dictionary"""
        return cls(
            id=data["id"],
            location=GeoPoint(
                latitude=data["location"]["latitude"],
                longitude=data["location"]["longitude"],
                accuracy=data["location"].get("accuracy", 10.0),
            ),
            threat_type=ThreatType(data["threat_type"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            message=data["message"],
            language=data.get("language", "es"),
            verified=data.get("verified", False),
            expires_at=datetime.fromisoformat(data["expires_at"])
            if data.get("expires_at")
            else None,
            source_count=data.get("source_count", 1),
            metadata=data.get("metadata", {}),
        )


@dataclass
class MeshMessage:
    """Message transmitted through mesh network"""

    id: str = field(default_factory=lambda: str(uuid4()))
    type: MessageType = MessageType.PING
    payload: dict = field(default_factory=dict)
    sender_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    ttl: int = 10  # Time to live (hops)

    def to_dict(self) -> dict:
        """Convert to dictionary for transmission"""
        return {
            "id": self.id,
            "type": self.type.value,
            "payload": self.payload,
            "sender_id": self.sender_id,
            "timestamp": self.timestamp.isoformat(),
            "ttl": self.ttl,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MeshMessage":
        """Create MeshMessage from dictionary"""
        return cls(
            id=data["id"],
            type=MessageType(data["type"]),
            payload=data["payload"],
            sender_id=data["sender_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            ttl=data.get("ttl", 10),
        )


@dataclass
class MeshStatus:
    """Current mesh network status"""

    peer_count: int = 0
    coverage_km2: float = 0.0
    avg_latency_ms: float = 0.0
    message_count: int = 0
    is_healthy: bool = True
    connected_peers: List[str] = field(default_factory=list)


@dataclass
class LibertyAlertConfig:
    """Liberty Alert system configuration"""

    # Mesh settings
    mesh_enabled: bool = True
    webrtc_signaling_server: Optional[str] = None  # Optional bootstrap
    meshtastic_enabled: bool = False
    auto_discovery: bool = True

    # Alert settings
    default_language: str = "es"
    alert_radius_km: float = 5.0
    alert_ttl_hours: int = 1
    require_verification: bool = False  # Multi-source verification

    # Voice settings
    voice_enabled: bool = True
    voice_provider: str = "edge-tts"  # or "pyttsx3" for offline

    # Map settings
    map_offline_tiles: bool = True
    map_tile_server: str = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"

    # Security
    encryption_enabled: bool = True
    encryption_key: Optional[bytes] = None

    # Performance
    max_peers: int = 50
    max_message_size_kb: int = 100

    def __post_init__(self):
        """Generate encryption key if needed"""
        if self.encryption_enabled and self.encryption_key is None:
            from cryptography.fernet import Fernet

            self.encryption_key = Fernet.generate_key()


@dataclass
class Route:
    """Safe route calculation result"""

    waypoints: List[GeoPoint] = field(default_factory=list)
    distance_km: float = 0.0
    estimated_time_min: int = 0
    avoided_zones: List[Alert] = field(default_factory=list)
    safety_score: float = 1.0  # 0.0 (dangerous) to 1.0 (safe)
