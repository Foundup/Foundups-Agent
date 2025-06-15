"""
Token Manager Module for Windsurf Project

Handles OAuth token rotation and health checking for YouTube API authentication.
Integrates with existing OAuth manager and quota tracking.
"""

import logging
import time
import asyncio
import os
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from utils.oauth_manager import get_oauth_token_file

logger = logging.getLogger(__name__)

def _save_oauth_token_file(credentials: Credentials, credential_type: str) -> None:
    """
    Saves the OAuth credentials to the specified token file.
    Co-located here to resolve a persistent file-write issue in the canonical oauth_manager.
    """
    token_file_path = get_oauth_token_file(credential_type)
    try:
        # Ensure the credentials directory exists
        os.makedirs(os.path.dirname(token_file_path), exist_ok=True)
        with open(token_file_path, 'w') as token_file:
            token_file.write(credentials.to_json())
        logger.info(f"Refreshed token saved successfully to {token_file_path}")
    except Exception as e:
        logger.error(f"Failed to save token file to {token_file_path}: {e}")

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
                    logger.debug(f"Token set_{token_index + 1} is in cooldown until {datetime.fromtimestamp(cooldown_end)}")
                    return False
                    
        # Check cache for healthy tokens (improved cache hit logic)
        if token_index in self.token_health_cache:
            cache_entry = self.token_health_cache[token_index]
            cache_age = time.time() - cache_entry['timestamp']
            if cache_age < self.health_check_interval and cache_entry.get('healthy', False):
                logger.debug(f"Using cached health status for set_{token_index + 1}: {cache_entry['healthy']}")
                return cache_entry['healthy']
        
        try:
            # A more robust health check is to see if the token can be refreshed.
            # This is platform-agnostic and confirms the refresh token is valid.
            creds = get_oauth_token_file(f"set_{token_index + 1}")
            if not creds:
                logger.warning(f"Token health check failed for set_{token_index + 1}: Could not load credentials.")
                self._update_health_cache(token_index, False)
                return False

            # If the token is expired or close to expiring, a refresh is attempted.
            # If it's valid, this does nothing. If it's invalid, it raises an exception.
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                # If refresh is successful, save the new token
                _save_oauth_token_file(creds, f"set_{token_index + 1}")

            logger.debug(f"Token health check passed for set_{token_index + 1}")
            self._update_health_cache(token_index, True)
            return True
            
        except Exception as e:
            logger.error(f"Token health check failed for set_{token_index + 1} during refresh: {e}")
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
        Rotates to the next available healthy token using parallel checking with fallback.
        
        Returns:
            Optional[int]: Index of the new token if successful, None if rotation failed
        """
        original_index = self.current_token_index
        all_indices = list(range(4))  # Assuming 4 token sets
        
        logger.info(f"🔄 Starting token rotation from set_{original_index + 1}")
        
        # Try all tokens in parallel first (improved parallel logic)
        try:
            healthy_token = await self._check_tokens_parallel(all_indices)
            if healthy_token is not None:
                self.current_token_index = healthy_token
                logger.info(f"✅ Parallel rotation successful to set_{self.current_token_index + 1}")
                return self.current_token_index
        except Exception as e:
            logger.warning(f"⚠️ Parallel token check failed: {e}, falling back to sequential")
            
        # If parallel check fails, fall back to sequential checking with retry logic
        for retry_attempt in range(self.max_retries):
            logger.info(f"🔄 Sequential rotation attempt {retry_attempt + 1}/{self.max_retries}")
            
            tokens_tried = 0
            while tokens_tried < 4:  # Try all 4 tokens
                # Try next token
                self.current_token_index = (self.current_token_index + 1) % 4
                tokens_tried += 1
                
                # Skip if we're back to the original (all tokens tried)
                if self.current_token_index == original_index and tokens_tried > 1:
                    logger.warning(f"⚠️ Completed full token cycle, no healthy tokens found")
                    break
                    
                # Check if token is healthy
                try:
                    if self.check_token_health(self.current_token_index):
                        logger.info(f"✅ Sequential rotation successful to set_{self.current_token_index + 1}")
                        return self.current_token_index
                except Exception as e:
                    logger.error(f"❌ Health check failed for set_{self.current_token_index + 1}: {e}")
                    continue
                    
            # If we get here, no healthy tokens found in this attempt
            if retry_attempt < self.max_retries - 1:
                logger.warning(f"⏳ Retry attempt {retry_attempt + 1} failed, waiting {self.retry_delay}s...")
                await asyncio.sleep(self.retry_delay)
            else:
                logger.error("❌ All retry attempts exhausted")
                
        # Reset to original index if rotation completely failed
        self.current_token_index = original_index
        logger.error(f"💥 Token rotation failed completely, staying with set_{original_index + 1}")
        return None

# Initialize token manager
token_manager = TokenManager() 