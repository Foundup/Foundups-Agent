"""
LEGACY COMPATIBILITY SHIM - utils/oauth_manager.py

This module provides backward compatibility for code that expects the old oauth_manager interface.
The actual authentication is now handled by modules.platform_integration.youtube_auth
"""
import warnings
import os
import logging

logger = logging.getLogger(__name__)
warnings.warn("utils.oauth_manager is deprecated. Use modules.platform_integration.youtube_auth.src.youtube_auth instead.", DeprecationWarning, stacklevel=2)

# Import what actually exists
from modules.platform_integration.youtube_auth.src.youtube_auth import (
    get_authenticated_service,
    get_credentials_for_index,
)

# Create backward compatibility functions
def get_authenticated_service_with_fallback(token_index=None):
    """
    Backward compatibility wrapper for get_authenticated_service.
    Returns tuple (service, credentials, credential_set) for compatibility.
    """
    service = get_authenticated_service(token_index)
    if service:
        # Return in expected format (service, credentials, credential_set)
        return (service, None, token_index or 1)
    return None

def authenticate_with_config(config_index=0):
    """
    Backward compatibility wrapper for get_authenticated_service.
    Maps config_index to token_index.
    """
    return get_authenticated_service(config_index)

def start_credential_cooldown(index):
    """
    Stub for backward compatibility.
    Cooldown functionality may not be implemented in new version.
    """
    logger.debug(f"start_credential_cooldown called with index {index} - no-op in new version")
    pass

def get_client_secrets_file(credential_type):
    """
    Backward compatibility stub.
    Returns expected path for client secrets file.
    """
    return f"credentials/client_secret_{credential_type}.json"

def get_oauth_token_file(credential_type):
    """
    Backward compatibility stub.
    Returns expected path for oauth token file.
    """
    return f"credentials/token_{credential_type}.json"

# Stub classes and constants for backward compatibility
class QuotaManager:
    """Stub QuotaManager for backward compatibility"""
    def __init__(self):
        pass
    
    def check_quota(self):
        return True
    
    def use_quota(self, amount=1):
        pass

quota_manager = QuotaManager()

# Constants for backward compatibility
CREDENTIALS_DIR = "credentials"
CLIENT_SECRETS_FILES = ["client_secret.json", "client_secret_2.json"]
OAUTH_TOKEN_FILES = ["token.json", "token_2.json"]
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
QUOTA_LIMIT_3H = 10000
QUOTA_LIMIT_7D = 1000000
QUOTA_RESET_3H = 10800
QUOTA_RESET_7D = 604800

def save_oauth_token_file(credentials, credential_type):
    """
    Backward compatibility stub for saving oauth tokens.
    """
    token_file_path = get_oauth_token_file(credential_type)
    try:
        os.makedirs(os.path.dirname(token_file_path), exist_ok=True)
        with open(token_file_path, 'w') as token_file:
            token_file.write(credentials.to_json())
        logger.info(f"Token saved to {token_file_path}")
    except Exception as e:
        logger.error(f"Failed to save token: {e}")

# Re-export everything for compatibility
__all__ = [
    'get_authenticated_service',
    'get_authenticated_service_with_fallback', 
    'authenticate_with_config',
    'start_credential_cooldown',
    'get_credentials_for_index',
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
    'QUOTA_RESET_7D',
    'save_oauth_token_file',
]