"""YouTube Live audio source for local STT pipelines.

WSP Compliance:
    - WSP 3: platform_integration domain (YouTube-specific)
    - WSP 11: Public interface defined
    - WSP 49: Module structure compliant
    - WSP 84: Reuses soundcard for WASAPI loopback

Architecture:
    Hybrid Option A - System Audio Loopback
    - Browser plays YouTube LIVE (already running for livechat DAE)
    - WASAPI captures system audio (what speakers play)
    - Works with protected/private streams (no auth issues)
    - Minimal dependencies: soundcard + numpy
"""

from dataclasses import dataclass
from typing import Iterable, Iterator, Optional, Generator
import logging
import time
import numpy as np

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AudioStreamConfig:
    """Configuration for PCM16 audio output."""

    sample_rate_hz: int = 16000
    channels: int = 1
    sample_format: str = "s16le"
    chunk_duration_sec: float = 5.0  # Duration per chunk for STT
    overlap_sec: float = 0.5  # Overlap between chunks for word boundaries
    ffmpeg_path: str = "ffmpeg"
    ytdlp_path: str = "yt-dlp"


@dataclass
class AudioChunk:
    """Audio chunk with metadata for STT processing."""

    audio: np.ndarray  # float32 audio data, shape (samples,)
    sample_rate: int
    timestamp_ms: int  # Unix timestamp when chunk was captured
    duration_sec: float
    chunk_index: int


class SystemAudioCapture:
    """Capture system audio via WASAPI loopback (what speakers play).

    This is the Occam's simplest approach for YouTube Live STT:
    - No yt-dlp authentication battles
    - Works with ANY audio (protected, private, etc.)
    - Just play audio normally, system captures it
    """

    def __init__(self, config: Optional[AudioStreamConfig] = None) -> None:
        self.config = config or AudioStreamConfig()
        self._loopback_mic = None
        self._initialized = False

    def _initialize(self) -> bool:
        """Lazy initialization of audio loopback device."""
        if self._initialized:
            return True

        try:
            import soundcard as sc

            # Get default speaker and create loopback microphone
            speakers = sc.default_speaker()
            logger.info(f"[AUDIO] Default speaker: {speakers.name}")

            # Get loopback device (captures what speakers play)
            self._loopback_mic = sc.get_microphone(
                speakers.name,
                include_loopback=True
            )
            logger.info(f"[AUDIO] Loopback device initialized: {self._loopback_mic.name}")
            self._initialized = True
            return True

        except ImportError:
            logger.error("[AUDIO] soundcard not installed. Run: pip install soundcard")
            return False
        except Exception as e:
            logger.error(f"[AUDIO] Failed to initialize loopback: {e}")
            return False

    def capture_chunk(self, duration_sec: Optional[float] = None) -> Optional[AudioChunk]:
        """Capture a single audio chunk from system audio.

        Args:
            duration_sec: Duration to capture (default from config)

        Returns:
            AudioChunk with float32 audio data, or None on failure
        """
        if not self._initialize():
            return None

        duration = duration_sec or self.config.chunk_duration_sec
        num_frames = int(self.config.sample_rate_hz * duration)

        try:
            timestamp_ms = int(time.time() * 1000)

            with self._loopback_mic.recorder(
                samplerate=self.config.sample_rate_hz,
                channels=self.config.channels
            ) as rec:
                audio = rec.record(numframes=num_frames)

            # Ensure mono and float32
            if len(audio.shape) > 1:
                audio = audio.mean(axis=1)
            audio = audio.astype(np.float32)

            return AudioChunk(
                audio=audio,
                sample_rate=self.config.sample_rate_hz,
                timestamp_ms=timestamp_ms,
                duration_sec=duration,
                chunk_index=0
            )

        except Exception as e:
            logger.error(f"[AUDIO] Capture failed: {e}")
            return None

    def stream_chunks(self, max_chunks: Optional[int] = None) -> Generator[AudioChunk, None, None]:
        """Continuously stream audio chunks for real-time STT.

        Args:
            max_chunks: Maximum chunks to yield (None = infinite)

        Yields:
            AudioChunk objects for STT processing
        """
        if not self._initialize():
            return

        chunk_idx = 0
        chunk_duration = self.config.chunk_duration_sec
        overlap = self.config.overlap_sec

        # Calculate frames
        chunk_frames = int(self.config.sample_rate_hz * chunk_duration)
        overlap_frames = int(self.config.sample_rate_hz * overlap)
        step_frames = chunk_frames - overlap_frames

        logger.info(f"[AUDIO] Streaming: {chunk_duration}s chunks, {overlap}s overlap")

        # Rolling buffer for overlap
        buffer = np.array([], dtype=np.float32)

        try:
            with self._loopback_mic.recorder(
                samplerate=self.config.sample_rate_hz,
                channels=self.config.channels
            ) as rec:
                while max_chunks is None or chunk_idx < max_chunks:
                    # Record step_frames (not full chunk, to maintain overlap)
                    new_audio = rec.record(numframes=step_frames)

                    # Ensure mono and float32
                    if len(new_audio.shape) > 1:
                        new_audio = new_audio.mean(axis=1)
                    new_audio = new_audio.astype(np.float32)

                    # Append to buffer
                    buffer = np.concatenate([buffer, new_audio])

                    # Yield chunk when buffer is full
                    if len(buffer) >= chunk_frames:
                        chunk_audio = buffer[:chunk_frames]
                        buffer = buffer[step_frames:]  # Keep overlap

                        yield AudioChunk(
                            audio=chunk_audio,
                            sample_rate=self.config.sample_rate_hz,
                            timestamp_ms=int(time.time() * 1000),
                            duration_sec=chunk_duration,
                            chunk_index=chunk_idx
                        )
                        chunk_idx += 1

        except KeyboardInterrupt:
            logger.info("[AUDIO] Streaming stopped by user")
        except Exception as e:
            logger.error(f"[AUDIO] Streaming error: {e}")

    def test_capture(self, duration_sec: float = 3.0) -> bool:
        """Test audio capture with a short recording.

        Returns:
            True if capture works and audio level detected
        """
        logger.info(f"[AUDIO] Testing capture for {duration_sec}s...")
        chunk = self.capture_chunk(duration_sec)

        if chunk is None:
            logger.error("[AUDIO] Test failed: No audio captured")
            return False

        # Check audio level
        rms = np.sqrt(np.mean(chunk.audio ** 2))
        peak = np.max(np.abs(chunk.audio))

        logger.info(f"[AUDIO] Test results: RMS={rms:.4f}, Peak={peak:.4f}, Samples={len(chunk.audio)}")

        if rms < 0.0001:
            logger.warning("[AUDIO] Very low audio level - is audio playing?")
            return False

        logger.info("[AUDIO] Test passed - audio capture working")
        return True


