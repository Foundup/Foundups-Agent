"""
Karaoke Schema - STT lyrics overlay with beat-synced animation.

Status: COMPLETE (lyrics cache), PARTIAL (live STT)
Commands: /karaoki, /lyrics, !karaoke
"""

from ..base import BaseSchema, SchemaMode, SchemaConfig
from .. import register_schema, SchemaType


class KaraokeSchema(BaseSchema):
    """
    STT lyrics overlay with beat-synced text animation.

    Features:
    - Lyrics cache lookup (SQLite from whisper-stt)
    - LRCLib fallback for missing lyrics
    - SRT subtitle overlay via FFmpeg
    - Beat-synced fontsize pulse animation
    """

    NAME = "karaoke"
    DISPLAY_NAME = "Karaoke"
    DESCRIPTION = "STT lyrics overlay with beat-synced animation"
    MODE = SchemaMode.FFMPEG

    def __init__(self, config: SchemaConfig = None):
        super().__init__(config)
        # Default settings
        defaults = {
            'srt_path': '',
            'font_size': 48,
            'bpm': 120,
        }
        for key, value in defaults.items():
            if key not in self.config.settings:
                self.config.settings[key] = value

    def build_ffmpeg_filter(self) -> str:
        """Build FFmpeg filter for karaoke mode."""
        srt_path = self.config.settings.get('srt_path', '')
        font_size = self.config.settings.get('font_size', 48)
        bpm = self.config.settings.get('bpm', 120)

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
            # Placeholder with beat-synced animation
            bpm_freq = bpm / 60.0 * 6.28
            fontsize_expr = f"{font_size}+10*sin(t*{bpm_freq:.4f})"
            return (
                f"[1:v]scale=1920:1080,format=yuv420p[bg];"
                f"[bg]drawtext=text='Karaoke Mode - No SRT loaded':"
                f"fontsize='{fontsize_expr}':fontcolor=white:"
                f"x=(w-text_w)/2:y=h-100:"
                f"shadowcolor=black:shadowx=2:shadowy=2[out]"
            )

    def set_srt(self, srt_path: str) -> None:
        """Set the SRT file path for lyrics display."""
        self.config.settings['srt_path'] = srt_path

    def set_bpm(self, bpm: int) -> None:
        """Set BPM for beat-synced animation."""
        self.config.settings['bpm'] = bpm


# Register on import
register_schema(SchemaType.KARAOKE, KaraokeSchema)
