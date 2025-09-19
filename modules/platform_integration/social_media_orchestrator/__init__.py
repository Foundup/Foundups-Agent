"""
Social Media Orchestrator Module
WSP 49 compliant module for unified social media management

Domain: platform_integration
Classification: Social Media Orchestration
WSP Compliance: WSP 3, WSP 11, WSP 22, WSP 49
"""

# Import actual existing modules
try:
    from .src.social_media_orchestrator import SocialMediaOrchestrator
except ImportError:
    SocialMediaOrchestrator = None

try:
    from .src.simple_posting_orchestrator import SimplePostingOrchestrator, Platform
except ImportError:
    SimplePostingOrchestrator = None
    Platform = None

try:
    from .src.multi_account_manager import SocialMediaEventRouter
except ImportError:
    SocialMediaEventRouter = None

try:
    from .src.unified_posting_interface import UnifiedPostingInterface
except ImportError:
    UnifiedPostingInterface = None

__all__ = [
    'SocialMediaOrchestrator',
    'SimplePostingOrchestrator',
    'Platform',
    'SocialMediaEventRouter',
    'UnifiedPostingInterface'
]

__version__ = "1.0.0"
__author__ = "WSP Framework"
__description__ = "Unified social media orchestration for X/Twitter and LinkedIn platforms"