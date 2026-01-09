"""
Test: Direct Selenium click without vision coordinates

Instead of using UI-TARS to find coordinates, use Selenium's querySelector
to find the button and click it directly. Then verify visually.
"""
import asyncio
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(repo_root))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from modules.infrastructure.foundups_vision.src.ui_tars_bridge import UITarsBridge

async def test_direct_selenium_click():
    print("\n" + "="*80)
    print(" DIRECT SELENIUM CLICK TEST")
    print("="*80)

    # Connect to browser
    print("\n[1] Connecting to Chrome...")
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=chrome_options)
    print(f"[OK] Connected: {driver.current_url[:60]}...")

    # Capture BEFORE state
    print("\n[2] Capturing BEFORE state...")
    selector = "ytcp-comment-thread:first-child ytcp-icon-button[aria-label='Like']"

    before_state = driver.execute_script("""
        const el = document.querySelector(arguments[0]);
        if (!el) return {error: 'Element not found'};

        return {
            aria_disabled: el.getAttribute('aria-disabled'),
            aria_label: el.getAttribute('aria-label'),
            class_list: Array.from(el.classList),
            // Check for any state indicators
            parent_class: el.parentElement ? Array.from(el.parentElement.classList) : []
        };
    """, selector)

    if 'error' in before_state:
        print(f"[ERROR] {before_state['error']}")
        return

    print(f"[OK] BEFORE state:")
    print(f"  aria-disabled: {before_state['aria_disabled']}")
    print(f"  Classes: {before_state['class_list']}")

    # CLICK via Selenium (direct)
    print("\n[3] Clicking via Selenium .click()...")

    try:
        click_success = driver.execute_script("""
            const el = document.querySelector(arguments[0]);
            if (!el) return {success: false, error: 'Element not found'};

            el.click();
            return {success: true};
        """, selector)

        if click_success.get('success'):
            print(f"[OK] Selenium click executed")
        else:
            print(f"[ERROR] {click_success.get('error')}")
            return
    except Exception as e:
        print(f"[ERROR] Click failed: {e}")
        return

    # Wait for UI update
    await asyncio.sleep(2)

    # Capture AFTER state
    print("\n[4] Capturing AFTER state...")
    after_state = driver.execute_script("""
        const el = document.querySelector(arguments[0]);
        if (!el) return {error: 'Element not found'};

        return {
            aria_disabled: el.getAttribute('aria-disabled'),
            aria_label: el.getAttribute('aria-label'),
            class_list: Array.from(el.classList),
            parent_class: el.parentElement ? Array.from(el.parentElement.classList) : []
        };
    """, selector)

    print(f"[OK] AFTER state:")
    print(f"  aria-disabled: {after_state['aria_disabled']}")
    print(f"  Classes: {after_state['class_list']}")

    # Compare
    print("\n[5] Comparing states...")
    if before_state['class_list'] != after_state['class_list']:
        print(f"  Classes changed:")
        print(f"    BEFORE: {before_state['class_list']}")
        print(f"    AFTER:  {after_state['class_list']}")
        dom_verified = True
    else:
        print(f"  No class changes detected")
        dom_verified = False

    # Visual verification
    print("\n[6] Visual verification via UI-TARS...")
    bridge = UITarsBridge(browser_port=9222)
    await bridge.connect()

    verify_result = await bridge.verify(
        "blue highlighted thumbs up Like button on the first comment",
        driver=driver
    )

    print(f"  Vision: {verify_result.success} (confidence: {verify_result.confidence:.2f})")

    # Take screenshot for manual verification
    print("\n[7] Taking screenshot for manual verification...")
    screenshot_path = Path(__file__).parent / "after_direct_click.png"
    driver.save_screenshot(str(screenshot_path))
    print(f"  Saved to: {screenshot_path}")

    # Conclusion
    print("\n" + "="*80)
    print(" CONCLUSION")
    print("="*80)

    if dom_verified:
        print("\n  DOM state changed - Selenium click likely worked")
    elif verify_result.success and verify_result.confidence >= 0.7:
        print("\n  Vision verification passed - Like button appears blue")
    else:
        print("\n  NO verification - Click may not have worked")
        print("  Check the screenshot manually")

    print("\n  Screenshot path: " + str(screenshot_path))

if __name__ == "__main__":
    asyncio.run(test_direct_selenium_click())
