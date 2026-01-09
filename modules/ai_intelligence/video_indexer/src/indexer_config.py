"""
Video Indexer Configuration & Automation Gates

WSP Compliance:
    - WSP 91: DAEMON Observability (feature flags, health monitoring)
    - WSP 72: Module Independence (self-contained config)

Feature Flags:
    VIDEO_INDEXER_ENABLED       - Master switch (default: true)
    VIDEO_INDEXER_AUDIO_ENABLED - Audio analysis layer (default: true)
    VIDEO_INDEXER_VISUAL_ENABLED - Visual analysis layer (default: true)
    VIDEO_INDEXER_MULTIMODAL_ENABLED - Multimodal alignment (default: true)
    VIDEO_INDEXER_CLIPS_ENABLED - Clip generation (default: true)
    VIDEO_INDEXER_DRY_RUN       - Log actions without executing (default: false)
    VIDEO_INDEXER_VERBOSE       - Verbose debug logging (default: false)

STOP File:
    Create `memory/STOP_VIDEO_INDEXER` to immediately halt processing.
    No code edit required - file presence triggers stop.
"""

import os
import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


# =============================================================================
# Environment Helper
# =============================================================================

def _env_truthy(name: str, default: str = "false") -> bool:
    """
    Check if environment variable is truthy.

    Truthy values: "1", "true", "yes", "y", "on"
    """
    try:
        value = os.getenv(name, default).strip().lower()
        return value in ("1", "true", "yes", "y", "on")
    except Exception:
        return default.lower() in ("1", "true", "yes", "y", "on")


def _env_int(name: str, default: int) -> int:
    """Get integer from environment variable."""
    try:
        return int(os.getenv(name, str(default)))
    except (ValueError, TypeError):
        return default


def _env_float(name: str, default: float) -> float:
    """Get float from environment variable."""
    try:
        return float(os.getenv(name, str(default)))
    except (ValueError, TypeError):
        return default


# =============================================================================
# Health Status
# =============================================================================

