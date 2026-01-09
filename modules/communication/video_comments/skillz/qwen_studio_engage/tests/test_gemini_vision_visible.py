"""
GEMINI VISION TEST - Actually SEE and CLICK the heart button
Uses AI vision to find buttons, not Selenium selectors
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.infrastructure.foundups_selenium.src.browser_manager import get_browser_manager
from selenium.webdriver.common.by import By
import json

print("\n" + "="*60)
print("GEMINI VISION - Heart Button Click Test")
print("="*60 + "\n")

# Get browser (Gemini Vision auto-enabled)
print("[1] Opening browser with Gemini Vision...")
browser_manager = get_browser_manager()
browser = browser_manager.get_browser(
    browser_type='chrome',
    profile_name='youtube_move2japan'
)

# Make visible
print("[1.5] Maximizing window...")
browser.maximize_window()
time.sleep(1)

# Navigate
url = "https://studio.youtube.com/channel/UC-LSSlOZwpGIRIYihaz8zCw/comments/inbox"
print(f"[2] Navigating to: {url}")
browser.get(url)
time.sleep(8)

print(f"[3] Taking screenshot for Gemini to analyze...")
screenshot_bytes = browser.get_screenshot_as_png()

# Use Gemini Vision to find the HEART button
print(f"[4] Asking Gemini Vision to find the HEART button...")
if hasattr(browser, 'vision_analyzer') and browser.vision_analyzer:
    try:
        import io
        from PIL import Image

        img = Image.open(io.BytesIO(screenshot_bytes))

        prompt = """You are looking at a YouTube Studio comments page.

I need to find and click the CREATOR HEART button (heart icon) on the FIRST comment.

Each comment has an action bar with these buttons from left to right:
- Reply button (text)
- "0 replies" dropdown
- Thumbs up (like) button
- Thumbs down (dislike) button
- HEART button (creator heart - this is what I want!)
- Three-dot menu

The HEART button is a gray outlined heart icon. When clicked, it turns RED.

Please identify:
1. Can you see the heart button on the first comment?
2. What is a CSS selector or XPath that will find it?
3. Where is it positioned on screen?

Return ONLY valid JSON:
{
  "found": true/false,
  "selector": "CSS or XPath selector",
  "description": "brief description of location"
}"""

        response = browser.vision_analyzer.model.generate_content([prompt, img])
        print(f"\n[GEMINI RESPONSE]")
        print(response.text)
        print()

        # Parse response
        text = response.text.strip()
        if '```json' in text:
            text = text.split('```json')[1].split('```')[0]
        elif '```' in text:
            text = text.split('```')[1].split('```')[0]

        result = json.loads(text.strip())

        if result.get('found'):
            print(f"[5] Gemini found the heart button!")
            print(f"    Selector: {result.get('selector')}")
            print(f"    Description: {result.get('description')}")

            # Try to click using the selector
            print(f"\n[6] Attempting to click using Gemini's selector...")
            selector = result.get('selector', '')

            elements = []
            if selector.startswith('//'):
                elements = browser.find_elements(By.XPATH, selector)
            elif selector:
                try:
                    elements = browser.find_elements(By.CSS_SELECTOR, selector)
                except:
                    # If CSS fails, try all buttons and click first one
                    print(f"    CSS selector failed, trying visual approach...")
                    elements = browser.find_elements(By.TAG_NAME, 'button')

            if elements:
                element = elements[0]

                # Scroll into view
                print(f"    Scrolling element into view...")
                browser.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                time.sleep(2)

                # Highlight the element before clicking (visual feedback)
                print(f"    Highlighting element (you should see a red border)...")
                browser.execute_script("arguments[0].style.border='3px solid red'", element)
                time.sleep(2)

                print(f"\n[7] CLICKING NOW (WATCH THE SCREEN)...")
                element.click()

                print(f"[8] CLICKED! Watch for the RED HEART to appear!")
                time.sleep(3)

                print(f"\n[SUCCESS] Heart button clicked!")
            else:
                print(f"[ERROR] Selector found no elements")

        else:
            print(f"[5] Gemini could not find the heart button")

    except Exception as e:
        print(f"[ERROR] Gemini Vision failed: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"[ERROR] Gemini Vision not available")

print("\n" + "="*60)
print("Browser window staying open for 30 seconds")
print("Look for the RED HEART on the first comment!")
print("="*60 + "\n")

time.sleep(30)

print("[DONE] Test complete")
