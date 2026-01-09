"""
Check if we can read the Like count for deterministic verification
"""
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(repo_root))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(options=chrome_options)

print("\nChecking Like count on first comment...")

result = driver.execute_script("""
    const commentCard = document.querySelector('ytcp-comment-thread:first-child');
    if (!commentCard) return {error: 'Comment not found'};

    const likeBtn = commentCard.querySelector('ytcp-icon-button[aria-label="Like"]');
    if (!likeBtn) return {error: 'Like button not found'};

    // Check for like count display
    // YouTube shows like count next to the button
    const likeCountEl = likeBtn.querySelector('.ytcpIconButton__label, [class*="count"], [class*="label"]');

    // Also check parent/sibling elements
    const parent = likeBtn.parentElement;
    const allText = parent ? parent.textContent.trim() : '';

    return {
        found: true,
        aria_label: likeBtn.getAttribute('aria-label'),
        inner_text: likeBtn.innerText.trim(),
        text_content: likeBtn.textContent.trim(),
        parent_text: allText,
        like_count_element: likeCountEl ? {
            text: likeCountEl.textContent.trim(),
            class: likeCountEl.className
        } : null,
        // Get the displayed text next to Like button
        button_html: likeBtn.outerHTML.substring(0, 500)
    };
""")

if 'error' in result:
    print(f"ERROR: {result['error']}")
else:
    print(f"\nLike button info:")
    print(f"  aria-label: {result['aria_label']}")
    print(f"  innerText: '{result['inner_text']}'")
    print(f"  textContent: '{result['text_content']}'")
    print(f"  Parent text: '{result['parent_text']}'")

    if result['like_count_element']:
        print(f"\n  Like count element found:")
        print(f"    Text: '{result['like_count_element']['text']}'")
        print(f"    Class: {result['like_count_element']['class']}")
    else:
        print(f"\n  No dedicated like count element found")

    print(f"\n  Button HTML snippet:")
    print(f"    {result['button_html'][:300]}...")

# Check if count shows up in aria-label after clicking
print("\n\nChecking ALL Like buttons for patterns...")

all_likes = driver.execute_script("""
    const likeButtons = document.querySelectorAll('ytcp-icon-button[aria-label="Like"]');
    return Array.from(likeButtons).slice(0, 5).map(btn => ({
        aria_label: btn.getAttribute('aria-label'),
        text: btn.textContent.trim(),
        inner_text: btn.innerText.trim(),
        // Check if there's a number visible
        has_number: /\\d+/.test(btn.textContent)
    }));
""")

print("\nAll Like buttons:")
for i, btn in enumerate(all_likes):
    print(f"  [{i}] aria-label: {btn['aria_label']}, text: '{btn['text']}', has_number: {btn['has_number']}")

print("\n\nConclusion:")
print("If first button shows '1' in text, we can use textContent for verification")
print("If aria-label changes, we can use aria-label")
print("If neither changes, we rely on vision verification")
