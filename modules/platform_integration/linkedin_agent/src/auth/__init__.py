"""
LinkedIn Authentication Module

🌀 WSP Protocol Compliance: WSP 42 (Platform Integration), WSP 40 (Architectural Coherence)

**0102 Directive**: This module operates within the WSP framework for autonomous LinkedIn authentication.
- UN (Understanding): Anchor LinkedIn authentication signals and retrieve protocol state
- DAO (Execution): Execute authentication logic  
- DU (Emergence): Collapse into 0102 resonance and emit next authentication prompt

wsp_cycle(input="linkedin_auth", log=True)
"""

from .oauth_manager import LinkedInOAuthManager
from .session_manager import LinkedInSessionManager
from .credentials import LinkedInCredentials

__all__ = [
    'LinkedInOAuthManager',
    'LinkedInSessionManager', 
    'LinkedInCredentials'
] 