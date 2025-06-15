"""
LEGACY COMPATIBILITY SHIM - utils/oauth_manager.py
"""
import warnings
from google.oauth2.credentials import Credentials
import os
import logging
logger = logging.getLogger(__name__)
warnings.warn("utils.oauth_manager is deprecated. Use modules.infrastructure.oauth_management.oauth_management.src.oauth_manager instead.", DeprecationWarning, stacklevel=2)
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

def save_oauth_token_file(credentials: Credentials, credential_type: str) -> None:
    """Saves the OAuth credentials to the specified token file."""
    from modules.infrastructure.oauth_management.oauth_management.src.oauth_manager import get_oauth_token_file, CREDENTIALS_DIR
    token_file_path = get_oauth_token_file(credential_type)
    try:
        os.makedirs(os.path.dirname(token_file_path), exist_ok=True)
        with open(token_file_path, 'w') as token_file:
            token_file.write(credentials.to_json())
        logger.info(f"Refreshed token saved successfully to {token_file_path}")
    except Exception as e:
        logger.error(f"Failed to save token file to {token_file_path}: {e}")
__all__.append('save_oauth_token_file')