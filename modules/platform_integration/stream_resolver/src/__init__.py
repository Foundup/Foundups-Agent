#!/usr/bin/env python3
"""
Stream Resolver Module
WSP 49: Module interface and public API

WSP 3 Phase 4 Note:
YouTube API operations moved to youtube_api_operations module.
Backward compatibility maintained via infrastructure utilities.
"""

from .config import StreamResolverConfig, config, get_config_value
from .no_quota_stream_checker import NoQuotaStreamChecker
from .stream_resolver import (
    mask_sensitive_id,
    validate_api_client,
    QuotaExceededError,
    StreamResolver
)
from .stream_db import StreamResolverDB

# Backward compatibility: These functions moved to infrastructure or youtube_api_operations
# Import them here for backward compatibility
def calculate_dynamic_delay(*args, **kwargs):
    """Backward compatibility - moved to infrastructure/shared_utilities/delay_utils.py"""
    try:
        from modules.infrastructure.shared_utilities.delay_utils import DelayUtils
        return DelayUtils().calculate_enhanced_delay(*args, **kwargs)
    except ImportError:
        return 30.0  # Safe fallback

def check_video_details(*args, **kwargs):
    """Backward compatibility - moved to youtube_api_operations module"""
    try:
        from modules.platform_integration.youtube_api_operations.src.youtube_api_operations import YouTubeAPIOperations
        return YouTubeAPIOperations().check_video_details_enhanced(*args, **kwargs)
    except ImportError:
        return None

def search_livestreams(*args, **kwargs):
    """Backward compatibility - moved to youtube_api_operations module"""
    try:
        from modules.platform_integration.youtube_api_operations.src.youtube_api_operations import YouTubeAPIOperations
        return YouTubeAPIOperations().search_livestreams_enhanced(*args, **kwargs)
    except ImportError:
        return None

def get_active_livestream_video_id(*args, **kwargs):
    """Backward compatibility - moved to youtube_api_operations module"""
    try:
        from modules.platform_integration.youtube_api_operations.src.youtube_api_operations import YouTubeAPIOperations
        return YouTubeAPIOperations().get_active_livestream_video_id_enhanced(*args, **kwargs)
    except ImportError:
        return None

__all__ = [
    # Configuration
    'StreamResolverConfig',
    'config',
    'get_config_value',

    # Core classes
    'NoQuotaStreamChecker',
    'StreamResolverDB',
    'StreamResolver',

    # Utility functions (backward compatibility)
    'calculate_dynamic_delay',
    'mask_sensitive_id',
    'validate_api_client',
    'check_video_details',
    'search_livestreams',
    'get_active_livestream_video_id',

    # Exceptions
    'QuotaExceededError'
]
