"""
Video Loop Schema - Background video rotation with optional color pulse.

Status: COMPLETE
Commands: /video, !grid
"""

from ..base import BaseSchema, SchemaMode, SchemaConfig
from .. import register_schema, SchemaType


class VideoLoopSchema(BaseSchema):
    """
    Background video loop with optional color pulse effect.

    The foundational visual layer for antifaFM streaming.
    Scales video to 1920x1080, applies optional hue shift.
    """

    NAME = "video_loop"
    DISPLAY_NAME = "Video Loop"
    DESCRIPTION = "Background video loop with optional color pulse"
    MODE = SchemaMode.FFMPEG

    def __init__(self, config: SchemaConfig = None):
        super().__init__(config)
        # Default settings
        if 'color_pulse' not in self.config.settings:
            self.config.settings['color_pulse'] = True

    def build_ffmpeg_filter(self) -> str:
        """Build FFmpeg filter for video loop mode."""
        color_pulse = self.config.settings.get('color_pulse', True)

        filter_parts = [
            "[1:v]scale=1920:1080:force_original_aspect_ratio=decrease",
            "pad=1920:1080:(ow-iw)/2:(oh-ih)/2"
        ]

        if color_pulse:
            filter_parts.append("hue=h=sin(t*0.1)*15")

        filter_parts.append("format=yuv420p[out]")
        return ",".join(filter_parts)


# Register on import
register_schema(SchemaType.VIDEO_LOOP, VideoLoopSchema)
