"""Stream Resolver Module for Windsurf Project"""

# Import available functions and classes from src
from .src.stream_resolver import (
    get_active_livestream_video_id, 
    check_video_details, 
    search_livestreams,
    # StreamResolver,        # Removed - Class doesn't exist in source
    QuotaExceededError     # Keep QuotaExceededError
)

__all__ = [
    # 'StreamResolver',            # Removed - Class doesn't exist in source
    'QuotaExceededError',            # Keep QuotaExceededError
    'get_active_livestream_video_id', 
    'check_video_details', 
    'search_livestreams'
] 