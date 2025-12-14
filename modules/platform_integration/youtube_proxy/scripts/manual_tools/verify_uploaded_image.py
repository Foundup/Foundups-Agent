from pathlib import Path
import sys
import os

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
os.chdir(REPO_ROOT)

import sys
import os
import json
from pathlib import Path

# Add repo root to path
repo_root = REPO_ROOT

from modules.platform_integration.social_media_orchestrator.src.gemini_vision_analyzer import GeminiVisionAnalyzer

def verify_screenshot():
    print("Analyzing User Screenshot...")
    
    # Image path provided by user
    img_path = r"C:/Users/user/.gemini/antigravity/brain/d197d6c4-fed5-4cb5-999a-d45648ab371b/uploaded_image_1764944712079.png"
    
    if not os.path.exists(img_path):
        print(f"[FAIL] Image not found at {img_path}")
        return

    # Load API Key
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv('GOOGLE_AISTUDIO_API_KEY')
    
    analyzer = GeminiVisionAnalyzer(api_key=api_key)
    
    with open(img_path, "rb") as f:
        img_bytes = f.read()

    # Test 1: Find Heart Button
    print("\n[Test 1] Finding Creator Heart Button...")
    description = "gray outlined heart icon in the comment action bar, located between thumbs down and three-dot menu"
    
    result = analyzer.find_element_by_description(img_bytes, description)
    print(json.dumps(result, indent=2))
    
    if result.get('found'):
        print("[PASS] Heart button identified successfully!")
    else:
        print("[FAIL] Could not find heart button.")

if __name__ == "__main__":
    verify_screenshot()
