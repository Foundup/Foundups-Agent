"""
FINAL AUTONOMOUS GEMINI VISION TEST
Launches own Chrome with FoundUps Gemini Vision integration
Zero manual intervention required
"""
import sys
import time
from pathlib import Path

repo_root = Path(__file__).resolve().parent
sys.path.insert(0, str(repo_root))

from modules.infrastructure.foundups_selenium.src.browser_manager import get_browser_manager
from selenium.webdriver.common.by import By
import json

print("\n" + "="*70)
print(" AUTONOMOUS GEMINI VISION - YouTube Studio Heart Click")
print(" 0102-Driven | Zero Manual Intervention")
print("="*70 + "\n")

# Step 1: Launch FoundUps browser with Gemini Vision
print("[1] Launching FoundUps browser with Gemini Vision...")
browser_manager = get_browser_manager()
browser = browser_manager.get_browser(
    browser_type='chrome',
    profile_name='youtube_move2japan'
)
print("[OK] Browser launched with vision_analyzer embedded")

# Step 2: Navigate to YouTube Studio
url = "https://studio.youtube.com/channel/UC-LSSlOZwpGIRIYihaz8zCw/comments/inbox"
print(f"\n[2] Navigating to YouTube Studio...")
print(f"    URL: {url}")
browser.get(url)
time.sleep(8)  # Wait for page load
print("[OK] Page loaded")

# Step 3: Verify Gemini Vision available
print("\n[3] Verifying Gemini Vision...")
if not hasattr(browser, 'vision_analyzer') or not browser.vision_analyzer:
    print("[ERROR] vision_analyzer not available!")
    browser.quit()
    sys.exit(1)
print("[OK] Gemini Vision operational")

# Step 4: Use Gemini Vision to find heart button
print("\n[4] Gemini analyzing page for heart button...")

prompt = """TASK: Find the CREATOR HEART button (NOT like button) on YouTube Studio.

CRITICAL DISTINCTIONS:
- LIKE button: Thumbs up icon - position 3 from left - IGNORE THIS
- HEART button: Outlined heart icon - position 5 from left - TARGET THIS

The heart is between thumbs down and three-dot menu in comment action bar.

Return JSON:
{
  "found": true/false,
  "confidence": "High/Medium/Low",
  "element_description": "describe heart button only",
  "selector": "CSS selector or XPath for HEART button"
}
"""

try:
    import io
    from PIL import Image

    screenshot = browser.get_screenshot_as_png()
    img = Image.open(io.BytesIO(screenshot))

    response = browser.vision_analyzer.model.generate_content([prompt, img])
    result = response.text
    print(f"\n[GEMINI RESPONSE]:\n{result}\n")

    # Parse JSON
    if "```json" in result:
        json_str = result.split("```json")[1].split("```")[0].strip()
    elif "```" in result:
        json_str = result.split("```")[1].split("```")[0].strip()
    else:
        json_str = result

    result_data = json.loads(json_str)

    print(f"[5] Gemini Result:")
    print(f"    Found: {result_data.get('found', False)}")
    print(f"    Confidence: {result_data.get('confidence', 'Unknown')}")
    print(f"    Description: {result_data.get('element_description', 'N/A')}")
    print(f"    Selector: {result_data.get('selector', 'N/A')}")

    if not result_data.get('found', False):
        print("\n[ERROR] Gemini did not find heart button")
        browser.quit()
        sys.exit(1)

except Exception as e:
    print(f"[ERROR] Gemini analysis failed: {e}")
    import traceback
    traceback.print_exc()
    browser.quit()
    sys.exit(1)

# Step 5: Locate and click element
try:
    print("\n[6] Locating element via Selenium...")
    selector = result_data.get('selector', '')

# Try multiple strategies
elements = []

# Strategy 1: Try Gemini's full selector
try:
    if selector.startswith('//'):
        elements = browser.find_elements(By.XPATH, selector)
    elif selector:
        elements = browser.find_elements(By.CSS_SELECTOR, selector)
except Exception as e:
    print(f"    [WARN] Gemini selector failed: {e}")

# Strategy 2: If no elements, try simpler aria-label selector (more stable)
if not elements and 'aria-label="Give appreciation"' in selector:
    print("    [INFO] Trying simpler aria-label selector...")
    try:
        elements = browser.find_elements(By.CSS_SELECTOR, 'button[aria-label="Give appreciation"]')
    except Exception as e:
        print(f"    [WARN] Aria-label selector failed: {e}")

# Strategy 3: Find all yt-icon-button elements and filter
if not elements:
    print("    [INFO] Trying yt-icon-button search...")
    try:
        all_buttons = browser.find_elements(By.TAG_NAME, 'yt-icon-button')
        for btn in all_buttons:
            aria = btn.get_attribute('aria-label') or ''
            if 'appreciation' in aria.lower() or 'heart' in aria.lower():
                elements = [btn]
                break
    except Exception as e:
        print(f"    [WARN] Icon button search failed: {e}")

if not elements:
    print(f"[ERROR] All selector strategies failed - no elements found")
    print(f"    Gemini selector: {selector}")
    browser.quit()
    sys.exit(1)

element = elements[0]
print(f"[OK] Element located: <{element.tag_name}>")

# Highlight (2sec RED border)
browser.execute_script("""
    arguments[0].style.border = '3px solid red';
    arguments[0].style.backgroundColor = 'rgba(255,0,0,0.2)';
""", element)
print("\n[7] Element highlighted with RED border (2 seconds)")
time.sleep(2)

# Scroll and click
browser.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
time.sleep(1)
element.click()

print("\n" + "="*70)
print("[SUCCESS] Autonomous heart button click executed!")
print("="*70)
print("\nCheck browser - heart should be RED (filled)")
time.sleep(5)

    print("\n[OK] Test complete - browser staying open for 30 seconds...")
    time.sleep(30)

except Exception as e:
    print(f"[ERROR] Click failed: {e}")
    import traceback
    traceback.print_exc()
    browser.quit()
    sys.exit(1)

print("\nClosing browser...")
browser.quit()
print("Done.")
