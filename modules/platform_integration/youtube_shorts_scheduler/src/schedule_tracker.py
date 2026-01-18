"""
Schedule Tracker for YouTube Shorts Scheduler

Persistent state management for tracking scheduled videos per date.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Default storage location
TRACKER_DIR = Path(__file__).parent.parent / "memory"


class ScheduleTracker:
    """
    Tracks scheduled videos per date with JSON persistence.

    Implements smart slot allocation:
    - Max 3 videos per day
    - Time slots separated by ~6 hours
    - Prioritizes empty dates over partially filled
    """

    def __init__(self, channel_id: str, storage_dir: Optional[Path] = None):
        """
        Initialize tracker for a channel.

        Args:
            channel_id: YouTube channel ID
            storage_dir: Optional custom storage directory
        """
        self.channel_id = channel_id
        self.storage_dir = storage_dir or TRACKER_DIR
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.tracker_file = self.storage_dir / f"schedule_{channel_id}.json"
        self.schedule: Dict[str, int] = {}  # {date_str: count}
        self.video_ids: Dict[str, List[str]] = {}  # {date_str: [video_ids]}

        self._load()

    def _load(self):
        """Load schedule from JSON file."""
        if self.tracker_file.exists():
            try:
                with open(self.tracker_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.schedule = data.get("schedule", {})
                    self.video_ids = data.get("video_ids", {})
                    logger.info(f"[TRACKER] Loaded {len(self.schedule)} dates for {self.channel_id}")
            except Exception as e:
                logger.error(f"[TRACKER] Error loading: {e}")
                self.schedule = {}
                self.video_ids = {}
        else:
            logger.info(f"[TRACKER] New tracker for {self.channel_id}")

    def save(self):
        """Persist schedule to JSON file."""
        try:
            data = {
                "channel_id": self.channel_id,
                "last_updated": datetime.now().isoformat(),
                "schedule": self.schedule,
                "video_ids": self.video_ids,
            }
            with open(self.tracker_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            logger.info(f"[TRACKER] Saved {len(self.schedule)} dates")
        except Exception as e:
            logger.error(f"[TRACKER] Error saving: {e}")

    def get_count(self, date_str: str) -> int:
        """
        Get video count for a date.

        Args:
            date_str: Date string like "Jan 5, 2026"

        Returns:
            Number of videos scheduled for that date
        """
        return self.schedule.get(date_str, 0)

    def increment(self, date_str: str, video_id: Optional[str] = None):
        """
        Record a scheduled video.

        Args:
            date_str: Date string like "Jan 5, 2026"
            video_id: Optional video ID to track
        """
        self.schedule[date_str] = self.schedule.get(date_str, 0) + 1

        if video_id:
            if date_str not in self.video_ids:
                self.video_ids[date_str] = []
            self.video_ids[date_str].append(video_id)

        self.save()

    def set_count(self, date_str: str, count: int):
        """
        Set video count for a date (used when scanning existing schedule).

        Args:
            date_str: Date string
            count: Number of videos
        """
        self.schedule[date_str] = count
        # Don't save immediately - batch updates expected

    def get_next_available_slot(
        self,
        time_slots: List[str],
        max_per_day: int = 3,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Optional[Tuple[str, str]]:
        """
        Find next available scheduling slot.

        Args:
            time_slots: List of time strings ["5:00 AM", "11:00 AM", "5:00 PM"]
            max_per_day: Maximum videos per day
            start_date: Start of scheduling window (default: tomorrow)
            end_date: End of scheduling window (default: 60 days out)

        Returns:
            (date_str, time_str) tuple or None if all slots filled
        """
        if start_date is None:
            start_date = datetime.now() + timedelta(days=1)
        if end_date is None:
            end_date = start_date + timedelta(days=60)

        current = start_date

        while current <= end_date:
            # Format date like YouTube Studio shows it: "Jan 5, 2026"
            # Windows-safe formatting (avoid %-d which is unsupported on Windows)
            date_str = f"{current.strftime('%b')} {current.day}, {current.year}"

            count = self.get_count(date_str)

            if count < max_per_day:
                # Determine which time slot
                time_slot = time_slots[count] if count < len(time_slots) else time_slots[-1]
                return (date_str, time_slot)

            current += timedelta(days=1)

        logger.warning("[TRACKER] All slots filled in date range")
        return None

    def get_summary(self) -> Dict:
        """
        Get summary statistics.

        Returns:
            Dict with total_scheduled, dates_with_videos, available_slots
        """
        total = sum(self.schedule.values())
        dates_with_videos = len([d for d, c in self.schedule.items() if c > 0])

        return {
            "channel_id": self.channel_id,
            "total_scheduled": total,
            "dates_with_videos": dates_with_videos,
            "schedule": self.schedule,
        }

    def sync_from_youtube(self, scheduled_videos: List[Dict]):
        """
        Sync tracker with actual YouTube schedule.

        Args:
            scheduled_videos: List of dicts with date key from DOM scrape
        """
        # Reset current schedule
        self.schedule = {}
        self.video_ids = {}

        # Rebuild from YouTube data
        for video in scheduled_videos:
            date_str = video.get("date", "")
            video_id = video.get("video_id", "")

            if date_str:
                self.schedule[date_str] = self.schedule.get(date_str, 0) + 1

                if video_id:
                    if date_str not in self.video_ids:
                        self.video_ids[date_str] = []
                    self.video_ids[date_str].append(video_id)

        self.save()
        logger.info(f"[TRACKER] Synced {len(scheduled_videos)} videos from YouTube")
