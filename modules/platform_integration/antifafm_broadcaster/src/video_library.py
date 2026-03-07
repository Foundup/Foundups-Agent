"""
Video Library Manager for antifaFM YouTube Live Broadcaster

Manages video downloads and rotation for background visuals.
Managing Directors can add videos via `/add link [URL]` command.

WSP Compliance:
- WSP 27: Universal DAE Architecture (Phase 1: Protocol layer)
- WSP 64: Secure credential management (cookies for authenticated downloads)
- WSP 91: Observability (download logging)

Pattern: Occam's Layer - yt-dlp for downloads, simple JSON registry
"""

import json
import logging
import os
import subprocess
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)


class VideoStatus(Enum):
    """Video download/availability status."""
    PENDING = "pending"
    DOWNLOADING = "downloading"
    READY = "ready"
    ERROR = "error"
    DELETED = "deleted"


@dataclass
class VideoEntry:
    """Video library entry."""
    id: str
    source_url: str
    filename: str
    title: str
    added_by: str
    added_at: str
    status: VideoStatus = VideoStatus.PENDING
    duration_seconds: Optional[float] = None
    file_size_bytes: Optional[int] = None
    error_message: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "source_url": self.source_url,
            "filename": self.filename,
            "title": self.title,
            "added_by": self.added_by,
            "added_at": self.added_at,
            "status": self.status.value,
            "duration_seconds": self.duration_seconds,
            "file_size_bytes": self.file_size_bytes,
            "error_message": self.error_message,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "VideoEntry":
        return cls(
            id=data["id"],
            source_url=data["source_url"],
            filename=data["filename"],
            title=data.get("title", "Unknown"),
            added_by=data.get("added_by", "system"),
            added_at=data.get("added_at", datetime.now().isoformat()),
            status=VideoStatus(data.get("status", "pending")),
            duration_seconds=data.get("duration_seconds"),
            file_size_bytes=data.get("file_size_bytes"),
            error_message=data.get("error_message"),
        )


