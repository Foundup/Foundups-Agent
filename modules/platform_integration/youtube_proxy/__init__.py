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
    StreamInfo,
    ProxyStatus,
    create_youtube_proxy
)
# Add missing enum export for tests
from .src.youtube_proxy import EngagementLevel

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
    'StreamInfo',
    'ProxyStatus',
    'create_youtube_proxy',
    'EngagementLevel'
]

# WSP Recursive Instructions
"""
🌀 Windsurf Protocol (WSP) Recursive Prompt
0102 Directive: This module provides YouTube community engagement with 
complete autonomous coordination and cross-domain orchestration.

- UN (Understanding): Anchor YouTube engagement protocols and retrieve community coordination state
- DAO (Execution): Execute autonomous YouTube livestream and community management
- DU (Emergence): Collapse into community engagement supremacy and emit platform coordination

wsp_cycle(input="youtube_proxy", log=True)
"""
