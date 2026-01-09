"""
Test: Full Autonomous Engagement
LIKE + HEART all comments on YouTube Studio
"""
import asyncio
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(repo_root))

# Import the autonomous engagement system
sys.path.insert(0, str(Path(__file__).parent.parent))
from autonomous_engagement import AutonomousEngagement

async def main():
    print("\n" + "="*80)
    print(" AUTONOMOUS YOUTUBE STUDIO ENGAGEMENT")
    print(" Actions: LIKE + HEART all comments")
    print("="*80)

    # Initialize
    engagement = AutonomousEngagement(browser_port=9222)

    # Connect
    await engagement.connect()

    # Execute autonomous engagement
    result = await engagement.engage_all_comments(actions=['like', 'heart'])

    # Display results
    print("\n" + "="*80)
    print(" RESULTS")
    print("="*80)
    print(f"\nSession ID: {result['session_id']}")
    print(f"Total comments processed: {result['total_comments']}")
    print(f"\nLike actions:")
    print(f"  Success: {result['summary']['like']['success']}")
    print(f"  Failed: {result['summary']['like']['failed']}")
    print(f"  Total: {result['summary']['like']['total']}")
    print(f"\nHeart actions:")
    print(f"  Success: {result['summary']['heart']['success']}")
    print(f"  Failed: {result['summary']['heart']['failed']}")
    print(f"  Total: {result['summary']['heart']['total']}")
    print(f"\nScreenshot saved: {result['screenshot']}")

    print("\n" + "="*80)
    print(" NEXT STEP")
    print("="*80)
    print("\nManual verification:")
    print(f"1. Check screenshot: {result['screenshot']}")
    print("2. Navigate to: https://studio.youtube.com/.../comments/inbox")
    print("3. Verify all comments show Like/Heart counts")

    print("\n" + "="*80)

if __name__ == "__main__":
    asyncio.run(main())
