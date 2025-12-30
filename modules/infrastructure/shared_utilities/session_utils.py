# -*- coding: utf-8 -*-
import sys
import io


"""
# === UTF-8 ENFORCEMENT (WSP 90) ===
# Prevent UnicodeEncodeError on Windows systems
# Only apply when running as main script, not during import
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===

Session Utilities Module
Infrastructure utilities for session management and caching

WSP 3: Infrastructure Domain - Shared session management utilities
WSP 49: Module structure with clear responsibilities
WSP 62: Focused functionality (<200 lines)

Extracted from stream_resolver.py vibecoded functionality
"""

import os
import json
import logging
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SessionUtils:
    """
    Session management utilities extracted from stream_resolver.py

    Provides centralized session caching functionality for:
    - Video/Chat ID mapping persistence
    - Cache loading and saving
    - Cache validation and cleanup
    """

    DEFAULT_CACHE_FILE = "memory/session_cache.json"

    @staticmethod
    def load_cache(cache_file: str = None) -> Optional[Dict[str, Any]]:
        """
        Load session cache from JSON file.

        Args:
            cache_file: Path to cache file (uses default if None)

        Returns:
            Cache dictionary or None if loading fails
        """
        cache_path = cache_file or SessionUtils.DEFAULT_CACHE_FILE

        try:
            if not os.path.exists(cache_path):
                logger.debug(f"Cache file {cache_path} does not exist")
                return None

            with open(cache_path, 'r', encoding='utf-8') as f:
                cache = json.load(f)

            logger.debug(f"Loaded cache with {len(cache)} entries from {cache_path}")
            return cache

        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load cache from {cache_path}: {e}")
            return None

    @staticmethod
    def save_cache(
        video_id: str,
        chat_id: str,
        cache_file: str = None,
        channel_id: Optional[str] = None,
        title: Optional[str] = None,
    ) -> bool:
        """
        Save video/chat ID mapping to cache.

        Args:
            video_id: YouTube video ID
            chat_id: Live chat ID
            cache_file: Path to cache file (uses default if None)
            channel_id: Optional channel ID for allowlist validation
            title: Optional stream title

        Returns:
            True if saved successfully, False otherwise
        """
        cache_path = cache_file or SessionUtils.DEFAULT_CACHE_FILE

        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)

            # Load existing cache or create new
            cache = SessionUtils.load_cache(cache_path) or {}

            # Update cache with new mapping
            existing = cache.get(video_id, {})
            existing_title = existing.get('title') if isinstance(existing, dict) else None
            existing_channel = existing.get('channel_id') if isinstance(existing, dict) else None

            cache_entry = {
                'chat_id': chat_id,
                'timestamp': datetime.now().isoformat(),
            }
            if title or existing_title:
                cache_entry['title'] = title or existing_title
            if channel_id or existing_channel:
                cache_entry['channel_id'] = channel_id or existing_channel

            cache[video_id] = cache_entry

            # Save updated cache
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache, f, indent=2, ensure_ascii=False)

            logger.debug(f"Saved cache entry: {video_id} -> {chat_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to save cache to {cache_path}: {e}")
            return False

    @staticmethod
    def try_cached_stream(
        cache: Dict[str, Any],
        allowed_channel_ids: Optional[List[str]] = None,
        require_channel_id: bool = False,
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Try to find an active stream from cache.

        Args:
            cache: Cache dictionary from load_cache()
            allowed_channel_ids: Optional allowlist of channel IDs
            require_channel_id: If True, skip entries without channel_id

        Returns:
            Tuple of (video_id, chat_id) if found, (None, None) otherwise
        """
        if not cache:
            return None, None

        try:
            # Look for recent entries (within last 6 hours)
            cutoff_time = datetime.now() - timedelta(hours=6)
            allowed_set = set(allowed_channel_ids or [])

            for video_id, data in cache.items():
                if isinstance(data, dict) and 'timestamp' in data and 'chat_id' in data:
                    try:
                        entry_time = datetime.fromisoformat(data['timestamp'])
                        if entry_time > cutoff_time:
                            channel_id = data.get('channel_id')
                            if allowed_set:
                                if not channel_id and require_channel_id:
                                    logger.info(f"[CACHE] Skipping cached stream without channel_id: {video_id}")
                                    continue
                                if channel_id and channel_id not in allowed_set:
                                    logger.info(f"[CACHE] Skipping cached stream for non-allowed channel: {channel_id}")
                                    continue
                            chat_id = data['chat_id']
                            logger.info(f"Found cached active stream: {video_id} -> {chat_id}")
                            return video_id, chat_id
                    except (ValueError, TypeError) as e:
                        logger.debug(f"Invalid timestamp in cache entry {video_id}: {e}")
                        continue

            logger.debug("No recent cached streams found")
            return None, None

        except Exception as e:
            logger.error(f"Error processing cache: {e}")
            return None, None

    @staticmethod
    def cleanup_expired_entries(cache_file: str = None, max_age_hours: int = 24) -> int:
        """
        Clean up expired cache entries.

        Args:
            cache_file: Path to cache file (uses default if None)
            max_age_hours: Maximum age in hours for cache entries

        Returns:
            Number of entries removed
        """
        cache_path = cache_file or SessionUtils.DEFAULT_CACHE_FILE

        try:
            cache = SessionUtils.load_cache(cache_path)
            if not cache:
                return 0

            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            cleaned_cache = {}

            for video_id, data in cache.items():
                if isinstance(data, dict) and 'timestamp' in data:
                    try:
                        entry_time = datetime.fromisoformat(data['timestamp'])
                        if entry_time > cutoff_time:
                            cleaned_cache[video_id] = data
                    except (ValueError, TypeError):
                        # Keep entries with invalid timestamps (they might be salvageable)
                        cleaned_cache[video_id] = data

            removed_count = len(cache) - len(cleaned_cache)

            if removed_count > 0:
                with open(cache_path, 'w', encoding='utf-8') as f:
                    json.dump(cleaned_cache, f, indent=2, ensure_ascii=False)
                logger.info(f"Cleaned up {removed_count} expired cache entries")

            return removed_count

        except Exception as e:
            logger.error(f"Error during cache cleanup: {e}")
            return 0


# Convenience functions for backward compatibility
def load_session_cache(cache_file: str = None) -> Optional[Dict[str, Any]]:
    """Backward compatibility function."""
    return SessionUtils.load_cache(cache_file)

def save_session_cache(
    video_id: str,
    chat_id: str,
    cache_file: str = None,
    channel_id: Optional[str] = None,
    title: Optional[str] = None,
) -> bool:
    """Backward compatibility function."""
    return SessionUtils.save_cache(
        video_id,
        chat_id,
        cache_file=cache_file,
        channel_id=channel_id,
        title=title,
    )

def try_cached_stream(
    cache: Dict[str, Any],
    allowed_channel_ids: Optional[List[str]] = None,
    require_channel_id: bool = False,
) -> Tuple[Optional[str], Optional[str]]:
    """Backward compatibility function."""
    return SessionUtils.try_cached_stream(
        cache,
        allowed_channel_ids=allowed_channel_ids,
        require_channel_id=require_channel_id,
    )
