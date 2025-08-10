"""
LinkedIn Unified Platform Integration
WSP Compliance: WSP 3, WSP 11, WSP 22, WSP 49, WSP 42

Consolidates linkedin_agent, linkedin_scheduler, linkedin_proxy functionality
"""

from .linkedin_manager import (
    LinkedInManager,
    LinkedInAuthError,
    LinkedInAPIError,
    LinkedInContentError,
    create_linkedin_manager
)

# Import key components for direct access if needed
try:
    from .auth.oauth_manager import OAuthManager
    from .content.post_generator import PostGenerator
    from .scheduling.linkedin_scheduler import LinkedInScheduler
    from .proxy.linkedin_proxy import LinkedInProxy
    from .engagement.interaction_manager import InteractionManager
except ImportError:
    # Components may not be available, fallback gracefully
    OAuthManager = None
    PostGenerator = None
    LinkedInScheduler = None
    LinkedInProxy = None
    InteractionManager = None

__all__ = [
    # Main unified interface
    'LinkedInManager',
    'create_linkedin_manager',
    
    # Exceptions
    'LinkedInAuthError',
    'LinkedInAPIError', 
    'LinkedInContentError',
    
    # Component access (if available)
    'OAuthManager',
    'PostGenerator',
    'LinkedInScheduler',
    'LinkedInProxy',
    'InteractionManager'
]

# Module metadata
__version__ = '1.0.0'
__description__ = 'Unified LinkedIn platform integration for FoundUps'
__author__ = 'FoundUps Development Team'