"""
Comprehensive DOM Inspector - Find Like/Heart buttons in YouTube Studio

Previous inspection found zero Like/Heart buttons, but user's screenshot
clearly shows they exist. This script examines the FULL DOM structure
without assumptions about aria-labels.
"""
import sys
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(repo_root))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

print("\n" + "="*80)
print(" COMPREHENSIVE DOM INSPECTOR - YouTube Studio Comments")
print("="*80)

# Connect to existing Chrome
print("\n[1] Connecting to Chrome on port 9222...")
chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(options=chrome_options)
print(f"[OK] Connected to: {driver.current_url[:80]}...")

print("\n[2] Examining FULL comment card structure...")
print("="*80)

# Get comprehensive structure of first comment card
result = driver.execute_script("""
    const cards = document.querySelectorAll('ytcp-comment-thread');
    if (cards.length === 0) {
        return {error: 'No comment cards found'};
    }

    const firstCard = cards[0];

    // Get ALL interactive elements (not just buttons)
    const allClickable = firstCard.querySelectorAll('button, [role="button"], ytcp-icon-button, a, [onclick]');

    const elementInfo = Array.from(allClickable).map((el, idx) => {
        // Get all attributes
        const attrs = {};
        for (let attr of el.attributes) {
            attrs[attr.name] = attr.value;
        }

        // Get computed styles
        const style = window.getComputedStyle(el);

        return {
            index: idx,
            tagName: el.tagName,
            id: el.id,
            className: el.className,
            attributes: attrs,
            text: el.textContent.trim().substring(0, 100),
            innerHTML: el.innerHTML.substring(0, 200),
            display: style.display,
            visibility: style.visibility,
            cursor: style.cursor,
            hasChildren: el.children.length > 0,
            childCount: el.children.length
        };
    });

    // Also get the raw HTML of engagement toolbar area
    const toolbar = firstCard.querySelector('#engagement-toolbar, [id*="toolbar"], [class*="toolbar"], [class*="action"]');

    return {
        total_cards: cards.length,
        clickable_elements: elementInfo,
        toolbar_html: toolbar ? toolbar.outerHTML.substring(0, 1000) : 'Not found',
        first_card_snippet: firstCard.outerHTML.substring(0, 500)
    };
""")

if 'error' in result:
    print(f"\n[ERROR] {result['error']}")
    print("\nMake sure you're on: https://studio.youtube.com/.../comments/inbox")
else:
    print(f"\n[OK] Found {result['total_cards']} comment cards")
    print(f"\n[CLICKABLE ELEMENTS IN FIRST COMMENT]")
    print("-"*80)

    for el in result['clickable_elements']:
        print(f"\n[{el['index']}] {el['tagName']}")
        print(f"  ID: {el['id']}")
        print(f"  Class: {el['className']}")
        print(f"  Text: {el['text']}")
        print(f"  Display: {el['display']}, Visibility: {el['visibility']}, Cursor: {el['cursor']}")
        print(f"  Children: {el['childCount']}")

        # Show key attributes
        if 'aria-label' in el['attributes']:
            print(f"  aria-label: {el['attributes']['aria-label']}")
        if 'aria-pressed' in el['attributes']:
            print(f"  aria-pressed: {el['attributes']['aria-pressed']}")
        if 'title' in el['attributes']:
            print(f"  title: {el['attributes']['title']}")
        if 'data-tooltip' in el['attributes']:
            print(f"  data-tooltip: {el['attributes']['data-tooltip']}")

        # Show innerHTML snippet if it contains SVG or icon
        if 'svg' in el['innerHTML'].lower() or 'icon' in el['innerHTML'].lower():
            print(f"  innerHTML (icon?): {el['innerHTML'][:100]}...")

    print("\n" + "="*80)
    print(" ENGAGEMENT TOOLBAR HTML")
    print("="*80)
    print(result['toolbar_html'])

    print("\n" + "="*80)
    print(" FIRST CARD HTML SNIPPET")
    print("="*80)
    print(result['first_card_snippet'])

print("\n" + "="*80)
print(" TESTING SPECIFIC SELECTORS")
print("="*80)

# Test various selectors that might match Like/Heart based on structure
selectors_to_test = [
    # Icon button selectors
    "ytcp-comment-thread ytcp-icon-button",
    "ytcp-comment-thread [role='button']",

    # Toolbar selectors
    "ytcp-comment-thread #engagement-toolbar button",
    "ytcp-comment-thread #engagement-toolbar ytcp-icon-button",

    # SVG/icon selectors
    "ytcp-comment-thread button svg",
    "ytcp-comment-thread ytcp-icon-button svg",

    # Class-based selectors
    "ytcp-comment-thread [class*='like']",
    "ytcp-comment-thread [class*='heart']",
    "ytcp-comment-thread [class*='favorite']",

    # Data attribute selectors
    "ytcp-comment-thread [data-tooltip*='Like']",
    "ytcp-comment-thread [data-tooltip*='Heart']",
]

print("\nTesting selectors:")
for selector in selectors_to_test:
    try:
        elements = driver.execute_script("""
            const elements = document.querySelectorAll(arguments[0]);
            if (elements.length === 0) return null;

            return Array.from(elements).slice(0, 3).map(el => ({
                tagName: el.tagName,
                aria_label: el.getAttribute('aria-label'),
                aria_pressed: el.getAttribute('aria-pressed'),
                title: el.getAttribute('title'),
                text: el.textContent.trim().substring(0, 50),
                hasAriaPressed: el.hasAttribute('aria-pressed')
            }));
        """, selector)

        if elements:
            print(f"\n✓ FOUND {len(elements)}: {selector}")
            for i, el in enumerate(elements):
                print(f"  [{i}] {el['tagName']}: {el.get('aria_label') or el.get('title') or el.get('text') or 'No label'}")
                if el['hasAriaPressed']:
                    print(f"      aria-pressed: {el['aria_pressed']}")
        else:
            print(f"\n✗ NONE: {selector}")
    except Exception as e:
        print(f"\n✗ ERROR: {selector} - {e}")

print("\n" + "="*80)
print(" DONE")
print("="*80)
print("\nIf Like/Heart buttons found, note their selector and aria-pressed attribute.")
