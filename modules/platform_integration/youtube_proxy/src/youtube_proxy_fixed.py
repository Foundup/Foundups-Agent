"""
YouTube Proxy with find_active_livestream method
WSP 48 Compliant: Self-healing authentication
"""

import logging
import sys
from typing import Optional, Tuple
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)

class YouTubeProxyFixed:
    """YouTube Proxy with missing methods added"""
    
    def __init__(self, credentials=None):
        """Initialize with credentials"""
        self.credentials = credentials
        self.service = None
        self.logger = logger
        
    def find_active_livestream(self, channel_id: str) -> Optional[Tuple[str, str]]:
        """
        Find active livestream for a channel.
        WSP 48: Self-healing authentication with automatic token refresh.
        
        Returns:
            Tuple of (video_id, chat_id) if found, None otherwise
        """
        try:
            # Import stream resolver functions
            from modules.platform_integration.stream_resolver.src.stream_resolver import (
                get_active_livestream_video_id_enhanced,
                get_authenticated_service_with_fallback
            )
            
            # WSP 48: Self-healing - Try to get authenticated service
            self.logger.info("[INFO] Attempting to find active livestream...")
            
            # First try with provided credentials
            if self.credentials:
                # Use existing credentials
                from googleapiclient.discovery import build
                self.service = build('youtube', 'v3', credentials=self.credentials)
            else:
                # WSP 48: Self-heal by getting new authentication
                self.logger.info("[INFO] No credentials provided, attempting self-healing auth...")
                auth_result = get_authenticated_service_with_fallback()
                
                if auth_result:
                    self.service, self.credentials, credential_set = auth_result
                    self.logger.info(f"[OK] Self-healed authentication with {credential_set}")
                else:
                    # Try to refresh tokens automatically
                    self.logger.warning("[WARN] Authentication failed, attempting token refresh...")
                    if self._auto_refresh_tokens():
                        # Retry authentication
                        auth_result = get_authenticated_service_with_fallback()
                        if auth_result:
                            self.service, self.credentials, credential_set = auth_result
                            self.logger.info(f"[OK] Authentication successful after token refresh")
                        else:
                            self.logger.error("[ERROR] Authentication failed even after token refresh")
                            return None
                    else:
                        self.logger.error("[ERROR] Could not refresh tokens")
                        return None
            
            # Now use stream resolver to find livestream
            if self.service:
                result = get_active_livestream_video_id_enhanced(self.service, channel_id)
                if result:
                    video_id, chat_id = result
                    self.logger.info(f"[OK] Found active livestream: {video_id[:8]}...")
                    return result
                else:
                    self.logger.info("[INFO] No active livestream found")
                    return None
            else:
                self.logger.error("[ERROR] No YouTube service available")
                return None
                
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to find livestream: {e}")
            return None
    
    def _auto_refresh_tokens(self) -> bool:
        """
        WSP 48: Automatic token refresh for self-healing
        """
        try:
            import os
            import json
            from google.oauth2.credentials import Credentials
            from google.auth.transport.requests import Request
            
            CREDENTIALS_DIR = "credentials"
            TOKEN_FILES = ["oauth_token.json", "oauth_token2.json", "oauth_token3.json", "oauth_token4.json"]
            SCOPES = [
                "https://www.googleapis.com/auth/youtube.force-ssl",
                "https://www.googleapis.com/auth/youtube.readonly"
            ]
            
            refreshed_any = False
            
            for token_file in TOKEN_FILES:
                token_path = os.path.join(CREDENTIALS_DIR, token_file)
                
                if os.path.exists(token_path):
                    try:
                        with open(token_path, 'r') as f:
                            creds_data = json.load(f)
                        
                        creds = Credentials.from_authorized_user_info(creds_data, SCOPES)
                        
                        if creds and creds.refresh_token:
                            try:
                                creds.refresh(Request())
                                
                                # Save refreshed token
                                with open(token_path, 'w') as f:
                                    f.write(creds.to_json())
                                
                                self.logger.info(f"[OK] Auto-refreshed token: {token_file}")
                                refreshed_any = True
                                break  # One successful refresh is enough
                                
                            except Exception as refresh_error:
                                if 'invalid_grant' in str(refresh_error):
                                    self.logger.warning(f"[WARN] Token {token_file} expired, needs reauth")
                                else:
                                    self.logger.error(f"[ERROR] Failed to refresh {token_file}: {refresh_error}")
                    except Exception as e:
                        self.logger.error(f"[ERROR] Could not load {token_file}: {e}")
            
            return refreshed_any
            
        except Exception as e:
            self.logger.error(f"[ERROR] Auto-refresh failed: {e}")
            return False

# Monkey-patch the existing YouTubeProxy if it's imported
def patch_youtube_proxy():
    """Apply the fix to existing YouTubeProxy class"""
    try:
        from modules.platform_integration.youtube_proxy.src.youtube_proxy import YouTubeProxy
        
        # Add the missing method
        YouTubeProxy.find_active_livestream = YouTubeProxyFixed.find_active_livestream
        YouTubeProxy._auto_refresh_tokens = YouTubeProxyFixed._auto_refresh_tokens
        
        logger.info("[OK] YouTubeProxy patched with find_active_livestream method")
        return True
    except Exception as e:
        logger.error(f"[ERROR] Could not patch YouTubeProxy: {e}")
        return False

# Auto-patch on import
patch_youtube_proxy()