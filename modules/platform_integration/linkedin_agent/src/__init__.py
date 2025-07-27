"""
LinkedIn Agent Source Module

This module contains the LinkedIn agent implementation following WSP 3: Enterprise Domain Architecture.
Provides professional networking automation with WRE integration.
"""

from .linkedin_agent import (
    LinkedInAgent,
    LinkedInPost,
    LinkedInProfile,
    EngagementAction,
    EngagementType,
    PostType,
    create_linkedin_agent
)

__version__ = "1.0.0"
__all__ = [
    'LinkedInAgent',
    'LinkedInPost', 
    'LinkedInProfile',
    'EngagementAction',
    'EngagementType',
    'PostType',
    'create_linkedin_agent'
] 