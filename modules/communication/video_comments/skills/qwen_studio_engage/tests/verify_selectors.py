"""
Verify Like/Heart/Reply selectors and aria-pressed attributes
"""
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(repo_root))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

print("\n" + "="*80)
print(" SELECTOR VERIFICATION - Like/Heart/Reply Buttons")
print("="*80)

chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(options=chrome_options)
print(f"[OK] Connected: {driver.current_url[:60]}...")

# Test selectors on FIRST comment
selectors = {
    "Like": "ytcp-comment-thread:first-child ytcp-icon-button[aria-label='Like']",
    "Heart": "ytcp-comment-thread:first-child ytcp-icon-button[aria-label='Heart']",
    "Reply": "ytcp-comment-thread:first-child button[aria-label='Reply']"
}

print("\n[TESTING SELECTORS ON FIRST COMMENT]")
print("="*80)

for action, selector in selectors.items():
    result = driver.execute_script("""
        const el = document.querySelector(arguments[0]);
        if (!el) return {found: false};

        // Get all attributes
        const attrs = {};
        for (let attr of el.attributes) {
            attrs[attr.name] = attr.value;
        }

        return {
            found: true,
            tagName: el.tagName,
            aria_label: el.getAttribute('aria-label'),
            aria_pressed: el.getAttribute('aria-pressed'),
            has_aria_pressed: el.hasAttribute('aria-pressed'),
            class: el.className,
            all_attributes: attrs
        };
    """, selector)

    print(f"\n[{action}]")
    if result['found']:
        print(f"  Selector: {selector}")
        print(f"  Tag: {result['tagName']}")
        print(f"  aria-label: {result['aria_label']}")
        print(f"  aria-pressed: {result['aria_pressed']}")
        print(f"  Has aria-pressed: {result['has_aria_pressed']}")

        # Show all attributes
        print("  All attributes:")
        for attr_name, attr_val in result['all_attributes'].items():
            if attr_name not in ['class', 'aria-label', 'aria-pressed']:
                print(f"    {attr_name}: {attr_val}")
    else:
        print(f"  NOT FOUND: {selector}")

# Count total Like/Heart/Reply buttons
print("\n" + "="*80)
print(" TOTAL COUNTS")
print("="*80)

counts = driver.execute_script("""
    return {
        like_buttons: document.querySelectorAll('ytcp-icon-button[aria-label="Like"]').length,
        heart_buttons: document.querySelectorAll('ytcp-icon-button[aria-label="Heart"]').length,
        reply_buttons: document.querySelectorAll('button[aria-label="Reply"]').length,
        total_comments: document.querySelectorAll('ytcp-comment-thread').length
    };
""")

print(f"\nTotal comment cards: {counts['total_comments']}")
print(f"Like buttons: {counts['like_buttons']}")
print(f"Heart buttons: {counts['heart_buttons']}")
print(f"Reply buttons: {counts['reply_buttons']}")

print("\n" + "="*80)
print(" DOM STATE VERIFICATION TEST")
print("="*80)

# Test if we can capture BEFORE/AFTER state
print("\nTesting state capture on Like button...")
state = driver.execute_script("""
    const el = document.querySelector('ytcp-comment-thread:first-child ytcp-icon-button[aria-label="Like"]');
    if (!el) return {error: 'Element not found'};

    return {
        aria_pressed: el.getAttribute('aria-pressed'),
        aria_label: el.getAttribute('aria-label'),
        // Check if button has any state indicator
        class_list: Array.from(el.classList),
        // Check for pressed/active state in parent or children
        parent_class: el.parentElement ? Array.from(el.parentElement.classList) : [],
        has_state: el.hasAttribute('aria-pressed') || el.hasAttribute('data-state') || el.hasAttribute('pressed')
    };
""")

if 'error' in state:
    print(f"ERROR: {state['error']}")
else:
    print(f"aria-pressed: {state['aria_pressed']}")
    print(f"aria-label: {state['aria_label']}")
    print(f"Classes: {state['class_list']}")
    print(f"Has state attribute: {state['has_state']}")

    if state['aria_pressed'] is not None:
        print("\n[OK] DOM verification available via aria-pressed")
    else:
        print("\n[WARNING] No aria-pressed - may need class-based verification")

print("\n" + "="*80)
print(" RECOMMENDED CONFIGURATION")
print("="*80)

print("\nUse these selectors in executor.py:")
print(f"  LIKE_SELECTOR = 'ytcp-comment-thread:nth-child({{idx}}) ytcp-icon-button[aria-label=\"Like\"]'")
print(f"  HEART_SELECTOR = 'ytcp-comment-thread:nth-child({{idx}}) ytcp-icon-button[aria-label=\"Heart\"]'")
print(f"  REPLY_SELECTOR = 'ytcp-comment-thread:nth-child({{idx}}) button[aria-label=\"Reply\"]'")

if state.get('aria_pressed') is not None:
    print(f"\n  DOM verification: aria-pressed (deterministic)")
else:
    print(f"\n  DOM verification: class-based (monitor class changes)")

print("\n" + "="*80)
print(" DONE")
print("="*80)
