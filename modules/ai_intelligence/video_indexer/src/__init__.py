"""
Video Indexer Module - Comprehensive video content indexing for 012's YouTube channels.

WSP Compliance:
    - WSP 49: Module Structure
    - WSP 3: Domain Organization (ai_intelligence)
    - WSP 72: Module Independence
    - WSP 91: DAEMON Observability (telemetry, feature flags)

Components:
    - VideoIndexer: Main orchestrator with hardening
    - GeminiVideoAnalyzer: Direct YouTube analysis via Gemini AI (Tier 1)
    - AudioAnalyzer: ASR, diarization, NLP (Tier 2 fallback)
    - VisualAnalyzer: Shot detection, faces, objects
    - MultimodalAligner: Cross-modal moments
    - ClipGenerator: Short-form extraction
    - VideoIndexStore: JSON artifact storage
    - IndexerConfig: Feature flags and automation gates
    - IndexerTelemetry: JSONL heartbeat and breadcrumb integration

Primary Use Case:
    Live YouTube stream indexing for 012's consciousness streams.
    Uses Gemini 2.0 Flash for direct video analysis without downloading.
"""

from .video_indexer import VideoIndexer, IndexResult, SearchResult, LayerResult
from .gemini_video_analyzer import (
    GeminiVideoAnalyzer,
    GeminiAnalysisResult,
    VideoSegment,
    save_analysis_result,
)
from .audio_analyzer import AudioAnalyzer
from .visual_analyzer import VisualAnalyzer, VisualResult
from .multimodal_aligner import MultimodalAligner, MultimodalResult
from .clip_generator import ClipGenerator, ClipGeneratorResult
from .video_index_store import VideoIndexStore, IndexData
from .indexer_config import IndexerConfig, get_indexer_config, reload_config
from .indexer_telemetry import IndexerTelemetry, get_indexer_telemetry
from .gemma_segment_classifier import (
    GemmaSegmentClassifier,
    SegmentClassification,
    get_segment_classifier,
)

__all__ = [
    # Main orchestrator
    "VideoIndexer",
    "IndexResult",
    "SearchResult",
    "LayerResult",
    # Gemini Analyzer (Tier 1 - PRIMARY)
    "GeminiVideoAnalyzer",
    "GeminiAnalysisResult",
    "VideoSegment",
    "save_analysis_result",
    # Local Analyzers (Tier 2 fallback)
    "AudioAnalyzer",
    "VisualAnalyzer",
    "VisualResult",
    "MultimodalAligner",
    "MultimodalResult",
    "ClipGenerator",
    "ClipGeneratorResult",
    # Storage
    "VideoIndexStore",
    "IndexData",
    # Hardening (WSP 91)
    "IndexerConfig",
    "get_indexer_config",
    "reload_config",
    "IndexerTelemetry",
    "get_indexer_telemetry",
    # Gemma Segment Classifier (Phase 9)
    "GemmaSegmentClassifier",
    "SegmentClassification",
    "get_segment_classifier",
]

__version__ = "0.10.0"  # Gemma Segment Classifier for training data quality
