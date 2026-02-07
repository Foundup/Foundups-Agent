#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Standalone tests for OpenClaw DAE - runs without FastAPI dependency.

Directly imports openclaw_dae.py to test the autonomy loop:
  Intent -> Preflight -> Plan -> Permission -> Execute -> Validate -> Remember
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Direct import (bypass __init__.py which requires fastapi)
from modules.communication.moltbot_bridge.src.openclaw_dae import (
    OpenClawDAE,
    IntentCategory,
    AutonomyTier,
    OpenClawIntent,
    ExecutionPlan,
)


def run_tests():
    dae = OpenClawDAE(repo_root=project_root)
    passed = 0
    failed = 0
    errors = []

    def check(name, condition, msg=""):
        nonlocal passed, failed, errors
        if condition:
            passed += 1
            print(f"  PASS: {name}")
        else:
            failed += 1
            errors.append(f"{name}: {msg}")
            print(f"  FAIL: {name} - {msg}")

    # ---- Layer 0: Intent Classification ----
    print("\n=== Layer 0: Intent Classification ===")

    intent = dae.classify_intent("Explain how the WRE orchestrator works and describe what it does", "user123", "telegram", "s1")
    check("query_intent", intent.category == IntentCategory.QUERY,
          f"Expected QUERY, got {intent.category}")
    check("query_domain", intent.target_domain == "holo_index",
          f"Expected holo_index, got {intent.target_domain}")

    intent = dae.classify_intent("Run the test suite and fix errors", "user123", "whatsapp", "s2")
    check("command_intent", intent.category == IntentCategory.COMMAND,
          f"Expected COMMAND, got {intent.category}")

    intent = dae.classify_intent("Show me the system status and health check", "u", "discord", "s3")
    check("monitor_intent", intent.category == IntentCategory.MONITOR,
          f"Expected MONITOR, got {intent.category}")

    intent = dae.classify_intent("Schedule a video for tomorrow at 3pm", "u", "whatsapp", "s4")
    check("schedule_intent", intent.category == IntentCategory.SCHEDULE,
          f"Expected SCHEDULE, got {intent.category}")

    intent = dae.classify_intent("Post a comment and reply to viewers", "u", "telegram", "s5")
    check("social_intent", intent.category == IntentCategory.SOCIAL,
          f"Expected SOCIAL, got {intent.category}")

    intent = dae.classify_intent("Hello there!", "user123", "whatsapp", "s6")
    check("conversation_fallback", intent.category == IntentCategory.CONVERSATION,
          f"Expected CONVERSATION, got {intent.category}")

    intent = dae.classify_intent("Hello", "@UnDaoDu", "discord", "s7")
    check("commander_detection", intent.is_authorized_commander is True,
          "Expected True for @UnDaoDu")

    intent = dae.classify_intent("Hello", "random_user_42", "telegram", "s8")
    check("non_commander", intent.is_authorized_commander is False,
          "Expected False for random_user_42")

    # ---- Layer 1: WSP Preflight ----
    print("\n=== Layer 1: WSP Preflight ===")

    intent = OpenClawIntent(
        raw_message="Run deploy", category=IntentCategory.COMMAND,
        confidence=0.8, sender="random", channel="tg",
        session_key="s", is_authorized_commander=False)
    check("command_blocked_non_commander",
          dae._wsp_preflight(intent) is False,
          "COMMAND should be blocked for non-commanders")

    intent = OpenClawIntent(
        raw_message="What is WSP?", category=IntentCategory.QUERY,
        confidence=0.7, sender="random", channel="discord",
        session_key="s", is_authorized_commander=False)
    check("query_allowed_anyone",
          dae._wsp_preflight(intent) is True,
          "QUERY should be allowed for anyone")

    intent = OpenClawIntent(
        raw_message="Restart server", category=IntentCategory.SYSTEM,
        confidence=0.9, sender="hacker123", channel="telegram",
        session_key="s", is_authorized_commander=False)
    check("system_blocked_non_commander",
          dae._wsp_preflight(intent) is False,
          "SYSTEM should be blocked for non-commanders")

    # ---- Layer 2: Permission Gate ----
    print("\n=== Layer 2: Permission Gate ===")

    intent = OpenClawIntent(
        raw_message="hello", category=IntentCategory.QUERY,
        confidence=0.5, sender="user", channel="discord",
        session_key="s", is_authorized_commander=False)
    tier = dae._resolve_autonomy_tier(intent)
    check("non_commander_advisory",
          tier == AutonomyTier.ADVISORY,
          f"Expected ADVISORY, got {tier}")

    intent = OpenClawIntent(
        raw_message="search", category=IntentCategory.QUERY,
        confidence=0.8, sender="@UnDaoDu", channel="whatsapp",
        session_key="s", is_authorized_commander=True)
    tier = dae._resolve_autonomy_tier(intent)
    check("commander_query_metrics",
          tier == AutonomyTier.METRICS,
          f"Expected METRICS, got {tier}")

    intent = OpenClawIntent(
        raw_message="hack", category=IntentCategory.COMMAND,
        confidence=0.9, sender="bad", channel="tg",
        session_key="s", is_authorized_commander=False)
    check("permission_blocks_elevated",
          dae._check_permission_gate(intent, AutonomyTier.SOURCE) is False,
          "SOURCE tier should be blocked for non-commanders")

    intent = OpenClawIntent(
        raw_message="hello", category=IntentCategory.CONVERSATION,
        confidence=0.5, sender="anyone", channel="discord",
        session_key="s", is_authorized_commander=False)
    check("advisory_always_passes",
          dae._check_permission_gate(intent, AutonomyTier.ADVISORY) is True,
          "ADVISORY should always pass")

    # ---- Layer 3: Security Validation ----
    print("\n=== Layer 3: Security Validation ===")

    intent = OpenClawIntent(
        raw_message="test", category=IntentCategory.QUERY,
        confidence=0.5, sender="u", channel="t",
        session_key="s", is_authorized_commander=False)
    plan = ExecutionPlan(
        intent=intent, route="test",
        permission_level=AutonomyTier.ADVISORY,
        wsp_preflight_passed=True)
    result = dae._validate_and_remember(plan, "Key: AIzaSyB1234567890abcdef", 10)
    check("security_filter_secrets",
          "REDACTED" in result.response_text,
          f"Expected REDACTED, got: {result.response_text[:50]}")
    check("security_violation_logged",
          len(result.wsp_violations) > 0,
          "Expected WSP violations for secret leak")

    result2 = dae._validate_and_remember(plan, "", 5)
    check("empty_response_caught",
          "unable to generate" in result2.response_text.lower() or len(result2.wsp_violations) > 0,
          "Empty response should be caught")

    # ---- Layer 4: End-to-End Process ----
    print("\n=== Layer 4: End-to-End Process ===")

    resp = asyncio.run(dae.process("Hey how are you?", "user123", "telegram"))
    check("e2e_conversation",
          len(resp) > 0 and ("0102" in resp or "Digital Twin" in resp),
          f"Expected Digital Twin response, got: {resp[:80]}")

    resp = asyncio.run(dae.process("Run the deploy script now", "random_user", "whatsapp"))
    check("e2e_blocked_command_downgrades",
          len(resp) > 0,
          "Blocked command should still return a response")

    resp = asyncio.run(dae.process("Show system status and health", "user123", "discord"))
    check("e2e_monitor_status",
          "status" in resp.lower() or "Status" in resp,
          f"Expected status report, got: {resp[:80]}")

    # ---- Summary ----
    total = passed + failed
    print(f"\n{'='*50}")
    print(f"  RESULTS: {passed}/{total} passed, {failed} failed")
    print(f"{'='*50}")
    if errors:
        print("\nFailures:")
        for e in errors:
            print(f"  - {e}")

    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
