"""
Social Media Orchestrator Module
WSP 49 compliant module for unified social media management

Domain: platform_integration
Classification: Social Media Orchestration
WSP Compliance: WSP 3, WSP 11, WSP 22, WSP 49
"""

from .src.social_media_orchestrator import SocialMediaOrchestrator
from .src.oauth_coordinator import OAuthCoordinator
from .src.content_orchestrator import ContentOrchestrator
from .src.scheduling_engine import SchedulingEngine
from .src.platform_adapters import TwitterAdapter, LinkedInAdapter

__all__ = [
    'SocialMediaOrchestrator',
    'OAuthCoordinator', 
    'ContentOrchestrator',
    'SchedulingEngine',
    'TwitterAdapter',
    'LinkedInAdapter'
]

__version__ = "1.0.0"
__author__ = "WSP Framework"
__description__ = "Unified social media orchestration for X/Twitter and LinkedIn platforms"