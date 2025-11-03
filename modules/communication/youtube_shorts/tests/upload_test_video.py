"""
Simple script to upload test video to YouTube Shorts

Run this to verify upload capability works.
Uploads 5-second test video as UNLISTED.
"""

import sys
from pathlib import Path

# Add module to path
module_root = Path(__file__).parent.parent
sys.path.insert(0, str(module_root.parent.parent.parent))

from modules.communication.youtube_shorts.src.youtube_uploader import YouTubeShortsUploader

# Path to test video
test_video = Path(__file__).parent.parent / "assets" / "test" / "test_upload.mp4"

if not test_video.exists():
    print(f"[FAIL] Test video not found: {test_video}")
    print("   Run: python modules/communication/youtube_shorts/tests/test_upload_to_youtube.py")
    print("   to create the test video first.")
    sys.exit(1)

print("\n[U+1F3AC] Uploading test video to YouTube Shorts...")
print(f"   Video: {test_video}")
print(f"   Privacy: UNLISTED")
print()

uploader = YouTubeShortsUploader()

shorts_url = uploader.upload_short(
    video_path=str(test_video),
    title="Move2Japan Test - Talking Baby Feature",
    description="Testing YouTube Shorts upload capability for Move2Japan talking baby videos. #Shorts #Move2Japan #TestUpload",
    tags=["Shorts", "Japan", "Move2Japan", "Test"],
    privacy="unlisted"
)

print(f"\n[OK] SUCCESS!")
print(f"   Shorts URL: {shorts_url}")
print(f"\n[LINK] View your upload: {shorts_url}")
print(f"   Status: Unlisted (not public)")
