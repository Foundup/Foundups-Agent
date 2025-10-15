#!/usr/bin/env python3
"""
Session Cache Module for Stream Resolver
Handles session caching functionality extracted from stream_resolver.py

WSP 62: Large File Refactoring - Extracted vibecoded caching logic
"""

import os
import json
import logging
from typing import Optional, Dict, Any, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class SessionCache:
    """
    Session cache for storing and retrieving stream session data.
    Extracted from vibecoded functionality in stream_resolver.py.
    """

    def __init__(self, cache_file: str = "memory/session_cache.json"):
        """
        Initialize session cache.

        Args:
            cache_file: Path to cache file
        """
        self.cache_file = Path(cache_file)
        self._ensure_memory_dir()
        self._cache = {}
        self.logger = logging.getLogger(__name__)

    def _ensure_memory_dir(self):
        """Ensure memory directory exists."""
        self.cache_file.parent.mkdir(exist_ok=True)

    def load_cache(self) -> Optional[Dict[str, Any]]:
        """
        Load session cache from file.

        Returns:
            Cache data or None if not available
        """
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)

                # Validate cache structure
                if isinstance(cache_data, dict) and 'video_id' in cache_data and 'chat_id' in cache_data:
                    self.logger.info("📂 Loaded valid session cache")
                    return cache_data
                else:
                    self.logger.warning("📂 Invalid cache structure, ignoring")
                    return None
            else:
                self.logger.debug("📂 No session cache file found")
                return None

        except (json.JSONDecodeError, IOError) as e:
            self.logger.warning(f"📂 Failed to load session cache: {e}")
            return None

    def save_cache(self, video_id: str, chat_id: str, title: Optional[str] = None):
        """
        Save session cache to file.

        Args:
            video_id: Video ID to cache
            chat_id: Chat ID to cache
            title: Optional stream title
        """
        try:
            cache_data = {
                'video_id': video_id,
                'chat_id': chat_id,
                'timestamp': self._current_timestamp(),
                'title': title or self._get_stream_title(video_id)
            }

            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"💾 Saved session cache for video {video_id[:12]}...")

        except Exception as e:
            self.logger.error(f"💾 Failed to save session cache: {e}")

    def try_cached_stream(self, cache: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
        """
        Try to use cached stream data.

        Args:
            cache: Cache data from load_cache()

        Returns:
            Tuple of (video_id, chat_id) if valid, (None, None) otherwise
        """
        if not cache:
            return None, None

        video_id = cache.get('video_id')
        chat_id = cache.get('chat_id')

        if video_id and chat_id:
            # Could add validation here to check if stream is still live
            self.logger.info(f"🔄 Using cached stream: {video_id[:12]}...")
            return video_id, chat_id

        return None, None

    def clear_cache(self):
        """Clear the session cache."""
        try:
            if self.cache_file.exists():
                self.cache_file.unlink()
                self.logger.info("🗑️ Cleared session cache")
        except Exception as e:
            self.logger.error(f"🗑️ Failed to clear session cache: {e}")

    def _current_timestamp(self) -> str:
        """Get current timestamp for cache metadata."""
        from datetime import datetime
        return datetime.now().isoformat()

    def _get_stream_title(self, video_id: str) -> Optional[str]:
        """
        Get stream title for cache metadata.
        This is a placeholder - actual implementation would use YouTube API.
        """
        # Placeholder - in real implementation this would fetch from YouTube API
        return f"Stream {video_id[:12]}..."


# Global cache instance for backward compatibility
session_cache = SessionCache()
