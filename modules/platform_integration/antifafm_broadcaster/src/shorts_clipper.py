"""
antifaFM Shorts Clipper

Captures song segments from antifaFM live stream and creates ready-to-upload Shorts.
Output folder is processed by youtube_shorts_scheduler CLI.

Usage:
    python -m antifafm_broadcaster.src.shorts_clipper --output data/clips/pending

Architecture:
    AzuraCast API (song info) + FFmpeg (record + visual) → MP4 files → shorts_scheduler CLI
"""

import os
import sys
import json
import time
import logging
import subprocess
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
AZURACAST_API = "https://a12.asurahosting.com/api/nowplaying/antifafm"
STREAM_URL = "https://a12.asurahosting.com/listen/antifafm/radio.mp3"
DEFAULT_OUTPUT_DIR = Path("data/clips/pending")
CLIPS_DB = Path("data/clips/clips_db.json")

# Visual settings (Ken Burns on branded background)
BACKGROUND_IMAGE = Path("modules/platform_integration/antifafm_broadcaster/assets/backgrounds/ffcpln_bg.png")
DEFAULT_BG_COLOR = "#1a1a2e"  # Dark blue fallback

# Karaoke styling
KARAOKE_FONT = "Arial"
KARAOKE_FONT_SIZE = 48
KARAOKE_COLOR = "&H00FFFFFF"  # White (ASS format: AABBGGRR)
KARAOKE_OUTLINE = "&H00000000"  # Black outline


@dataclass
class SongInfo:
    """Current song information from AzuraCast."""
    title: str
    artist: str
    elapsed: int  # seconds into song
    duration: int  # total song length
    song_id: str  # unique identifier

    @property
    def remaining(self) -> int:
        return max(0, self.duration - self.elapsed)

    @property
    def safe_filename(self) -> str:
        """Generate filesystem-safe filename."""
        safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in self.title)
        safe_artist = "".join(c if c.isalnum() or c in " -_" else "_" for c in self.artist)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{safe_artist[:30]}_{safe_title[:50]}_{timestamp}".strip("_")


@dataclass
class ClipRecord:
    """Record of a captured clip."""
    song_id: str
    title: str
    artist: str
    duration: int
    filename: str
    created_at: str
    status: str = "pending"  # pending, scheduled, uploaded, failed


class ClipsDatabase:
    """Simple JSON database for tracking clips."""

    def __init__(self, db_path: Path = CLIPS_DB):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.clips: Dict[str, ClipRecord] = {}
        self._load()

    def _load(self):
        if self.db_path.exists():
            try:
                with open(self.db_path, 'r') as f:
                    data = json.load(f)
                    self.clips = {k: ClipRecord(**v) for k, v in data.items()}
            except Exception as e:
                logger.warning(f"Failed to load clips DB: {e}")
                self.clips = {}

    def _save(self):
        with open(self.db_path, 'w') as f:
            json.dump({k: asdict(v) for k, v in self.clips.items()}, f, indent=2)

    def has_clip(self, song_id: str) -> bool:
        """Check if we already have a clip for this song."""
        return song_id in self.clips

    def add_clip(self, record: ClipRecord):
        """Add a clip record."""
        self.clips[record.song_id] = record
        self._save()

    def get_pending_count(self) -> int:
        return sum(1 for c in self.clips.values() if c.status == "pending")


