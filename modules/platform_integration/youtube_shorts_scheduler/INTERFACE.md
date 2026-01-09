# YouTube Shorts Scheduler - Interface Documentation

## Public API

### YouTubeShortsScheduler

Main orchestrator class for scheduling automation.

```python
class YouTubeShortsScheduler:
    def __init__(self, channel: str, driver: WebDriver = None):
        """
        Initialize scheduler for a specific channel.

        Args:
            channel: "move2japan", "undaodu", or "foundups"
            driver: Optional existing Selenium WebDriver
        """

    def gather_existing_schedule(self) -> Dict[str, int]:
        """
        Scan scheduled videos and build schedule tracker.

        Returns:
            Dict mapping date strings to video counts
            e.g., {"Jan 4, 2026": 2, "Jan 5, 2026": 1}
        """

    def get_unlisted_videos(self) -> List[Dict]:
        """
        Get all unlisted Shorts for this channel.

        Returns:
            List of dicts with video_id, title, href
        """

    def get_next_available_slot(self) -> Tuple[str, str]:
        """
        Find next available scheduling slot.

        Returns:
            (date_str, time_str) e.g., ("Jan 5, 2026", "5:00 AM")
        """

    def schedule_video(self, video_id: str, date_str: str, time_str: str) -> bool:
        """
        Schedule a specific video.

        Returns:
            True if successful
        """

    def run_scheduling_workflow(self, max_videos: int = 10) -> Dict:
        """
        Main automation loop.

        Returns:
            Summary dict with scheduled count, errors, etc.
        """
```

### ChannelConfig

Channel configuration management.

```python
CHANNELS = {
    "move2japan": {
        "id": "UC-LSSlOZwpGIRIYihaz8zCw",
        "name": "Move2Japan",
        "timezone": "Asia/Tokyo",
        "time_slots": ["5:00 AM", "11:00 AM", "5:00 PM"]
    },
    "undaodu": {
        "id": "UCfHM9Fw9HD-NwiS0seD_oIA",
        "name": "UnDaoDu",
        "timezone": "Asia/Tokyo",
        "time_slots": ["5:00 AM", "11:00 AM", "5:00 PM"]
    },
    "foundups": {
        "id": "UCSNTUXjAgpd4sgWYP0xoJgw",
        "name": "FoundUps",
        "timezone": "America/New_York",
        "time_slots": ["9:00 AM", "3:00 PM", "9:00 PM"]
    }
}
```

### ScheduleTracker

Persistent schedule state management.

```python
class ScheduleTracker:
    def __init__(self, channel_id: str):
        """Load/create schedule state for channel."""

    def get_count(self, date_str: str) -> int:
        """Get video count for a date."""

    def increment(self, date_str: str) -> None:
        """Record a scheduled video."""

    def save(self) -> None:
        """Persist to JSON."""
```

## Events

The scheduler emits events for monitoring:

- `schedule_started` - Workflow beginning
- `video_found` - Unlisted video discovered
- `video_scheduled` - Successfully scheduled
- `schedule_failed` - Scheduling error
- `schedule_completed` - Workflow finished

## Error Handling

```python
class SchedulerError(Exception):
    """Base scheduler error."""

class DOMError(SchedulerError):
    """Element not found or interaction failed."""

class AuthError(SchedulerError):
    """Not logged in or session expired."""

class QuotaError(SchedulerError):
    """Rate limited by YouTube."""
```
