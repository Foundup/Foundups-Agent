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
from modules.platform_integration.youtube_auth.youtube_auth import get_authenticated_service
from utils.oauth_manager import get_oauth_token_file

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
            cache_entry = self.token_health_cache[token_index]
            if not cache_entry.get('healthy', False):
                cooldown_end = cache_entry.get('cooldown_end', 0)
                if time.time() < cooldown_end:
                    logger.info(f"Token set_{token_index + 1} is in cooldown until {datetime.fromtimestamp(cooldown_end)}")
                    return False
                    
        # Check cache for healthy tokens
        if token_index in self.token_health_cache:
            cache_entry = self.token_health_cache[token_index]
            if time.time() - cache_entry['timestamp'] < self.health_check_interval:
                return cache_entry['healthy']
        
        # Get token file path
        token_file = get_oauth_token_file(f"set_{token_index + 1}")
        
        try:
            # Try to load and validate token
            service = get_authenticated_service(token_index)
            if not service:
                logger.warning(f"Token health check failed for set_{token_index + 1}: Service creation failed")
                self._update_health_cache(token_index, False)
                return False
                
            # Test token with a lightweight API call
            service.channels().list(
                part="snippet",
                id="UC-LSSlOZwpGIRIYihaz8zCw"  # Using a known channel ID
            ).execute()
            
            logger.info(f"Token health check passed for set_{token_index + 1}")
            self._update_health_cache(token_index, True)
            return True
            
        except Exception as e:
            logger.error(f"Token health check failed for set_{token_index + 1}: {e}")
            self._update_health_cache(token_index, False)
            return False
            
    def _update_health_cache(self, token_index: int, is_healthy: bool):
        """Updates the health check cache for a token."""
        self.token_health_cache[token_index] = {
            'healthy': is_healthy,
            'timestamp': time.time(),
            'cooldown_end': time.time() + self.cooldown_period if not is_healthy else 0
        }
        
    async def _check_token_parallel(self, token_index: int) -> Optional[int]:
        """Check a single token's health asynchronously."""
        try:
            is_healthy = self.check_token_health(token_index)
            return token_index if is_healthy else None
        except Exception as e:
            logger.error(f"Parallel token check failed for set_{token_index + 1}: {e}")
            return None
            
    async def _check_tokens_parallel(self, token_indices: List[int]) -> Optional[int]:
        """Check multiple tokens in parallel and return the first healthy one."""
        tasks = [self._check_token_parallel(idx) for idx in token_indices]
        try:
            results = await asyncio.wait_for(asyncio.gather(*tasks), timeout=self.parallel_check_timeout)
            for result in results:
                if result is not None:
                    return result
        except asyncio.TimeoutError:
            logger.warning("Parallel token check timed out")
        except Exception as e:
            logger.error(f"Parallel token check failed: {e}")
        return None
        
    async def rotate_tokens(self) -> Optional[int]:
        """
        Rotates to the next available healthy token using parallel checking.
        
        Returns:
            Optional[int]: Index of the new token if successful, None if rotation failed
        """
        original_index = self.current_token_index
        all_indices = list(range(4))  # Assuming 4 token sets
        
        # Try all tokens in parallel first
        healthy_token = await self._check_tokens_parallel(all_indices)
        if healthy_token is not None:
            self.current_token_index = healthy_token
            logger.info(f"Successfully rotated to token set_{self.current_token_index + 1}")
            return self.current_token_index
            
        # If parallel check fails, fall back to sequential checking
        attempts = 0
        while attempts < self.max_retries:
            # Try next token
            self.current_token_index = (self.current_token_index + 1) % 4
            
            # Skip if we've tried all tokens
            if self.current_token_index == original_index:
                logger.error("All tokens failed health check")
                return None
                
            # Check if token is healthy
            if self.check_token_health(self.current_token_index):
                logger.info(f"Successfully rotated to token set_{self.current_token_index + 1}")
                return self.current_token_index
                
            attempts += 1
            if attempts < self.max_retries:
                logger.warning(f"Token rotation attempt {attempts} failed, retrying...")
                await asyncio.sleep(self.retry_delay)
                
        logger.error("Token rotation failed after maximum retries")
        return None

# Initialize token manager
token_manager = TokenManager() 