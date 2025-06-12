"""
LinkedIn Scheduler Module - Public API
WSP 11 Compliant: Interface definition for external usage
Enhanced with LinkedIn API v2 Integration
"""

from .src.linkedin_scheduler import LinkedInScheduler, PostQueue, LinkedInAPIError

# Public API exports
__all__ = [
    'LinkedInScheduler',
    'PostQueue',
    'LinkedInAPIError'
]

# Module metadata
__version__ = '0.2.0'
__status__ = 'Enhanced'  # Enhanced with real API integration
