#!/usr/bin/env python3
"""
Full Chain: LinkedIn Digital Twin Flow (L0 → L1 → L2 → L3)

Combines all layers into a complete Digital Twin engagement flow:
- L0: Context Gate (validate target post)
- L1: Comment (post 012 comment with @mentions)
- L2: Identity Likes (FoundUp identities like the comment)
- L3: Schedule Repost (repost with thoughts, scheduled)

Test Modes:
    --selenium: Run full chain with Selenium
    --dry-run: Validate all layers without side effects
    --stop-at: Stop after specific layer (0, 1, 2, or 3)
    --info: Show chain info only

Usage:
    python -m modules.platform_integration.linkedin_agent.tests.test_full_chain --selenium
    python -m modules.platform_integration.linkedin_agent.tests.test_full_chain --selenium --dry-run
    python -m modules.platform_integration.linkedin_agent.tests.test_full_chain --selenium --stop-at 1
"""

import argparse
import os
import sys
import time
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))

# Import layer tests
from modules.platform_integration.linkedin_agent.tests.test_layer0_context_gate import test_layer0_selenium
from modules.platform_integration.linkedin_agent.tests.test_layer1_comment import test_layer1_selenium
from modules.platform_integration.linkedin_agent.tests.test_layer2_identity_likes import test_layer2_selenium
from modules.platform_integration.linkedin_agent.tests.test_layer3_schedule_repost import test_layer3_selenium


def _pulse(event: str, flow_id: str, layer: str = "", step: str = "", status: str = "", error: str = "", duration_ms: int = 0) -> None:
    """DAEmon pulse point logging (core only)."""
    payload = {
        "flow_id": flow_id,
        "layer": layer,
        "step": step,
        "status": status,
        "error": error,
        "duration_ms": duration_ms,
    }
    print(f"[{event}] {payload}")


def _is_rate_limit_error(error_text: str) -> bool:
    lowered = (error_text or "").lower()
    return any(token in lowered for token in ["rate limit", "too many", "throttle", "temporarily restricted"])

def _layer_delay_seconds() -> float:
    value = os.getenv("LINKEDIN_LAYER_DELAY_SEC", "4")
    try:
        return max(0.0, float(value))
    except ValueError:
        return 4.0

def _layer_pause(label: str) -> None:
    delay = _layer_delay_seconds()
    if delay <= 0:
        return
    print(f"[PAUSE] {label} ({delay:.1f}s)")
    time.sleep(delay)

