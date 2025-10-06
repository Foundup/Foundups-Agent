"""
Google Veo 3 Video Generator

Uses Google's Veo 3 API for AI-powered video generation from text prompts.
Supports both fast and high-quality generation modes.

WSP Compliance:
- Comprehensive daemon logging for monitoring
- Step-by-step video generation tracking
- Cost and performance metrics logging
"""

import os
import time
import json
import logging
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Use newer google.genai SDK for Veo 3 video generation
from google import genai
from google.genai import types

# Keep generativeai for Gemini text (prompt enhancement)
import google.generativeai as genai_legacy

# Initialize logger for daemon monitoring
logger = logging.getLogger(__name__)


class Veo3GenerationError(Exception):
    """Veo 3 API generation failed"""
    pass


class InsufficientCreditsError(Exception):
    """Not enough API credits for generation"""
    pass


class Veo3Generator:
    """
    Google Veo 3 video generation interface.

    Generates videos from text prompts using Veo 3 API.
    Tracks costs and manages output files.
    """

    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize Veo 3 generator.

        Args:
            output_dir: Directory for generated videos (default: module assets/)
        """
        # Load environment
        load_dotenv()
        api_key = os.getenv('GOOGLE_API_KEY')

        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in .env file")

        # Initialize Veo client (new SDK)
        self.client = genai.Client(api_key=api_key)

        # Configure legacy SDK for Gemini text (prompt enhancement)
        genai_legacy.configure(api_key=api_key)

        # Set output directory
        if output_dir is None:
            module_root = Path(__file__).parent.parent
            output_dir = module_root / "assets" / "generated"

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Cost tracking
        self.cost_per_second = 0.40  # Veo 3 Fast pricing

        logger.info("🎬 [VEO3-INIT] Veo 3 Generator initialized")
        logger.info(f"📁 [VEO3-INIT] Output directory: {self.output_dir}")
        logger.info(f"💰 [VEO3-INIT] Cost: ${self.cost_per_second}/second (Veo 3 Fast)")

    def generate_video(
        self,
        prompt: str,
        duration: int = 30,
        fast_mode: bool = True
    ) -> str:
        """
        Generate video from text prompt using Veo 3.

        Args:
            prompt: Text description of video to generate
            duration: Video length in seconds (15-60)
            fast_mode: Use Veo 3 Fast (cheaper, faster) vs standard

        Returns:
            str: Path to generated .mp4 file

        Raises:
            Veo3GenerationError: If generation fails
            InsufficientCreditsError: If quota exceeded
        """

        # Validate duration
        if not 15 <= duration <= 60:
            raise ValueError(f"Duration must be 15-60 seconds, got {duration}")

        # Calculate cost
        estimated_cost = duration * self.cost_per_second
        logger.info("🎬 [VEO3-GEN] Starting video generation")
        logger.info(f"📝 [VEO3-GEN] Prompt: {prompt[:60]}...")
        logger.info(f"⏱️  [VEO3-GEN] Duration: {duration}s")
        logger.info(f"💰 [VEO3-GEN] Estimated cost: ${estimated_cost:.2f}")

        try:
            # Select model
            model_name = (
                "veo-3.0-fast-generate-001" if fast_mode
                else "veo-3.0-generate-001"
            )

            # Generate video using new SDK
            logger.info(f"🚀 [VEO3-API] Calling Veo 3 API: {model_name}")
            logger.info(f"⚡ [VEO3-API] Fast mode: {fast_mode}")

            operation = self.client.models.generate_videos(
                model=model_name,
                prompt=prompt
            )

            # Poll for completion
            logger.info("🎥 [VEO3-PROGRESS] Video generation in progress...")
            poll_count = 0
            while not operation.done:
                time.sleep(10)
                poll_count += 1
                logger.info(f"⏳ [VEO3-PROGRESS] Still generating... ({poll_count * 10}s elapsed)")
                operation = self.client.operations.get(operation)

            # Download generated video
            logger.info("📥 [VEO3-DOWNLOAD] Retrieving generated video...")
            generated_video = operation.response.generated_videos[0]

            # Download to file
            video_id = f"veo3_{int(time.time())}"
            video_path = self.output_dir / f"{video_id}.mp4"
            logger.info(f"💾 [VEO3-DOWNLOAD] Saving to: {video_path}")

            # Download and save
            self.client.files.download(file=generated_video.video)
            generated_video.video.save(str(video_path))
            logger.info("✅ [VEO3-DOWNLOAD] Video file saved successfully")

            # Save metadata
            metadata = {
                "video_id": video_id,
                "prompt": prompt,
                "duration": duration,
                "cost": estimated_cost,
                "model": model_name,
                "generated_at": time.time(),
                "file_path": str(video_path)
            }

            metadata_path = self.output_dir / f"{video_id}_meta.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            logger.info(f"📄 [VEO3-META] Metadata saved: {metadata_path}")

            logger.info("🎉 [VEO3-SUCCESS] Video generated successfully!")
            logger.info(f"📁 [VEO3-SUCCESS] File: {video_path}")
            logger.info(f"💰 [VEO3-SUCCESS] Cost: ${estimated_cost:.2f}")

            return str(video_path)

        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ [VEO3-ERROR] Generation failed: {error_msg}")

            # Check for quota errors
            if "quota" in error_msg.lower() or "insufficient" in error_msg.lower():
                logger.error("💸 [VEO3-ERROR] API quota exceeded")
                raise InsufficientCreditsError(f"API quota exceeded: {error_msg}")

            raise Veo3GenerationError(f"Video generation failed: {error_msg}")

    def enhance_prompt(
        self,
        simple_topic: str,
        use_anti_maga: bool = False,
        use_trending: bool = True
    ) -> str:
        """
        Enhance simple topic into detailed Veo 3 prompt.

        Uses Move2Japan prompt enhancer + Gemini for final polish.

        Args:
            simple_topic: Simple topic like "Cherry blossoms in Tokyo"
            use_anti_maga: Add progressive Japan positioning
            use_trending: Include 2025 trending elements

        Returns:
            str: Enhanced prompt for Veo 3
        """

        print(f"[Veo3] Enhancing prompt for: {simple_topic}")

        try:
            # Import Move2Japan prompt enhancer
            from modules.communication.youtube_shorts.src.prompt_enhancer import Move2JapanPromptEnhancer

            enhancer = Move2JapanPromptEnhancer()

            # Stage 1: Move2Japan style enhancement
            if use_anti_maga:
                enhanced_v1 = enhancer.create_anti_maga_japan_prompt(simple_topic)
            else:
                enhanced_v1 = enhancer.enhance(
                    simple_topic,
                    include_anti_maga=False,
                    use_trending=use_trending
                )

            print(f"[Veo3] Stage 1 (Move2Japan): {enhanced_v1[:100]}...")

            # Stage 2: Gemini final polish for Veo 3 optimization
            model = genai_legacy.GenerativeModel('gemini-2.0-flash-exp')

            polish_prompt = f"""
