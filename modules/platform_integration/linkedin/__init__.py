"""
LinkedIn Unified Module
WSP Compliance: WSP 49

Main module entry point for LinkedIn platform integration
"""

from .src import (
    LinkedInManager,
    LinkedInAuthError,
    LinkedInAPIError,
    LinkedInContentError,
    create_linkedin_manager
)

__all__ = [
    'LinkedInManager',
    'LinkedInAuthError',
    'LinkedInAPIError',
    'LinkedInContentError', 
    'create_linkedin_manager'
]