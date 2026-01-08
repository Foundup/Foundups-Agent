"""
Video Indexer - Main orchestrator for video content indexing.

WSP Compliance:
    - WSP 27: DAE Architecture (orchestration pattern)
    - WSP 72: Module Independence
    - WSP 77: Agent Coordination (Qwen/Gemma integration points)
    - WSP 91: DAEMON Observability (telemetry, feature flags)

Integration:
    - Reuses batch_transcriber.py for ASR
    - Reuses transcript_index.py for ChromaDB
    - Reuses dae_dependencies.py for browser auto-launch
    - Reuses YouTubeStudioDOM for navigation

Hardening:
    - Feature flags via indexer_config (toggle layers for testing)
    - JSONL telemetry via indexer_telemetry (DAE heartbeat)
    - Graceful degradation (continue when non-required layers fail)
    - STOP file support (memory/STOP_VIDEO_INDEXER)

Grep-able Logging:
    [VIDEO-INDEXER] General orchestration
    [INDEXER-LAYER] Layer processing events
    [INDEXER-ERROR] Error conditions
"""

import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from .indexer_config import get_indexer_config, IndexerConfig
from .indexer_telemetry import get_indexer_telemetry, IndexerTelemetry

logger = logging.getLogger(__name__)


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class IndexResult:
    """Result of indexing a single video."""
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
    """Result of searching indexed content."""
    video_id: str
    timestamp: float
    content: str
    modality: str  # "audio" | "visual" | "multimodal"
    relevance: float
    context: str


@dataclass
class LayerResult:
    """Result of processing a single layer (for graceful degradation)."""
    layer: str
    success: bool
    duration_ms: float
    data: Optional[Any]
    message: str
    skipped: bool = False


# =============================================================================
# Channel Configuration
# =============================================================================

CHANNEL_CONFIG = {
    "move2japan": {
        "channel_id": "UC-LSSlOZwpGIRIYihaz8zCw",
        "browser": "chrome",
        "port": 9222,
    },
    "undaodu": {
        "channel_id": "UC-LSSlOZwpGIRIYihaz8zCw",  # Shared profile
        "browser": "chrome",
        "port": 9222,
    },
    "foundups": {
        "channel_id": "UCSNTUXjAgpd4sgWYP0xoJgw",
        "browser": "edge",
        "port": 9223,
    },
}


# =============================================================================
# Main Orchestrator
# =============================================================================

