"""
Test Gemini Vision - Target HEART button specifically (not like button)
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.infrastructure.foundups_selenium.src.browser_manager import get_browser_manager
from selenium.webdriver.common.by import By

print("\n" + "="*60)
print("GEMINI VISION - Precise Heart Button Test")
print("="*60 + "\n")

# Get existing browser
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

# Take screenshot
print(f"[3] Taking screenshot for Gemini analysis...")
screenshot = browser.get_screenshot_as_png()

# Use Gemini Vision
print(f"[4] Analyzing with Gemini Vision...")
if hasattr(browser, 'vision_analyzer') and browser.vision_analyzer:
    try:
        import io
        from PIL import Image
        import json

        img = Image.open(io.BytesIO(screenshot))

        prompt = """This is YouTube Studio comments page.

CRITICAL: I need to click the HEART button (♡ creator heart), NOT the thumbs up like button.

The action bar has these buttons in order from left to right:
1. Reply
2. 0 replies (dropdown)
3. 👍 (thumbs up - LIKE button) - DO NOT TARGET THIS
4. 👎 (thumbs down)
5. ♡ (HEART - creator heart button) - TARGET THIS ONE
6. ⋮ (three-dot menu)

Visual characteristics of the HEART button:
- It's an OUTLINE heart icon (♡)
- Located BETWEEN the thumbs down and the three-dot menu
- It's the 5th button from left in the action bar
- Gray outline when not engaged, turns RED when clicked

Please identify the HEART button specifically.

Return only JSON:
{
  "found": true/false,
  "element_type": "button type",
  "position_description": "where it is in the action bar",
  "suggested_selector": "CSS or XPATH selector",
  "confidence": "how confident you are this is the heart not the like"
}"""

        response = browser.vision_analyzer.model.generate_content([prompt, img])
        print(f"\n[GEMINI]:")
        print(response.text)

        # Parse and use
        try:
            # Extract JSON from markdown if needed
            text = response.text.strip()
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0]
            elif '```' in text:
                text = text.split('```')[1].split('```')[0]

            result = json.loads(text.strip())

            if result.get('found'):
                print(f"\n[5] Gemini found HEART button!")
                print(f"    Position: {result.get('position_description')}")
                print(f"    Confidence: {result.get('confidence')}")
                print(f"    Selector: {result.get('suggested_selector')}")

                # Try to click
                print(f"\n[6] Attempting click...")
                selector = result.get('suggested_selector', '')

                # Try different selector types
                if selector.startswith('//'):
                    elements = browser.find_elements(By.XPATH, selector)
                elif '#' in selector or '.' in selector:
                    elements = browser.find_elements(By.CSS_SELECTOR, selector)
                else:
                    # Fallback: search all buttons
                    elements = browser.find_elements(By.TAG_NAME, 'button')
                    print(f"    Searching {len(elements)} buttons...")

                if elements:
                    # Scroll element into view first
                    element = elements[0]
                    browser.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                    print(f"    Scrolled element into view...")
                    time.sleep(1)

                    # Highlight before clicking
                    browser.execute_script("""
                        arguments[0].style.border = '3px solid red';
                        arguments[0].style.backgroundColor = 'rgba(255,0,0,0.1)';
                    """, element)
                    print(f"    Highlighted element (should see RED border)...")
                    time.sleep(2)

                    element.click()
                    print(f"[7] ✓ Clicked!")
                    time.sleep(3)

                    # Check if heart turned red
                    print(f"\n[8] Verifying heart is now red...")
                    time.sleep(2)
                else:
                    print(f"[7] ✗ Selector found no elements")
            else:
                print(f"\n[5] Gemini did not find HEART button")

        except Exception as e:
            print(f"[ERROR] Parsing/clicking: {e}")
            import traceback
            traceback.print_exc()

    except Exception as e:
        print(f"[ERROR] Gemini failed: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"[ERROR] Gemini Vision not enabled")

print(f"\n[DONE] Check if heart button turned RED. Browser staying open.")
input("Press Enter to exit...")
