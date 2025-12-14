"""
GEMINI VISION - Click heart and KEEP WINDOW OPEN
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.infrastructure.foundups_selenium.src.browser_manager import get_browser_manager
import json

print("\n" + "="*60)
print("GEMINI VISION - Heart Click (Window Stays Open)")
print("="*60 + "\n")

# Get browser
print("[1] Opening browser...")
browser_manager = get_browser_manager()
browser = browser_manager.get_browser(
    browser_type='chrome',
    profile_name='youtube_move2japan'
)

# Maximize
print("[1.5] Maximizing window...")
browser.maximize_window()
time.sleep(1)

# Navigate
url = "https://studio.youtube.com/channel/UC-LSSlOZwpGIRIYihaz8zCw/comments/inbox"
print(f"[2] Navigating to: {url}")
browser.get(url)
print("[3] Waiting 8 seconds for page to load...")
time.sleep(8)

print(f"\n[4] Taking screenshot for Gemini...")
screenshot_bytes = browser.get_screenshot_as_png()

# Ask Gemini for coordinates
print(f"[5] Asking Gemini Vision to find heart button...")
if hasattr(browser, 'vision_analyzer') and browser.vision_analyzer:
    try:
        import io
        from PIL import Image

        img = Image.open(io.BytesIO(screenshot_bytes))
        img_width, img_height = img.size

        prompt = f"""You are analyzing a YouTube Studio comments page.

Screenshot dimensions: {img_width} x {img_height} pixels

I need to click the CREATOR HEART button on the FIRST comment.

Each comment has these buttons: Reply | 0 replies | Thumbs up | Thumbs down | HEART | Menu

The HEART is a small gray outlined heart icon.

Return ONLY JSON with the exact pixel coordinates:
{{
  "found": true/false,
  "x": pixel_x,
  "y": pixel_y,
  "description": "what you see"
}}"""

        response = browser.vision_analyzer.model.generate_content([prompt, img])
        print(f"\n[GEMINI SAYS]:")
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

            print(f"[6] Gemini found heart at: ({x}, {y})")
            print(f"    Description: {result.get('description')}")

            # Draw red circle
            print(f"\n[7] Drawing RED CIRCLE at target (watch the screen!)...")
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
                ctx.strokeStyle = 'red';
                ctx.lineWidth = 5;
                ctx.stroke();
            """)

            print(f"    RED CIRCLE should be visible now!")
            time.sleep(3)

            # Click
            print(f"\n[8] CLICKING NOW (watch for heart to turn RED)...")
            browser.execute_script(f"""
                var element = document.elementFromPoint({x}, {y});
                if (element) {{
                    element.click();
                    console.log('Clicked:', element);
                }}
            """)

            print(f"\n[9] CLICKED!")
            print(f"    Watch the first comment - the heart should turn RED now!")
            time.sleep(3)

            print(f"\n[SUCCESS] Heart button clicked!")

        else:
            print(f"[ERROR] Gemini could not find heart button")

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()

print("\n" + "="*60)
print("WINDOW WILL STAY OPEN")
print("Press Ctrl+C in terminal to close it")
print("="*60 + "\n")

print("CHECK THE BROWSER:")
print("  - Is there a RED CIRCLE around a button?")
print("  - Did the heart turn RED?")
print("\nPress Ctrl+C to exit...")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n[EXIT] Closing browser...")
