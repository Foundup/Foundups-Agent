# youtube_live_audio Interface

## AudioStreamConfig
```
AudioStreamConfig(
    sample_rate_hz: int = 16000,
    channels: int = 1,
    sample_format: str = "s16le",
    chunk_bytes: int = 4096,
    ffmpeg_path: str = "ffmpeg",
    ytdlp_path: str = "yt-dlp",
)
```

## YouTubeLiveAudioSource
```
source = YouTubeLiveAudioSource(config: Optional[AudioStreamConfig] = None)
```

### resolve_stream_url
```
resolve_stream_url(input_ref: str) -> str
```
Resolve a live stream URL from a channel id, video id, or URL. The resolver
uses stream_resolver and yt-dlp when implemented.

### stream_pcm16
```
stream_pcm16(input_ref: str) -> Iterable[bytes]
```
Yield PCM16 mono audio chunks suitable for local streaming STT engines.

## Notes
- This module is platform specific and should not include STT logic.
- All outputs are raw bytes; no disk writes in MVP.
