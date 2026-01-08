# Video Indexer Interface

**WSP Compliance**: WSP 11 (Interface Protocol), WSP 49 (Module Structure)

## Public API

### VideoIndexer (Main Orchestrator)

```python
from modules.ai_intelligence.video_indexer.src.video_indexer import VideoIndexer

class VideoIndexer:
    """
    Main orchestrator for video content indexing.

    Coordinates audio, visual, and multimodal analysis pipelines.
    """

    def __init__(
        self,
        channel: str,                    # "move2japan" | "undaodu" | "foundups"
        chroma_path: str = None,         # ChromaDB path (default: holo_index/chroma_store)
        artifact_path: str = None,       # JSON output path (default: video_index/)
        auto_launch: bool = True         # Auto-launch browser if not running
    ):
        """Initialize indexer for specific channel."""

    def index_video(
        self,
        video_id: str,                   # YouTube video ID
        include_visual: bool = True,     # Process visual frames
        include_clips: bool = True,      # Generate clip candidates
        force_reindex: bool = False      # Re-process even if exists
    ) -> IndexResult:
        """Index single video across all modalities."""

    def index_channel(
        self,
        max_videos: int = 50,            # Limit videos to process
        filter_type: str = "shorts",     # "shorts" | "videos" | "all"
        since_date: str = None           # Only videos after date
    ) -> List[IndexResult]:
        """Index multiple videos from channel."""

    def search(
        self,
        query: str,                      # Natural language query
        modality: str = "all",           # "audio" | "visual" | "all"
        top_k: int = 10,                 # Number of results
        min_relevance: float = 0.7       # Minimum similarity score
    ) -> List[SearchResult]:
        """Search indexed content across modalities."""
```

### AudioAnalyzer

```python
from modules.ai_intelligence.video_indexer.src.audio_analyzer import AudioAnalyzer

class AudioAnalyzer:
    """
    Audio content analysis: ASR, diarization, NLP extraction.

    Extends batch_transcriber.py with speaker identification.
    """

    def __init__(
        self,
        whisper_model: str = "base",     # Whisper model size
        enable_diarization: bool = True  # Speaker identification
    ):
        """Initialize audio analyzer."""

    def transcribe(
        self,
        audio_path: str                  # Path to audio file
    ) -> TranscriptResult:
        """Transcribe audio with timestamps."""

    def extract_quotes(
        self,
        transcript: TranscriptResult,
        min_length: int = 10,            # Minimum quote words
        max_length: int = 50             # Maximum quote words
    ) -> List[Quote]:
        """Extract notable quotes from transcript."""

    def identify_topics(
        self,
        transcript: TranscriptResult
    ) -> List[Topic]:
        """Extract topics using NLP."""
```

### VisualAnalyzer

```python
from modules.ai_intelligence.video_indexer.src.visual_analyzer import VisualAnalyzer

class VisualAnalyzer:
    """
    Visual content analysis: shots, faces, objects.
    """

    def __init__(
        self,
        frame_interval: float = 1.0,     # Seconds between frame samples
        enable_face_detection: bool = True
    ):
        """Initialize visual analyzer."""

    def extract_keyframes(
        self,
        video_path: str
    ) -> List[Keyframe]:
        """Extract representative frames from video."""

    def detect_shots(
        self,
        video_path: str,
        threshold: float = 0.3           # Scene change threshold
    ) -> List[Shot]:
        """Detect shot boundaries."""

    def analyze_frame(
        self,
        frame: np.ndarray
    ) -> FrameAnalysis:
        """Analyze single frame for faces, objects, text."""
```

### MultimodalAligner

```python
from modules.ai_intelligence.video_indexer.src.multimodal_aligner import MultimodalAligner

class MultimodalAligner:
    """
    Cross-modal alignment: sync audio moments with visual content.
    """

    def align_moments(
        self,
        audio_analysis: AudioAnalysis,
        visual_analysis: VisualAnalysis
    ) -> List[Moment]:
        """Align audio and visual moments."""

    def detect_highlights(
        self,
        moments: List[Moment],
        min_score: float = 0.8           # Highlight threshold
    ) -> List[Highlight]:
        """Detect high-engagement moments."""
```

### ClipGenerator

```python
from modules.ai_intelligence.video_indexer.src.clip_generator import ClipGenerator

class ClipGenerator:
    """
    Generate clip candidates for short-form content.
    """

    def generate_candidates(
        self,
        moments: List[Moment],
        min_duration: float = 15.0,      # Minimum clip seconds
        max_duration: float = 60.0       # Maximum clip seconds
    ) -> List[ClipCandidate]:
        """Generate clip candidates from moments."""

    def score_virality(
        self,
        clip: ClipCandidate
    ) -> float:
        """Score clip for viral potential (0-1)."""
```

### VideoIndexStore

```python
from modules.ai_intelligence.video_indexer.src.video_index_store import VideoIndexStore

class VideoIndexStore:
    """
    JSON artifact storage for video index data.
    """

    def __init__(
        self,
        base_path: str = "video_index"   # Output directory
    ):
        """Initialize store."""

    def save_index(
        self,
        video_id: str,
        index_data: IndexData
    ) -> str:
        """Save index to JSON, return path."""

    def load_index(
        self,
        video_id: str
    ) -> Optional[IndexData]:
        """Load existing index if available."""

    def list_indexed(
        self,
        channel: str = None              # Filter by channel
    ) -> List[str]:
        """List all indexed video IDs."""
```

## Data Classes

```python
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class IndexResult:
    video_id: str
    channel: str
    title: str
    duration: float
    indexed_at: datetime
    audio_segments: int
    visual_frames: int
    clip_candidates: int
    success: bool
    error: Optional[str] = None

@dataclass
class SearchResult:
    video_id: str
    timestamp: float
    content: str
    modality: str          # "audio" | "visual" | "multimodal"
    relevance: float
    context: str           # Surrounding content

@dataclass
class Quote:
    text: str
    start_time: float
    end_time: float
    speaker: Optional[str]
    sentiment: float       # -1 to 1

@dataclass
class Moment:
    start_time: float
    end_time: float
    audio_content: str
    visual_description: str
    engagement_score: float

@dataclass
class ClipCandidate:
    start_time: float
    end_time: float
    title_suggestion: str
    hook: str              # Opening line
    virality_score: float
    moments: List[Moment]
```

## Error Handling

```python
class VideoIndexerError(Exception):
    """Base exception for video indexer."""

class VideoNotFoundError(VideoIndexerError):
    """Video ID not found on YouTube."""

class TranscriptionError(VideoIndexerError):
    """Audio transcription failed."""

class BrowserConnectionError(VideoIndexerError):
    """Could not connect to browser (Chrome/Edge)."""
```

## Event Hooks

```python
# Progress callbacks for long-running operations
indexer.on_progress = lambda pct, msg: print(f"{pct}%: {msg}")
indexer.on_video_complete = lambda result: log_result(result)
indexer.on_error = lambda error: handle_error(error)
```
