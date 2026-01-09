"""
Test: Show what element UI-TARS is actually clicking

This intercepts the click coordinates and shows what element is at that location.
"""
import asyncio
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(repo_root))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from modules.infrastructure.foundups_vision.src.ui_tars_bridge import UITarsBridge

async def test_what_gets_clicked():
    print("\n" + "="*80)
    print(" WHAT ELEMENT GETS CLICKED TEST")
    print("="*80)

    # Connect to browser
    print("\n[1] Connecting to Chrome...")
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=chrome_options)
    print(f"[OK] Connected: {driver.current_url[:60]}...")

    # Initialize UI-TARS Bridge
    print("\n[2] Initializing UI-TARS Bridge...")
    bridge = UITarsBridge(browser_port=9222)
    await bridge.connect()
    print("[OK] UI-TARS ready")

    # Request click
    print("\n[3] Requesting click on Like button...")
    print("Description: 'gray thumbs up Like button in the action bar on the first comment'")

    # This will call UI-TARS and get coordinates
    click_result = await bridge.click(
        "gray thumbs up Like button in the action bar on the first comment",
        driver=driver
    )

    if not click_result.success:
        print(f"[ERROR] Click failed: {click_result.error}")
        return

    # Get the coordinates from metadata
    coords = click_result.metadata.get('coordinates', {})
    box_coords = coords.get('box', (0, 0))

    print(f"\n[OK] UI-TARS found element:")
    print(f"  Box coordinates (1000x1000 space): {box_coords}")
    print(f"  Normalized: ({coords.get('x'):.3f}, {coords.get('y'):.3f})")
    print(f"  Thought: {click_result.metadata.get('thought', 'N/A')[:150]}...")

    # Now let's see what element is ACTUALLY at those pixel coordinates
    print("\n[4] Checking what element is at the converted pixel coordinates...")

    # Get screenshot dimensions
    screenshot_bytes = driver.get_screenshot_as_png()
    from PIL import Image
    import io
    img = Image.open(io.BytesIO(screenshot_bytes))
    screenshot_size = img.size

    # Convert box coordinates to pixels (same logic as UITarsBridge)
    pixel_x = int((box_coords[0] / 1000.0) * screenshot_size[0])
    pixel_y = int((box_coords[1] / 1000.0) * screenshot_size[1])

    print(f"  Screenshot size: {screenshot_size}")
    print(f"  Pixel coordinates: ({pixel_x}, {pixel_y})")

    # Get the element at those coordinates
    element_info = driver.execute_script("""
        const x = arguments[0];
        const y = arguments[1];
        const el = document.elementFromPoint(x, y);

        if (!el) return {error: 'No element at coordinates'};

        return {
            tagName: el.tagName,
            id: el.id,
            className: el.className,
            aria_label: el.getAttribute('aria-label'),
            aria_pressed: el.getAttribute('aria-pressed'),
            text: el.textContent.trim().substring(0, 100),
            innerHTML_snippet: el.innerHTML.substring(0, 150),

            // Check if it's the button or a child/parent
            is_ytcp_icon_button: el.tagName === 'YTCP-ICON-BUTTON',
            is_button: el.tagName === 'BUTTON',

            // Get parent info
            parent: el.parentElement ? {
                tagName: el.parentElement.tagName,
                className: el.parentElement.className,
                aria_label: el.parentElement.getAttribute('aria-label')
            } : null
        };
    """, pixel_x, pixel_y)

    if 'error' in element_info:
        print(f"[ERROR] {element_info['error']}")
        return

    print("\n[ELEMENT AT COORDINATES]")
    print(f"  Tag: {element_info['tagName']}")
    print(f"  ID: {element_info['id']}")
    print(f"  Class: {element_info['className']}")
    print(f"  aria-label: {element_info['aria_label']}")
    print(f"  aria-pressed: {element_info['aria_pressed']}")
    print(f"  Text: {element_info['text']}")
    print(f"  Is YTCP-ICON-BUTTON: {element_info['is_ytcp_icon_button']}")
    print(f"  Is BUTTON: {element_info['is_button']}")

    if element_info['parent']:
        print(f"\n  Parent Tag: {element_info['parent']['tagName']}")
        print(f"  Parent Class: {element_info['parent']['className']}")
        print(f"  Parent aria-label: {element_info['parent']['aria_label']}")

    # Diagnose
    print("\n" + "="*80)
    print(" DIAGNOSIS")
    print("="*80)

    if element_info['aria_label'] == 'Like':
        print("\n✓ CORRECT! Clicked the Like button")
    elif element_info['is_ytcp_icon_button'] and element_info['parent'] and element_info['parent'].get('aria_label') == 'Like':
        print("\n⚠ CLOSE! Clicked child of Like button (might still work)")
    else:
        print("\n✗ WRONG ELEMENT! Did NOT click the Like button")
        print(f"  Expected: YTCP-ICON-BUTTON with aria-label='Like'")
        print(f"  Got: {element_info['tagName']} with aria-label='{element_info['aria_label']}'")

    # Show the correct Like button selector
    print("\n[5] Finding the ACTUAL Like button for comparison...")
    correct_button = driver.execute_script("""
        const likeBtn = document.querySelector('ytcp-comment-thread:first-child ytcp-icon-button[aria-label="Like"]');
        if (!likeBtn) return {error: 'Like button not found'};

        const rect = likeBtn.getBoundingClientRect();
        return {
            found: true,
            center_x: Math.round(rect.left + rect.width / 2),
            center_y: Math.round(rect.top + rect.height / 2),
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

    if correct_button.get('found'):
        print("\n[ACTUAL LIKE BUTTON LOCATION]")
        print(f"  Center: ({correct_button['center_x']}, {correct_button['center_y']})")
        print(f"  Bounding box: {correct_button['rect']}")
        print(f"\n[COMPARISON]")
        print(f"  UI-TARS clicked: ({pixel_x}, {pixel_y})")
        print(f"  Should click: ({correct_button['center_x']}, {correct_button['center_y']})")
        print(f"  Offset: ({pixel_x - correct_button['center_x']}, {pixel_y - correct_button['center_y']})")

        # Check if clicked coordinates are inside the button's bounding box
        rect = correct_button['rect']
        inside = (rect['left'] <= pixel_x <= rect['right'] and
                  rect['top'] <= pixel_y <= rect['bottom'])

        if inside:
            print(f"\n  ✓ Coordinates ARE inside Like button bounds")
        else:
            print(f"\n  ✗ Coordinates are OUTSIDE Like button bounds!")

    print("\n" + "="*80)

if __name__ == "__main__":
    asyncio.run(test_what_gets_clicked())
