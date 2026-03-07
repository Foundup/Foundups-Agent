"""
Waveform Visualizer for antifaFM YouTube Live Broadcaster

Layer 3: Audio visualization using FFmpeg showwaves/showfreqs filters.
Creates animated audio visualizations from the Icecast stream.

Visualizations:
- showwaves: Waveform display (line, point, filled, cline)
- showfreqs: Frequency spectrum (bar, dot, line)

WSP Compliance:
- WSP 27: Universal DAE Architecture (Phase 1: Protocol layer)
- WSP 84: Code Reuse (FFmpeg filter patterns from visual_effects.py)
- WSP 91: Observability (visualization mode logging)

Pattern: Occam's Layer 3 - zero-cost audio visualization with FFmpeg
"""

import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List

logger = logging.getLogger(__name__)


class WaveformMode(Enum):
    """Waveform display modes (FFmpeg showwaves)."""
    LINE = "line"           # Simple line
    POINT = "point"         # Points
    FILLED = "filled"       # Filled waveform
    CLINE = "cline"         # Centered line (bi-directional)
    P2P = "p2p"             # Peak to peak


class FrequencyMode(Enum):
    """Frequency spectrum display modes (FFmpeg showfreqs)."""
    BAR = "bar"             # Bar graph
    DOT = "dot"             # Dot display
    LINE = "line"           # Line graph


class VisualizerType(Enum):
    """Type of audio visualization."""
    WAVEFORM = "waveform"   # Time-domain waveform (showwaves)
    SPECTRUM = "spectrum"   # Frequency spectrum (showfreqs)
    COMBINED = "combined"   # Both overlaid


@dataclass
class WaveformConfig:
    """Waveform (showwaves) configuration."""
    enabled: bool = True
    mode: WaveformMode = WaveformMode.CLINE
    # Color scheme (FFmpeg color names or hex)
    colors: str = "0xff0000|0xffffff"  # Red + white gradient
    # Visualization dimensions (within 1920x1080 output)
    width: int = 1920
    height: int = 540   # Half screen height for bottom visualization
    # Rate of frames per second
    rate: int = 30
    # Scale factor for amplitude
    scale: str = "lin"  # lin, log, sqrt, cbrt


@dataclass
class SpectrumConfig:
    """Frequency spectrum (showfreqs) configuration."""
    enabled: bool = False
    mode: FrequencyMode = FrequencyMode.BAR
    colors: str = "0xff0000|0x00ff00|0x0000ff"  # RGB gradient
    width: int = 1920
    height: int = 540
    # FFT window size (power of 2)
    fft_size: int = 2048
    # Frequency scale
    fscale: str = "log"  # lin, log, rlog


@dataclass
class BackgroundConfig:
    """Background configuration for waveform overlay."""
    # Color or image path
    color: str = "black"
    # If image path, use as background
    image_path: Optional[str] = None
    # Gradient overlay (top to bottom)
    gradient: bool = True
    gradient_colors: str = "0x1a1a2e:0x16213e"  # Dark blue gradient


@dataclass
class WaveformVisualizerConfig:
    """Combined waveform visualizer configuration."""
    visualizer_type: VisualizerType = VisualizerType.WAVEFORM
    waveform: WaveformConfig = field(default_factory=WaveformConfig)
    spectrum: SpectrumConfig = field(default_factory=SpectrumConfig)
    background: BackgroundConfig = field(default_factory=BackgroundConfig)
    output_resolution: str = "1920x1080"
    output_fps: int = 30
    # antifaFM branding
    add_logo_overlay: bool = True
    logo_text: str = "antifaFM"