class VideoIndexer:
    """
    Main orchestrator for video content indexing.

    Coordinates audio, visual, and multimodal analysis pipelines.

    Example:
        >>> indexer = VideoIndexer(channel="move2japan")
        >>> result = indexer.index_video(video_id="abc123")
        >>> results = indexer.search("012 talks about Japan visa")
    """

    def __init__(
        self,
        channel: str,
        chroma_path: Optional[str] = None,
        artifact_path: Optional[str] = None,
        auto_launch: bool = True,
        config: Optional[IndexerConfig] = None,
    ):
        """
        Initialize indexer for specific channel.

        Args:
            channel: Channel name ("move2japan", "undaodu", "foundups")
            chroma_path: Path to ChromaDB (default: holo_index/chroma_store)
            artifact_path: Path for JSON artifacts (default: video_index/)
            auto_launch: Auto-launch browser if not running
            config: IndexerConfig (optional, will load singleton if not provided)
        """
        if channel not in CHANNEL_CONFIG:
            raise ValueError(f"Unknown channel: {channel}. Valid: {list(CHANNEL_CONFIG.keys())}")

        self.channel = channel
        self.channel_config = CHANNEL_CONFIG[channel]
        self.auto_launch = auto_launch

        # Hardening: Feature flags and telemetry (WSP 91)
        self.config = config or get_indexer_config()
        self.telemetry = get_indexer_telemetry()

        # Paths (may be overridden by config)
        self.chroma_path = Path(chroma_path) if chroma_path else Path("holo_index/chroma_store")
        self.artifact_path = Path(artifact_path) if artifact_path else self.config.artifact_path

        # Lazy-loaded components
        self._audio_analyzer = None
        self._visual_analyzer = None
        self._multimodal_aligner = None
        self._clip_generator = None
        self._store = None

        # Progress callbacks
        self.on_progress = None
        self.on_video_complete = None
        self.on_error = None

        # Layer results (for graceful degradation tracking)
        self._layer_results: Dict[str, LayerResult] = {}

        logger.info(f"[VIDEO-INDEXER] Initialized for channel: {channel}")
        logger.info(f"[VIDEO-INDEXER] Enabled layers: {self.config.get_enabled_layers()}")

    def _ensure_browser(self) -> bool:
        """Ensure browser is running with remote debugging."""
        if not self.auto_launch:
            return True

        try:
            from modules.infrastructure.dependency_launcher.src.dae_dependencies import (
                is_port_open,
                launch_chrome,
                launch_edge,
            )

            port = self.channel_config["port"]
            if is_port_open(port):
                logger.info(f"[VIDEO-INDEXER] Browser already running on port {port}")
                return True

            browser = self.channel_config["browser"]
            logger.info(f"[VIDEO-INDEXER] Auto-launching {browser}...")

            if browser == "edge":
                success, msg = launch_edge()
            else:
                success, msg = launch_chrome()

            if success:
                logger.info(f"[VIDEO-INDEXER] Browser launched: {msg}")
            else:
                logger.error(f"[VIDEO-INDEXER] Failed to launch browser: {msg}")

            return success

        except ImportError:
            logger.warning("[VIDEO-INDEXER] dae_dependencies not available")
            return False

    # =========================================================================
    # Layer Processing with Graceful Degradation
    # =========================================================================

    def _process_layer(
        self,
        layer_name: str,
        video_id: str,
        processor_func: Callable,
        *args,
        **kwargs,
    ) -> LayerResult:
        """
        Process a layer with hardening: flags, telemetry, graceful degradation.

        Args:
            layer_name: Layer name (audio, visual, multimodal, clips)
            video_id: Video being processed
            processor_func: Function to execute for this layer
            *args, **kwargs: Arguments to pass to processor_func

        Returns:
            LayerResult with success status and data

        Raises:
            Exception: Only if layer is required and fails
        """
        # Check if layer is enabled
        if not self.config.should_process_layer(layer_name):
            reason = "Disabled in config"
            self.telemetry.layer_skipped(layer_name, video_id, reason)
            logger.info(f"[INDEXER-LAYER] Skipping {layer_name}: {reason}")
            return LayerResult(
                layer=layer_name,
                success=True,
                duration_ms=0,
                data=None,
                message=reason,
                skipped=True,
            )

        # Check STOP file
        if self.config.stop_active:
            reason = "STOP file active"
            self.telemetry.layer_skipped(layer_name, video_id, reason)
            logger.warning(f"[INDEXER-LAYER] {layer_name} halted: {reason}")
            return LayerResult(
                layer=layer_name,
                success=False,
                duration_ms=0,
                data=None,
                message=reason,
                skipped=True,
            )

        # Check dry run mode
        if self.config.dry_run:
            reason = "Dry run mode"
            self.telemetry.layer_skipped(layer_name, video_id, reason)
            logger.info(f"[INDEXER-LAYER] {layer_name} skipped: {reason}")
            return LayerResult(
                layer=layer_name,
                success=True,
                duration_ms=0,
                data=None,
                message=reason,
                skipped=True,
            )

        # Get layer config for required flag
        layer_config = getattr(self.config, layer_name, None)
        is_required = layer_config.required if layer_config else False

        # Execute layer with timing and telemetry
        self.telemetry.layer_started(layer_name, video_id)
        start_time = time.perf_counter()

        try:
            result_data = processor_func(*args, **kwargs)
            duration_ms = (time.perf_counter() - start_time) * 1000

            self.telemetry.layer_completed(layer_name, video_id, duration_ms)
            logger.info(f"[INDEXER-LAYER] {layer_name} completed in {duration_ms:.1f}ms")

            layer_result = LayerResult(
                layer=layer_name,
                success=True,
                duration_ms=duration_ms,
                data=result_data,
                message="Success",
            )

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            error_msg = f"{type(e).__name__}: {str(e)}"

            self.telemetry.layer_failed(layer_name, video_id, e)
            logger.error(f"[INDEXER-ERROR] {layer_name} failed: {error_msg}")

            # Graceful degradation: only raise if required
            if is_required:
                logger.error(f"[INDEXER-ERROR] Required layer {layer_name} failed - aborting")
                raise

            logger.warning(f"[INDEXER-LAYER] Non-required layer {layer_name} failed - continuing")
            layer_result = LayerResult(
                layer=layer_name,
                success=False,
                duration_ms=duration_ms,
                data=None,
                message=error_msg,
            )

        # Store result for tracking
        self._layer_results[layer_name] = layer_result
        return layer_result

    def index_video(
        self,
        video_id: str,
        force_reindex: bool = False,
    ) -> IndexResult:
        """
        Index single video across all modalities with hardening.

        Layer Processing Order:
            1. audio (REQUIRED) - Transcription via batch_transcriber
            2. visual (optional) - Keyframe extraction
            3. multimodal (optional) - Audio/visual alignment
            4. clips (optional) - Clip candidate generation

        Graceful Degradation:
            - Required layers (audio) will abort on failure
            - Optional layers will log warning and continue

        Args:
            video_id: YouTube video ID
            force_reindex: Re-process even if exists

        Returns:
            IndexResult with indexing status
        """
        # Check master switch
        if not self.config.is_enabled:
            reason = "Master switch disabled" if not self.config.enabled else "STOP file active"
            logger.warning(f"[VIDEO-INDEXER] Indexing disabled: {reason}")
            return IndexResult(
                video_id=video_id,
                channel=self.channel,
                title="",
                duration=0,
                indexed_at=datetime.now(),
                audio_segments=0,
                visual_frames=0,
                clip_candidates=0,
                success=False,
                error=reason,
            )

        logger.info(f"[VIDEO-INDEXER] Indexing video: {video_id}")
        self.telemetry.video_started(video_id, self.channel)
        start_time = time.perf_counter()

        # Check if already indexed
        if not force_reindex and self._is_indexed(video_id):
            logger.info(f"[VIDEO-INDEXER] Video {video_id} already indexed")
            return IndexResult(
                video_id=video_id,
                channel=self.channel,
                title="(cached)",
                duration=0,
                indexed_at=datetime.now(),
                audio_segments=0,
                visual_frames=0,
                clip_candidates=0,
                success=True,
                error="Already indexed (use force_reindex=True to re-process)",
            )

        # Clear layer results for new video
        self._layer_results.clear()

        try:
            # Phase 1: Audio analysis (REQUIRED)
            audio_result = self._process_layer(
                "audio",
                video_id,
                self._process_audio,
                video_id,
            )

            # Phase 2: Visual analysis (optional)
            visual_result = self._process_layer(
                "visual",
                video_id,
                self._process_visual,
                video_id,
            )

            # Phase 3: Multimodal alignment (optional)
            multimodal_result = self._process_layer(
                "multimodal",
                video_id,
                self._process_multimodal,
                video_id,
                audio_result.data,
                visual_result.data,
            )

            # Phase 4: Clip generation (optional)
            clips_result = self._process_layer(
                "clips",
                video_id,
                self._process_clips,
                video_id,
                multimodal_result.data,
            )

            # Calculate totals
            duration_ms = (time.perf_counter() - start_time) * 1000
            audio_segments = len(audio_result.data or []) if audio_result.success else 0

            # Visual data is a dict with keyframes list
            visual_data = visual_result.data or {}
            visual_frames = len(visual_data.get("keyframes", [])) if visual_result.success else 0

            # Clips data is a dict with candidates list
            clips_data = clips_result.data or {}
            clip_candidates = clips_data.get("total_candidates", 0) if clips_result.success else 0

            self.telemetry.video_completed(video_id, duration_ms)

            return IndexResult(
                video_id=video_id,
                channel=self.channel,
                title="(indexed)",
                duration=duration_ms / 1000,
                indexed_at=datetime.now(),
                audio_segments=audio_segments,
                visual_frames=visual_frames,
                clip_candidates=clip_candidates,
                success=True,
            )

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            error_msg = f"{type(e).__name__}: {str(e)}"
            self.telemetry.video_failed(video_id, e)
            logger.error(f"[INDEXER-ERROR] Video {video_id} failed: {error_msg}")

            return IndexResult(
                video_id=video_id,
                channel=self.channel,
                title="",
                duration=duration_ms / 1000,
                indexed_at=datetime.now(),
                audio_segments=0,
                visual_frames=0,
                clip_candidates=0,
                success=False,
                error=error_msg,
            )

    # =========================================================================
    # Layer Processors
    # =========================================================================

    def _get_audio_analyzer(self):
        """Get or create audio analyzer (lazy load)."""
        if self._audio_analyzer is None:
            from .audio_analyzer import AudioAnalyzer
            self._audio_analyzer = AudioAnalyzer(
                whisper_model=os.getenv("VIDEO_INDEXER_WHISPER_MODEL", "base"),
                enable_diarization=False,  # Disabled until pyannote integration
            )
        return self._audio_analyzer

    def _get_visual_analyzer(self):
        """Get or create visual analyzer (lazy load)."""
        if self._visual_analyzer is None:
            from .visual_analyzer import VisualAnalyzer
            self._visual_analyzer = VisualAnalyzer(
                frame_interval=float(os.getenv("VIDEO_INDEXER_FRAME_INTERVAL", "1.0")),
                enable_face_detection=os.getenv("VIDEO_INDEXER_FACE_DETECTION", "true").lower() == "true",
            )
        return self._visual_analyzer

    def _get_multimodal_aligner(self):
        """Get or create multimodal aligner (lazy load)."""
        if self._multimodal_aligner is None:
            from .multimodal_aligner import MultimodalAligner
            self._multimodal_aligner = MultimodalAligner(
                alignment_tolerance=float(os.getenv("VIDEO_INDEXER_ALIGNMENT_TOLERANCE", "0.5")),
                min_moment_duration=float(os.getenv("VIDEO_INDEXER_MIN_MOMENT_DURATION", "3.0")),
                min_highlight_score=float(os.getenv("VIDEO_INDEXER_MIN_HIGHLIGHT_SCORE", "0.65")),
            )
        return self._multimodal_aligner

    def _get_clip_generator(self):
        """Get or create clip generator (lazy load)."""
        if self._clip_generator is None:
            from .clip_generator import ClipGenerator
            self._clip_generator = ClipGenerator(
                min_duration=float(os.getenv("VIDEO_INDEXER_CLIP_MIN_DURATION", "15.0")),
                max_duration=float(os.getenv("VIDEO_INDEXER_CLIP_MAX_DURATION", "60.0")),
                min_virality=float(os.getenv("VIDEO_INDEXER_CLIP_MIN_VIRALITY", "0.6")),
            )
        return self._clip_generator

    def _process_audio(self, video_id: str) -> List[Dict]:
        """
        Process audio layer - transcription via AudioAnalyzer.

        Uses get_batch_transcriber() from voice_command_ingestion (WSP 84).

        Args:
            video_id: YouTube video ID

        Returns:
            List of transcript segment dicts
        """
        logger.info(f"[INDEXER-AUDIO] Processing audio for {video_id}")

        analyzer = self._get_audio_analyzer()
        result = analyzer.transcribe_video(video_id)

        # Convert to list of dicts for pipeline
        segments = analyzer.to_segments_list(result)

        logger.info(f"[INDEXER-AUDIO] Got {len(segments)} segments")
        return segments

    def _process_visual(self, video_id: str) -> Dict:
        """
        Process visual layer - keyframe extraction and shot detection.

        Uses VisualAnalyzer with yt-dlp download (WSP 84).

        Args:
            video_id: YouTube video ID

        Returns:
            Dict with visual analysis results (keyframes, shots, metadata)
        """
        logger.info(f"[INDEXER-VISUAL] Processing visual for {video_id}")

        analyzer = self._get_visual_analyzer()
        result = analyzer.analyze_video(video_id)

        # Convert to dict for pipeline
        visual_data = result.to_dict()

        logger.info(
            f"[INDEXER-VISUAL] Got {len(result.keyframes)} keyframes, "
            f"{len(result.shots)} shots, {result.face_count} faces"
        )
        return visual_data

    def _process_multimodal(
        self,
        video_id: str,
        audio_data: Optional[List],
        visual_data: Optional[Dict],
    ) -> Dict:
        """
        Process multimodal layer - audio/visual alignment.

        Uses MultimodalAligner to sync audio segments with visual shots.

        Args:
            video_id: YouTube video ID
            audio_data: List of audio segment dicts
            visual_data: Dict with visual analysis results

        Returns:
            Dict with aligned moments and highlights
        """
        logger.info(f"[INDEXER-MULTIMODAL] Aligning for {video_id}")

        aligner = self._get_multimodal_aligner()
        result = aligner.align_video(audio_data or [], visual_data or {})

        # Convert to dict for pipeline
        multimodal_data = result.to_dict()

        logger.info(
            f"[INDEXER-MULTIMODAL] Got {len(result.moments)} moments, "
            f"{result.highlight_count} highlights"
        )
        return multimodal_data

    def _process_clips(
        self,
        video_id: str,
        multimodal_data: Optional[Dict],
    ) -> Dict:
        """
        Process clips layer - generate clip candidates.

        Uses ClipGenerator to extract short-form content candidates.

        Args:
            video_id: YouTube video ID
            multimodal_data: Dict with moments and highlights from multimodal layer

        Returns:
            Dict with clip candidates and metrics
        """
        logger.info(f"[INDEXER-CLIPS] Generating clips for {video_id}")

        generator = self._get_clip_generator()
        result = generator.generate_clips(multimodal_data or {}, video_id)

        # Convert to dict for pipeline
        clips_data = result.to_dict()

        logger.info(
            f"[INDEXER-CLIPS] Generated {result.total_candidates} clips, "
            f"avg virality={result.avg_virality:.2f}"
        )
        return clips_data

    def index_channel(
        self,
        max_videos: int = 50,
        filter_type: str = "shorts",
        since_date: Optional[str] = None,
    ) -> List[IndexResult]:
        """
        Index multiple videos from channel.

        Args:
            max_videos: Limit videos to process
            filter_type: "shorts" | "videos" | "all"
            since_date: Only videos after date (YYYY-MM-DD)

        Returns:
            List of IndexResult for each video
        """
        logger.info(f"[VIDEO-INDEXER] Indexing channel: {self.channel} ({filter_type})")

        # Ensure browser is running
        if not self._ensure_browser():
            return [
                IndexResult(
                    video_id="",
                    channel=self.channel,
                    title="",
                    duration=0,
                    indexed_at=datetime.now(),
                    audio_segments=0,
                    visual_frames=0,
                    clip_candidates=0,
                    success=False,
                    error="Browser not available",
                )
            ]

        # TODO: Implement channel video listing via YouTubeStudioDOM
        # TODO: Iterate and index each video

        return []

    def search(
        self,
        query: str,
        modality: str = "all",
        top_k: int = 10,
        min_relevance: float = 0.7,
    ) -> List[SearchResult]:
        """
        Search indexed content across modalities.

        Args:
            query: Natural language query
            modality: "audio" | "visual" | "all"
            top_k: Number of results
            min_relevance: Minimum similarity score

        Returns:
            List of SearchResult sorted by relevance
        """
        logger.info(f"[VIDEO-INDEXER] Searching: '{query}' (modality={modality})")

        # TODO: Implement ChromaDB search across collections
        # - video_transcripts (audio)
        # - video_visual (visual)
        # - video_moments (multimodal)

        return []

    def _is_indexed(self, video_id: str) -> bool:
        """Check if video is already indexed."""
        artifact_file = self.artifact_path / f"{video_id}.json"
        return artifact_file.exists()

    # =========================================================================
    # Health & Status (WSP 91)
    # =========================================================================

    def get_health(self) -> Dict[str, Any]:
        """
        Get health status for DAE monitoring.

        Returns:
            Dict with health metrics for AI Overseer integration
        """
        return {
            "channel": self.channel,
            "enabled": self.config.is_enabled,
            "stop_active": self.config.stop_active,
            "dry_run": self.config.dry_run,
            "enabled_layers": self.config.get_enabled_layers(),
            "telemetry": self.telemetry.get_metrics(),
            "layer_health": self.telemetry.get_layer_health(),
            "layer_results": {
                k: {"success": v.success, "duration_ms": v.duration_ms, "skipped": v.skipped}
                for k, v in self._layer_results.items()
            },
            "gates": self.config.gate_snapshot(),
        }

    def get_status_line(self) -> str:
        """
        Get one-line status for logging.

        Returns:
            Grep-able status line
        """
        metrics = self.telemetry.get_metrics()
        layers = self.config.get_enabled_layers()
        return (
            f"[VIDEO-INDEXER] channel={self.channel} | "
            f"status={metrics['health_status']} | "
            f"videos={metrics['videos_indexed']} | "
            f"errors={metrics['errors_detected']} | "
            f"layers={','.join(layers)}"
        )


