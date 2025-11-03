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

Liberty Alert - Open Source Off-Grid Alert System
=================================================

Real-time mesh alert system for community safety.

WSP 3 Domain: communication/
Purpose: Mesh networking and alert broadcasts for community protection
Status: POC Development
"""

from .liberty_alert_orchestrator import LibertyAlertOrchestrator
from .liberty_alert_dae import LibertyAlertDAE, run_liberty_alert_dae
from .mesh_network import MeshNetwork
from .alert_broadcaster import AlertBroadcaster
from .models import (
    Alert,
    GeoPoint,
    ThreatType,
    MeshMessage,
    LibertyAlertConfig,
    MeshStatus,
)

__version__ = "0.1.0-POC"

__all__ = [
    "LibertyAlertOrchestrator",
    "LibertyAlertDAE",
    "run_liberty_alert_dae",
    "MeshNetwork",
    "AlertBroadcaster",
    "Alert",
    "GeoPoint",
    "ThreatType",
    "MeshMessage",
    "LibertyAlertConfig",
    "MeshStatus",
]
