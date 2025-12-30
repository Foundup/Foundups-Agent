#!/usr/bin/env python3
"""
Author Name Extraction DOM Diagnostics
======================================

Connects to Chrome and inspects YouTube Studio comment DOM structure
to identify the correct selectors for author name extraction.

Usage:
    python scripts/diagnose_author_name_selectors.py
"""

import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def connect_to_chrome():
    """Connect to existing Chrome debug instance."""
    port = int(os.getenv("FOUNDUPS_CHROME_PORT", "9222"))
    opts = Options()
    opts.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")

    try:
        driver = webdriver.Chrome(options=opts)
        print(f"[OK] Connected to Chrome on port {port}")
        print(f"Current URL: {driver.current_url[:80]}...")
        return driver
    except Exception as e:
        print(f"[ERROR] Failed to connect to Chrome: {e}")
        print(f"Make sure Chrome is running with --remote-debugging-port={port}")
        return None

def inspect_comment_dom(driver):
    """Inspect the DOM structure of YouTube Studio comments."""

    print("\n" + "="*80)
    print(" INSPECTING COMMENT DOM STRUCTURE")
    print("="*80)

    # Check current page
    current_url = driver.current_url
    if "studio.youtube.com" not in current_url:
        print("⚠️ Not on YouTube Studio page!")
        print(f"   Current URL: {current_url}")
        print("   Please navigate to: https://studio.youtube.com/channel/YOUR_CHANNEL/comments/inbox")
        return

    # Try multiple selector strategies
    selectors_to_test = [
        # Comment thread container
        ("ytcp-comment-thread", "Comment thread container"),
        ("ytcp-comment-renderer", "Comment renderer"),

        # Author name attempts (current selectors)
        ("#author-text", "Author text by ID"),
        ("yt-formatted-string.author-text", "Formatted string with author-text class"),
        ("a#name", "Link with name ID"),
        (".author-name", "Author name class"),
        ("a[href*='/channel/']", "Channel link"),
        ("a[href^='/@']", "Handle link"),

        # Alternative selectors (new attempts)
        ("ytcp-comment-thread a[href^='/@']", "Thread > Handle link"),
        ("ytcp-comment-thread a[href*='/channel/']", "Thread > Channel link"),
        ("#author-name", "Author name by ID"),
        ("[id*='author']", "Any element with 'author' in ID"),
        ("[class*='author']", "Any element with 'author' in class"),
        ("ytcp-comment-thread a", "Any link in thread"),
    ]

    print("\n🔍 Testing DOM selectors...\n")

    results = {}

    for selector, description in selectors_to_test:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            count = len(elements)
            results[selector] = count

            if count > 0:
                print(f"✅ {description:50} | Found: {count:3} elements")

                # Show first element details
                first = elements[0]
                try:
                    text = first.text[:50] if first.text else "(no text)"
                    print(f"   └─> First element text: '{text}'")

                    # Show href if it's a link
                    if first.tag_name == 'a':
                        href = first.get_attribute('href') or ""
                        print(f"   └─> href: {href[:60]}")
                except:
                    pass
            else:
                print(f"❌ {description:50} | Found: 0 elements")
        except Exception as e:
            print(f"⚠️ {description:50} | Error: {e}")

    # JavaScript deep inspection
    print("\n" + "="*80)
    print(" JAVASCRIPT DOM INSPECTION (First Comment Thread)")
    print("="*80)

    js_inspection = """
    const threads = document.querySelectorAll('ytcp-comment-thread');
    if (threads.length === 0) {
        return {error: "No comment threads found"};
    }

    const thread = threads[0];

    // Find all links in the thread
    const links = thread.querySelectorAll('a');
    const linkData = Array.from(links).map(link => ({
        text: link.textContent.trim(),
        href: link.href,
        id: link.id,
        className: link.className
    }));

    // Find all elements with text content
    const allElements = thread.querySelectorAll('*');
    const elementsWithText = Array.from(allElements)
        .filter(el => el.textContent && el.textContent.trim().length > 0 && el.children.length === 0)
        .map(el => ({
            tag: el.tagName,
            id: el.id,
            className: el.className,
            text: el.textContent.trim().substring(0, 50)
        }))
        .slice(0, 20);  // First 20 only

    return {
        threadHTML: thread.innerHTML.substring(0, 500),
        links: linkData.slice(0, 10),  // First 10 links
        elementsWithText: elementsWithText
    };
    """

    try:
        result = driver.execute_script(js_inspection)

        if 'error' in result:
            print(f"\n❌ {result['error']}")
            print("   Make sure you're on the YouTube Studio Comments page with visible comments")
        else:
            print("\n📝 Links found in first comment thread:")
            for i, link in enumerate(result.get('links', []), 1):
                print(f"\n   Link #{i}:")
                print(f"      Text: {link['text'][:50]}")
                print(f"      Href: {link['href'][:60]}")
                if link['id']:
                    print(f"      ID: {link['id']}")
                if link['className']:
                    print(f"      Class: {link['className']}")

            print("\n📝 Elements with text in first comment thread:")
            for i, el in enumerate(result.get('elementsWithText', []), 1):
                print(f"\n   Element #{i}:")
                print(f"      Tag: {el['tag']}")
                print(f"      Text: '{el['text']}'")
                if el['id']:
                    print(f"      ID: {el['id']}")
                if el['className']:
                    print(f"      Class: {el['className'][:60]}")

            print("\n📝 Thread HTML (first 500 chars):")
            print(result.get('threadHTML', '')[:500])

    except Exception as e:
        print(f"\n❌ JavaScript inspection failed: {e}")

    # Recommendations
    print("\n" + "="*80)
    print(" RECOMMENDATIONS")
    print("="*80)

    successful_selectors = [sel for sel, count in results.items() if count > 0]

    if successful_selectors:
        print("\n✅ Working selectors found:")
        for sel in successful_selectors[:5]:
            print(f"   - {sel}")

        print("\n💡 Update comment_engagement_dae.py line 522 with working selectors")
    else:
        print("\n⚠️ No selectors found author elements!")
        print("   Possible issues:")
        print("   1. Not on YouTube Studio comments page")
        print("   2. No comments visible")
        print("   3. YouTube changed DOM structure significantly")
        print("   4. Page not fully loaded")

    print("\n" + "="*80)

def main():
    driver = connect_to_chrome()

    if not driver:
        print("\n💡 Start Chrome with debugging:")
        print('   "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --remote-debugging-port=9222')
        sys.exit(1)

    try:
        inspect_comment_dom(driver)

        print("\n✅ Diagnostics complete!")
        print("   Check output above for working selectors")

    except Exception as e:
        print(f"\n❌ Error during inspection: {e}")
        import traceback
        traceback.print_exc()

    # Don't close driver (keep connection for manual inspection)

if __name__ == "__main__":
    main()
