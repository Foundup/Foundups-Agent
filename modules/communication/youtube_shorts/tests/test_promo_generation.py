"""
Test Script: Generate Promotional YouTube Short

This script tests the complete pipeline for generating the META promotional video
about the talking baby feature itself.

COST WARNING: Actual video generation costs $12 (30 seconds)
"""

import sys
from pathlib import Path

# Add module to path
module_root = Path(__file__).parent.parent
sys.path.insert(0, str(module_root.parent.parent.parent))

from modules.communication.youtube_shorts.src.prompt_enhancer import Move2JapanPromptEnhancer
from modules.communication.youtube_shorts.src.veo3_generator import Veo3Generator


def test_prompt_enhancement():
    """Test 1: Verify talking baby prompt enhancement works"""
    print("\n" + "="*80)
    print("TEST 1: Prompt Enhancement with Talking Baby")
    print("="*80)

    enhancer = Move2JapanPromptEnhancer()

    # Simple topic
    topic = "Cherry blossoms in Tokyo"

    # Enhance (now includes talking baby automatically)
    enhanced = enhancer.enhance(topic)

    print(f"\n📝 Original Topic: {topic}")
    print(f"\n✨ Enhanced Prompt:\n{enhanced}")

    # Verify talking baby is included
    if "baby" in enhanced.lower():
        print("\n✅ SUCCESS: Talking baby element detected in prompt!")
        return True
    else:
        print("\n❌ FAIL: Talking baby missing from prompt!")
        return False


def test_promo_prompt():
    """Test 2: Generate promotional video prompt"""
    print("\n" + "="*80)
    print("TEST 2: META Promotional Prompt")
    print("="*80)

    enhancer = Move2JapanPromptEnhancer()

    promo_topic = """
    Adorable baby in tiny kimono pointing at computer screen showing YouTube Live chat,
    chubby finger on screen saying 'Super Chat $20', baby excitedly babbling
    'You make video! Me talk! Japan show!', then cut to same baby narrating cherry blossoms,
    baby giggling 'See? Baby make video!', ending with baby waving bye-bye
    """

    enhanced_promo = enhancer.enhance(promo_topic.strip(), use_trending=True)

    print(f"\n🎬 PROMO PROMPT:\n{enhanced_promo}")

    print(f"\n📝 YOUTUBE METADATA:")
    print(f"Title: How To Get Talking Babies To Make Your Japan Video 👶🎥")
    print(f"Description:")
    print(f"  Want a custom AI video about Japan? Just Super Chat $20 in our live stream!")
    print(f"  Our talking baby will narrate YOUR topic in adorable baby-English.")
    print(f"  You type it, baby makes it, AI generates it. LIVE.")

    return True


def test_video_generation_dry_run():
    """Test 3: Initialize Veo3Generator (no video generation)"""
    print("\n" + "="*80)
    print("TEST 3: Veo3 Generator Initialization")
    print("="*80)

    try:
        generator = Veo3Generator()
        print(f"\n✅ Veo3Generator initialized successfully!")
        print(f"   Output dir: {generator.output_dir}")
        print(f"   Cost per second: ${generator.cost_per_second}")
        return True
    except Exception as e:
        print(f"\n❌ FAIL: {e}")
        return False


def generate_promo_video():
    """ACTUAL GENERATION: Generate promotional video (COSTS $12!)"""
    print("\n" + "="*80)
    print("⚠️  ACTUAL VIDEO GENERATION - THIS COSTS $12!")
    print("="*80)

    response = input("\nAre you SURE you want to generate the promo video? (yes/no): ")

    if response.lower() != "yes":
        print("\n⏸️  Skipped video generation (wise choice for testing!)")
        return False

    print("\n🎬 Generating promotional video...")

    try:
        # Initialize
        enhancer = Move2JapanPromptEnhancer()
        generator = Veo3Generator()

        # Create promo prompt
        promo_topic = """
        Adorable baby in tiny kimono pointing at computer screen showing YouTube Live chat,
        chubby finger on 'Super Chat $20' button, baby excitedly babbling
        'You make video! Me talk! Japan show!', then cut to same baby narrating cherry blossoms,
        baby giggling 'See? Baby make video for you!', ending with baby waving bye-bye with huge smile
        """

        # Enhance
        enhanced_promo = enhancer.enhance(promo_topic.strip(), use_trending=True)

        print(f"\n📝 Prompt: {enhanced_promo[:100]}...")

        # Generate video (30 seconds, $12 cost)
        video_path = generator.generate_video(
            prompt=enhanced_promo,
            duration=30,
            fast_mode=True
        )

        print(f"\n✅ SUCCESS!")
        print(f"   Video: {video_path}")
        print(f"   Cost: $12.00")
        print(f"\n📤 Next: Upload to YouTube with title:")
        print(f"   'How To Get Talking Babies To Make Your Japan Video 👶🎥'")

        return True

    except Exception as e:
        print(f"\n❌ GENERATION FAILED: {e}")
        return False


if __name__ == "__main__":
    print("\n🎬 YouTube Shorts Promo - Talking Baby Feature")
    print("="*80)

    # Run safe tests first
    test1_pass = test_prompt_enhancement()
    test2_pass = test_promo_prompt()
    test3_pass = test_video_generation_dry_run()

    print("\n" + "="*80)
    print("TEST RESULTS:")
    print("="*80)
    print(f"  Prompt Enhancement: {'✅ PASS' if test1_pass else '❌ FAIL'}")
    print(f"  Promo Prompt: {'✅ PASS' if test2_pass else '❌ FAIL'}")
    print(f"  Generator Init: {'✅ PASS' if test3_pass else '❌ FAIL'}")

    # Offer actual generation (costs money!)
    print("\n" + "="*80)
    print("ACTUAL VIDEO GENERATION:")
    print("="*80)
    print("⚠️  This will cost $12 (30-second video)")
    print("⏳ Takes 1-2 minutes to generate")
    print("🎥 Creates promotional Short about the feature")
    print()

    generate_promo_video()
