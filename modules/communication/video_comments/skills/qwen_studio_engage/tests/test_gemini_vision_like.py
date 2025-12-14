"""
Test Gemini Vision-based like/heart on YouTube Studio
Uses the built-in Gemini Vision analyzer in FoundUpsDriver
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.infrastructure.foundups_selenium.src.browser_manager import get_browser_manager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

print("\n" + "="*60)
print("YOUTUBE STUDIO - Gemini Vision Like/Heart Test")
print("="*60 + "\n")

# Get browser (Gemini Vision auto-enabled)
print("[1] Getting browser with Gemini Vision...")
browser_manager = get_browser_manager()
browser = browser_manager.get_browser(
    browser_type='chrome',
    profile_name='youtube_move2japan'
)

# Navigate
url = "https://studio.youtube.com/channel/UC-LSSlOZwpGIRIYihaz8zCw/comments/inbox"
print(f"[2] Navigating to: {url}")
browser.get(url)
time.sleep(5)

print(f"[3] Taking screenshot...")
screenshot_bytes = browser.get_screenshot_as_png()
print(f"   Screenshot size: {len(screenshot_bytes)} bytes")

# Use Gemini Vision to analyze
print(f"[4] Using Gemini Vision to find like button...")
if hasattr(browser, 'vision_analyzer') and browser.vision_analyzer:
    try:
        import io
        from PIL import Image

        # Custom prompt for YouTube Studio comments
        img = Image.open(io.BytesIO(screenshot_bytes))

        prompt = """Analyze this YouTube Studio comments page screenshot.

Find the action bar for the FIRST comment which has these buttons from left to right:
- Reply button
- "0 replies" dropdown
- Thumbs up (like) button
- Thumbs down button
- Heart button (creator heart)
- Three-dot menu

I need to click the THUMBS UP button on the first comment.

Return JSON:
{
  "like_button_found": true/false,
  "like_button_description": "precise description of location",
  "like_button_is_already_liked": true/false,
  "suggested_approach": "selenium selector or coordinates to click"
}
"""

        response = browser.vision_analyzer.model.generate_content([prompt, img])
        print(f"\n[GEMINI RESPONSE]")
        print(response.text)
        print()

        # Try to parse and execute
        import json
        try:
            analysis = json.loads(response.text.strip().strip('```json').strip('```'))

            if analysis.get('like_button_found'):
                print(f"[5] ✓ Gemini found like button!")
                print(f"    Location: {analysis.get('like_button_description')}")
                print(f"    Already liked: {analysis.get('like_button_is_already_liked')}")
                print(f"    Approach: {analysis.get('suggested_approach')}")

                # For now, try to find by aria-label
                print(f"\n[6] Attempting to click...")
                try:
                    # YouTube Studio uses tp-yt-paper-icon-button for action buttons
                    buttons = browser.find_elements(By.CSS_SELECTOR, "tp-yt-paper-icon-button")
                    print(f"    Found {len(buttons)} paper-icon-buttons")

                    # Check aria-labels
                    for i, btn in enumerate(buttons):
                        aria = btn.get_attribute('aria-label') or ''
                        if 'like' in aria.lower() or btn.get_attribute('id') == 'like-button':
                            print(f"    Button {i}: {aria}")
                            btn.click()
                            print(f"[7] ✓ Clicked like button!")
                            time.sleep(2)
                            break
                except Exception as e:
                    print(f"[ERROR] Could not click: {e}")
            else:
                print(f"[5] ✗ Gemini could not find like button")

        except json.JSONDecodeError:
            print(f"[WARN] Could not parse as JSON, raw response shown above")

    except Exception as e:
        print(f"[ERROR] Gemini analysis failed: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"[ERROR] Gemini Vision not available in browser")

print("\n[WAIT] Browser staying open - Press Ctrl+C to exit...")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n[EXIT] Test terminated")
