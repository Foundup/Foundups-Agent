"""
Generate First YouTube Short with Talking Baby

Creates actual AI-generated video using Veo 3 and uploads to YouTube.
This is the REAL thing - talking baby narrating Japan content!

Cost: $12 (30-second video)
"""

import sys
from pathlib import Path

# Add module to path
module_root = Path(__file__).parent.parent
sys.path.insert(0, str(module_root.parent.parent.parent))

from modules.communication.youtube_shorts.src.shorts_orchestrator import ShortsOrchestrator

print("\n" + "="*80)
print("[U+1F3AC] GENERATE FIRST YOUTUBE SHORT WITH TALKING BABY")
print("="*80)

# Initialize orchestrator
print("\n[1/4] Initializing Shorts Orchestrator...")
orchestrator = ShortsOrchestrator()

# Topic for first video
topic = "Cherry blossoms falling at Meguro River in Tokyo during spring sunset"

print(f"\n[2/4] Topic: {topic}")
print("\n[U+26A0]️  COST WARNING:")
print("   - 30-second video = $12 (Veo 3)")
print("   - Includes talking baby narrator automatically")
print("   - Will be uploaded as UNLISTED for testing")
print()

print("[3/4] Generating AI video with Veo 3...")
print("   This will take 1-2 minutes...")
print()

try:
    # Generate and upload
    shorts_url = orchestrator.create_and_upload(
        topic=topic,
        duration=30,  # 30 seconds = $12
        enhance_prompt=True,  # Add Move2Japan style + talking baby
        fast_mode=True,  # Use Veo 3 Fast (cheaper)
        privacy="unlisted"  # Safe for testing
    )

    print("\n" + "="*80)
    print("[OK] SUCCESS!")
    print("="*80)
    print(f"\n[U+1F3AC] Your first AI-generated talking baby Short is live!")
    print(f"\n[LINK] Watch here: {shorts_url}")
    print(f"\n[DATA] Details:")
    print(f"   Channel: UnDaoDu")
    print(f"   Duration: 30 seconds")
    print(f"   Privacy: Unlisted")
    print(f"   Cost: $12")
    print(f"   Features: Talking baby narrator (Move2Japan signature)")
    print()
    print(f"[CELEBRATE] Next: Change privacy to 'public' to share with the world!")
    print()

except Exception as e:
    print(f"\n[FAIL] GENERATION FAILED: {e}")
    print("\nPossible issues:")
    print("   - Insufficient Veo 3 API credits")
    print("   - API rate limit exceeded")
    print("   - Network connectivity")
    sys.exit(1)
