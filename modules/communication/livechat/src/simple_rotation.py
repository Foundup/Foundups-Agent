"""
Simple In-Browser Rotation - Uses Existing TarsAccountSwapper
==============================================================

WSP 77 Compliant: Uses existing account switching, no subprocess spawning.

ARCHITECTURE (Occam's Razor):
  - Single browser connection (Edge 9223 or Chrome 9222)
  - Use TarsAccountSwapper to rotate between accounts
  - Run engagement on each account sequentially
  - Per-channel timeout with asyncio.wait_for()

FLOW:
  ┌─────────────────────────────────────────────────────────────────┐
  │  Edge (port 9223):                                              │
  │    1. Connect to existing browser                               │
  │    2. FoundUps: navigate → engage → (timeout: 5 min)            │
  │    3. Swap to antifaFM (avatar → switch account → select)       │
  │    4. antifaFM: navigate → engage → (timeout: 5 min)            │
  │    5. Done                                                      │
  └─────────────────────────────────────────────────────────────────┘

DOM Path for Account Switching (012 documented):
  1. Click avatar: #avatar-btn
  2. Click "Switch account": tp-yt-paper-item with text "Switch account"
  3. Select account: ytd-account-item-renderer[index]
     - FoundUps: section 1, index 0
     - antifaFM: section 1, index 1

Author: 0102
Created: 2026-02-27
"""

import asyncio
import logging
import os
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


@dataclass
class ChannelResult:
    """Result from processing a single channel."""
    channel: str
    success: bool
    comments_processed: int
    elapsed_seconds: float
    error: Optional[str] = None


@dataclass
class RotationResult:
    """Result from a full rotation."""
    browser: str
    channels: List[ChannelResult]
    total_comments: int
    elapsed_seconds: float

    @property
    def successful_channels(self) -> List[str]:
        return [c.channel for c in self.channels if c.success]

    @property
    def failed_channels(self) -> List[str]:
        return [c.channel for c in self.channels if not c.success]


