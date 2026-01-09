# youtube_live_audio Interface

## AudioStreamConfig
```python
AudioStreamConfig(
    sample_rate_hz: int = 16000,
    channels: int = 1,
    sample_format: str = "s16le",
    chunk_duration_sec: float = 5.0,
    overlap_sec: float = 0.5,
    ffmpeg_path: str = "ffmpeg",  # Optional fallback
    ytdlp_path: str = "yt-dlp",   # Optional fallback
)
```

## AudioChunk
```python
AudioChunk(
    audio: np.ndarray,      # float32 audio data, shape (samples,)
    sample_rate: int,       # Sample rate (16000)
    timestamp_ms: int,      # Unix timestamp when captured
    duration_sec: float,    # Chunk duration
    chunk_index: int,       # Sequential index
)
```

## SystemAudioCapture
```python
capture = SystemAudioCapture(config: Optional[AudioStreamConfig] = None)
```

### capture_chunk
```python
capture_chunk(duration_sec: Optional[float] = None) -> Optional[AudioChunk]
```
Capture a single audio chunk from system audio.

### stream_chunks
```python
stream_chunks(max_chunks: Optional[int] = None) -> Generator[AudioChunk, None, None]
```
Continuously stream audio chunks for real-time STT.

### test_capture
```python
test_capture(duration_sec: float = 3.0) -> bool
```
Test audio capture with a short recording. Returns True if audio level detected.

## YouTubeLiveAudioSource
```python
source = YouTubeLiveAudioSource(config: Optional[AudioStreamConfig] = None)
```

### resolve_stream_url
```python
resolve_stream_url(input_ref: str) -> str
```
Resolve a live stream URL from a channel id, video id, or URL.
For loopback mode, just returns the URL for browser navigation.

### stream_pcm16
```python
stream_pcm16(input_ref: str) -> Iterable[bytes]
```
Yield PCM16 mono audio chunks (legacy interface).

### stream_audio_chunks
```python
stream_audio_chunks(max_chunks: Optional[int] = None) -> Generator[AudioChunk, None, None]
```
Stream AudioChunk objects for direct STT processing. **Preferred interface.**

### capture_single
```python
capture_single(duration_sec: float = 5.0) -> Optional[AudioChunk]
```
Capture a single audio chunk for testing/one-shot STT.

### test_audio
```python
test_audio(duration_sec: float = 3.0) -> bool
```
Test audio capture.

## Convenience Function
```python
get_audio_source(config: Optional[AudioStreamConfig] = None) -> YouTubeLiveAudioSource
```

---

# PHASE 2: VIDEO ARCHIVE EXTRACTION

## VideoInfo
```python
VideoInfo(
    video_id: str,        # YouTube video ID
    title: str,           # Video title
    duration_sec: float,  # Video duration in seconds
    upload_date: str,     # Upload date (YYYYMMDD format)
    channel_id: str,      # Channel ID
    url: str,             # Full video URL
)
```

## VideoArchiveExtractor
```python
extractor = VideoArchiveExtractor(
    cache_dir: Optional[str] = None,  # Default: memory/audio_cache
    config: Optional[AudioStreamConfig] = None
)
```

### list_channel_videos
```python
list_channel_videos(
    channel_id: str,
    max_videos: int = 50
) -> Generator[VideoInfo, None, None]
```
List videos from a YouTube channel using yt-dlp (0 API quota cost).

### extract_audio
```python
extract_audio(
    video_id: str,
    use_cache: bool = True
) -> Optional[np.ndarray]
```
Extract audio from a YouTube video. Returns float32 audio array.
Uses cache to avoid re-downloading.

### stream_video_chunks
```python
stream_video_chunks(
    video_id: str,
    chunk_duration_sec: float = 30.0
) -> Generator[AudioChunk, None, None]
```
Stream audio chunks from a video for STT processing.
**AudioChunk.timestamp_ms** contains the position in the video (for deep linking).

### get_extraction_progress
```python
get_extraction_progress(channel_id: str) -> dict
```
Returns: `{cached_count, cache_size_mb, cache_dir}`

## Convenience Function
```python
get_archive_extractor(
    cache_dir: Optional[str] = None,
    config: Optional[AudioStreamConfig] = None
) -> VideoArchiveExtractor
```

---

## Notes
- **Phase 1 (Live)**: Uses WASAPI loopback to capture system audio (what speakers play)
- **Phase 2 (Archive)**: Uses yt-dlp + ffmpeg to extract audio from video archives
- No API quota cost for video listing (uses yt-dlp playlist extraction)
- Audio cached to avoid re-downloading
- AudioChunk.timestamp_ms enables deep linking: `https://youtu.be/{video_id}?t={timestamp_sec}`
- This module is platform specific and should not include STT logic
