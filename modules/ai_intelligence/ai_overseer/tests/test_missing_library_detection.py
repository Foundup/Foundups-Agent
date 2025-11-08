#!/usr/bin/env python3
"""
Test AI Overseer detection of missing Python library errors
"""

import sys
import os
from pathlib import Path

# Add project root to path for imports (WSP 3 compliant)
project_root = Path(__file__).parent.parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from modules.ai_intelligence.ai_overseer.src.daemon_monitor_mixin import DaemonMonitorMixin

class TestDaemonMonitor(DaemonMonitorMixin):
    def __init__(self):
        # Mock the required attributes
        self.repo_root = Path('.')
        self.fix_attempts = {}

    def test_missing_library_detection(self):
        """Test detection of missing library error"""

        # Sample log output with missing library error
        bash_output = """
2025-11-03 21:14:52,775 - root - ERROR - openai library not installed. Install with: pip install openai
2025-11-03 21:14:52,775 - modules.ai_intelligence.banter_engine.src.banter_engine - INFO - [OK] GPT-3.5 Turbo initialized for BanterEngine
2025-11-03 21:14:52,775 - modules.ai_intelligence.banter_engine.src.banter_engine - INFO - [OK] Populated 59 responses across 15 themes
"""

        # Load the YouTube daemon monitor skill (WSP 3 compliant path)
        skill_path = project_root / "modules" / "communication" / "livechat" / "skills" / "youtube_daemon_monitor.json"
        skill = self._load_daemon_skill(skill_path)

        if not skill:
            print("Failed to load skill")
            return False

        print("Loaded YouTube daemon monitor skill")

        # Test error detection
        detected_bugs = self._gemma_detect_errors(bash_output, skill)

        print(f"Detected {len(detected_bugs)} bugs")

        for bug in detected_bugs:
            print(f"Bug: {bug['pattern_name']}")
            print(f"   Matches: {bug.get('matches', [])}")
            print(f"   Config: {bug['config'].get('qwen_action', 'unknown')}")

        # Check if missing_python_library was detected
        library_bugs = [b for b in detected_bugs if b['pattern_name'] == 'missing_python_library']
        if library_bugs:
            print("Successfully detected missing Python library error!")
            bug = library_bugs[0]
            matches = bug.get('matches', [])
            if matches:
                print(f"Would install library: {matches[0]}")
            return True
        else:
            print("Failed to detect missing Python library error")
            return False

if __name__ == "__main__":
    tester = TestDaemonMonitor()
    success = tester.test_missing_library_detection()
    sys.exit(0 if success else 1)
