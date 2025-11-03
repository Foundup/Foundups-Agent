#!/usr/bin/env python3
"""
PeerTube Relay PoC - Minimal YouTube → PeerTube Live Stream Relay
WSP 1: Single-purpose script for proof-of-concept testing

USAGE:
    1. Set environment variables:
       - PEERTUBE_API_TOKEN
       - PEERTUBE_CHANNEL_ID

    2. Edit YOUTUBE_VIDEO_ID and PEERTUBE_INSTANCE below

    3. Run: python scripts/peertube_relay_poc.py

    4. CTRL+C to stop

REQUIREMENTS:
    - yt-dlp (pip install yt-dlp)
    - requests (pip install requests)
    - ffmpeg (system PATH)
"""

import os
import sys
import time
import subprocess
import signal
import logging
from typing import Optional, Dict, Any

try:
    import requests
except ImportError:
    print("[ERROR] requests not installed. Run: pip install requests")
    sys.exit(1)

# ============================================================================
# CONFIGURATION (Edit these for your test)
# ============================================================================

YOUTUBE_VIDEO_ID = "YOUR_VIDEO_ID_HERE"  # Replace with actual video ID
PEERTUBE_INSTANCE = "https://peertube.example.com"  # Replace with your instance
PEERTUBE_API_TOKEN = os.getenv("PEERTUBE_API_TOKEN")
PEERTUBE_CHANNEL_ID = os.getenv("PEERTUBE_CHANNEL_ID")

POLL_INTERVAL_SECONDS = 30  # How often to check if stream is live
MAX_RETRIES = 5  # Max retries for failed operations

# ============================================================================
# LOGGING SETUP
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# ============================================================================
# GLOBAL STATE
# ============================================================================

ffmpeg_process: Optional[subprocess.Popen] = None
peertube_live_id: Optional[str] = None

# ============================================================================
# YOUTUBE LIVE STATUS CHECK
# ============================================================================

