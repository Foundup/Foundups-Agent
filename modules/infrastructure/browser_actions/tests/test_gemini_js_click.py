"""
Test Gemini Vision + JavaScript Click - More reliable for React UIs
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from modules.infrastructure.foundups_selenium.src.browser_manager import get_browser_manager

print("\n" + "="*60)
print("GEMINI VISION + JS CLICK - YouTube Studio Heart")
print("="*60 + "\n")

# Connect to browser
print("[1] Connecting to browser...")
browser_manager = get_browser_manager()
browser = browser_manager.get_browser(
    browser_type='chrome',
    profile_name='youtube_move2japan'
)

# Navigate
url = "https://studio.youtube.com/channel/UC-LSSlOZwpGIRIYihaz8zCw/comments/inbox"
print(f"[2] Navigating to: {url}")
browser.get(url)
time.sleep(6)

# Use Gemini Vision
print(f"\n[3] Using Gemini Vision...")

if hasattr(browser, 'vision_analyzer') and browser.vision_analyzer:
    try:
        import io
        from PIL import Image
        import json
        from selenium.webdriver.common.by import By

        screenshot = browser.get_screenshot_as_png()
        img = Image.open(io.BytesIO(screenshot))

        prompt = """Find the CREATOR HEART button (5th element in action bar, outline heart between thumbs down and menu).

Return JSON:
{
  "found": true,
  "selector": "CSS selector for the button or icon"
}"""

        response = browser.vision_analyzer.model.generate_content([prompt, img])
        text = response.text.strip()

        if '```json' in text:
            text = text.split('```json')[1].split('```')[0]
        elif '```' in text:
            text = text.split('```')[1].split('```')[0]

        result = json.loads(text.strip())
        print(f"[4] Gemini result: {result}")

        if result.get('found'):
            selector = result.get('selector', '')
            print(f"[5] Trying selector: {selector}")

            # Find element
            elements = browser.find_elements(By.CSS_SELECTOR, selector)

            if elements:
                element = elements[0]

                # Scroll into view
                browser.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                time.sleep(1)

                # Highlight
                browser.execute_script("""
                    arguments[0].style.border = '3px solid red';
                    arguments[0].style.backgroundColor = 'rgba(255,0,0,0.2)';
                """, element)
                print(f"[6] Element highlighted - check if RED border is on heart button")
                time.sleep(2)

                # JavaScript click (bypasses interactability check)
                browser.execute_script("arguments[0].click();", element)
                print(f"[7] ✓ Clicked via JavaScript!")

                time.sleep(3)
                print(f"\n[8] Check if heart button turned RED")

            else:
                print(f"[ERROR] Selector found no elements")

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"[ERROR] Gemini Vision not available")

print(f"\n[DONE] Test complete. Browser will stay open for 30 seconds...")
time.sleep(30)
