#!/usr/bin/env python3
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

EvadeNet Launch Script
Extracted from main.py per WSP 62 Large File Refactoring Protocol

Purpose: Launch Liberty Alert Mesh Alert System (Community Protection)
Domain: infrastructure
Module: evade_net
"""

import asyncio
import traceback

# WRE CoT preflight - recursive enforcement after watch period
try:
    from modules.infrastructure.wre_core.src.dae_preflight import preflight_guard
except ImportError:
    def preflight_guard(name, quiet=True):
        def decorator(func):
            return func
        return decorator


@preflight_guard("evade_net_dae")
def run_evade_net():
    """Run Liberty Alert Mesh Alert System (Community Protection)."""
    print("[WARN] Starting Liberty Alert - Mesh Alert System...")
    print("[INFO] Offline P2P alerts for community protection")
    try:
        from modules.communication.liberty_alert.src.liberty_alert_orchestrator import LibertyAlertOrchestrator
        from modules.communication.liberty_alert.src.models import LibertyAlertConfig

        # Configure Liberty Alert
        config = LibertyAlertConfig(
            mesh_enabled=True,
            voice_enabled=True,
            default_language="es",
            alert_radius_km=5.0,
        )

        orchestrator = LibertyAlertOrchestrator(config)
        asyncio.run(orchestrator.run())
    except Exception as e:
        print(f"[ERROR]Liberty Alert failed: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    run_evade_net()
