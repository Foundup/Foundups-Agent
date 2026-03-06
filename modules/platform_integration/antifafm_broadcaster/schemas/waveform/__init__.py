"""
Waveform Schema - Audio waveform visualization.

Status: COMPLETE
Commands: /waveform, /wave, !waveform
"""

from ..base import BaseSchema, SchemaMode, SchemaConfig
from .. import register_schema, SchemaType


class WaveformSchema(BaseSchema):
    """
    Audio waveform visualization using FFmpeg showwaves filter.

    Features:
    - Multiple waveform modes (cline, line, point, etc.)
    - Configurable colors
    - antifaFM branding overlay
    """

    NAME = "waveform"
    DISPLAY_NAME = "Waveform"
    DESCRIPTION = "Audio waveform visualization"
    MODE = SchemaMode.FFMPEG

    def __init__(self, config: SchemaConfig = None):
        super().__init__(config)
        # Default settings
        defaults = {
            'mode': 'cline',
            'colors': '0xff0000|0xffffff',
            'rate': 30,
        }
        for key, value in defaults.items():
            if key not in self.config.settings:
                self.config.settings[key] = value

    def build_ffmpeg_filter(self) -> str:
        """Build FFmpeg filter for waveform visualization."""
        mode = self.config.settings.get('mode', 'cline')
        colors = self.config.settings.get('colors', '0xff0000|0xffffff')
        rate = self.config.settings.get('rate', 30)

        return (
            f"color=c=black:s=1920x1080:r={rate}[bg];"
            f"[0:a]showwaves=s=1920x540:mode={mode}:colors={colors}:rate={rate}[wave];"
            f"[bg][wave]overlay=0:270[prefmt];"
            f"[prefmt]drawtext=text='antifaFM':fontsize=36:fontcolor=white@0.7:"
            f"x=20:y=20:shadowcolor=black@0.5:shadowx=2:shadowy=2[prefinal];"
            f"[prefinal]format=yuv420p[out]"
        )

    def set_mode(self, mode: str) -> None:
        """Set waveform mode (cline, line, point, etc.)."""
        valid_modes = ['cline', 'line', 'point', 'p2p', 'scale']
        if mode in valid_modes:
            self.config.settings['mode'] = mode


# Register on import
register_schema(SchemaType.WAVEFORM, WaveformSchema)