def fetch_lyrics_for_clip(artist: str, title: str) -> list:
    """
    Fetch synchronized lyrics using the existing karaoke system.
    Returns list of (timestamp_ms, text) tuples.

    Priority:
    1. SQLite cache (from previous fetch or manual import)
    2. LrcLib API (for non-original songs)
    3. Whisper STT (for original FFCPLN songs - transcribe from audio)
    """
    try:
        # Import from launch.py - checks cache first, then LrcLib
        from modules.platform_integration.antifafm_broadcaster.scripts.launch import (
            fetch_lyrics, get_cached_lyrics, _save_lyrics_to_cache
        )
        lyrics = fetch_lyrics(artist, title)
        if lyrics:
            return lyrics

        # Check if this was a cache miss (lrclib-miss)
        # For original songs, try Whisper STT fallback
        cached = get_cached_lyrics(artist, title)
        if cached is not None and len(cached) == 0:
            # This is a known lrclib-miss - try Whisper transcription
            logger.info(f"[KARAOKE] LrcLib miss for original song, trying Whisper STT...")
            whisper_lyrics = _transcribe_with_whisper(artist, title)
            if whisper_lyrics:
                # Cache the transcription for future use
                _save_lyrics_to_cache(artist, title, whisper_lyrics, source='whisper-stt')
                return whisper_lyrics

        return []

    except ImportError:
        logger.warning("[KARAOKE] Could not import fetch_lyrics, trying direct LrcLib...")

    # Fallback: direct LrcLib fetch
    try:
        import urllib.request
        import urllib.parse

        query = urllib.parse.urlencode({
            'artist_name': artist or '',
            'track_name': title,
        })
        url = f'https://lrclib.net/api/search?{query}'

        req = urllib.request.Request(url, headers={
            'User-Agent': 'antifaFM-Clipper/1.0',
            'Accept': 'application/json'
        })

        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))

        if not data:
            return []

        # Get first result with synced lyrics
        for result in data:
            synced = result.get('syncedLyrics', '')
            if synced:
                import re
                lyrics = []
                pattern = r'\[(\d{2}):(\d{2})\.(\d{2,3})\](.*)'
                for line in synced.split('\n'):
                    match = re.match(pattern, line)
                    if match:
                        mins, secs, ms, text = match.groups()
                        ms = ms.ljust(3, '0')[:3]
                        timestamp_ms = int(mins) * 60000 + int(secs) * 1000 + int(ms)
                        if text.strip():
                            lyrics.append((timestamp_ms, text.strip()))
                return lyrics

        return []
    except Exception as e:
        logger.warning(f"[KARAOKE] Lyrics fetch failed: {e}")
        return []


def _transcribe_with_whisper(artist: str, title: str, duration_sec: int = 30) -> list:
    """
    Transcribe audio from live stream using Whisper STT.

    For original FFCPLN songs without LrcLib lyrics, this captures
    a segment of the live stream and transcribes it.

    Args:
        artist: Song artist (for logging)
        title: Song title (for logging)
        duration_sec: Seconds of audio to capture and transcribe

    Returns:
        List of (timestamp_ms, text) tuples, or empty list on failure
    """
    import tempfile

    try:
        from modules.platform_integration.antifafm_broadcaster.src.karaoke_overlay import (
            WhisperSTTEngine, TranscriptSegment
        )
    except ImportError:
        logger.warning("[WHISPER] karaoke_overlay module not available")
        return []

    logger.info(f"[WHISPER] Transcribing: {artist} - {title} ({duration_sec}s)")

    # Capture audio from stream to temp file
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
        temp_audio = tmp.name

    try:
        # Record audio segment from stream
        cmd = [
            "ffmpeg", "-y",
            "-i", STREAM_URL,
            "-t", str(duration_sec),
            "-acodec", "pcm_s16le",
            "-ar", "16000",  # 16kHz for Whisper
            "-ac", "1",      # Mono
            temp_audio
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=duration_sec + 30)
        if result.returncode != 0:
            logger.warning(f"[WHISPER] Audio capture failed: {result.stderr[:200]}")
            return []

        # Transcribe with Whisper
        stt = WhisperSTTEngine(model_name="base.en", device="cpu")
        if not stt.initialize():
            logger.warning("[WHISPER] Failed to initialize Whisper model")
            return []

        segments = stt.transcribe_audio(temp_audio, language="en")

        if not segments:
            logger.warning("[WHISPER] No transcription results")
            return []

        # Convert to (timestamp_ms, text) format
        lyrics = []
        for segment in segments:
            if segment.words:
                # Word-level timing available
                for word in segment.words:
                    if word.word.strip():
                        lyrics.append((int(word.start_time * 1000), word.word.strip()))
            else:
                # Segment-level timing only
                if segment.text.strip():
                    lyrics.append((int(segment.start_time * 1000), segment.text.strip()))

        logger.info(f"[WHISPER] Transcribed {len(lyrics)} words/segments")
        return lyrics

    except subprocess.TimeoutExpired:
        logger.warning("[WHISPER] Audio capture timeout")
        return []
    except Exception as e:
        logger.error(f"[WHISPER] Transcription error: {e}")
        return []
    finally:
        # Cleanup temp file
        try:
            os.unlink(temp_audio)
        except:
            pass


