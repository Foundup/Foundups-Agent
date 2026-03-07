"""
Video Downloader Helper for antifaFM

Downloads YouTube videos to the backgrounds folder for use in broadcast.

Usage:
    python download_video.py <youtube_url>

Options:
    --browser chrome/edge/firefox  (use browser cookies for auth)
    --no-cookies                   (try without auth - may fail with 403)

Example:
    python download_video.py https://www.youtube.com/watch?v=suV48UQWcs0 --browser chrome

Note: Close your browser before running with --browser option!
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    url = sys.argv[1]
    browser = None
    no_cookies = False

    # Parse args
    for i, arg in enumerate(sys.argv[2:], 2):
        if arg == "--browser" and i + 1 < len(sys.argv):
            browser = sys.argv[i + 1]
        elif arg in ["chrome", "edge", "firefox"]:
            browser = arg
        elif arg == "--no-cookies":
            no_cookies = True

    # Output folder
    output_dir = Path(__file__).parent.parent / "assets" / "backgrounds"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Build filename from video ID
    import re
    match = re.search(r'(?:v=|youtu\.be/|shorts/)([a-zA-Z0-9_-]{11})', url)
    video_id = match.group(1) if match else "video"
    output_file = output_dir / f"{video_id}.mp4"

    print(f"[DOWNLOAD] URL: {url}")
    print(f"[DOWNLOAD] Output: {output_file}")

    # Build yt-dlp command
    cmd = [
        "yt-dlp",
        "-f", "bestvideo[height<=1080][ext=mp4]+bestaudio/best[height<=1080]",
        "--merge-output-format", "mp4",
        "-o", str(output_file),
        "--no-playlist",
    ]

    if browser and not no_cookies:
        cmd.extend(["--cookies-from-browser", browser])
        print(f"[DOWNLOAD] Using cookies from: {browser}")
        print("[DOWNLOAD] Note: Close browser before running this script!")

    cmd.append(url)

    print(f"[DOWNLOAD] Running: {' '.join(cmd[:8])}...")
    print()

    result = subprocess.run(cmd)

    if result.returncode == 0 and output_file.exists():
        size_mb = output_file.stat().st_size / 1024 / 1024
        print()
        print(f"[OK] Downloaded: {output_file.name} ({size_mb:.1f} MB)")
        print()
        print("Next steps:")
        print("1. Run: python -c \"from modules.platform_integration.antifafm_broadcaster.src.video_library import VideoLibrary; lib=VideoLibrary(); print(lib.scan_for_unregistered_videos('012'))\"")
        print("2. Or restart broadcaster to pick up new video")
        return 0
    else:
        print()
        print("[FAIL] Download failed")
        print()
        print("Try these alternatives:")
        print("1. Close ALL browser windows, then run again with --browser chrome")
        print("2. Manually download from browser and save to:", output_dir)
        print("3. Use a video downloader browser extension")
        return 1


if __name__ == "__main__":
    sys.exit(main())
