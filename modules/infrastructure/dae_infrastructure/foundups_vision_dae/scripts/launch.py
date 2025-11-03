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

Vision DAE Launch Script
Extracted from main.py per WSP 62 Large File Refactoring Protocol

Purpose: Launch FoundUps Vision DAE (multi-modal pattern sensorium)
Domain: infrastructure
Module: foundups_vision_dae
"""

import asyncio
import logging
import traceback

logger = logging.getLogger(__name__)


def run_vision_dae(enable_voice: bool = False):
    """Run FoundUps Vision DAE (multi-modal pattern sensorium)."""
    print("[VISION] Starting FoundUps Vision DAE (Pattern Sensorium)...")
    from modules.infrastructure.instance_lock.src.instance_manager import get_instance_lock
    lock = get_instance_lock("vision_dae_monitor")

    duplicates = lock.check_duplicates()
    if duplicates:
        logger.warning("[VisionDAE] Duplicate instances detected")
        print("\n[VisionDAE] Duplicate Vision DAE instances detected!")
        for i, pid in enumerate(duplicates, 1):
            print(f"  {i}. PID {pid}")
        print("Use --no-lock to bypass duplicate protection.")
        return

    if not lock.acquire():
        logger.error("[VisionDAE] Failed to acquire instance lock")
        print("\n[VisionDAE] Failed to acquire Vision DAE instance lock!")
        print("Another Vision DAE instance is already running.")
        print("Use --no-lock to disable locking if this is intentional.")
        return

    try:
        from modules.infrastructure.dae_infrastructure.foundups_vision_dae.src.vision_dae import launch_vision_dae
        asyncio.run(launch_vision_dae(enable_voice=enable_voice))
    except Exception as e:
        print(f"[VisionDAE] Vision DAE failed: {e}")
        traceback.print_exc()
    finally:
        lock.release()
        logger.info("[VisionDAE] Instance lock released")


if __name__ == "__main__":
    run_vision_dae()
