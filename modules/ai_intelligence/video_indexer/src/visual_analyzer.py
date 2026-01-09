"""
Visual Analyzer - Shot detection, faces, objects.

WSP Compliance:
    - WSP 72: Module Independence
    - WSP 27: DAE Architecture (frame extraction pipeline)
    - WSP 84: Code Reuse (reuses yt-dlp pattern from youtube_live_audio)
    - WSP 91: DAE Observability (telemetry integration)

Dependencies:
    - opencv-python: Frame extraction
    - ffmpeg-python: Video processing
    - yt-dlp: YouTube video download (via youtube_live_audio pattern)

Integration:
    - Wraps VideoArchiveExtractor pattern for video download
    - Integrates with IndexerTelemetry for observability
    - Uses video cache at memory/video_cache/
"""

import logging
import subprocess
import tempfile
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class Keyframe:
    """Single keyframe from video."""
    frame_number: int
    timestamp: float
    image_path: Optional[str] = None
    histogram: Optional[List[float]] = None


@dataclass
class Shot:
    """Single shot (scene) in video."""
    start_frame: int
    end_frame: int
    start_time: float
    end_time: float
    duration: float
    keyframe: Optional[Keyframe] = None


@dataclass
class FrameAnalysis:
    """Analysis results for single frame."""
    timestamp: float
    faces: List[dict]  # {"x": int, "y": int, "w": int, "h": int}
    objects: List[dict]  # {"label": str, "confidence": float, "bbox": dict}
    text: List[str]  # OCR results
    dominant_colors: List[str]


