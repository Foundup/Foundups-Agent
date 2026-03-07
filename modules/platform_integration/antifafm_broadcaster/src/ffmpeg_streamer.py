"""
FFmpeg Streamer for antifaFM YouTube Live Broadcaster

Manages FFmpeg subprocess for audio-to-video streaming.
Pattern: modules/communication/youtube_shorts/src/video_editor.py

Layers:
- Layer 1: Static image + audio (MVP)
- Layer 2.5: Visual effects (Ken Burns, Color Pulse, GIF Overlay)
- Layer 2.5D: Karaoke overlay with beat-synced text (STT)
- Layer 3: Audio visualization (waveform, spectrum)

Visual Schemes:
- VIDEO_LOOP: MP4/WebM background loop (default, working)
- WAVEFORM: Audio waveform visualization
- SPECTRUM: Frequency spectrum display
- KARAOKE: STT lyrics with beat-synced animation

WSP Compliance:
- WSP 27: Universal DAE Architecture (Phase 2: Agentic execution)
- WSP 50: Pre-Action Verification (subprocess safety)
- WSP 84: Code Reuse (visual effects module integration)
"""

import logging
import os
import subprocess
import signal
import time
import threading
from collections import deque
from pathlib import Path
from typing import Optional, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum

if TYPE_CHECKING:
    from .visual_effects import VisualEffectsBuilder
    from .scheme_manager import SchemeManager, OutputScheme

logger = logging.getLogger(__name__)


class StreamState(Enum):
    """FFmpeg stream states."""
    STOPPED = "stopped"
    STARTING = "starting"
    STREAMING = "streaming"
    ERROR = "error"
    STOPPING = "stopping"


@dataclass
class StreamConfig:
    """Configuration for FFmpeg stream."""
    audio_url: str
    visual_path: str
    rtmp_url: str
    stream_key: str
    audio_bitrate: str = "128k"
    audio_rate: int = 44100
    video_preset: str = "ultrafast"
    # Layer 2.5: Visual effects
    enable_visual_effects: bool = True
    gif_overlay_path: Optional[str] = None
    # Visual scheme selection (video_loop, waveform, spectrum, karaoke)
    output_scheme: str = "video_loop"
    # Scheme rotation (sequential, random, manual)
    scheme_rotation: str = "manual"


class FFmpegStreamerError(Exception):
    """FFmpeg streaming error."""
    pass


