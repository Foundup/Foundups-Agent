"""
Visual Scheme Manager for antifaFM YouTube Live Broadcaster

Manages rotation between different visual output modes:
- VIDEO_LOOP: Current working mode (MP4/WebM backgrounds)
- WAVEFORM: Layer 3 - Audio visualization with showwaves/showfreqs
- KARAOKE: Layer 2.5D - STT lyrics overlay with beat-synced animation
- NEWS_TICKER: Layer 2.5C - Scrolling headlines
- ENTANGLED: Bell state visualization (0102)
- LIVECAM: Multi-camera grid (Layer 7)
- SPECTRUM: Frequency spectrum visualization

WSP Compliance:
- WSP 27: Universal DAE Architecture (Phase 2: Agentic execution)
- WSP 84: Code Reuse (visual effects patterns)
- WSP 91: Observability (scheme transition logging)

Pattern: Occam's Layer-by-Layer - validate each mode before rotation

MODULAR ARCHITECTURE (2026-03-06):
Schemas are now self-contained modules in schemas/ directory.
See: modules/platform_integration/antifafm_broadcaster/schemas/
"""

import asyncio
import logging
import os
import random
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Callable, Dict, List, Optional, Any, Tuple

# Import modular schema system
try:
    from ..schemas import get_schema_by_name, list_schemas, SchemaType
    from ..schemas.base import BaseSchema, SchemaConfig as ModularSchemaConfig
    MODULAR_SCHEMAS_AVAILABLE = True
except ImportError:
    MODULAR_SCHEMAS_AVAILABLE = False

logger = logging.getLogger(__name__)


class OutputScheme(Enum):
    """Available visual output schemes."""
    VIDEO_LOOP = "video_loop"      # MP4/WebM background loop (working)
    STATIC_IMAGE = "static_image"  # Static image with Ken Burns (Layer 2.5)
    WAVEFORM = "waveform"          # Audio waveform visualization (Layer 3)
    SPECTRUM = "spectrum"          # Frequency spectrum (Layer 3)
    KARAOKE = "karaoke"            # STT lyrics overlay (Layer 2.5D)
    NEWS_TICKER = "news_ticker"    # Scrolling headlines (Layer 2.5C)
    ENTANGLED = "entangled"        # Bell state 0102 visualization
    LIVECAM = "livecam"            # Multi-camera grid (Layer 7)


@dataclass
class SchemeConfig:
    """Configuration for a visual scheme."""
    scheme: OutputScheme
    enabled: bool = True
    duration_seconds: int = 3600  # How long to show this scheme
    weight: float = 1.0           # Relative weight for random selection
    # Scheme-specific settings (passed to filter builder)
    settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SchemeManagerConfig:
    """Configuration for the scheme manager."""
    # Rotation mode: "sequential", "random", "manual"
    rotation_mode: str = "sequential"
    # Schemes to include in rotation
    schemes: List[SchemeConfig] = field(default_factory=list)
    # Default scheme when starting
    default_scheme: OutputScheme = OutputScheme.VIDEO_LOOP
    # Whether to restart FFmpeg on scheme change (required for filter changes)
    restart_on_change: bool = True
    # Callback when scheme changes
    on_scheme_change: Optional[Callable[[OutputScheme, OutputScheme], None]] = None


