"""
Visual Effects Module for antifaFM YouTube Live Broadcaster

Zero-cost animation effects using FFmpeg filters:
- Ken Burns (zoompan) - creates movement from static images
- Color Pulse (hue shift) - subtle color variation
- GIF Overlay - animated logo/waveform element
- Image Cycling - rotate through image library

WSP Compliance:
- WSP 27: Universal DAE Architecture (Phase 1: Protocol layer)
- WSP 84: Code Reuse (FFmpeg filter patterns)
- WSP 91: Observability (effect configuration logging)

Pattern: Occam's Layer 2.5 - maximum visual impact with zero AI cost
"""

import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


class EffectType(Enum):
    """Available visual effect types."""
    KEN_BURNS = "ken_burns"
    COLOR_PULSE = "color_pulse"
    GIF_OVERLAY = "gif_overlay"
    IMAGE_CYCLE = "image_cycle"


@dataclass
class KenBurnsConfig:
    """Ken Burns (zoompan) effect configuration."""
    enabled: bool = True
    zoom_range: float = 0.1  # Max zoom deviation (0.1 = 10% zoom in/out)
    speed: float = 0.05  # Oscillation speed (lower = slower)
    fps: int = 30  # Output frame rate


@dataclass
class ColorPulseConfig:
    """Color pulse (hue shift) effect configuration."""
    enabled: bool = True
    hue_range: float = 15.0  # Max hue shift in degrees
    speed: float = 0.1  # Oscillation speed


@dataclass
class GifOverlayConfig:
    """GIF overlay effect configuration."""
    enabled: bool = True
    gif_path: Optional[str] = None  # Path to animated GIF
    scale: int = 150  # GIF size in pixels
    position: str = "bottom_right"  # top_left, top_right, bottom_left, bottom_right, center
    margin: int = 20  # Margin from edge


@dataclass
class ImageCycleConfig:
    """Image cycling effect configuration."""
    enabled: bool = False  # Disabled by default (requires image library)
    image_dir: Optional[str] = None  # Directory containing images
    duration_per_image: float = 60.0  # Seconds per image
    transition: str = "fade"  # fade, cut


@dataclass
class VisualEffectsConfig:
    """Combined visual effects configuration."""
    ken_burns: KenBurnsConfig = field(default_factory=KenBurnsConfig)
    color_pulse: ColorPulseConfig = field(default_factory=ColorPulseConfig)
    gif_overlay: GifOverlayConfig = field(default_factory=GifOverlayConfig)
    image_cycle: ImageCycleConfig = field(default_factory=ImageCycleConfig)
    output_resolution: str = "1920x1080"
    output_fps: int = 30


