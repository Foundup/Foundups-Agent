"""
Karaoke Overlay for antifaFM YouTube Live Broadcaster

Layer 2.5D: Real-time lyrics display using Speech-to-Text on audio stream.
Creates karaoke-style text overlays with beat-synced animation.

Architecture:
    Icecast Audio -> faster-whisper STT -> SRT generator -> FFmpeg subtitles -> YouTube

Features:
- Real-time word timing from Whisper
- Beat-synced text sizing (pulse with BPM)
- Configurable font/position/style
- Confidence threshold filtering

WSP Compliance:
- WSP 27: Universal DAE Architecture (Phase 1: Protocol layer)
- WSP 84: Code Reuse (FFmpeg filter patterns)
- WSP 91: Observability (STT latency metrics)

Pattern: Occam's Layer 2.5D - zero-cost* STT lyrics (* CPU cost only)
"""

import asyncio
import logging
import math
import os
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from datetime import timedelta
from enum import Enum
from pathlib import Path
from typing import List, Optional, Tuple
import threading
import queue

logger = logging.getLogger(__name__)


class TextPosition(Enum):
    """Text overlay position on screen."""
    TOP = "top"
    CENTER = "center"
    BOTTOM = "bottom"


class TextAnimation(Enum):
    """Text animation style."""
    NONE = "none"
    PULSE = "pulse"          # Size pulsing with beat
    FADE = "fade"            # Fade in/out per word
    BOUNCE = "bounce"        # Vertical bounce
    COLOR_SHIFT = "color"    # Hue rotation


@dataclass
class KaraokeConfig:
    """Karaoke overlay configuration."""
    enabled: bool = True
    # STT settings
    whisper_model: str = "base.en"  # Whisper model size (tiny, base, small, medium, large)
    language: str = "en"
    confidence_threshold: float = 0.7  # Min confidence to display word
    # Display settings
    font_size: int = 48
    font_color: str = "white"
    font_name: str = "Arial"
    position: TextPosition = TextPosition.BOTTOM
    margin_bottom: int = 80  # Pixels from bottom
    margin_top: int = 50     # Pixels from top (if position=top)
    # Animation settings
    animation: TextAnimation = TextAnimation.PULSE
    bpm: float = 120.0       # Beats per minute for pulse timing
    pulse_range: int = 10    # Font size variation (+/- pixels)
    # Shadow/outline for readability
    shadow_color: str = "black"
    shadow_x: int = 2
    shadow_y: int = 2
    outline_color: str = "black"
    outline_width: int = 1


@dataclass
class TranscriptWord:
    """A single transcribed word with timing."""
    word: str
    start_time: float  # seconds
    end_time: float    # seconds
    confidence: float  # 0.0 - 1.0


@dataclass
class TranscriptSegment:
    """A segment of transcribed text."""
    text: str
    start_time: float
    end_time: float
    words: List[TranscriptWord] = field(default_factory=list)


