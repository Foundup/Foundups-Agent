#!/usr/bin/env python3
"""
Generate LRC files from audio using Whisper STT.

For original FFCPLN songs, this creates .lrc files that can be:
1. Reviewed/edited by 012 for accuracy
2. Imported into lyrics_cache.db

Usage:
    # From single audio file:
    python generate_lrc_files.py --audio "path/to/song.mp3" --artist "UnDaoDu" --title "fuck trump"

    # From folder of audio files:
    python generate_lrc_files.py --folder "E:/Music/FFCPLN" --output "data/lrc_files"

    # From live stream (capture current song):
    python generate_lrc_files.py --live --duration 180

    # Auto-import generated LRC files to cache:
    python generate_lrc_files.py --folder "data/lrc_files" --import-to-cache
"""

import argparse
import json
import logging
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Tuple, Optional

# Setup paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
STREAM_URL = "https://a12.asurahosting.com/listen/antifafm/radio.mp3"
DEFAULT_OUTPUT_DIR = Path("data/lrc_files")


def transcribe_audio(audio_path: str, model_name: str = "base.en") -> List[Tuple[int, str]]:
    """
    Transcribe audio file using Whisper STT.

    Args:
        audio_path: Path to audio file
        model_name: Whisper model (tiny, base, small, medium, large)

    Returns:
        List of (timestamp_ms, text) tuples
    """
    try:
        from modules.platform_integration.antifafm_broadcaster.src.karaoke_overlay import (
            WhisperSTTEngine
        )
    except ImportError:
        logger.error("karaoke_overlay module not available. Install faster-whisper:")
        logger.error("  pip install faster-whisper")
        return []

    logger.info(f"[WHISPER] Loading model: {model_name}")
    stt = WhisperSTTEngine(model_name=model_name, device="cpu")

    if not stt.initialize():
        logger.error("[WHISPER] Failed to initialize model")
        return []

    logger.info(f"[WHISPER] Transcribing: {audio_path}")
    segments = stt.transcribe_audio(audio_path, language="en")

    if not segments:
        logger.warning("[WHISPER] No transcription results")
        return []

    # Convert to (timestamp_ms, text) format
    lyrics = []
    for segment in segments:
        if segment.words:
            # Word-level timing - group into lines (every ~8 words)
            line_words = []
            line_start = None

            for word in segment.words:
                if not word.word.strip():
                    continue

                if line_start is None:
                    line_start = int(word.start_time * 1000)

                line_words.append(word.word.strip())

                # Create line every 8 words or at sentence end
                if len(line_words) >= 8 or word.word.strip().endswith(('.', '!', '?', ',')):
                    lyrics.append((line_start, ' '.join(line_words)))
                    line_words = []
                    line_start = None

            # Remaining words
            if line_words:
                lyrics.append((line_start, ' '.join(line_words)))
        else:
            # Segment-level timing
            if segment.text.strip():
                lyrics.append((int(segment.start_time * 1000), segment.text.strip()))

    logger.info(f"[WHISPER] Generated {len(lyrics)} lyric lines")
    return lyrics


def lyrics_to_lrc(lyrics: List[Tuple[int, str]], artist: str = "", title: str = "") -> str:
    """
    Convert lyrics to LRC format string.

    Args:
        lyrics: List of (timestamp_ms, text) tuples
        artist: Song artist (for metadata)
        title: Song title (for metadata)

    Returns:
        LRC format string
    """
    lines = []

    # LRC metadata header
    if artist:
        lines.append(f"[ar:{artist}]")
    if title:
        lines.append(f"[ti:{title}]")
    lines.append("[by:Whisper STT / antifaFM]")
    lines.append("")

    # Lyrics with timestamps
    for timestamp_ms, text in lyrics:
        mins = timestamp_ms // 60000
        secs = (timestamp_ms % 60000) // 1000
        centis = (timestamp_ms % 1000) // 10
        lines.append(f"[{mins:02d}:{secs:02d}.{centis:02d}] {text}")

    return '\n'.join(lines)


