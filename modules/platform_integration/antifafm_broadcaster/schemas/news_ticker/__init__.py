"""
News Ticker Schema - Scrolling headlines with RSS aggregation.

Status: PARTIAL (basic ticker), PLANNED (military alerts)
Commands: /news, !news, !ticker
"""

from ..base import BaseSchema, SchemaMode, SchemaConfig
from .. import register_schema, SchemaType


class NewsTickerSchema(BaseSchema):
    """
    Scrolling news ticker with RSS aggregation.

    Features:
    - Basic scrolling text overlay (COMPLETE)
    - NewsOrchestrator headline queue (COMPLETE)
    - RSS aggregation (PLANNED)
    - Military alerts categorization (PLANNED)
    - AI classification via Gemma (PLANNED)
    """

    NAME = "news_ticker"
    DISPLAY_NAME = "News Ticker"
    DESCRIPTION = "Scrolling headlines with RSS aggregation"
    MODE = SchemaMode.FFMPEG

    def __init__(self, config: SchemaConfig = None):
        super().__init__(config)
        # Default settings
        defaults = {
            'text': 'antifaFM - 24/7 Resistance Radio',
            'speed': 100,
            'font_size': 36,
        }
        for key, value in defaults.items():
            if key not in self.config.settings:
                self.config.settings[key] = value

    def build_ffmpeg_filter(self) -> str:
        """Build FFmpeg filter for scrolling news ticker."""
        text = self.config.settings.get('text', 'antifaFM - 24/7 Resistance Radio')
        speed = self.config.settings.get('speed', 100)
        font_size = self.config.settings.get('font_size', 36)

        # Escape special characters for FFmpeg drawtext
        safe_text = text.replace("'", "\\'").replace(":", "\\:")

        return (
            f"[1:v]scale=1920:1080,format=yuv420p[bg];"
            f"[bg]drawtext=text='{safe_text}':"
            f"fontsize={font_size}:fontcolor=white:"
            f"x=w-mod(t*{speed}\\,w+tw):y=h-50:"
            f"shadowcolor=black:shadowx=2:shadowy=2[out]"
        )

    def set_headline(self, text: str) -> None:
        """Set the current headline text."""
        self.config.settings['text'] = text

    def set_speed(self, pixels_per_second: int) -> None:
        """Set scroll speed in pixels per second."""
        self.config.settings['speed'] = pixels_per_second


# Register on import
register_schema(SchemaType.NEWS_TICKER, NewsTickerSchema)
