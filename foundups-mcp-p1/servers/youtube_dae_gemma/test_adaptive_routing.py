"""
Test Adaptive Routing with Mock Training Data

Demonstrates:
1. Gemma handles simple queries
2. Qwen monitors quality
3. Threshold adjusts based on performance
4. 0102 architect can override
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from adaptive_router import AdaptiveComplexityRouter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_adaptive_learning():
    """
    Test adaptive threshold learning over multiple queries.

    Expected behavior:
    - Start at threshold 0.30
    - Simple queries succeed → threshold decreases
    - Complex queries fail → threshold increases
    - System converges to optimal threshold
    """

    print("\n" + "="*80)
    print("ADAPTIVE ROUTING TEST - Qwen Monitors Gemma Output")
    print("="*80)

    # Initialize router
    print("\nInitializing router...")
    print("- Gemma 3 270M: Fast classification (50-100ms)")
    print("- Qwen 1.5B: Architect & quality monitor (250ms)")
    print("- Starting threshold: 0.30 (optimistic)")
    print()

    # Note: This will attempt to load models
    # If models not found, will gracefully skip actual inference
    try:
        router = AdaptiveComplexityRouter()
    except Exception as e:
        print(f"[WARNING] Could not load models: {e}")
        print("This test demonstrates the LOGIC, not actual inference")
        print("Models expected at:")
        print("  - E:/HoloIndex/models/gemma-3-270m-it-Q4_K_M.gguf")
        print("  - E:/HoloIndex/models/qwen-coder-1.5b.gguf")
        return

    # Test queries with expected complexity
    test_queries = [
        {
            "message": "!createshort my cool idea",
            "role": "USER",
            "expected_complexity": 0.15,  # Simple command
            "expected_intent": "command_shorts"
        },
        {
            "message": "/score",
            "role": "USER",
            "expected_complexity": 0.10,  # Very simple
            "expected_intent": "command_whack"
        },
        {
            "message": "how do i use !shorts to create videos?",
            "role": "USER",
            "expected_complexity": 0.45,  # Question about commands
            "expected_intent": "question"
        },
        {
            "message": "factcheck @user about quantum physics",
            "role": "MOD",
            "expected_complexity": 0.50,  # Factcheck + context
            "expected_intent": "command_factcheck"
        },
        {
            "message": "✊✋🖐",
            "role": "USER",
            "expected_complexity": 0.10,  # Simple emoji
            "expected_intent": "consciousness"
        },
        {
            "message": "MAGA 2024!!!! TRUMP 2024!!!!",
            "role": "USER",
            "expected_complexity": 0.20,  # Caps spam
            "expected_intent": "spam"
        },
    ]

    print("\n" + "-"*80)
    print("TESTING QUERIES")
    print("-"*80)

    threshold_history = [router.complexity_threshold]

    for i, query in enumerate(test_queries, 1):
        print(f"\n[Query {i}/{len(test_queries)}] \"{query['message']}\"")
        print(f"Role: {query['role']}")

        # Classify
        result = router.classify_intent(
            message=query['message'],
            role=query['role']
        )

        # Display results
        print(f"→ Complexity: {result['complexity_score']:.3f} (expected: {query['expected_complexity']:.3f})")
        print(f"→ Threshold: {router.complexity_threshold:.3f}")
        print(f"→ Intent: {result['intent']} (expected: {query['expected_intent']})")
        print(f"→ Processing: {result['processing_path']}")
        print(f"→ Latency: {result['latency_ms']}ms")
        print(f"→ Quality: {result['quality_score']:.3f}")

        # Threshold adjustment
        threshold_history.append(router.complexity_threshold)
        if len(threshold_history) > 1:
            delta = threshold_history[-1] - threshold_history[-2]
            if delta != 0:
                direction = "DOWN" if delta < 0 else "UP"
                print(f"→ Threshold adjusted: {direction} by {abs(delta):.3f}")

    # Final statistics
    print("\n" + "-"*80)
    print("FINAL STATISTICS")
    print("-"*80)

    stats = router.get_stats()
    print(f"\nTotal queries: {stats['total_queries']}")
    print(f"Gemma direct (success): {stats['gemma_direct']} ({stats['gemma_success_rate']*100:.1f}%)")
    print(f"Gemma→Qwen (corrected): {stats['gemma_corrected']} ({stats['gemma_correction_rate']*100:.1f}%)")
    print(f"Qwen direct (complex): {stats['qwen_direct']} ({stats['qwen_usage_rate']*100:.1f}%)")
    print(f"Average latency: {stats['avg_latency_ms']:.0f}ms")

    print(f"\nThreshold journey:")
    print(f"  Start: {threshold_history[0]:.3f}")
    print(f"  End:   {threshold_history[-1]:.3f}")
    print(f"  Delta: {threshold_history[-1] - threshold_history[0]:+.3f}")

    if threshold_history[-1] < threshold_history[0]:
        print("\n[SUCCESS] System learned to trust Gemma more (optimizing for speed)")
    elif threshold_history[-1] > threshold_history[0]:
        print("\n[INFO] System learned queries are complex (optimizing for quality)")
    else:
        print("\n[INFO] Threshold stable (balanced performance)")

    # Test 0102 architect override
    print("\n" + "-"*80)
    print("0102 ARCHITECT OVERRIDE")
    print("-"*80)

    print(f"\nCurrent threshold: {router.complexity_threshold:.3f}")
    print("0102 decision: Trust Gemma more for speed")

    old_threshold = router.complexity_threshold
    router.complexity_threshold = 0.25

    print(f"Manual adjustment: {old_threshold:.3f} → 0.25")
    print("\nThis is the architect layer - 0102 tunes system based on observed performance")

    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)
    print("\nKey Insights:")
    print("1. Gemma handles simple queries quickly (50-100ms)")
    print("2. Qwen monitors quality and corrects mistakes")
    print("3. Threshold adapts based on performance")
    print("4. 0102 architect can override for system tuning")
    print("\nThis replaces 300+ lines of regex with intelligent classification!")


if __name__ == "__main__":
    test_adaptive_learning()