class VisualEffectsBuilder:
    """
    Builds FFmpeg filter_complex strings for visual effects.

    Stacks multiple effects in order:
    1. Image input (static or cycling)
    2. Ken Burns (zoompan)
    3. Color Pulse (hue shift)
    4. GIF Overlay
    """

    def __init__(self, config: Optional[VisualEffectsConfig] = None):
        """
        Initialize visual effects builder.

        Args:
            config: Visual effects configuration. Loads from ENV if None.
        """
        self.config = config or self._load_config_from_env()
        logger.info(f"[FX] Visual effects initialized: {self._enabled_effects()}")

    def _load_config_from_env(self) -> VisualEffectsConfig:
        """Load configuration from environment variables."""
        config = VisualEffectsConfig()

        # Ken Burns
        config.ken_burns.enabled = os.getenv(
            "ANTIFAFM_FX_KEN_BURNS", "true"
        ).lower() in ("true", "1", "yes")

        # Color Pulse
        config.color_pulse.enabled = os.getenv(
            "ANTIFAFM_FX_COLOR_PULSE", "true"
        ).lower() in ("true", "1", "yes")

        # GIF Overlay
        config.gif_overlay.enabled = os.getenv(
            "ANTIFAFM_FX_GIF_OVERLAY", "true"
        ).lower() in ("true", "1", "yes")
        gif_path = os.getenv("ANTIFAFM_FX_GIF_PATH")
        if gif_path:
            config.gif_overlay.gif_path = gif_path

        # Image Cycling (disabled by default)
        config.image_cycle.enabled = os.getenv(
            "ANTIFAFM_FX_IMAGE_CYCLE", "false"
        ).lower() in ("true", "1", "yes")
        image_dir = os.getenv("ANTIFAFM_FX_IMAGE_DIR")
        if image_dir:
            config.image_cycle.image_dir = image_dir

        return config

    def _enabled_effects(self) -> List[str]:
        """Get list of enabled effect names."""
        effects = []
        if self.config.ken_burns.enabled:
            effects.append("ken_burns")
        if self.config.color_pulse.enabled:
            effects.append("color_pulse")
        if self.config.gif_overlay.enabled and self.config.gif_overlay.gif_path:
            effects.append("gif_overlay")
        if self.config.image_cycle.enabled and self.config.image_cycle.image_dir:
            effects.append("image_cycle")
        return effects

    def build_filter_complex(self, base_input_index: int = 1) -> str:
        """
        Build FFmpeg filter_complex string.

        Args:
            base_input_index: Index of the image input (usually 1, after audio at 0)

        Returns:
            FFmpeg filter_complex string
        """
        filters = []
        current_stream = f"[{base_input_index}:v]"
        output_stream = "out"

        width, height = self.config.output_resolution.split("x")

        # 1. Ken Burns (zoompan)
        if self.config.ken_burns.enabled:
            kb = self.config.ken_burns
            fps = self.config.output_fps
            # Oscillating zoom with centered framing
            # Note: zoompan uses 'on' (output frame number), not 't' (time)
            # Convert to time-like behavior: on/fps gives seconds
            zoom_expr = f"1.0+{kb.zoom_range}*sin(on/{fps}*{kb.speed})"
            x_expr = "iw/2-(iw/zoom/2)"
            y_expr = "ih/2-(ih/zoom/2)"

            filter_str = (
                f"{current_stream}zoompan="
                f"z='{zoom_expr}':"
                f"x='{x_expr}':"
                f"y='{y_expr}':"
                f"d=1:"
                f"s={self.config.output_resolution}:"
                f"fps={fps}"
                f"[kb]"
            )
            filters.append(filter_str)
            current_stream = "[kb]"

        # 2. Color Pulse (hue shift)
        if self.config.color_pulse.enabled:
            cp = self.config.color_pulse
            hue_expr = f"sin(t*{cp.speed})*{cp.hue_range}"

            filter_str = f"{current_stream}hue=h={hue_expr}[colored]"
            filters.append(filter_str)
            current_stream = "[colored]"

        # 3. GIF Overlay
        if self.config.gif_overlay.enabled and self.config.gif_overlay.gif_path:
            go = self.config.gif_overlay
            gif_input_index = base_input_index + 1  # GIF is next input after image

            # Scale GIF
            filters.append(f"[{gif_input_index}:v]scale={go.scale}:{go.scale}[gif]")

            # Calculate position
            pos = self._calculate_overlay_position(go.position, go.margin, go.scale)

            # Overlay + format conversion for YouTube RTMP compatibility
            filter_str = f"{current_stream}[gif]overlay={pos}[prefmt];[prefmt]format=yuv420p[{output_stream}]"
            filters.append(filter_str)
            current_stream = f"[{output_stream}]"
        else:
            # No GIF overlay - just tag the final stream
            if current_stream != f"[{base_input_index}:v]":
                # We have some filters, need to rename the output
                last_filter = filters[-1]
                # Replace the output tag with temp stream, then add format conversion
                if "[colored]" in last_filter:
                    filters[-1] = last_filter.replace("[colored]", "[prefmt]")
                elif "[kb]" in last_filter:
                    filters[-1] = last_filter.replace("[kb]", "[prefmt]")
                # Add format=yuv420p for YouTube RTMP compatibility
                filters.append(f"[prefmt]format=yuv420p[{output_stream}]")

        # Join filters with semicolons
        if filters:
            return ";".join(filters)

        # No effects enabled - return empty
        return ""

    def _calculate_overlay_position(
        self, position: str, margin: int, size: int
    ) -> str:
        """Calculate FFmpeg overlay position expression."""
        positions = {
            "top_left": f"{margin}:{margin}",
            "top_right": f"W-w-{margin}:{margin}",
            "bottom_left": f"{margin}:H-h-{margin}",
            "bottom_right": f"W-w-{margin}:H-h-{margin}",
            "center": "W/2-w/2:H/2-h/2",
        }
        return positions.get(position, positions["bottom_right"])

    def get_additional_inputs(self) -> List[str]:
        """
        Get list of additional FFmpeg input arguments needed.

        Returns:
            List of FFmpeg input arguments (e.g., ["-ignore_loop", "0", "-i", "logo.gif"])
        """
        inputs = []

        if self.config.gif_overlay.enabled and self.config.gif_overlay.gif_path:
            gif_path = Path(self.config.gif_overlay.gif_path)
            if gif_path.exists():
                inputs.extend(["-ignore_loop", "0", "-i", str(gif_path.absolute())])
            else:
                logger.warning(f"[FX] GIF not found: {gif_path}")

        return inputs

    def get_output_map(self) -> List[str]:
        """
        Get FFmpeg output mapping arguments.

        Returns:
            List of FFmpeg map arguments
        """
        if self._enabled_effects():
            return ["-map", "[out]", "-map", "0:a"]
        return []

    def get_status(self) -> dict:
        """Get current visual effects status."""
        return {
            "enabled_effects": self._enabled_effects(),
            "ken_burns": {
                "enabled": self.config.ken_burns.enabled,
                "zoom_range": self.config.ken_burns.zoom_range,
                "speed": self.config.ken_burns.speed,
            },
            "color_pulse": {
                "enabled": self.config.color_pulse.enabled,
                "hue_range": self.config.color_pulse.hue_range,
                "speed": self.config.color_pulse.speed,
            },
            "gif_overlay": {
                "enabled": self.config.gif_overlay.enabled,
                "gif_path": self.config.gif_overlay.gif_path,
                "position": self.config.gif_overlay.position,
            },
            "image_cycle": {
                "enabled": self.config.image_cycle.enabled,
                "image_dir": self.config.image_cycle.image_dir,
            },
            "output_resolution": self.config.output_resolution,
        }


