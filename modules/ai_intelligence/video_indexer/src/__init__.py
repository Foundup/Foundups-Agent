"""
Video Indexer Module - Comprehensive video content indexing for 012's YouTube channels.

WSP Compliance:
    - WSP 49: Module Structure
    - WSP 3: Domain Organization (ai_intelligence)
    - WSP 72: Module Independence
    - WSP 91: DAEMON Observability (telemetry, feature flags)

Components:
    - VideoIndexer: Main orchestrator with hardening
    - AudioAnalyzer: ASR, diarization, NLP
    - VisualAnalyzer: Shot detection, faces, objects
    - MultimodalAligner: Cross-modal moments
    - ClipGenerator: Short-form extraction
    - VideoIndexStore: JSON artifact storage
    - IndexerConfig: Feature flags and automation gates
    - IndexerTelemetry: JSONL heartbeat and breadcrumb integration
"""

from .video_indexer import VideoIndexer, IndexResult, SearchResult, LayerResult
from .audio_analyzer import AudioAnalyzer
from .visual_analyzer import VisualAnalyzer, VisualResult
from .multimodal_aligner import MultimodalAligner, MultimodalResult
from .clip_generator import ClipGenerator, ClipGeneratorResult
from .video_index_store import VideoIndexStore, IndexData
from .indexer_config import IndexerConfig, get_indexer_config, reload_config
from .indexer_telemetry import IndexerTelemetry, get_indexer_telemetry

__all__ = [
    # Main orchestrator
    "VideoIndexer",
    "IndexResult",
    "SearchResult",
    "LayerResult",
    # Analyzers
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
]

__version__ = "0.6.0"  # Test Suite & Audit complete
