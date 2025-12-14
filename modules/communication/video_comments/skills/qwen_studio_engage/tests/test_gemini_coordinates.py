"""
GEMINI VISION - Click by COORDINATES (not CSS selectors)
Ask Gemini where the heart button is in pixels, then click there
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.infrastructure.foundups_selenium.src.browser_manager import get_browser_manager
from selenium.webdriver.common.action_chains import ActionChains
import json

print("\n" + "="*60)
print("GEMINI VISION - Coordinate-Based Heart Click")
print("="*60 + "\n")

# Get browser
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

print(f"[3] Taking screenshot...")
screenshot_bytes = browser.get_screenshot_as_png()

# Get window size for coordinate conversion
window_size = browser.get_window_size()
print(f"    Window size: {window_size['width']}x{window_size['height']}")

# Use Gemini Vision to find coordinates
print(f"[4] Asking Gemini for PIXEL COORDINATES of heart button...")
if hasattr(browser, 'vision_analyzer') and browser.vision_analyzer:
    try:
        import io
        from PIL import Image

        img = Image.open(io.BytesIO(screenshot_bytes))
        img_width, img_height = img.size
        print(f"    Screenshot size: {img_width}x{img_height}")

        prompt = f"""You are analyzing a YouTube Studio comments page screenshot.

Screenshot dimensions: {img_width} x {img_height} pixels

I need to click the CREATOR HEART button (heart icon) on the FIRST comment visible on the page.

Each comment has an action bar below it with buttons:
Reply | 0 replies | Thumbs up | Thumbs down | HEART | Three-dot menu

The HEART button is a small gray outlined heart icon.

Please tell me the EXACT PIXEL COORDINATES where I should click to hit the heart button.

Return ONLY valid JSON:
{{
  "found": true/false,
  "x": pixel_x_coordinate,
  "y": pixel_y_coordinate,
  "description": "what you see at those coordinates"
}}

The coordinates should be relative to the screenshot (0,0 is top-left corner)."""

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
            x = result.get('x')
            y = result.get('y')

            print(f"[5] Gemini found the heart button!")
            print(f"    Coordinates: ({x}, {y})")
            print(f"    Description: {result.get('description')}")

            # Draw a red circle at those coordinates (visual feedback)
            print(f"\n[6] Drawing red circle at target coordinates...")
            browser.execute_script(f"""
                var canvas = document.createElement('canvas');
                canvas.id = 'clickMarker';
                canvas.style.position = 'fixed';
                canvas.style.top = '0';
                canvas.style.left = '0';
                canvas.style.width = '100%';
                canvas.style.height = '100%';
                canvas.style.pointerEvents = 'none';
                canvas.style.zIndex = '999999';
                canvas.width = window.innerWidth;
                canvas.height = window.innerHeight;
                document.body.appendChild(canvas);

                var ctx = canvas.getContext('2d');
                ctx.beginPath();
                ctx.arc({x}, {y}, 20, 0, 2 * Math.PI);
                ctx.strokeStyle = 'red';
                ctx.lineWidth = 3;
                ctx.stroke();
            """)
            time.sleep(2)

            # Click at those coordinates using JavaScript
            print(f"\n[7] CLICKING at coordinates ({x}, {y})...")
            browser.execute_script(f"""
                var element = document.elementFromPoint({x}, {y});
                if (element) {{
                    console.log('Clicking element:', element);
                    element.click();
                }} else {{
                    console.log('No element found at ({x}, {y})');
                }}
            """)

            print(f"[8] CLICKED! Watch for the RED HEART!")
            time.sleep(3)

            print(f"\n[SUCCESS] Click executed at Gemini's coordinates!")
        else:
            print(f"[5] Gemini could not find the heart button")

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"[ERROR] Gemini Vision not available")

print("\n" + "="*60)
print("Browser staying open for 30 seconds")
print("Look for the RED HEART!")
print("="*60 + "\n")

time.sleep(30)

print("[DONE] Test complete")
