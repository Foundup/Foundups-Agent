"""
Clip Exporter - Cut segments from cached YouTube videos and format for Shorts.

Uses ffmpeg to trim by timestamps and optionally formats to 9:16 via VideoEditor.

Sources:
 - VisualAnalyzer cache: memory/video_cache/{video_id}.mp4
 - Explicit local path (mp4)
"""

import subprocess
from pathlib import Path
from typing import Optional, Tuple


class ClipExportError(Exception):
    """Raised when clip export fails."""


def _parse_timecode(ts: str) -> float:
    """
    Parse time string into seconds.

    Accepts:
        - seconds as float/int ("75" or "12.5")
        - mm:ss ("01:15")
        - hh:mm:ss ("00:02:10")
    """
    ts = ts.strip()
    if not ts:
        raise ValueError("Empty timecode")

    if ":" not in ts:
        return float(ts)

    parts = ts.split(":")
    parts = [float(p) for p in parts]
    if len(parts) == 2:
        minutes, seconds = parts
        return minutes * 60 + seconds
    if len(parts) == 3:
        hours, minutes, seconds = parts
        return hours * 3600 + minutes * 60 + seconds
    raise ValueError(f"Unrecognized timecode: {ts}")


def _find_cached_video(video_id: str) -> Optional[Path]:
    """Locate cached video in memory/video_cache."""
    cache_path = Path("memory/video_cache") / f"{video_id}.mp4"
    return cache_path if cache_path.exists() else None


def export_clip(
    video_id: str,
    start_time: str,
    end_time: str,
    source_path: Optional[str] = None,
    format_shorts: bool = False,
    output_dir: str = "memory/video_lab/clips",
) -> Tuple[Path, Optional[Path]]:
    """
    Export a clip from a cached/local video.

    Args:
        video_id: YouTube video ID (used for cache lookup + filenames)
        start_time: Start timestamp (seconds or mm:ss or hh:mm:ss)
        end_time: End timestamp
        source_path: Optional explicit mp4 path (bypasses cache lookup)
        format_shorts: If True, format output to 9:16 (1080x1920)
        output_dir: Directory for outputs

    Returns:
        (raw_clip_path, shorts_path|None)
    """
    src = Path(source_path) if source_path else _find_cached_video(video_id)
    if not src or not src.exists():
        raise ClipExportError(f"Source video not found. Provide path or cache missing for {video_id}.")

    start_sec = _parse_timecode(start_time)
    end_sec = _parse_timecode(end_time)
    if end_sec <= start_sec:
        raise ClipExportError("end_time must be greater than start_time")

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_out = out_dir / f"{video_id}_{int(start_sec)}-{int(end_sec)}.mp4"

    cmd = [
        "ffmpeg",
        "-y",
        "-ss",
        str(start_sec),
        "-to",
        str(end_sec),
        "-i",
        str(src),
        "-c",
        "copy",
        str(raw_out),
    ]

    try:
        subprocess.run(cmd, capture_output=True, check=True)
    except subprocess.CalledProcessError as e:
        raise ClipExportError(f"ffmpeg failed: {e.stderr.decode(errors='ignore')}")

    shorts_path: Optional[Path] = None
    if format_shorts:
        try:
            from .video_editor import VideoEditor

            editor = VideoEditor()
            shorts_path = Path(editor.ensure_shorts_format(str(raw_out)))
        except Exception as e:
            raise ClipExportError(f"Shorts formatting failed: {e}")

    return raw_out, shorts_path
