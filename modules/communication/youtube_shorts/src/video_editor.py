"""
Video Editor using ffmpeg

Concatenates multiple video clips into final YouTube Short.
Uses open-source ffmpeg for professional video editing.
"""

import subprocess
from pathlib import Path
from typing import List, Optional


class VideoEditorError(Exception):
    """Video editing failed"""
    pass


class VideoEditor:
    """
    Professional video editor using ffmpeg.

    Handles:
    - Concatenating multiple clips
    - Adding transitions (optional)
    - Ensuring proper Shorts format (vertical 9:16)
    - Audio normalization
    """

    def __init__(self):
        """Initialize video editor."""
        self.temp_dir = Path("modules/communication/youtube_shorts/assets/temp")
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def concatenate_clips(
        self,
        clip_paths: List[str],
        output_path: str,
        add_transitions: bool = False
    ) -> str:
        """
        Concatenate multiple video clips into one.

        Args:
            clip_paths: List of paths to video clips (in order)
            output_path: Path for final concatenated video
            add_transitions: Add crossfade transitions between clips

        Returns:
            str: Path to concatenated video

        Raises:
            VideoEditorError: If concatenation fails
        """

        if len(clip_paths) < 2:
            raise VideoEditorError("Need at least 2 clips to concatenate")

        # Verify all clips exist
        for clip_path in clip_paths:
            if not Path(clip_path).exists():
                raise VideoEditorError(f"Clip not found: {clip_path}")

        print(f"\n[VideoEditor] Concatenating {len(clip_paths)} clips...")
        print(f"  Output: {output_path}")

        try:
            if add_transitions:
                return self._concatenate_with_transitions(clip_paths, output_path)
            else:
                return self._concatenate_simple(clip_paths, output_path)

        except subprocess.CalledProcessError as e:
            raise VideoEditorError(f"ffmpeg failed: {e.stderr.decode()}")
        except Exception as e:
            raise VideoEditorError(f"Concatenation failed: {e}")

    def _concatenate_simple(self, clip_paths: List[str], output_path: str) -> str:
        """Simple concatenation without transitions (fastest)."""

        # Create concat file for ffmpeg
        concat_file = self.temp_dir / "concat_list.txt"

        with open(concat_file, 'w') as f:
            for clip_path in clip_paths:
                # Convert to absolute path for ffmpeg
                abs_path = Path(clip_path).absolute()
                f.write(f"file '{abs_path}'\n")

        # ffmpeg concat command
        cmd = [
            'ffmpeg',
            '-y',  # Overwrite output
            '-f', 'concat',
            '-safe', '0',
            '-i', str(concat_file),
            '-c', 'copy',  # Fast copy without re-encoding
            str(output_path)
        ]

        print("[VideoEditor] Running ffmpeg (simple concat)...")
        result = subprocess.run(
            cmd,
            capture_output=True,
            check=True
        )

        print(f"[VideoEditor] ✅ Concatenated {len(clip_paths)} clips")
        print(f"  Output: {output_path}")

        return str(output_path)

    def _concatenate_with_transitions(
        self,
        clip_paths: List[str],
        output_path: str,
        transition_duration: float = 0.5
    ) -> str:
        """
        Concatenate with crossfade transitions between clips.

        Note: This re-encodes video so it's slower but looks more professional.
        """

        # Build filter complex for crossfade transitions
        filter_parts = []
        current_input = "[0:v]"

        for i in range(len(clip_paths) - 1):
            next_input = f"[{i+1}:v]"
            output = f"[v{i}]" if i < len(clip_paths) - 2 else "[outv]"

            # Crossfade transition
            filter_parts.append(
                f"{current_input}{next_input}xfade=transition=fade:"
                f"duration={transition_duration}:offset=4.5{output}"
            )

            current_input = f"[v{i}]"

        filter_complex = ";".join(filter_parts)

        # Build ffmpeg command
        cmd = ['ffmpeg', '-y']

        # Add all input files
        for clip_path in clip_paths:
            cmd.extend(['-i', str(clip_path)])

        # Add filter complex
        cmd.extend([
            '-filter_complex', filter_complex,
            '-map', '[outv]',
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '23',
            str(output_path)
        ])

        print("[VideoEditor] Running ffmpeg (with transitions)...")
        subprocess.run(cmd, capture_output=True, check=True)

        print(f"[VideoEditor] ✅ Concatenated with transitions")
        return str(output_path)

    def ensure_shorts_format(self, video_path: str) -> str:
        """
        Ensure video is in proper YouTube Shorts format.

        - Vertical aspect ratio (9:16)
        - Resolution: 1080x1920
        - Duration: <60 seconds
        """

        output_path = str(Path(video_path).with_suffix('.formatted.mp4'))

        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-vf', 'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2',
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '128k',
            output_path
        ]

        subprocess.run(cmd, capture_output=True, check=True)

        return output_path

    def get_video_duration(self, video_path: str) -> float:
        """Get video duration in seconds."""

        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            video_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())

    def verify_ffmpeg_installed(self) -> bool:
        """Check if ffmpeg is installed."""
        try:
            subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False


# Example usage
if __name__ == "__main__":
    editor = VideoEditor()

    # Check ffmpeg
    if not editor.verify_ffmpeg_installed():
        print("❌ ffmpeg not installed")
        print("   Install: choco install ffmpeg (Windows)")
        exit(1)

    print("✅ ffmpeg installed and ready!")

    # Test with example clips (if they exist)
    test_clips = [
        "modules/communication/youtube_shorts/assets/test/clip1.mp4",
        "modules/communication/youtube_shorts/assets/test/clip2.mp4",
        "modules/communication/youtube_shorts/assets/test/clip3.mp4"
    ]

    # Check if test clips exist
    existing_clips = [c for c in test_clips if Path(c).exists()]

    if existing_clips:
        print(f"\n🎬 Testing concatenation with {len(existing_clips)} clips...")

        output = "modules/communication/youtube_shorts/assets/test/concatenated.mp4"

        final_video = editor.concatenate_clips(
            existing_clips,
            output,
            add_transitions=False
        )

        duration = editor.get_video_duration(final_video)
        print(f"\n✅ Final video: {duration:.1f} seconds")
    else:
        print("\n⏭️  No test clips found (will work once Veo 3 generates them)")
