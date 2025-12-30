# Test script for AutoGate
from pathlib import Path
import sys
import traceback

# Add project root to path
repo_root = Path("o:/Foundups-Agent")
sys.path.append(str(repo_root))

print("--- DIAGNOSTIC START ---")
try:
    from modules.ai_intelligence.ai_overseer.src.auto_gate import AutoGate
    from modules.ai_intelligence.ai_overseer.src.holo_adapter import HoloAdapter
    print("[OK] Imports successful.")
except Exception as e:
    print(f"[FATAL] Import failed: {e}")
    traceback.print_exc()
    sys.exit(1)

from dataclasses import dataclass
from typing import Any, List

@dataclass
class MockMissionType:
    name: str = "TARS_DEPLOY"
    value: str = "tars_deploy"

@dataclass
class MockPlan:
    mission_type: Any = MockMissionType()
    phases: List[Any] = None
    estimated_complexity: int = 5
    recommended_approach: str = "full_deployment"

# Create a mock plan that VIOLATES Smart Engagement (e.g. 100% reply rate)
phases = [
    {"phase": 1, "description": "Deploy global reply logic to ALL comments (100% rate)"},
    {"phase": 2, "description": "Ignore sentiment analysis"},
]
plan = MockPlan(phases=phases)

print("--- INITIALIZING AUTO-GATE ---")
try:
    adapter = HoloAdapter(repo_root)
    gate = AutoGate(repo_root, adapter)
    print("[OK] Initialization successful.")
except Exception as e:
    print(f"[FATAL] Init failed: {e}")
    traceback.print_exc()
    sys.exit(1)

print(f"--- TESTING PLAN: {plan.mission_type.value} ---")
print(f"Phases: {phases}")

print("\n--- RUNNING VALIDATION ---")
try:
    verdict = gate.validate_plan(plan)
    print(f"\n--- VERDICT: {verdict.status} ---")
    print(f"Warnings: {verdict.warnings}")
    print(f"Citations: {verdict.citations}")

    if verdict.status in ["WARN", "BLOCK"]:
        print("\n[SUCCESS] Gate correctly caught the violation!")
    else:
        print("\n[FAILURE] Gate let it pass (or LLM/Holo unavailable).")

except Exception as e:
    print(f"[FATAL] Validation failed: {e}")
    traceback.print_exc()
