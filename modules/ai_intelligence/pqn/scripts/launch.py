#!/usr/bin/env python3
"""
PQN DAE Launch Script
Extracted from main.py per WSP 62 Large File Refactoring Protocol

Purpose: Launch PQN Orchestration (Research & Alignment)
Domain: ai_intelligence
Module: pqn
"""

import asyncio
import traceback


def run_pqn_dae():
    """Run PQN Orchestration (Research & Alignment)."""
    print("[INFO] Starting PQN Research DAE...")
    try:
        from modules.ai_intelligence.pqn_alignment.src.pqn_research_dae_orchestrator import PQNResearchDAEOrchestrator
        pqn_dae = PQNResearchDAEOrchestrator()
        asyncio.run(pqn_dae.run())
    except Exception as e:
        print(f"[ERROR]PQN DAE failed: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    run_pqn_dae()
