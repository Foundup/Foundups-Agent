"""
Shorts Pipeline - Build shorts from indexed clip candidates.

Flow:
1) Load index JSON (memory/video_index/{channel}/{video_id}.json)
2) Select clip candidate (or fallback to audio segments)
3) Ensure cached video (yt-dlp)
4) Export clip + format to Shorts
"""

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional


@dataclass
class ShortClipSelection:
    source_video_id: str
    start_time: float
    end_time: float
    duration: float
    selection_source: str  # "clips" | "audio_segments"
    title_hint: str = ""
    description_hint: str = ""


@dataclass
class ShortsBuildResult:
    output_path: str
    formatted_path: Optional[str]
    selection: ShortClipSelection
    cached_source: Optional[str]


def _coerce_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def find_latest_index_video_id(
    *,
    channel_key: str,
    base_dir: Optional[Path] = None,
    skip_marked: bool = True,
) -> Optional[str]:
    """Find the newest indexed video_id for a channel."""
    base = base_dir or Path(os.getenv("VIDEO_INDEXER_ARTIFACT_PATH", "memory/video_index"))
    channel_dir = base / channel_key.lower()
    if not channel_dir.exists():
        return None

    candidates = sorted(channel_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    for path in candidates:
        if not skip_marked:
            return path.stem
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            payload = None
        if isinstance(payload, dict):
            pipeline = payload.get("shorts_pipeline") or {}
            if pipeline.get("built_at"):
                continue
        return path.stem
    return None


def load_index_json(*, channel_key: str, video_id: str) -> Optional[Dict]:
    """Load index JSON from memory/video_index."""
    from modules.platform_integration.youtube_shorts_scheduler.src.index_weave import load_index_json
    return load_index_json(channel_key=channel_key, video_id=video_id)


def select_clip_from_index(
    index_json: Dict,
    *,
    min_duration: float = 15.0,
    max_duration: float = 60.0,
) -> Optional[ShortClipSelection]:
    """Select a clip candidate or fallback to an audio segment."""
    clips = (index_json.get("clips") or {}).get("candidates", []) if isinstance(index_json, dict) else []
    candidates = []

    for c in clips:
        start = _coerce_float(c.get("start_time"))
        end = _coerce_float(c.get("end_time"))
        duration = _coerce_float(c.get("duration"), end - start)
        virality = _coerce_float(c.get("virality_score"), 0.0)
        if duration <= 0:
            continue
        if duration < min_duration or duration > max_duration:
            continue
        candidates.append((virality, start, end, c))

    if candidates:
        candidates.sort(key=lambda item: item[0], reverse=True)
        _, start, end, c = candidates[0]
        duration = end - start
        return ShortClipSelection(
            source_video_id=index_json.get("video_id", ""),
            start_time=start,
            end_time=end,
            duration=duration,
            selection_source="clips",
            title_hint=(c.get("title_suggestion") or ""),
            description_hint=(c.get("description_suggestion") or ""),
        )

    # Fallback: pick from audio segments (Gemini/Whisper)
    segments = (index_json.get("audio") or {}).get("segments", []) if isinstance(index_json, dict) else []
    best = None
    for seg in segments:
        start = _coerce_float(seg.get("start"))
        end = _coerce_float(seg.get("end"))
        duration = end - start
        if duration <= 0:
            continue
        if duration < min_duration or duration > max_duration:
            continue
        if not best or duration > best["duration"]:
            best = {"start": start, "end": end, "duration": duration, "text": seg.get("text", "")}

    if best:
        return ShortClipSelection(
            source_video_id=index_json.get("video_id", ""),
            start_time=best["start"],
            end_time=best["end"],
            duration=best["duration"],
            selection_source="audio_segments",
            title_hint=(best.get("text") or "")[:80],
            description_hint=(best.get("text") or "")[:160],
        )

    return None


def ensure_video_cached(*, video_id: str, max_quality: str = "720p") -> Optional[str]:
    """Ensure video is available in memory/video_cache."""
    from modules.ai_intelligence.video_indexer.src.visual_analyzer import VisualAnalyzer

    va = VisualAnalyzer()
    return va.download_video(video_id=video_id, use_cache=True, max_quality=max_quality)


def build_short_from_index(
    *,
    channel_key: str,
    video_id: str,
    min_duration: float = 15.0,
    max_duration: float = 60.0,
    format_shorts: bool = True,
    max_quality: str = "720p",
) -> ShortsBuildResult:
    """Build a short from indexed clip candidates."""
    index_json = load_index_json(channel_key=channel_key, video_id=video_id)
    if not index_json:
        raise ValueError(f"No index JSON found for {channel_key}:{video_id}")

    selection = select_clip_from_index(
        index_json,
        min_duration=min_duration,
        max_duration=max_duration,
    )
    if not selection:
        raise ValueError("No suitable clip candidates or audio segments found.")

    cached = ensure_video_cached(video_id=video_id, max_quality=max_quality)
    if not cached:
        raise ValueError("Failed to cache source video (yt-dlp)")

    from modules.communication.youtube_shorts.src.clip_exporter import export_clip

    raw_path, shorts_path = export_clip(
        video_id=video_id,
        start_time=str(selection.start_time),
        end_time=str(selection.end_time),
        source_path=cached,
        format_shorts=format_shorts,
    )

    return ShortsBuildResult(
        output_path=str(shorts_path or raw_path),
        formatted_path=str(shorts_path) if shorts_path else None,
        selection=selection,
        cached_source=cached,
    )


def mark_index_short_built(
    *,
    channel_key: str,
    video_id: str,
    result: ShortsBuildResult,
) -> bool:
    """Mark index JSON with Shorts build metadata."""
    index_json = load_index_json(channel_key=channel_key, video_id=video_id)
    if not isinstance(index_json, dict):
        return False

    selection = result.selection
    index_json["shorts_pipeline"] = {
        "built_at": _now_iso(),
        "output_path": result.output_path,
        "formatted_path": result.formatted_path,
        "cached_source": result.cached_source,
        "selection": {
            "start_time": selection.start_time,
            "end_time": selection.end_time,
            "duration": selection.duration,
            "selection_source": selection.selection_source,
            "title_hint": selection.title_hint,
            "description_hint": selection.description_hint,
        },
    }

    from modules.platform_integration.youtube_shorts_scheduler.src.index_weave import save_index_json

    return save_index_json(channel_key=channel_key, video_id=video_id, data=index_json)


def build_short_from_index_auto(
    *,
    channel_key: str,
    video_id: Optional[str] = None,
    min_duration: float = 15.0,
    max_duration: float = 60.0,
    format_shorts: bool = True,
    max_quality: str = "720p",
    auto_pick: bool = True,
    skip_marked: bool = True,
    mark_index: bool = True,
) -> ShortsBuildResult:
    """Build a short from index JSON with optional auto-pick and marking."""
    resolved_video_id = video_id
    if not resolved_video_id and auto_pick:
        resolved_video_id = find_latest_index_video_id(
            channel_key=channel_key,
            skip_marked=skip_marked,
        )

    if not resolved_video_id:
        raise ValueError("video_id required (no index files found)")

    result = build_short_from_index(
        channel_key=channel_key,
        video_id=resolved_video_id,
        min_duration=min_duration,
        max_duration=max_duration,
        format_shorts=format_shorts,
        max_quality=max_quality,
    )

    if mark_index:
        mark_index_short_built(
            channel_key=channel_key,
            video_id=resolved_video_id,
            result=result,
        )

    return result