class VideoLibrary:
    """
    Manages video library for antifaFM broadcaster.

    Features:
    - Download videos from YouTube via yt-dlp
    - Store in assets/backgrounds/ folder
    - Registry tracking (video_registry.json)
    - Rotation support for visual cycling
    - Managing Director access control
    """

    # Managing Directors who can add videos
    MANAGING_DIRECTORS = {
        "012",           # Primary operator
        "undaodu",       # UnDaoDu persona
        "antifafm",      # Channel identity
        "foundups",      # FoundUps ecosystem
    }

    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize video library.

        Args:
            base_path: Base path for video storage. Defaults to module assets/backgrounds.
        """
        if base_path is None:
            base_path = Path(__file__).parent.parent / "assets" / "backgrounds"

        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

        self.registry_path = self.base_path / "video_registry.json"
        self.videos: Dict[str, VideoEntry] = {}

        self._load_registry()
        logger.info(f"[VIDEO_LIB] Initialized with {len(self.videos)} videos in {self.base_path}")

    def _load_registry(self) -> None:
        """Load video registry from JSON."""
        if self.registry_path.exists():
            try:
                with open(self.registry_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for entry in data.get("videos", []):
                    video = VideoEntry.from_dict(entry)
                    self.videos[video.id] = video
                logger.debug(f"[VIDEO_LIB] Loaded {len(self.videos)} videos from registry")
            except Exception as e:
                logger.error(f"[VIDEO_LIB] Failed to load registry: {e}")

    def _save_registry(self) -> None:
        """Save video registry to JSON."""
        try:
            data = {
                "last_updated": datetime.now().isoformat(),
                "videos": [v.to_dict() for v in self.videos.values()],
            }
            with open(self.registry_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            logger.debug(f"[VIDEO_LIB] Saved {len(self.videos)} videos to registry")
        except Exception as e:
            logger.error(f"[VIDEO_LIB] Failed to save registry: {e}")

    def _generate_id(self, url: str) -> str:
        """Generate unique ID from URL."""
        return hashlib.sha256(url.encode()).hexdigest()[:12]

    def _is_managing_director(self, username: str) -> bool:
        """Check if user is a Managing Director."""
        return username.lower() in [md.lower() for md in self.MANAGING_DIRECTORS]

    def add_video(
        self,
        url: str,
        added_by: str,
        title: Optional[str] = None,
        download_now: bool = True,
    ) -> Dict[str, Any]:
        """
        Add video to library via /add link command.

        Args:
            url: YouTube video URL (supports shorts, regular videos, etc.)
            added_by: Username of person adding the video
            title: Optional title override
            download_now: Download immediately (True) or queue for later

        Returns:
            dict: Result with success status, video_id, message
        """
        # Check permissions
        if not self._is_managing_director(added_by):
            return {
                "success": False,
                "message": f"Permission denied: {added_by} is not a Managing Director",
                "allowed_directors": list(self.MANAGING_DIRECTORS),
            }

        # Normalize URL
        normalized_url = self._normalize_youtube_url(url)
        if not normalized_url:
            return {
                "success": False,
                "message": f"Invalid YouTube URL: {url}",
            }

        # Generate ID
        video_id = self._generate_id(normalized_url)

        # Check for duplicates
        if video_id in self.videos:
            existing = self.videos[video_id]
            return {
                "success": False,
                "message": f"Video already in library: {existing.filename}",
                "video_id": video_id,
                "status": existing.status.value,
            }

        # Create entry
        filename = f"video_{video_id}.mp4"
        entry = VideoEntry(
            id=video_id,
            source_url=normalized_url,
            filename=filename,
            title=title or f"Video {video_id[:8]}",
            added_by=added_by,
            added_at=datetime.now().isoformat(),
            status=VideoStatus.PENDING,
        )

        self.videos[video_id] = entry
        self._save_registry()

        logger.info(f"[VIDEO_LIB] Added video {video_id} from {added_by}: {normalized_url}")

        # Download if requested
        if download_now:
            download_result = self.download_video(video_id)
            return {
                "success": download_result["success"],
                "message": download_result["message"],
                "video_id": video_id,
                "filename": filename,
                "download_result": download_result,
            }

        return {
            "success": True,
            "message": f"Video queued for download: {filename}",
            "video_id": video_id,
            "filename": filename,
            "status": "pending",
        }

    def download_video(self, video_id: str) -> Dict[str, Any]:
        """
        Download video using yt-dlp.

        Args:
            video_id: Video ID to download

        Returns:
            dict: Download result
        """
        if video_id not in self.videos:
            return {"success": False, "message": f"Video not found: {video_id}"}

        entry = self.videos[video_id]

        if entry.status == VideoStatus.READY:
            output_path = self.base_path / entry.filename
            if output_path.exists():
                return {
                    "success": True,
                    "message": f"Video already downloaded: {entry.filename}",
                    "path": str(output_path),
                }

        entry.status = VideoStatus.DOWNLOADING
        self._save_registry()

        output_path = self.base_path / entry.filename

        logger.info(f"[VIDEO_LIB] Downloading {entry.source_url} -> {output_path}")

        try:
            # Build yt-dlp command
            cmd = [
                "yt-dlp",
                "-f", "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best",
                "--merge-output-format", "mp4",
                "-o", str(output_path),
                "--no-playlist",
                "--quiet",
                "--progress",
            ]

            # Check for cookies file (for authenticated downloads)
            cookies_path = Path(os.getenv("YTDLP_COOKIES_PATH", ""))
            if cookies_path.exists():
                cmd.extend(["--cookies", str(cookies_path)])
                logger.debug(f"[VIDEO_LIB] Using cookies from {cookies_path}")

            cmd.append(entry.source_url)

            # Execute download
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout
            )

            if result.returncode == 0 and output_path.exists():
                # Get file info
                file_stat = output_path.stat()
                entry.file_size_bytes = file_stat.st_size
                entry.status = VideoStatus.READY
                entry.error_message = None
                self._save_registry()

                logger.info(f"[VIDEO_LIB] Downloaded {entry.filename} ({entry.file_size_bytes / 1024 / 1024:.1f} MB)")

                return {
                    "success": True,
                    "message": f"Downloaded: {entry.filename}",
                    "path": str(output_path),
                    "size_mb": entry.file_size_bytes / 1024 / 1024,
                }
            else:
                error_msg = result.stderr[:500] if result.stderr else "Unknown error"
                entry.status = VideoStatus.ERROR
                entry.error_message = error_msg
                self._save_registry()

                logger.error(f"[VIDEO_LIB] Download failed: {error_msg}")

                # Check for 403 Forbidden - YouTube auth required
                if "403" in error_msg or "Forbidden" in error_msg:
                    return {
                        "success": False,
                        "message": "YouTube blocked download (403 Forbidden). Manual download required.",
                        "video_id": video_id,
                        "manual_instructions": [
                            "1. Open the video URL in browser",
                            "2. Right-click -> Save video as...",
                            "3. Save to: assets/backgrounds/ folder",
                            "4. Or use: yt-dlp --cookies-from-browser chrome [URL]",
                        ],
                        "target_folder": str(self.base_path),
                    }

                return {
                    "success": False,
                    "message": f"Download failed: {error_msg}",
                    "video_id": video_id,
                }

        except subprocess.TimeoutExpired:
            entry.status = VideoStatus.ERROR
            entry.error_message = "Download timed out (10 min limit)"
            self._save_registry()

            return {
                "success": False,
                "message": "Download timed out",
                "video_id": video_id,
            }
        except FileNotFoundError:
            entry.status = VideoStatus.ERROR
            entry.error_message = "yt-dlp not installed"
            self._save_registry()

            return {
                "success": False,
                "message": "yt-dlp not installed. Install via: pip install yt-dlp",
                "video_id": video_id,
            }
        except Exception as e:
            entry.status = VideoStatus.ERROR
            entry.error_message = str(e)
            self._save_registry()

            logger.error(f"[VIDEO_LIB] Download error: {e}")

            return {
                "success": False,
                "message": f"Download error: {e}",
                "video_id": video_id,
            }

    def _normalize_youtube_url(self, url: str) -> Optional[str]:
        """Normalize YouTube URL to standard format."""
        import re

        # Patterns for YouTube URLs (flexible matching)
        patterns = [
            # Shorts (with or without www, with optional parameters)
            r'(?:www\.)?youtube\.com/shorts/([a-zA-Z0-9_-]{11})',
            r'youtu\.be/([a-zA-Z0-9_-]{11})',
            # Regular videos
            r'(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
            r'(?:www\.)?youtube\.com/v/([a-zA-Z0-9_-]{11})',
            r'(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})',
            # Mobile URLs
            r'm\.youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)
                return f"https://www.youtube.com/watch?v={video_id}"

        return None

    def list_videos(self, status_filter: Optional[VideoStatus] = None) -> List[VideoEntry]:
        """List videos in library, optionally filtered by status."""
        videos = list(self.videos.values())
        if status_filter:
            videos = [v for v in videos if v.status == status_filter]
        return sorted(videos, key=lambda v: v.added_at, reverse=True)

    def get_ready_videos(self) -> List[Path]:
        """Get list of ready video paths for rotation."""
        ready = []
        for entry in self.videos.values():
            if entry.status == VideoStatus.READY:
                path = self.base_path / entry.filename
                if path.exists():
                    ready.append(path)
        return ready

    def get_random_video(self) -> Optional[Path]:
        """Get random video from ready videos for rotation."""
        import random
        ready = self.get_ready_videos()
        if ready:
            return random.choice(ready)
        return None

    def remove_video(self, video_id: str, added_by: str, delete_file: bool = True) -> Dict[str, Any]:
        """
        Remove video from library.

        Args:
            video_id: Video ID to remove
            added_by: Username requesting removal (must be MD)
            delete_file: Also delete the file

        Returns:
            dict: Result
        """
        if not self._is_managing_director(added_by):
            return {
                "success": False,
                "message": f"Permission denied: {added_by} is not a Managing Director",
            }

        if video_id not in self.videos:
            return {
                "success": False,
                "message": f"Video not found: {video_id}",
            }

        entry = self.videos[video_id]

        if delete_file:
            file_path = self.base_path / entry.filename
            if file_path.exists():
                try:
                    file_path.unlink()
                    logger.info(f"[VIDEO_LIB] Deleted file: {file_path}")
                except Exception as e:
                    logger.error(f"[VIDEO_LIB] Failed to delete file: {e}")

        del self.videos[video_id]
        self._save_registry()

        logger.info(f"[VIDEO_LIB] Removed video {video_id} by {added_by}")

        return {
            "success": True,
            "message": f"Removed video: {entry.filename}",
            "video_id": video_id,
        }

    def register_local_video(
        self,
        filename: str,
        added_by: str,
        source_url: Optional[str] = None,
        title: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Register a manually downloaded video that's already in the assets folder.

        Use this when:
        - yt-dlp fails due to 403 errors
        - Video was manually downloaded via browser
        - Video was transferred from another source

        Args:
            filename: Name of video file in assets/backgrounds/
            added_by: Username registering the video (must be MD)
            source_url: Original YouTube URL (optional)
            title: Video title (optional)

        Returns:
            dict: Result
        """
        if not self._is_managing_director(added_by):
            return {
                "success": False,
                "message": f"Permission denied: {added_by} is not a Managing Director",
            }

        file_path = self.base_path / filename
        if not file_path.exists():
            return {
                "success": False,
                "message": f"File not found: {file_path}",
                "expected_location": str(self.base_path),
            }

        # Check if already registered
        for v in self.videos.values():
            if v.filename == filename:
                return {
                    "success": False,
                    "message": f"Video already registered: {v.id}",
                    "video_id": v.id,
                }

        # Generate ID from filename or URL
        video_id = self._generate_id(source_url or filename)

        # Get file info
        file_stat = file_path.stat()

        entry = VideoEntry(
            id=video_id,
            source_url=source_url or f"local://{filename}",
            filename=filename,
            title=title or filename,
            added_by=added_by,
            added_at=datetime.now().isoformat(),
            status=VideoStatus.READY,
            file_size_bytes=file_stat.st_size,
        )

        self.videos[video_id] = entry
        self._save_registry()

        logger.info(f"[VIDEO_LIB] Registered local video: {filename} ({file_stat.st_size / 1024 / 1024:.1f} MB)")

        return {
            "success": True,
            "message": f"Registered: {filename}",
            "video_id": video_id,
            "size_mb": file_stat.st_size / 1024 / 1024,
        }

    def scan_for_unregistered_videos(self, added_by: str) -> Dict[str, Any]:
        """
        Scan assets folder for videos not in registry and register them.

        Args:
            added_by: Username performing scan (must be MD)

        Returns:
            dict: Scan results
        """
        if not self._is_managing_director(added_by):
            return {
                "success": False,
                "message": f"Permission denied: {added_by} is not a Managing Director",
            }

        video_extensions = {'.mp4', '.webm', '.mkv', '.avi', '.mov'}
        registered_filenames = {v.filename for v in self.videos.values()}
        new_videos = []

        for file_path in self.base_path.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in video_extensions:
                if file_path.name not in registered_filenames:
                    result = self.register_local_video(file_path.name, added_by)
                    if result["success"]:
                        new_videos.append(file_path.name)

        return {
            "success": True,
            "message": f"Registered {len(new_videos)} new videos",
            "new_videos": new_videos,
            "total_videos": len(self.videos),
        }

    def get_status(self) -> Dict[str, Any]:
        """Get library status."""
        ready = [v for v in self.videos.values() if v.status == VideoStatus.READY]
        pending = [v for v in self.videos.values() if v.status == VideoStatus.PENDING]
        errors = [v for v in self.videos.values() if v.status == VideoStatus.ERROR]

        total_size = sum(v.file_size_bytes or 0 for v in ready)

        return {
            "total_videos": len(self.videos),
            "ready": len(ready),
            "pending": len(pending),
            "errors": len(errors),
            "total_size_mb": total_size / 1024 / 1024,
            "storage_path": str(self.base_path),
            "managing_directors": list(self.MANAGING_DIRECTORS),
        }


def handle_add_link_command(url: str, username: str) -> str:
    """
    Handle /add link command from Managing Directors.

    Args:
        url: YouTube URL to add
        username: User issuing command

    Returns:
        str: Response message
    """
    library = VideoLibrary()
    result = library.add_video(url, username)

    if result["success"]:
        return f"[VIDEO] Added: {result.get('filename', 'video')} - {result.get('message', 'Success')}"
    else:
        return f"[VIDEO] Failed: {result.get('message', 'Unknown error')}"


# CLI testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    print("\n[TEST] Video Library Manager")
    print("=" * 50)

    library = VideoLibrary()

    print(f"\nStatus: {json.dumps(library.get_status(), indent=2)}")

    # Test add (without download for quick test)
    test_url = "https://www.youtube.com/shorts/J9CmL54rhU8"
    result = library.add_video(test_url, "012", download_now=False)
    print(f"\nAdd result: {json.dumps(result, indent=2)}")

    print(f"\nUpdated status: {json.dumps(library.get_status(), indent=2)}")