class WaveformVisualizerBuilder:
    """
    Builds FFmpeg filter_complex strings for audio visualization.

    Creates waveform/spectrum visualizations overlaid on background.
    """

    def __init__(self, config: Optional[WaveformVisualizerConfig] = None):
        """
        Initialize waveform visualizer builder.

        Args:
            config: Visualizer configuration. Loads from ENV if None.
        """
        self.config = config or self._load_config_from_env()
        logger.info(f"[WAVEFORM] Visualizer initialized: {self.config.visualizer_type.value}")

    def _load_config_from_env(self) -> WaveformVisualizerConfig:
        """Load configuration from environment variables."""
        config = WaveformVisualizerConfig()

        # Visualizer type
        viz_type = os.getenv("ANTIFAFM_VIZ_TYPE", "waveform").lower()
        if viz_type == "spectrum":
            config.visualizer_type = VisualizerType.SPECTRUM
        elif viz_type == "combined":
            config.visualizer_type = VisualizerType.COMBINED
        else:
            config.visualizer_type = VisualizerType.WAVEFORM

        # Waveform mode
        wave_mode = os.getenv("ANTIFAFM_VIZ_WAVE_MODE", "cline").lower()
        for mode in WaveformMode:
            if mode.value == wave_mode:
                config.waveform.mode = mode
                break

        # Colors (can be customized via ENV)
        wave_colors = os.getenv("ANTIFAFM_VIZ_COLORS")
        if wave_colors:
            config.waveform.colors = wave_colors
            config.spectrum.colors = wave_colors

        # Background color
        bg_color = os.getenv("ANTIFAFM_VIZ_BG_COLOR")
        if bg_color:
            config.background.color = bg_color

        return config

    def build_filter_complex(self, audio_input_index: int = 0) -> str:
        """
        Build FFmpeg filter_complex string for audio visualization.

        Args:
            audio_input_index: Index of the audio input (usually 0)

        Returns:
            FFmpeg filter_complex string
        """
        filters = []
        width, height = self.config.output_resolution.split("x")
        w, h = int(width), int(height)

        # 1. Generate background
        bg_filter = self._build_background_filter(w, h)
        filters.append(bg_filter)

        # 2. Generate visualization based on type
        if self.config.visualizer_type == VisualizerType.WAVEFORM:
            viz_filter = self._build_waveform_filter(audio_input_index)
            filters.append(viz_filter)

        elif self.config.visualizer_type == VisualizerType.SPECTRUM:
            viz_filter = self._build_spectrum_filter(audio_input_index)
            filters.append(viz_filter)

        elif self.config.visualizer_type == VisualizerType.COMBINED:
            # Both waveform and spectrum
            wave_filter = self._build_waveform_filter(audio_input_index, output_tag="wave")
            spec_filter = self._build_spectrum_filter(audio_input_index, output_tag="spec")
            filters.append(wave_filter)
            filters.append(spec_filter)

        # 3. Overlay visualization on background
        overlay_filter = self._build_overlay_filter()
        filters.append(overlay_filter)

        # 4. Add logo text if enabled
        if self.config.add_logo_overlay:
            logo_filter = self._build_logo_filter()
            filters.append(logo_filter)

        # 5. Format conversion for YouTube RTMP
        filters.append("[prefinal]format=yuv420p[out]")

        return ";".join(filters)

    def _build_background_filter(self, width: int, height: int) -> str:
        """Build background color/gradient filter."""
        if self.config.background.gradient:
            # Create gradient background using FFmpeg
            colors = self.config.background.gradient_colors.replace(":", ",")
            return (
                f"color=c={self.config.background.color}:s={width}x{height}:r={self.config.output_fps},"
                f"format=yuv420p[bg]"
            )
        else:
            return (
                f"color=c={self.config.background.color}:s={width}x{height}:r={self.config.output_fps},"
                f"format=yuv420p[bg]"
            )

    def _build_waveform_filter(self, audio_idx: int, output_tag: str = "viz") -> str:
        """Build showwaves filter for waveform visualization."""
        wc = self.config.waveform
        return (
            f"[{audio_idx}:a]showwaves="
            f"s={wc.width}x{wc.height}:"
            f"mode={wc.mode.value}:"
            f"colors={wc.colors}:"
            f"rate={wc.rate}:"
            f"scale={wc.scale}"
            f"[{output_tag}]"
        )

    def _build_spectrum_filter(self, audio_idx: int, output_tag: str = "viz") -> str:
        """Build showfreqs filter for frequency spectrum."""
        sc = self.config.spectrum
        return (
            f"[{audio_idx}:a]showfreqs="
            f"s={sc.width}x{sc.height}:"
            f"mode={sc.mode.value}:"
            f"colors={sc.colors}:"
            f"fscale={sc.fscale}:"
            f"win_size={sc.fft_size}"
            f"[{output_tag}]"
        )

    def _build_overlay_filter(self) -> str:
        """Build overlay filter to place visualization on background."""
        h = int(self.config.output_resolution.split("x")[1])
        wc = self.config.waveform

        if self.config.visualizer_type == VisualizerType.COMBINED:
            # Stack waveform on top, spectrum on bottom
            return (
                "[bg][wave]overlay=0:0[tmp1];"
                f"[tmp1][spec]overlay=0:{h - wc.height}[prefinal]"
            )
        else:
            # Center visualization vertically (or put at bottom)
            y_pos = h - wc.height  # Bottom position
            return f"[bg][viz]overlay=0:{y_pos}[prefinal]"

    def _build_logo_filter(self) -> str:
        """Build logo text overlay filter."""
        return (
            "[prefinal]drawtext="
            f"text='{self.config.logo_text}':"
            "fontsize=36:"
            "fontcolor=white@0.7:"
            "x=20:y=20:"
            "shadowcolor=black@0.5:shadowx=2:shadowy=2"
            "[prefinal]"
        )

    def get_status(self) -> dict:
        """Get current visualizer status."""
        return {
            "visualizer_type": self.config.visualizer_type.value,
            "waveform": {
                "enabled": self.config.waveform.enabled,
                "mode": self.config.waveform.mode.value,
                "colors": self.config.waveform.colors,
            },
            "spectrum": {
                "enabled": self.config.spectrum.enabled,
                "mode": self.config.spectrum.mode.value,
            },
            "background": {
                "color": self.config.background.color,
                "gradient": self.config.background.gradient,
            },
            "output_resolution": self.config.output_resolution,
            "add_logo": self.config.add_logo_overlay,
        }


