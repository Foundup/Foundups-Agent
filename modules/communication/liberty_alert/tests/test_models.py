"""
Test Data Models
===============

Unit tests for Liberty Alert data models.
"""

import pytest
from datetime import datetime, timedelta

from modules.communication.liberty_alert.src.models import (
    Alert,
    GeoPoint,
    ThreatType,
    MeshMessage,
    MessageType,
    LibertyAlertConfig,
)


class TestGeoPoint:
    """Test GeoPoint functionality"""

    def test_create_geopoint(self):
        """Test basic GeoPoint creation"""
        point = GeoPoint(latitude=34.0522, longitude=-118.2437, accuracy=10.0)

        assert point.latitude == 34.0522
        assert point.longitude == -118.2437
        assert point.accuracy == 10.0

    def test_distance_calculation(self):
        """Test Haversine distance calculation"""
        # Los Angeles
        la = GeoPoint(34.0522, -118.2437)

        # San Francisco (approx 559 km away)
        sf = GeoPoint(37.7749, -122.4194)

        distance = la.distance_to(sf)

        # Should be approximately 559 km
        assert 550 < distance < 570

    def test_string_representation(self):
        """Test GeoPoint string representation"""
        point = GeoPoint(34.0522, -118.2437)
        assert str(point) == "(34.052200, -118.243700)"


class TestAlert:
    """Test Alert functionality"""

    def test_create_alert(self):
        """Test basic alert creation"""
        location = GeoPoint(34.0522, -118.2437)
        alert = Alert(
            location=location,
            threat_type=ThreatType.SURVEILLANCE_VEHICLE,
            message="Van blanca en 38th",
            language="es",
        )

        assert alert.location == location
        assert alert.threat_type == ThreatType.SURVEILLANCE_VEHICLE
        assert alert.message == "Van blanca en 38th"
        assert alert.language == "es"
        assert not alert.verified  # Default false
        assert alert.source_count == 1

    def test_alert_expiration(self):
        """Test alert expiration logic"""
        # Create alert that expires in 1 hour
        alert = Alert(
            location=GeoPoint(34.0522, -118.2437),
            threat_type=ThreatType.CHECKPOINT,
            message="Checkpoint en Main St",
            expires_at=datetime.now() + timedelta(hours=1),
        )

        assert not alert.is_expired()

        # Create already-expired alert
        expired_alert = Alert(
            location=GeoPoint(34.0522, -118.2437),
            threat_type=ThreatType.CHECKPOINT,
            message="Old checkpoint",
            expires_at=datetime.now() - timedelta(hours=1),
        )

        assert expired_alert.is_expired()

    def test_is_near_location(self):
        """Test proximity detection"""
        alert_location = GeoPoint(34.0522, -118.2437)
        alert = Alert(
            location=alert_location,
            threat_type=ThreatType.SUSPICIOUS_ACTIVITY,
            message="Test alert",
        )

        # Same location
        assert alert.is_near(alert_location, radius_km=1.0)

        # Nearby location (1km away - roughly 0.009 degrees)
        nearby = GeoPoint(34.0612, -118.2437)
        assert alert.is_near(nearby, radius_km=5.0)

        # Far location (San Francisco)
        far_away = GeoPoint(37.7749, -122.4194)
        assert not alert.is_near(far_away, radius_km=5.0)

    def test_alert_serialization(self):
        """Test alert to/from dict conversion"""
        location = GeoPoint(34.0522, -118.2437)
        alert = Alert(
            id="test-alert-123",
            location=location,
            threat_type=ThreatType.ICE_RAID,
            message="ICE raid alert",
            language="es",
            verified=True,
        )

        # Convert to dict
        alert_dict = alert.to_dict()

        assert alert_dict["id"] == "test-alert-123"
        assert alert_dict["threat_type"] == "ice_raid"
        assert alert_dict["message"] == "ICE raid alert"
        assert alert_dict["verified"] is True

        # Convert back to Alert
        restored_alert = Alert.from_dict(alert_dict)

        assert restored_alert.id == alert.id
        assert restored_alert.threat_type == alert.threat_type
        assert restored_alert.message == alert.message
        assert restored_alert.verified == alert.verified


class TestMeshMessage:
    """Test MeshMessage functionality"""

    def test_create_mesh_message(self):
        """Test basic mesh message creation"""
        message = MeshMessage(
            type=MessageType.ALERT,
            payload={"test": "data"},
            sender_id="peer-123",
            ttl=10,
        )

        assert message.type == MessageType.ALERT
        assert message.payload == {"test": "data"}
        assert message.sender_id == "peer-123"
        assert message.ttl == 10

    def test_message_serialization(self):
        """Test message to/from dict conversion"""
        message = MeshMessage(
            id="msg-456",
            type=MessageType.PING,
            payload={"ping": "pong"},
            sender_id="peer-789",
            ttl=5,
        )

        # Convert to dict
        msg_dict = message.to_dict()

        assert msg_dict["id"] == "msg-456"
        assert msg_dict["type"] == "ping"
        assert msg_dict["payload"] == {"ping": "pong"}

        # Convert back to MeshMessage
        restored_msg = MeshMessage.from_dict(msg_dict)

        assert restored_msg.id == message.id
        assert restored_msg.type == message.type
        assert restored_msg.payload == message.payload


class TestLibertyAlertConfig:
    """Test LibertyAlertConfig functionality"""

    def test_default_config(self):
        """Test default configuration"""
        config = LibertyAlertConfig()

        assert config.mesh_enabled is True
        assert config.default_language == "es"
        assert config.voice_enabled is True
        assert config.alert_radius_km == 5.0
        assert config.encryption_enabled is True
        assert config.encryption_key is not None  # Auto-generated

    def test_custom_config(self):
        """Test custom configuration"""
        config = LibertyAlertConfig(
            mesh_enabled=False,
            default_language="en",
            alert_radius_km=10.0,
            voice_enabled=False,
        )

        assert config.mesh_enabled is False
        assert config.default_language == "en"
        assert config.alert_radius_km == 10.0
        assert config.voice_enabled is False


class TestThreatTypes:
    """Test threat type enums"""

    def test_threat_type_values(self):
        """Test all threat types exist"""
        assert ThreatType.SURVEILLANCE_VEHICLE.value == "surveillance_vehicle"
        assert ThreatType.ICE_RAID.value == "ice_raid"
        assert ThreatType.CHECKPOINT.value == "checkpoint"
        assert ThreatType.SUSPICIOUS_ACTIVITY.value == "suspicious_activity"
        assert ThreatType.COMMUNITY_VERIFIED.value == "community_verified"
        assert ThreatType.ALL_CLEAR.value == "all_clear"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