# =============================================================================
# Quick Test
# =============================================================================

if __name__ == "__main__":
    import os
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("Video Indexer Hardening Test")
    print("=" * 60)

    # Test with default config (all layers enabled)
    print("\n--- Test 1: Default Config (all layers ON) ---")
    indexer = VideoIndexer(channel="move2japan", auto_launch=False)
    print(f"Channel: {indexer.channel}")
    print(f"Enabled: {indexer.config.is_enabled}")
    print(f"Enabled layers: {indexer.config.get_enabled_layers()}")
    print(f"Status: {indexer.get_status_line()}")

    # Test dry run mode
    print("\n--- Test 2: Dry Run Mode ---")
    os.environ["VIDEO_INDEXER_DRY_RUN"] = "true"
    from .indexer_config import reload_config
    reload_config()
    indexer2 = VideoIndexer(channel="move2japan", auto_launch=False)
    result = indexer2.index_video("test_dry_run")
    print(f"Dry run result: success={result.success}, error={result.error}")
    os.environ.pop("VIDEO_INDEXER_DRY_RUN", None)

    # Test layer toggling
    print("\n--- Test 3: Layer Toggling (visual OFF) ---")
    os.environ["VIDEO_INDEXER_VISUAL_ENABLED"] = "false"
    reload_config()
    indexer3 = VideoIndexer(channel="foundups", auto_launch=False)
    print(f"Enabled layers: {indexer3.config.get_enabled_layers()}")
    os.environ.pop("VIDEO_INDEXER_VISUAL_ENABLED", None)

    # Test health output
    print("\n--- Test 4: Health Output ---")
    health = indexer.get_health()
    import json
    print(json.dumps(health, indent=2, default=str))

    print("\n--- All hardening tests complete ---")