class SchemeManager:
    """
    Manages visual scheme rotation for antifaFM broadcaster.

    Handles scheme selection, timing, and FFmpeg filter transitions.
    """

    def __init__(self, config: Optional[SchemeManagerConfig] = None):
        """
        Initialize scheme manager.

        Args:
            config: Manager configuration. Loads from ENV if None.
        """
        self.config = config or self._load_config_from_env()
        self.current_scheme = self.config.default_scheme
        self.scheme_start_time = time.time()
        self._running = False
        self._rotation_task = None

        logger.info(f"[SCHEME] Manager initialized, default: {self.current_scheme.value}")

    def _load_config_from_env(self) -> SchemeManagerConfig:
        """Load configuration from environment variables."""
        config = SchemeManagerConfig()

        # Rotation mode
        config.rotation_mode = os.getenv("ANTIFAFM_SCHEME_ROTATION", "sequential")

        # Default scheme
        default = os.getenv("ANTIFAFM_DEFAULT_SCHEME", "video_loop")
        for scheme in OutputScheme:
            if scheme.value == default:
                config.default_scheme = scheme
                break

        # Build scheme list from ENV
        # Format: ANTIFAFM_SCHEMES=video_loop:3600,waveform:1800,karaoke:1800
        schemes_str = os.getenv(
            "ANTIFAFM_SCHEMES",
            "video_loop:3600,waveform:1800"
        )

        for item in schemes_str.split(","):
            parts = item.strip().split(":")
            if parts:
                scheme_name = parts[0]
                duration = int(parts[1]) if len(parts) > 1 else 3600

                for scheme in OutputScheme:
                    if scheme.value == scheme_name:
                        config.schemes.append(SchemeConfig(
                            scheme=scheme,
                            duration_seconds=duration,
                            enabled=True
                        ))
                        break

        # If no schemes specified, use defaults
        if not config.schemes:
            config.schemes = [
                SchemeConfig(scheme=OutputScheme.VIDEO_LOOP, duration_seconds=3600),
                SchemeConfig(scheme=OutputScheme.WAVEFORM, duration_seconds=1800),
            ]

        return config

    def get_current_scheme(self) -> OutputScheme:
        """Get currently active scheme."""
        return self.current_scheme

    def get_scheme_config(self, scheme: OutputScheme) -> Optional[SchemeConfig]:
        """Get configuration for a specific scheme."""
        for sc in self.config.schemes:
            if sc.scheme == scheme:
                return sc
        return None

    def get_time_remaining(self) -> int:
        """Get seconds remaining in current scheme."""
        sc = self.get_scheme_config(self.current_scheme)
        if not sc:
            return 0
        elapsed = time.time() - self.scheme_start_time
        remaining = sc.duration_seconds - elapsed
        return max(0, int(remaining))

    def set_scheme(self, scheme: OutputScheme) -> bool:
        """
        Manually set the current scheme.

        Args:
            scheme: Scheme to switch to

        Returns:
            True if scheme changed
        """
        if scheme == self.current_scheme:
            return False

        old_scheme = self.current_scheme
        self.current_scheme = scheme
        self.scheme_start_time = time.time()

        logger.info(f"[SCHEME] Changed: {old_scheme.value} -> {scheme.value}")

        if self.config.on_scheme_change:
            self.config.on_scheme_change(old_scheme, scheme)

        return True

    def next_scheme(self) -> OutputScheme:
        """
        Advance to next scheme based on rotation mode.

        Returns:
            New current scheme
        """
        enabled_schemes = [sc for sc in self.config.schemes if sc.enabled]
        if not enabled_schemes:
            return self.current_scheme

        if self.config.rotation_mode == "sequential":
            # Find current index and advance
            current_idx = None
            for i, sc in enumerate(enabled_schemes):
                if sc.scheme == self.current_scheme:
                    current_idx = i
                    break

            if current_idx is None:
                next_idx = 0
            else:
                next_idx = (current_idx + 1) % len(enabled_schemes)

            new_scheme = enabled_schemes[next_idx].scheme

        elif self.config.rotation_mode == "random":
            # Weighted random selection
            weights = [sc.weight for sc in enabled_schemes]
            choices = [sc.scheme for sc in enabled_schemes]
            new_scheme = random.choices(choices, weights=weights, k=1)[0]

        else:  # manual
            return self.current_scheme

        self.set_scheme(new_scheme)
        return new_scheme

    async def start_rotation(self):
        """Start automatic scheme rotation."""
        if self._running:
            return

        self._running = True
        self._rotation_task = asyncio.create_task(self._rotation_loop())
        logger.info(f"[SCHEME] Rotation started, mode: {self.config.rotation_mode}")

    async def stop_rotation(self):
        """Stop automatic scheme rotation."""
        self._running = False
        if self._rotation_task:
            self._rotation_task.cancel()
            try:
                await self._rotation_task
            except asyncio.CancelledError:
                pass
        logger.info("[SCHEME] Rotation stopped")

    async def _rotation_loop(self):
        """Background task for scheme rotation."""
        while self._running:
            try:
                remaining = self.get_time_remaining()

                if remaining <= 0:
                    self.next_scheme()
                    remaining = self.get_time_remaining()

                # Sleep for 1 minute or remaining time, whichever is less
                sleep_time = min(60, remaining)
                await asyncio.sleep(sleep_time)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[SCHEME] Rotation error: {e}")
                await asyncio.sleep(60)

    def build_ffmpeg_filter(self) -> str:
        """
        Build FFmpeg filter_complex for current scheme.

        Returns:
            FFmpeg filter string
        """
        scheme = self.current_scheme
        sc = self.get_scheme_config(scheme)
        settings = sc.settings if sc else {}

        # Try modular schema system first (WSP 84: Code Reuse)
        if MODULAR_SCHEMAS_AVAILABLE:
            filter_str = self._build_from_modular_schema(scheme.value, settings)
            if filter_str:
                return filter_str

        # Fallback to legacy hardcoded methods
        if scheme == OutputScheme.VIDEO_LOOP:
            return self._build_video_loop_filter(settings)
        elif scheme == OutputScheme.STATIC_IMAGE:
            return self._build_static_image_filter(settings)
        elif scheme == OutputScheme.WAVEFORM:
            return self._build_waveform_filter(settings)
        elif scheme == OutputScheme.SPECTRUM:
            return self._build_spectrum_filter(settings)
        elif scheme == OutputScheme.KARAOKE:
            return self._build_karaoke_filter(settings)
        elif scheme == OutputScheme.NEWS_TICKER:
            return self._build_news_ticker_filter(settings)
        else:
            return self._build_video_loop_filter(settings)

    def _build_from_modular_schema(
        self, schema_name: str, settings: Dict[str, Any]
    ) -> Optional[str]:
        """
        Build filter using modular schema system.

        Args:
            schema_name: Name of schema (e.g., 'video_loop', 'karaoke')
            settings: Schema-specific settings

        Returns:
            FFmpeg filter string or None if schema not found
        """
        if not MODULAR_SCHEMAS_AVAILABLE:
            return None

        schema_class = get_schema_by_name(schema_name)
        if not schema_class:
            logger.debug(f"[SCHEME] No modular schema for '{schema_name}'")
            return None

        try:
            # Create schema instance with settings
            config = ModularSchemaConfig(settings=settings)
            schema_instance = schema_class(config)

            # Build filter
            filter_str = schema_instance.build_ffmpeg_filter()
            logger.debug(f"[SCHEME] Using modular schema: {schema_name}")
            return filter_str

        except Exception as e:
            logger.warning(f"[SCHEME] Modular schema error for {schema_name}: {e}")
            return None

    def get_modular_schema(self, schema_name: str) -> Optional['BaseSchema']:
        """
        Get instantiated modular schema object.

        Useful for accessing schema-specific methods like set_srt(), set_bpm().

        Args:
            schema_name: Name of schema

        Returns:
            Schema instance or None
        """
        if not MODULAR_SCHEMAS_AVAILABLE:
            return None

        schema_class = get_schema_by_name(schema_name)
        if not schema_class:
            return None

        sc = self.get_scheme_config_by_name(schema_name)
        settings = sc.settings if sc else {}
        config = ModularSchemaConfig(settings=settings)
        return schema_class(config)

    def get_scheme_config_by_name(self, name: str) -> Optional[SchemeConfig]:
        """Get configuration for a scheme by name."""
        for sc in self.config.schemes:
            if sc.scheme.value == name:
                return sc
        return None

    def _build_video_loop_filter(self, settings: Dict[str, Any]) -> str:
        """Build filter for video loop mode (current working mode)."""
        # Scale video, optional color pulse
        color_pulse = settings.get('color_pulse', True)
        filter_parts = [
            "[1:v]scale=1920:1080:force_original_aspect_ratio=decrease",
            "pad=1920:1080:(ow-iw)/2:(oh-ih)/2"
        ]
        if color_pulse:
            filter_parts.append("hue=h=sin(t*0.1)*15")
        filter_parts.append("format=yuv420p[out]")
        return ",".join(filter_parts)

    def _build_static_image_filter(self, settings: Dict[str, Any]) -> str:
        """Build filter for static image with Ken Burns effect."""
        zoom_range = settings.get('zoom_range', 0.1)
        zoom_speed = settings.get('zoom_speed', 0.05)
        fps = settings.get('fps', 30)

        zoom_expr = f"1.0+{zoom_range}*sin(on/{fps}*{zoom_speed})"
        return (
            f"[1:v]zoompan=z='{zoom_expr}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            f"d=1:s=1920x1080:fps={fps}[kb];"
            f"[kb]format=yuv420p[out]"
        )

    def _build_waveform_filter(self, settings: Dict[str, Any]) -> str:
        """Build filter for waveform visualization."""
        mode = settings.get('mode', 'cline')
        colors = settings.get('colors', '0xff0000|0xffffff')
        rate = settings.get('rate', 30)

        return (
            f"color=c=black:s=1920x1080:r={rate}[bg];"
            f"[0:a]showwaves=s=1920x540:mode={mode}:colors={colors}:rate={rate}[wave];"
            f"[bg][wave]overlay=0:270[prefmt];"
            f"[prefmt]drawtext=text='antifaFM':fontsize=36:fontcolor=white@0.7:"
            f"x=20:y=20:shadowcolor=black@0.5:shadowx=2:shadowy=2[prefinal];"
            f"[prefinal]format=yuv420p[out]"
        )

    def _build_spectrum_filter(self, settings: Dict[str, Any]) -> str:
        """Build filter for frequency spectrum visualization."""
        mode = settings.get('mode', 'bar')
        colors = settings.get('colors', '0xff0000|0x00ff00|0x0000ff')
        rate = settings.get('rate', 30)

        return (
            f"color=c=black:s=1920x1080:r={rate}[bg];"
            f"[0:a]showfreqs=s=1920x540:mode={mode}:colors={colors}:fscale=log[spec];"
            f"[bg][spec]overlay=0:270[prefmt];"
            f"[prefmt]drawtext=text='antifaFM':fontsize=36:fontcolor=white@0.7:"
            f"x=20:y=20:shadowcolor=black@0.5:shadowx=2:shadowy=2[prefinal];"
            f"[prefinal]format=yuv420p[out]"
        )

    def _build_karaoke_filter(self, settings: Dict[str, Any]) -> str:
        """Build filter for karaoke mode (requires SRT file)."""
        srt_path = settings.get('srt_path', '')
        font_size = settings.get('font_size', 48)
        bpm = settings.get('bpm', 120)

        if srt_path:
            # With SRT subtitles
            escaped_path = srt_path.replace('\\', '/').replace(':', '\\:')
            return (
                f"[1:v]scale=1920:1080,format=yuv420p[bg];"
                f"[bg]subtitles='{escaped_path}':"
                f"force_style='FontSize={font_size},PrimaryColour=&H00FFFFFF,"
                f"OutlineColour=&H00000000,Outline=2,Shadow=1,Alignment=2,MarginV=80'"
                f"[out]"
            )
        else:
            # Placeholder without subtitles
            bpm_freq = bpm / 60.0 * 6.28
            fontsize_expr = f"{font_size}+10*sin(t*{bpm_freq:.4f})"
            return (
                f"[1:v]scale=1920:1080,format=yuv420p[bg];"
                f"[bg]drawtext=text='Karaoke Mode - No SRT loaded':"
                f"fontsize='{fontsize_expr}':fontcolor=white:"
                f"x=(w-text_w)/2:y=h-100:"
                f"shadowcolor=black:shadowx=2:shadowy=2[out]"
            )

    def _build_news_ticker_filter(self, settings: Dict[str, Any]) -> str:
        """Build filter for scrolling news ticker."""
        text = settings.get('text', 'antifaFM - 24/7 Resistance Radio')
        speed = settings.get('speed', 100)
        font_size = settings.get('font_size', 36)

        return (
            f"[1:v]scale=1920:1080,format=yuv420p[bg];"
            f"[bg]drawtext=text='{text}':"
            f"fontsize={font_size}:fontcolor=white:"
            f"x=w-mod(t*{speed}\\,w+tw):y=h-50:"
            f"shadowcolor=black:shadowx=2:shadowy=2[out]"
        )

    def get_status(self) -> Dict[str, Any]:
        """Get current scheme manager status."""
        return {
            "current_scheme": self.current_scheme.value,
            "time_remaining": self.get_time_remaining(),
            "rotation_mode": self.config.rotation_mode,
            "running": self._running,
            "enabled_schemes": [
                {"scheme": sc.scheme.value, "duration": sc.duration_seconds}
                for sc in self.config.schemes if sc.enabled
            ]
        }


