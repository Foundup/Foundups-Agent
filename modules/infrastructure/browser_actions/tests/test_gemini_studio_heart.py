"""
Test Gemini Vision - YouTube Studio Heart Button
Tier 2 Vision with improved targeting
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from modules.infrastructure.foundups_selenium.src.browser_manager import get_browser_manager

print("\n" + "="*60)
print("GEMINI VISION - YouTube Studio Heart Button")
print("="*60 + "\n")

# Step 1: Connect to browser
print("[1] Connecting to browser...")
browser_manager = get_browser_manager()
browser = browser_manager.get_browser(
    browser_type='chrome',
    profile_name='youtube_move2japan'
)

# Step 2: Navigate to Studio
url = "https://studio.youtube.com/channel/UC-LSSlOZwpGIRIYihaz8zCw/comments/inbox"
print(f"[2] Navigating to: {url}")
browser.get(url)
time.sleep(6)

# Step 3: Use Gemini Vision with precise description
print(f"\n[3] Using Gemini Vision to find HEART button...")

if hasattr(browser, 'vision_analyzer') and browser.vision_analyzer:
    try:
        import io
        from PIL import Image
        import json

        # Take screenshot
        screenshot = browser.get_screenshot_as_png()
        img = Image.open(io.BytesIO(screenshot))

        # CRITICAL: Very specific prompt to avoid confusion
        prompt = """TASK: Find the CREATOR HEART button (NOT the like button) on YouTube Studio.

CRITICAL DISTINCTIONS:
- LIKE button: Thumbs up icon (👍) - position 3 from left - DO NOT SELECT THIS
- HEART button: Outlined heart (♡) - position 5 from left - THIS IS THE TARGET

Action bar layout (left to right):
1. Reply text
2. "0 replies" dropdown
3. 👍 LIKE (thumbs up) - SKIP THIS
4. 👎 Thumbs down
5. ♡ HEART (creator heart) - **TARGET THIS ONE**
6. ⋮ Three dots menu

The HEART button is:
- An outline heart shape (not filled)
- Located AFTER the thumbs down button
- Located BEFORE the three-dot menu
- The 5th interactive element in the action bar

Return JSON with the heart button location:
{
  "found": true/false,
  "confidence": "how sure this is the heart not the like",
  "element_description": "what you see",
  "selector": "CSS or XPath selector"
}"""

        response = browser.vision_analyzer.model.generate_content([prompt, img])
        print(f"\n[GEMINI RESPONSE]:")
        print(response.text)

        # Parse response
        text = response.text.strip()
        if '```json' in text:
            text = text.split('```json')[1].split('```')[0]
        elif '```' in text:
            text = text.split('```')[1].split('```')[0]

        result = json.loads(text.strip())

        if result.get('found'):
            print(f"\n[4] Gemini found element!")
            print(f"    Confidence: {result.get('confidence')}")
            print(f"    Description: {result.get('element_description')}")

            selector = result.get('selector', '')
            print(f"    Selector: {selector}")

            # Auto-proceed with click (Gemini has high confidence)
            print(f"\n[5] Gemini has high confidence - proceeding with click...")

            if True:  # Auto-click enabled
                from selenium.webdriver.common.by import By

                # Try to find and click
                if selector.startswith('//'):
                    elements = browser.find_elements(By.XPATH, selector)
                elif '#' in selector or '.' in selector:
                    elements = browser.find_elements(By.CSS_SELECTOR, selector)
                else:
                    elements = browser.find_elements(By.TAG_NAME, 'button')

                if elements:
                    element = elements[0]

                    # Highlight before clicking
                    browser.execute_script("""
                        arguments[0].style.border = '3px solid red';
                        arguments[0].style.backgroundColor = 'rgba(255,0,0,0.2)';
                    """, element)
                    print(f"\n[6] Element highlighted with RED border")
                    print(f"    Check if red border is on the HEART button")
                    time.sleep(2)

                    # Scroll into view and click
                    browser.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                    time.sleep(1)
                    element.click()

                    print(f"[7] ✓ Clicked!")
                    time.sleep(3)
                    print(f"\n[8] Check if heart turned RED")
                else:
                    print(f"[ERROR] Selector found no elements")
            else:
                print(f"[CANCELLED] User cancelled click")
        else:
            print(f"\n[4] Gemini did not find the heart button")

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"[ERROR] Gemini Vision not available")

print(f"\n[DONE] Test complete. Check if heart turned RED.")
print(f"Browser will stay open for 30 seconds...")
time.sleep(30)
