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

Test suite for session_utils module
WSP 34: Comprehensive test coverage for infrastructure utilities
"""

import pytest
import json
import os
import tempfile
from datetime import datetime, timedelta
from unittest.mock import patch

from modules.infrastructure.shared_utilities.session_utils import SessionUtils


class TestSessionUtils:
    """Test cases for SessionUtils functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_file = os.path.join(self.temp_dir, "test_cache.json")

    def teardown_method(self):
        """Clean up test fixtures."""
        # Remove test cache file if it exists
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
        os.rmdir(self.temp_dir)

    def test_load_cache_nonexistent_file(self):
        """Test loading cache from non-existent file returns None."""
        result = SessionUtils.load_cache("nonexistent.json")
        assert result is None

    def test_load_cache_empty_file(self):
        """Test loading cache from empty file returns None."""
        with open(self.cache_file, 'w') as f:
            f.write("")

        result = SessionUtils.load_cache(self.cache_file)
        assert result is None

    def test_load_cache_valid_file(self):
        """Test loading cache from valid JSON file."""
        test_data = {
            "VIDEO_123": {
                "chat_id": "CHAT_456",
                "timestamp": "2025-01-13T10:00:00",
                "title": "Test Stream"
            }
        }

        with open(self.cache_file, 'w') as f:
            json.dump(test_data, f)

        result = SessionUtils.load_cache(self.cache_file)
        assert result == test_data

    def test_save_cache_creates_file(self):
        """Test saving cache creates the cache file."""
        result = SessionUtils.save_cache("VIDEO_123", "CHAT_456", self.cache_file)
        assert result is True
        assert os.path.exists(self.cache_file)

        # Verify content
        with open(self.cache_file, 'r') as f:
            data = json.load(f)

        assert "VIDEO_123" in data
        assert data["VIDEO_123"]["chat_id"] == "CHAT_456"
        assert "timestamp" in data["VIDEO_123"]

    def test_save_cache_updates_existing(self):
        """Test saving cache updates existing entries."""
        # Create initial cache
        initial_data = {"VIDEO_123": {"chat_id": "OLD_CHAT", "timestamp": "2025-01-13T09:00:00"}}
        with open(self.cache_file, 'w') as f:
            json.dump(initial_data, f)

        # Update cache
        result = SessionUtils.save_cache("VIDEO_123", "NEW_CHAT", self.cache_file)
        assert result is True

        # Verify update
        with open(self.cache_file, 'r') as f:
            data = json.load(f)

        assert data["VIDEO_123"]["chat_id"] == "NEW_CHAT"
        # Should preserve any existing title if present
        assert "timestamp" in data["VIDEO_123"]

    def test_try_cached_stream_no_cache(self):
        """Test trying cached stream with no cache returns None."""
        result = SessionUtils.try_cached_stream(None)
        assert result == (None, None)

        result = SessionUtils.try_cached_stream({})
        assert result == (None, None)

    def test_try_cached_stream_recent_entry(self):
        """Test trying cached stream finds recent entries."""
        recent_time = datetime.now() - timedelta(hours=1)
        cache = {
            "VIDEO_123": {
                "chat_id": "CHAT_456",
                "timestamp": recent_time.isoformat()
            }
        }

        result = SessionUtils.try_cached_stream(cache)
        assert result == ("VIDEO_123", "CHAT_456")

    def test_try_cached_stream_expired_entry(self):
        """Test trying cached stream ignores expired entries."""
        old_time = datetime.now() - timedelta(hours=12)  # More than 6 hours ago
        cache = {
            "VIDEO_123": {
                "chat_id": "CHAT_456",
                "timestamp": old_time.isoformat()
            }
        }

        result = SessionUtils.try_cached_stream(cache)
        assert result == (None, None)

    def test_try_cached_stream_mixed_entries(self):
        """Test trying cached stream with mix of recent and expired entries."""
        recent_time = datetime.now() - timedelta(hours=1)
        old_time = datetime.now() - timedelta(hours=12)

        cache = {
            "OLD_VIDEO": {
                "chat_id": "OLD_CHAT",
                "timestamp": old_time.isoformat()
            },
            "RECENT_VIDEO": {
                "chat_id": "RECENT_CHAT",
                "timestamp": recent_time.isoformat()
            }
        }

        result = SessionUtils.try_cached_stream(cache)
        assert result == ("RECENT_VIDEO", "RECENT_CHAT")

    def test_try_cached_stream_invalid_timestamp(self):
        """Test trying cached stream handles invalid timestamps gracefully."""
        cache = {
            "VIDEO_123": {
                "chat_id": "CHAT_456",
                "timestamp": "invalid-timestamp"
            }
        }

        result = SessionUtils.try_cached_stream(cache)
        assert result == (None, None)

    def test_cleanup_expired_entries(self):
        """Test cleanup of expired cache entries."""
        recent_time = datetime.now() - timedelta(hours=1)
        old_time = datetime.now() - timedelta(hours=25)  # More than 24 hours ago

        cache = {
            "RECENT_VIDEO": {
                "chat_id": "RECENT_CHAT",
                "timestamp": recent_time.isoformat()
            },
            "OLD_VIDEO": {
                "chat_id": "OLD_CHAT",
                "timestamp": old_time.isoformat()
            }
        }

        with open(self.cache_file, 'w') as f:
            json.dump(cache, f)

        removed_count = SessionUtils.cleanup_expired_entries(self.cache_file, max_age_hours=24)

        assert removed_count == 1

        # Verify only recent entry remains
        with open(self.cache_file, 'r') as f:
            data = json.load(f)

        assert "RECENT_VIDEO" in data
        assert "OLD_VIDEO" not in data

    def test_backward_compatibility_functions(self):
        """Test backward compatibility functions work."""
        from modules.infrastructure.shared_utilities.session_utils import (
            load_session_cache, save_session_cache, try_cached_stream
        )

        # Test they exist and are callable
        assert callable(load_session_cache)
        assert callable(save_session_cache)
        assert callable(try_cached_stream)

        # Test basic functionality
        result = save_session_cache("VIDEO_123", "CHAT_456", self.cache_file)
        assert result is True

        cache = load_session_cache(self.cache_file)
        assert cache is not None
        assert "VIDEO_123" in cache

        video_id, chat_id = try_cached_stream(cache)
        assert video_id == "VIDEO_123"
        assert chat_id == "CHAT_456"


if __name__ == "__main__":
    pytest.main([__file__])