# =============================================================================
# FILE-BASED IPC FOR CROSS-PROCESS SCHEME SWITCHING
# Chat commands write to signal file, FFmpeg streamer watches and reacts
# =============================================================================

# Default signal file location
SCHEME_SIGNAL_FILE = Path(os.getenv(
    "ANTIFAFM_SCHEME_SIGNAL_FILE",
    str(Path(__file__).parent.parent / "data" / "scheme_signal.txt")
))


def write_scheme_signal(scheme: str) -> bool:
    """
    Write scheme signal to file for cross-process communication.

    Called by chat commands to signal the running FFmpeg streamer.

    Args:
        scheme: Scheme name (video_loop, karaoke, waveform, etc.)

    Returns:
        True if successful
    """
    try:
        # Ensure directory exists
        SCHEME_SIGNAL_FILE.parent.mkdir(parents=True, exist_ok=True)

        # Write scheme + timestamp
        with open(SCHEME_SIGNAL_FILE, 'w', encoding='utf-8') as f:
            f.write(f"{scheme}\n{time.time()}")

        logger.info(f"[SCHEME-IPC] Signal written: {scheme}")
        return True

    except Exception as e:
        logger.error(f"[SCHEME-IPC] Failed to write signal: {e}")
        return False


def read_scheme_signal() -> Optional[Tuple[str, float]]:
    """
    Read scheme signal from file.

    Called by FFmpeg streamer to check for scheme change requests.

    Returns:
        Tuple of (scheme_name, timestamp) or None if no signal
    """
    try:
        if not SCHEME_SIGNAL_FILE.exists():
            return None

        with open(SCHEME_SIGNAL_FILE, 'r', encoding='utf-8') as f:
            lines = f.read().strip().split('\n')

        if len(lines) >= 2:
            scheme = lines[0].strip()
            timestamp = float(lines[1].strip())
            return (scheme, timestamp)
        elif len(lines) == 1:
            return (lines[0].strip(), 0.0)

        return None

    except Exception as e:
        logger.debug(f"[SCHEME-IPC] Failed to read signal: {e}")
        return None