class WhisperSTTEngine:
    """
    Speech-to-text engine using faster-whisper.

    Processes audio chunks and returns word-level timestamps.
    """

    def __init__(self, model_name: str = "base.en", device: str = "cpu"):
        """
        Initialize Whisper STT engine.

        Args:
            model_name: Whisper model size
            device: "cpu" or "cuda"
        """
        self.model_name = model_name
        self.device = device
        self.model = None
        self._initialized = False

    def initialize(self) -> bool:
        """Load the Whisper model."""
        if self._initialized:
            return True

        try:
            from faster_whisper import WhisperModel

            logger.info(f"[KARAOKE] Loading Whisper model: {self.model_name}")
            self.model = WhisperModel(
                self.model_name,
                device=self.device,
                compute_type="int8" if self.device == "cpu" else "float16"
            )
            self._initialized = True
            logger.info(f"[KARAOKE] Whisper model loaded successfully")
            return True

        except ImportError:
            logger.error("[KARAOKE] faster-whisper not installed. Run: pip install faster-whisper")
            return False
        except Exception as e:
            logger.error(f"[KARAOKE] Failed to load Whisper model: {e}")
            return False

    def transcribe_audio(
        self,
        audio_path: str,
        language: str = "en"
    ) -> List[TranscriptSegment]:
        """
        Transcribe audio file and return segments with word timestamps.

        Args:
            audio_path: Path to audio file (WAV, MP3, etc.)
            language: Language code

        Returns:
            List of TranscriptSegment with word-level timing
        """
        if not self._initialized:
            if not self.initialize():
                return []

        try:
            segments, info = self.model.transcribe(
                audio_path,
                language=language,
                word_timestamps=True,
                vad_filter=True,  # Voice Activity Detection
            )

            result = []
            for segment in segments:
                words = []
                if segment.words:
                    for word in segment.words:
                        words.append(TranscriptWord(
                            word=word.word.strip(),
                            start_time=word.start,
                            end_time=word.end,
                            confidence=word.probability if hasattr(word, 'probability') else 0.9
                        ))

                result.append(TranscriptSegment(
                    text=segment.text.strip(),
                    start_time=segment.start,
                    end_time=segment.end,
                    words=words
                ))

            return result

        except Exception as e:
            logger.error(f"[KARAOKE] Transcription failed: {e}")
            return []


