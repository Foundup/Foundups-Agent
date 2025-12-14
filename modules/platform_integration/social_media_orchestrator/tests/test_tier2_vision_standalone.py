import os
import sys
from dotenv import load_dotenv
from PIL import Image
import io
from pathlib import Path

# Add repo root to path (4 levels up from tests/)
# modules/platform_integration/social_media_orchestrator/tests -> root
repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(repo_root))

try:
    from modules.platform_integration.social_media_orchestrator.src.gemini_vision_analyzer import GeminiVisionAnalyzer
except ImportError:
    print("[FAIL] Could not import GeminiVisionAnalyzer. Check python path.")
    sys.exit(1)

def main():
    print("Locked Step: Verifying Tier 2 (Gemini Vision) Configuration")
    
    # 1. Load Environment
    # Try loading from repo root .env
    env_path = repo_root / '.env'
    load_dotenv(dotenv_path=env_path)
    
    api_key = os.getenv('GOOGLE_AISTUDIO_API_KEY')
    if not api_key:
        print("[FAIL] GOOGLE_AISTUDIO_API_KEY not found in .env")
        return
            
    if api_key:
        print(f"[OK] API Key found: {api_key[:5]}...{api_key[-4:]}")
    else:
        print("[CRITICAL] No API Key available.")
        return

    # 2. Initialize Analyzer
    try:
        analyzer = GeminiVisionAnalyzer(api_key=api_key)
        if not analyzer.model:
            print("[FAIL] Model initialization failed (likely missing library)")
            return
    except Exception as e:
        print(f"[FAIL] Initialization exception: {e}")
        return

    # 3. Create Dummy Image (Simple solid color)
    print("Generating synthetic test image...")
    try:
        img = Image.new('RGB', (100, 100), color = (73, 109, 137))
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_bytes = img_byte_arr.getvalue()
    except Exception as e:
        print(f"[FAIL] Image generation failed: {e}")
        print("Ensure Pillow is installed: pip install Pillow")
        return

    # 4. Test API
    print("Sending request to Gemini Vision API...")
    result = analyzer.analyze_posting_ui(img_bytes)
    
    if "error" in result:
        print(f"[FAIL] Analysis failed: {result['error']}")
    else:
        print("[PASS] Gemini Vision returned valid analysis:")
        print(result)

    # 5. Test Selector Generation (New Prompt)
    print("\nTesting Selector Generation (React/XPath logic)...")
    selector_result = analyzer.detect_ui_changes(img_bytes, known_ui_version="2024-01")
    
    if "error" in selector_result:
        print(f"[FAIL] Selector generation failed: {selector_result['error']}")
    else:
        print("[PASS] Selector generation prompt accepted. Response preview:")
        print(selector_result)

if __name__ == "__main__":
    main()
