"""YouTube Live audio source for local STT pipelines."""

from dataclasses import dataclass
from typing import Iterable, Optional


@dataclass(frozen=True)
class AudioStreamConfig:
    """Configuration for PCM16 audio output."""

    sample_rate_hz: int = 16000
    channels: int = 1
    sample_format: str = "s16le"
    chunk_bytes: int = 4096
    ffmpeg_path: str = "ffmpeg"
    ytdlp_path: str = "yt-dlp"


class YouTubeLiveAudioSource:
    """Resolve a YouTube live source and stream PCM16 audio."""

    def __init__(self, config: Optional[AudioStreamConfig] = None) -> None:
        self.config = config or AudioStreamConfig()

    def resolve_stream_url(self, input_ref: str) -> str:
        """Resolve a live stream URL from a channel id, video id, or URL."""
        raise NotImplementedError("Stream resolution is not implemented yet.")

    def stream_pcm16(self, input_ref: str) -> Iterable[bytes]:
        """Yield PCM16 mono audio chunks for downstream STT."""
        raise NotImplementedError("PCM16 streaming is not implemented yet.")
