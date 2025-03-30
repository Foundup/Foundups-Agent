"""
Token Manager Module for Windsurf Project

Handles OAuth token rotation and health checking for YouTube API authentication.
Integrates with existing OAuth manager and quota tracking.
"""

import logging
import time
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# Add project root to Python path for imports
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from utils.oauth_manager import (
    quota_manager,
    get_authenticated_service,
    get_oauth_token_file,
    get_client_secrets_file
)

logger = logging.getLogger(__name__)

class TokenManager:
    """Manages OAuth token rotation and health checking."""
    
    def __init__(self):
        self.current_token_index = 0
        self.token_health_cache: Dict[int, Dict[str, Any]] = {}
        self.health_check_interval = 300  # 5 minutes
        self.max_retries = 3
        self.retry_delay = 5  # seconds
        self.cooldown_period = 1800  # 30 minutes
        self.token_usage: Dict[int, Dict[str, Any]] = {}
        self.parallel_check_timeout = 10  # seconds
        
    def check_token_health(self, token_index: Optional[int] = None) -> bool:
        """
        Validates the health of the specified token or current token.
        
        Args:
            token_index: Optional index of token to check. If None, uses current token.
            
        Returns:
            bool: True if token is healthy, False otherwise
        """
        if token_index is None:
            token_index = self.current_token_index
            
        # Check cooldown first
        if token_index in self.token_health_cache:
            last_check = self.token_health_cache[token_index].get('last_check')
            if last_check and time.time() - last_check < self.health_check_interval:
                return self.token_health_cache[token_index].get('is_healthy', False)
                
        # Check token file exists
        token_file = get_oauth_token_file(token_index)
        if not os.path.exists(token_file):
            logger.error(f"Token file not found: {token_file}")
            self._update_health_cache(token_index, False)
            return False
            
        try:
            # Load and validate token
            credentials = Credentials.from_authorized_user_file(token_file)
            if not credentials or not credentials.valid:
                if credentials and credentials.expired and credentials.refresh_token:
                    credentials.refresh(Request())
                    with open(token_file, 'w') as token:
                        token.write(credentials.to_json())
                else:
                    logger.error(f"Invalid or expired token in {token_file}")
                    self._update_health_cache(token_index, False)
                    return False
                    
            # Check quota
            if not quota_manager.check_quota(token_index):
                logger.warning(f"Quota exceeded for token {token_index}")
                self._update_health_cache(token_index, False)
                return False
                
            self._update_health_cache(token_index, True)
            return True
            
        except Exception as e:
            logger.error(f"Error checking token health: {str(e)}")
            self._update_health_cache(token_index, False)
            return False
            
    def _update_health_cache(self, token_index: int, is_healthy: bool):
        """Update the health cache for a token."""
        self.token_health_cache[token_index] = {
            'is_healthy': is_healthy,
            'last_check': time.time()
        }
        
    async def _check_token_parallel(self, token_index: int) -> Optional[int]:
        """Check a single token's health asynchronously."""
        try:
            is_healthy = self.check_token_health(token_index)
            return token_index if is_healthy else None
        except Exception as e:
            logger.error(f"Error checking token {token_index}: {str(e)}")
            return None
            
    async def _check_tokens_parallel(self, token_indices: List[int]) -> Optional[int]:
        """Check multiple tokens' health in parallel."""
        tasks = [self._check_token_parallel(idx) for idx in token_indices]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Error in parallel token check: {str(result)}")
            elif result is not None:
                return result
                
        return None
        
    async def rotate_tokens(self) -> Optional[int]:
        """
        Rotate to the next healthy token if available.
        
        Returns:
            Optional[int]: Index of the new token if successful, None otherwise
        """
        # Get all available token indices
        token_files = [f for f in os.listdir(os.path.dirname(get_oauth_token_file(0)))
                      if f.startswith('token_') and f.endswith('.json')]
        token_indices = [int(f.split('_')[1].split('.')[0]) for f in token_files]
        
        if not token_indices:
            logger.error("No token files found")
            return None
            
        # Check current token first
        if self.check_token_health(self.current_token_index):
            return self.current_token_index
            
        # Check other tokens in parallel
        other_indices = [idx for idx in token_indices if idx != self.current_token_index]
        if not other_indices:
            logger.error("No alternative tokens available")
            return None
            
        try:
            new_index = await self._check_tokens_parallel(other_indices)
            if new_index is not None:
                self.current_token_index = new_index
                logger.info(f"Rotated to token {new_index}")
                return new_index
            else:
                logger.error("No healthy tokens found")
                return None
                
        except Exception as e:
            logger.error(f"Error during token rotation: {str(e)}")
            return None

# Create singleton instance
token_manager = TokenManager() 