"""
LEGACY COMPATIBILITY SHIM - utils/oauth_manager.py

⚠️  DEPRECATION NOTICE ⚠️
========================
This file is a COMPATIBILITY SHIM only. The actual OAuth Manager has been moved to:
modules/infrastructure/oauth_management/oauth_management/src/oauth_manager.py

This shim exists to maintain backward compatibility during the transition period.
All new code should import directly from the new location:

    from modules.infrastructure.oauth_management.oauth_management.src.oauth_manager import (
        get_authenticated_service, get_authenticated_service_with_fallback, QuotaManager
    )

This shim will be removed in a future version once all imports have been updated.
"""

import warnings

# Issue deprecation warning
warnings.warn(
    "utils.oauth_manager is deprecated. Use modules.infrastructure.oauth_management.oauth_management.src.oauth_manager instead.",
    DeprecationWarning,
    stacklevel=2
)

# Import everything from the new location for backward compatibility
from modules.infrastructure.oauth_management.oauth_management.src.oauth_manager import (
    # Core authentication functions
    get_authenticated_service,
    get_authenticated_service_with_fallback,
    authenticate_with_config,
    start_credential_cooldown,
    
    # Utility functions
    get_client_secrets_file,
    get_oauth_token_file,
    
    # Classes
    QuotaManager,
    
    # Module-level instances
    quota_manager,
    
    # Constants (for backward compatibility)
    CREDENTIALS_DIR,
    CLIENT_SECRETS_FILES,
    OAUTH_TOKEN_FILES,
    API_SERVICE_NAME,
    API_VERSION,
    SCOPES,
    QUOTA_LIMIT_3H,
    QUOTA_LIMIT_7D,
    QUOTA_RESET_3H,
    QUOTA_RESET_7D
)

# Re-export everything to maintain full compatibility
__all__ = [
    'get_authenticated_service',
    'get_authenticated_service_with_fallback', 
    'authenticate_with_config',
    'start_credential_cooldown',
    'get_client_secrets_file',
    'get_oauth_token_file',
    'QuotaManager',
    'quota_manager',
    'CREDENTIALS_DIR',
    'CLIENT_SECRETS_FILES',
    'OAUTH_TOKEN_FILES',
    'API_SERVICE_NAME',
    'API_VERSION',
    'SCOPES',
    'QUOTA_LIMIT_3H',
    'QUOTA_LIMIT_7D',
    'QUOTA_RESET_3H',
    'QUOTA_RESET_7D'
] 