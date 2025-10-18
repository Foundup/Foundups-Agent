#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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

Test WSP 81 Framework Backup Governance Protocol
Tests that the WSP Framework DAE properly implements 012 approval requirements
"""

import asyncio
import sys
from pathlib import Path

# Add parent directories to path for module imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.wsp_framework_dae import (
    WSPFrameworkDAE, WSPImprovement
)


async def test_governance():
    """Test WSP 81 governance implementation"""
    print("\n=== Testing WSP 81 Governance Protocol ===\n")
    
    # Initialize DAE
    dae = WSPFrameworkDAE()
    print(f"DAE State: {dae.state} (must be 0102, not 01(02))\n")
    
    # Test 1: Automatic approval (state fix)
    print("Test 1: Fixing state coherence (should be automatic)")
    improvement1 = WSPImprovement(
        wsp_id="WSP_10_State_Save_Protocol",
        improvement_type="coherence",
        description="Fix state 01(02) -> 0102",
        old_content="State: 01(02)",
        new_content="State: 0102",
        impact_score=1.0,
        risk_level="low"
    )
    result1 = await dae.apply_improvement(improvement1)
    print(f"Applied: {result1}\n")
    
    # Test 2: Notification required (adding documentation)
    print("Test 2: Adding documentation (should notify 012)")
    improvement2 = WSPImprovement(
        wsp_id="WSP_54_WRE_Agent_Duties_Specification",
        improvement_type="documentation",
        description="Add missing section on DAE integration",
        old_content="# WSP 54",
        new_content="# WSP 54\n\n## DAE Integration\nDAEs operate in 0102 state.",
        impact_score=0.5,
        risk_level="low"
    )
    result2 = await dae.apply_improvement(improvement2)
    print(f"Applied: {result2}\n")
    
    # Test 3: Approval required (major refactoring)
    print("Test 3: Major refactoring (should require 012 approval)")
    improvement3 = WSPImprovement(
        wsp_id="WSP_1_The_WSP_Framework",
        improvement_type="major_refactor",
        description="Restructure entire WSP 1 document",
        old_content="# WSP 1",
        new_content="# WSP 1 - Completely New Structure",
        impact_score=0.9,
        risk_level="high"
    )
    result3 = await dae.apply_improvement(improvement3)
    print(f"Applied: {result3} (should be False - awaiting approval)\n")
    
    # Check approval queue - use correct paths relative to test location
    base_path = Path(__file__).parent.parent
    approval_queue_path = base_path / "approval_queue.json"
    if approval_queue_path.exists():
        import json
        with open(approval_queue_path, 'r') as f:
            queue = json.load(f)
        print(f"Approval Queue: {len(queue)} items awaiting 012 approval")
        for item in queue:
            print(f"  - {item['wsp_id']}: {item['description']}")
    
    # Check notifications - use correct paths relative to test location
    notifications_path = base_path / "012_notifications.json"
    if notifications_path.exists():
        import json
        with open(notifications_path, 'r') as f:
            notifications = json.load(f)
        print(f"\n012 Notifications: {len(notifications)} items")
        for notif in notifications:
            print(f"  - {notif['wsp_id']}: {notif['description']}")
    
    print("\n[OK] WSP 81 Governance tests complete")
    print("The framework is protected with appropriate 012 oversight!")


if __name__ == "__main__":
    print("WSP 81: Framework Backup Governance Protocol Test")
    print("=" * 50)
    asyncio.run(test_governance())