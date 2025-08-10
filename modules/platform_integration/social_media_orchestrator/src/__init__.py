"""
Social Media Orchestrator - Unified social media management system
WSP Compliance: WSP 3, WSP 11, WSP 22, WSP 49, WSP 42
"""

from .social_media_orchestrator import (
    SocialMediaOrchestrator,
    OrchestrationError,
    AuthenticationError,
    ContentError,
    SchedulingError,
    PostResult,
    create_social_media_orchestrator
)

from .oauth import OAuthCoordinator
from .content import ContentOrchestrator
from .scheduling import SchedulingEngine, ScheduledPost
from .platform_adapters import (
    BasePlatformAdapter,
    TwitterAdapter,
    LinkedInAdapter
)

__all__ = [
    # Main orchestrator
    'SocialMediaOrchestrator',
    'create_social_media_orchestrator',
    
    # Exceptions
    'OrchestrationError',
    'AuthenticationError', 
    'ContentError',
    'SchedulingError',
    
    # Data classes
    'PostResult',
    'ScheduledPost',
    
    # Core components
    'OAuthCoordinator',
    'ContentOrchestrator',
    'SchedulingEngine',
    
    # Platform adapters
    'BasePlatformAdapter',
    'TwitterAdapter',
    'LinkedInAdapter'
]

# Module metadata
__version__ = '1.0.0'
__description__ = 'Unified social media orchestration system for FoundUps'
__author__ = 'FoundUps Development Team'