def run_full_chain(dry_run: bool = False, stop_at: int = 3) -> dict:
    """
    Execute the full Digital Twin flow.
    
    Args:
        dry_run: If True, validate without side effects
        stop_at: Stop after this layer (0-3)
    
    Returns:
        dict with overall results and per-layer results
    """
    flow_id = f"ln_flow_{int(time.time())}"
    print("\n" + "=" * 60)
    print("LINKEDIN DIGITAL TWIN - FULL CHAIN TEST")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'} | Stop at: L{stop_at}")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 60)
    _pulse("BATCH_START", flow_id, status="started")

    results = {
        "success": False,
        "layers_completed": 0,
        "layers_attempted": 0,
        "dry_run": dry_run,
        "stop_at": stop_at,
        "layer_results": {},
        "errors": []
    }

    failure_streak = 0

    # Layer 0: Context Gate
    print("\n" + "-" * 60)
    print("LAYER 0: CONTEXT GATE")
    print("-" * 60)
    _layer_pause("before L0")
    results["layers_attempted"] += 1
    
    try:
        l0_result = test_layer0_selenium()
        results["layer_results"]["L0"] = l0_result
        
        if l0_result.get("success"):
            results["layers_completed"] += 1
            _pulse("PROGRESS", flow_id, layer="L0", status="complete")
            failure_streak = 0
            print("[L0] OK Context Gate passed")
        else:
            print("[L0] FAIL Context Gate failed")
            results["errors"].append(f"L0: {l0_result.get('error', 'Unknown')}")
            failure_streak += 1
            _pulse("PROGRESS", flow_id, layer="L0", status="failed", error=l0_result.get("error", "Unknown"))
            if _is_rate_limit_error(l0_result.get("error", "")):
                _pulse("RATE_LIMIT", flow_id, layer="L0", status="detected")
            if failure_streak >= 3:
                _pulse("FAILURE_STREAK", flow_id, layer="L0", status="streak_3")
            return results
    except Exception as e:
        print(f"[L0] ERROR Exception: {e}")
        results["errors"].append(f"L0 exception: {str(e)}")
        failure_streak += 1
        _pulse("PROGRESS", flow_id, layer="L0", status="exception", error=str(e))
        if _is_rate_limit_error(str(e)):
            _pulse("RATE_LIMIT", flow_id, layer="L0", status="detected")
        if failure_streak >= 3:
            _pulse("FAILURE_STREAK", flow_id, layer="L0", status="streak_3")
        return results

    if stop_at == 0:
        results["success"] = True
        return results

    if not l0_result.get("ai_gate_passed", True):
        reason = "promoted/repost gate" if (l0_result.get("is_promoted") or l0_result.get("is_repost")) else "ai_gate"
        print(f"[L0] SKIP Remaining layers due to {reason}")
        results["success"] = True
        return results

    _layer_pause("after L0")

    # Layer 1: Comment
    print("\n" + "-" * 60)
    print("LAYER 1: COMMENT")
    print("-" * 60)
    _layer_pause("before L1")
    results["layers_attempted"] += 1
    
    try:
        l1_result = test_layer1_selenium(dry_run=dry_run, ai_gate_passed=l0_result.get("ai_gate_passed", True))
        results["layer_results"]["L1"] = l1_result
        
        if l1_result.get("success"):
            results["layers_completed"] += 1
            _pulse("PROGRESS", flow_id, layer="L1", status="complete")
            failure_streak = 0
            print("[L1] OK Comment posted")
        else:
            print("[L1] FAIL Comment failed")
            results["errors"].append(f"L1: {l1_result.get('error', 'Unknown')}")
            failure_streak += 1
            _pulse("PROGRESS", flow_id, layer="L1", status="failed", error=l1_result.get("error", "Unknown"))
            if _is_rate_limit_error(l1_result.get("error", "")):
                _pulse("RATE_LIMIT", flow_id, layer="L1", status="detected")
            if failure_streak >= 3:
                _pulse("FAILURE_STREAK", flow_id, layer="L1", status="streak_3")
            return results
    except Exception as e:
        print(f"[L1] ERROR Exception: {e}")
        results["errors"].append(f"L1 exception: {str(e)}")
        failure_streak += 1
        _pulse("PROGRESS", flow_id, layer="L1", status="exception", error=str(e))
        if _is_rate_limit_error(str(e)):
            _pulse("RATE_LIMIT", flow_id, layer="L1", status="detected")
        if failure_streak >= 3:
            _pulse("FAILURE_STREAK", flow_id, layer="L1", status="streak_3")
        return results

    if stop_at == 1:
        results["success"] = True
        return results

    _layer_pause("after L1")

    # Layer 2: Identity Likes
    print("\n" + "-" * 60)
    print("LAYER 2: IDENTITY LIKES")
    print("-" * 60)
    _layer_pause("before L2")
    results["layers_attempted"] += 1
    
    try:
        l2_result = test_layer2_selenium(dry_run=dry_run)
        results["layer_results"]["L2"] = l2_result
        
        if l2_result.get("success"):
            results["layers_completed"] += 1
            _pulse("PROGRESS", flow_id, layer="L2", status="complete")
            failure_streak = 0
            print(f"[L2] OK {l2_result.get('likes_applied', 0)} likes applied")
        else:
            print("[L2] WARN Identity likes partial/failed")
            # Don't fail entire chain for L2 issues
            failure_streak += 1
            _pulse("PROGRESS", flow_id, layer="L2", status="partial", error="identity_likes_partial")
            if failure_streak >= 3:
                _pulse("FAILURE_STREAK", flow_id, layer="L2", status="streak_3")
    except Exception as e:
        print(f"[L2] WARN Exception (non-fatal): {e}")
        results["errors"].append(f"L2 exception: {str(e)}")
        failure_streak += 1
        _pulse("PROGRESS", flow_id, layer="L2", status="exception", error=str(e))
        if _is_rate_limit_error(str(e)):
            _pulse("RATE_LIMIT", flow_id, layer="L2", status="detected")
        if failure_streak >= 3:
            _pulse("FAILURE_STREAK", flow_id, layer="L2", status="streak_3")

    if stop_at == 2:
        results["success"] = results["layers_completed"] >= 2
        return results

    _layer_pause("after L2")

    # Layer 3: Schedule Repost
    print("\n" + "-" * 60)
    print("LAYER 3: SCHEDULE REPOST")
    print("-" * 60)
    _layer_pause("before L3")
    results["layers_attempted"] += 1
    
    try:
        l3_result = test_layer3_selenium(dry_run=dry_run)
        results["layer_results"]["L3"] = l3_result
        
        if l3_result.get("success"):
            results["layers_completed"] += 1
            _pulse("PROGRESS", flow_id, layer="L3", status="complete")
            failure_streak = 0
            scheduled_time = l3_result.get("scheduled_time", "N/A")
            print(f"[L3] OK Repost scheduled for: {scheduled_time}")
        else:
            print("[L3] FAIL Schedule repost failed")
            results["errors"].append(f"L3: {l3_result.get('error', 'Unknown')}")
            failure_streak += 1
            _pulse("PROGRESS", flow_id, layer="L3", status="failed", error=l3_result.get("error", "Unknown"))
            if _is_rate_limit_error(l3_result.get("error", "")):
                _pulse("RATE_LIMIT", flow_id, layer="L3", status="detected")
            if failure_streak >= 3:
                _pulse("FAILURE_STREAK", flow_id, layer="L3", status="streak_3")
    except Exception as e:
        print(f"[L3] ERROR Exception: {e}")
        results["errors"].append(f"L3 exception: {str(e)}")
        failure_streak += 1
        _pulse("PROGRESS", flow_id, layer="L3", status="exception", error=str(e))
        if _is_rate_limit_error(str(e)):
            _pulse("RATE_LIMIT", flow_id, layer="L3", status="detected")
        if failure_streak >= 3:
            _pulse("FAILURE_STREAK", flow_id, layer="L3", status="streak_3")

    # Final summary
    results["success"] = results["layers_completed"] >= 3

    print("\n" + "=" * 60)
    print("FULL CHAIN SUMMARY")
    print("=" * 60)
    print(f"Layers completed: {results['layers_completed']}/{results['layers_attempted']}")
    print(f"Overall success: {'OK' if results['success'] else 'FAIL'}")
    
    if results["errors"]:
        print(f"Errors: {results['errors']}")

    _pulse("BATCH_COMPLETE", flow_id, status="complete", error="; ".join(results["errors"]))
    return results


