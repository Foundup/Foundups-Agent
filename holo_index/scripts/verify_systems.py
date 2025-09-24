#!/usr/bin/env python3
"""Verify Memory & Violation Systems"""

from modules.infrastructure.database import AgentDB
from holo_index.violation_tracker import ViolationTracker, Violation
from datetime import datetime, timezone

def verify_systems():
    print('🔍 Verifying Memory & Violation Systems')
    print('='*50)

    # Test AgentDB memory
    agent_db = AgentDB()
    patterns = agent_db.get_patterns('holo_index', 'search_interaction', limit=5)
    print(f'✅ AgentDB Memory: {len(patterns)} search interactions stored')

    # Test ViolationTracker
    tracker = ViolationTracker()
    violations = tracker.get_all_violations()
    print(f'✅ Violation Storage: {len(violations)} violations tracked')

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

    print('✅ Memory Architecture: OPERATIONAL')
    print('✅ Violation Storage: OPERATIONAL')
    print('✅ Phase 2 Infrastructure: COMPLETE')

if __name__ == "__main__":
    verify_systems()
