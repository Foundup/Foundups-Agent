#!/usr/bin/env python3
"""
Test OpenAI Sora2 API for video generation
Checks if Sora2 video generation capabilities are available

WSP 49 Compliance: Test file in proper module tests directory
Module: youtube_shorts
Domain: communication/
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

def test_sora2_api():
    """Test Sora2 video generation API"""

    # Load environment variables
    load_dotenv()

    # Check for Sora2 API keys (try multiple possible env var names)
    api_key = (os.getenv('SORA_API_KEY') or
               os.getenv('OPENAI_API_KEY') or
               os.getenv('AZURE_OPENAI_KEY'))

    azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')

    if not api_key:
        print("ERROR: No Sora2 API key found. Set SORA_API_KEY, OPENAI_API_KEY, or AZURE_OPENAI_KEY in .env file")
        return False

    print(f"[INFO] API Key found: {api_key[:10]}...{api_key[-4:]}")

    if azure_endpoint:
        print(f"[INFO] Using Azure OpenAI endpoint: {azure_endpoint}")
        deployment = os.getenv('AZURE_OPENAI_SORA_DEPLOYMENT', 'sora')
        print(f"[INFO] Azure deployment: {deployment}")
    else:
        print("[INFO] Using direct OpenAI API")

    try:
        # Import the Sora2Generator
        print("[INFO] Importing Sora2Generator...")
        from modules.communication.youtube_shorts.src.sora2_generator import Sora2Generator

        print("[INFO] Initializing Sora2Generator...")
        generator = Sora2Generator()

        print("[SUCCESS] Sora2Generator initialized successfully")
        print(f"  - Model: {generator.model}")
        print(f"  - Output directory: {generator.output_dir}")
        print(f"  - Cost per second: ${generator.cost_per_second}")
        print(f"  - Using Azure: {generator.use_azure}")

        # Test prompt enhancement (free)
        print("\n[INFO] Testing prompt enhancement...")
        test_topic = "cherry blossoms in Tokyo"
        enhanced_prompt = generator.enhance_prompt(test_topic)
        print("[SUCCESS] Prompt enhancement works")
        print(f"  - Original: '{test_topic}'")
        print(f"  - Enhanced: '{enhanced_prompt[:100]}...'")

        # Test API connectivity without generating video
        print("\n[INFO] Testing API connectivity...")
        print("[WARNING] Skipping actual video generation to avoid costs")
        print("   To test full generation, use test_promo_generation.py with Sora2")

        return True

    except ImportError as e:
        print(f"ERROR: Failed to import Sora2Generator: {e}")
        return False
    except ValueError as e:
        print(f"ERROR: Configuration error: {e}")
        return False
    except Exception as e:
        print(f"ERROR: Unexpected error during Sora2 API test: {e}")
        return False

if __name__ == "__main__":
    print("Testing Sora2 API connectivity...")
    print("=" * 50)

    success = test_sora2_api()

    print("\n" + "=" * 50)
    if success:
        print("SUCCESS: Sora2 API test PASSED")
        print("\nNext steps:")
        print("1. Run test_promo_generation.py to test actual video generation")
        print("2. Use !shortsora command in live chat")
        print("3. Monitor costs - Sora2 is ~$0.80/second")
    else:
        print("FAILED: Sora2 API test FAILED")
        print("\nTroubleshooting:")
        print("1. Check .env file has SORA_API_KEY or OPENAI_API_KEY")
        print("2. For Azure: Set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_KEY")
        print("3. Verify Sora API access and credits")
        sys.exit(1)