class HealthStatus(Enum):
    """Health status levels for telemetry."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    STOPPED = "stopped"


# =============================================================================
# Layer Configuration
# =============================================================================

@dataclass
class LayerConfig:
    """Configuration for a processing layer."""
    name: str
    enabled: bool
    required: bool  # If true, failure = critical
    timeout_seconds: float
    retry_count: int

    def __str__(self):
        status = "ON" if self.enabled else "OFF"
        req = " (required)" if self.required else ""
        return f"{self.name}: {status}{req}"


# =============================================================================
# Main Configuration Class
# =============================================================================

class IndexerConfig:
    """
    Video Indexer configuration with feature flags and automation gates.

    Usage:
        config = IndexerConfig()

        if config.is_enabled:
            if config.audio.enabled:
                # Process audio
            if config.visual.enabled:
                # Process visual

    STOP File:
        Create `memory/STOP_VIDEO_INDEXER` to halt processing immediately.
    """

    STOP_FILE = Path("memory/STOP_VIDEO_INDEXER")

    def __init__(self):
        """Initialize configuration from environment."""
        self._load_config()
        self._log_config()

    def _load_config(self):
        """Load all configuration from environment."""
        # Master switch
        self.enabled = _env_truthy("VIDEO_INDEXER_ENABLED", "true")
        self.dry_run = _env_truthy("VIDEO_INDEXER_DRY_RUN", "false")
        self.verbose = _env_truthy("VIDEO_INDEXER_VERBOSE", "false")

        # Layer configurations
        self.audio = LayerConfig(
            name="audio",
            enabled=_env_truthy("VIDEO_INDEXER_AUDIO_ENABLED", "true"),
            required=True,  # Audio is core functionality
            timeout_seconds=_env_float("VIDEO_INDEXER_AUDIO_TIMEOUT", 300.0),
            retry_count=_env_int("VIDEO_INDEXER_AUDIO_RETRIES", 3),
        )

        self.visual = LayerConfig(
            name="visual",
            enabled=_env_truthy("VIDEO_INDEXER_VISUAL_ENABLED", "true"),
            required=False,  # Visual can fail gracefully
            timeout_seconds=_env_float("VIDEO_INDEXER_VISUAL_TIMEOUT", 600.0),
            retry_count=_env_int("VIDEO_INDEXER_VISUAL_RETRIES", 2),
        )

        self.multimodal = LayerConfig(
            name="multimodal",
            enabled=_env_truthy("VIDEO_INDEXER_MULTIMODAL_ENABLED", "true"),
            required=False,  # Depends on audio + visual
            timeout_seconds=_env_float("VIDEO_INDEXER_MULTIMODAL_TIMEOUT", 120.0),
            retry_count=_env_int("VIDEO_INDEXER_MULTIMODAL_RETRIES", 1),
        )

        self.clips = LayerConfig(
            name="clips",
            enabled=_env_truthy("VIDEO_INDEXER_CLIPS_ENABLED", "true"),
            required=False,  # Optional feature
            timeout_seconds=_env_float("VIDEO_INDEXER_CLIPS_TIMEOUT", 60.0),
            retry_count=_env_int("VIDEO_INDEXER_CLIPS_RETRIES", 1),
        )

        # Performance limits
        self.max_concurrent_videos = _env_int("VIDEO_INDEXER_MAX_CONCURRENT", 2)
        self.heartbeat_interval = _env_int("VIDEO_INDEXER_HEARTBEAT_INTERVAL", 30)
        self.memory_limit_mb = _env_int("VIDEO_INDEXER_MEMORY_LIMIT_MB", 1024)
        self.cpu_limit_percent = _env_int("VIDEO_INDEXER_CPU_LIMIT", 80)

        # Paths
        self.telemetry_path = Path(os.getenv(
            "VIDEO_INDEXER_TELEMETRY_PATH",
            "logs/video_indexer_heartbeat.jsonl"
        ))
        self.artifact_path = Path(os.getenv(
            "VIDEO_INDEXER_ARTIFACT_PATH",
            "video_index"
        ))

    def _log_config(self):
        """Log configuration on startup."""
        if self.verbose:
            logger.info("[CONFIG] Video Indexer Configuration:")
            logger.info(f"  Master: {'ENABLED' if self.enabled else 'DISABLED'}")
            logger.info(f"  Dry Run: {self.dry_run}")
            logger.info(f"  Audio: {self.audio}")
            logger.info(f"  Visual: {self.visual}")
            logger.info(f"  Multimodal: {self.multimodal}")
            logger.info(f"  Clips: {self.clips}")

    @property
    def is_enabled(self) -> bool:
        """Check if indexer should run (master switch + no STOP file)."""
        if self.stop_active:
            return False
        return self.enabled

    @property
    def stop_active(self) -> bool:
        """Check if STOP file exists."""
        return self.STOP_FILE.exists()

    def create_stop_file(self, reason: str = "Manual stop"):
        """Create STOP file to halt processing."""
        self.STOP_FILE.parent.mkdir(parents=True, exist_ok=True)
        self.STOP_FILE.write_text(f"Stopped at: {__import__('datetime').datetime.now()}\nReason: {reason}")
        logger.warning(f"[STOP] Created STOP file: {reason}")

    def remove_stop_file(self):
        """Remove STOP file to resume processing."""
        if self.STOP_FILE.exists():
            self.STOP_FILE.unlink()
            logger.info("[STOP] Removed STOP file - processing can resume")

    def gate_snapshot(self) -> Dict[str, Any]:
        """
        Get current state of all automation gates.
        Include in telemetry for debugging.
        """
        return {
            "stop_active": self.stop_active,
            "master_enabled": self.enabled,
            "dry_run": self.dry_run,
            "verbose": self.verbose,
            "layers": {
                "audio": self.audio.enabled,
                "visual": self.visual.enabled,
                "multimodal": self.multimodal.enabled,
                "clips": self.clips.enabled,
            },
            "limits": {
                "max_concurrent": self.max_concurrent_videos,
                "memory_mb": self.memory_limit_mb,
                "cpu_percent": self.cpu_limit_percent,
            }
        }

    def get_enabled_layers(self) -> list:
        """Get list of enabled layer names."""
        layers = []
        if self.audio.enabled:
            layers.append("audio")
        if self.visual.enabled:
            layers.append("visual")
        if self.multimodal.enabled:
            layers.append("multimodal")
        if self.clips.enabled:
            layers.append("clips")
        return layers

    def should_process_layer(self, layer_name: str) -> bool:
        """Check if a specific layer should be processed."""
        if not self.is_enabled:
            return False

        layer_map = {
            "audio": self.audio,
            "visual": self.visual,
            "multimodal": self.multimodal,
            "clips": self.clips,
        }

        layer = layer_map.get(layer_name)
        if layer is None:
            logger.warning(f"[CONFIG] Unknown layer: {layer_name}")
            return False

        return layer.enabled


# =============================================================================
# Singleton Instance
# =============================================================================

_config_instance: Optional[IndexerConfig] = None


def get_indexer_config() -> IndexerConfig:
    """Get singleton configuration instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = IndexerConfig()
    return _config_instance


def reload_config():
    """Force reload configuration from environment."""
    global _config_instance
    _config_instance = None
    return get_indexer_config()


# =============================================================================
# Quick Test
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("Video Indexer Configuration Test")
    print("=" * 60)

    # Force verbose for testing
    os.environ["VIDEO_INDEXER_VERBOSE"] = "true"

    config = get_indexer_config()

    print(f"\nMaster Enabled: {config.is_enabled}")
    print(f"STOP Active: {config.stop_active}")
    print(f"Dry Run: {config.dry_run}")
    print(f"\nEnabled Layers: {config.get_enabled_layers()}")
    print(f"\nGate Snapshot:")

    import json
    print(json.dumps(config.gate_snapshot(), indent=2))

    # Test STOP file
    print("\n--- Testing STOP file ---")
    config.create_stop_file("Test stop")
    print(f"After creating STOP: is_enabled={config.is_enabled}")
    config.remove_stop_file()
    print(f"After removing STOP: is_enabled={config.is_enabled}")
