"""
DOM Inspector - Find correct selectors for YouTube Studio buttons

This script connects to Chrome on port 9222 and inspects the actual
DOM structure to find working selectors with aria-pressed attributes.
"""
import sys
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(repo_root))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

print("\n" + "="*80)
print(" DOM INSPECTOR - YouTube Studio Comments")
print("="*80)

# Connect to existing Chrome
print("\n[1] Connecting to Chrome on port 9222...")
chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(options=chrome_options)
print(f"[OK] Connected to: {driver.current_url[:80]}...")

print("\n[2] Inspecting DOM structure...")
print("="*80)

# Inspect first comment thread
result = driver.execute_script("""
    const cards = document.querySelectorAll('ytcp-comment-thread');
    if (cards.length === 0) {
        return {error: 'No comment cards found'};
    }

    const firstCard = cards[0];

    // Find all buttons in first comment
    const buttons = firstCard.querySelectorAll('button');
    const buttonInfo = Array.from(buttons).map((btn, idx) => ({
        index: idx,
        aria_label: btn.getAttribute('aria-label'),
        aria_pressed: btn.getAttribute('aria-pressed'),
        id: btn.id,
        classes: Array.from(btn.classList).join(' '),
        text: btn.textContent.trim().substring(0, 50),
        has_aria_pressed: btn.hasAttribute('aria-pressed')
    }));

    return {
        total_cards: cards.length,
        buttons: buttonInfo,
        first_card_html: firstCard.outerHTML.substring(0, 500)
    };
""")

if 'error' in result:
    print(f"\n[ERROR] {result['error']}")
    print("\nMake sure you're on: https://studio.youtube.com/.../comments/inbox")
else:
    print(f"\n[OK] Found {result['total_cards']} comment cards")
    print(f"\n[BUTTONS IN FIRST COMMENT]")
    print("-"*80)

    for btn in result['buttons']:
        print(f"\nButton {btn['index']}:")
        print(f"  aria-label: {btn['aria_label']}")
        print(f"  aria-pressed: {btn['aria_pressed']}")
        print(f"  has aria-pressed: {btn['has_aria_pressed']}")
        print(f"  id: {btn['id']}")
        print(f"  classes: {btn['classes']}")
        print(f"  text: {btn['text']}")

print("\n" + "="*80)
print(" RECOMMENDED SELECTORS")
print("="*80)

# Test various selectors
selectors_to_test = [
    "ytcp-comment-thread:nth-child(1) button[aria-label*='Like']",
    "ytcp-comment-thread:first-child button[aria-label*='Like']",
    "ytcp-comment-thread button[aria-label*='Like this comment']",
    "ytcp-comment-thread #engagement-toolbar button[aria-label*='Like']",
    "ytcp-comment-thread ytcp-icon-button[aria-label*='Like']",
]

print("\nTesting selectors:")
for selector in selectors_to_test:
    try:
        element = driver.execute_script("""
            const el = document.querySelector(arguments[0]);
            if (!el) return null;
            return {
                found: true,
                aria_pressed: el.getAttribute('aria-pressed'),
                aria_label: el.getAttribute('aria-label')
            };
        """, selector)

        if element:
            print(f"\n✓ WORKS: {selector}")
            print(f"  aria-pressed: {element['aria_pressed']}")
            print(f"  aria-label: {element['aria_label']}")
        else:
            print(f"\n✗ FAILS: {selector}")
    except Exception as e:
        print(f"\n✗ ERROR: {selector} - {e}")

print("\n" + "="*80)
print(" DONE")
print("="*80)
print("\nUse the working selector in executor.py for DOM verification")
