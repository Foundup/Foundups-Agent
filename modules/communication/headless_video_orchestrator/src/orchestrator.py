"""
Headless Video Orchestrator - Assemble music videos from audio + visuals.
"""

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from modules.communication.youtube_shorts.src.video_editor import VideoEditor, VideoEditorError


class MusicVideoBuildError(Exception):
    """Raised when music video assembly fails."""


@dataclass
class MusicVideoRequest:
    """Input contract for music video assembly."""
    audio_path: str
    visual_paths: List[str]
    output_dir: str = "memory/video_lab/music_videos"
    aspect: str = "shorts"  # "shorts" | "landscape" | "raw"
    add_transitions: bool = False
    loop_video: bool = False


@dataclass
class MusicVideoOutput:
    """Output contract for music video assembly."""
    output_path: str
    formatted_path: Optional[str]
    combined_visual_path: Optional[str]


class HeadlessVideoOrchestrator:
    """Builds a music video by stitching visuals and overlaying audio."""

    def __init__(self, editor: Optional[VideoEditor] = None) -> None:
        self.editor = editor or VideoEditor()

    def build_music_video(self, req: MusicVideoRequest) -> MusicVideoOutput:
        """Assemble a music video from audio + visuals."""
        if not req.audio_path:
            raise MusicVideoBuildError("audio_path is required")
        audio_path = Path(req.audio_path)
        if not audio_path.exists():
            raise MusicVideoBuildError(f"audio file not found: {audio_path}")

        if not req.visual_paths:
            raise MusicVideoBuildError("visual_paths must contain at least one video")

        visual_paths = [Path(p) for p in req.visual_paths]
        for path in visual_paths:
            if not path.exists():
                raise MusicVideoBuildError(f"visual clip not found: {path}")

        output_dir = Path(req.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        stem = audio_path.stem or "music_video"
        combined_visual_path: Optional[Path] = None

        if len(visual_paths) == 1:
            visual_path = visual_paths[0]
        else:
            combined_visual_path = output_dir / f"{stem}_visuals.mp4"
            try:
                self.editor.concatenate_clips(
                    [str(p) for p in visual_paths],
                    str(combined_visual_path),
                    add_transitions=req.add_transitions,
                )
            except VideoEditorError as e:
                raise MusicVideoBuildError(str(e))
            visual_path = combined_visual_path

        assembled_path = output_dir / f"{stem}_mv.mp4"
        self._overlay_audio(
            video_path=str(visual_path),
            audio_path=str(audio_path),
            output_path=str(assembled_path),
            loop_video=req.loop_video,
        )

        formatted_path: Optional[str] = None
        aspect = (req.aspect or "raw").strip().lower()
        if aspect == "shorts":
            formatted_path = self.editor.ensure_shorts_format(str(assembled_path))
        elif aspect == "landscape":
            formatted_path = self._ensure_landscape_format(str(assembled_path))
        elif aspect in {"raw", ""}:
            formatted_path = None
        else:
            raise MusicVideoBuildError(f"Unknown aspect: {req.aspect}")

        final_path = formatted_path or str(assembled_path)

        return MusicVideoOutput(
            output_path=final_path,
            formatted_path=formatted_path,
            combined_visual_path=str(combined_visual_path) if combined_visual_path else None,
        )

    def _overlay_audio(
        self,
        *,
        video_path: str,
        audio_path: str,
        output_path: str,
        loop_video: bool,
    ) -> None:
        """Use ffmpeg to combine video + audio."""
        cmd = ["ffmpeg", "-y"]
        if loop_video:
            cmd.extend(["-stream_loop", "-1"])
        cmd.extend([
            "-i", video_path,
            "-i", audio_path,
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            output_path,
        ])
        try:
            subprocess.run(cmd, capture_output=True, check=True)
        except subprocess.CalledProcessError as e:
            raise MusicVideoBuildError(f"ffmpeg overlay failed: {e.stderr.decode(errors='ignore')}")

    def _ensure_landscape_format(self, video_path: str) -> str:
        """Ensure 16:9 output for longform."""
        output_path = str(Path(video_path).with_suffix(".landscape.mp4"))
        cmd = [
            "ffmpeg",
            "-y",
            "-i", video_path,
            "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "128k",
            output_path,
        ]
        try:
            subprocess.run(cmd, capture_output=True, check=True)
        except subprocess.CalledProcessError as e:
            raise MusicVideoBuildError(f"ffmpeg landscape format failed: {e.stderr.decode(errors='ignore')}")
        return output_path
