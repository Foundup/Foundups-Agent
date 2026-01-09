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

---

# PHASE 2: VIDEO ARCHIVE TRANSCRIPTION (Digital Twin Foundation)

**Objective**: Transcribe ALL 012's YouTube videos for searchable digital twin knowledge base

## Sprint 5 - Video Archive Audio Extraction (COMPLETE - 2026-01-07)
Architecture Decision: yt-dlp for VOD (video-on-demand) audio extraction
- [x] Implement VideoArchiveExtractor class
- [x] yt-dlp audio download (m4a → wav conversion via ffmpeg)
- [x] Batch processing: list_channel_videos() using yt-dlp (0 API quota)
- [x] Cache extracted audio to avoid re-download (memory/audio_cache/)
- [x] stream_video_chunks() yields AudioChunks with timestamps for STT

## Sprint 6 - Batch Transcription Pipeline (COMPLETE - 2026-01-07)
Reuses faster-whisper from voice_command_ingestion
- [x] Implement BatchTranscriber with progress tracking (in voice_command_ingestion)
- [x] Chunk long videos (>10min) for memory efficiency (30s chunks default)
- [x] Store transcripts as JSONL with timestamps and video metadata
- [x] Output format: `{video_id, title, timestamp_sec, text, confidence, url}`
- [x] Deep link URLs for "What did 012 say?" queries

Note: BatchTranscriber implemented in voice_command_ingestion (STT domain)

## Sprint 7 - Transcript Index (HoloIndex Pattern) (COMPLETE - 2026-01-07)
Enable semantic search across all video content
- [x] Create VideoTranscriptIndex class (ChromaDB + embeddings)
- [x] Index: video_id, timestamp, text, embedding, metadata
- [x] Search API: `search(query) -> [SearchResult with score]`
- [x] MCP-compatible: `search_012_transcripts(query)`

Note: Implemented in voice_command_ingestion/src/transcript_index.py

## Sprint 8 - Digital Twin Knowledge Integration (COMPLETE - 2026-01-07)
The digital twin can query 012's video content
- [x] Enable "What did 012 say about X?" queries → search_012_transcripts()
- [x] Deep links to exact video moments in results
- [ ] Pattern extraction: recurring topics, teaching moments (FUTURE)
- [ ] Cross-reference with code commits (temporal correlation) (FUTURE)
- [ ] Connect to PQN learning pipeline (FUTURE)

## Notes
- Hybrid Option A chosen over yt-dlp extraction (Occam's simplest) for LIVE
- Video archive uses yt-dlp (necessary for VOD download)
- Works with protected/private streams (no auth issues)
- Reuses existing browser infrastructure from livechat DAE
- Digital twin objective: searchable knowledge from all 012 videos
