"""
Simple approach: Find LIKE button with Gemini, then offset to the right for HEART
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.infrastructure.foundups_selenium.src.browser_manager import get_browser_manager
import json

print("\n" + "="*60)
print("HEART CLICK - Offset Method")
print("="*60 + "\n")

browser_manager = get_browser_manager()
browser = browser_manager.get_browser(
    browser_type='chrome',
    profile_name='youtube_move2japan'
)

browser.maximize_window()
time.sleep(1)

url = "https://studio.youtube.com/channel/UC-LSSlOZwpGIRIYihaz8zCw/comments/inbox"
print(f"[1] Navigating to: {url}")
browser.get(url)
time.sleep(8)

print(f"[2] Taking screenshot...")
screenshot_bytes = browser.get_screenshot_as_png()

print(f"[3] Finding LIKE button with Gemini...")
if hasattr(browser, 'vision_analyzer') and browser.vision_analyzer:
    try:
        import io
        from PIL import Image

        img = Image.open(io.BytesIO(screenshot_bytes))

        prompt = """Find the THUMBS UP (like) button on the first comment.

Return JSON with its coordinates:
{
  "x": pixel_x,
  "y": pixel_y
}"""

        response = browser.vision_analyzer.model.generate_content([prompt, img])
        text = response.text.strip()
        if '```json' in text:
            text = text.split('```json')[1].split('```')[0]
        elif '```' in text:
            text = text.split('```')[1].split('```')[0]

        result = json.loads(text.strip())
        like_x = result.get('x')
        like_y = result.get('y')

        print(f"    Like button at: ({like_x}, {like_y})")

        # Heart button is ~80-100 pixels to the RIGHT of like button
        heart_x = like_x + 90
        heart_y = like_y

        print(f"\n[4] Calculated heart position: ({heart_x}, {heart_y})")
        print(f"    (90 pixels to the right of like button)")

        # Draw GREEN circle at calculated heart position
        print(f"\n[5] Drawing GREEN CIRCLE at calculated heart position...")
        browser.execute_script(f"""
            var canvas = document.createElement('canvas');
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
            ctx.arc({heart_x}, {heart_y}, 30, 0, 2 * Math.PI);
            ctx.strokeStyle = 'green';
            ctx.lineWidth = 5;
            ctx.stroke();
        """)

        print(f"    GREEN CIRCLE should be on the HEART now!")
        time.sleep(3)

        # Click
        print(f"\n[6] CLICKING at heart position...")
        browser.execute_script(f"""
            var element = document.elementFromPoint({heart_x}, {heart_y});
            if (element) {{
                element.click();
                console.log('Clicked:', element);
            }}
        """)

        print(f"\n[7] CLICKED!")
        print(f"    Watch for RED FILLED HEART to appear!")
        time.sleep(3)

        print(f"\n[SUCCESS] Heart should be clicked now!")

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()

print("\n" + "="*60)
print("WINDOW STAYS OPEN - Press Ctrl+C to exit")
print("Look for:")
print("  - GREEN CIRCLE on the heart button")
print("  - RED FILLED HEART after click")
print("="*60 + "\n")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n[EXIT]")