def create_ass_subtitles(lyrics: list, duration_sec: int, output_path: Path) -> bool:
    """
    Create .ass subtitle file from lyrics for FFmpeg.

    Args:
        lyrics: List of (timestamp_ms, text) tuples
        duration_sec: Total video duration in seconds
        output_path: Path to save .ass file

    Returns:
        True if created successfully
    """
    if not lyrics:
        return False

    ass_header = f"""[Script Info]
Title: antifaFM Karaoke
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Karaoke,{KARAOKE_FONT},{KARAOKE_FONT_SIZE},{KARAOKE_COLOR},&H000000FF,{KARAOKE_OUTLINE},&H80000000,-1,0,0,0,100,100,0,0,1,3,2,2,50,50,100,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    events = []
    for i, (timestamp_ms, text) in enumerate(lyrics):
        # Calculate start/end times
        start_sec = timestamp_ms / 1000

        # End time: next lyric or +4 seconds
        if i + 1 < len(lyrics):
            end_sec = lyrics[i + 1][0] / 1000
        else:
            end_sec = min(start_sec + 4, duration_sec)

        # Format times as H:MM:SS.cc
        start_str = f"{int(start_sec//3600)}:{int((start_sec%3600)//60):02d}:{start_sec%60:05.2f}"
        end_str = f"{int(end_sec//3600)}:{int((end_sec%3600)//60):02d}:{end_sec%60:05.2f}"

        # Escape special characters
        safe_text = text.replace('\\', '\\\\').replace('{', '\\{').replace('}', '\\}')

        events.append(f"Dialogue: 0,{start_str},{end_str},Karaoke,,0,0,0,,{safe_text}")

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(ass_header)
            f.write('\n'.join(events))
        logger.info(f"[KARAOKE] Created subtitle file with {len(events)} lines")
        return True
    except Exception as e:
        logger.error(f"[KARAOKE] Failed to create subtitles: {e}")
        return False


class ShortsClipper:
    """Main clipper that monitors stream and captures songs."""

    def __init__(self, output_dir: Path = DEFAULT_OUTPUT_DIR, karaoke: bool = False):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.db = ClipsDatabase()
        self.current_song: Optional[SongInfo] = None
        self.recording_process: Optional[subprocess.Popen] = None
        self.karaoke = karaoke

        if karaoke:
            logger.info("[KARAOKE] Karaoke mode enabled - lyrics will be overlaid")

    def get_current_song(self) -> Optional[SongInfo]:
        """Fetch current song from AzuraCast API."""
        try:
            r = requests.get(AZURACAST_API, timeout=10)
            r.raise_for_status()
            data = r.json()

            now_playing = data.get("now_playing", {})
            song = now_playing.get("song", {})

            return SongInfo(
                title=song.get("title", "Unknown"),
                artist=song.get("artist", "Unknown"),
                elapsed=now_playing.get("elapsed", 0),
                duration=now_playing.get("duration", 180),
                song_id=song.get("id", f"{song.get('artist')}_{song.get('title')}")
            )
        except Exception as e:
            logger.error(f"Failed to get song info: {e}")
            return None

    def should_clip(self, song: SongInfo) -> bool:
        """Determine if we should clip this song."""
        # Skip if already clipped
        if self.db.has_clip(song.song_id):
            logger.info(f"[SKIP] Already clipped: {song.artist} - {song.title}")
            return False

        # Skip very short songs (< 60s)
        if song.duration < 60:
            logger.info(f"[SKIP] Too short ({song.duration}s): {song.artist} - {song.title}")
            return False

        # Skip very long songs (> 4 min for Shorts)
        if song.duration > 240:
            logger.info(f"[SKIP] Too long ({song.duration}s): {song.artist} - {song.title}")
            return False

        return True

    def create_clip(self, song: SongInfo) -> Optional[Path]:
        """
        Record song and create video clip with visuals.
        Optionally adds karaoke lyrics overlay.

        Returns path to created clip or None if failed.
        """
        suffix = "_karaoke" if self.karaoke else ""
        output_file = self.output_dir / f"{song.safe_filename}{suffix}.mp4"
        duration = song.remaining + 5  # Add 5s buffer

        logger.info(f"[RECORD] Starting: {song.artist} - {song.title} ({duration}s)")

        # Fetch lyrics if karaoke mode
        ass_file = None
        if self.karaoke:
            logger.info(f"[KARAOKE] Fetching lyrics for: {song.artist} - {song.title}")
            lyrics = fetch_lyrics_for_clip(song.artist, song.title)
            if lyrics:
                ass_file = self.output_dir / f"{song.safe_filename}.ass"
                if create_ass_subtitles(lyrics, duration, ass_file):
                    logger.info(f"[KARAOKE] Lyrics ready: {len(lyrics)} lines")
                else:
                    ass_file = None
            else:
                logger.warning(f"[KARAOKE] No lyrics found, creating clip without karaoke")

        # Build FFmpeg command
        # Record audio from stream + add visual (solid color or background image)

        if BACKGROUND_IMAGE.exists():
            # Use background image with Ken Burns effect
            filter_complex = (
                "[1:v]scale=1080:1920:force_original_aspect_ratio=increase,"
                "crop=1080:1920,"
                "zoompan=z='1.0+0.0005*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
                "d=1:s=1080x1920:fps=30[v]"
            )

            # Add subtitles if karaoke
            if ass_file and ass_file.exists():
                # Escape path for FFmpeg (Windows paths need escaping)
                ass_path_escaped = str(ass_file).replace('\\', '/').replace(':', '\\:')
                filter_complex = (
                    "[1:v]scale=1080:1920:force_original_aspect_ratio=increase,"
                    "crop=1080:1920,"
                    "zoompan=z='1.0+0.0005*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
                    f"d=1:s=1080x1920:fps=30,ass='{ass_path_escaped}'[v]"
                )

            cmd = [
                "ffmpeg", "-y",
                "-i", STREAM_URL,  # Audio input
                "-loop", "1", "-i", str(BACKGROUND_IMAGE),  # Image input
                "-t", str(duration),
                "-filter_complex", filter_complex,
                "-map", "[v]", "-map", "0:a",
                "-c:v", "libx264", "-preset", "fast", "-crf", "23",
                "-c:a", "aac", "-b:a", "128k",
                "-pix_fmt", "yuv420p",
                "-movflags", "+faststart",
                str(output_file)
            ]
        else:
            # Fallback: solid color background
            vf_filter = ""
            if ass_file and ass_file.exists():
                ass_path_escaped = str(ass_file).replace('\\', '/').replace(':', '\\:')
                vf_filter = f"ass='{ass_path_escaped}'"

            cmd = [
                "ffmpeg", "-y",
                "-i", STREAM_URL,  # Audio input
                "-f", "lavfi", "-i", f"color=c={DEFAULT_BG_COLOR}:s=1080x1920:d={duration}",
                "-t", str(duration),
            ]

            if vf_filter:
                cmd.extend(["-vf", vf_filter])

            cmd.extend([
                "-map", "1:v", "-map", "0:a",
                "-c:v", "libx264", "-preset", "fast", "-crf", "23",
                "-c:a", "aac", "-b:a", "128k",
                "-pix_fmt", "yuv420p",
                "-shortest",
                str(output_file)
            ])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=duration + 60  # Allow extra time for encoding
            )

            if result.returncode == 0 and output_file.exists():
                logger.info(f"[SUCCESS] Created: {output_file.name}")

                # Save metadata alongside video
                meta_file = output_file.with_suffix(".json")
                with open(meta_file, 'w') as f:
                    json.dump({
                        "title": song.title,
                        "artist": song.artist,
                        "duration": song.duration,
                        "song_id": song.song_id,
                        "created_at": datetime.now().isoformat(),
                        "source": "antifaFM",
                        "target_channel": "move2japan"  # For shorts scheduler
                    }, f, indent=2)

                # Record in database
                self.db.add_clip(ClipRecord(
                    song_id=song.song_id,
                    title=song.title,
                    artist=song.artist,
                    duration=song.duration,
                    filename=output_file.name,
                    created_at=datetime.now().isoformat()
                ))

                return output_file
            else:
                logger.error(f"[FAILED] FFmpeg error: {result.stderr[:500]}")
                return None

        except subprocess.TimeoutExpired:
            logger.error(f"[TIMEOUT] Recording took too long")
            return None
        except Exception as e:
            logger.error(f"[ERROR] {e}")
            return None

    def run(self, max_clips: int = 0):
        """
        Main loop - monitor stream and clip songs.

        Args:
            max_clips: Stop after this many clips (0 = unlimited)
        """
        logger.info("=" * 60)
        logger.info("[CLIPPER] antifaFM Shorts Clipper Started")
        logger.info(f"[CLIPPER] Output: {self.output_dir}")
        logger.info(f"[CLIPPER] Existing clips: {len(self.db.clips)}")
        logger.info("=" * 60)

        clips_created = 0
        last_song_id = None

        while True:
            try:
                song = self.get_current_song()

                if not song:
                    logger.warning("[WAIT] No song info, retrying in 30s...")
                    time.sleep(30)
                    continue

                # New song detected
                if song.song_id != last_song_id:
                    logger.info(f"[NOW PLAYING] {song.artist} - {song.title} ({song.duration}s)")
                    last_song_id = song.song_id

                    # Check if we should clip
                    if self.should_clip(song):
                        # Wait for song to start fresh (if we caught it mid-song)
                        if song.elapsed > 10:
                            logger.info(f"[WAIT] Caught mid-song ({song.elapsed}s in), waiting for next...")
                        else:
                            clip_path = self.create_clip(song)
                            if clip_path:
                                clips_created += 1
                                logger.info(f"[STATS] Clips created this session: {clips_created}")
                                logger.info(f"[STATS] Total pending clips: {self.db.get_pending_count()}")

                                if max_clips > 0 and clips_created >= max_clips:
                                    logger.info(f"[DONE] Reached max clips ({max_clips})")
                                    break

                # Poll every 10 seconds
                time.sleep(10)

            except KeyboardInterrupt:
                logger.info("[STOP] Interrupted by user")
                break
            except Exception as e:
                logger.error(f"[ERROR] {e}")
                time.sleep(30)

        logger.info("=" * 60)
        logger.info(f"[CLIPPER] Session complete. Clips created: {clips_created}")
        logger.info(f"[CLIPPER] Total pending: {self.db.get_pending_count()}")
        logger.info(f"[NEXT] Run: python -m youtube_shorts_scheduler.cli schedule --source {self.output_dir}")
        logger.info("=" * 60)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="antifaFM Shorts Clipper")
    parser.add_argument("--output", "-o", type=Path, default=DEFAULT_OUTPUT_DIR,
                        help="Output directory for clips")
    parser.add_argument("--max", "-m", type=int, default=0,
                        help="Max clips to create (0 = unlimited)")
    parser.add_argument("--once", action="store_true",
                        help="Clip current song and exit")
    parser.add_argument("--karaoke", "-k", action="store_true",
                        help="Enable karaoke mode (lyrics overlay)")

    args = parser.parse_args()

    clipper = ShortsClipper(output_dir=args.output, karaoke=args.karaoke)

    if args.once:
        song = clipper.get_current_song()
        if song:
            mode = "karaoke" if args.karaoke else "standard"
            logger.info(f"[ONCE] Clipping ({mode}): {song.artist} - {song.title}")
            clipper.create_clip(song)
        else:
            logger.error("[ONCE] No song playing")
    else:
        clipper.run(max_clips=args.max)


if __name__ == "__main__":
    main()
