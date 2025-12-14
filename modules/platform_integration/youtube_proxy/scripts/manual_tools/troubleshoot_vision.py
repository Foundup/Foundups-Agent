"""
Troubleshoot UI-TARS vision integration
- Saves debug screenshots
- Logs full model responses
- Tests coordinate accuracy
"""
from pathlib import Path
import sys
import os

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
os.chdir(REPO_ROOT)

import asyncio
import base64
import logging
import os
import requests
from pathlib import Path
from PIL import Image
import io
from datetime import datetime

# Set up detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_vision_detection():
    """Test UI-TARS vision detection with full debugging."""

    print("\n" + "="*80)
    print(" UI-TARS TROUBLESHOOTING - VISION DETECTION")
    print("="*80)

    # 1. Connect to existing Chrome
    from modules.infrastructure.foundups_selenium.src.foundups_driver import FoundUpsDriver

    print("\n[1] Connecting to Chrome on port 9222...")
    driver = FoundUpsDriver(port=9222)
    print(f"    URL: {driver.current_url}")
    print(f"    Window size: {driver.get_window_size()}")

    # 2. Capture screenshot
    print("\n[2] Capturing screenshot...")
    screenshot_bytes = driver.get_screenshot_as_png()

    # Resize for vision model
    img = Image.open(io.BytesIO(screenshot_bytes))
    original_size = img.size
    print(f"    Original size: {original_size}")

    if img.width > 1280:
        ratio = 1280 / img.width
        new_size = (1280, int(img.height * ratio))
        img = img.resize(new_size, Image.Resampling.LANCZOS)
        print(f"    Resized to: {new_size}")

    # Save debug screenshot
    debug_dir = Path("modules/infrastructure/foundups_vision/memory/screenshots/debug")
    debug_dir.mkdir(parents=True, exist_ok=True)
    debug_path = debug_dir / f"debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    img.save(debug_path)
    print(f"    Saved: {debug_path}")

    # Convert to base64
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    screenshot_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
    print(f"    Base64 size: {len(screenshot_base64)} bytes")

    # 3. Test with different descriptions
    descriptions = [
        "thumbs up like button",
        "gray thumbs up icon",
        "like button in the comment actions",
    ]

    for desc in descriptions:
        print(f"\n[3] Testing description: '{desc}'")
        print("="*80)

        # Build UI-TARS Desktop format prompt
        prompt = f"""You are a GUI agent. Find and click the {desc} in this screenshot.

## Output Format
```
Thought: ...
Action: ...
```

## Action Space
click(start_box='<|box_start|>(x,y)<|box_end|>')

## Task
Locate the {desc} and perform a click action on it."""

        print(f"    Prompt: {prompt[:100]}...")

        # Call LM Studio API
        tars_api_url = "http://127.0.0.1:1234"

        print(f"    Calling {tars_api_url}/v1/chat/completions...")

        try:
            response = requests.post(
                f"{tars_api_url}/v1/chat/completions",
                json={
                    "model": "ui-tars-1.5-7b",
                    "messages": [{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/png;base64,{screenshot_base64}"}
                            }
                        ]
                    }],
                    "max_tokens": 200,
                    "temperature": 0.1,
                },
                timeout=90
            )

            if response.status_code == 200:
                response_data = response.json()
                model_output = response_data['choices'][0]['message']['content']

                print("\n    [MODEL RESPONSE]")
                print("    " + "-"*76)
                print("    " + model_output.replace("\n", "\n    "))
                print("    " + "-"*76)

                # Parse coordinates
                import re
                coords_match = re.search(r'click\(start_box=["\']<\|box_start\|>\((\d+),\s*(\d+)\)<\|box_end\|>["\']', model_output)

                if coords_match:
                    box_x = int(coords_match.group(1))
                    box_y = int(coords_match.group(2))
                    normalized_x = box_x / 1000.0
                    normalized_y = box_y / 1000.0

                    window_size = driver.get_window_size()
                    pixel_x = int(normalized_x * window_size['width'])
                    pixel_y = int(normalized_y * window_size['height'])

                    print(f"\n    [COORDINATES]")
                    print(f"      Box (1000x1000 space): ({box_x}, {box_y})")
                    print(f"      Normalized (0-1): ({normalized_x:.3f}, {normalized_y:.3f})")
                    print(f"      Pixel (actual): ({pixel_x}, {pixel_y})")
                    print(f"      Window size: {window_size}")

                    # Test click
                    print(f"\n    [TESTING CLICK at ({pixel_x}, {pixel_y})]")
                    element_found = driver.execute_script(f"""
                        const element = document.elementFromPoint({pixel_x}, {pixel_y});
                        if (element) {{
                            console.log('Element found:', element.tagName, element.className, element.id);
                            return {{
                                tag: element.tagName,
                                className: element.className,
                                id: element.id,
                                text: element.innerText?.substring(0, 50)
                            }};
                        }}
                        return null;
                    """)

                    if element_found:
                        print(f"      ✓ Element found: {element_found}")
                    else:
                        print(f"      ✗ No element at coordinates")
                else:
                    print(f"\n    ✗ Could not parse coordinates from response")
            else:
                print(f"    ✗ API error: {response.status_code} - {response.text[:200]}")

        except Exception as e:
            print(f"    ✗ Exception: {e}")

        print("\n")

    print("="*80)
    print(" TROUBLESHOOTING COMPLETE")
    print("="*80)
    print(f"\nDebug screenshot saved to: {debug_path}")
    print("Check the model responses above to see what UI-TARS is detecting")

if __name__ == "__main__":
    asyncio.run(test_vision_detection())