class FFmpegStreamer:
    """
    Manages FFmpeg subprocess for streaming audio to YouTube Live.

    Converts Icecast audio stream + static image to RTMP video stream.
    """

    def __init__(self, config: Optional[StreamConfig] = None):
        """
        Initialize FFmpeg streamer.

        Args:
            config: Stream configuration. If None, loads from environment.
        """
        self.config = config or self._load_config_from_env()
        self.process: Optional[subprocess.Popen] = None
        self.state = StreamState.STOPPED
        self.start_time: Optional[float] = None
        self.error_message: Optional[str] = None
        self.scheme_manager = None  # Initialized lazily if needed
        # Continuous stderr monitoring for debugging
        self._stderr_buffer = deque(maxlen=50)  # Keep last 50 lines
        self._stderr_thread: Optional[threading.Thread] = None
        self._stop_stderr_monitor = threading.Event()
        self._verify_ffmpeg_installed()

        # Initialize scheme manager if using scheme-based output
        if self.config.output_scheme != "video_loop":
            self._init_scheme_manager()

    def _load_config_from_env(self) -> StreamConfig:
        """Load configuration from environment variables."""
        audio_url = os.getenv("ANTIFAFM_STREAM_URL", "https://a12.asurahosting.com/listen/antifafm/radio.mp3")
        visual_path = os.getenv(
            "ANTIFAFM_DEFAULT_VISUAL",
            "modules/platform_integration/antifafm_broadcaster/assets/default_visual.png"
        )
        stream_key = os.getenv("ANTIFAFM_YOUTUBE_STREAM_KEY", "")

        # Layer control: ANTIFAFM_FX_ENABLED=false disables all visual effects (Layer 1 only)
        enable_fx = os.getenv("ANTIFAFM_FX_ENABLED", "true").lower() in ("true", "1", "yes")

        if not stream_key:
            logger.warning("ANTIFAFM_YOUTUBE_STREAM_KEY not set - streaming will fail")

        if not enable_fx:
            logger.info("[LAYER] Visual effects DISABLED (ANTIFAFM_FX_ENABLED=false) - running Layer 1 MVP")

        # Visual scheme selection (video_loop, waveform, spectrum, karaoke, news_ticker)
        output_scheme = os.getenv("ANTIFAFM_OUTPUT_SCHEME", "video_loop")
        scheme_rotation = os.getenv("ANTIFAFM_SCHEME_ROTATION", "manual")

        # RTMP URL resolution priority:
        # 1. ANTIFAFM_RTMP_URL env var (explicit override)
        # 2. YouTube Data API (stream-specific ingest URL)
        # 3. Generic fallback (may not work for all streams)
        rtmp_url = os.getenv("ANTIFAFM_RTMP_URL", "")
        token_set_raw = os.getenv("ANTIFAFM_YOUTUBE_TOKEN_SET", "10").strip()
        token_set = int(token_set_raw) if token_set_raw.isdigit() else None

        if not rtmp_url:
            # Try API resolution for stream-specific ingest URL
            # This is critical - generic URLs like a.rtmps.youtube.com may not work
            # YouTube assigns specific ingest endpoints per stream
            try:
                from .youtube_ingest_resolver import get_ingest_url_with_fallback
                rtmp_url, is_api_resolved = get_ingest_url_with_fallback(
                    stream_key=stream_key,
                    fallback_url="rtmps://a.rtmps.youtube.com:443/live2",
                    token_index=token_set,
                )
                if is_api_resolved:
                    logger.info(f"[INGEST] Using API-resolved URL: {rtmp_url[:50]}...")
                else:
                    logger.warning("[INGEST] API resolution failed, using generic fallback URL")
            except ImportError:
                logger.warning("[INGEST] Ingest resolver not available, using generic URL")
                rtmp_url = "rtmps://a.rtmps.youtube.com:443/live2"
            except Exception as e:
                logger.error(f"[INGEST] Error resolving ingest URL: {e}")
                rtmp_url = "rtmps://a.rtmps.youtube.com:443/live2"

        return StreamConfig(
            audio_url=audio_url,
            visual_path=visual_path,
            rtmp_url=rtmp_url,
            stream_key=stream_key,
            enable_visual_effects=enable_fx,
            output_scheme=output_scheme,
            scheme_rotation=scheme_rotation,
        )

    def _verify_ffmpeg_installed(self) -> bool:
        """Verify FFmpeg is installed and accessible."""
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                check=True,
                timeout=10
            )
            logger.debug("FFmpeg verified: installed and accessible")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
            logger.error(f"FFmpeg not available: {e}")
            raise FFmpegStreamerError(
                "FFmpeg not installed. Install via: choco install ffmpeg (Windows) "
                "or apt install ffmpeg (Linux)"
            )

    def _init_scheme_manager(self) -> None:
        """Initialize scheme manager for visual output modes."""
        try:
            from .scheme_manager import SchemeManager, OutputScheme, SchemeManagerConfig, SchemeConfig

            # Build scheme config from environment
            config = SchemeManagerConfig(
                rotation_mode=self.config.scheme_rotation,
            )

            # Set default scheme
            for scheme in OutputScheme:
                if scheme.value == self.config.output_scheme:
                    config.default_scheme = scheme
                    break

            self.scheme_manager = SchemeManager(config)
            logger.info(f"[SCHEME] Manager initialized: {self.config.output_scheme}")
        except ImportError as e:
            logger.warning(f"[SCHEME] scheme_manager module not available: {e}")
            self.scheme_manager = None
        except Exception as e:
            logger.warning(f"[SCHEME] Failed to initialize scheme manager: {e}")
            self.scheme_manager = None

    def _build_ffmpeg_command(self) -> list:
        """
        Build FFmpeg command for streaming.

        Layer 1 (no effects):
        ffmpeg -re -i <audio_url> -loop 1 -i <image>
               -c:v libx264 -preset ultrafast -tune stillimage
               -c:a aac -b:a 128k -ar 44100
               -f flv <rtmp_url>/<stream_key>

        Layer 2.5 (with effects):
        ffmpeg -re -i <audio_url> -loop 1 -i <image> [-ignore_loop 0 -i <gif>]
               -filter_complex "<visual_effects>"
               -map "[out]" -map 0:a
               -c:v libx264 -preset ultrafast
               -c:a aac -b:a 128k -ar 44100
               -f flv <rtmp_url>/<stream_key>
        """
        if not self.config.stream_key:
            raise FFmpegStreamerError("Stream key not configured")

        visual_path = Path(self.config.visual_path)
        if not visual_path.exists():
            logger.warning(f"Visual not found: {visual_path}, using placeholder")
            # Create a simple placeholder if missing
            self._create_placeholder_visual(visual_path)

        rtmp_target = f"{self.config.rtmp_url}/{self.config.stream_key}"

        # Detect if visual is video or image
        video_extensions = {'.mp4', '.webm', '.mkv', '.avi', '.mov'}
        is_video = visual_path.suffix.lower() in video_extensions

        # Check for scheme-based visual output (waveform, spectrum, karaoke)
        use_scheme_filter = self.scheme_manager is not None and self.config.output_scheme != "video_loop"

        # Base command - inputs
        cmd = [
            "ffmpeg",
            "-re",  # Read input at native frame rate (real-time streaming)
            "-i", self.config.audio_url,  # Audio input (Icecast stream) [0]
        ]

        # Scheme-based visual modes (waveform, spectrum use audio as video source)
        if use_scheme_filter and self.config.output_scheme in ("waveform", "spectrum"):
            # No visual input needed - generate video from audio
            logger.info(f"[SCHEME] Using {self.config.output_scheme} mode (audio visualization)")
        else:
            # Add visual input (different for video vs image)
            if is_video:
                # Video: loop infinitely, ignore its audio
                cmd.extend(["-stream_loop", "-1", "-i", str(visual_path.absolute())])
                logger.info(f"[VIDEO] Using video background: {visual_path.name} (looped)")
            else:
                # Image: loop single frame
                cmd.extend(["-loop", "1", "-i", str(visual_path.absolute())])

        # Layer 3: Scheme-based visual output (waveform, spectrum, karaoke)
        use_effects = False
        if use_scheme_filter:
            filter_complex = self.scheme_manager.build_ffmpeg_filter()
            cmd.extend(["-filter_complex", filter_complex])
            cmd.extend(["-map", "[out]", "-map", "0:a"])
            use_effects = True
            logger.info(f"[SCHEME] Using {self.config.output_scheme} filter")

        # Layer 2.5: Visual effects (only if not using scheme filter)
        elif is_video:
            # Video background: simpler filter (scale + format, no Ken Burns)
            # Scale to 1920x1080, convert to yuv420p, and optionally apply color pulse
            filter_parts = ["[1:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2"]

            # Optional: Add color pulse to video
            if self.config.enable_visual_effects and os.getenv("ANTIFAFM_FX_COLOR_PULSE", "true").lower() in ("true", "1"):
                filter_parts.append("hue=h=sin(t*0.1)*15")

            filter_parts.append("format=yuv420p[out]")
            filter_complex = ",".join(filter_parts)
            cmd.extend(["-filter_complex", filter_complex])
            cmd.extend(["-map", "[out]", "-map", "0:a"])
            use_effects = True
            logger.info(f"[VIDEO] Video filter applied: scale + format" +
                       (" + color_pulse" if "hue=" in filter_complex else ""))
        elif self.config.enable_visual_effects:
            try:
                from .visual_effects import VisualEffectsBuilder, VisualEffectsConfig, GifOverlayConfig

                # Configure GIF overlay if path provided
                fx_config = VisualEffectsConfig()
                if self.config.gif_overlay_path:
                    fx_config.gif_overlay.gif_path = self.config.gif_overlay_path
                else:
                    # Check default location
                    default_gif = Path(__file__).parent.parent / "assets" / "overlays" / "antifafm_pulse.gif"
                    if default_gif.exists():
                        fx_config.gif_overlay.gif_path = str(default_gif)
                    else:
                        fx_config.gif_overlay.enabled = False

                fx_builder = VisualEffectsBuilder(fx_config)

                # Add GIF input if enabled
                additional_inputs = fx_builder.get_additional_inputs()
                if additional_inputs:
                    cmd.extend(additional_inputs)

                # Build filter_complex
                filter_complex = fx_builder.build_filter_complex(base_input_index=1)
                if filter_complex:
                    cmd.extend(["-filter_complex", filter_complex])
                    use_effects = True
                    logger.info(f"[FX] Visual effects enabled: {fx_builder._enabled_effects()}")

                # Add output mapping
                output_map = fx_builder.get_output_map()
                if output_map:
                    cmd.extend(output_map)

            except ImportError as e:
                logger.warning(f"[FX] Visual effects module not available: {e}")
            except Exception as e:
                logger.warning(f"[FX] Visual effects error (falling back to Layer 1): {e}")

        # Video encoding - optimized for stable streaming
        cmd.extend([
            "-c:v", "libx264",  # Video codec
            "-preset", self.config.video_preset,  # Encoding speed (ultrafast)
            "-b:v", "2500k",  # Video bitrate (lower for stability, YouTube min is 1500k for 720p)
            "-maxrate", "3000k",  # Max bitrate cap
            "-bufsize", "6000k",  # Buffer size (2x maxrate for smooth streaming)
            "-g", "60",  # Keyframe interval (2 seconds at 30fps)
            "-force_key_frames", "expr:gte(t,n_forced*2)",  # Force keyframes every 2s (YouTube requires ≤4s)
            "-threads", "2",  # Limit CPU threads for stability
        ])

        # Only use stillimage tune when no effects (static image)
        if not use_effects:
            cmd.extend(["-tune", "stillimage"])

        # Audio encoding
        cmd.extend([
            "-c:a", "aac",  # Audio codec
            "-b:a", self.config.audio_bitrate,  # Audio bitrate
            "-ar", str(self.config.audio_rate),  # Audio sample rate
            "-shortest",  # End when shortest input ends (audio stream)
            "-f", "flv",  # Output format for RTMP
            rtmp_target,  # YouTube RTMP endpoint
        ])

        return cmd

    def _create_placeholder_visual(self, path: Path) -> None:
        """Create a simple placeholder image if none exists."""
        path.parent.mkdir(parents=True, exist_ok=True)

        # Create a simple 1920x1080 black image with text using FFmpeg
        placeholder_cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", "color=c=black:s=1920x1080:d=1",
            "-vf", "drawtext=text='antifaFM':fontsize=72:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2",
            "-frames:v", "1",
            str(path.absolute())
        ]

        try:
            subprocess.run(placeholder_cmd, capture_output=True, check=True, timeout=30)
            logger.info(f"Created placeholder visual: {path}")
        except Exception as e:
            logger.error(f"Failed to create placeholder: {e}")
            raise FFmpegStreamerError(f"Cannot create placeholder visual: {e}")

    def _kill_orphan_ffmpeg_streams(self) -> int:
        """
        Kill any orphaned FFmpeg processes streaming to YouTube RTMP.

        Returns:
            int: Number of processes killed
        """
        killed = 0
        try:
            if os.name == 'nt':
                # Windows: Find and kill FFmpeg processes streaming to rtmp
                result = subprocess.run(
                    ['wmic', 'process', 'where', "name='ffmpeg.exe'", 'get', 'processid,commandline'],
                    capture_output=True, text=True, timeout=10
                )
                for line in result.stdout.splitlines():
                    if ('rtmp://' in line or 'rtmps://' in line) and self.config.stream_key in line:
                        # Extract PID (last number in line)
                        parts = line.strip().split()
                        if parts:
                            try:
                                pid = int(parts[-1])
                                subprocess.run(['taskkill', '/F', '/PID', str(pid)],
                                             capture_output=True, timeout=5)
                                logger.info(f"[CLEANUP] Killed orphaned FFmpeg process {pid}")
                                killed += 1
                            except (ValueError, subprocess.SubprocessError):
                                pass
            else:
                # Linux/Mac: Use pkill
                subprocess.run(['pkill', '-f', f'ffmpeg.*{self.config.stream_key}'],
                             capture_output=True, timeout=5)
                killed = 1  # Can't easily count on Linux
        except Exception as e:
            logger.debug(f"[CLEANUP] Orphan cleanup error (non-fatal): {e}")

        if killed > 0:
            logger.info(f"[CLEANUP] Killed {killed} orphaned FFmpeg stream(s)")
            time.sleep(1)  # Let processes fully terminate

        return killed

    def start(self) -> bool:
        """
        Start FFmpeg streaming process.

        Returns:
            bool: True if started successfully

        Raises:
            FFmpegStreamerError: If start fails
        """
        if self.state == StreamState.STREAMING:
            logger.warning("Stream already running")
            return True

        if self.state == StreamState.STARTING:
            logger.warning("Stream is starting, please wait")
            return False

        self.state = StreamState.STARTING
        self.error_message = None

        # Kill any orphaned FFmpeg streams to same endpoint
        self._kill_orphan_ffmpeg_streams()

        try:
            logger.info("[BROADCAST] Building FFmpeg command...")
            cmd = self._build_ffmpeg_command()
            logger.info(f"[BROADCAST] Starting FFmpeg stream to YouTube Live")

            # Log command for debugging (mask stream key)
            safe_cmd = [c if self.config.stream_key not in c else '***KEY***' for c in cmd]
            logger.info(f"[BROADCAST] FFmpeg command ({len(cmd)} args): {' '.join(safe_cmd[:10])}...")
            logger.debug(f"[BROADCAST] Full command: {' '.join(safe_cmd)}")

            # Start FFmpeg process
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL,  # No interactive input
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
            )

            # Start continuous stderr monitoring
            self._start_stderr_monitor()

            # Give FFmpeg time to connect to RTMP (5 seconds)
            logger.info("[BROADCAST] Waiting for RTMP connection...")
            time.sleep(5)

            # Check if process is still running
            if self.process.poll() is not None:
                # Process exited - get error
                _, stderr = self.process.communicate(timeout=5)
                error_text = stderr.decode('utf-8', errors='replace')
                self.state = StreamState.ERROR
                self.error_message = error_text[:500]
                logger.error(f"[BROADCAST] FFmpeg exited: {error_text[:300]}")
                raise FFmpegStreamerError(f"FFmpeg exited immediately: {error_text[:200]}")

            # Read initial stderr to check for connection errors
            stderr_sample = self._read_stderr_nonblocking()
            if stderr_sample:
                logger.debug(f"[BROADCAST] FFmpeg stderr: {stderr_sample[:200]}")
                # Check for common errors
                if "Connection refused" in stderr_sample or "Connection timed out" in stderr_sample:
                    self.state = StreamState.ERROR
                    self.error_message = "RTMP connection failed"
                    self.process.terminate()
                    raise FFmpegStreamerError(f"RTMP connection failed: {stderr_sample[:200]}")
                if "Invalid stream key" in stderr_sample or "Unauthorized" in stderr_sample:
                    self.state = StreamState.ERROR
                    self.error_message = "Invalid stream key"
                    self.process.terminate()
                    raise FFmpegStreamerError("Invalid YouTube stream key")
                # Check for successful connection indicators
                if "frame=" in stderr_sample or "Output #0" in stderr_sample:
                    logger.info("[BROADCAST] RTMP connection verified - frames being sent")

            self.state = StreamState.STREAMING
            self.start_time = time.time()
            logger.info("[OK] FFmpeg streaming started successfully")
            return True

        except FFmpegStreamerError:
            raise
        except Exception as e:
            self.state = StreamState.ERROR
            self.error_message = str(e)
            logger.error(f"Failed to start FFmpeg: {e}")
            raise FFmpegStreamerError(f"Failed to start streaming: {e}")

    def _start_stderr_monitor(self) -> None:
        """Start continuous stderr monitoring in background thread."""
        self._stop_stderr_monitor.clear()
        self._stderr_buffer.clear()

        def monitor_stderr():
            """Background thread to continuously read FFmpeg stderr."""
            while not self._stop_stderr_monitor.is_set():
                if self.process is None or self.process.stderr is None:
                    break
                try:
                    line = self.process.stderr.readline()
                    if line:
                        decoded = line.decode('utf-8', errors='replace').strip()
                        if decoded:
                            self._stderr_buffer.append(decoded)
                            # Log important FFmpeg messages
                            if any(err in decoded.lower() for err in ['error', 'failed', 'refused', 'broken']):
                                logger.warning(f"[FFMPEG] {decoded}")
                            elif 'frame=' in decoded:
                                # Frame progress - log occasionally
                                if len(self._stderr_buffer) % 20 == 0:
                                    logger.debug(f"[FFMPEG] {decoded}")
                    elif self.process.poll() is not None:
                        # Process ended
                        logger.warning(f"[FFMPEG] Process exited with code {self.process.returncode}")
                        break
                except Exception as e:
                    if not self._stop_stderr_monitor.is_set():
                        logger.debug(f"[FFMPEG] stderr read error: {e}")
                    break

        self._stderr_thread = threading.Thread(target=monitor_stderr, daemon=True)
        self._stderr_thread.start()
        logger.debug("[FFMPEG] stderr monitor started")

    def _stop_stderr_monitor_thread(self) -> None:
        """Stop the stderr monitoring thread."""
        self._stop_stderr_monitor.set()
        if self._stderr_thread and self._stderr_thread.is_alive():
            self._stderr_thread.join(timeout=2.0)
        self._stderr_thread = None

    def get_last_stderr(self, lines: int = 20) -> str:
        """Get the last N lines of FFmpeg stderr for debugging."""
        buffer_lines = list(self._stderr_buffer)
        return '\n'.join(buffer_lines[-lines:])

    def _read_stderr_nonblocking(self, max_bytes: int = 4096) -> str:
        """Read available stderr without blocking."""
        # First check our buffer from the monitoring thread
        if self._stderr_buffer:
            return '\n'.join(list(self._stderr_buffer)[-10:])

        import select
        if self.process is None or self.process.stderr is None:
            return ""

        try:
            if os.name == 'nt':
                # Windows: use peek() to check available data
                import msvcrt
                import ctypes
                from ctypes import wintypes

                # Simple approach: just try to read with a short timeout via thread
                result = []
                def read_stderr():
                    try:
                        # Read a chunk (this may block briefly)
                        data = self.process.stderr.read(max_bytes)
                        if data:
                            result.append(data.decode('utf-8', errors='replace'))
                    except Exception:
                        pass

                thread = threading.Thread(target=read_stderr)
                thread.daemon = True
                thread.start()
                thread.join(timeout=1.0)  # Wait max 1 second
                return result[0] if result else ""
            else:
                # Unix: use select
                readable, _, _ = select.select([self.process.stderr], [], [], 0.5)
                if readable:
                    data = self.process.stderr.read(max_bytes)
                    return data.decode('utf-8', errors='replace') if data else ""
                return ""
        except Exception as e:
            logger.debug(f"[BROADCAST] stderr read error: {e}")
            return ""

    def stop(self, timeout: float = 10.0) -> bool:
        """
        Stop FFmpeg streaming process gracefully.

        Args:
            timeout: Seconds to wait for graceful shutdown

        Returns:
            bool: True if stopped successfully
        """
        if self.state == StreamState.STOPPED:
            logger.debug("Stream already stopped")
            return True

        if self.process is None:
            self.state = StreamState.STOPPED
            return True

        self.state = StreamState.STOPPING
        logger.info("[STOP] Stopping FFmpeg stream...")

        # Stop stderr monitor first
        self._stop_stderr_monitor_thread()

        try:
            # Send SIGTERM for graceful shutdown
            if os.name == 'nt':
                # Windows: terminate
                self.process.terminate()
            else:
                # Unix: SIGTERM
                self.process.send_signal(signal.SIGTERM)

            # Wait for graceful exit
            try:
                self.process.wait(timeout=timeout)
                logger.info("[OK] FFmpeg stopped gracefully")
            except subprocess.TimeoutExpired:
                # Force kill if graceful shutdown fails
                logger.warning("FFmpeg didn't stop gracefully, forcing kill...")
                self.process.kill()
                self.process.wait(timeout=5)
                logger.info("[OK] FFmpeg force-killed")

            self.state = StreamState.STOPPED
            self.process = None
            return True

        except Exception as e:
            logger.error(f"Error stopping FFmpeg: {e}")
            self.state = StreamState.ERROR
            self.error_message = str(e)
            return False

    def is_running(self) -> bool:
        """Check if FFmpeg process is currently running."""
        if self.process is None:
            return False
        return self.process.poll() is None

    def is_streaming_healthy(self) -> tuple[bool, str]:
        """
        Check if FFmpeg is actually streaming (not just running).

        Returns:
            tuple: (is_healthy, status_message)
        """
        if not self.is_running():
            # Process died - get last stderr for debugging
            last_stderr = self.get_last_stderr(10)
            if last_stderr:
                logger.error(f"[FFMPEG] Process died. Last output:\n{last_stderr}")
                self.error_message = f"Process died: {last_stderr[-200:]}"
            return False, f"FFmpeg process not running. Last error: {last_stderr[-100:] if last_stderr else 'unknown'}"

        # Check stderr for frame progress
        stderr_sample = self._read_stderr_nonblocking()
        if stderr_sample:
            if "frame=" in stderr_sample:
                # Extract frame info for status
                import re
                match = re.search(r'frame=\s*(\d+)', stderr_sample)
                if match:
                    frames = match.group(1)
                    return True, f"Streaming OK (frame={frames})"
            if "Connection refused" in stderr_sample or "broken pipe" in stderr_sample.lower():
                return False, f"RTMP connection lost: {stderr_sample[-100:]}"
            if "error" in stderr_sample.lower():
                return False, f"FFmpeg error: {stderr_sample[-150:]}"

        # Process running but no stderr - assume OK
        return True, "Process running"

    def get_uptime(self) -> Optional[float]:
        """Get stream uptime in seconds, or None if not streaming."""
        if self.state != StreamState.STREAMING or self.start_time is None:
            return None
        return time.time() - self.start_time

    def get_status(self) -> dict:
        """Get current streamer status."""
        uptime = self.get_uptime()
        return {
            "state": self.state.value,
            "is_running": self.is_running(),
            "uptime_seconds": uptime,
            "uptime_formatted": self._format_uptime(uptime) if uptime else None,
            "audio_url": self.config.audio_url,
            "error": self.error_message,
            "last_stderr": self.get_last_stderr(5),  # Last 5 lines for debugging
        }

    @staticmethod
    def _format_uptime(seconds: Optional[float]) -> str:
        """Format uptime seconds as human-readable string."""
        if seconds is None:
            return "N/A"
        hours, remainder = divmod(int(seconds), 3600)
        minutes, secs = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"


# CLI testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    print("[TEST] FFmpeg Streamer")
    print("=" * 40)

    try:
        streamer = FFmpegStreamer()
        print(f"[OK] Streamer initialized")
        print(f"    Audio URL: {streamer.config.audio_url}")
        print(f"    Visual: {streamer.config.visual_path}")
        print(f"    Stream Key: {'***' if streamer.config.stream_key else 'NOT SET'}")

        if not streamer.config.stream_key:
            print("\n[WARN] Set ANTIFAFM_YOUTUBE_STREAM_KEY to test streaming")
        else:
            print("\n[INFO] Starting 10-second test stream...")
            streamer.start()
            time.sleep(10)
            status = streamer.get_status()
            print(f"    Status: {status}")
            streamer.stop()
            print("[OK] Test complete")

    except FFmpegStreamerError as e:
        print(f"[ERROR] {e}")
