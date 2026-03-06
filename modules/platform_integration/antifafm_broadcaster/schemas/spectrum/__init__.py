"""
Spectrum Schema - Frequency spectrum visualization.

Status: COMPLETE
Commands: /spectrum, /freq, !spectrum
"""

from ..base import BaseSchema, SchemaMode, SchemaConfig
from .. import register_schema, SchemaType


class SpectrumSchema(BaseSchema):
    """
    Frequency spectrum visualization using FFmpeg showfreqs filter.

    Features:
    - Multiple display modes (bar, line, etc.)
    - Logarithmic frequency scale
    - Multi-color gradient
    - antifaFM branding overlay
    """

    NAME = "spectrum"
    DISPLAY_NAME = "Spectrum"
    DESCRIPTION = "Frequency spectrum visualization"
    MODE = SchemaMode.FFMPEG

    def __init__(self, config: SchemaConfig = None):
        super().__init__(config)
        # Default settings
        defaults = {
            'mode': 'bar',
            'colors': '0xff0000|0x00ff00|0x0000ff',
            'rate': 30,
            'fscale': 'log',
        }
        for key, value in defaults.items():
            if key not in self.config.settings:
                self.config.settings[key] = value

    def build_ffmpeg_filter(self) -> str:
        """Build FFmpeg filter for frequency spectrum visualization."""
        mode = self.config.settings.get('mode', 'bar')
        colors = self.config.settings.get('colors', '0xff0000|0x00ff00|0x0000ff')
        rate = self.config.settings.get('rate', 30)
        fscale = self.config.settings.get('fscale', 'log')

        return (
            f"color=c=black:s=1920x1080:r={rate}[bg];"
            f"[0:a]showfreqs=s=1920x540:mode={mode}:colors={colors}:fscale={fscale}[spec];"
            f"[bg][spec]overlay=0:270[prefmt];"
            f"[prefmt]drawtext=text='antifaFM':fontsize=36:fontcolor=white@0.7:"
            f"x=20:y=20:shadowcolor=black@0.5:shadowx=2:shadowy=2[prefinal];"
            f"[prefinal]format=yuv420p[out]"
        )

    def set_mode(self, mode: str) -> None:
        """Set display mode (bar, line)."""
        valid_modes = ['bar', 'line']
        if mode in valid_modes:
            self.config.settings['mode'] = mode


# Register on import
register_schema(SchemaType.SPECTRUM, SpectrumSchema)
