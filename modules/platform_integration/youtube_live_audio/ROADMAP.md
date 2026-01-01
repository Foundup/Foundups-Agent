# youtube_live_audio Roadmap

## Phase 0 - Scaffold (complete)
- Create module structure and interface stubs
- Document inputs, outputs, and dependencies

## Phase 1 - Stream resolution and audio pipe
- Resolve live stream URL using stream_resolver + yt-dlp
- Pipe ffmpeg output to PCM16 mono bytes
- Emit structured log lines for each stage

## Phase 2 - Isolated tests
- Mock yt-dlp output and verify ffmpeg args generation
- Feed a local MP4 and assert PCM output frames

## Phase 3 - Stability hardening
- Detect stalls and restart ffmpeg
- Add timeouts and backoff for stream resolution
