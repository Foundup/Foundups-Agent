#!/usr/bin/env python3
"""
Liberty Alert DAE Launch Script
Extracted from main.py per WSP 62 Large File Refactoring Protocol

Purpose: Launch Liberty Alert DAE (Community Protection Autonomous Entity)
Domain: communication
Module: liberty_alert
"""

import asyncio
import traceback


def run_liberty_alert_dae():
    """Run Liberty Alert DAE (Community Protection Autonomous Entity)."""
    print("[LIBERTY ALERT DAE] Starting Community Protection Autonomous Entity...")
    print("[LIBERTY ALERT DAE] 'L as resistance roots' - Liberty through community protection via mesh alerts")
    try:
        from modules.communication.liberty_alert.src.liberty_alert_dae import run_liberty_alert_dae as _run_dae
        asyncio.run(_run_dae())
    except Exception as e:
        print(f"[ERROR] Liberty Alert DAE failed: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    run_liberty_alert_dae()