def clear_scheme_signal():
    """Clear the scheme signal file."""
    try:
        if SCHEME_SIGNAL_FILE.exists():
            SCHEME_SIGNAL_FILE.unlink()
        logger.debug("[SCHEME-IPC] Signal cleared")
    except Exception as e:
        logger.debug(f"[SCHEME-IPC] Failed to clear signal: {e}")


async def watch_scheme_signal(
    callback: Callable[[str], None],
    poll_interval: float = 2.0
) -> None:
    """
    Async watcher for scheme signal file changes.

    Call this in the FFmpeg streamer's event loop to react to scheme changes.

    Args:
        callback: Function to call with new scheme name
        poll_interval: How often to check the file (seconds)
    """
    last_timestamp = 0.0
    logger.info(f"[SCHEME-IPC] Watcher started, polling every {poll_interval}s")

    while True:
        try:
            signal = read_scheme_signal()
            if signal:
                scheme, timestamp = signal
                if timestamp > last_timestamp:
                    logger.info(f"[SCHEME-IPC] New scheme signal detected: {scheme}")
                    last_timestamp = timestamp
                    callback(scheme)
                    clear_scheme_signal()

            await asyncio.sleep(poll_interval)

        except asyncio.CancelledError:
            logger.info("[SCHEME-IPC] Watcher stopped")
            break
        except Exception as e:
            logger.error(f"[SCHEME-IPC] Watcher error: {e}")
            await asyncio.sleep(poll_interval)