def build_waveform_ffmpeg_cmd(
    audio_url: str,
    rtmp_target: str,
    config: Optional[WaveformVisualizerConfig] = None
) -> List[str]:
    """
    Build complete FFmpeg command for waveform visualization streaming.

    This is a standalone command builder for testing waveform mode
    without the full FFmpegStreamer infrastructure.

    Args:
        audio_url: Icecast audio stream URL
        rtmp_target: Full RTMP URL with stream key
        config: Optional visualizer configuration

    Returns:
        List of FFmpeg command arguments
    """
    builder = WaveformVisualizerBuilder(config)
    filter_complex = builder.build_filter_complex(audio_input_index=0)

    cmd = [
        "ffmpeg",
        "-re",  # Real-time input
        "-i", audio_url,  # Audio input [0]
        "-filter_complex", filter_complex,
        "-map", "[out]",  # Video from visualization
        "-map", "0:a",    # Audio passthrough
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-b:v", "2500k",
        "-maxrate", "3000k",
        "-bufsize", "6000k",
        "-g", "60",
        "-c:a", "aac",
        "-b:a", "128k",
        "-ar", "44100",
        "-f", "flv",
        rtmp_target,
    ]

    return cmd


# CLI testing
if __name__ == "__main__":
    import subprocess
    import sys

    logging.basicConfig(level=logging.DEBUG)

    print("[TEST] Waveform Visualizer Builder")
    print("=" * 50)

    # Test with default config
    builder = WaveformVisualizerBuilder()

    print(f"\nVisualizer type: {builder.config.visualizer_type.value}")
    print(f"\nStatus: {builder.get_status()}")

    # Test filter generation
    filter_str = builder.build_filter_complex()
    print(f"\nFilter complex:\n{filter_str}")

    # Generate test command (don't run - just display)
    test_audio = "https://a12.asurahosting.com/listen/antifafm/radio.mp3"
    test_rtmp = "rtmp://a.rtmp.youtube.com/live2/TEST_KEY"

    cmd = build_waveform_ffmpeg_cmd(test_audio, test_rtmp)
    print(f"\nTest command ({len(cmd)} args):")
    safe_cmd = [c if "TEST_KEY" not in c else "***KEY***" for c in cmd]
    print(" ".join(safe_cmd[:15]) + " ...")

    # Optional: Run 10-second local test (output to file instead of RTMP)
    if "--test" in sys.argv:
        print("\n[TEST] Running 10-second local visualization test...")
        test_cmd = cmd.copy()
        # Replace RTMP with local file
        test_cmd[-1] = "waveform_test_output.mp4"
        test_cmd.insert(-1, "-t")
        test_cmd.insert(-1, "10")

        try:
            result = subprocess.run(test_cmd, capture_output=True, timeout=60)
            if result.returncode == 0:
                print("[OK] Test output saved to waveform_test_output.mp4")
            else:
                print(f"[ERROR] FFmpeg failed: {result.stderr.decode()[:300]}")
        except subprocess.TimeoutExpired:
            print("[ERROR] Test timed out")
        except Exception as e:
            print(f"[ERROR] {e}")