def test_full_chain_info():
    """Show chain info without running."""
    print("\n[FULL CHAIN] LinkedIn Digital Twin Flow")
    print("=" * 60)
    print("")
    print("Layers:")
    print("  L0: Context Gate")
    print("      - Validate LinkedIn feed")
    print("      - Extract author, check AI keywords")
    print("")
    print("  L1: Comment (LIVE)")
    print("      - Post 012 Digital Twin comment")
    print("      - @mention handling and validation")
    print("      - Most-recent guard")
    print("")
    print("  L2: Identity Likes")
    print("      - Switch through FoundUp identities")
    print("      - Like 012 comment from each identity")
    print("      - Return to 012")
    print("")
    print("  L3: Schedule Repost")
    print("      - Repost with thoughts")
    print("      - Schedule for future (4-6 hours)")
    print("      - Confirm and verify")
    print("")
    print("Flow: L0 → L1 → L2 → L3")
    print("")
    print("Usage:")
    print("  python -m ...test_full_chain --selenium")
    print("  python -m ...test_full_chain --selenium --dry-run")
    print("  python -m ...test_full_chain --selenium --stop-at 1")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Full Chain: LinkedIn Digital Twin Test")
    parser.add_argument("--selenium", action="store_true", help="Run with Selenium")
    parser.add_argument("--dry-run", action="store_true", help="Validate without side effects")
    parser.add_argument("--stop-at", type=int, default=3, choices=[0, 1, 2, 3],
                        help="Stop after layer N (0-3)")
    parser.add_argument("--info", action="store_true", help="Show chain info only")

    args = parser.parse_args()

    if args.info:
        test_full_chain_info()
    elif args.selenium:
        result = run_full_chain(dry_run=args.dry_run, stop_at=args.stop_at)
        sys.exit(0 if result["success"] else 1)
    else:
        test_full_chain_info()
        print("\n[TIP] Add --selenium to run the test")
