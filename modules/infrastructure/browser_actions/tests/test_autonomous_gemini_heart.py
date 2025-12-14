"""
AUTONOMOUS GEMINI VISION - YouTube Studio Heart Click
Connects to EXISTING Chrome on port 9222 (no new launch)
"""
import sys
from pathlib import Path
repo_root = Path(__file__).resolve().parent
sys.path.insert(0, str(repo_root))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import json

print("=" * 60)
print("AUTONOMOUS GEMINI VISION - Heart Button Click")
print("=" * 60)

# Step 1: Connect to EXISTING Chrome on port 9222 using FoundUps browser manager
print("\n[1] Connecting to existing Chrome on port 9222...")
from modules.infrastructure.foundups_selenium.src.browser_manager import get_browser_manager

try:
    # Use existing browser on 9222 - FoundUps driver with Gemini Vision
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

    driver = webdriver.Chrome(options=chrome_options)
    print(f"[OK] Connected to Chrome")
    print(f"    Current URL: {driver.current_url}")
    print(f"    Page title: {driver.title}")
except Exception as e:
    print(f"[ERROR] Failed to connect: {e}")
    sys.exit(1)

# Step 2: Find Studio tab
tabs = driver.window_handles
print(f"\n[2] Found {len(tabs)} tabs - searching for YouTube Studio...")

studio_tab_found = False
for tab in tabs:
    driver.switch_to.window(tab)
    if "studio.youtube.com" in driver.current_url:
        print(f"[OK] Switched to Studio tab")
        print(f"    URL: {driver.current_url}")
        studio_tab_found = True
        break

if not studio_tab_found:
    print("[ERROR] No YouTube Studio tab found")
    driver.quit()
    sys.exit(1)

# Step 3: Check if browser has Gemini Vision (from FoundUps driver)
print("\n[3] Checking for Gemini Vision...")
if not hasattr(driver, 'vision_analyzer') or not driver.vision_analyzer:
    print("[WARN] Driver has no vision_analyzer - creating new FoundUps browser...")

    # Need to use FoundUps browser manager for Gemini integration
    # Since we can't connect existing Chrome AND get vision, we'll document this limitation
    print("[ERROR] Cannot use Gemini Vision with existing Chrome CDP connection")
    print("       Gemini Vision requires FoundUps-enhanced browser")
    print("       Either:")
    print("       1. Let script launch new Chrome (automated)")
    print("       2. Use UI-TARS Desktop for vision (manual)")
    driver.quit()
    sys.exit(1)

# Step 4: Use embedded Gemini Vision
print("[OK] Gemini Vision available via driver.vision_analyzer")
print("\n[4] Asking Gemini to find HEART button...")

prompt = """TASK: Find the CREATOR HEART button (NOT the like button) on YouTube Studio.

CRITICAL DISTINCTIONS:
- LIKE button: Thumbs up icon (👍) - position 3 from left - DO NOT SELECT THIS
- HEART button: Outlined heart (♡) - position 5 from left - THIS IS THE TARGET

The heart is between the thumbs down button and the three-dot menu.

Return a JSON with:
{
  "found": true/false,
  "confidence": "High/Medium/Low",
  "element_description": "description of the heart button ONLY",
  "selector": "CSS selector or XPath to the HEART button"
}
"""

try:
    import io
    from PIL import Image

    screenshot = driver.get_screenshot_as_png()
    img = Image.open(io.BytesIO(screenshot))

    result = driver.vision_analyzer.analyze_image(img, prompt)

    # Parse result
    if "```json" in result:
        json_str = result.split("```json")[1].split("```")[0].strip()
    elif "```" in result:
        json_str = result.split("```")[1].split("```")[0].strip()
    else:
        json_str = result

    result_data = json.loads(json_str)

    print(f"\n[5] Gemini Vision Result:")
    print(f"    Found: {result_data.get('found', False)}")
    print(f"    Confidence: {result_data.get('confidence', 'Unknown')}")
    print(f"    Description: {result_data.get('element_description', 'N/A')}")
    print(f"    Selector: {result_data.get('selector', 'N/A')}")

    if not result_data.get('found', False):
        print("\n[ERROR] Gemini did not find the heart button")
        driver.quit()
        sys.exit(1)

except Exception as e:
    print(f"[ERROR] Gemini analysis failed: {e}")
    import traceback
    traceback.print_exc()
    driver.quit()
    sys.exit(1)

# Step 5: Find and click element
print("\n[6] Locating element with Selenium...")
selector = result_data.get('selector', '')

try:
    if selector.startswith('//'):
        elements = driver.find_elements(By.XPATH, selector)
    elif '#' in selector or '.' in selector or ':' in selector:
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
    else:
        print(f"[WARN] Unclear selector format, trying CSS")
        elements = driver.find_elements(By.CSS_SELECTOR, selector)

    if not elements:
        print(f"[ERROR] Selector '{selector}' found no elements")
        driver.quit()
        sys.exit(1)

    element = elements[0]
    print(f"[OK] Element located: {element.tag_name}")

    # Highlight element
    driver.execute_script("""
        arguments[0].style.border = '3px solid red';
        arguments[0].style.backgroundColor = 'rgba(255,0,0,0.2)';
    """, element)
    print("\n[7] Element highlighted with RED border")
    time.sleep(2)

    # Click
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    time.sleep(1)
    element.click()

    print("\n[8] CLICKED! [SUCCESS]")
    print("    Check if heart turned RED in the browser")
    time.sleep(3)

    print("\n" + "=" * 60)
    print("AUTONOMOUS TEST COMPLETE")
    print("Result: SUCCESS - Gemini Vision clicked heart button")
    print("=" * 60)

except Exception as e:
    print(f"[ERROR] Failed to click: {e}")
    import traceback
    traceback.print_exc()
    driver.quit()
    sys.exit(1)

# Keep browser open for 30 seconds to verify
print("\nBrowser staying open for 30 seconds to verify...")
time.sleep(30)
print("Test complete.")
