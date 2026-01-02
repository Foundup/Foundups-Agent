# youtube_live_audio Roadmap (Sprint Plan)

## Sprint 0 - Scaffold (COMPLETE)
- [x] Create module structure and interface stubs
- [x] Document inputs, outputs, and dependencies

## Sprint 1 - System Audio Loopback (COMPLETE - 2026-01-02)
Architecture Decision: Hybrid Option A (system audio loopback)
- [x] Implement SystemAudioCapture using soundcard WASAPI loopback
- [x] Implement AudioChunk dataclass for STT-ready data
- [x] Implement YouTubeLiveAudioSource with stream_audio_chunks()
- [x] Add test_capture() for audio level verification
- [x] Create test_live_stt.py end-to-end test script
- [x] Update requirements.txt with soundcard dependency

## Sprint 2 - Integration Testing (COMPLETE - 2026-01-02)
- [x] Verify audio capture initialization
- [x] Test with voice_command_ingestion STT
- [x] End-to-end pipeline working

## Sprint 3 - Stability Hardening (PENDING)
- [ ] Detect audio stalls and auto-reconnect
- [ ] Add configurable timeouts
- [ ] Handle device changes gracefully
- [ ] Add metrics/telemetry for audio health

## Sprint 4 - yt-dlp Fallback Mode (OPTIONAL)
Only if loopback mode proves insufficient:
- [ ] Implement stream URL resolution via yt-dlp
- [ ] Pipe ffmpeg output to PCM16 mono bytes
- [ ] Handle authentication for private streams

## Notes
- Hybrid Option A chosen over yt-dlp extraction (Occam's simplest)
- Works with protected/private streams (no auth issues)
- Reuses existing browser infrastructure from livechat DAE
