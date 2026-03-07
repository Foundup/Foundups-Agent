"""
antifaFM YouTube Live Broadcaster

Bridges Icecast audio stream to YouTube Live via FFmpeg.

Layers:
- Layer 1: Static image + audio (MVP)
- Layer 2.5: Zero-cost animation (Ken Burns, Color Pulse, GIF Overlay)
- Layer 3: Waveform visualization (planned)
- Layer 4: AI-generated visuals (future)
"""

from .antifafm_broadcaster import AntifaFMBroadcaster
from .ffmpeg_streamer import FFmpegStreamer, FFmpegStreamerError, StreamConfig, StreamState
from .stream_health_monitor import StreamHealthMonitor, RecoveryConfig, HealthState
from .visual_effects import (
    VisualEffectsBuilder,
    VisualEffectsConfig,
    KenBurnsConfig,
    ColorPulseConfig,
    GifOverlayConfig,
    ImageCycleConfig,
    EffectType,
    create_default_gif,
)
from .video_library import (
    VideoLibrary,
    VideoEntry,
    VideoStatus,
    handle_add_link_command,
)
from .youtube_go_live import click_go_live, verify_stream_connected, edit_stream_settings
from .youtube_ingest_resolver import (
    resolve_ingest_endpoints,
    get_ingest_url_with_fallback,
    diagnose_ingest_config,
    IngestEndpoints,
)

__all__ = [
    # Main DAE
    "AntifaFMBroadcaster",
    # FFmpeg streaming
    "FFmpegStreamer",
    "FFmpegStreamerError",
    "StreamConfig",
    "StreamState",
    # Health monitoring
    "StreamHealthMonitor",
    "RecoveryConfig",
    "HealthState",
    # Visual effects (Layer 2.5)
    "VisualEffectsBuilder",
    "VisualEffectsConfig",
    "KenBurnsConfig",
    "ColorPulseConfig",
    "GifOverlayConfig",
    "ImageCycleConfig",
    "EffectType",
    "create_default_gif",
    # Video library (Layer 2.5 - video backgrounds)
    "VideoLibrary",
    "VideoEntry",
    "VideoStatus",
    "handle_add_link_command",
    # YouTube automation
    "click_go_live",
    "verify_stream_connected",
    "edit_stream_settings",
    # Ingest URL resolution (Fix 8)
    "resolve_ingest_endpoints",
    "get_ingest_url_with_fallback",
    "diagnose_ingest_config",
    "IngestEndpoints",
]