class SRTGenerator:
    """Generates SRT subtitle files from transcripts."""

    @staticmethod
    def format_time(seconds: float) -> str:
        """Format seconds as SRT timestamp (HH:MM:SS,mmm)."""
        td = timedelta(seconds=seconds)
        hours, remainder = divmod(td.seconds, 3600)
        minutes, secs = divmod(remainder, 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    @classmethod
    def generate_srt(
        cls,
        segments: List[TranscriptSegment],
        output_path: str,
        word_level: bool = True,
        confidence_threshold: float = 0.7
    ) -> bool:
        """
        Generate SRT file from transcript segments.

        Args:
            segments: List of TranscriptSegment
            output_path: Path to save SRT file
            word_level: If True, create entry per word; else per segment
            confidence_threshold: Min confidence for word inclusion

        Returns:
            True if successful
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                index = 1

                if word_level:
                    # One subtitle entry per word
                    for segment in segments:
                        for word in segment.words:
                            if word.confidence >= confidence_threshold:
                                start = cls.format_time(word.start_time)
                                end = cls.format_time(word.end_time)
                                f.write(f"{index}\n")
                                f.write(f"{start} --> {end}\n")
                                f.write(f"{word.word}\n\n")
                                index += 1
                else:
                    # One subtitle entry per segment
                    for segment in segments:
                        start = cls.format_time(segment.start_time)
                        end = cls.format_time(segment.end_time)
                        f.write(f"{index}\n")
                        f.write(f"{start} --> {end}\n")
                        f.write(f"{segment.text}\n\n")
                        index += 1

            logger.info(f"[KARAOKE] Generated SRT with {index - 1} entries: {output_path}")
            return True

        except Exception as e:
            logger.error(f"[KARAOKE] SRT generation failed: {e}")
            return False


class KaraokeFilterBuilder:
    """Builds FFmpeg filter strings for karaoke text overlay."""

    def __init__(self, config: KaraokeConfig):
        self.config = config

    def build_subtitle_filter(self, srt_path: str) -> str:
        """
        Build FFmpeg subtitles filter with karaoke styling.

        Args:
            srt_path: Path to SRT file

        Returns:
            FFmpeg filter string
        """
        c = self.config

        # Build force_style string for ASS styling
        # Format: FontName,FontSize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,
        #         Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,
        #         BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding

        # Convert color names to ASS format (&HBBGGRR)
        primary_color = self._color_to_ass(c.font_color)
        outline_color = self._color_to_ass(c.outline_color)
        shadow_color = self._color_to_ass(c.shadow_color)

        # Alignment: 1=left, 2=center, 5=top-left, 6=top-center, 9=center-left, 10=center
        alignment = 2  # bottom-center
        if c.position == TextPosition.TOP:
            alignment = 6  # top-center
        elif c.position == TextPosition.CENTER:
            alignment = 10  # center

        # Margin from edge
        margin_v = c.margin_bottom if c.position == TextPosition.BOTTOM else c.margin_top

        force_style = (
            f"FontName={c.font_name},"
            f"FontSize={c.font_size},"
            f"PrimaryColour={primary_color},"
            f"OutlineColour={outline_color},"
            f"BackColour={shadow_color},"
            f"Bold=1,"
            f"Outline={c.outline_width},"
            f"Shadow=1,"
            f"Alignment={alignment},"
            f"MarginV={margin_v}"
        )

        # Escape path for FFmpeg (Windows paths need escaping)
        escaped_path = srt_path.replace('\\', '/').replace(':', '\\:')

        return f"subtitles='{escaped_path}':force_style='{force_style}'"

    def build_animated_text_filter(self, text: str, start_time: float, duration: float) -> str:
        """
        Build FFmpeg drawtext filter with beat-synced animation.

        This is for real-time text overlay without SRT files.

        Args:
            text: Text to display
            start_time: When to show (seconds)
            duration: How long to show (seconds)

        Returns:
            FFmpeg drawtext filter string
        """
        c = self.config

        # Calculate Y position
        if c.position == TextPosition.TOP:
            y_expr = str(c.margin_top)
        elif c.position == TextPosition.CENTER:
            y_expr = "(h-text_h)/2"
        else:  # BOTTOM
            y_expr = f"h-text_h-{c.margin_bottom}"

        # Build font size expression based on animation
        if c.animation == TextAnimation.PULSE:
            # Pulse font size with BPM
            # fontsize = base + range * sin(t * BPM/60 * 2 * PI)
            bpm_freq = c.bpm / 60.0 * 2 * math.pi
            fontsize_expr = f"{c.font_size}+{c.pulse_range}*sin(t*{bpm_freq:.4f})"
        elif c.animation == TextAnimation.BOUNCE:
            # Vertical bounce
            bpm_freq = c.bpm / 60.0 * 2 * math.pi
            y_expr = f"h-text_h-{c.margin_bottom}+10*sin(t*{bpm_freq:.4f})"
            fontsize_expr = str(c.font_size)
        else:
            fontsize_expr = str(c.font_size)

        # Enable/disable based on time
        enable_expr = f"between(t,{start_time},{start_time + duration})"

        # Escape text for FFmpeg
        escaped_text = text.replace("'", "\\'").replace(":", "\\:")

        return (
            f"drawtext="
            f"text='{escaped_text}':"
            f"fontsize='{fontsize_expr}':"
            f"fontcolor={c.font_color}:"
            f"x=(w-text_w)/2:"
            f"y={y_expr}:"
            f"shadowcolor={c.shadow_color}:"
            f"shadowx={c.shadow_x}:"
            f"shadowy={c.shadow_y}:"
            f"enable='{enable_expr}'"
        )

    def _color_to_ass(self, color: str) -> str:
        """Convert color name/hex to ASS format (&HAABBGGRR)."""
        # Common color names
        colors = {
            "white": "&H00FFFFFF",
            "black": "&H00000000",
            "red": "&H000000FF",
            "green": "&H0000FF00",
            "blue": "&H00FF0000",
            "yellow": "&H0000FFFF",
            "cyan": "&H00FFFF00",
            "magenta": "&H00FF00FF",
        }
        return colors.get(color.lower(), "&H00FFFFFF")


class RealTimeKaraokeProcessor:
    """
    Real-time karaoke processing for live streams.

    Captures audio chunks, transcribes, and generates overlay commands.
    """

    def __init__(self, config: KaraokeConfig):
        self.config = config
        self.stt_engine = WhisperSTTEngine(model_name=config.whisper_model)
        self.filter_builder = KaraokeFilterBuilder(config)
        self._running = False
        self._audio_queue = queue.Queue()
        self._subtitle_queue = queue.Queue()

    def start(self):
        """Start real-time processing."""
        if not self.stt_engine.initialize():
            logger.error("[KARAOKE] Failed to initialize STT engine")
            return False

        self._running = True
        logger.info("[KARAOKE] Real-time processor started")
        return True

    def stop(self):
        """Stop processing."""
        self._running = False
        logger.info("[KARAOKE] Real-time processor stopped")

    def process_audio_chunk(self, audio_data: bytes, timestamp: float) -> Optional[str]:
        """
        Process an audio chunk and return subtitle text if any.

        Args:
            audio_data: Raw audio bytes
            timestamp: Current stream timestamp

        Returns:
            Transcribed text or None
        """
        # Save audio chunk to temp file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            f.write(audio_data)
            temp_path = f.name

        try:
            segments = self.stt_engine.transcribe_audio(temp_path, self.config.language)
            if segments:
                return segments[0].text
        finally:
            os.unlink(temp_path)

        return None


def build_karaoke_ffmpeg_cmd(
    audio_url: str,
    rtmp_target: str,
    srt_path: str,
    background_image: Optional[str] = None,
    config: Optional[KaraokeConfig] = None
) -> List[str]:
    """
    Build complete FFmpeg command for karaoke streaming.

    Args:
        audio_url: Icecast audio stream URL
        rtmp_target: Full RTMP URL with stream key
        srt_path: Path to SRT subtitle file
        background_image: Optional background image path
        config: Karaoke configuration

    Returns:
        List of FFmpeg command arguments
    """
    config = config or KaraokeConfig()
    filter_builder = KaraokeFilterBuilder(config)

    # Build subtitle filter
    subtitle_filter = filter_builder.build_subtitle_filter(srt_path)

    # Build complete filter chain
    if background_image:
        # With background image
        filter_complex = (
            f"[1:v]scale=1920:1080,format=yuv420p[bg];"
            f"[bg]{subtitle_filter}[out]"
        )

        cmd = [
            "ffmpeg",
            "-re",
            "-i", audio_url,        # [0] Audio
            "-loop", "1",
            "-i", background_image,  # [1] Background image
            "-filter_complex", filter_complex,
            "-map", "[out]",
            "-map", "0:a",
        ]
    else:
        # Generate black background
        filter_complex = (
            f"color=c=black:s=1920x1080:r=30[bg];"
            f"[bg]{subtitle_filter}[out]"
        )

        cmd = [
            "ffmpeg",
            "-re",
            "-i", audio_url,
            "-f", "lavfi",
            "-i", f"color=c=black:s=1920x1080:r=30",
            "-filter_complex", filter_complex,
            "-map", "[out]",
            "-map", "0:a",
        ]

    # Add encoding options
    cmd.extend([
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
    ])

    return cmd


# CLI testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    print("[TEST] Karaoke Overlay Module")
    print("=" * 50)

    # Test configuration
    config = KaraokeConfig()
    print(f"\nConfig:")
    print(f"  Model: {config.whisper_model}")
    print(f"  Font: {config.font_name} {config.font_size}px")
    print(f"  Animation: {config.animation.value}")
    print(f"  BPM: {config.bpm}")

    # Test filter builder
    builder = KaraokeFilterBuilder(config)

    # Test animated text filter
    text_filter = builder.build_animated_text_filter("Hello World", 0, 5)
    print(f"\nAnimated text filter:\n  {text_filter}")

    # Test subtitle filter (would need actual SRT file)
    # subtitle_filter = builder.build_subtitle_filter("test.srt")
    # print(f"\nSubtitle filter:\n  {subtitle_filter}")

    print("\n[OK] Karaoke module ready")
    print("\nTo use with live stream:")
    print("  1. Transcribe audio to SRT")
    print("  2. Apply karaoke filter to FFmpeg stream")
