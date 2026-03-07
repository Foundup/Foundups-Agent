#!/usr/bin/env python
"""
Video Rotator for antifaFM OBS Stream

Automatically cycles through videos, showing one at a time in the center area.

Usage:
    python -m antifafm_broadcaster.scripts.video_rotator
    python -m antifafm_broadcaster.scripts.video_rotator --interval 60  # 60 seconds per video
"""

import asyncio
import os
import sys
import time
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from modules.platform_integration.antifafm_broadcaster.src.obs_controller import OBSController

# Videos to rotate through (names as they appear in OBS)
ROTATION_VIDEOS = [
    "Off the Grid",
    "Charlie Chaplin",
    "Throw Tomatoes",
]

# Default rotation interval in seconds
DEFAULT_INTERVAL = 30


class VideoRotator:
    """Rotates through videos in OBS, showing one at a time."""

    def __init__(self, interval: int = DEFAULT_INTERVAL):
        self.interval = interval
        self.controller = None
        self.current_index = 0
        self.running = False

    async def connect(self) -> bool:
        """Connect to OBS."""
        host = os.getenv("OBS_WEBSOCKET_HOST", "localhost")
        self.controller = OBSController(host=host)
        return await self.controller.connect()

    async def set_video_visibility(self, video_name: str, visible: bool) -> bool:
        """Show or hide a video source."""
        if not self.controller or not self.controller.connected:
            return False

        try:
            scene_name = await self.controller.get_current_scene()
            item_id = await self.controller.get_scene_item_id(video_name)

            if not scene_name or not item_id:
                print(f"  [SKIP] {video_name} not found in scene")
                return False

            self.controller.ws.set_scene_item_enabled(scene_name, item_id, visible)
            return True

        except Exception as e:
            print(f"  [ERROR] {video_name}: {e}")
            return False

    async def show_video(self, video_name: str):
        """Show one video, hide all others."""
        print(f"\n[ROTATE] Showing: {video_name}")

        # Hide all rotation videos
        for name in ROTATION_VIDEOS:
            if name != video_name:
                await self.set_video_visibility(name, False)

        # Show the selected video
        await self.set_video_visibility(video_name, True)

        # Position it in the center
        await self.controller.set_source_bounds(
            video_name,
            x=320, y=180,  # Center position
            width=1280, height=720
        )

    async def rotate_once(self):
        """Advance to next video."""
        video_name = ROTATION_VIDEOS[self.current_index]
        await self.show_video(video_name)
        self.current_index = (self.current_index + 1) % len(ROTATION_VIDEOS)

    async def run(self):
        """Run the rotation loop."""
        print("=" * 60)
        print("antifaFM Video Rotator")
        print("=" * 60)
        print(f"Interval: {self.interval} seconds")
        print(f"Videos: {', '.join(ROTATION_VIDEOS)}")
        print("Press Ctrl+C to stop")
        print("=" * 60)

        if not await self.connect():
            print("[ERROR] Could not connect to OBS")
            return

        self.running = True

        try:
            while self.running:
                await self.rotate_once()

                # Wait for interval (check running flag periodically)
                for _ in range(self.interval):
                    if not self.running:
                        break
                    await asyncio.sleep(1)

        except KeyboardInterrupt:
            print("\n[STOP] Rotation stopped by user")

        finally:
            self.running = False
            if self.controller:
                self.controller.disconnect()

    def stop(self):
        """Stop the rotation loop."""
        self.running = False


async def rotate_videos(interval: int = DEFAULT_INTERVAL):
    """Convenience function to start rotation."""
    rotator = VideoRotator(interval=interval)
    await rotator.run()


async def show_all_videos():
    """Show all videos (for testing layout)."""
    print("=" * 60)
    print("Showing ALL Videos")
    print("=" * 60)

    host = os.getenv("OBS_WEBSOCKET_HOST", "localhost")
    controller = OBSController(host=host)

    if not await controller.connect():
        print("[ERROR] Could not connect to OBS")
        return

    for video_name in ROTATION_VIDEOS:
        try:
            scene_name = await controller.get_current_scene()
            item_id = await controller.get_scene_item_id(video_name)
            if scene_name and item_id:
                controller.ws.set_scene_item_enabled(scene_name, item_id, True)
                print(f"  [OK] Enabled: {video_name}")
        except Exception as e:
            print(f"  [ERROR] {video_name}: {e}")

    controller.disconnect()
    print("\n[DONE] All videos visible")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Rotate videos in OBS")
    parser.add_argument("--interval", type=int, default=DEFAULT_INTERVAL,
                        help=f"Seconds between rotations (default: {DEFAULT_INTERVAL})")
    parser.add_argument("--show-all", action="store_true",
                        help="Show all videos instead of rotating")

    args = parser.parse_args()

    if args.show_all:
        asyncio.run(show_all_videos())
    else:
        asyncio.run(rotate_videos(interval=args.interval))
