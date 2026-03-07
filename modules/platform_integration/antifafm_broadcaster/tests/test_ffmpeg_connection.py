#!/usr/bin/env python3
"""
Minimal FFmpeg connection test - NO browser automation.

This tests ONLY the FFmpeg -> YouTube RTMP connection.
Run: python modules/platform_integration/antifafm_broadcaster/tests/test_ffmpeg_connection.py

Switches (environment variables):
- ANTIFAFM_TEST_DURATION: How long to stream (default: 30 seconds)
- ANTIFAFM_TEST_VISUAL: Use video file instead of test pattern (default: test pattern)
- ANTIFAFM_TEST_AUDIO: Use audio file instead of sine wave (default: sine wave)
- ANTIFAFM_DRY_RUN: Just print the FFmpeg command, don't run it (default: 0)
"""

import os
import sys
import subprocess
import time

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, PROJECT_ROOT)

# Load .env
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
except ImportError:
    pass

# Configuration
STREAM_KEY = os.getenv("ANTIFAFM_YOUTUBE_STREAM_KEY", "")
RTMP_URL = os.getenv("ANTIFAFM_RTMP_URL", "rtmps://a.rtmps.youtube.com:443/live2")
TEST_DURATION = int(os.getenv("ANTIFAFM_TEST_DURATION", "30"))
DRY_RUN = os.getenv("ANTIFAFM_DRY_RUN", "0") == "1"

# Test pattern sources (no external files needed)
USE_TEST_PATTERN = os.getenv("ANTIFAFM_TEST_VISUAL", "") == ""
USE_TEST_AUDIO = os.getenv("ANTIFAFM_TEST_AUDIO", "") == ""


def check_ffmpeg():
    """Verify FFmpeg is installed."""
    print("[STEP 1] Checking FFmpeg installation...")
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"  [OK] {version_line}")
            return True
        else:
            print(f"  [FAIL] FFmpeg returned error: {result.stderr}")
            return False
    except FileNotFoundError:
        print("  [FAIL] FFmpeg not found. Install it first.")
        return False
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False


def check_stream_key():
    """Verify stream key is configured."""
    print("\n[STEP 2] Checking stream key...")
    if not STREAM_KEY:
        print("  [FAIL] ANTIFAFM_YOUTUBE_STREAM_KEY not set in .env")
        print("  [INFO] Get your stream key from YouTube Studio > Go Live > Stream Settings")
        return False

    # Mask the key for display
    masked = STREAM_KEY[:4] + "****" + STREAM_KEY[-4:] if len(STREAM_KEY) > 8 else "****"
    print(f"  [OK] Stream key configured: {masked}")
    return True


def check_rtmp_url():
    """Display RTMP URL being used."""
    print("\n[STEP 3] RTMP URL configuration...")
    print(f"  [INFO] URL: {RTMP_URL}")

    if "rtmps://" in RTMP_URL:
        print("  [OK] Using RTMPS (port 443) - firewall friendly")
    elif "rtmp://" in RTMP_URL:
        print("  [WARN] Using RTMP (port 1935) - may be blocked by firewall")

    return True


def build_ffmpeg_command():
    """Build the minimal FFmpeg command for testing."""
    print("\n[STEP 4] Building FFmpeg command...")

    full_rtmp = f"{RTMP_URL}/{STREAM_KEY}"

    cmd = ["ffmpeg"]

    # Input sources
    if USE_TEST_PATTERN:
        # Generate test pattern (color bars + timestamp)
        print("  [INFO] Using FFmpeg test pattern (no external video)")
        cmd.extend([
            "-f", "lavfi",
            "-i", f"testsrc=duration={TEST_DURATION}:size=1920x1080:rate=30",
        ])
    else:
        visual = os.getenv("ANTIFAFM_TEST_VISUAL")
        print(f"  [INFO] Using video file: {visual}")
        cmd.extend(["-re", "-i", visual])

    if USE_TEST_AUDIO:
        # Generate sine wave audio
        print("  [INFO] Using FFmpeg sine wave audio (no external audio)")
        cmd.extend([
            "-f", "lavfi",
            "-i", f"sine=frequency=440:duration={TEST_DURATION}",
        ])
    else:
        audio = os.getenv("ANTIFAFM_TEST_AUDIO")
        print(f"  [INFO] Using audio file: {audio}")
        cmd.extend(["-i", audio])

    # Video encoding
    cmd.extend([
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-b:v", "2500k",
        "-maxrate", "2500k",
        "-bufsize", "5000k",
        "-pix_fmt", "yuv420p",
        "-g", "60",  # Keyframe every 2 seconds at 30fps
    ])

    # Audio encoding
    cmd.extend([
        "-c:a", "aac",
        "-b:a", "128k",
        "-ar", "44100",
    ])

    # Output
    cmd.extend([
        "-f", "flv",
        full_rtmp,
    ])

    return cmd


