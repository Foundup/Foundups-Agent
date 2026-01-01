"""
YouTube Shorts Scheduler Module

WSP 80 DAE pattern for automated Shorts scheduling across channels.
"""

from .scheduler import YouTubeShortsScheduler, run_scheduler_dae
from .channel_config import CHANNELS, get_channel_config, get_studio_urls
from .schedule_tracker import ScheduleTracker
from .content_generator import generate_clickbait_title, get_standard_description
from .dom_automation import YouTubeStudioDOM, DOMSelectors

__all__ = [
    # Main classes
    "YouTubeShortsScheduler",
    "run_scheduler_dae",
    # Channel config
    "CHANNELS",
    "get_channel_config",
    "get_studio_urls",
    # Schedule tracking
    "ScheduleTracker",
    # Content generation
    "generate_clickbait_title",
    "get_standard_description",
    # DOM automation
    "YouTubeStudioDOM",
    "DOMSelectors",
]
