"""
GEMINI VISION - Find the HEART button (NOT the like button)
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.infrastructure.foundups_selenium.src.browser_manager import get_browser_manager
import json

print("\n" + "="*60)
print("GEMINI VISION - Heart Button (NOT Like)")
print("="*60 + "\n")

# Get browser
print("[1] Opening browser...")
browser_manager = get_browser_manager()
browser = browser_manager.get_browser(
    browser_type='chrome',
    profile_name='youtube_move2japan'
)

browser.maximize_window()
time.sleep(1)

# Navigate
url = "https://studio.youtube.com/channel/UC-LSSlOZwpGIRIYihaz8zCw/comments/inbox"
print(f"[2] Navigating to: {url}")
browser.get(url)
time.sleep(8)

print(f"[3] Taking screenshot...")
screenshot_bytes = browser.get_screenshot_as_png()

# Ask Gemini with VERY specific instructions
print(f"[4] Asking Gemini to find HEART button (NOT like)...")
if hasattr(browser, 'vision_analyzer') and browser.vision_analyzer:
    try:
        import io
        from PIL import Image

        img = Image.open(io.BytesIO(screenshot_bytes))
        img_width, img_height = img.size

        prompt = f"""You are looking at a YouTube Studio comments page.

Screenshot size: {img_width} x {img_height} pixels

IMPORTANT: I need the CREATOR HEART button on the FIRST comment.

Each comment has these buttons in this exact order from LEFT to RIGHT:
1. Reply (text button)
2. "0 replies" (dropdown)
3. THUMBS UP / LIKE button (this is NOT what I want!)
4. THUMBS DOWN / DISLIKE button
5. HEART button (HOLLOW HEART OUTLINE - THIS IS WHAT I WANT!)
6. Three-dot menu

The HEART button is:
- To the RIGHT of the thumbs down button
- The THIRD icon button (after thumbs up and thumbs down)
- A HOLLOW HEART OUTLINE (not filled)
- When clicked, it turns into a RED FILLED HEART

DO NOT give me the thumbs up/like button coordinates.
I need the HEART button which is 2 buttons to the RIGHT of the thumbs up.

Return ONLY JSON:
{{
  "found": true/false,
  "x": pixel_x_coordinate_of_HEART_button,
  "y": pixel_y_coordinate_of_HEART_button,
  "description": "what you see at those coordinates"
}}"""

        response = browser.vision_analyzer.model.generate_content([prompt, img])
        print(f"\n[GEMINI RESPONSE]:")
        print(response.text)
        print()

        # Parse
        text = response.text.strip()
        if '```json' in text:
            text = text.split('```json')[1].split('```')[0]
        elif '```' in text:
            text = text.split('```')[1].split('```')[0]

        result = json.loads(text.strip())

        if result.get('found'):
            x = result.get('x')
            y = result.get('y')

            print(f"[5] Gemini found HEART at: ({x}, {y})")
            print(f"    Description: {result.get('description')}")

            # Draw BLUE circle (different color so we can see it's a new test)
            print(f"\n[6] Drawing BLUE CIRCLE at heart button...")
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
                ctx.arc({x}, {y}, 30, 0, 2 * Math.PI);
                ctx.strokeStyle = 'blue';
                ctx.lineWidth = 5;
                ctx.stroke();
            """)

            print(f"    BLUE CIRCLE should be on the HEART now!")
            print(f"    (If it's on the like button again, Gemini made the same mistake)")
            time.sleep(3)

            # Click
            print(f"\n[7] CLICKING the HEART button...")
            browser.execute_script(f"""
                var element = document.elementFromPoint({x}, {y});
                if (element) {{
                    element.click();
                }}
            """)

            print(f"\n[8] CLICKED!")
            print(f"    Watch for the heart to turn RED (filled heart)")
            time.sleep(3)

            print(f"\n[SUCCESS] Clicked at Gemini's coordinates!")

        else:
            print(f"[ERROR] Gemini could not find heart button")

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()

print("\n" + "="*60)
print("WINDOW STAYS OPEN")
print("Check if BLUE CIRCLE is on the HEART button")
print("(If it's on thumbs up again, we need a different approach)")
print("Press Ctrl+C to exit...")
print("="*60 + "\n")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n[EXIT]")
