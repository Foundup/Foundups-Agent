"""
Base Schema Interface - All visual schemas inherit from this.

WSP Compliance:
- WSP 11: Interface Protocol (abstract methods define contract)
- WSP 27: Universal DAE Architecture (sensor/actuator pattern)

Each schema must implement:
- build_ffmpeg_filter(): Generate FFmpeg filter_complex string
- get_inputs(): Additional FFmpeg inputs needed
- get_obs_scene(): OBS scene configuration (optional)
- on_activate(): Called when schema becomes active
- on_deactivate(): Called when schema becomes inactive
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum


class SchemaMode(Enum):
    """How the schema generates video output."""
    FFMPEG = "ffmpeg"      # Pure FFmpeg filter (headless)
    OBS = "obs"            # OBS scene control
    HYBRID = "hybrid"      # FFmpeg + OBS overlays


@dataclass
class SchemaConfig:
    """Base configuration for all schemas."""
    enabled: bool = True
    duration_seconds: int = 3600  # How long before rotation
    weight: float = 1.0           # Selection weight for random rotation
    mode: SchemaMode = SchemaMode.FFMPEG
    settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FFmpegInput:
    """Additional FFmpeg input specification."""
    path: str
    options: List[str] = field(default_factory=list)  # e.g., ["-stream_loop", "-1"]
    label: str = ""  # e.g., "video", "overlay"


@dataclass
class OBSSceneConfig:
    """OBS scene configuration for schema."""
    scene_name: str
    sources: List[str] = field(default_factory=list)
    transitions: Dict[str, Any] = field(default_factory=dict)


class BaseSchema(ABC):
    """
    Abstract base class for all visual output schemas.

    Each schema encapsulates:
    1. FFmpeg filter generation (for headless streaming)
    2. OBS scene configuration (for OBS-based streaming)
    3. Lifecycle hooks (activate/deactivate)
    4. Schema-specific settings
    """

    # Schema metadata (override in subclass)
    NAME: str = "base"
    DISPLAY_NAME: str = "Base Schema"
    DESCRIPTION: str = "Abstract base schema"
    MODE: SchemaMode = SchemaMode.FFMPEG

    def __init__(self, config: Optional[SchemaConfig] = None):
        """Initialize schema with optional configuration."""
        self.config = config or SchemaConfig()
        self._active = False

    @property
    def is_active(self) -> bool:
        """Whether this schema is currently active."""
        return self._active

    @abstractmethod
    def build_ffmpeg_filter(self) -> str:
        """
        Build FFmpeg filter_complex string for this schema.

        Returns:
            FFmpeg filter string (e.g., "[1:v]scale=1920:1080[out]")
        """
        pass

    def get_inputs(self) -> List[FFmpegInput]:
        """
        Get additional FFmpeg inputs needed by this schema.

        Override in subclass if schema needs extra inputs
        (e.g., overlay images, SRT files).

        Returns:
            List of FFmpegInput specifications
        """
        return []

    def get_obs_scene(self) -> Optional[OBSSceneConfig]:
        """
        Get OBS scene configuration for this schema.

        Override in subclass if schema uses OBS.

        Returns:
            OBSSceneConfig or None if FFmpeg-only
        """
        return None

    def on_activate(self) -> None:
        """
        Called when this schema becomes active.

        Override in subclass for setup logic.
        """
        self._active = True

    def on_deactivate(self) -> None:
        """
        Called when this schema becomes inactive.

        Override in subclass for cleanup logic.
        """
        self._active = False

    def get_settings(self) -> Dict[str, Any]:
        """Get current schema settings."""
        return self.config.settings.copy()

    def update_settings(self, **kwargs) -> None:
        """Update schema settings."""
        self.config.settings.update(kwargs)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize schema state for telemetry."""
        return {
            "name": self.NAME,
            "display_name": self.DISPLAY_NAME,
            "mode": self.MODE.value,
            "active": self._active,
            "settings": self.config.settings,
        }


class SchemaError(Exception):
    """Base exception for schema errors."""
    pass


class SchemaNotFoundError(SchemaError):
    """Raised when requested schema doesn't exist."""
    pass


class SchemaConfigError(SchemaError):
    """Raised when schema configuration is invalid."""
    pass
