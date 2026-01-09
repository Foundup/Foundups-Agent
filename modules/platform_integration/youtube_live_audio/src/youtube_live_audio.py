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


# =============================================================================
# PHASE 2: VIDEO ARCHIVE EXTRACTION (Sprint 5)
# =============================================================================

@dataclass
class VideoInfo:
    """Metadata for a YouTube video."""
    video_id: str
    title: str
    duration_sec: float
    upload_date: str
    channel_id: str
    url: str


class VideoArchiveExtractor:
    """Extract audio from YouTube video archives for transcription.

    Uses yt-dlp for:
    - Listing channel videos (0 API quota cost)
    - Downloading audio from videos
    - Converting to WAV format for STT

    WSP Compliance:
    - WSP 84: Reuses yt-dlp pattern from acoustic_lab
    - WSP 50: Pre-action verification (checks cache before download)
    """

    def __init__(
        self,
        cache_dir: Optional[str] = None,
        config: Optional[AudioStreamConfig] = None
    ) -> None:
        """Initialize video archive extractor.

        Args:
            cache_dir: Directory to cache extracted audio (default: memory/audio_cache)
            config: Audio configuration (sample rate, etc.)
        """
        from pathlib import Path
        self.config = config or AudioStreamConfig()
        self.cache_dir = Path(cache_dir) if cache_dir else Path("memory/audio_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._yt_dlp = None

    def _get_yt_dlp(self):
        """Lazy initialization of yt-dlp."""
        if self._yt_dlp is None:
            try:
                import yt_dlp
                self._yt_dlp = yt_dlp
                logger.info("[ARCHIVE] yt-dlp initialized")
            except ImportError:
                logger.error("[ARCHIVE] yt-dlp not installed. Run: pip install yt-dlp")
                raise ImportError("yt-dlp required for video archive extraction")
        return self._yt_dlp

    def list_channel_videos(
        self,
        channel_id: str,
        max_videos: int = 50
    ) -> Generator[VideoInfo, None, None]:
        """List videos from a YouTube channel using yt-dlp.

        Uses yt-dlp playlist extraction (0 API quota cost).

        Args:
            channel_id: YouTube channel ID (e.g., "UC-LSSlOZwpGIRIYihaz8zCw")
            max_videos: Maximum videos to retrieve

        Yields:
            VideoInfo for each video
        """
        yt_dlp = self._get_yt_dlp()

        # Use channel/videos URL for full video list
        channel_url = f"https://www.youtube.com/channel/{channel_id}/videos"

        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,  # Don't download, just extract info
            'playlistend': max_videos,
        }

        logger.info(f"[ARCHIVE] Listing videos from channel: {channel_id}")

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(channel_url, download=False)

                if not info or 'entries' not in info:
                    logger.warning("[ARCHIVE] No videos found in channel")
                    return

                count = 0
                for entry in info['entries']:
                    if entry is None:
                        continue
                    if count >= max_videos:
                        break

                    yield VideoInfo(
                        video_id=entry.get('id', ''),
                        title=entry.get('title', 'Unknown'),
                        duration_sec=entry.get('duration', 0) or 0,
                        upload_date=entry.get('upload_date', ''),
                        channel_id=channel_id,
                        url=f"https://www.youtube.com/watch?v={entry.get('id', '')}"
                    )
                    count += 1

                logger.info(f"[ARCHIVE] Found {count} videos")

        except Exception as e:
            logger.error(f"[ARCHIVE] Failed to list videos: {e}")

    def extract_audio(
        self,
        video_id: str,
        use_cache: bool = True
    ) -> Optional[np.ndarray]:
        """Extract audio from a YouTube video.

        Args:
            video_id: YouTube video ID
            use_cache: Use cached audio if available

        Returns:
            Float32 audio array, or None on failure
        """
        import subprocess
        import tempfile
        from pathlib import Path

        yt_dlp = self._get_yt_dlp()

        # Check cache
        cache_path = self.cache_dir / f"{video_id}.wav"
        if use_cache and cache_path.exists():
            logger.info(f"[ARCHIVE] Using cached audio: {video_id}")
            return self._load_wav(cache_path)

        video_url = f"https://www.youtube.com/watch?v={video_id}"
        logger.info(f"[ARCHIVE] Extracting audio from: {video_id}")

        try:
            # Download to temp file
            with tempfile.NamedTemporaryFile(suffix='.m4a', delete=False) as temp_audio:
                temp_path = temp_audio.name

            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                # More flexible format: try m4a, then any audio, then best overall
                'format': 'bestaudio[ext=m4a]/bestaudio/best',
                'outtmpl': temp_path,
                'postprocessors': [],  # No post-processing, we'll use ffmpeg
                # Use browser cookies for authenticated content (private/unlisted)
                'cookiesfrombrowser': ('chrome',),
            }

            # Download audio
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])

            # Convert to WAV using ffmpeg
            ffmpeg_cmd = [
                'ffmpeg', '-y', '-i', temp_path,
                '-f', 'wav',
                '-ac', '1',  # Mono
                '-ar', str(self.config.sample_rate_hz),  # 16kHz for Whisper
                str(cache_path)
            ]

            subprocess.run(ffmpeg_cmd, capture_output=True, check=True)
            logger.info(f"[ARCHIVE] Audio extracted and cached: {video_id}")

            # Clean up temp file
            Path(temp_path).unlink(missing_ok=True)

            # Load and return
            return self._load_wav(cache_path)

        except Exception as e:
            logger.error(f"[ARCHIVE] Failed to extract audio from {video_id}: {e}")
            return None

    def _load_wav(self, path) -> Optional[np.ndarray]:
        """Load WAV file as float32 numpy array."""
        try:
            import wave
            with wave.open(str(path), 'rb') as wav:
                frames = wav.readframes(wav.getnframes())
                audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32767.0
                return audio
        except Exception as e:
            logger.error(f"[ARCHIVE] Failed to load WAV: {e}")
            return None

    def stream_video_chunks(
        self,
        video_id: str,
        chunk_duration_sec: float = 30.0
    ) -> Generator[AudioChunk, None, None]:
        """Stream audio chunks from a video for STT processing.

        Args:
            video_id: YouTube video ID
            chunk_duration_sec: Duration of each chunk (default 30s for long videos)

        Yields:
            AudioChunk objects for STT processing
        """
        audio = self.extract_audio(video_id)
        if audio is None:
            return

        chunk_samples = int(chunk_duration_sec * self.config.sample_rate_hz)
        total_samples = len(audio)
        chunk_idx = 0

        logger.info(f"[ARCHIVE] Streaming {total_samples / self.config.sample_rate_hz:.1f}s of audio in {chunk_duration_sec}s chunks")

        for start in range(0, total_samples, chunk_samples):
            end = min(start + chunk_samples, total_samples)
            chunk_audio = audio[start:end]

            # Calculate timestamp in video (milliseconds from start)
            timestamp_ms = int(start / self.config.sample_rate_hz * 1000)

            yield AudioChunk(
                audio=chunk_audio,
                sample_rate=self.config.sample_rate_hz,
                timestamp_ms=timestamp_ms,
                duration_sec=len(chunk_audio) / self.config.sample_rate_hz,
                chunk_index=chunk_idx
            )
            chunk_idx += 1

        logger.info(f"[ARCHIVE] Yielded {chunk_idx} chunks")

    def get_extraction_progress(self, channel_id: str) -> dict:
        """Get extraction progress for a channel.

        Returns:
            Dict with cached_count, total_estimated, cache_size_mb
        """
        cached_files = list(self.cache_dir.glob("*.wav"))
        total_size = sum(f.stat().st_size for f in cached_files)

        return {
            "cached_count": len(cached_files),
            "cache_size_mb": total_size / (1024 * 1024),
            "cache_dir": str(self.cache_dir)
        }


# Convenience function for archive extraction
def get_archive_extractor(
    cache_dir: Optional[str] = None,
    config: Optional[AudioStreamConfig] = None
) -> VideoArchiveExtractor:
    """Get a configured video archive extractor instance."""
    return VideoArchiveExtractor(cache_dir=cache_dir, config=config)
