# Video Indexer Roadmap

**WSP Compliance**: WSP 27 (DAE Architecture), WSP 77 (Agent Coordination)

## Phase 1: Audio Foundation (Current)

**Status**: Existing infrastructure in voice_command_ingestion

### Capabilities
- [x] ASR via Whisper (`batch_transcriber.py`)
- [x] ChromaDB storage (`transcript_index.py`)
- [x] JSON artifacts (`video_index/`)
- [x] Browser auto-launch (`dae_dependencies.py`)
- [x] YouTube Studio navigation (`YouTubeStudioDOM`)

### Integration Required
- [ ] Create `audio_analyzer.py` wrapper around batch_transcriber
- [ ] Add speaker diarization (pyannote.audio)
- [ ] Add quote extraction (NLP pipeline)
- [ ] Add topic identification (keyword extraction)

---

## Phase 2: Visual Analysis

**Status**: COMPLETE (2026-01-09)

### Capabilities Added
- [x] Keyframe extraction (OpenCV + frame sampling)
- [x] Shot boundary detection (histogram diff)
- [x] Face detection (OpenCV Haar cascade)
- [ ] Object detection (YOLO or similar) - Future
- [ ] OCR for on-screen text - Future

### Implementation
- `visual_analyzer.py`: Complete visual pipeline
- `VisualResult` dataclass with keyframes, shots, metadata
- yt-dlp video download (reuses youtube_live_audio pattern, WSP 84)
- Video caching at `memory/video_cache/`

### ChromaDB Collections
```python
# New collection for visual embeddings
video_visual = chroma_client.get_or_create_collection(
    name="video_visual",
    metadata={"hnsw:space": "cosine"}
)
```

### Dependencies
```
opencv-python>=4.8.0
ffmpeg-python>=0.2.0
# Optional for face detection:
# face_recognition>=1.3.0
```

---

## Phase 3: Multimodal Alignment

**Status**: Not started

### Capabilities to Add
- [ ] Audio-visual moment alignment
- [ ] Highlight detection (engagement scoring)
- [ ] Cross-modal search (query audio, find visual)
- [ ] Moment embedding (combined representation)

### Algorithm
```python
def align_moments(audio_segments, visual_frames):
    """
    For each audio segment:
    1. Find visual frames within timestamp range
    2. Compute combined embedding
    3. Score engagement (audio energy + visual motion)
    4. Return aligned moments
    """
```

---

## Phase 4: Clip Generation

**Status**: Not started

### Capabilities to Add
- [ ] Clip candidate extraction (15-60s segments)
- [ ] Hook detection (strong opening moments)
- [ ] Virality scoring (engagement + novelty)
- [ ] Title/description generation (LLM integration)

### Output Format
```json
{
  "clip_id": "abc123_clip_001",
  "source_video": "abc123",
  "start_time": 45.5,
  "end_time": 75.2,
  "duration": 29.7,
  "hook": "Here's what nobody tells you about...",
  "title_suggestion": "The REAL reason Japan visas are hard",
  "virality_score": 0.82,
  "moments": [
    {"time": 48.0, "type": "quote", "content": "..."},
    {"time": 52.0, "type": "visual", "content": "face closeup"}
  ]
}
```

---

## Phase 5: DAE Integration

**Status**: Future

### Capabilities to Add
- [ ] Background indexing daemon
- [ ] Auto-index new uploads
- [ ] Re-index on demand
- [ ] Health monitoring

### DAE Architecture (WSP 27)
```python
class VideoIndexerDAE:
    """
    Phase -1: Check dependencies (browsers, models)
    Phase 0: Initialize indexer
    Phase 1: Poll for new videos
    Phase 2: Index video (audio + visual + multimodal)
    Phase 3: Generate clip candidates
    Phase 4: Store artifacts
    Phase 5: Report metrics
    """
```

---

## Dependencies Summary

### Phase 1 (Audio)
```
whisper>=1.0.0           # Already installed
chromadb>=0.4.0          # Already installed
pyannote.audio>=3.0.0    # NEW: diarization
spacy>=3.7.0             # NEW: NLP
```

### Phase 2 (Visual)
```
opencv-python>=4.8.0     # Frame extraction
ffmpeg-python>=0.2.0     # Video processing
```

### Phase 3-4 (Multimodal + Clips)
```
sentence-transformers    # Already installed (embeddings)
```

### Phase 5 (DAE)
```
# No new deps - uses existing DAE infrastructure
```

---

## Success Metrics

| Phase | Metric | Target |
|-------|--------|--------|
| 1 | Transcripts indexed | 100% of videos |
| 2 | Visual frames extracted | 1 frame/second |
| 3 | Moments aligned | 90% audio-visual sync |
| 4 | Clip candidates | 3-5 per video |
| 5 | Auto-index latency | < 1 hour after upload |

---

## Integration Points

### With HoloIndex
```python
# Video content becomes searchable alongside code
holo search "012 explains Japan visa requirements"
# Returns: video timestamps + code examples
```

### With 0102 Digital Twin
```python
# 0102 can recall 012's teachings
"What does 012 say about starting a business in Japan?"
# Returns: Video clips + transcript quotes
```

### With YouTube Shorts Scheduler
```python
# Clip candidates feed into scheduling pipeline
scheduler.add_clips(indexer.get_clip_candidates())
```