# CLI testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    print("[TEST] Scheme Manager")
    print("=" * 50)

    # Test modular schema availability
    print(f"\n[INFO] Modular schemas available: {MODULAR_SCHEMAS_AVAILABLE}")
    if MODULAR_SCHEMAS_AVAILABLE:
        registered = list_schemas()
        print("[INFO] Registered schemas:")
        for name, is_registered in registered.items():
            status = "OK" if is_registered else "MISSING"
            print(f"  - {name}: {status}")

    manager = SchemeManager()

    print(f"\nStatus: {manager.get_status()}")
    print(f"\nCurrent scheme: {manager.current_scheme.value}")
    print(f"Time remaining: {manager.get_time_remaining()}s")

    # Test scheme switching
    print("\n--- Testing scheme rotation ---")
    for _ in range(5):
        scheme = manager.next_scheme()
        print(f"  Now: {scheme.value}")

    # Test filter building (both legacy and modular)
    print("\n--- Testing filter builders ---")
    for scheme in OutputScheme:
        manager.set_scheme(scheme)
        filter_str = manager.build_ffmpeg_filter()
        print(f"\n{scheme.value}:")
        print(f"  {filter_str[:100]}...")

    # Test modular schema direct access
    if MODULAR_SCHEMAS_AVAILABLE:
        print("\n--- Testing modular schema access ---")
        karaoke = manager.get_modular_schema("karaoke")
        if karaoke:
            print(f"  Karaoke schema: {karaoke.NAME}")
            print(f"  Display name: {karaoke.DISPLAY_NAME}")
            print(f"  Mode: {karaoke.MODE.value}")

    print("\n[OK] Scheme manager ready")
