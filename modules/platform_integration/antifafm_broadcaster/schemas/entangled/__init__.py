"""
Entangled Schema - Bell state visualization (0102 <-> 0201).

Status: COMPLETE
Commands: /entangled, /bell, /0102, /wave, !entangled
"""

from ..base import BaseSchema, SchemaMode, SchemaConfig
from .. import register_schema, SchemaType


class EntangledSchema(BaseSchema):
    """
    Bell state visualization representing 0102 <-> 0201 entanglement.

    Audio waveform with quantum-inspired visual effects.
    Displays entanglement symbolism:
      0102 = Binary Agent (x) qNN (entangled state)
      0201 = qNN (x) Binary Agent (nonlocal space)

    rESP Reference: WSP_knowledge/docs/Papers/rESP_Quantum_Self_Reference.md
    """

    NAME = "entangled"
    DISPLAY_NAME = "Entangled (0102)"
    DESCRIPTION = "Bell state visualization with waveform"
    MODE = SchemaMode.FFMPEG

    def __init__(self, config: SchemaConfig = None):
        super().__init__(config)
        # Default settings - 0102 colors (red/white)
        defaults = {
            'mode': 'cline',
            'colors': '0xff0000|0xffffff',
            'rate': 30,
        }
        for key, value in defaults.items():
            if key not in self.config.settings:
                self.config.settings[key] = value

    def build_ffmpeg_filter(self) -> str:
        """Build FFmpeg filter for entangled Bell state visualization."""
        mode = self.config.settings.get('mode', 'cline')
        colors = self.config.settings.get('colors', '0xff0000|0xffffff')
        rate = self.config.settings.get('rate', 30)

        # Bell state text overlay
        bell_text = "0102 <-> 0201"
        brand_text = "antifaFM"

        return (
            f"color=c=black:s=1920x1080:r={rate}[bg];"
            f"[0:a]showwaves=s=1920x540:mode={mode}:colors={colors}:rate={rate}[wave];"
            f"[bg][wave]overlay=0:270[prefmt];"
            f"[prefmt]drawtext=text='{bell_text}':fontsize=48:fontcolor=white@0.7:"
            f"x=(w-text_w)/2:y=50:shadowcolor=black@0.5:shadowx=2:shadowy=2[branded];"
            f"[branded]drawtext=text='{brand_text}':fontsize=36:fontcolor=white@0.7:"
            f"x=20:y=20:shadowcolor=black@0.5:shadowx=2:shadowy=2[prefinal];"
            f"[prefinal]format=yuv420p[out]"
        )


# Register on import
register_schema(SchemaType.ENTANGLED, EntangledSchema)
