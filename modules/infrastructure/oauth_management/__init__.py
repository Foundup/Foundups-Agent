"""
OAuth Management Module - FoundUps Agent Authentication System

This module provides OAuth 2.0 authentication and quota management for the FoundUps Agent.
It supports multiple credential sets with intelligent rotation and fallback capabilities.
"""

from .src.oauth_manager import (
    get_authenticated_service,
    get_authenticated_service_with_fallback,
    QuotaManager,
    OAuthManager,
    quota_manager
)

__all__ = [
    'get_authenticated_service',
    'get_authenticated_service_with_fallback', 
    'QuotaManager',
    'OAuthManager',
    'quota_manager'
] 