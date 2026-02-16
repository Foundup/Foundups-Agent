"""
Legacy OAuthManager compatibility module.

This keeps older imports working:
    from modules.infrastructure.oauth_management.src.oauth_manager import ...
"""

from modules.platform_integration.utilities.oauth_management.src.oauth_manager import *  # noqa: F401,F403

