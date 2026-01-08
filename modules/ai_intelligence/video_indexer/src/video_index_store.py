"""
Video Index Store - JSON artifact storage for video index data.

WSP Compliance:
    - WSP 72: Module Independence
    - WSP 84: Code Reuse (same format as video_index/)

Purpose:
    Persist indexed video data as JSON artifacts.
    Compatible with existing video_index/ structure.
"""

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class IndexData:
    """
    Complete index data for a video.
    """
    video_id: str
    channel: str
    title: str
    duration: float
    indexed_at: str  # ISO format
    audio: Dict[str, Any]  # Transcript segments, quotes, topics
    visual: Dict[str, Any]  # Keyframes, shots
    moments: List[Dict[str, Any]]  # Aligned moments
    clips: List[Dict[str, Any]]  # Clip candidates
    metadata: Dict[str, Any]  # Additional metadata


# =============================================================================
# Video Index Store
# =============================================================================

class VideoIndexStore:
    """
    JSON artifact storage for video index data.

    Example:
        >>> store = VideoIndexStore()
        >>> store.save_index("abc123", index_data)
        >>> loaded = store.load_index("abc123")
    """

    def __init__(self, base_path: str = "video_index"):
        """
        Initialize store.

        Args:
            base_path: Base directory for JSON artifacts
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"[VIDEO-INDEX-STORE] Initialized at: {self.base_path}")

    def save_index(self, video_id: str, index_data: IndexData) -> str:
        """
        Save index data to JSON file.

        Args:
            video_id: YouTube video ID
            index_data: IndexData object to save

        Returns:
            Path to saved file
        """
        file_path = self.base_path / f"{video_id}.json"

        # Convert dataclass to dict
        if isinstance(index_data, IndexData):
            data = asdict(index_data)
        else:
            data = index_data

        # Add save timestamp
        data["saved_at"] = datetime.now().isoformat()

        # Write JSON
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"[VIDEO-INDEX-STORE] Saved: {file_path}")
        return str(file_path)

    def load_index(self, video_id: str) -> Optional[IndexData]:
        """
        Load index data from JSON file.

        Args:
            video_id: YouTube video ID

        Returns:
            IndexData if exists, None otherwise
        """
        file_path = self.base_path / f"{video_id}.json"

        if not file_path.exists():
            logger.debug(f"[VIDEO-INDEX-STORE] Not found: {video_id}")
            return None

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        logger.info(f"[VIDEO-INDEX-STORE] Loaded: {video_id}")

        return IndexData(
            video_id=data.get("video_id", video_id),
            channel=data.get("channel", "unknown"),
            title=data.get("title", ""),
            duration=data.get("duration", 0),
            indexed_at=data.get("indexed_at", ""),
            audio=data.get("audio", {}),
            visual=data.get("visual", {}),
            moments=data.get("moments", []),
            clips=data.get("clips", []),
            metadata=data.get("metadata", {}),
        )

    def list_indexed(self, channel: Optional[str] = None) -> List[str]:
        """
        List all indexed video IDs.

        Args:
            channel: Optional channel filter

        Returns:
            List of video IDs
        """
        video_ids = []

        for file_path in self.base_path.glob("*.json"):
            video_id = file_path.stem

            if channel:
                # Load and check channel
                index = self.load_index(video_id)
                if index and index.channel == channel:
                    video_ids.append(video_id)
            else:
                video_ids.append(video_id)

        logger.info(f"[VIDEO-INDEX-STORE] Found {len(video_ids)} indexed videos")
        return video_ids

    def delete_index(self, video_id: str) -> bool:
        """
        Delete index for video.

        Args:
            video_id: YouTube video ID

        Returns:
            True if deleted, False if not found
        """
        file_path = self.base_path / f"{video_id}.json"

        if not file_path.exists():
            return False

        file_path.unlink()
        logger.info(f"[VIDEO-INDEX-STORE] Deleted: {video_id}")
        return True

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get storage statistics.

        Returns:
            Dict with counts and sizes
        """
        total_files = 0
        total_size = 0
        channels = {}

        for file_path in self.base_path.glob("*.json"):
            total_files += 1
            total_size += file_path.stat().st_size

            # Count by channel
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    channel = data.get("channel", "unknown")
                    channels[channel] = channels.get(channel, 0) + 1
            except Exception:
                pass

        return {
            "total_files": total_files,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "channels": channels,
            "base_path": str(self.base_path),
        }


# =============================================================================
# Quick Test
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("Video Index Store Test")
    print("=" * 60)

    # Create test store in temp directory
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        store = VideoIndexStore(base_path=tmpdir)

        # Create test data
        test_data = IndexData(
            video_id="test123",
            channel="move2japan",
            title="Test Video",
            duration=120.5,
            indexed_at=datetime.now().isoformat(),
            audio={
                "segments": [
                    {"start": 0, "end": 10, "text": "Hello world"}
                ],
                "quotes": [],
            },
            visual={
                "keyframes": 24,
                "shots": 5,
            },
            moments=[
                {"start": 0, "end": 10, "engagement": 0.8}
            ],
            clips=[],
            metadata={"source": "test"},
        )

        # Save
        path = store.save_index("test123", test_data)
        print(f"Saved to: {path}")

        # Load
        loaded = store.load_index("test123")
        print(f"Loaded: {loaded.title}")

        # List
        indexed = store.list_indexed()
        print(f"Indexed: {indexed}")

        # Stats
        stats = store.get_statistics()
        print(f"Stats: {stats}")