Refine this video prompt for Google Veo 3 (keep under 200 words):

{enhanced_v1}

Requirements:
- Make it more cinematic and visually specific
- Ensure camera movements are smooth and natural
- Add specific details about lighting quality
- Include emotional/atmospheric elements
- Keep Japan/Move2Japan authentic theme
- Make it fun, cheeky, and engaging
- Output in 2-3 sentences maximum

Return ONLY the polished video prompt.
"""

            response = model.generate_content(
                polish_prompt,
                generation_config=genai_legacy.types.GenerationConfig(
                    temperature=0.6,
                    max_output_tokens=250
                )
            )

            final_prompt = response.text.strip()
            print(f"[Veo3] Stage 2 (Gemini polish): {final_prompt}")

            return final_prompt

        except ImportError:
            print(f"[Veo3] ⚠️  Move2Japan enhancer not available, using basic enhancement")
            return self._basic_enhance(simple_topic)

        except Exception as e:
            print(f"[Veo3] ⚠️  Enhancement failed: {e}")
            print(f"[Veo3] Using original topic as prompt")
            return simple_topic

    def _basic_enhance(self, simple_topic: str) -> str:
        """Fallback basic enhancement without prompt_enhancer module."""
        try:
            model = genai_legacy.GenerativeModel('gemini-2.0-flash-exp')

            enhancement_prompt = f"""
