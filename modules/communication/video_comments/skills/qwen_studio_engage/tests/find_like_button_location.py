"""
Find the actual pixel location of the Like button
"""
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(repo_root))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
import io

chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(options=chrome_options)

# Get screenshot size
screenshot_bytes = driver.get_screenshot_as_png()
img = Image.open(io.BytesIO(screenshot_bytes))
screenshot_size = img.size

print(f"\nScreenshot size: {screenshot_size}")

# Find Like button location
result = driver.execute_script("""
    const likeBtn = document.querySelector('ytcp-comment-thread:first-child ytcp-icon-button[aria-label="Like"]');
    if (!likeBtn) return {error: 'Like button not found'};

    const rect = likeBtn.getBoundingClientRect();
    return {
        found: true,
        center: {
            x: Math.round(rect.left + rect.width / 2),
            y: Math.round(rect.top + rect.height / 2)
        },
        rect: {
            left: Math.round(rect.left),
            top: Math.round(rect.top),
            right: Math.round(rect.right),
            bottom: Math.round(rect.bottom),
            width: Math.round(rect.width),
            height: Math.round(rect.height)
        }
    };
""")

if 'error' in result:
    print(f"ERROR: {result['error']}")
else:
    print(f"\nLike button location:")
    print(f"  Center: ({result['center']['x']}, {result['center']['y']})")
    print(f"  Bounding box: {result['rect']}")

    # Convert to 1000x1000 box coordinates for UI-TARS
    box_x = int((result['center']['x'] / screenshot_size[0]) * 1000)
    box_y = int((result['center']['y'] / screenshot_size[1]) * 1000)

    print(f"\n  In UI-TARS 1000x1000 space: ({box_x}, {box_y})")

    # What UI-TARS actually used
    print(f"\nWhat UI-TARS clicked:")
    print(f"  Box coordinates: (509, 304)")
    print(f"  Pixel coordinates: (977, 248)")

    print(f"\nDifference:")
    print(f"  Box space: ({box_x - 509}, {box_y - 304})")
    print(f"  Pixel space: ({result['center']['x'] - 977}, {result['center']['y'] - 248})")

    # Test if we can click the correct location
    print(f"\nTesting manual click at correct location...")
    clicked = driver.execute_script("""
        const x = arguments[0];
        const y = arguments[1];
        const el = document.elementFromPoint(x, y);
        if (!el) return {error: 'No element at coordinates'};

        return {
            tagName: el.tagName,
            aria_label: el.getAttribute('aria-label'),
            is_like_button: el.tagName === 'YTCP-ICON-BUTTON' && el.getAttribute('aria-label') === 'Like'
        };
    """, result['center']['x'], result['center']['y'])

    if clicked.get('is_like_button'):
        print(f"  Success! Element at correct location is the Like button")
    else:
        print(f"  Element at that location: {clicked['tagName']} (aria-label: {clicked['aria_label']})")
