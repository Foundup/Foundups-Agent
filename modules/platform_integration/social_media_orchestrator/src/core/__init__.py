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

__all__ = [
    'DuplicatePreventionManager',
    'LiveStatusVerifier',
    'ChannelConfigurationManager',
    'LinkedInPage',
    'XAccount',
    'PlatformPostingService',
    'PostingResult',
    'PostingStatus'
]

# Module version
__version__ = '1.1.0'