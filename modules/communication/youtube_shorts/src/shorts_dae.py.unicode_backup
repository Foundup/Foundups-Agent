"""
YouTube Shorts DAE (Digital Autonomous Entity)

WSP 80 DAE pattern for autonomous Shorts generation.
Runs as background process, creating and posting Shorts on schedule.
"""

import time
import threading
from typing import List, Optional
from .shorts_orchestrator import ShortsOrchestrator


class ShortsDAE:
    """
    Autonomous DAE for scheduled YouTube Shorts generation.

    WSP 80 Pattern: Self-contained autonomous cube.
    """

    def __init__(self):
        """Initialize Shorts DAE."""

        self.orchestrator = ShortsOrchestrator()
        self.active = False
        self.thread: Optional[threading.Thread] = None

        # Topic queue for autonomous posting
        self.topic_queue: List[str] = []
        self.current_topic_index = 0

        print("[ShortsDAE] Initialized")

    def start_autonomous_mode(
        self,
        topics: List[str],
        interval_hours: int = 24,
        duration: int = 30,
        privacy: str = "public"
    ):
        """
        Start autonomous Short generation on schedule.

        Args:
            topics: List of topics to cycle through
            interval_hours: Hours between posts (default: 24 = daily)
            duration: Video duration in seconds (default: 30)
            privacy: Privacy setting (default: "public")
        """

        if self.active:
            print("[ShortsDAE] ⚠️  Already running in autonomous mode")
            return

        if not topics:
            print("[ShortsDAE] ❌ No topics provided")
            return

        self.topic_queue = topics
        self.current_topic_index = 0
        self.active = True

        # Start background thread
        self.thread = threading.Thread(
            target=self._autonomous_loop,
            args=(interval_hours, duration, privacy),
            daemon=True
        )
        self.thread.start()

        print(f"[ShortsDAE] ✅ Autonomous mode started")
        print(f"  Topics: {len(topics)}")
        print(f"  Interval: Every {interval_hours} hours")
        print(f"  Duration: {duration}s per Short")

    def _autonomous_loop(
        self,
        interval_hours: int,
        duration: int,
        privacy: str
    ):
        """
        Background loop for autonomous Short generation.

        Runs in separate thread.
        """

        interval_seconds = interval_hours * 3600

        print(f"[ShortsDAE] 🤖 Autonomous loop started")

        while self.active:
            try:
                # Get next topic (cycle through queue)
                topic = self.topic_queue[self.current_topic_index]
                self.current_topic_index = (self.current_topic_index + 1) % len(self.topic_queue)

                print(f"\n[ShortsDAE] 🎬 Creating scheduled Short...")
                print(f"  Topic: {topic}")

                # Create and upload Short
                youtube_url = self.orchestrator.create_and_upload(
                    topic=topic,
                    duration=duration,
                    privacy=privacy
                )

                print(f"[ShortsDAE] ✅ Autonomous Short posted: {youtube_url}")

                # Wait for next interval
                if self.active:
                    print(f"[ShortsDAE] ⏰ Next Short in {interval_hours} hours...")
                    time.sleep(interval_seconds)

            except Exception as e:
                print(f"[ShortsDAE] ❌ Error in autonomous loop: {e}")
                print(f"[ShortsDAE] ⏰ Retrying in 1 hour...")
                time.sleep(3600)  # Wait 1 hour on error

        print(f"[ShortsDAE] 🛑 Autonomous loop stopped")

    def stop_autonomous_mode(self):
        """Stop autonomous Short generation."""

        if not self.active:
            print("[ShortsDAE] ℹ️  Not running in autonomous mode")
            return

        print("[ShortsDAE] 🛑 Stopping autonomous mode...")
        self.active = False

        if self.thread:
            self.thread.join(timeout=5)

        print("[ShortsDAE] ✅ Autonomous mode stopped")

    def add_topics(self, topics: List[str]):
        """
        Add topics to the queue.

        Args:
            topics: List of new topics to add
        """

        self.topic_queue.extend(topics)
        print(f"[ShortsDAE] ✅ Added {len(topics)} topics to queue")
        print(f"  Total topics: {len(self.topic_queue)}")

    def get_status(self) -> dict:
        """
        Get DAE status.

        Returns:
            dict: Status information
        """

        return {
            "active": self.active,
            "topic_queue_size": len(self.topic_queue),
            "current_topic_index": self.current_topic_index,
            "next_topic": self.topic_queue[self.current_topic_index] if self.topic_queue else None,
            "stats": self.orchestrator.get_stats()
        }

    def create_single_short(
        self,
        topic: str,
        duration: int = 30,
        privacy: str = "public"
    ) -> str:
        """
        Create a single Short immediately (non-autonomous).

        Args:
            topic: Video topic
            duration: Video duration (default: 30s)
            privacy: Privacy setting (default: "public")

        Returns:
            str: YouTube Shorts URL
        """

        return self.orchestrator.create_and_upload(
            topic=topic,
            duration=duration,
            privacy=privacy
        )


if __name__ == "__main__":
    # Test the DAE
    dae = ShortsDAE()

    # Show status
    status = dae.get_status()
    print(f"\nDAE Status:")
    print(f"  Active: {status['active']}")
    print(f"  Topics in queue: {status['topic_queue_size']}")

    # Example autonomous mode (commented out - costs money)
    # dae.start_autonomous_mode(
    #     topics=[
    #         "Cherry blossoms in Tokyo",
    #         "Japanese street food",
    #         "Traditional tea ceremony"
    #     ],
    #     interval_hours=24,  # One Short per day
    #     duration=30
    # )
    #
    # # Let it run for 10 seconds
    # time.sleep(10)
    #
    # # Stop
    # dae.stop_autonomous_mode()
