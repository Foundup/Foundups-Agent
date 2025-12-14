"""
Test: Click Like button and detect DOM state changes

This will show us what changes in the DOM when a Like button is clicked,
so we know what to use for deterministic verification.
"""
import asyncio
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(repo_root))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from modules.infrastructure.foundups_vision.src.ui_tars_bridge import UITarsBridge

async def test_click_and_detect_change():
    print("\n" + "="*80)
    print(" CLICK STATE CHANGE TEST")
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

    # Capture BEFORE state
    print("\n[3] Capturing BEFORE state...")
    selector = "ytcp-comment-thread:first-child ytcp-icon-button[aria-label='Like']"

    before_state = driver.execute_script("""
        const el = document.querySelector(arguments[0]);
        if (!el) return {error: 'Element not found'};

        // Capture everything that might change
        return {
            // Attributes
            aria_disabled: el.getAttribute('aria-disabled'),
            aria_pressed: el.getAttribute('aria-pressed'),
            aria_label: el.getAttribute('aria-label'),
            compact: el.getAttribute('compact'),
            role: el.getAttribute('role'),

            // Classes
            class_list: Array.from(el.classList),

            // Computed style
            color: window.getComputedStyle(el).color,
            background_color: window.getComputedStyle(el).backgroundColor,

            // Inner elements (icon might change)
            inner_html_length: el.innerHTML.length,
            inner_text: el.innerText,

            // Check icon element
            icon: el.querySelector('yt-icon') ? {
                class: Array.from(el.querySelector('yt-icon').classList),
                icon_name: el.querySelector('yt-icon').className
            } : null
        };
    """, selector)

    if 'error' in before_state:
        print(f"[ERROR] {before_state['error']}")
        return

    print("[OK] BEFORE state captured:")
    print(f"  aria-disabled: {before_state['aria_disabled']}")
    print(f"  aria-pressed: {before_state['aria_pressed']}")
    print(f"  Classes: {before_state['class_list']}")
    print(f"  Color: {before_state['color']}")
    print(f"  Icon: {before_state['icon']}")

    # CLICK via UI-TARS Vision
    print("\n[4] Clicking Like button via UI-TARS Vision...")
    click_result = await bridge.click(
        "gray thumbs up Like button in the action bar on the first comment",
        driver=driver
    )

    if click_result.success:
        print(f"[OK] Click succeeded (confidence: {click_result.confidence:.2f})")
        if click_result.metadata:
            print(f"  Metadata: {click_result.metadata}")
    else:
        print(f"[ERROR] Click failed")
        if click_result.error:
            print(f"  Error: {click_result.error}")
        return

    # Wait for UI update
    await asyncio.sleep(2)

    # Capture AFTER state
    print("\n[5] Capturing AFTER state...")
    after_state = driver.execute_script("""
        const el = document.querySelector(arguments[0]);
        if (!el) return {error: 'Element not found'};

        return {
            aria_disabled: el.getAttribute('aria-disabled'),
            aria_pressed: el.getAttribute('aria-pressed'),
            aria_label: el.getAttribute('aria-label'),
            compact: el.getAttribute('compact'),
            role: el.getAttribute('role'),
            class_list: Array.from(el.classList),
            color: window.getComputedStyle(el).color,
            background_color: window.getComputedStyle(el).backgroundColor,
            inner_html_length: el.innerHTML.length,
            inner_text: el.innerText,
            icon: el.querySelector('yt-icon') ? {
                class: Array.from(el.querySelector('yt-icon').classList),
                icon_name: el.querySelector('yt-icon').className
            } : null
        };
    """, selector)

    print("[OK] AFTER state captured:")
    print(f"  aria-disabled: {after_state['aria_disabled']}")
    print(f"  aria-pressed: {after_state['aria_pressed']}")
    print(f"  Classes: {after_state['class_list']}")
    print(f"  Color: {after_state['color']}")
    print(f"  Icon: {after_state['icon']}")

    # COMPARE and show what changed
    print("\n" + "="*80)
    print(" WHAT CHANGED")
    print("="*80)

    changes = []

    if before_state['aria_disabled'] != after_state['aria_disabled']:
        changes.append(f"aria-disabled: {before_state['aria_disabled']} → {after_state['aria_disabled']}")

    if before_state['aria_pressed'] != after_state['aria_pressed']:
        changes.append(f"aria-pressed: {before_state['aria_pressed']} → {after_state['aria_pressed']}")

    if before_state['aria_label'] != after_state['aria_label']:
        changes.append(f"aria-label: {before_state['aria_label']} → {after_state['aria_label']}")

    if before_state['class_list'] != after_state['class_list']:
        changes.append(f"Classes: {before_state['class_list']} → {after_state['class_list']}")

    if before_state['color'] != after_state['color']:
        changes.append(f"Color: {before_state['color']} → {after_state['color']}")

    if before_state['inner_html_length'] != after_state['inner_html_length']:
        changes.append(f"innerHTML length: {before_state['inner_html_length']} → {after_state['inner_html_length']}")

    if before_state['icon'] != after_state['icon']:
        changes.append(f"Icon: {before_state['icon']} → {after_state['icon']}")

    if changes:
        print("\nDetected changes:")
        for change in changes:
            print(f"  ✓ {change}")
    else:
        print("\n[WARNING] NO CHANGES DETECTED - Click may not have worked!")

    # Visual verification via TARS
    print("\n[6] Visual verification via UI-TARS...")
    verify_result = await bridge.verify(
        "blue highlighted thumbs up Like button",
        driver=driver
    )

    print(f"Vision says: {verify_result.success} (confidence: {verify_result.confidence:.2f})")
    if verify_result.metadata:
        print(f"Metadata: {verify_result.metadata}")

    print("\n" + "="*80)
    print(" CONCLUSION")
    print("="*80)

    if changes:
        print("\n✓ DOM state changes detected - can use for verification")
        print("\nRecommended DOM verification:")
        for change in changes[:3]:  # Show top 3 changes
            print(f"  • {change}")
    else:
        print("\n✗ No DOM changes - vision-only verification required")
        print("OR: Click didn't work - coordinates may be wrong")

    print("\n" + "="*80)

if __name__ == "__main__":
    asyncio.run(test_click_and_detect_change())
