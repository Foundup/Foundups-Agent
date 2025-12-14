"""
Test Qwen Studio Engage Skill - Autonomous YouTube Comment Engagement

Simple test to verify the agentic Skillz execution.

Usage:
    python tests/test_qwen_studio_engage.py
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.communication.livechat.skills.qwen_studio_engage import execute_skill


async def main():
    """Test the Qwen Studio Engage skill"""

    print("\n" + "="*60)
    print("QWEN STUDIO ENGAGE - Autonomous Comment Engagement Test")
    print("="*60 + "\n")

    print("Configuration:")
    print("  Channel: UC-LSSlOZwpGIRIYihaz8zCw")
    print("  Max Comments: 3 (testing with small batch)")
    print("  Existing Browser: Yes (uses logged-in session)")
    print("  Mode: Agentic (Qwen analysis -> Gemma validation -> Vision execution)")
    print()

    # Execute skill
    result = await execute_skill(
        channel_id="UC-LSSlOZwpGIRIYihaz8zCw",
        max_comments_to_check=3,
        engagement_policy={
            "like_threshold": 0.7,
            "reply_threshold": 0.8,
            "ignore_spam": True,
            "brand_voice": "helpful, friendly, professional"
        },
        existing_browser=True
    )

    # Print results
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)

    if result['success']:
        print(f"\n[OK] Skill Execution: SUCCESS")
        print(f"\nMetrics:")
        print(f"  Comments Analyzed: {result['comments_analyzed']}")
        print(f"  Engagements Made: {result['engagements_made']}")
        print(f"  Likes Given: {result['likes_given']}")
        print(f"  Hearts Given: {result['hearts_given']}")
        print(f"  Replies Sent: {result['replies_sent']}")
        print(f"  Engagement Rate: {result['engagement_rate']:.1%}")
        print(f"  Total Duration: {result['duration_ms']}ms")

        print(f"\nDetailed Results:")
        for i, engagement in enumerate(result['results'], 1):
            print(f"\n  Comment {i}:")
            print(f"    Action: {engagement['action_taken']}")
            print(f"    Success: {engagement['success']}")
            if engagement['like_success']:
                print(f"    [+] Liked")
            if engagement['heart_success']:
                print(f"    [HEART] Creator Heart Given")
            if engagement['reply_success']:
                print(f"    [REPLY] Replied")
            if engagement['error']:
                print(f"    [ERROR] {engagement['error']}")

    else:
        print(f"\n[FAIL] Skill Execution: FAILED")
        print(f"  Error: {result.get('error', 'Unknown error')}")

    print("\n" + "="*60 + "\n")

    # Keep browser open - press Ctrl+C to exit
    print("[WAIT] Browser window staying open - Press Ctrl+C to exit...")
    try:
        await asyncio.sleep(999999)  # Wait indefinitely
    except KeyboardInterrupt:
        print("\n[EXIT] Test terminated by user")

    return 0 if result['success'] else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
