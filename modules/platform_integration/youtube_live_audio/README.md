# youtube_live_audio

Domain: platform_integration
Status: MVP
WSP: WSP 3, WSP 11, WSP 22, WSP 49, WSP 84

## Overview

youtube_live_audio captures system audio via WASAPI loopback for downstream local STT.
Uses the Hybrid Option A architecture: browser plays YouTube LIVE, system captures what speakers play.

## Architecture

```
Browser (YouTube LIVE playing)
        |
        v
SystemAudioCapture (WASAPI loopback)
        |
        v
AudioChunk (float32 @ 16kHz mono)
        |
        v
voice_command_ingestion (STT)
```

## Key Classes

- **SystemAudioCapture**: WASAPI loopback capture via soundcard library
- **AudioChunk**: Dataclass with audio data, sample rate, timestamp, duration
- **YouTubeLiveAudioSource**: High-level interface with streaming and testing

## Responsibilities

- Capture system audio (what speakers play) via WASAPI loopback
- Stream audio chunks at 16kHz mono for Whisper compatibility
- Provide overlap between chunks for word boundary handling
- Test audio levels to verify capture is working

## Inputs and Outputs

Input:
- System audio (browser playing YouTube LIVE)
- No direct URL/video ID needed (browser handles stream)

Output:
- Generator of AudioChunk objects (float32 @ 16kHz mono)
- PCM16 byte stream (legacy interface)

## Dependencies

- soundcard>=0.4.2 (WASAPI loopback on Windows)
- numpy>=1.21.0

Optional (yt-dlp fallback mode - not currently used):
- yt-dlp>=2024.3.10
- ffmpeg (system install)

## Usage

```python
from modules.platform_integration.youtube_live_audio.src.youtube_live_audio import (
    get_audio_source
)

# Get audio source
source = get_audio_source()

# Test audio capture (play some audio first)
source.test_audio(duration_sec=3.0)

# Capture single chunk
chunk = source.capture_single(duration_sec=5.0)
print(f"Captured {len(chunk.audio)} samples")

# Stream continuous chunks
for chunk in source.stream_audio_chunks(max_chunks=10):
    print(f"Chunk {chunk.chunk_index}: {chunk.duration_sec}s")
    # Process chunk.audio with STT...
```

## Integration

- modules/communication/voice_command_ingestion consumes AudioChunk stream
- Browser already running for livechat DAE (no new browser needed)
- Works with protected/private streams (no auth issues)

## Testing

```bash
# Run end-to-end test (play audio first)
python -m modules.platform_integration.youtube_live_audio.scripts.test_live_stt
```

## Logging

Every stage emits structured log lines:
- `[AUDIO] Default speaker: {name}`
- `[AUDIO] Loopback device initialized: {name}`
- `[AUDIO] Streaming: {duration}s chunks, {overlap}s overlap`

## Roadmap

See ROADMAP.md for sprint plan.
