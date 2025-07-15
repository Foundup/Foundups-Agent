"""
YouTube Proxy Source Module

Community engagement platform integration with WRE orchestration capabilities.
Provides unified interface for YouTube operations following WSP-42 Universal Platform Protocol.
"""

from .youtube_proxy import (
    YouTubeProxy,
    YouTubeStream,
    CommunityMetrics,
    StreamStatus,
    EngagementLevel,
    create_youtube_proxy,
    test_youtube_proxy
)

__version__ = "1.0.0"
__all__ = [
    'YouTubeProxy',
    'YouTubeStream',
    'CommunityMetrics',
    'StreamStatus',
    'EngagementLevel',
    'create_youtube_proxy',
    'test_youtube_proxy'
]
