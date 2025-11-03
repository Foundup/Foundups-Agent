#!/usr/bin/env python3
"""
Stream End Detector - No-Quota Stream Status Monitoring
WSP 86: Uses web scraping to detect when streams end without API quota
"""

import logging
import asyncio
from typing import Optional, Tuple
from modules.platform_integration.stream_resolver.src.no_quota_stream_checker import NoQuotaStreamChecker

logger = logging.getLogger(__name__)


class StreamEndDetector:
    """Detect stream end using no-quota web scraping"""

    def __init__(self):
        self.checker = NoQuotaStreamChecker()
        self.last_known_status = None
        self.check_count = 0

    async def check_stream_status(self, video_id: str) -> Tuple[bool, str]:
        """
        Check if a stream is still live using no-quota scraping.

        Returns:
            Tuple of (is_live, status_message)
        """
        try:
            logger.info(f"[SEARCH] Checking stream status for {video_id} (no quota)...")

            # Use the no-quota checker
            result = await asyncio.to_thread(
                self.checker.check_video_is_live,
                video_id
            )

            is_live = result.get("live", False)
            title = result.get("title", "Unknown")

            self.check_count += 1

            # Detect status change
            if self.last_known_status is not None and self.last_known_status != is_live:
                if not is_live:
                    logger.warning(f"[U+1F51A] STREAM ENDED: {title}")
                    logger.info(f"[DATA] Detected after {self.check_count} checks (0 API units used)")
                    return False, f"Stream '{title}' has ended"
                else:
                    logger.info(f"[U+1F3AC] STREAM STARTED: {title}")
                    return True, f"Stream '{title}' is now live"

            self.last_known_status = is_live

            if is_live:
                logger.info(f"[OK] Stream still live: {title}")
                return True, f"Stream '{title}' is live"
            else:
                logger.info(f"[FAIL] Stream not live: {title}")
                return False, f"Stream '{title}' is not live"

        except Exception as e:
            logger.error(f"Error checking stream status: {e}")
            # On error, assume stream is still live to avoid false positives
            return True, f"Could not verify stream status: {e}"

    async def monitor_stream_until_end(self, video_id: str, check_interval: int = 120):
        """
        Monitor a stream until it ends using no-quota scraping.

        Args:
            video_id: YouTube video ID to monitor
            check_interval: Seconds between checks (default 2 minutes)
        """
        logger.info(f"[U+1F441]️ Starting no-quota stream monitoring for {video_id}")
        logger.info(f"⏱️ Will check every {check_interval} seconds")

        # Reset state for new monitoring session
        self.last_known_status = True  # Assume live when starting
        self.check_count = 0

        while True:
            is_live, message = await self.check_stream_status(video_id)

            if not is_live:
                logger.warning(f"[STOP] Stream ended: {message}")
                logger.info(f"[U+1F4B0] Total quota saved: {self.check_count} API units")
                return False  # Stream ended

            logger.info(f"[U+1F4A4] Sleeping {check_interval}s until next check...")
            await asyncio.sleep(check_interval)

    def reset(self):
        """Reset detector state for new stream"""
        self.last_known_status = None
        self.check_count = 0
        logger.info("[REFRESH] Stream end detector reset")


async def test_detector():
    """Test the stream end detector"""
    detector = StreamEndDetector()

    # Test with a video ID (replace with actual stream)
    test_video_id = "xL_kGmZj3R8"  # Example

    # Check once
    is_live, message = await detector.check_stream_status(test_video_id)
    print(f"Status: {message}")

    # Monitor until end (for testing, use short interval)
    # await detector.monitor_stream_until_end(test_video_id, check_interval=30)


if __name__ == "__main__":
    asyncio.run(test_detector())