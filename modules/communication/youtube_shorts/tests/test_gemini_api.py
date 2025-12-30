#!/usr/bin/env python3
"""
Quick test script for Gemini API functionality
Tests basic text generation to verify API access
"""

import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai

def test_gemini_api():
    """Test basic Gemini API functionality"""

    # Load environment variables
    load_dotenv()
    api_key = (
        os.getenv('GEMINI_API_KEY')
        or os.getenv('GOOGLE_API_KEY')
        or os.getenv('GOOGLE_AISTUDIO_API_KEY')
    )

    if not api_key:
        print("ERROR: No Gemini API key found in .env file")
        print("Please add: GEMINI_API_KEY=your_api_key_here")
        return False

    print(f"[INFO] API Key found: {api_key[:10]}...{api_key[-4:]}")

    # Configure Gemini
    genai.configure(api_key=api_key)

    print("[INFO] Testing Gemini API with simple text generation...")

    try:
        # Use Gemini 2.0 Flash for testing (fast and free)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')

        # Simple test prompt
        response = model.generate_content(
            "Say 'Hello from Gemini API!' in exactly 5 words.",
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                max_output_tokens=20
            )
        )

        print("\n=== GEMINI API TEST RESULTS ===")
        print(f"Model: gemini-2.0-flash-exp")
        print(f"Response: {response.text}")
        print("================================\n")

        print("[SUCCESS] Gemini API is working correctly!")
        return True

    except Exception as e:
        print(f"\n[ERROR] Gemini API test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_gemini_api()
    sys.exit(0 if success else 1)
