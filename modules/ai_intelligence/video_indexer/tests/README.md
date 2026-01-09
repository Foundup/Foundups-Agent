# Video Indexer Test Suite

**WSP Compliance**: WSP 5 (Test Coverage), WSP 6 (Test Audit), WSP 49 (Module Structure)

## Purpose

This test suite validates the video_indexer module's ability to index 012's YouTube channels for knowledge extraction. Tests verify the complete pipeline from Selenium navigation to multimodal indexing.

## Test Categories

### 1. Unit Tests (Offline)
Test individual components without external dependencies:
- `test_indexer_config.py` - Feature flag parsing
- `test_indexer_telemetry.py` - Heartbeat and health calculation
- `test_clip_generator.py` - Virality scoring algorithms
- `test_multimodal_aligner.py` - Moment alignment logic

### 2. Integration Tests (Requires Browser)
Test full pipeline with Selenium automation:
- `test_integration_oldest_video.py` - Navigate to oldest UnDaoDu video and index

### 3. Component Tests
Test individual analyzers with mocked inputs:
- `test_audio_analyzer.py` - ASR integration with batch_transcriber
- `test_visual_analyzer.py` - OpenCV frame extraction
- `test_video_index_store.py` - JSON artifact storage

## Key Integration Test: UnDaoDu Oldest Video

**File**: `test_integration_oldest_video.py`

**Purpose**: Validate end-to-end indexing by processing UnDaoDu's oldest video (2009).

**What 012 Should See**:
1. Chrome browser opens (port 9222)
2. Navigates to YouTube Studio for UnDaoDu channel
3. Video list sorted oldest-first
4. First video (2009) selected and indexed
5. Console output showing indexing progress

**Why UnDaoDu 2009 Video**:
- UnDaoDu is 012's consciousness exploration channel
- 2009 video is earliest content - foundational to 012's YouTube presence
- Tests full pipeline with real historical content
- Validates that ancient videos still process correctly

## Running Tests

### Prerequisites
```bash
# Ensure Chrome is running with remote debugging
"C:\Program Files\Google\Chrome\Application\chrome.exe" ^
    --remote-debugging-port=9222 ^
    --user-data-dir="%LOCALAPPDATA%\Google\Chrome\User Data"
```

### Run All Tests
```bash
cd O:\Foundups-Agent
python -m pytest modules/ai_intelligence/video_indexer/tests/ -v
```

### Run Integration Test Only
```bash
python -m pytest modules/ai_intelligence/video_indexer/tests/test_integration_oldest_video.py -v -s
```

### Run Offline Tests Only
```bash
python -m pytest modules/ai_intelligence/video_indexer/tests/ -v -m "not integration"
```

## Test Fixtures

### Channel Configuration
```python
CHANNELS = {
    "undaodu": {
        "id": "UCfHM9Fw9HD-NwiS0seD_oIA",
        "name": "UnDaoDu",
        "chrome_port": 9222,
    },
    "move2japan": {
        "id": "UC-LSSlOZwpGIRIYihaz8zCw",
        "name": "Move2Japan",
        "chrome_port": 9222,
    },
    "foundups": {
        "id": "UCSNTUXjAgpd4sgWYP0xoJgw",
        "name": "FoundUps",
        "chrome_port": 9223,  # Edge browser
    },
}
```

### Environment Variables
```bash
# Enable/disable layers for testing
VIDEO_INDEXER_AUDIO_ENABLED=true
VIDEO_INDEXER_VISUAL_ENABLED=true
VIDEO_INDEXER_MULTIMODAL_ENABLED=true
VIDEO_INDEXER_CLIPS_ENABLED=true
VIDEO_INDEXER_DRY_RUN=false
VIDEO_INDEXER_VERBOSE=true
```

## Test Artifacts

Tests produce artifacts in `memory/video_index/`:
```
memory/video_index/
├── undaodu_oldest_2009.json     # Index data for 2009 video
├── video_cache/                  # Downloaded video files
│   └── {video_id}.mp4
└── test_results/                 # Test run artifacts
    └── integration_run_{timestamp}.json
```

## Dependencies

```python
# Core
pytest>=7.0.0
pytest-asyncio>=0.21.0

# Selenium (reuse from foundups_selenium)
selenium>=4.10.0

# Module dependencies
from modules.communication.voice_command_ingestion.scripts.index_channel import (
    list_videos_via_selenium, CHANNELS
)
from modules.ai_intelligence.video_indexer.src.video_indexer import VideoIndexer
```

## WSP Compliance

| WSP | Description | Implementation |
|-----|-------------|----------------|
| WSP 5 | Test Coverage | All 4 phases tested |
| WSP 6 | Test Audit | This README documents test strategy |
| WSP 49 | Module Structure | tests/ directory per spec |
| WSP 50 | Pre-Action Verification | Reuses existing Selenium patterns |
| WSP 84 | Code Reuse | Uses index_channel.py patterns |

## Test Evolution Log

| Date | Test Added | Purpose |
|------|------------|---------|
| 2026-01-09 | test_integration_oldest_video.py | Initial E2E test for oldest UnDaoDu video |

---

*Tests are 012's memory verification - ensuring 0102 correctly indexes and recalls 012's teachings.*
