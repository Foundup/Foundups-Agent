#!/usr/bin/env python3
"""
PeerTube Relay Handler - YouTube DAE Integration
Hooks into AutoModeratorDAE's stream detection to relay to PeerTube

WSP Compliance:
- WSP 27: DAE architecture integration
- WSP 64: Secure credential management (ENV vars only)
- WSP 91: DAEMON observability (logs to YouTube DAE logger)

NAVIGATION: Called by AutoModeratorDAE._trigger_social_media_posting_for_streams
-> Receives: found_streams (list of stream metadata dicts)
-> Returns: None (logs all actions to YouTube DAE logger)
"""

import os
import subprocess
import logging
from typing import Optional, Dict, List
import time

try:
    import requests
except ImportError:
    requests = None

# Use YouTube DAE's logger (not separate logger!)
logger = logging.getLogger("modules.communication.livechat.src.auto_moderator_dae")


class PeerTubeRelayHandler:
    """
    Handles YouTube → PeerTube stream relay when streams are detected.

    Integrates with AutoModeratorDAE lifecycle:
    - Called when stream_start event fires
    - Uses YouTube DAE logger for observability
    - Manages FFmpeg subprocess lifecycle
    - Cleanup on YouTube stream end
    """

    def __init__(self):
        """Initialize PeerTube relay handler with ENV configuration"""
        self.enabled = os.getenv("PEERTUBE_RELAY_ENABLED", "false").lower() == "true"
        self.instance_url = os.getenv("PEERTUBE_INSTANCE_URL", "")
        self.api_token = os.getenv("PEERTUBE_API_TOKEN", "")
        self.channel_id = os.getenv("PEERTUBE_CHANNEL_ID", "")

        # Track active relays (video_id → FFmpeg process)
        self.active_relays: Dict[str, subprocess.Popen] = {}

        # Validate configuration
        if self.enabled:
            if not self.instance_url or not self.api_token or not self.channel_id:
                logger.warning("[PEERTUBE] [RELAY] Relay enabled but missing config - disabling")
                logger.warning("[PEERTUBE] Required: PEERTUBE_INSTANCE_URL, PEERTUBE_API_TOKEN, PEERTUBE_CHANNEL_ID")
                self.enabled = False
            else:
                logger.info(f"[PEERTUBE] [RELAY] Initialized - instance={self.instance_url}")
        else:
            logger.debug("[PEERTUBE] [RELAY] Disabled (set PEERTUBE_RELAY_ENABLED=true to enable)")

    def handle_streams_detected(self, found_streams: List[Dict]) -> None:
        """
        Handle stream detection event from AutoModeratorDAE.

        Args:
            found_streams: List of stream metadata dicts with keys:
                - video_id: YouTube video ID
                - channel_name: Channel name (for logging)
                - live_chat_id: Live chat ID (unused for relay)
        """
        if not self.enabled:
            return

        if not found_streams:
            logger.debug("[PEERTUBE] [RELAY] No streams to relay")
            return

        logger.info(f"[PEERTUBE] [RELAY] Processing {len(found_streams)} stream(s) for relay")

        for stream in found_streams:
            video_id = stream.get('video_id')
            channel_name = stream.get('channel_name', 'Unknown')

            if not video_id:
                logger.warning("[PEERTUBE] [RELAY] Stream missing video_id - skipping")
                continue

            # Check if already relaying this stream
            if video_id in self.active_relays:
                logger.debug(f"[PEERTUBE] [RELAY] Already relaying {video_id} - skipping")
                continue

            # Start relay for this stream
            self._start_relay(video_id, channel_name)

    def _start_relay(self, video_id: str, channel_name: str) -> None:
        """
        Start FFmpeg relay for a YouTube stream.

        Flow:
        1. Extract HLS URL via yt-dlp
        2. Create PeerTube live stream via API
        3. Start FFmpeg subprocess (HLS → RTMP)
        4. Track process in active_relays
        """
        logger.info(f"[PEERTUBE] [RELAY] [START] Starting relay for {video_id} ({channel_name})")

        try:
            # Step 1: Extract HLS URL
            hls_url = self._extract_hls_url(video_id)
            if not hls_url:
                logger.error(f"[PEERTUBE] [RELAY] [FAIL] Could not extract HLS URL for {video_id}")
                return

            logger.info(f"[PEERTUBE] [RELAY] [OK] Extracted HLS URL")

            # Step 2: Create PeerTube live stream
            peertube_stream = self._create_peertube_live(video_id, channel_name)
            if not peertube_stream:
                logger.error(f"[PEERTUBE] [RELAY] [FAIL] Could not create PeerTube live stream")
                return

            rtmp_url = peertube_stream['rtmp_url']
            stream_key = peertube_stream['stream_key']
            logger.info(f"[PEERTUBE] [RELAY] [OK] Created PeerTube live stream (ID: {peertube_stream['live_id']})")

            # Step 3: Start FFmpeg relay
            ffmpeg_proc = self._start_ffmpeg(hls_url, rtmp_url, stream_key, video_id)
            if not ffmpeg_proc:
                logger.error(f"[PEERTUBE] [RELAY] [FAIL] Could not start FFmpeg process")
                return

            # Step 4: Track relay
            self.active_relays[video_id] = ffmpeg_proc
            logger.info(f"[PEERTUBE] [RELAY] [OK] [ROCKET] Relay ACTIVE for {video_id} (PID: {ffmpeg_proc.pid})")

        except Exception as e:
            logger.error(f"[PEERTUBE] [RELAY] [FAIL] Error starting relay: {e}")
            import traceback
            logger.error(traceback.format_exc())

    def _extract_hls_url(self, video_id: str) -> Optional[str]:
        """Extract HLS manifest URL using yt-dlp"""
        try:
            result = subprocess.run(
                ["yt-dlp", "-f", "best", "-g", f"https://www.youtube.com/watch?v={video_id}"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                logger.warning(f"[PEERTUBE] [RELAY] yt-dlp failed: {result.stderr[:200]}")
                return None

            hls_url = result.stdout.strip()
            return hls_url if hls_url else None

        except FileNotFoundError:
            logger.error("[PEERTUBE] [RELAY] yt-dlp not found - install with: pip install yt-dlp")
            return None
        except Exception as e:
            logger.error(f"[PEERTUBE] [RELAY] Error extracting HLS: {e}")
            return None

    def _create_peertube_live(self, video_id: str, channel_name: str) -> Optional[Dict]:
        """Create live stream on PeerTube via API"""
        if not requests:
            logger.error("[PEERTUBE] [RELAY] requests library not available")
            return None

        try:
            # API endpoint: POST /api/v1/videos/live
            url = f"{self.instance_url}/api/v1/videos/live"
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
            payload = {
                "channelId": self.channel_id,
                "name": f"{channel_name} - YouTube Live Relay",
                "privacy": 1,  # 1 = public, 2 = unlisted, 3 = private
                "category": 15,  # 15 = Science & Technology
                "saveReplay": True,  # Save as VOD after stream ends
                "permanentLive": False
            }

            response = requests.post(url, headers=headers, json=payload, timeout=30)

            if response.status_code not in [200, 201]:
                logger.error(f"[PEERTUBE] [RELAY] API error ({response.status_code}): {response.text[:200]}")
                return None

            data = response.json()
            live_id = data.get('video', {}).get('id')
            rtmp_url = data.get('rtmpUrl', '')
            stream_key = data.get('streamKey', '')

            if not all([live_id, rtmp_url, stream_key]):
                logger.error(f"[PEERTUBE] [RELAY] Invalid API response: {data}")
                return None

            return {
                'live_id': live_id,
                'rtmp_url': rtmp_url,
                'stream_key': stream_key
            }

        except Exception as e:
            logger.error(f"[PEERTUBE] [RELAY] Error creating live stream: {e}")
            return None

    def _start_ffmpeg(self, hls_url: str, rtmp_url: str, stream_key: str, video_id: str) -> Optional[subprocess.Popen]:
        """Start FFmpeg relay process"""
        try:
            full_rtmp = f"{rtmp_url}/{stream_key}"

            # FFmpeg command: HLS input → RTMP output (copy codecs, no transcoding)
            cmd = [
                "ffmpeg",
                "-i", hls_url,
                "-c", "copy",  # Copy video/audio codecs (no transcoding)
                "-f", "flv",   # FLV format for RTMP
                full_rtmp,
                "-loglevel", "error"  # Only show errors
            ]

            # Start process (non-blocking)
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL
            )

            # Wait 2 seconds and check if process crashed
            time.sleep(2)
            poll_result = proc.poll()
            if poll_result is not None:
                # Process exited immediately - read error
                stderr = proc.stderr.read().decode('utf-8', errors='ignore')
                logger.error(f"[PEERTUBE] [RELAY] FFmpeg crashed: {stderr[:500]}")
                return None

            logger.debug(f"[PEERTUBE] [RELAY] FFmpeg started (PID: {proc.pid})")
            return proc

        except FileNotFoundError:
            logger.error("[PEERTUBE] [RELAY] ffmpeg not found - install FFmpeg first")
            return None
        except Exception as e:
            logger.error(f"[PEERTUBE] [RELAY] Error starting FFmpeg: {e}")
            return None

    def stop_relay(self, video_id: str) -> None:
        """Stop relay for a specific video"""
        if video_id not in self.active_relays:
            logger.debug(f"[PEERTUBE] [RELAY] No active relay for {video_id}")
            return

        proc = self.active_relays[video_id]
        logger.info(f"[PEERTUBE] [RELAY] [STOP] Stopping relay for {video_id} (PID: {proc.pid})")

        try:
            # Graceful termination
            proc.terminate()
            try:
                proc.wait(timeout=5)
                logger.info(f"[PEERTUBE] [RELAY] [OK] Relay stopped gracefully")
            except subprocess.TimeoutExpired:
                # Force kill if still running
                proc.kill()
                proc.wait()
                logger.warning(f"[PEERTUBE] [RELAY] [OK] Relay force-killed")

            del self.active_relays[video_id]

        except Exception as e:
            logger.error(f"[PEERTUBE] [RELAY] Error stopping relay: {e}")

    def stop_all_relays(self) -> None:
        """Stop all active relays (cleanup on shutdown)"""
        if not self.active_relays:
            return

        logger.info(f"[PEERTUBE] [RELAY] [CLEANUP] Stopping {len(self.active_relays)} active relay(s)")

        for video_id in list(self.active_relays.keys()):
            self.stop_relay(video_id)

        logger.info("[PEERTUBE] [RELAY] [CLEANUP] All relays stopped")

    def get_relay_status(self) -> Dict:
        """Get status of all active relays (for monitoring)"""
        status = {}
        for video_id, proc in list(self.active_relays.items()):
            poll_result = proc.poll()
            if poll_result is None:
                status[video_id] = "running"
            else:
                status[video_id] = f"stopped (exit code: {poll_result})"
                # Clean up stopped processes
                del self.active_relays[video_id]

        return status
