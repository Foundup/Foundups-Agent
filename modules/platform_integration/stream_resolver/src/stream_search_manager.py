#!/usr/bin/env python3
"""
Stream Search Manager - Intelligent search with reduced logging
WSP 87: Manages search intervals and logging to prevent spam

This module reduces log spam by:
1. Logging detailed info only on first search and changes
2. Using brief progress indicators for repeated searches
3. Implementing exponential backoff when no stream found
"""

import time
import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class StreamSearchManager:
    """Manages stream search with intelligent logging and delays"""

    def __init__(self):
        self.last_detailed_log = None
        self.search_count = 0
        self.last_search_time = None
        self.consecutive_failures = 0
        self.initial_delay = 10  # Start with 10 seconds
        self.max_delay = 120  # Cap at 2 minutes
        self.detailed_log_interval = 300  # Show detailed logs every 5 minutes

    def should_show_detailed_log(self) -> bool:
        """Determine if we should show detailed logging"""
        now = datetime.now()

        # Always show on first search
        if self.search_count == 0:
            return True

        # Show if 5 minutes have passed since last detailed log
        if self.last_detailed_log is None:
            return True

        if (now - self.last_detailed_log).total_seconds() > self.detailed_log_interval:
            return True

        return False

    def get_search_delay(self) -> float:
        """Calculate intelligent delay between searches"""
        if self.consecutive_failures < 5:
            # Quick retry for first few attempts (10-15 seconds)
            return self.initial_delay + (self.consecutive_failures * 2)
        elif self.consecutive_failures < 20:
            # Moderate backoff (20-60 seconds)
            return min(20 + (self.consecutive_failures * 4), 60)
        else:
            # Slow polling after many failures (60-120 seconds)
            return min(60 + (self.consecutive_failures * 2), self.max_delay)

    def log_search_start(self, channel_id: str, credential_set: int):
        """Log search start with intelligent verbosity"""
        self.search_count += 1

        if self.should_show_detailed_log():
            # Detailed logging
            logger.info("="*60)
            logger.info(f"[SEARCH] STREAM SEARCH INITIATED")
            logger.info(f"   Channel: {channel_id}")
            logger.info(f"   Credential Set: {credential_set}")
            logger.info(f"   Search #{self.search_count}")
            logger.info(f"   Consecutive Failures: {self.consecutive_failures}")
            logger.info("="*60)
            self.last_detailed_log = datetime.now()
        else:
            # Brief progress indicator
            if self.consecutive_failures > 0 and self.consecutive_failures % 10 == 0:
                logger.info(f"⏳ Still searching... (attempt #{self.search_count}, no stream found yet)")
            # Otherwise, stay quiet to reduce spam

    def log_search_result(self, found: bool, video_id: Optional[str] = None):
        """Log search result"""
        if found:
            logger.info(f"[OK] STREAM FOUND! Video ID: {video_id}")
            logger.info(f"   Found after {self.search_count} searches")
            self.consecutive_failures = 0
        else:
            self.consecutive_failures += 1
            # Only log failures periodically
            if self.consecutive_failures == 1:
                logger.info("[SEARCH] No active stream found, will continue searching...")
            elif self.consecutive_failures % 30 == 0:  # Every 30 attempts
                delay = self.get_search_delay()
                logger.info(f"[DATA] Status: {self.consecutive_failures} searches, no stream yet. Delay: {delay}s")

    def get_wait_message(self) -> str:
        """Get appropriate wait message based on failure count"""
        delay = self.get_search_delay()

        if self.consecutive_failures < 5:
            return f"Waiting {delay:.0f}s before next check..."
        elif self.consecutive_failures < 20:
            return f"No stream yet, waiting {delay:.0f}s (checking less frequently)..."
        else:
            return f"Stream appears offline, checking every {delay:.0f}s..."

    def reset(self):
        """Reset manager state when stream found"""
        self.consecutive_failures = 0
        self.search_count = 0
        self.last_detailed_log = None


# Global instance for use across module
search_manager = StreamSearchManager()