def create_default_gif(output_path: Path, text: str = "antifaFM") -> bool:
    """
    Create a simple animated GIF using FFmpeg.

    Creates a pulsing text animation for overlay.

    Args:
        output_path: Path to save the GIF
        text: Text to display in the animation

    Returns:
        bool: True if created successfully
    """
    import subprocess

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Create a 3-second pulsing text animation
    # Uses FFmpeg's drawtext with opacity animation
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", "color=c=black@0:s=200x200:d=3:r=15",
        "-vf", (
            f"drawtext=text='{text}':"
            "fontsize=24:"
            "fontcolor=white@'0.5+0.5*sin(t*3)':"
            "x=(w-text_w)/2:"
            "y=(h-text_h)/2"
        ),
        "-gifflags", "+transdiff",
        "-loop", "0",
        str(output_path.absolute())
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            check=True,
            timeout=30
        )
        logger.info(f"[FX] Created default GIF: {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"[FX] Failed to create GIF: {e.stderr.decode()[:200]}")
        return False
    except Exception as e:
        logger.error(f"[FX] GIF creation error: {e}")
        return False


# CLI testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    print("[TEST] Visual Effects Builder")
    print("=" * 50)

    # Test with default config
    builder = VisualEffectsBuilder()

    print(f"\nEnabled effects: {builder._enabled_effects()}")
    print(f"\nStatus: {builder.get_status()}")

    # Test filter generation
    filter_str = builder.build_filter_complex()
    print(f"\nFilter complex:\n{filter_str}")

    # Test additional inputs
    inputs = builder.get_additional_inputs()
    print(f"\nAdditional inputs: {inputs}")

    # Test output map
    output_map = builder.get_output_map()
    print(f"\nOutput map: {output_map}")
