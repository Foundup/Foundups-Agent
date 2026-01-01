"""
YouTube Shorts Scheduler - Main Orchestrator

WSP 80 DAE pattern for automated Shorts scheduling.
Connects to Chrome (9222) or Edge (9223) debug sessions.
"""

import asyncio
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.common.exceptions import WebDriverException

from .channel_config import get_channel_config, CHANNELS
from .dom_automation import YouTubeStudioDOM
from .schedule_tracker import ScheduleTracker
from .content_generator import (
    generate_clickbait_title,
    get_standard_description,
    generate_description_with_context,
)

logger = logging.getLogger(__name__)


class YouTubeShortsScheduler:
    """
    Main orchestrator for YouTube Shorts scheduling automation.

    Supports:
    - Move2Japan (Chrome 9222)
    - UnDaoDu (Chrome 9222)
    - FoundUps (Edge 9223)

    Usage:
        scheduler = YouTubeShortsScheduler("move2japan")
        await scheduler.run_scheduling_cycle(max_videos=10)
    """

    def __init__(
        self,
        channel_key: str,
        storage_dir: Optional[Path] = None,
        dry_run: bool = False,
    ):
        """
        Initialize scheduler for a channel.

        Args:
            channel_key: "move2japan", "undaodu", or "foundups"
            storage_dir: Optional custom storage directory
            dry_run: If True, don't actually make changes
        """
        self.channel_key = channel_key.lower()
        self.config = get_channel_config(self.channel_key)

        if not self.config:
            raise ValueError(f"Unknown channel: {channel_key}")

        self.channel_id = self.config["id"]
        self.channel_name = self.config["name"]
        self.chrome_port = self.config["chrome_port"]
        self.time_slots = self.config["time_slots"]
        self.max_per_day = self.config["max_per_day"]
        self.dry_run = dry_run

        # Initialize tracker
        self.tracker = ScheduleTracker(self.channel_id, storage_dir)

        # Driver and DOM (initialized on connect)
        self.driver = None
        self.dom = None

        logger.info(f"[SCHEDULER] Initialized for {self.channel_name} (port {self.chrome_port})")

    # =========================================
    # BROWSER CONNECTION
    # =========================================

    def connect_browser(self) -> bool:
        """
        Connect to existing Chrome/Edge debug session.

        Returns:
            True if connected successfully
        """
        try:
            if self.chrome_port == 9223:
                # Edge browser for FoundUps
                options = EdgeOptions()
                options.add_experimental_option("debuggerAddress", f"127.0.0.1:{self.chrome_port}")
                self.driver = webdriver.Edge(options=options)
                logger.info(f"[SCHEDULER] Connected to Edge on port {self.chrome_port}")
            else:
                # Chrome browser for Move2Japan/UnDaoDu
                options = ChromeOptions()
                options.add_experimental_option("debuggerAddress", f"127.0.0.1:{self.chrome_port}")
                self.driver = webdriver.Chrome(options=options)
                logger.info(f"[SCHEDULER] Connected to Chrome on port {self.chrome_port}")

            # Initialize DOM automation layer
            self.dom = YouTubeStudioDOM(self.driver)
            return True

        except WebDriverException as e:
            logger.error(f"[SCHEDULER] Failed to connect: {e}")
            return False

    def disconnect(self):
        """Disconnect from browser (doesn't close it)."""
        if self.driver:
            try:
                # Don't quit - just disconnect
                self.driver = None
                self.dom = None
                logger.info("[SCHEDULER] Disconnected from browser")
            except Exception as e:
                logger.warning(f"[SCHEDULER] Disconnect error: {e}")

    # =========================================
    # SCHEDULING WORKFLOW
    # =========================================

    async def run_scheduling_cycle(
        self,
        max_videos: int = 10,
        update_metadata: bool = True,
    ) -> Dict[str, Any]:
        """
        Run a full scheduling cycle.

        1. Navigate to unlisted Shorts
        2. For each video:
           a. Update title/description if needed
           b. Schedule to next available slot
        3. Track all scheduled videos

        Args:
            max_videos: Maximum videos to process
            update_metadata: Whether to update titles/descriptions

        Returns:
            Summary dict with scheduled_count, errors, etc.
        """
        if not self.driver:
            raise RuntimeError("Not connected to browser. Call connect_browser() first.")

        results = {
            "channel": self.channel_name,
            "started_at": datetime.now().isoformat(),
            "scheduled": [],
            "errors": [],
            "skipped": [],
        }

        try:
            # Step 1: Navigate to unlisted Shorts
            logger.info(f"[SCHEDULER] Navigating to unlisted Shorts for {self.channel_name}")
            self.dom.navigate_to_shorts(self.channel_id, "UNLISTED")
            await asyncio.sleep(2)  # Wait for page load

            # Step 2: Get unlisted videos
            unlisted = self.dom.get_unlisted_videos()
            logger.info(f"[SCHEDULER] Found {len(unlisted)} unlisted videos")

            if not unlisted:
                results["message"] = "No unlisted videos found"
                return results

            # Step 3: First sync existing scheduled videos
            await self._sync_scheduled_videos()

            # Step 4: Process each video
            processed = 0
            for video in unlisted[:max_videos]:
                if processed >= max_videos:
                    break

                video_id = video.get("video_id")
                original_title = video.get("title", "")

                logger.info(f"[SCHEDULER] Processing: {video_id} - {original_title[:40]}...")

                try:
                    # Get next available slot
                    slot = self.tracker.get_next_available_slot(
                        self.time_slots,
                        self.max_per_day,
                    )

                    if not slot:
                        logger.warning("[SCHEDULER] No available slots in date range")
                        results["skipped"].append({
                            "video_id": video_id,
                            "reason": "No available slots",
                        })
                        break

                    date_str, time_str = slot

                    if self.dry_run:
                        logger.info(f"[DRY RUN] Would schedule {video_id} for {date_str} at {time_str}")
                        results["scheduled"].append({
                            "video_id": video_id,
                            "date": date_str,
                            "time": time_str,
                            "dry_run": True,
                        })
                        self.tracker.increment(date_str, video_id)
                        processed += 1
                        continue

                    # Navigate to video edit page
                    self.dom.navigate_to_video(video_id)
                    await asyncio.sleep(1.5)

                    # Update metadata if requested
                    if update_metadata:
                        await self._update_video_metadata(original_title)

                    # Schedule the video
                    success = self.dom.schedule_video(date_str, time_str)

                    if success:
                        self.tracker.increment(date_str, video_id)
                        results["scheduled"].append({
                            "video_id": video_id,
                            "date": date_str,
                            "time": time_str,
                        })
                        logger.info(f"[SCHEDULER] Scheduled {video_id} for {date_str} at {time_str}")
                    else:
                        results["errors"].append({
                            "video_id": video_id,
                            "error": "Schedule failed",
                        })

                    processed += 1

                    # Human-like delay between videos
                    await asyncio.sleep(self.dom.human_delay(3.0, 1.0))

                except Exception as e:
                    logger.error(f"[SCHEDULER] Error processing {video_id}: {e}")
                    results["errors"].append({
                        "video_id": video_id,
                        "error": str(e),
                    })

        except Exception as e:
            logger.error(f"[SCHEDULER] Cycle error: {e}")
            results["errors"].append({"error": str(e)})

        results["finished_at"] = datetime.now().isoformat()
        results["total_scheduled"] = len(results["scheduled"])
        results["total_errors"] = len(results["errors"])

        return results

    async def _sync_scheduled_videos(self):
        """Sync tracker with actual YouTube scheduled videos."""
        try:
            # Navigate to scheduled filter
            self.dom.navigate_to_shorts(self.channel_id, "SCHEDULED")
            await asyncio.sleep(2)

            # Get all scheduled videos (paginate if needed)
            all_scheduled = []
            while True:
                scheduled = self.dom.get_scheduled_videos()
                all_scheduled.extend(scheduled)

                if self.dom.has_next_page():
                    self.dom.click_next_page()
                    await asyncio.sleep(1)
                else:
                    break

            # Sync to tracker
            self.tracker.sync_from_youtube(all_scheduled)
            logger.info(f"[SCHEDULER] Synced {len(all_scheduled)} scheduled videos")

        except Exception as e:
            logger.warning(f"[SCHEDULER] Sync warning: {e}")

    async def _update_video_metadata(self, original_title: str):
        """Update video title and description with FFCPLN content."""
        try:
            # Generate new title
            new_title = generate_clickbait_title(original_title=original_title)

            # Generate description
            new_description = get_standard_description(
                self.config.get("description_template", "ffcpln")
            )

            # Update via DOM
            self.dom.edit_title(new_title)
            await asyncio.sleep(0.5)

            self.dom.edit_description(new_description)
            await asyncio.sleep(0.5)

            logger.info(f"[SCHEDULER] Updated metadata: {new_title[:50]}...")

        except Exception as e:
            logger.warning(f"[SCHEDULER] Metadata update failed: {e}")

    # =========================================
    # UTILITY METHODS
    # =========================================

    def get_schedule_summary(self) -> Dict:
        """Get current schedule summary."""
        return self.tracker.get_summary()

    async def preview_slots(self, count: int = 10) -> List[Dict]:
        """
        Preview next available slots without scheduling.

        Args:
            count: Number of slots to preview

        Returns:
            List of {date, time, slot_number} dicts
        """
        slots = []
        temp_tracker = ScheduleTracker(self.channel_id)

        for i in range(count):
            slot = temp_tracker.get_next_available_slot(
                self.time_slots,
                self.max_per_day,
            )
            if slot:
                date_str, time_str = slot
                slots.append({
                    "date": date_str,
                    "time": time_str,
                    "slot_number": i + 1,
                })
                temp_tracker.increment(date_str)
            else:
                break

        return slots


