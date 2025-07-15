"""
LinkedIn Agent Module

Professional networking automation module with WRE integration.
Provides intelligent posting, feed reading, content generation, and engagement
automation while maintaining professional LinkedIn standards.

This module follows WSP 3: Enterprise Domain Architecture for platform_integration domain.
"""

from .src import (
    LinkedInAgent,
    LinkedInPost,
    LinkedInProfile, 
    EngagementAction,
    EngagementType,
    ContentType,
    create_linkedin_agent,
    test_linkedin_agent
)

__version__ = "0.0.1"
__author__ = "0102 pArtifact"
__domain__ = "platform_integration"
__status__ = "POC"

# WSP Compliance
__wsp_compliant__ = True
__wsp_protocols__ = ["WSP_1", "WSP_3", "WSP_42", "WSP_53"]

__all__ = [
    'LinkedInAgent',
    'LinkedInPost',
    'LinkedInProfile',
    'EngagementAction', 
    'EngagementType',
    'ContentType',
    'create_linkedin_agent',
    'test_linkedin_agent'
] 