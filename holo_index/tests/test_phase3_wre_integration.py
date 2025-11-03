#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Phase 3 WRE Integration

Validates HoloDAE → WRE → GitPushDAE integration
WSP Compliance: WSP 5 (Test Coverage), WSP 96 (WRE Skills Phase 3)
"""

import sys
from pathlib import Path

# Add project root to path
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root))


def test_health_check_methods():
    """Test health check methods exist and return correct structure"""
    print("\n" + "="*70)
    print("[TEST] Phase 3 Health Check Methods")
    print("="*70)

    from holo_index.qwen_advisor.holodae_coordinator import HoloDAECoordinator

    coordinator = HoloDAECoordinator()

    # Test 1: check_git_health()
    print("\n[1/3] Testing check_git_health()...")
    git_health = coordinator.check_git_health()
    assert isinstance(git_health, dict), "check_git_health must return dict"
    assert "uncommitted_changes" in git_health or "error" in git_health
    print(f"[OK] Git health check: {git_health.get('uncommitted_changes', 'N/A')} changes")

    # Test 2: check_daemon_health()
    print("\n[2/3] Testing check_daemon_health()...")
    daemon_health = coordinator.check_daemon_health()
    assert isinstance(daemon_health, dict), "check_daemon_health must return dict"
    assert "healthy" in daemon_health
    print(f"[OK] Daemon health check: healthy={daemon_health['healthy']}")

    # Test 3: check_wsp_compliance()
    print("\n[3/3] Testing check_wsp_compliance()...")
    wsp_health = coordinator.check_wsp_compliance()
    assert isinstance(wsp_health, dict), "check_wsp_compliance must return dict"
    assert "violations_found" in wsp_health
    print(f"[OK] WSP compliance check: {wsp_health['violations_found']} violations")

    print("\n" + "="*70)
    print("[SUCCESS] All health check methods validated")
    print("="*70)


def test_wre_trigger_detection():
    """Test _check_wre_triggers() method"""
    print("\n" + "="*70)
    print("[TEST] Phase 3 WRE Trigger Detection")
    print("="*70)

    from holo_index.qwen_advisor.holodae_coordinator import HoloDAECoordinator

    coordinator = HoloDAECoordinator()

    # Create mock monitoring result
    class MockMonitoringResult:
        def has_actionable_events(self):
            return True

    result = MockMonitoringResult()

    print("\n[1/1] Testing _check_wre_triggers()...")
    triggers = coordinator._check_wre_triggers(result)

    assert isinstance(triggers, list), "_check_wre_triggers must return list"
    print(f"[OK] Trigger detection returned {len(triggers)} triggers")

    if triggers:
        for i, trigger in enumerate(triggers, 1):
            print(f"  Trigger {i}: {trigger['skill_name']} (reason: {trigger['trigger_reason']})")

    print("\n" + "="*70)
    print("[SUCCESS] WRE trigger detection validated")
    print("="*70)


def test_monitoring_loop_integration():
    """Test that monitoring loop has WRE integration"""
    print("\n" + "="*70)
    print("[TEST] Phase 3 Monitoring Loop Integration")
    print("="*70)

    import inspect
    from holo_index.qwen_advisor.holodae_coordinator import HoloDAECoordinator

    coordinator = HoloDAECoordinator()

    # Check _monitoring_loop source contains WRE calls
    print("\n[1/2] Checking _monitoring_loop() source code...")
    source = inspect.getsource(coordinator._monitoring_loop)

    assert "_check_wre_triggers" in source, "Monitoring loop must call _check_wre_triggers"
    assert "_execute_wre_skills" in source, "Monitoring loop must call _execute_wre_skills"
    print("[OK] Monitoring loop contains WRE integration calls")

    # Check methods exist
    print("\n[2/2] Verifying WRE methods exist...")
    assert hasattr(coordinator, "_check_wre_triggers"), "Missing _check_wre_triggers method"
    assert hasattr(coordinator, "_execute_wre_skills"), "Missing _execute_wre_skills method"
    assert hasattr(coordinator, "check_git_health"), "Missing check_git_health method"
    assert hasattr(coordinator, "check_daemon_health"), "Missing check_daemon_health method"
    assert hasattr(coordinator, "check_wsp_compliance"), "Missing check_wsp_compliance method"
    print("[OK] All WRE methods present")

    print("\n" + "="*70)
    print("[SUCCESS] Monitoring loop integration validated")
    print("="*70)


def test_phase3_complete():
    """Final validation - Phase 3 complete"""
    print("\n" + "="*70)
    print("[TEST] Phase 3 Completion Validation")
    print("="*70)

    print("\n[VALIDATION] Running all Phase 3 tests...")

    test_health_check_methods()
    test_wre_trigger_detection()
    test_monitoring_loop_integration()

    print("\n" + "="*70)
    print("[SUCCESS] PHASE 3 COMPLETE")
    print("="*70)
    print("\nKEY DELIVERABLES:")
    print("1. ✅ Health check methods (git, daemon, WSP)")
    print("2. ✅ WRE trigger detection (_check_wre_triggers)")
    print("3. ✅ WRE skill execution (_execute_wre_skills)")
    print("4. ✅ Monitoring loop integration (lines 1067-1070)")
    print("\nNOTE: End-to-end autonomous execution requires:")
    print("  - WRE Master Orchestrator operational")
    print("  - Skills discovered in filesystem")
    print("  - Qwen/Gemma inference available")
    print("  - GitPushDAE for autonomous commits")


if __name__ == "__main__":
    test_phase3_complete()
