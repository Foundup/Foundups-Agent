"""
Test: Teaching System - 012 teaches 0102 how to engage with comments

Workflow:
1. TEACH MODE: 012 demonstrates LIKE action (15s recording)
2. System stores pattern with DOM ground truth
3. REPLAY MODE: 0102 replicates action with verification
4. Compare DOM state changes to validate success

WSP Compliance:
- WSP 96: WRE Skills with recursive learning
- WSP 48: Self-improvement through demonstration
"""

import asyncio
import sys
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(repo_root))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from modules.communication.video_comments.skills.qwen_studio_engage.teaching_system import TeachingSystem


async def test_teaching_workflow():
    """
    Full teaching workflow test

    Phase 1: TEACH MODE - 012 demonstrates
    Phase 2: REPLAY MODE - 0102 replicates
    """

    print("\n" + "="*80)
    print(" 0102 TEACHING SYSTEM - Learning from Demonstration")
    print(" 012 demonstrates → 0102 learns → 0102 replicates")
    print("="*80)

    # Connect to existing Chrome
    print("\n[1] Connecting to Chrome on port 9222...")
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=chrome_options)
    print("[OK] Connected")

    # Navigate to YouTube Studio
    target_url = "https://studio.youtube.com/channel/UC-LSSlOZwpGIRIYihaz8zCw/comments/inbox"
    print(f"\n[2] Navigating to Studio inbox...")
    driver.get(target_url)
    await asyncio.sleep(5)
    print("[OK] On YouTube Studio page")

    # Initialize teaching system
    teaching_system = TeachingSystem()

    # Phase 1: TEACH MODE - 012 demonstrates LIKE action
    print("\n" + "="*80)
    print(" PHASE 1: TEACH MODE")
    print("="*80)
    print("\n[3] Starting teaching session for LIKE action...")
    print("    012: Please click the LIKE button on the first comment")
    print("    Recording will last 15 seconds...")

    # Define element selector for Like button on first comment
    like_button_selector = "ytcp-comment-thread:nth-child(1) button[aria-label*='Like']"

    recording = await teaching_system.start_teaching_session(
        driver,
        action_name="like_comment",
        element_selector=like_button_selector,
        duration_seconds=15
    )

    if recording:
        print("\n[OK] Teaching session complete!")
        print(f"    State change captured:")
        for key, change in recording.state_change_signature.items():
            print(f"      {key}: {change['before']} → {change['after']}")
    else:
        print("\n[FAIL] Teaching session failed")
        return

    # Phase 2: REPLAY MODE - 0102 replicates learned action
    print("\n" + "="*80)
    print(" PHASE 2: REPLAY MODE")
    print("="*80)
    print("\n[4] 0102 will now replicate the LIKE action...")

    # Navigate to next comment (to test on fresh element)
    print("    Testing on a different comment...")
    next_like_button_selector = "ytcp-comment-thread:nth-child(2) button[aria-label*='Like']"

    result = await teaching_system.replicate_action(
        driver,
        action_name="like_comment",
        element_selector=next_like_button_selector,
        max_retries=3
    )

    print(f"\n{'='*80}")
    print(" REPLAY RESULTS")
    print("="*80)

    if result["success"]:
        print(f"\n[SUCCESS] Action replicated successfully!")
        print(f"  Confidence: {result['confidence']:.2f}")
        print(f"  Attempts: {result['attempts']}")
        print(f"  State change:")
        for key, change in result["state_change"].items():
            print(f"    {key}: {change['before']} → {change['after']}")
    else:
        print(f"\n[FAILED] Could not replicate action")
        print(f"  Error: {result.get('error', 'Unknown')}")
        print(f"  Attempts: {result['attempts']}")

    # Phase 3: Continuous autonomous engagement
    print("\n" + "="*80)
    print(" PHASE 3: AUTONOMOUS ENGAGEMENT")
    print("="*80)
    print("\n[5] 0102 will now autonomously LIKE all remaining comments...")

    # Get all comments
    comment_count = driver.execute_script("""
        const cards = document.querySelectorAll('ytcp-comment-thread');
        return cards.length;
    """)

    print(f"    Found {comment_count} comments")

    engaged_count = 0
    for i in range(2, comment_count):  # Start from 3rd (already did 1st and 2nd)
        print(f"\n  [Comment {i+1}/{comment_count}]")
        selector = f"ytcp-comment-thread:nth-child({i+1}) button[aria-label*='Like']"

        result = await teaching_system.replicate_action(
            driver,
            action_name="like_comment",
            element_selector=selector,
            max_retries=3
        )

        if result["success"]:
            print(f"    [OK] LIKED (confidence: {result['confidence']:.2f})")
            engaged_count += 1
        else:
            print(f"    [FAIL] Could not like")

        await asyncio.sleep(1)

    print("\n" + "="*80)
    print(" AUTONOMOUS ENGAGEMENT COMPLETE")
    print("="*80)
    print(f"\nSuccessfully engaged with {engaged_count}/{comment_count-2} comments")
    print("\n0102 has learned from 012's demonstration and autonomously replicated it!")


if __name__ == "__main__":
    asyncio.run(test_teaching_workflow())
