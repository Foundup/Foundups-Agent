#!/usr/bin/env python
"""
antifaFM Stream Orchestrator

Runs all stream automation features together:
- Video rotation (center content)
- News ticker (scrolling headlines)
- Layout management (positions all sources)

Usage:
    python -m antifafm_broadcaster.scripts.stream_orchestrator
    python -m antifafm_broadcaster.scripts.stream_orchestrator --video-interval 30 --ticker-interval 10
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from modules.platform_integration.antifafm_broadcaster.src.obs_controller import OBSController
from modules.platform_integration.antifafm_broadcaster.src.news_ticker import NewsTicker

# Default rotation videos
DEFAULT_VIDEOS = [
    "Off the Grid",
    "Charlie Chaplin",
    "Throw Tomatoes",
]


class StreamOrchestrator:
    """Orchestrates all antifaFM stream automation."""

    def __init__(
        self,
        video_interval: int = 30,
        ticker_interval: int = 10,
        videos: list = None,
    ):
        self.video_interval = video_interval
        self.ticker_interval = ticker_interval
        self.videos = videos or DEFAULT_VIDEOS
        self.controller = None
        self.ticker = None
        self.running = False
        self.current_video_index = 0

    async def connect(self) -> bool:
        """Connect to OBS."""
        host = os.getenv("OBS_WEBSOCKET_HOST", "localhost")
        self.controller = OBSController(host=host)
        return await self.controller.connect()

    async def apply_layout(self):
        """Apply the stream layout."""
        from modules.platform_integration.antifafm_broadcaster.scripts.apply_layout import LAYOUTS

        scene_name = await self.controller.get_current_scene()
        if not scene_name:
            return

        # Get list of sources in scene
        items = await self.controller.list_scene_items()
        source_names = [item['name'] for item in items]

        applied = 0
        for source_name, layout in LAYOUTS.items():
            if source_name in source_names:
                await self.controller.set_source_bounds(
                    source_name,
                    x=layout["x"],
                    y=layout["y"],
                    width=layout["width"],
                    height=layout["height"],
                )
                applied += 1

        print(f"[LAYOUT] Applied to {applied} sources")

    async def rotate_video(self):
        """Show next video in rotation."""
        if not self.controller or not self.controller.connected:
            return

        scene_name = await self.controller.get_current_scene()
        if not scene_name:
            return

        current_video = self.videos[self.current_video_index]

        # Hide all videos, show current
        for i, video in enumerate(self.videos):
            item_id = await self.controller.get_scene_item_id(video)
            if item_id:
                visible = (video == current_video)
                self.controller.ws.set_scene_item_enabled(scene_name, item_id, visible)

                if visible:
                    # Position in center
                    await self.controller.set_source_bounds(
                        video, x=320, y=180, width=1280, height=720
                    )

        print(f"[VIDEO] Now showing: {current_video}")

        # Advance to next video
        self.current_video_index = (self.current_video_index + 1) % len(self.videos)

    async def update_ticker(self):
        """Update news ticker to next headline."""
        if not self.ticker:
            return

        headline = self.ticker.get_current_headline()
        await self.ticker.update_ticker_text(headline)
        print(f"[TICKER] {headline}")
        self.ticker.next_headline()

    async def run(self):
        """Run the stream orchestrator."""
        print("=" * 60)
        print("antifaFM Stream Orchestrator")
        print("=" * 60)
        print(f"Video rotation: {self.video_interval}s interval")
        print(f"News ticker: {self.ticker_interval}s interval")
        print(f"Videos: {', '.join(self.videos)}")
        print("Press Ctrl+C to stop")
        print("=" * 60)

        if not await self.connect():
            print("[ERROR] Could not connect to OBS")
            return

        # Initialize ticker
        self.ticker = NewsTicker(interval=self.ticker_interval)
        self.ticker.load_headlines()
        self.ticker.controller = self.controller
        await self.ticker.create_ticker_source()

        # Apply initial layout
        await self.apply_layout()

        # Show first video
        await self.rotate_video()
        await self.update_ticker()

        self.running = True
        video_countdown = self.video_interval
        ticker_countdown = self.ticker_interval

        try:
            while self.running:
                await asyncio.sleep(1)

                # Video rotation countdown
                video_countdown -= 1
                if video_countdown <= 0:
                    await self.rotate_video()
                    video_countdown = self.video_interval

                # Ticker update countdown
                ticker_countdown -= 1
                if ticker_countdown <= 0:
                    await self.update_ticker()
                    # Reload headlines in case they were updated
                    self.ticker.load_headlines()
                    ticker_countdown = self.ticker_interval

        except KeyboardInterrupt:
            print("\n[STOP] Orchestrator stopped")

        finally:
            self.running = False
            if self.controller:
                self.controller.disconnect()

    def stop(self):
        """Stop the orchestrator."""
        self.running = False


async def quick_test():
    """Quick test - run for 30 seconds."""
    print("Quick test mode - running for 30 seconds...")

    orchestrator = StreamOrchestrator(
        video_interval=10,  # Faster for testing
        ticker_interval=5,
    )

    if not await orchestrator.connect():
        print("[ERROR] Could not connect to OBS")
        return

    # Initialize
    orchestrator.ticker = NewsTicker(interval=5)
    orchestrator.ticker.load_headlines()
    orchestrator.ticker.controller = orchestrator.controller
    await orchestrator.ticker.create_ticker_source()

    # Run for 30 seconds
    for i in range(6):  # 6 iterations of 5 seconds each
        print(f"\n--- Iteration {i+1}/6 ---")
        await orchestrator.rotate_video()
        await orchestrator.update_ticker()
        await asyncio.sleep(5)

    orchestrator.controller.disconnect()
    print("\n[DONE] Quick test complete")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="antifaFM Stream Orchestrator")
    parser.add_argument("--video-interval", type=int, default=30,
                        help="Seconds between video rotations (default: 30)")
    parser.add_argument("--ticker-interval", type=int, default=10,
                        help="Seconds between headline changes (default: 10)")
    parser.add_argument("--test", action="store_true",
                        help="Run quick 30-second test")

    args = parser.parse_args()

    if args.test:
        asyncio.run(quick_test())
    else:
        orchestrator = StreamOrchestrator(
            video_interval=args.video_interval,
            ticker_interval=args.ticker_interval,
        )
        asyncio.run(orchestrator.run())
