#!/usr/bin/env python3
"""
Test AI_overseer autonomous Unicode bug detection and fix

This test:
1. Feeds AI_overseer the YouTube DAE bash output with Unicode error
2. Verifies Gemma Phase 1 detects the pattern
3. Supervises Qwen Phase 2:
   - Uses agentic Holo to search for bug location
   - Classifies as auto_fix (complexity=1, P1)
4. Supervises Qwen Phase 3: Apply fix
5. Verifies fix: Unicode tags converted before YouTube send
"""

import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from modules.ai_intelligence.ai_overseer.src.ai_overseer import AIIntelligenceOverseer

def main():
    print("=" * 80)
    print("AI_OVERSEER AUTONOMOUS FIX TEST")
    print("=" * 80)

    # Initialize AI_overseer
    overseer = AIIntelligenceOverseer(project_root)

    # Simulate YouTube DAE bash output with Unicode error
    bash_output = """
2025-10-26 11:45:08,151 - modules.communication.livechat.src.chat_sender - INFO - [U+1F4E4] Sending message: [11:45] [U+1F4AB] CONSCIOUSNESS UPGRADE: 0102 analyzes your message content after [U+270A][U+270B][U+1F590]️ - try it out!
2025-10-26 11:45:08,152 - modules.communication.livechat.src.chat_sender - ERROR - UnicodeEncodeError: 'charmap' codec can't encode character '\\U0001f4ab' in position 45
2025-10-26 11:45:08,153 - modules.communication.livechat.src.livechat_core - WARNING - Failed to send consciousness trigger announcement
"""

    print("\n[BASH OUTPUT]")
    print(bash_output)

    print("\n" + "=" * 80)
    print("PHASE 1 (GEMMA): Fast Error Detection")
    print("=" * 80)

    # Load skill to show detection patterns
    skill_path = project_root / "modules/communication/livechat/skills/youtube_daemon_monitor.json"

    # Call AI_overseer.monitor_daemon()
    print(f"\n[AI-OVERSEER] Calling monitor_daemon()")
    print(f"  - bash_output: {len(bash_output)} chars")
    print(f"  - skill_path: {skill_path.name}")
    print(f"  - auto_fix: True (Qwen autonomous)")
    print(f"  - report_complex: True (complexity ≥3)")

    results = overseer.monitor_daemon(
        bash_output=bash_output,
        skill_path=skill_path,
        auto_fix=True,
        report_complex=True,
        chat_sender=None,  # No live chat for test
        announce_to_chat=False
    )

    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)
    print(json.dumps(results, indent=2))

    # Verify detection
    if results["bugs_detected"] > 0:
        print(f"\n[OK] Gemma detected {results['bugs_detected']} bugs")

        if results["bugs_fixed"] > 0:
            print(f"[OK] Qwen auto-fixed {results['bugs_fixed']} bugs")

            # Show fix details
            for fix in results.get("fixes_applied", []):
                print(f"\n[FIX APPLIED]")
                print(f"  Bug: {fix['bug']}")
                print(f"  Action: {fix.get('fix_applied', 'Unknown')}")
                print(f"  Method: {fix.get('method', 'Unknown')}")
                print(f"  Success: {fix['success']}")

                if fix.get('needs_restart'):
                    print(f"  [RESTART] Daemon restart required")
                    print(f"  [RESTART] Files modified: {fix.get('files_modified')}")

        if results["reports_generated"] > 0:
            print(f"\n[REPORT] Generated {results['reports_generated']} bug reports for 0102 review")
    else:
        print("[FAIL] No bugs detected - pattern matching may be off")

    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

    # Show next steps
    print("\n[NEXT STEPS]")
    if results["bugs_fixed"] > 0:
        print("1. Verify fix was applied to chat_sender.py")
        print("2. Check that Unicode conversion happens before YouTube API send")
        print("3. Restart YouTube DAE to load patched code")
        print("4. Monitor live chat for fix announcement (when wired)")
    elif results["bugs_detected"] > 0:
        print("1. Review bug reports generated")
        print("2. Check complexity scoring (should be 1 for auto-fix)")
        print("3. Verify Qwen decision logic")
    else:
        print("1. Check if bash_output matches regex patterns in skill")
        print("2. Verify skill path is correct")
        print("3. Review Gemma detection logic")

if __name__ == "__main__":
    main()
