#!/usr/bin/env python3
"""
AMO DAE Launch Script
Extracted from main.py per WSP 62 Large File Refactoring Protocol

Purpose: Launch AMO DAE (Autonomous Moderation Operations)
Domain: communication
Module: auto_meeting_orchestrator
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


@preflight_guard("auto_meeting_orchestrator_dae")
def run_amo_dae():
    """Run AMO DAE (Autonomous Moderation Operations)."""
    print("[AMO] Starting AMO DAE (Autonomous Moderation Operations)...")
    try:
        from modules.communication.livechat.src.auto_moderator_dae import AutoModeratorDAE
        dae = AutoModeratorDAE()
        asyncio.run(dae.run())
    except Exception as e:
        print(f"[AMO-ERROR] AMO DAE failed: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    run_amo_dae()
