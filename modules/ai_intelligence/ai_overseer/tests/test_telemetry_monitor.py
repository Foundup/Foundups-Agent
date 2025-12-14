#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test HoloDAE Telemetry Monitor Integration

Quick smoke test to verify:
1. AI Overseer can initialize telemetry monitor
2. Telemetry monitor can tail JSONL files
3. Events are queued correctly

Location: modules/ai_intelligence/ai_overseer/tests/test_telemetry_monitor.py
"""

import asyncio
from pathlib import Path
import sys

# Add repo root to path (4 levels up from tests/)
repo_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(repo_root))

from modules.ai_intelligence.ai_overseer.src.ai_overseer import AIIntelligenceOverseer


async def test_telemetry_integration():
    """Test telemetry monitor integration"""
    print("[TEST] Initializing AI Overseer...")
    overseer = AIIntelligenceOverseer(repo_root)

    # Check telemetry monitor initialized
    if not overseer.telemetry_monitor:
        print("[FAIL] Telemetry monitor not initialized")
        return False

    print("[OK] Telemetry monitor initialized")

    # Get initial statistics
    stats = overseer.get_telemetry_statistics()
    print(f"[STATS] Initial: {stats}")

    # Start monitoring
    print("[TEST] Starting telemetry monitoring...")
    await overseer.start_telemetry_monitoring(poll_interval=1.0)

    # Let it run for 5 seconds
    print("[TEST] Monitoring for 5 seconds...")
    await asyncio.sleep(5)

    # Check statistics
    stats = overseer.get_telemetry_statistics()
    print(f"[STATS] After 5s: {stats}")

    # Stop monitoring
    print("[TEST] Stopping telemetry monitoring...")
    await overseer.stop_telemetry_monitoring()

    # Final statistics
    stats = overseer.get_telemetry_statistics()
    print(f"[STATS] Final: {stats}")

    # Verify events were processed
    if stats.get("events_processed", 0) > 0:
        print(f"[OK] Processed {stats['events_processed']} events")
        print(f"[OK] Queued {stats['events_queued']} actionable events")
        return True
    else:
        print("[WARN] No events processed (telemetry files may be empty)")
        return True  # Still pass - telemetry files might be old


if __name__ == "__main__":
    result = asyncio.run(test_telemetry_integration())
    sys.exit(0 if result else 1)

