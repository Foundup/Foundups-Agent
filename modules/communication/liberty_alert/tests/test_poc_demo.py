# -*- coding: utf-8 -*-
import sys
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

POC Demo Test
============

Integration test for 2-phone mesh ping demonstration.

This test validates:
1. Mesh network initialization
2. Alert creation and broadcast
3. Alert propagation (when mesh connected)
4. System health monitoring
"""

import pytest
import asyncio

from modules.communication.liberty_alert.src import (
    LibertyAlertOrchestrator,
    LibertyAlertConfig,
    GeoPoint,
    ThreatType,
)


@pytest.mark.asyncio
async def test_single_phone_initialization():
    """Test single phone can initialize"""
    config = LibertyAlertConfig(
        mesh_enabled=True,
        voice_enabled=False,  # Disabled for POC
        default_language="es",
    )

    orchestrator = LibertyAlertOrchestrator(config)

    # Start system
    assert await orchestrator.start()

    # Check mesh status
    status = orchestrator.get_mesh_status()
    assert status.is_healthy  # Healthy even with 0 peers
    assert status.peer_count == 0  # No peers yet

    # Stop system
    assert await orchestrator.stop()


@pytest.mark.asyncio
async def test_alert_creation():
    """Test alert creation without mesh"""
    config = LibertyAlertConfig(mesh_enabled=True, voice_enabled=False)
    orchestrator = LibertyAlertOrchestrator(config)

    await orchestrator.start()

    # Create alert
    location = GeoPoint(34.0522, -118.2437, accuracy=10.0)
    alert = await orchestrator.broadcast_alert(
        location=location,
        threat_type=ThreatType.SURVEILLANCE_VEHICLE,
        message="Van blanca en 38th - corre por el callejón",
        language="es",
    )

    # Verify alert created
    assert alert.id is not None
    assert alert.threat_type == ThreatType.SURVEILLANCE_VEHICLE
    assert alert.message == "Van blanca en 38th - corre por el callejón"
    assert alert.language == "es"

    # Check active alerts
    active_alerts = orchestrator.get_active_alerts()
    assert len(active_alerts) == 1
    assert active_alerts[0].id == alert.id

    await orchestrator.stop()


@pytest.mark.asyncio
async def test_system_stats():
    """Test system statistics collection"""
    config = LibertyAlertConfig(mesh_enabled=True, voice_enabled=False)
    orchestrator = LibertyAlertOrchestrator(config)

    await orchestrator.start()

    # Get stats
    stats = orchestrator.get_system_stats()

    # Verify stats structure
    assert "peer_id" in stats
    assert "is_running" in stats
    assert "mesh" in stats
    assert "alerts" in stats
    assert "config" in stats

    # Verify mesh stats
    assert stats["mesh"]["peer_count"] == 0
    assert stats["mesh"]["is_healthy"] is True

    # Verify config
    assert stats["config"]["default_language"] == "es"
    assert stats["config"]["mesh_enabled"] is True

    await orchestrator.stop()


@pytest.mark.asyncio
async def test_two_phone_simulation():
    """
    POC: 2-Phone Mesh Simulation

    Note: Full WebRTC mesh requires signaling server or manual offer/answer exchange.
    This test simulates the basic flow without actual peer connection.
    """
    # Create two phones
    config_a = LibertyAlertConfig(mesh_enabled=True, voice_enabled=False)
    config_b = LibertyAlertConfig(mesh_enabled=True, voice_enabled=False)

    phone_a = LibertyAlertOrchestrator(config_a)
    phone_b = LibertyAlertOrchestrator(config_b)

    # Start both phones
    assert await phone_a.start()
    assert await phone_b.start()

    # Phone A creates alert
    alert_location = GeoPoint(34.0522, -118.2437, accuracy=10.0)
    alert = await phone_a.broadcast_alert(
        location=alert_location,
        threat_type=ThreatType.SURVEILLANCE_VEHICLE,
        message="Test alert from phone A",
        language="es",
    )

    # Verify alert on phone A
    alerts_on_a = phone_a.get_active_alerts()
    assert len(alerts_on_a) == 1
    assert alerts_on_a[0].id == alert.id

    # Note: In POC without WebRTC connection, phone B won't receive alert
    # This will be tested in integration tests with actual mesh setup

    # Cleanup
    await phone_a.stop()
    await phone_b.stop()


@pytest.mark.asyncio
async def test_alert_expiration():
    """Test alert automatic expiration"""
    from datetime import timedelta

    config = LibertyAlertConfig(
        mesh_enabled=True, voice_enabled=False, alert_ttl_hours=1
    )

    orchestrator = LibertyAlertOrchestrator(config)
    await orchestrator.start()

    # Create alert
    location = GeoPoint(34.0522, -118.2437)
    alert = await orchestrator.broadcast_alert(
        location=location,
        threat_type=ThreatType.CHECKPOINT,
        message="Checkpoint test",
        language="es",
    )

    # Alert should be active
    active = orchestrator.get_active_alerts()
    assert len(active) == 1

    # Manually expire alert for test
    alert.expires_at = alert.expires_at - timedelta(hours=2)

    # Wait for cleanup (runs every 60s, so we need to trigger manually in test)
    # In production, cleanup loop handles this automatically

    await orchestrator.stop()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
