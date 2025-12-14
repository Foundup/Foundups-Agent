"""
Simple Gemini Vision test - ONE browser window
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.infrastructure.foundups_selenium.src.browser_manager import get_browser_manager
from selenium.webdriver.common.by import By

print("\n" + "="*60)
print("GEMINI VISION - Simple Like Button Test")
print("="*60 + "\n")

# Get existing browser (reuses if already open)
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

I need to find and click the THUMBS UP (like) button on the first comment.

The action bar has: Reply | 0 replies | 👍 | 👎 | ♡ | ⋮

Please identify:
1. Is there a like button visible?
2. What HTML element type is it?
3. What attributes can help me find it?

Return only JSON:
{
  "found": true/false,
  "element_type": "button type",
  "suggested_selector": "CSS or XPATH selector"
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
                print(f"\n[5] Gemini found button!")
                print(f"    Type: {result.get('element_type')}")
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
                    # Scroll element into view first (fix "element not interactable")
                    element = elements[0]
                    browser.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                    print(f"    Scrolled element into view...")
                    time.sleep(1)  # Wait for scroll animation

                    element.click()
                    print(f"[7] ✓ Clicked!")
                    time.sleep(2)
                else:
                    print(f"[7] ✗ Selector found no elements")
            else:
                print(f"\n[5] Gemini did not find button")

        except Exception as e:
            print(f"[ERROR] Parsing/clicking: {e}")

    except Exception as e:
        print(f"[ERROR] Gemini failed: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"[ERROR] Gemini Vision not enabled")

print(f"\n[DONE] Browser staying open. Close manually when ready.")
input("Press Enter to exit...")