def run_ffmpeg_test(cmd):
    """Run FFmpeg and monitor output."""
    print("\n[STEP 5] Starting FFmpeg stream...")
    print(f"  [INFO] Duration: {TEST_DURATION} seconds")
    print(f"  [INFO] Command: {' '.join(cmd[:10])}... (truncated)")

    if DRY_RUN:
        print("\n  [DRY RUN] Full command:")
        # Mask stream key in output
        safe_cmd = ' '.join(cmd).replace(STREAM_KEY, "****STREAM_KEY****")
        print(f"  {safe_cmd}")
        return True

    print("\n  [INFO] FFmpeg output:")
    print("  " + "-" * 50)

    try:
        # Run FFmpeg with real-time output
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        start_time = time.time()
        connected = False
        frames_sent = 0

        for line in process.stdout:
            elapsed = time.time() - start_time
            line = line.strip()

            # Print important lines
            if any(x in line.lower() for x in ['error', 'fail', 'refused', 'broken', 'frame=']):
                print(f"  [{elapsed:.1f}s] {line[:80]}")

            # Check for successful connection
            if 'frame=' in line and not connected:
                connected = True
                print(f"\n  [OK] FFmpeg CONNECTED to YouTube! (after {elapsed:.1f}s)")

            # Parse frame count
            if 'frame=' in line:
                try:
                    frames_sent = int(line.split('frame=')[1].split()[0])
                except:
                    pass

            # Check for errors
            if 'error' in line.lower() or 'refused' in line.lower():
                print(f"\n  [ERROR] {line}")

        process.wait()

        print("  " + "-" * 50)

        total_time = time.time() - start_time
        print(f"\n[RESULT] FFmpeg ran for {total_time:.1f}s, sent {frames_sent} frames")

        if process.returncode == 0:
            print("[SUCCESS] FFmpeg completed normally")
            return True
        elif connected and frames_sent > 10:
            print(f"[PARTIAL SUCCESS] Connection worked, sent {frames_sent} frames")
            print("  Stream may have been rejected by YouTube after connecting.")
            print("  Check YouTube Studio to see if stream appeared.")
            return True
        else:
            print(f"[FAIL] FFmpeg exited with code {process.returncode}")
            print("  Check the error messages above.")
            return False

    except KeyboardInterrupt:
        print("\n  [INTERRUPTED] User cancelled")
        process.terminate()
        return True
    except Exception as e:
        print(f"\n  [ERROR] {e}")
        return False


def main():
    print("=" * 60)
    print("antifaFM FFmpeg Connection Test")
    print("=" * 60)
    print("This tests ONLY the FFmpeg -> YouTube RTMP connection.")
    print("No browser automation involved.")
    print("=" * 60)

    # Step 1: Check FFmpeg
    if not check_ffmpeg():
        return False

    # Step 2: Check stream key
    if not check_stream_key():
        return False

    # Step 3: Check RTMP URL
    check_rtmp_url()

    # Step 4: Build command
    cmd = build_ffmpeg_command()

    # Step 5: Run test
    success = run_ffmpeg_test(cmd)

    print("\n" + "=" * 60)
    if success:
        print("TEST PASSED - FFmpeg can connect to YouTube")
        print("\nIf this works but production doesn't:")
        print("  1. Browser automation (Go Live) is the problem")
        print("  2. YouTube may require Go Live to be clicked first")
        print("  3. Try manually clicking Go Live in YouTube Studio, then run production")
    else:
        print("TEST FAILED - FFmpeg cannot connect to YouTube")
        print("\nTroubleshooting:")
        print("  1. Is your stream key correct?")
        print("  2. Is port 443 open? (try: Test-NetConnection a.rtmps.youtube.com -Port 443)")
        print("  3. Is YouTube Studio ready? (manually click Go Live first)")
    print("=" * 60)

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
