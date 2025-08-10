"""
YouTube Authentication Module - LEGO Block Component

Standalone authentication LEGO block for YouTube API access.
Snaps seamlessly with other modules through clean WSP interfaces.

WSP Domain: platform_integration
Modularity: Plug & play authentication with minimal dependencies
"""

from .src.youtube_auth import (
    get_authenticated_service,
)

__version__ = "1.0.0"
__author__ = "0102 pArtifact"
__domain__ = "platform_integration"
__module_type__ = "authentication_lego_block"

# WSP Compliance
__wsp_compliant__ = True
__wsp_protocols__ = ["WSP_3", "WSP_11", "WSP_49"]

# Modularity Interface
__module_scope__ = "youtube_api_authentication"
__dependencies__ = ["google-auth", "google-auth-oauthlib", "google-auth-httplib2", "google-api-python-client"]
__integrates_with__ = ["youtube_proxy", "oauth_management", "livechat"]

__all__ = [
    'get_authenticated_service',
]