# =========================================
# DAE ENTRY POINT
# =========================================

async def run_scheduler_dae(
    channel_key: str,
    max_videos: int = 10,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    DAE entry point for YouTube Shorts scheduling.

    Args:
        channel_key: "move2japan", "undaodu", or "foundups"
        max_videos: Maximum videos to schedule
        dry_run: Preview mode without actual changes

    Returns:
        Scheduling results dict
    """
    scheduler = YouTubeShortsScheduler(channel_key, dry_run=dry_run)

    if not scheduler.connect_browser():
        return {
            "error": f"Failed to connect to browser for {channel_key}",
            "channel": channel_key,
        }

    try:
        results = await scheduler.run_scheduling_cycle(max_videos=max_videos)
        return results
    finally:
        scheduler.disconnect()


# =========================================
# CLI INTERFACE
# =========================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="YouTube Shorts Scheduler")
    parser.add_argument(
        "channel",
        choices=["move2japan", "undaodu", "foundups"],
        help="Channel to schedule for",
    )
    parser.add_argument(
        "--max",
        type=int,
        default=10,
        help="Maximum videos to schedule",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview mode without changes",
    )
    parser.add_argument(
        "--preview-slots",
        type=int,
        default=0,
        help="Preview N available slots",
    )

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    if args.preview_slots > 0:
        # Preview mode
        scheduler = YouTubeShortsScheduler(args.channel, dry_run=True)
        slots = asyncio.run(scheduler.preview_slots(args.preview_slots))
        print(f"\nNext {len(slots)} available slots for {args.channel}:")
        for slot in slots:
            print(f"  {slot['slot_number']}. {slot['date']} at {slot['time']}")
    else:
        # Run scheduling
        results = asyncio.run(run_scheduler_dae(
            args.channel,
            max_videos=args.max,
            dry_run=args.dry_run,
        ))

        print(f"\n=== Scheduling Results for {results.get('channel', args.channel)} ===")
        print(f"Scheduled: {results.get('total_scheduled', 0)}")
        print(f"Errors: {results.get('total_errors', 0)}")

        if results.get("scheduled"):
            print("\nScheduled videos:")
            for v in results["scheduled"]:
                dry = " [DRY RUN]" if v.get("dry_run") else ""
                print(f"  - {v['video_id']}: {v['date']} at {v['time']}{dry}")

        if results.get("errors"):
            print("\nErrors:")
            for e in results["errors"]:
                print(f"  - {e}")