def generate_from_audio(audio_path: Path, output_dir: Path, artist: str = "", title: str = "", model: str = "base.en") -> Optional[Path]:
    """
    Generate LRC file from audio file.

    Args:
        audio_path: Path to audio file
        output_dir: Directory to save LRC file
        artist: Song artist
        title: Song title (defaults to filename)
        model: Whisper model name

    Returns:
        Path to generated LRC file, or None on failure
    """
    if not audio_path.exists():
        logger.error(f"Audio file not found: {audio_path}")
        return None

    # Default title from filename
    if not title:
        title = audio_path.stem

    logger.info(f"[GENERATE] Processing: {artist} - {title}")

    # Transcribe
    lyrics = transcribe_audio(str(audio_path), model_name=model)

    if not lyrics:
        logger.warning(f"[GENERATE] No lyrics generated for: {title}")
        return None

    # Convert to LRC format
    lrc_content = lyrics_to_lrc(lyrics, artist=artist, title=title)

    # Save LRC file
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_filename = "".join(c if c.isalnum() or c in " -_" else "_" for c in f"{artist}_{title}")
    lrc_path = output_dir / f"{safe_filename[:60]}.lrc"

    with open(lrc_path, 'w', encoding='utf-8') as f:
        f.write(lrc_content)

    logger.info(f"[GENERATE] Created: {lrc_path}")
    return lrc_path


def generate_from_live(duration: int, output_dir: Path, model: str = "base.en") -> Optional[Path]:
    """
    Capture audio from live stream and generate LRC file.

    Args:
        duration: Seconds of audio to capture
        output_dir: Directory to save LRC file
        model: Whisper model name

    Returns:
        Path to generated LRC file, or None on failure
    """
    import requests

    # Get current song info from AzuraCast
    try:
        r = requests.get("https://a12.asurahosting.com/api/nowplaying/antifafm", timeout=10)
        r.raise_for_status()
        data = r.json()
        song = data.get("now_playing", {}).get("song", {})
        artist = song.get("artist", "Unknown")
        title = song.get("title", "Unknown")
        logger.info(f"[LIVE] Current song: {artist} - {title}")
    except Exception as e:
        logger.warning(f"[LIVE] Could not get song info: {e}")
        artist = "antifaFM"
        title = f"live_capture_{duration}s"

    # Capture audio to temp file
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
        temp_audio = tmp.name

    try:
        logger.info(f"[LIVE] Capturing {duration}s of audio...")
        cmd = [
            "ffmpeg", "-y",
            "-i", STREAM_URL,
            "-t", str(duration),
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            temp_audio
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=duration + 60)
        if result.returncode != 0:
            logger.error(f"[LIVE] Audio capture failed: {result.stderr[:200]}")
            return None

        # Generate LRC from captured audio
        return generate_from_audio(Path(temp_audio), output_dir, artist=artist, title=title, model=model)

    finally:
        try:
            os.unlink(temp_audio)
        except:
            pass


def batch_generate_from_folder(folder: Path, output_dir: Path, model: str = "base.en") -> List[Path]:
    """
    Generate LRC files for all audio files in a folder.

    Supports: .mp3, .wav, .flac, .ogg, .m4a

    Args:
        folder: Folder containing audio files
        output_dir: Directory to save LRC files
        model: Whisper model name

    Returns:
        List of generated LRC file paths
    """
    audio_extensions = {'.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac'}

    audio_files = [f for f in folder.iterdir() if f.suffix.lower() in audio_extensions]

    if not audio_files:
        logger.warning(f"[BATCH] No audio files found in: {folder}")
        return []

    logger.info(f"[BATCH] Found {len(audio_files)} audio files")

    generated = []
    for audio_file in audio_files:
        # Try to extract artist from filename (format: "Artist - Title.mp3")
        parts = audio_file.stem.split(' - ', 1)
        if len(parts) == 2:
            artist, title = parts
        else:
            artist = ""
            title = audio_file.stem

        lrc_path = generate_from_audio(audio_file, output_dir, artist=artist, title=title, model=model)
        if lrc_path:
            generated.append(lrc_path)

    logger.info(f"[BATCH] Generated {len(generated)}/{len(audio_files)} LRC files")
    return generated


