#!/usr/bin/env python3
"""
Test Google Veo 3 API for video generation
Checks if video generation capabilities are available

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
import google.generativeai as genai

def test_veo3_api():
    """Test Veo 3 video generation API"""

    # Load environment variables
    load_dotenv()
    api_key = os.getenv('GOOGLE_API_KEY')

    if not api_key:
        print("ERROR: GOOGLE_API_KEY not found in .env file")
        return False

    print(f"[INFO] API Key found: {api_key[:10]}...{api_key[-4:]}")

    # Configure Gemini
    genai.configure(api_key=api_key)

    print("[INFO] Checking available models for video generation...")

    try:
        # List all available models
        models = genai.list_models()

        video_models = []
        for model in models:
            if 'video' in model.name.lower() or 'veo' in model.name.lower():
                video_models.append(model.name)
                print(f"  [OK] Found: {model.name}")
                print(f"    Supported methods: {model.supported_generation_methods}")

        if video_models:
            print(f"\n[SUCCESS] Found {len(video_models)} video generation model(s)")
            print("[INFO] Veo 3 API is available!")
            return True
        else:
            print("\n[INFO] No video generation models found")
            print("[INFO] Veo 3 may require separate API access or different project setup")
            print("[INFO] We can proceed with POC using stock videos + MoviePy")
            return False

    except Exception as e:
        print(f"\n[ERROR] API test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_veo3_api()
    sys.exit(0 if success else 1)