def check_youtube_live(video_id: str) -> bool:
    """
    Check if YouTube video is currently live using yt-dlp

    Returns:
        True if live, False otherwise
    """
    try:
        logger.info(f"Checking live status for YouTube video: {video_id}")

        # Use yt-dlp to get video info
        result = subprocess.run(
            ["yt-dlp", "--dump-json", f"https://www.youtube.com/watch?v={video_id}"],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            logger.warning(f"yt-dlp failed: {result.stderr}")
            return False

        # Parse JSON output
        import json
        video_info = json.loads(result.stdout)

        # Check if live
        is_live = video_info.get('is_live', False)

        if is_live:
            logger.info(f"[LIVE] YouTube video {video_id} is LIVE")
        else:
            logger.info(f"[NOT LIVE] YouTube video {video_id} is not live")

        return is_live

    except subprocess.TimeoutExpired:
        logger.error("yt-dlp timeout - video might not exist")
        return False
    except Exception as e:
        logger.error(f"Error checking YouTube live status: {e}")
        return False

# ============================================================================
# EXTRACT HLS URL
# ============================================================================

def get_hls_url(video_id: str) -> Optional[str]:
    """
    Extract HLS stream URL from YouTube video using yt-dlp

    Returns:
        HLS URL string or None if not available
    """
    try:
        logger.info(f"Extracting HLS URL for video: {video_id}")

        # Use yt-dlp to get best format URL
        result = subprocess.run(
            [
                "yt-dlp",
                "-f", "best",
                "-g",  # Get direct URL
                f"https://www.youtube.com/watch?v={video_id}"
            ],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            logger.error(f"Failed to extract HLS URL: {result.stderr}")
            return None

        hls_url = result.stdout.strip()
        logger.info(f"[OK] Extracted HLS URL: {hls_url[:80]}...")
        return hls_url

    except Exception as e:
        logger.error(f"Error extracting HLS URL: {e}")
        return None

# ============================================================================
# PEERTUBE API
# ============================================================================

def create_peertube_live(title: str = "YouTube Relay Stream") -> Optional[Dict[str, Any]]:
    """
    Create a PeerTube live stream and get RTMP ingest URL

    Returns:
        Dict with 'rtmpUrl' and 'streamKey', or None on failure
    """
    global peertube_live_id

    if not PEERTUBE_API_TOKEN or not PEERTUBE_CHANNEL_ID:
        logger.error("PEERTUBE_API_TOKEN or PEERTUBE_CHANNEL_ID not set")
        return None

    try:
        logger.info("Creating PeerTube live stream...")

        url = f"{PEERTUBE_INSTANCE}/api/v1/videos/live"
        headers = {
            "Authorization": f"Bearer {PEERTUBE_API_TOKEN}",
            "Content-Type": "application/json"
        }

        data = {
            "channelId": int(PEERTUBE_CHANNEL_ID),
            "name": title,
            "privacy": 1,  # Public
            "saveReplay": False,
            "permanentLive": True
        }

        response = requests.post(url, headers=headers, json=data, timeout=30)

        if response.status_code != 200:
            logger.error(f"PeerTube API error: {response.status_code} - {response.text}")
            return None

        result = response.json()

        # Extract RTMP details
        live_video = result.get('video', {})
        peertube_live_id = str(live_video.get('id'))

        rtmp_url = f"{PEERTUBE_INSTANCE}/live"
        stream_key = live_video.get('streamKey')

        if not stream_key:
            logger.error("No stream key returned from PeerTube API")
            return None

        logger.info(f"[OK] PeerTube live created - ID: {peertube_live_id}")
        logger.info(f"[OK] RTMP URL: {rtmp_url}")
        logger.info(f"[OK] Stream Key: {stream_key[:8]}...")

        return {
            'rtmpUrl': rtmp_url,
            'streamKey': stream_key,
            'liveId': peertube_live_id
        }

    except Exception as e:
        logger.error(f"Error creating PeerTube live stream: {e}")
        return None

# ============================================================================
# FFMPEG RELAY
# ============================================================================

def start_ffmpeg_relay(hls_url: str, rtmp_url: str, stream_key: str) -> bool:
    """
    Start FFmpeg process to relay HLS → RTMP

    Returns:
        True if started successfully
    """
    global ffmpeg_process

    try:
        logger.info("Starting FFmpeg relay...")

        full_rtmp = f"{rtmp_url}/{stream_key}"

        # FFmpeg command: copy video/audio without re-encoding
        cmd = [
            "ffmpeg",
            "-i", hls_url,
            "-c", "copy",  # Copy codecs (no re-encoding)
            "-f", "flv",
            full_rtmp
        ]

        logger.info(f"FFmpeg command: {' '.join(cmd[:6])}... [RTMP URL hidden]")

        # Start FFmpeg subprocess
        ffmpeg_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        logger.info(f"[OK] FFmpeg relay started (PID: {ffmpeg_process.pid})")
        return True

    except Exception as e:
        logger.error(f"Error starting FFmpeg relay: {e}")
        return False

def monitor_ffmpeg():
    """
    Monitor FFmpeg process output
    """
    global ffmpeg_process

    if not ffmpeg_process:
        return

    try:
        # Check if process is still running
        poll_result = ffmpeg_process.poll()

        if poll_result is not None:
            # Process has exited
            logger.error(f"[FAIL] FFmpeg exited with code {poll_result}")

            # Read any remaining error output
            stderr = ffmpeg_process.stderr.read() if ffmpeg_process.stderr else ""
            if stderr:
                logger.error(f"FFmpeg stderr: {stderr[:500]}")

            ffmpeg_process = None
            return False

        # Process is still running
        return True

    except Exception as e:
        logger.error(f"Error monitoring FFmpeg: {e}")
        return False

# ============================================================================
# CLEANUP
# ============================================================================

def cleanup():
    """
    Stop FFmpeg and cleanup resources
    """
    global ffmpeg_process

    logger.info("Cleaning up...")

    if ffmpeg_process:
        try:
            logger.info("Terminating FFmpeg process...")
            ffmpeg_process.terminate()

            # Wait up to 5 seconds for graceful shutdown
            try:
                ffmpeg_process.wait(timeout=5)
                logger.info("[OK] FFmpeg terminated gracefully")
            except subprocess.TimeoutExpired:
                logger.warning("FFmpeg didn't terminate, killing...")
                ffmpeg_process.kill()
                ffmpeg_process.wait()
                logger.info("[OK] FFmpeg killed")

        except Exception as e:
            logger.error(f"Error stopping FFmpeg: {e}")

        ffmpeg_process = None

    logger.info("Cleanup complete")

def signal_handler(sig, frame):
    """
    Handle CTRL+C
    """
    logger.info("\n[INTERRUPT] CTRL+C detected")
    cleanup()
    sys.exit(0)

# ============================================================================
# MAIN LOOP
# ============================================================================

def main():
    """
    Main PoC loop
    """
    global ffmpeg_process

    # Validate config
    if YOUTUBE_VIDEO_ID == "YOUR_VIDEO_ID_HERE":
        logger.error("Please set YOUTUBE_VIDEO_ID in the script")
        sys.exit(1)

    if PEERTUBE_INSTANCE == "https://peertube.example.com":
        logger.error("Please set PEERTUBE_INSTANCE in the script")
        sys.exit(1)

    if not PEERTUBE_API_TOKEN:
        logger.error("Please set PEERTUBE_API_TOKEN environment variable")
        sys.exit(1)

    if not PEERTUBE_CHANNEL_ID:
        logger.error("Please set PEERTUBE_CHANNEL_ID environment variable")
        sys.exit(1)

    # Register CTRL+C handler
    signal.signal(signal.SIGINT, signal_handler)

    logger.info("=" * 60)
    logger.info("PeerTube Relay PoC - YouTube → PeerTube Live Stream")
    logger.info("=" * 60)
    logger.info(f"YouTube Video ID: {YOUTUBE_VIDEO_ID}")
    logger.info(f"PeerTube Instance: {PEERTUBE_INSTANCE}")
    logger.info(f"Poll Interval: {POLL_INTERVAL_SECONDS}s")
    logger.info("=" * 60)
    logger.info("Press CTRL+C to stop")
    logger.info("=" * 60)

    relay_active = False

    try:
        while True:
            # Check if YouTube stream is live
            is_live = check_youtube_live(YOUTUBE_VIDEO_ID)

            if is_live and not relay_active:
                # Stream just went live - start relay
                logger.info("[TRIGGER] Stream went LIVE - starting relay")

                # Extract HLS URL
                hls_url = get_hls_url(YOUTUBE_VIDEO_ID)
                if not hls_url:
                    logger.error("Failed to extract HLS URL - waiting for next poll")
                    time.sleep(POLL_INTERVAL_SECONDS)
                    continue

                # Create PeerTube live stream
                peertube_info = create_peertube_live(f"Relay: {YOUTUBE_VIDEO_ID}")
                if not peertube_info:
                    logger.error("Failed to create PeerTube live stream - waiting for next poll")
                    time.sleep(POLL_INTERVAL_SECONDS)
                    continue

                # Start FFmpeg relay
                success = start_ffmpeg_relay(
                    hls_url,
                    peertube_info['rtmpUrl'],
                    peertube_info['streamKey']
                )

                if success:
                    relay_active = True
                    logger.info("[OK] Relay is ACTIVE")
                else:
                    logger.error("Failed to start FFmpeg relay")

            elif not is_live and relay_active:
                # Stream went offline - stop relay
                logger.info("[OFFLINE] Stream ended - stopping relay")
                cleanup()
                relay_active = False

            elif relay_active:
                # Monitor FFmpeg process
                if not monitor_ffmpeg():
                    logger.error("FFmpeg process died - stopping relay")
                    relay_active = False

            # Wait before next poll
            time.sleep(POLL_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        logger.info("\n[STOP] Interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        cleanup()

if __name__ == "__main__":
    main()
