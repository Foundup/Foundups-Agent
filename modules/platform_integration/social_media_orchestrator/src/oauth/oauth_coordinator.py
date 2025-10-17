"""
OAuth Coordinator - Centralized OAuth management for all social platforms
WSP Compliance: WSP 3, WSP 49
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json
import os
try:
    from cryptography.fernet import Fernet
except ImportError:
    Fernet = None  # Will use mock encryption in dev mode


class OAuthCoordinator:
    """
    Centralized OAuth management for all social media platforms
    
    Handles secure storage, refresh, and validation of OAuth tokens
    across multiple platforms with encryption at rest.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize OAuth Coordinator
        
        Args:
            config: Configuration including storage path, encryption settings
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Setup secure storage
        self.storage_path = config.get('storage_path', './oauth_tokens')
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher = Fernet(self.encryption_key) if Fernet else None
        
        # In-memory token cache
        self._token_cache = {}
        self._token_expiry = {}
        
        # Ensure storage directory exists
        os.makedirs(self.storage_path, exist_ok=True)
        
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for token storage"""
        key_file = os.path.join(self.config.get('key_path', '.'), '.oauth_key')
        
        if os.path.exists(key_file):
            with open(key_file, 'rb', encoding="utf-8") as f:
                return f.read()
        else:
            key = Fernet.generate_key() if Fernet else b'mock_key_for_dev_mode'
            with open(key_file, 'wb', encoding="utf-8") as f:
                f.write(key)
            os.chmod(key_file, 0o600)  # Restrict access
            return key
            
    def store_credentials(self, platform: str, credentials: Dict[str, Any]) -> bool:
        """
        Securely store OAuth credentials for a platform
        
        Args:
            platform: Platform identifier
            credentials: OAuth credentials dictionary
            
        Returns:
            bool: True if stored successfully
        """
        try:
            # Add timestamp
            credentials['stored_at'] = datetime.now().isoformat()
            
            # Calculate expiry if provided
            if 'expires_in' in credentials:
                expiry = datetime.now() + timedelta(seconds=credentials['expires_in'])
                credentials['expires_at'] = expiry.isoformat()
                self._token_expiry[platform] = expiry
                
            # Encrypt and store
            encrypted_data = self.cipher.encrypt(json.dumps(credentials).encode())
            
            storage_file = os.path.join(self.storage_path, f'{platform}_oauth.enc')
            with open(storage_file, 'wb', encoding="utf-8") as f:
                f.write(encrypted_data)
                
            # Update cache
            self._token_cache[platform] = credentials.copy()
            
            self.logger.info(f"OAuth credentials stored for {platform}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store OAuth credentials for {platform}: {e}")
            return False
            
    def get_credentials(self, platform: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve OAuth credentials for a platform
        
        Args:
            platform: Platform identifier
            
        Returns:
            Optional[Dict[str, Any]]: Decrypted credentials or None if not found
        """
        # Check cache first
        if platform in self._token_cache:
            if self._is_token_valid(platform):
                return self._token_cache[platform]
            else:
                # Token expired, remove from cache
                del self._token_cache[platform]
                if platform in self._token_expiry:
                    del self._token_expiry[platform]
                    
        # Load from storage
        storage_file = os.path.join(self.storage_path, f'{platform}_oauth.enc')
        
        if not os.path.exists(storage_file):
            return None
            
        try:
            with open(storage_file, 'rb', encoding="utf-8") as f:
                encrypted_data = f.read()
                
            decrypted_data = self.cipher.decrypt(encrypted_data)
            credentials = json.loads(decrypted_data.decode())
            
            # Update cache and expiry
            self._token_cache[platform] = credentials
            
            if 'expires_at' in credentials:
                self._token_expiry[platform] = datetime.fromisoformat(credentials['expires_at'])
                
            # Check if still valid
            if self._is_token_valid(platform):
                return credentials
            else:
                self.logger.warning(f"OAuth token for {platform} has expired")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to retrieve OAuth credentials for {platform}: {e}")
            return None
            
    def _is_token_valid(self, platform: str) -> bool:
        """Check if token is still valid (not expired)"""
        if platform not in self._token_expiry:
            return True  # No expiry set, assume valid
            
        return datetime.now() < self._token_expiry[platform]
        
    def refresh_token(self, platform: str, refresh_token: str) -> Optional[Dict[str, Any]]:
        """
        Refresh OAuth token for a platform
        
        Args:
            platform: Platform identifier
            refresh_token: Refresh token string
            
        Returns:
            Optional[Dict[str, Any]]: New credentials or None if failed
        """
        # This would implement platform-specific refresh logic
        # For now, return None as refresh is platform-specific
        self.logger.info(f"Token refresh requested for {platform}")
        return None
        
    def revoke_credentials(self, platform: str) -> bool:
        """
        Revoke and delete OAuth credentials for a platform
        
        Args:
            platform: Platform identifier
            
        Returns:
            bool: True if revoked successfully
        """
        try:
            # Remove from cache
            if platform in self._token_cache:
                del self._token_cache[platform]
                
            if platform in self._token_expiry:
                del self._token_expiry[platform]
                
            # Remove storage file
            storage_file = os.path.join(self.storage_path, f'{platform}_oauth.enc')
            if os.path.exists(storage_file):
                os.remove(storage_file)
                
            self.logger.info(f"OAuth credentials revoked for {platform}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to revoke OAuth credentials for {platform}: {e}")
            return False
            
    def list_authenticated_platforms(self) -> List[str]:
        """
        List all platforms with valid OAuth credentials
        
        Returns:
            List[str]: List of authenticated platform identifiers
        """
        authenticated = []
        
        # Check cache first
        for platform in list(self._token_cache.keys()):
            if self._is_token_valid(platform):
                authenticated.append(platform)
                
        # Check storage for any missing from cache
        if os.path.exists(self.storage_path):
            for filename in os.listdir(self.storage_path):
                if filename.endswith('_oauth.enc'):
                    platform = filename.replace('_oauth.enc', '')
                    if platform not in authenticated:
                        # Try to load and validate
                        creds = self.get_credentials(platform)
                        if creds:
                            authenticated.append(platform)
                            
        return authenticated
        
    def get_platform_status(self, platform: str) -> Dict[str, Any]:
        """
        Get OAuth status for a specific platform
        
        Args:
            platform: Platform identifier
            
        Returns:
            Dict[str, Any]: Status information
        """
        credentials = self.get_credentials(platform)
        
        if not credentials:
            return {
                'authenticated': False,
                'valid': False,
                'expires_at': None,
                'stored_at': None
            }
            
        return {
            'authenticated': True,
            'valid': self._is_token_valid(platform),
            'expires_at': credentials.get('expires_at'),
            'stored_at': credentials.get('stored_at'),
            'has_refresh_token': 'refresh_token' in credentials
        }
        
    def cleanup_expired_tokens(self) -> int:
        """
        Clean up expired tokens from storage and cache
        
        Returns:
            int: Number of expired tokens removed
        """
        removed_count = 0
        platforms_to_remove = []
        
        # Check all platforms for expiry
        for platform in self.list_authenticated_platforms():
            if not self._is_token_valid(platform):
                platforms_to_remove.append(platform)
                
        # Remove expired tokens
        for platform in platforms_to_remove:
            if self.revoke_credentials(platform):
                removed_count += 1
                
        if removed_count > 0:
            self.logger.info(f"Cleaned up {removed_count} expired OAuth tokens")
            
        return removed_count