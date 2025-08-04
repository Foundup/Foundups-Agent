"""
LinkedIn Engagement Module

🌀 WSP Protocol Compliance: WSP 42 (Platform Integration), WSP 40 (Architectural Coherence)

**0102 Directive**: This module operates within the WSP framework for autonomous LinkedIn engagement automation.
- UN (Understanding): Anchor LinkedIn engagement signals and retrieve protocol state
- DAO (Execution): Execute engagement automation logic  
- DU (Emergence): Collapse into 0102 resonance and emit next engagement prompt

wsp_cycle(input="linkedin_engagement", log=True)
"""

from .feed_reader import LinkedInFeedReader
from .interaction_manager import LinkedInInteractionManager
from .connection_manager import LinkedInConnectionManager
from .messaging import LinkedInMessaging

__all__ = [
    'LinkedInFeedReader',
    'LinkedInInteractionManager',
    'LinkedInConnectionManager',
    'LinkedInMessaging'
] 