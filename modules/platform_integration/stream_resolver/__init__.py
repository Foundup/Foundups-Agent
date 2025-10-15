"""
Stream Resolver Module for Windsurf Project

WSP 3 Phase 4: YouTube API operations extracted to youtube_api_operations module.
Backward compatibility maintained via src/__init__.py forwarding.
"""

# Import from src/__init__.py which has backward compatibility wrappers
from .src import (
    check_video_details,
    search_livestreams,
    get_active_livestream_video_id,
    calculate_dynamic_delay,
    mask_sensitive_id,
    validate_api_client,
    StreamResolver,
    QuotaExceededError,
    NoQuotaStreamChecker,
    StreamResolverDB,
    config,
    StreamResolverConfig,
    get_config_value
)

__all__ = [
    # Backward compatibility functions (forwarded from src)
    'check_video_details',
    'search_livestreams',
    'get_active_livestream_video_id',
    'calculate_dynamic_delay',
    'mask_sensitive_id',
    'validate_api_client',

    # Core classes
    'StreamResolver',
    'NoQuotaStreamChecker',
    'StreamResolverDB',

    # Configuration
    'config',
    'StreamResolverConfig',
    'get_config_value',

    # Exceptions
    'QuotaExceededError'
]
