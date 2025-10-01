"""
Core components for social media orchestration
Modular, single-responsibility services extracted from simple_posting_orchestrator.py
"""

from .duplicate_prevention_manager import DuplicatePreventionManager
from .live_status_verifier import LiveStatusVerifier
from .channel_configuration_manager import (
    ChannelConfigurationManager,
    LinkedInPage,
    XAccount
)
from .platform_posting_service import (
    PlatformPostingService,
    PostingResult,
    PostingStatus
)
from .browser_manager import BrowserManager, get_browser_manager

__all__ = [
    'DuplicatePreventionManager',
    'LiveStatusVerifier',
    'ChannelConfigurationManager',
    'LinkedInPage',
    'XAccount',
    'PlatformPostingService',
    'PostingResult',
    'PostingStatus',
    'BrowserManager',
    'get_browser_manager'
]

# Module version
__version__ = '1.1.0'