def import_lrc_folder_to_cache(lrc_folder: Path) -> int:
    """
    Import all LRC files from folder into lyrics cache.

    Args:
        lrc_folder: Folder containing .lrc files

    Returns:
        Number of files imported
    """
    try:
        from modules.platform_integration.antifafm_broadcaster.scripts.launch import import_lrc_file
    except ImportError:
        logger.error("Could not import launch.py functions")
        return 0

    lrc_files = list(lrc_folder.glob("*.lrc"))

    if not lrc_files:
        logger.warning(f"[IMPORT] No .lrc files found in: {lrc_folder}")
        return 0

    logger.info(f"[IMPORT] Found {len(lrc_files)} LRC files")

    imported = 0
    for lrc_file in lrc_files:
        # Parse metadata from LRC file
        artist = ""
        title = ""

        with open(lrc_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith("[ar:"):
                    artist = line[4:].rstrip("]\n")
                elif line.startswith("[ti:"):
                    title = line[4:].rstrip("]\n")
                elif line.startswith("[") and not line.startswith("[by:"):
                    break  # Reached lyrics

        # Fallback to filename
        if not title:
            parts = lrc_file.stem.split('_', 1)
            if len(parts) == 2:
                artist, title = parts
            else:
                title = lrc_file.stem

        if import_lrc_file(artist, title, str(lrc_file)):
            imported += 1
            logger.info(f"[IMPORT] Imported: {artist} - {title}")
        else:
            logger.warning(f"[IMPORT] Failed: {lrc_file.name}")

    logger.info(f"[IMPORT] Successfully imported {imported}/{len(lrc_files)} files")
    return imported


def main():
    parser = argparse.ArgumentParser(
        description="Generate LRC files from audio using Whisper STT",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single audio file:
  python generate_lrc_files.py --audio song.mp3 --artist "UnDaoDu" --title "fuck trump"

  # Folder of audio files:
  python generate_lrc_files.py --folder "E:/Music/FFCPLN" --output "data/lrc_files"

  # Capture from live stream:
  python generate_lrc_files.py --live --duration 180

  # Import generated LRC files to cache:
  python generate_lrc_files.py --import-folder "data/lrc_files"
        """
    )

    # Input options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--audio", type=Path, help="Single audio file to transcribe")
    input_group.add_argument("--folder", type=Path, help="Folder of audio files to batch process")
    input_group.add_argument("--live", action="store_true", help="Capture from live stream")
    input_group.add_argument("--import-folder", type=Path, dest="import_folder",
                            help="Import LRC files from folder to cache")

    # Common options
    parser.add_argument("--output", "-o", type=Path, default=DEFAULT_OUTPUT_DIR,
                        help="Output directory for LRC files")
    parser.add_argument("--model", "-m", default="base.en",
                        choices=["tiny", "tiny.en", "base", "base.en", "small", "small.en", "medium", "large"],
                        help="Whisper model size (default: base.en)")
    parser.add_argument("--artist", "-a", default="", help="Artist name (for single file)")
    parser.add_argument("--title", "-t", default="", help="Song title (for single file)")
    parser.add_argument("--duration", "-d", type=int, default=180,
                        help="Duration in seconds for live capture (default: 180)")

    args = parser.parse_args()

    print("=" * 60)
    print("[LRC GENERATOR] Whisper STT to LRC files")
    print("=" * 60)

    if args.import_folder:
        # Import mode
        count = import_lrc_folder_to_cache(args.import_folder)
        print(f"\n[DONE] Imported {count} LRC files to cache")

    elif args.live:
        # Live stream capture
        lrc_path = generate_from_live(args.duration, args.output, model=args.model)
        if lrc_path:
            print(f"\n[DONE] Generated: {lrc_path}")
            print(f"[NEXT] Review/edit the file, then import:")
            print(f"       python generate_lrc_files.py --import-folder {args.output}")

    elif args.folder:
        # Batch processing
        generated = batch_generate_from_folder(args.folder, args.output, model=args.model)
        print(f"\n[DONE] Generated {len(generated)} LRC files in: {args.output}")
        print(f"[NEXT] Review/edit the files, then import:")
        print(f"       python generate_lrc_files.py --import-folder {args.output}")

    elif args.audio:
        # Single file
        lrc_path = generate_from_audio(args.audio, args.output, artist=args.artist,
                                       title=args.title, model=args.model)
        if lrc_path:
            print(f"\n[DONE] Generated: {lrc_path}")
            print(f"[NEXT] Review/edit the file, then import:")
            print(f"       python generate_lrc_files.py --import-folder {args.output}")


if __name__ == "__main__":
    main()
