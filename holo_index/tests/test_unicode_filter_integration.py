#!/usr/bin/env python3
"""
Test Unicode Filter Integration - WSP 90 Compliance

Validates that agentic_output_throttler correctly filters emojis
for multi-agent output (0102/Qwen/Gemma).

WSP Compliance: WSP 90 (UTF-8 Enforcement), WSP 5 (Test Coverage)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from holo_index.output.agentic_output_throttler import AgenticOutputThrottler


def test_filter_with_emojis():
    """Test that emojis are replaced with ASCII equivalents"""
    throttler = AgenticOutputThrottler()

    # Test content with emojis (using Unicode escapes to avoid cp932 crash)
    test_content = "\u2705 [OK] System working\n\u274C [FAIL] Error occurred\n\U0001F4CA [METRICS] Confidence: 0.87"

    filtered_content, stats = throttler.filter_unicode_violations(test_content)

    print("[TEST 1] Filter with emojis")
    print(f"  Original length: {len(test_content)}")
    print(f"  Filtered length: {len(filtered_content)}")
    print(f"  Violations detected: {stats.get('violations', 0)}")
    print(f"  Replacements made: {stats.get('replaced', 0)}")
    print(f"  Agent: {stats.get('agent', 'unknown')}")
    print(f"  Filtered content: {filtered_content}")

    # Verify emojis were replaced
    assert "\u2705" not in filtered_content, "Checkmark emoji not replaced"
    assert "\u274C" not in filtered_content, "X emoji not replaced"
    assert "[OK]" in filtered_content, "Checkmark replacement missing"
    assert "[FAIL]" in filtered_content, "X replacement missing"

    print("[PASS] Emojis correctly replaced with ASCII\n")


def test_filter_without_emojis():
    """Test that content without emojis passes through unchanged"""
    throttler = AgenticOutputThrottler()

    test_content = "[OK] System working\n[FAIL] Error occurred\n[METRICS] Confidence: 0.87"

    filtered_content, stats = throttler.filter_unicode_violations(test_content)

    print("[TEST 2] Filter without emojis")
    print(f"  Violations detected: {stats.get('violations', 0)}")
    print(f"  Replacements made: {stats.get('replaced', 0)}")

    assert filtered_content == test_content, "Content should be unchanged"
    assert stats['violations'] == 0, "Should detect no violations"
    assert stats['replaced'] == 0, "Should make no replacements"

    print("[PASS] Clean content passes through unchanged\n")


def test_render_pipeline_integration():
    """Test that render_prioritized_output calls filter correctly"""
    throttler = AgenticOutputThrottler()

    # Set up error state with emoji (using Unicode escapes)
    throttler.set_system_state("error", Exception("Test error"))

    # Render should call filter internally
    output = throttler.render_prioritized_output(verbose=False)

    print("[TEST 3] Pipeline integration")
    print(f"  Output length: {len(output)}")
    print(f"  Agent ID: {throttler.agent_id}")

    # For 0102 agent, output should have emojis replaced
    # Check that common emojis are NOT in output
    assert "\u2705" not in output, "Checkmark emoji found in output"
    assert "\u274C" not in output, "X emoji found in output"
    assert "\U0001F534" not in output, "Red circle emoji found in output"

    print("[PASS] Pipeline correctly filters emojis\n")


def test_multi_agent_awareness():
    """Test that filter tracks which agent is requesting output"""
    # Test 0102 agent (default)
    throttler_0102 = AgenticOutputThrottler()
    test_content = "\u2705 Test"
    filtered, stats = throttler_0102.filter_unicode_violations(test_content)

    print("[TEST 4] Multi-agent awareness")
    print(f"  0102 agent ID: {throttler_0102.agent_id}")
    print(f"  Stats agent: {stats.get('agent', 'not_tracked')}")

    # Agent should be tracked in stats when replacements occur
    assert stats.get('agent') == '0102', f"Expected agent=0102, got {stats.get('agent')}"

    print("[PASS] Agent tracking working\n")


if __name__ == "__main__":
    print("=" * 60)
    print("Unicode Filter Integration Tests - WSP 90 Compliance")
    print("=" * 60 + "\n")

    try:
        test_filter_with_emojis()
        test_filter_without_emojis()
        test_render_pipeline_integration()
        test_multi_agent_awareness()

        print("=" * 60)
        print("[SUCCESS] All tests passed - Unicode filtering working")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n[FAIL] Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