Create a detailed video generation prompt for Google Veo 3 based on this topic:
"{simple_topic}"

The prompt should:
- Describe visual scenes in detail
- Include camera movements (pan, zoom, etc.)
- Specify lighting and atmosphere
- Be 2-3 sentences maximum
- Focus on Japan/Move2Japan theme if applicable
- Be fun, cheeky, and engaging

Return ONLY the video prompt, no explanation.
"""

            response = model.generate_content(
                enhancement_prompt,
                generation_config=genai_legacy.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=200
                )
            )

            return response.text.strip()

        except Exception as e:
            print(f"[Veo3] Basic enhancement failed: {e}")
            return simple_topic

    def generate_three_act_short(
        self,
        topic: str,
        fast_mode: bool = True,
        mode: str = "journal"
    ) -> str:
        """
        Generate 3-Act Short - 2×8s CLIPS MERGED

        Clip 1: Act 1 + Act 2 (setup + shock) ~8s
        Clip 2: Act 3 (reveal) ~8s
        Merged: ~16s perfect Short!

        Args:
            topic: Japan topic
            fast_mode: Use Veo 3 Fast (default: True)
            mode: "journal" or "random"

        Returns:
            str: Path to merged video

        Economics:
            2 clips × 8s × $0.4 = $6.40
        """

        logger.info("🎬 [3ACT-INIT] Starting 3-Act Short generation (2×8s merged)")
        logger.info(f"📝 [3ACT-INIT] Topic: {topic}")
        logger.info(f"🌟 [3ACT-INIT] Mode: {mode.upper()} {'(Emergence Journal)' if mode == 'journal' else '(Random)'}")
        logger.info(f"💰 [3ACT-INIT] Estimated cost: ~$6.40 (2×8s clips)")

        try:
            # Import dependencies
            logger.info("📦 [3ACT-DEPS] Loading story generation dependencies...")
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent))

            from story_generator_simple import ThreeActStoryGenerator
            from video_editor import VideoEditor
            logger.info("✅ [3ACT-DEPS] Dependencies loaded successfully")

            # Generate story
            logger.info(f"📖 [3ACT-STORY] Generating {mode} story structure...")
            story_gen = ThreeActStoryGenerator()
            story = story_gen.generate_story(topic=topic, mode=mode)

            logger.info(f"✨ [3ACT-STORY] Story generated: {story['full_story']}")
            logger.info(f"🎭 [3ACT-STORY] Act 1 (Setup): {story['act1'][:50]}...")
            logger.info(f"⚡ [3ACT-STORY] Act 2 (Shock): {story['act2'][:50]}...")
            logger.info(f"🌟 [3ACT-STORY] Act 3 (0102 Reveal): {story['act3'][:50]}...")

            clips = []

            # CLIP 1: Setup + Shock (8s)
            clip1_prompt = f"{story['act1']}. Suddenly, {story['act2']}"
            logger.info("🎥 [3ACT-CLIP1] Generating Clip 1/2 - Setup + Shock")
            logger.info(f"📝 [3ACT-CLIP1] Prompt: {clip1_prompt[:80]}...")

            clip1 = self.generate_video(
                prompt=clip1_prompt,
                duration=15,  # Gets ~8s
                fast_mode=fast_mode
            )
            clips.append(clip1)
            logger.info(f"✅ [3ACT-CLIP1] Clip 1 generated: {clip1}")

            # CLIP 2: Reveal (8s)
            logger.info("🌟 [3ACT-CLIP2] Generating Clip 2/2 - 0102 Reveal")
            logger.info(f"📝 [3ACT-CLIP2] Prompt: {story['act3'][:80]}...")

            clip2 = self.generate_video(
                prompt=story['act3'],
                duration=15,  # Gets ~8s
                fast_mode=fast_mode
            )
            clips.append(clip2)
            logger.info(f"✅ [3ACT-CLIP2] Clip 2 generated: {clip2}")

            # Merge with ffmpeg
            logger.info("🎞️  [3ACT-MERGE] Merging clips with ffmpeg...")
            logger.info(f"🔗 [3ACT-MERGE] Clips to merge: {len(clips)}")
            editor = VideoEditor()

            video_id = f"3act_{int(time.time())}"
            final_path = self.output_dir / f"{video_id}.mp4"
            logger.info(f"💾 [3ACT-MERGE] Output path: {final_path}")

            merged_video = editor.concatenate_clips(
                clip_paths=clips,
                output_path=str(final_path)
            )
            logger.info(f"✅ [3ACT-MERGE] Clips merged successfully: {merged_video}")

            # Save metadata
            metadata = {
                "video_id": video_id,
                "type": "3-act-merged",
                "topic": topic,
                "mode": mode,
                "story": story['full_story'],
                "clips": clips,
                "merged_video": merged_video,
                "duration": 16,  # 2×8s
                "cost": 2 * 8 * self.cost_per_second,
                "generated_at": time.time()
            }

            metadata_path = self.output_dir / f"{video_id}_meta.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            logger.info(f"📄 [3ACT-META] Metadata saved: {metadata_path}")

            logger.info("🎉 [3ACT-SUCCESS] 3-Act Short complete!")
            logger.info(f"📖 [3ACT-SUCCESS] Story: {story['full_story']}")
            logger.info(f"⏱️  [3ACT-SUCCESS] Duration: ~16s (2×8s)")
            logger.info(f"💰 [3ACT-SUCCESS] Total cost: ${2 * 8 * self.cost_per_second:.2f}")
            logger.info(f"📁 [3ACT-SUCCESS] Final video: {merged_video}")

            return merged_video

        except ImportError as e:
            logger.error(f"❌ [3ACT-ERROR] Missing dependency: {e}")
            raise Veo3GenerationError(f"Missing dependency: {e}")
        except Exception as e:
            logger.error(f"❌ [3ACT-ERROR] 3-Act generation failed: {e}")
            raise Veo3GenerationError(f"3-Act generation failed: {e}")

    def get_total_cost(self) -> float:
        """
        Calculate total cost of all generated videos.

        Returns:
            float: Total USD spent
        """
        total_cost = 0.0

        for meta_file in self.output_dir.glob("*_meta.json"):
            with open(meta_file) as f:
                metadata = json.load(f)
                total_cost += metadata.get("cost", 0.0)

        return total_cost

    def list_generated_videos(self) -> list:
        """
        List all generated videos with metadata.

        Returns:
            list: List of video metadata dicts
        """
        videos = []

        for meta_file in self.output_dir.glob("*_meta.json"):
            with open(meta_file) as f:
                metadata = json.load(f)
                videos.append(metadata)

        return sorted(videos, key=lambda x: x['generated_at'], reverse=True)


if __name__ == "__main__":
    # Test the generator
    generator = Veo3Generator()

    # Test prompt enhancement
    topic = "Cherry blossoms falling in a Japanese garden"
    enhanced = generator.enhance_prompt(topic)
    print(f"\nTopic: {topic}")
    print(f"Enhanced: {enhanced}")

    # Note: Actual video generation costs money, so commented out
    # video_path = generator.generate_video(enhanced, duration=30)
    # print(f"\nGenerated: {video_path}")
