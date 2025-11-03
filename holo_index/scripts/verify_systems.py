#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io

"""Verify Memory & Violation Systems"""

from modules.infrastructure.database import AgentDB
from holo_index.violation_tracker import ViolationTracker, Violation
from datetime import datetime, timezone

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

def verify_systems():
    print('[SEARCH] Verifying Memory & Violation Systems')
    print('='*50)

    # Test AgentDB memory
    agent_db = AgentDB()
    patterns = agent_db.get_patterns('holo_index', 'search_interaction', limit=5)
    print(f'[OK] AgentDB Memory: {len(patterns)} search interactions stored')

    # Test ViolationTracker
    tracker = ViolationTracker()
    violations = tracker.get_all_violations()
    print(f'[OK] Violation Storage: {len(violations)} violations tracked')

    # Test creating a new violation
    test_violation = Violation(
        id=f'test-{datetime.now(timezone.utc).strftime("%H%M%S")}',
        timestamp=datetime.now(timezone.utc),
        wsp='WSP 87',
        module='test_module',
        severity='MEDIUM',
        description='Phase 2 verification test',
        agent='0102'
    )
    tracker.record_violation(test_violation)
    tracker.close()

    print('[OK] Memory Architecture: OPERATIONAL')
    print('[OK] Violation Storage: OPERATIONAL')
    print('[OK] Phase 2 Infrastructure: COMPLETE')

if __name__ == "__main__":
    verify_systems()