class SimpleRotation:
    """
    Simple in-browser rotation using TarsAccountSwapper.

    No subprocess spawning - just connect, swap, engage.
    """

    BROWSER_PORTS = {
        "chrome": 9222,
        "edge": 9223,
    }

    BROWSER_CHANNELS = {
        "edge": ["FoundUps", "antifaFM"],
        "chrome": ["Move2Japan", "UnDaoDu"],
    }

    def __init__(
        self,
        browser: str = "edge",
        channel_timeout: float = 300.0,  # 5 min per channel
    ):
        self.browser = browser
        self.port = self.BROWSER_PORTS.get(browser, 9223)
        self.channel_timeout = channel_timeout
        self.driver = None
        self.swapper = None

        logger.info(f"[SIMPLE-ROTATION] Initialized for {browser} (port {self.port})")
        logger.info(f"[SIMPLE-ROTATION] Channel timeout: {channel_timeout}s")

    async def connect(self) -> bool:
        """Connect to the browser."""
        try:
            from modules.infrastructure.dependency_launcher.src.dae_dependencies import (
                connect_edge_with_retry,
                connect_chrome_with_retry,
            )

            logger.info(f"[SIMPLE-ROTATION] Connecting to {self.browser} on port {self.port}...")

            if self.browser == "edge":
                self.driver = await asyncio.to_thread(
                    connect_edge_with_retry,
                    max_retries=3,
                    retry_delay=2.0,
                    relaunch_on_fail=True,
                )
            else:
                self.driver = await asyncio.to_thread(
                    connect_chrome_with_retry,
                    max_retries=3,
                    retry_delay=2.0,
                    relaunch_on_fail=True,
                )

            if self.driver is None:
                logger.error(f"[SIMPLE-ROTATION] Failed to connect to {self.browser}")
                return False

            # Initialize account swapper
            from modules.communication.video_comments.skillz.tars_account_swapper.account_swapper_skill import TarsAccountSwapper
            self.swapper = TarsAccountSwapper(self.driver, ui_tars_verify=False)

            logger.info(f"[SIMPLE-ROTATION] Connected successfully")
            return True

        except Exception as e:
            logger.error(f"[SIMPLE-ROTATION] Connection failed: {e}")
            return False

    async def _process_channel(
        self,
        channel: str,
        max_comments: int = 10,
    ) -> ChannelResult:
        """
        Process a single channel: navigate → engage → return stats.

        Uses asyncio.wait_for for per-channel timeout.
        """
        start_time = time.time()
        result = ChannelResult(
            channel=channel,
            success=False,
            comments_processed=0,
            elapsed_seconds=0,
        )

        try:
            logger.info(f"[SIMPLE-ROTATION] Processing {channel}...")

            # Navigate to channel's comment inbox
            await self.swapper.navigate_to_comments(channel)
            await asyncio.sleep(3)  # Wait for page load

            # Check for OOPS page
            if self.swapper._is_permission_error():
                logger.warning(f"[SIMPLE-ROTATION] OOPS page on {channel} - attempting account switch")
                # Try to recover via account picker
                success = await self.swapper.swap_from_oops_page(channel)
                if not success:
                    result.error = "OOPS page - account switch failed"
                    result.elapsed_seconds = time.time() - start_time
                    return result
                await asyncio.sleep(3)

            # Run comment engagement with timeout
            logger.info(f"[SIMPLE-ROTATION] Running engagement for {channel} (timeout: {self.channel_timeout}s)...")

            from modules.communication.video_comments.skillz.tars_like_heart_reply.comment_engagement_dae import CommentEngagementDAE

            # Get channel ID
            channel_id = self.swapper.CHANNELS.get(channel, {}).get("id")
            if not channel_id:
                result.error = f"Unknown channel: {channel}"
                result.elapsed_seconds = time.time() - start_time
                return result

            # Create DAE for this channel (reusing driver)
            dae = CommentEngagementDAE(
                channel_id=channel_id,
                use_vision=False,
                use_dom=True,
            )
            dae.driver = self.driver  # Reuse existing connection

            # Run engagement with timeout
            try:
                engage_result = await asyncio.wait_for(
                    dae.engage_all_comments(
                        max_comments=max_comments,
                        do_like=True,
                        do_heart=True,
                        do_reply=True,
                        use_intelligent_reply=True,
                    ),
                    timeout=self.channel_timeout,
                )

                stats = engage_result.get("stats", {})
                result.comments_processed = stats.get("comments_processed", 0)
                result.success = True
                logger.info(f"[SIMPLE-ROTATION] {channel} complete: {result.comments_processed} comments")

            except asyncio.TimeoutError:
                logger.warning(f"[SIMPLE-ROTATION] {channel} TIMEOUT after {self.channel_timeout}s")
                result.error = f"Timeout after {self.channel_timeout}s"

        except Exception as e:
            logger.error(f"[SIMPLE-ROTATION] {channel} failed: {e}")
            result.error = str(e)

        result.elapsed_seconds = time.time() - start_time
        return result

    async def run_rotation(
        self,
        channels: List[str] = None,
        max_comments: int = 10,
    ) -> RotationResult:
        """
        Run rotation across all channels.

        For Edge: FoundUps → (swap) → antifaFM
        For Chrome: Move2Japan → (swap) → UnDaoDu
        """
        if channels is None:
            channels = self.BROWSER_CHANNELS.get(self.browser, [])

        rotation_start = time.time()
        results: List[ChannelResult] = []
        total_comments = 0

        tag = self.browser.upper()
        logger.info("")
        logger.info("=" * 60)
        logger.info(f"[{tag}] SIMPLE ROTATION STARTING")
        logger.info(f"[{tag}] Channels: {' → '.join(channels)}")
        logger.info(f"[{tag}] Timeout: {self.channel_timeout}s per channel")
        logger.info("=" * 60)

        # Connect to browser
        if not await self.connect():
            return RotationResult(
                browser=self.browser,
                channels=[],
                total_comments=0,
                elapsed_seconds=time.time() - rotation_start,
            )

        for idx, channel in enumerate(channels):
            logger.info("")
            logger.info(f"[{tag}] [{idx + 1}/{len(channels)}] {channel}")
            logger.info("-" * 40)

            # For first channel: just navigate
            # For subsequent channels: swap account first, then navigate
            if idx > 0:
                logger.info(f"[{tag}] Swapping to {channel}...")
                # Swap to account (don't navigate yet - _process_channel will do it)
                swap_success = await self.swapper.swap_to(channel, navigate_to_comments=False)
                if not swap_success:
                    logger.warning(f"[{tag}] Swap to {channel} failed - will try direct navigation")
                await asyncio.sleep(2)

            # Process channel (navigates to inbox, handles OOPS, runs engagement)
            result = await self._process_channel(channel, max_comments)
            results.append(result)
            total_comments += result.comments_processed

            if result.success:
                logger.info(f"[{tag}] ✅ {channel}: {result.comments_processed} comments ({result.elapsed_seconds:.1f}s)")
            else:
                logger.warning(f"[{tag}] ❌ {channel}: {result.error} ({result.elapsed_seconds:.1f}s)")

        elapsed = time.time() - rotation_start

        logger.info("")
        logger.info("=" * 60)
        logger.info(f"[{tag}] ROTATION COMPLETE")
        logger.info(f"[{tag}] Channels: {len([r for r in results if r.success])}/{len(channels)} successful")
        logger.info(f"[{tag}] Comments: {total_comments}")
        logger.info(f"[{tag}] Time: {elapsed:.1f}s")
        logger.info("=" * 60)

        return RotationResult(
            browser=self.browser,
            channels=results,
            total_comments=total_comments,
            elapsed_seconds=elapsed,
        )


# =============================================================================
# CLI Entry Point
# =============================================================================

async def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Simple In-Browser Rotation")
    parser.add_argument("--browser", default="edge", choices=["chrome", "edge"])
    parser.add_argument("--max-comments", type=int, default=10)
    parser.add_argument("--timeout", type=int, default=300, help="Per-channel timeout (seconds)")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    rotation = SimpleRotation(
        browser=args.browser,
        channel_timeout=args.timeout,
    )

    result = await rotation.run_rotation(
        max_comments=args.max_comments,
    )

    print(f"\nResults: {len(result.successful_channels)}/{len(result.channels)} channels, {result.total_comments} comments")


if __name__ == "__main__":
    asyncio.run(main())
