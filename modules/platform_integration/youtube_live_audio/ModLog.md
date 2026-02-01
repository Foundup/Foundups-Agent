# ModLog - youtube_live_audio

### 2026-01-19 - Fix: yt-dlp Cookie Database Error
**WSP Protocol**: WSP 22, WSP 50 (Occam's razor)
**Agent**: 0102

#### Problem
`ERROR: Could not copy Chrome cookie database` when Chrome is running.
yt-dlp was hardcoded to use `cookiesfrombrowser: ('chrome',)` which fails
because Chrome locks its cookie database while running.

#### Fix
Made browser cookies optional via env var `YT_DLP_COOKIES_BROWSER`:
- Default: No cookies (most public videos work fine)
- Set to `chrome`, `firefox`, `edge`, or `safari` to enable
- Browser must be closed when using cookies

#### Occam's Razor
Most videos are public and don't need authentication.
Only enable cookies for private/unlisted content when needed.

---

### 2026-01-07 - Sprint 6: Batch Transcription Pipeline (COMPLETE)
**WSP Protocol**: WSP 22, WSP 84
**Phase**: Implementation
**Agent**: 0102

#### Changes
- Sprint 6 implemented in voice_command_ingestion module (STT domain)
- BatchTranscriber connects VideoArchiveExtractor with faster-whisper
- Transcripts stored in `memory/transcripts/` as JSONL
- Deep link URLs enable "What did 012 say about X?" queries
- Updated ROADMAP.md to mark Sprint 6 complete

#### Cross-Reference
Implementation in: `modules/communication/voice_command_ingestion/src/voice_command_ingestion.py`
- BatchTranscriber class
- TranscriptSegment dataclass
- transcribe_channel() uses VideoArchiveExtractor from this module

#### Architecture (Full Pipeline)
```
YouTube Video → yt-dlp (audio) → VideoArchiveExtractor → AudioChunk
                                                              ↓
                              BatchTranscriber ← faster-whisper (STT)
                                                              ↓
                                        TranscriptSegment with timestamp
                                                              ↓
                                          memory/transcripts/*.jsonl
```

#### WSP Compliance
- WSP 84: Batch transcription reuses faster-whisper from voice_command_ingestion
- WSP 22: ModLog documented

---

### 2026-01-07 - Sprint 5: Video Archive Audio Extraction (COMPLETE)
**WSP Protocol**: WSP 22, WSP 50, WSP 84
**Phase**: Implementation
**Agent**: 0102

#### Changes
- Implemented `VideoArchiveExtractor` class (264 lines added)
- Implemented `VideoInfo` dataclass for video metadata
- `list_channel_videos()`: Lists channel videos using yt-dlp (0 API quota cost)
- `extract_audio()`: Downloads and extracts audio to WAV, with caching
- `stream_video_chunks()`: Yields AudioChunks with timestamps for STT
- `get_extraction_progress()`: Reports cache status
- Updated INTERFACE.md with Phase 2 documentation
- Total module size: 549 lines (within WSP 87 limits)

#### Architecture
```
YouTube Video → yt-dlp (audio) → ffmpeg (WAV) → AudioChunk → STT
                                     ↓
                           memory/audio_cache/ (cached)
```

#### Key Feature: Timestamp Deep Linking
AudioChunk.timestamp_ms contains position in video, enabling:
```
"What did 012 say about WSP?" → https://youtu.be/abc123?t=45
```

#### WSP Compliance
- WSP 84: Reuses yt-dlp pattern from acoustic_lab
- WSP 50: Searched existing code before implementation
- WSP 22: ModLog documented

#### Dependencies
- yt-dlp (pip install yt-dlp)
- ffmpeg (system PATH)

---

### 2026-01-07 - Phase 2 Roadmap: Video Archive Transcription for Digital Twin
**WSP Protocol**: WSP 22, WSP 50
**Phase**: Planning
**Agent**: 0102

#### Changes
- Added Phase 2 roadmap (Sprints 5-8) for video archive transcription
- Sprint 5: Video Archive Audio Extraction (yt-dlp for VOD)
- Sprint 6: Batch Transcription Pipeline (reuses faster-whisper)
- Sprint 7: Transcript Index (HoloIndex pattern for semantic search)
- Sprint 8: Digital Twin Knowledge Integration

#### Objective
Enable digital twin to learn from ALL 012's YouTube videos:
- Transcribe entire video archive (not just live streams)
- Index transcripts for semantic search ("What did 012 say about X?")
- Cross-reference with git commits for temporal correlation
- Pattern extraction for teaching moments and decisions

#### Architecture
```
YouTube Video → yt-dlp (audio) → faster-whisper (STT) → Transcript Index → Digital Twin
```

#### Impact
- Extends module scope from live-only to live + archive
- Enables searchable knowledge base from video content
- Foundation for 012 digital twin personality modeling

#### WSP Compliance
- WSP 22: Roadmap documented
- WSP 50: Pre-action verification (searched existing infra first)

---

### 2026-01-02 - Sprint 1: System Audio Loopback Implementation
**WSP Protocol**: WSP 3, WSP 11, WSP 22, WSP 84
**Phase**: Implementation
**Agent**: 0102

#### Changes
- Implemented SystemAudioCapture class using soundcard WASAPI loopback
- Implemented AudioChunk dataclass for STT-ready audio data
- Implemented YouTubeLiveAudioSource with dual-mode support (loopback + yt-dlp fallback)
- Added stream_audio_chunks() generator for continuous streaming
- Added test_capture() for audio level verification
- Created test_live_stt.py end-to-end test script
- Updated requirements.txt with soundcard dependency

#### Architecture Decision
- **Hybrid Option A**: System audio loopback (Occam's simplest)
- Browser plays YouTube LIVE (already running for livechat DAE)
- WASAPI captures system audio (what speakers play)
- Works with protected/private streams (no auth issues)
- No yt-dlp authentication battles

#### Impact
- Sprint 1 complete: Audio capture operational
- Ready for integration with voice_command_ingestion STT

#### WSP Compliance
- WSP 84: Reuses existing browser infrastructure
- WSP 3: platform_integration domain (YouTube-specific)
- WSP 11: Public interface defined

### 2026-01-01 - Sprint roadmap and integration notes
**WSP Protocol**: WSP 22, WSP 84
**Phase**: Enhancement
**Agent**: Codex

#### Changes
- Converted roadmap to sprint plan
- Documented downstream reuse of LiveChat command routing

#### Impact
- Aligns voice pipeline docs with WSP sprint expectations

#### WSP Compliance
- WSP 84 duplication avoidance

### 2026-01-01 - Initial scaffolding for YouTube live audio source
**WSP Protocol**: WSP 3, WSP 22, WSP 49
**Phase**: Initial Creation
**Agent**: Codex

#### Changes
- Added module structure, documentation, and interface stubs
- Added placeholder tests and memory documentation
- Added requirements list for yt-dlp dependency

#### Impact
- Establishes the platform_integration block for live audio capture

#### WSP Compliance
- WSP 3 domain placement
- WSP 49 module structure
