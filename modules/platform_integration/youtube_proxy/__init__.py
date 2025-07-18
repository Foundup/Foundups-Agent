"""
YouTube Proxy Module

Community engagement platform integration with WRE orchestration capabilities.
Acts as unified, WSP-compliant interface for all YouTube operations following
WSP-42 Universal Platform Protocol for community engagement automation.

This module orchestrates underlying authentication and communication modules
with WRE integration for autonomous development.
"""

from .src import (
    YouTubeProxy,
    YouTubeStream,
    CommunityMetrics,
    StreamStatus,
    EngagementLevel,
    create_youtube_proxy,
    test_youtube_proxy
)

__version__ = "1.0.0"
__author__ = "0102 pArtifact"
__domain__ = "platform_integration"
__status__ = "prototype"

# WSP Compliance
__wsp_compliant__ = True
__wsp_protocols__ = ["WSP_1", "WSP_3", "WSP_42", "WSP_53"]

# Platform Integration
__platform__ = "youtube"
__integration_type__ = "community_engagement"
__orchestration_mode__ = "wre_enabled"

__all__ = [
    'YouTubeProxy',
    'YouTubeStream', 
    'CommunityMetrics',
    'StreamStatus',
    'EngagementLevel',
    'create_youtube_proxy',
    'test_youtube_proxy'
]
