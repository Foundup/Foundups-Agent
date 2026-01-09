#!/usr/bin/env python3
"""
Quick test: Verify AI_overseer detects Unicode patterns in logs
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from modules.ai_intelligence.ai_overseer.src.ai_overseer import AIIntelligenceOverseer

# Sample log with Unicode tags
test_log = """
2025-10-26 12:32:07,342 - modules.communication.livechat.src.chat_sender - INFO - [U+1F4E4] Sending message: [U+1F31E] MAGA.exe crashed at [U+270A]. Ctrl+Alt+Consciousness: [U+270A][U+270B][U+1F590]me!
2025-10-26 12:32:08,123 - modules.communication.livechat.src.chat_sender - INFO - [OK] Message sent successfully
"""

print("=" * 80)
print("TESTING AI_OVERSEER UNICODE DETECTION")
print("=" * 80)

# Initialize
repo_root = Path(__file__).parent
overseer = AIIntelligenceOverseer(repo_root)

# Skill path
skill_path = repo_root / "modules/communication/livechat/skillz/youtube_daemon_monitor.json"

print(f"\n[TEST] Calling monitor_daemon with sample log...")
print(f"  Skill: {skill_path.name}")
print(f"  Log length: {len(test_log)} chars")

# Call monitor
result = overseer.monitor_daemon(
    bash_output=test_log,
    skill_path=skill_path,
    auto_fix=True,  # ENABLE AUTO-FIX!
    report_complex=True,
    announce_to_chat=False
)

print(f"\n[RESULTS]")
print(f"  Bugs detected: {result.get('bugs_detected', 0)}")
print(f"  Bugs fixed: {result.get('bugs_fixed', 0)}")
print(f"  Reports generated: {result.get('reports_generated', 0)}")

if result.get("bugs_detected", 0) > 0:
    print(f"\n[DETECTED BUGS]")
    for i, bug in enumerate(result.get("detected_bugs", []), 1):
        print(f"  {i}. {bug.get('pattern_name', 'unknown')}")
        print(f"     Match: {bug.get('match', 'N/A')}")
        mps = bug.get('config', {}).get('wsp_15_mps', {})
        if mps:
            print(f"     MPS: complexity={mps.get('complexity')}, priority={mps.get('priority')}")
            print(f"     Action: {bug.get('action', 'N/A')}")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
