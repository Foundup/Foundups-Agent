"""
YouTube Shorts Orchestrator

Manages the complete 012↔0102 interaction flow:
1. 012 provides topic
2. 0102 enhances prompt
3. Veo 3 generates video
4. Upload to YouTube
5. Report back to 012

WSP Compliance:
- Comprehensive daemon logging for full flow monitoring
- Step-by-step tracking from topic to YouTube upload
- Integration with main.py DAE logging system
"""

import json
import time
import logging
from pathlib import Path
from typing import Optional, Dict
from .veo3_generator import Veo3Generator, Veo3GenerationError, InsufficientCreditsError
from .youtube_uploader import YouTubeShortsUploader, YouTubeUploadError

# Initialize logger for daemon monitoring
logger = logging.getLogger(__name__)


class ShortsOrchestrator:
    """
    Main orchestration for autonomous YouTube Shorts creation.

    Coordinates the full flow from topic input to YouTube upload.
    """

    def __init__(self, channel: str = "move2japan"):
        """
        Initialize orchestrator with generator and uploader.

        Args:
            channel: YouTube channel to use ("move2japan" or "undaodu")
                    Default: "move2japan" for Move2Japan talking baby Shorts
        """

        logger.info("🎬 [SHORTS-INIT] Initializing YouTube Shorts Orchestrator")
        logger.info(f"📺 [SHORTS-INIT] Target channel: {channel.upper()}")

        self.generator = Veo3Generator()
        self.uploader = YouTubeShortsUploader(channel=channel)
        self.channel = channel

        # Memory for tracking created Shorts
        module_root = Path(__file__).parent.parent
        self.memory_file = module_root / "memory" / "generated_shorts.json"
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)

        # Load existing memory
        self.shorts_memory = self._load_memory()

        logger.info(f"✅ [SHORTS-INIT] Orchestrator initialized for {channel.upper()}")
        logger.info(f"💾 [SHORTS-INIT] Memory: {len(self.shorts_memory)} Shorts tracked")
        logger.info(f"📁 [SHORTS-INIT] Memory file: {self.memory_file}")

    def _load_memory(self) -> list:
        """Load Shorts memory from JSON file."""
        if self.memory_file.exists():
            with open(self.memory_file) as f:
                return json.load(f)
        return []

    def _save_memory(self):
        """Save Shorts memory to JSON file."""
        with open(self.memory_file, 'w') as f:
            json.dump(self.shorts_memory, f, indent=2)

    def create_and_upload(
        self,
        topic: str,
        duration: int = 15,
        enhance_prompt: bool = True,
        fast_mode: bool = True,
        privacy: str = "public",
        use_3act: bool = True
    ) -> str:
        """
        Complete 012↔0102 flow: Generate and upload Short.

        Args:
            topic: Simple topic from 012 (e.g., "Cherry blossoms in Tokyo")
            duration: Video length in seconds (15-60)
                     Default: 15 (uses 3-act multi-clip system)
            enhance_prompt: Use Gemini to enhance topic (ignored if use_3act=True)
            fast_mode: Use Veo 3 Fast (cheaper) vs standard
            privacy: "public", "unlisted", or "private"
            use_3act: Use 3-act multi-clip system (recommended for 15s Shorts)
                     Default: True

        Returns:
            str: YouTube Shorts URL

        Raises:
            Veo3GenerationError: If video generation fails
            YouTubeUploadError: If upload fails
            InsufficientCreditsError: If quota exceeded

        Notes:
            - 3-act system: Setup → Shock → 0102 Reveal (baby IS 0102)
            - Economics: 3×5s = $6 vs 30s = $12 (50% cheaper)
            - Guaranteed 15s duration vs unpredictable single clip
        """

        print(f"\n{'='*60}")
        print(f"🎬 YouTube Shorts Creation Flow - 012↔0102")
        print(f"{'='*60}")
        print(f"\n[012 Input] Topic: {topic}")

        start_time = time.time()

        try:
            # Step 1 & 2: Generate video
            # Use 3-act system for 15s, single clip for other durations
            if use_3act and duration == 15:
                print(f"\n[0102 Generating] Creating 3-act Short (Setup → Shock → Reveal)...")
                video_path = self.generator.generate_three_act_short(
                    topic=topic,
                    fast_mode=fast_mode,
                    mode="journal"  # Default to emergence journal POC
                )
                # 3-act system has its own prompting
                video_prompt = f"3-act story: {topic}"

            else:
                # Traditional single-clip generation
                if enhance_prompt:
                    print("\n[0102 Processing] Enhancing prompt with Gemini...")
                    video_prompt = self.generator.enhance_prompt(topic)
                else:
                    video_prompt = topic

                print(f"\n[0102 Generating] Creating video with Veo 3...")
                video_path = self.generator.generate_video(
                    prompt=video_prompt,
                    duration=duration,
                    fast_mode=fast_mode
                )

            # Step 3: Prepare metadata for upload
            title = topic[:100]  # YouTube max 100 chars
            description = f"{topic}\n\nGenerated with AI for Move2Japan\n\n#Shorts #Japan #AI"

            tags = ["Shorts", "Japan", "Move2Japan", "AI"]

            # Add topic-specific tags
            if "cherry" in topic.lower() or "sakura" in topic.lower():
                tags.append("CherryBlossoms")
            if "tokyo" in topic.lower():
                tags.append("Tokyo")
            if "food" in topic.lower():
                tags.append("JapaneseFood")

            # Step 4: Upload to YouTube
            print(f"\n[0102 Uploading] Posting to YouTube...")
            youtube_url = self.uploader.upload_short(
                video_path=video_path,
                title=title,
                description=description,
                tags=tags,
                privacy=privacy
            )

            # Step 5: Save to memory
            elapsed_time = time.time() - start_time
            estimated_cost = duration * self.generator.cost_per_second

            short_record = {
                "id": youtube_url.split('/')[-1],  # Extract video ID
                "topic": topic,
                "prompt": video_prompt,
                "video_path": video_path,
                "youtube_url": youtube_url,
                "duration": duration,
                "cost": estimated_cost,
                "privacy": privacy,
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "processing_time": round(elapsed_time, 2),
                "status": "uploaded"
            }

            self.shorts_memory.append(short_record)
            self._save_memory()

            # Step 6: Report back to 012
            print(f"\n{'='*60}")
            print(f"✅ SHORT CREATED SUCCESSFULLY")
            print(f"{'='*60}")
            print(f"  Topic: {topic}")
            print(f"  URL: {youtube_url}")
            print(f"  Duration: {duration}s")
            print(f"  Cost: ${estimated_cost:.2f}")
            print(f"  Processing time: {elapsed_time:.1f}s")
            print(f"  Privacy: {privacy}")
            print(f"{'='*60}\n")

            return youtube_url

        except Veo3GenerationError as e:
            print(f"\n❌ [ERROR] Video generation failed: {e}")
            raise

        except YouTubeUploadError as e:
            print(f"\n❌ [ERROR] YouTube upload failed: {e}")
            raise

        except InsufficientCreditsError as e:
            print(f"\n❌ [ERROR] {e}")
            raise

        except Exception as e:
            print(f"\n❌ [ERROR] Unexpected error: {e}")
            raise

    def generate_video_only(
        self,
        topic: str,
        duration: int = 30,
        enhance_prompt: bool = True,
        fast_mode: bool = True
    ) -> str:
        """
        Generate video without uploading.

        Args:
            topic: Video topic
            duration: Video length in seconds
            enhance_prompt: Use Gemini to enhance prompt
            fast_mode: Use Veo 3 Fast

        Returns:
            str: Path to generated .mp4 file
        """

        if enhance_prompt:
            video_prompt = self.generator.enhance_prompt(topic)
        else:
            video_prompt = topic

        return self.generator.generate_video(
            prompt=video_prompt,
            duration=duration,
            fast_mode=fast_mode
        )

    def upload_existing(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: Optional[list] = None,
        privacy: str = "public"
    ) -> str:
        """
        Upload pre-existing video as Short.

        Args:
            video_path: Path to .mp4 file
            title: Video title
            description: Video description
            tags: List of tags
            privacy: Privacy setting

        Returns:
            str: YouTube Shorts URL
        """

        return self.uploader.upload_short(
            video_path=video_path,
            title=title,
            description=description,
            tags=tags,
            privacy=privacy
        )

    def get_stats(self) -> Dict:
        """
        Get statistics about created Shorts.

        Returns:
            dict: Stats including total count, cost, etc.
        """

        total_shorts = len(self.shorts_memory)
        total_cost = sum(s.get('cost', 0.0) for s in self.shorts_memory)
        total_duration = sum(s.get('duration', 0) for s in self.shorts_memory)

        uploaded_count = sum(1 for s in self.shorts_memory if s.get('status') == 'uploaded')

        return {
            "total_shorts": total_shorts,
            "uploaded": uploaded_count,
            "total_cost_usd": round(total_cost, 2),
            "total_duration_seconds": total_duration,
            "average_cost_per_short": round(total_cost / total_shorts, 2) if total_shorts > 0 else 0,
            "recent_shorts": self.shorts_memory[-5:]  # Last 5
        }

    def list_shorts(self, limit: int = 10) -> list:
        """
        List recently created Shorts.

        Args:
            limit: Number of Shorts to return

        Returns:
            list: List of Short records
        """

        return self.shorts_memory[-limit:]


if __name__ == "__main__":
    # Test orchestrator
    orchestrator = ShortsOrchestrator()

    # Show stats
    stats = orchestrator.get_stats()
    print(f"\nShorts Statistics:")
    print(f"  Total created: {stats['total_shorts']}")
    print(f"  Total cost: ${stats['total_cost_usd']}")
    print(f"  Average cost: ${stats['average_cost_per_short']}")

    # Note: Actual generation costs money, so commented out
    # url = orchestrator.create_and_upload(
    #     topic="Cherry blossoms falling in a serene Japanese garden",
    #     duration=30
    # )
    # print(f"\nCreated Short: {url}")
