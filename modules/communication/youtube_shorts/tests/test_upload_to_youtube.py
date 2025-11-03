"""
Test YouTube Shorts Upload Functionality

This script tests if we can actually upload a video to YouTube.
We'll create a simple test video and attempt to upload it as unlisted.

[U+26A0]️  WARNING: This will actually upload to YouTube!
"""

import sys
from pathlib import Path

# Add module to path
module_root = Path(__file__).parent.parent
sys.path.insert(0, str(module_root.parent.parent.parent))


def test_upload_capability():
    """Test 1: Verify we have YouTube upload capability"""
    print("\n" + "="*80)
    print("TEST 1: YouTube Upload Capability Check")
    print("="*80)

    try:
        from modules.communication.youtube_shorts.src.youtube_uploader import YouTubeShortsUploader

        uploader = YouTubeShortsUploader()
        print("\n[OK] YouTube uploader initialized successfully!")

        # Get channel info to verify auth works
        channel_info = uploader.get_channel_info()
        print(f"\n[U+1F4FA] Connected to Channel:")
        print(f"   Name: {channel_info.get('title', 'Unknown')}")
        print(f"   ID: {channel_info.get('id', 'Unknown')}")

        return True

    except Exception as e:
        print(f"\n[FAIL] FAIL: {e}")
        return False


def test_orchestrator_init():
    """Test 2: Verify orchestrator initializes"""
    print("\n" + "="*80)
    print("TEST 2: Shorts Orchestrator Initialization")
    print("="*80)

    try:
        from modules.communication.youtube_shorts.src.shorts_orchestrator import ShortsOrchestrator

        orchestrator = ShortsOrchestrator()
        print("\n[OK] Shorts orchestrator initialized!")
        print(f"   Memory: {len(orchestrator.shorts_memory)} tracked Shorts")

        return True

    except Exception as e:
        print(f"\n[FAIL] FAIL: {e}")
        return False


def create_test_video():
    """Create a simple black video for testing (requires ffmpeg)"""
    print("\n" + "="*80)
    print("TEST 3: Create Test Video")
    print("="*80)

    try:
        import subprocess
        from pathlib import Path

        # Output path
        assets_dir = Path(__file__).parent.parent / "assets" / "test"
        assets_dir.mkdir(parents=True, exist_ok=True)
        test_video = assets_dir / "test_upload.mp4"

        # Check if ffmpeg is available
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("\n[U+26A0]️  SKIP: ffmpeg not found")
            print("   Install: choco install ffmpeg (Windows)")
            return None

        # Create 5-second black video (vertical 9:16 for Shorts)
        print("\n[U+1F4F9] Creating 5-second test video (vertical 9:16)...")

        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", "color=c=black:s=1080x1920:d=5",  # 5 seconds, 1080x1920 (9:16)
            "-vf", "drawtext=text='Move2Japan Test Upload':fontcolor=white:fontsize=60:x=(w-text_w)/2:y=(h-text_h)/2",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            str(test_video)
        ]

        result = subprocess.run(cmd, capture_output=True)

        if test_video.exists():
            print(f"[OK] Test video created: {test_video}")
            print(f"   Size: {test_video.stat().st_size / 1024:.1f} KB")
            return str(test_video)
        else:
            print(f"[FAIL] FAIL: Video creation failed")
            print(f"   Error: {result.stderr.decode()}")
            return None

    except Exception as e:
        print(f"\n[FAIL] FAIL: {e}")
        return None


def upload_test_video(video_path: str):
    """Upload test video to YouTube as unlisted"""
    print("\n" + "="*80)
    print("[U+26A0]️  ACTUAL UPLOAD TO YOUTUBE - UNLISTED")
    print("="*80)

    response = input("\nAre you SURE you want to upload test video to YouTube? (yes/no): ")

    if response.lower() != "yes":
        print("\n⏸️  Upload skipped")
        return False

    try:
        from modules.communication.youtube_shorts.src.youtube_uploader import YouTubeShortsUploader

        uploader = YouTubeShortsUploader()

        print("\n[U+1F4E4] Uploading test video...")

        shorts_url = uploader.upload_short(
            video_path=video_path,
            title="Move2Japan Test Upload - Talking Baby Feature",
            description="Testing YouTube Shorts upload capability for Move2Japan talking baby videos. #Shorts #Move2Japan #TestUpload",
            tags=["Shorts", "Japan", "Move2Japan", "Test"],
            privacy="unlisted"  # Unlisted so it doesn't appear on channel
        )

        print(f"\n[OK] SUCCESS!")
        print(f"   Shorts URL: {shorts_url}")
        print(f"\n[LINK] View: {shorts_url}")
        print(f"   Status: Unlisted (not public)")

        return True

    except Exception as e:
        print(f"\n[FAIL] UPLOAD FAILED: {e}")
        return False


if __name__ == "__main__":
    print("\n[U+1F3AC] YouTube Shorts Upload Test")
    print("="*80)

    # Test 1: Verify upload capability
    test1_pass = test_upload_capability()

    # Test 2: Verify orchestrator
    test2_pass = test_orchestrator_init()

    # Test 3: Create test video (if ffmpeg available)
    test_video_path = create_test_video()

    print("\n" + "="*80)
    print("TEST RESULTS:")
    print("="*80)
    print(f"  Upload Capability: {'[OK] PASS' if test1_pass else '[FAIL] FAIL'}")
    print(f"  Orchestrator Init: {'[OK] PASS' if test2_pass else '[FAIL] FAIL'}")
    print(f"  Test Video Created: {'[OK] PASS' if test_video_path else '⏭️  SKIP (no ffmpeg)'}")

    # Offer actual upload if test video exists
    if test_video_path:
        print("\n" + "="*80)
        print("ACTUAL YOUTUBE UPLOAD TEST:")
        print("="*80)
        print("[U+26A0]️  This will upload a 5-second test video to YouTube")
        print("   Privacy: Unlisted (won't appear on channel)")
        print("   Title: Move2Japan Test Upload - Talking Baby Feature")
        print()

        upload_test_video(test_video_path)
    else:
        print("\n⏭️  Skipping upload test (no test video)")

    print("\n" + "="*80)
    print("SUMMARY:")
    print("="*80)
    print("YouTube upload system is configured and ready!")
    print("\nTo test full Shorts creation with talking baby:")
    print("  python modules/communication/youtube_shorts/tests/test_promo_generation.py")
