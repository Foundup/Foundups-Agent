#!/usr/bin/env python3
"""
Stream Configuration Module
Contains stream timing and retry settings extracted from stream_resolver.py

WSP 62: Large File Refactoring - Extracted vibecoded configuration
WSP 70: Externalized configuration for maintainability
"""

import os
from typing import Optional


class StreamResolverConfig:
    """
    Configuration class for stream resolver timing and retry settings.
    Extracted from vibecoded functionality in stream_resolver.py.
    """

    def __init__(self):
        # Dynamic rate limiting constants
        self.MIN_DELAY = float(os.getenv("STREAM_RESOLVER_MIN_DELAY", "5.0"))  # Minimum delay in seconds (high activity)
        self.MAX_DELAY = float(os.getenv("STREAM_RESOLVER_MAX_DELAY", "1800.0"))  # Maximum delay in seconds (30 minutes for idle)
        self.CHECK_INTERVAL = float(os.getenv("STREAM_RESOLVER_CHECK_INTERVAL", "1800.0"))  # Check every 30 minutes when no stream
        self.MAX_RETRIES = int(os.getenv("STREAM_RESOLVER_MAX_RETRIES", "3"))  # maximum number of retries for quota errors
        self.QUOTA_ERROR_DELAY = float(os.getenv("STREAM_RESOLVER_QUOTA_ERROR_DELAY", "30.0"))  # Fixed delay for quota errors
        self.JITTER_FACTOR = float(os.getenv("STREAM_RESOLVER_JITTER_FACTOR", "0.2"))  # Random jitter factor (±20%)
        self.INITIAL_DELAY = float(os.getenv("STREAM_RESOLVER_INITIAL_DELAY", "10.0"))  # Initial delay when no previous delay exists
        self.MAX_CONSECUTIVE_FAILURES = int(os.getenv("STREAM_RESOLVER_MAX_CONSECUTIVE_FAILURES", "5"))  # Maximum number of consecutive failures

        # Enhanced retry configuration
        self.EXPONENTIAL_BACKOFF_BASE = float(os.getenv("STREAM_RESOLVER_BACKOFF_BASE", "2.0"))  # Base for exponential backoff
        self.MAX_BACKOFF_DELAY = float(os.getenv("STREAM_RESOLVER_MAX_BACKOFF_DELAY", "300.0"))  # Maximum backoff delay (5 minutes)
        self.CIRCUIT_BREAKER_THRESHOLD = int(os.getenv("STREAM_RESOLVER_CIRCUIT_BREAKER_THRESHOLD", "10"))  # Failures before circuit breaker opens
        self.CIRCUIT_BREAKER_TIMEOUT = int(os.getenv("STREAM_RESOLVER_CIRCUIT_BREAKER_TIMEOUT", "600"))  # Circuit breaker timeout (10 minutes)

        # Development override for faster testing
        self.FORCE_DEV_DELAY = os.getenv("FORCE_DEV_DELAY", "false").lower() == "true"

        # Load channel ID from environment with validation
        self.CHANNEL_ID = self._get_channel_id()

        # Additional channel IDs
        self.CHANNEL_ID2 = os.getenv('CHANNEL_ID2')
        self.MOVE2JAPAN_CHANNEL_ID = os.getenv('MOVE2JAPAN_CHANNEL_ID', 'UCklMTNnu5POwRmQsg5JJumA')

    def _get_channel_id(self) -> str:
        """Get and validate primary channel ID."""
        channel_id = os.getenv("CHANNEL_ID")
        if not channel_id:
            raise ValueError("CHANNEL_ID must be defined in environment variables")
        return channel_id


# Global configuration instance
config = StreamResolverConfig()

# Expose module-level constants for test patching (backward compatibility)
FORCE_DEV_DELAY = config.FORCE_DEV_DELAY
MIN_DELAY = config.MIN_DELAY
MAX_DELAY = config.MAX_DELAY
MAX_RETRIES = config.MAX_RETRIES
QUOTA_ERROR_DELAY = config.QUOTA_ERROR_DELAY
JITTER_FACTOR = config.JITTER_FACTOR
INITIAL_DELAY = config.INITIAL_DELAY
MAX_CONSECUTIVE_FAILURES = config.MAX_CONSECUTIVE_FAILURES
CHANNEL_ID = config.CHANNEL_ID