@dataclass
class VisualResult:
    """Complete visual analysis result for video_indexer pipeline."""
    keyframes: List[Keyframe]
    shots: List[Shot]
    total_frames: int
    duration: float
    fps: float
    resolution: tuple  # (width, height)
    face_count: int
    video_path: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for pipeline consumption."""
        return {
            "keyframes": [asdict(k) for k in self.keyframes],
            "shots": [asdict(s) for s in self.shots],
            "total_frames": self.total_frames,
            "duration": self.duration,
            "fps": self.fps,
            "resolution": self.resolution,
            "face_count": self.face_count,
            "video_path": self.video_path,
        }


# =============================================================================
# Visual Analyzer
# =============================================================================

class VisualAnalyzer:
    """
    Visual content analysis: shots, faces, objects.

    Supports both local files and YouTube video IDs.
    Integrates with VideoArchiveExtractor pattern for yt-dlp download (WSP 84).

    Example:
        >>> analyzer = VisualAnalyzer()
        >>> # Analyze YouTube video
        >>> result = analyzer.analyze_video("abc123")  # YouTube video ID
        >>> # Analyze local file
        >>> keyframes = analyzer.extract_keyframes("video.mp4")
        >>> shots = analyzer.detect_shots("video.mp4")
    """

    def __init__(
        self,
        frame_interval: float = 1.0,
        enable_face_detection: bool = True,
        cache_dir: Optional[str] = None,
    ):
        """
        Initialize visual analyzer.

        Args:
            frame_interval: Seconds between frame samples
            enable_face_detection: Enable face detection
            cache_dir: Directory for video cache (default: memory/video_cache)
        """
        self.frame_interval = frame_interval
        self.enable_face_detection = enable_face_detection
        self.cache_dir = Path(cache_dir) if cache_dir else Path("memory/video_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Lazy-loaded
        self._cv2 = None
        self._face_cascade = None
        self._yt_dlp = None

        logger.info(f"[VISUAL-ANALYZER] Initialized (interval={frame_interval}s, faces={enable_face_detection})")

    def _get_yt_dlp(self):
        """Lazy load yt-dlp (WSP 84 - reuse youtube_live_audio pattern)."""
        if self._yt_dlp is not None:
            return self._yt_dlp

        try:
            import yt_dlp
            self._yt_dlp = yt_dlp
            logger.info("[VISUAL-ANALYZER] yt-dlp loaded")
            return self._yt_dlp
        except ImportError:
            logger.error("[VISUAL-ANALYZER] yt-dlp not installed: pip install yt-dlp")
            raise

    def download_video(
        self,
        video_id: str,
        use_cache: bool = True,
        max_quality: str = "720p",
    ) -> Optional[str]:
        """
        Download YouTube video for visual analysis.

        Reuses yt-dlp pattern from youtube_live_audio (WSP 84).

        Args:
            video_id: YouTube video ID
            use_cache: Use cached video if available
            max_quality: Maximum quality (360p, 480p, 720p, 1080p)

        Returns:
            Path to downloaded video file, or None on failure
        """
        yt_dlp = self._get_yt_dlp()

        # Check cache
        cache_path = self.cache_dir / f"{video_id}.mp4"
        if use_cache and cache_path.exists():
            logger.info(f"[VISUAL-ANALYZER] Using cached video: {video_id}")
            return str(cache_path)

        video_url = f"https://www.youtube.com/watch?v={video_id}"
        logger.info(f"[VISUAL-ANALYZER] Downloading video: {video_id}")

        try:
            # Map quality to height
            quality_map = {
                "360p": 360,
                "480p": 480,
                "720p": 720,
                "1080p": 1080,
            }
            max_height = quality_map.get(max_quality, 720)

            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                # Video format with height limit
                'format': f'bestvideo[height<={max_height}][ext=mp4]+bestaudio[ext=m4a]/best[height<={max_height}][ext=mp4]/best',
                'outtmpl': str(cache_path),
                'merge_output_format': 'mp4',
                # Use browser cookies for authenticated content
                'cookiesfrombrowser': ('chrome',),
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])

            if cache_path.exists():
                logger.info(f"[VISUAL-ANALYZER] Video downloaded: {video_id} ({cache_path.stat().st_size / 1024 / 1024:.1f}MB)")
                return str(cache_path)
            else:
                logger.error(f"[VISUAL-ANALYZER] Download completed but file not found: {cache_path}")
                return None

        except Exception as e:
            logger.error(f"[VISUAL-ANALYZER] Failed to download video {video_id}: {e}")
            return None

    def analyze_video(self, video_id: str, use_cache: bool = True) -> VisualResult:
        """
        Complete visual analysis pipeline for YouTube video.

        Integrates with video_indexer orchestrator.

        Args:
            video_id: YouTube video ID
            use_cache: Use cached video if available

        Returns:
            VisualResult with keyframes, shots, and metadata
        """
        logger.info(f"[VISUAL-ANALYZER] Analyzing video: {video_id}")

        # Download video
        video_path = self.download_video(video_id, use_cache=use_cache)
        if not video_path:
            logger.warning(f"[VISUAL-ANALYZER] Could not download video: {video_id}")
            return VisualResult(
                keyframes=[],
                shots=[],
                total_frames=0,
                duration=0,
                fps=0,
                resolution=(0, 0),
                face_count=0,
                video_path=None,
            )

        # Extract video metadata
        self._load_cv2()
        cv2 = self._cv2
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            logger.error(f"[VISUAL-ANALYZER] Could not open video: {video_path}")
            return VisualResult(
                keyframes=[],
                shots=[],
                total_frames=0,
                duration=0,
                fps=0,
                resolution=(0, 0),
                face_count=0,
                video_path=video_path,
            )

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = total_frames / fps if fps > 0 else 0
        cap.release()

        # Extract keyframes and detect shots
        keyframes = self.extract_keyframes(video_path)
        shots = self.detect_shots(video_path)

        # Count faces across keyframes (sample-based)
        face_count = self._count_faces_sample(video_path, sample_count=10)

        result = VisualResult(
            keyframes=keyframes,
            shots=shots,
            total_frames=total_frames,
            duration=duration,
            fps=fps,
            resolution=(width, height),
            face_count=face_count,
            video_path=video_path,
        )

        logger.info(f"[VISUAL-ANALYZER] Analysis complete: {len(keyframes)} keyframes, {len(shots)} shots, {face_count} faces")
        return result

    def _count_faces_sample(self, video_path: str, sample_count: int = 10) -> int:
        """Count faces by sampling frames throughout video."""
        if not self.enable_face_detection:
            return 0

        self._load_cv2()
        cv2 = self._cv2

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return 0

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        step = max(1, total_frames // sample_count)

        face_count = 0
        for i in range(0, total_frames, step):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            if not ret:
                continue

            analysis = self.analyze_frame(frame)
            face_count += len(analysis.faces)

        cap.release()
        return face_count

    def _load_cv2(self):
        """Lazy load OpenCV."""
        if self._cv2 is not None:
            return

        try:
            import cv2
            self._cv2 = cv2
            logger.info("[VISUAL-ANALYZER] OpenCV loaded")

            if self.enable_face_detection:
                # Load face cascade
                cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
                self._face_cascade = cv2.CascadeClassifier(cascade_path)

        except ImportError:
            logger.error("[VISUAL-ANALYZER] opencv-python not installed: pip install opencv-python")
            raise

    def extract_keyframes(self, video_path: str) -> List[Keyframe]:
        """
        Extract representative frames from video.

        Args:
            video_path: Path to video file

        Returns:
            List of Keyframe objects
        """
        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")

        logger.info(f"[VISUAL-ANALYZER] Extracting keyframes: {video_path.name}")

        self._load_cv2()
        cv2 = self._cv2

        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_skip = int(fps * self.frame_interval)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        keyframes = []
        frame_num = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_num % frame_skip == 0:
                timestamp = frame_num / fps
                hist = cv2.calcHist([frame], [0], None, [256], [0, 256])
                hist = hist.flatten().tolist()

                keyframes.append(
                    Keyframe(
                        frame_number=frame_num,
                        timestamp=timestamp,
                        histogram=hist[:16],  # Simplified
                    )
                )

            frame_num += 1

        cap.release()
        logger.info(f"[VISUAL-ANALYZER] Extracted {len(keyframes)} keyframes")
        return keyframes

    def detect_shots(
        self,
        video_path: str,
        threshold: float = 0.3,
    ) -> List[Shot]:
        """
        Detect shot boundaries in video.

        Args:
            video_path: Path to video file
            threshold: Scene change threshold (0-1)

        Returns:
            List of Shot objects
        """
        logger.info(f"[VISUAL-ANALYZER] Detecting shots: {Path(video_path).name}")

        keyframes = self.extract_keyframes(video_path)
        if len(keyframes) < 2:
            return []

        self._load_cv2()

        shots = []
        shot_start = keyframes[0]

        for i in range(1, len(keyframes)):
            prev = keyframes[i - 1]
            curr = keyframes[i]

            # Compare histograms
            diff = self._histogram_diff(prev.histogram, curr.histogram)

            if diff > threshold:
                # Shot boundary detected
                shots.append(
                    Shot(
                        start_frame=shot_start.frame_number,
                        end_frame=prev.frame_number,
                        start_time=shot_start.timestamp,
                        end_time=prev.timestamp,
                        duration=prev.timestamp - shot_start.timestamp,
                        keyframe=shot_start,
                    )
                )
                shot_start = curr

        # Add final shot
        if keyframes:
            shots.append(
                Shot(
                    start_frame=shot_start.frame_number,
                    end_frame=keyframes[-1].frame_number,
                    start_time=shot_start.timestamp,
                    end_time=keyframes[-1].timestamp,
                    duration=keyframes[-1].timestamp - shot_start.timestamp,
                    keyframe=shot_start,
                )
            )

        logger.info(f"[VISUAL-ANALYZER] Detected {len(shots)} shots")
        return shots

    def _histogram_diff(self, hist1: List[float], hist2: List[float]) -> float:
        """Calculate normalized histogram difference."""
        if not hist1 or not hist2:
            return 0.0

        diff = sum(abs(a - b) for a, b in zip(hist1, hist2))
        max_val = max(sum(hist1), sum(hist2), 1)
        return diff / max_val

    def analyze_frame(self, frame) -> FrameAnalysis:
        """
        Analyze single frame for faces, objects, text.

        Args:
            frame: OpenCV frame (numpy array)

        Returns:
            FrameAnalysis with detected elements
        """
        self._load_cv2()
        cv2 = self._cv2

        faces = []
        if self.enable_face_detection and self._face_cascade is not None:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            detected = self._face_cascade.detectMultiScale(gray, 1.1, 4)
            for x, y, w, h in detected:
                faces.append({"x": int(x), "y": int(y), "w": int(w), "h": int(h)})

        return FrameAnalysis(
            timestamp=0,
            faces=faces,
            objects=[],  # TODO: Object detection
            text=[],  # TODO: OCR
            dominant_colors=[],  # TODO: Color analysis
        )


# =============================================================================
# Quick Test
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("Visual Analyzer Test")
    print("=" * 60)

    analyzer = VisualAnalyzer(frame_interval=2.0, enable_face_detection=True)
    print(f"Frame interval: {analyzer.frame_interval}s")
    print(f"Face detection: {analyzer.enable_face_detection}")