class YouTubeLiveAudioSource:
    """Resolve a YouTube live source and stream PCM16 audio.

    Supports two modes:
    1. System Audio Loopback (default, recommended)
       - Browser plays live stream, system captures audio
       - Works with protected/private streams

    2. yt-dlp Stream Extract (fallback)
       - Direct stream extraction via yt-dlp + ffmpeg
       - May have auth issues with some streams
    """

    def __init__(self, config: Optional[AudioStreamConfig] = None) -> None:
        self.config = config or AudioStreamConfig()
        self._system_capture = SystemAudioCapture(config)

    def resolve_stream_url(self, input_ref: str) -> str:
        """Resolve a live stream URL from a channel id, video id, or URL.

        Note: For system audio loopback mode, this just returns the input
        as the browser handles stream resolution.
        """
        # For loopback mode, just return the URL for browser navigation
        if input_ref.startswith("http"):
            return input_ref
        elif input_ref.startswith("UC"):
            # Channel ID - construct live URL
            return f"https://www.youtube.com/channel/{input_ref}/live"
        else:
            # Assume video ID
            return f"https://www.youtube.com/watch?v={input_ref}"

    def stream_pcm16(self, input_ref: str) -> Iterable[bytes]:
        """Yield PCM16 mono audio chunks for downstream STT.

        Note: For system audio loopback, input_ref is ignored.
        The browser should already be playing the stream.
        """
        for chunk in self._system_capture.stream_chunks():
            # Convert float32 to int16 PCM
            pcm16 = (chunk.audio * 32767).astype(np.int16)
            yield pcm16.tobytes()

    def stream_audio_chunks(self, max_chunks: Optional[int] = None) -> Generator[AudioChunk, None, None]:
        """Stream AudioChunk objects for direct STT processing.

        This is the preferred interface for faster-whisper integration.
        """
        yield from self._system_capture.stream_chunks(max_chunks)

    def capture_single(self, duration_sec: float = 5.0) -> Optional[AudioChunk]:
        """Capture a single audio chunk for testing/one-shot STT."""
        return self._system_capture.capture_chunk(duration_sec)

    def test_audio(self, duration_sec: float = 3.0) -> bool:
        """Test audio capture."""
        return self._system_capture.test_capture(duration_sec)


# Convenience function
def get_audio_source(config: Optional[AudioStreamConfig] = None) -> YouTubeLiveAudioSource:
    """Get a configured audio source instance."""
    return YouTubeLiveAudioSource(config)
