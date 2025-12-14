"""
Record YouTube Studio interaction using Selenium + JavaScript event capture
"""
import sys
import time
import json
from pathlib import Path
from datetime import datetime

# Add repo root to path
repo_root = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(repo_root))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from modules.infrastructure.wardrobe_ide.src.skill import WardrobeSkill
from modules.infrastructure.wardrobe_ide.src.skills_store import save_skill

print("[RECORDER] YouTube Studio Skill Recorder (Selenium)")
print("=" * 80)

# Connect to existing Chrome on port 9222
print("[RECORDER] Connecting to Chrome on port 9222...")
chrome_options = ChromeOptions()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

try:
    driver = webdriver.Chrome(options=chrome_options)
    print(f"[RECORDER] Connected! Current URL: {driver.current_url}")
except Exception as e:
    print(f"[ERROR] Could not connect to Chrome: {e}")
    print("[ERROR] Make sure Chrome is running with --remote-debugging-port=9222")
    sys.exit(1)

# Navigate to YouTube Studio
studio_url = "https://studio.youtube.com/channel/UC-LSSlOZwpGIRIYihaz8zCw/comments/inbox"
if driver.current_url != studio_url:
    print(f"\n[RECORDER] Navigating to YouTube Studio...")
    driver.get(studio_url)
    time.sleep(3)  # Wait for page load
    print(f"[RECORDER] Navigated! URL: {driver.current_url}")

# Inject JavaScript event capture
print("\n[RECORDER] Injecting event capture JavaScript...")

event_capture_js = """
// Initialize event storage
window.__wardrobeSteps = [];
window.__startTime = Date.now();

// Helper function to generate CSS selector
function getSelector(element) {
    if (element.id) {
        return '#' + element.id;
    }

    // Try aria-label
    if (element.hasAttribute('aria-label')) {
        let label = element.getAttribute('aria-label');
        return `[aria-label="${label}"]`;
    }

    // Try data attributes
    for (let attr of element.attributes) {
        if (attr.name.startsWith('data-')) {
            return `[${attr.name}="${attr.value}"]`;
        }
    }

    // Fallback to tag + class
    let selector = element.tagName.toLowerCase();
    if (element.className && typeof element.className === 'string') {
        let classes = element.className.split(' ').filter(c => c.length > 0);
        if (classes.length > 0) {
            selector += '.' + classes.join('.');
        }
    }

    return selector;
}

// Capture clicks
document.addEventListener('click', (e) => {
    const selector = getSelector(e.target);
    const timestamp = (Date.now() - window.__startTime) / 1000;

    console.log('[WARDROBE] Click:', selector);

    window.__wardrobeSteps.push({
        action: 'click',
        selector: selector,
        timestamp: timestamp,
        target_tag: e.target.tagName,
        target_text: e.target.textContent?.substring(0, 50) || '',
        target_aria_label: e.target.getAttribute('aria-label') || ''
    });
}, true);

// Capture typing
document.addEventListener('input', (e) => {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
        const selector = getSelector(e.target);
        const timestamp = (Date.now() - window.__startTime) / 1000;

        console.log('[WARDROBE] Type:', selector, e.target.value);

        window.__wardrobeSteps.push({
            action: 'type',
            selector: selector,
            text: e.target.value,
            timestamp: timestamp
        });
    }
}, true);

console.log('[WARDROBE] Event capture initialized');
return true;
"""

try:
    result = driver.execute_script(event_capture_js)
    print("[RECORDER] Event capture active!")
except Exception as e:
    print(f"[ERROR] Failed to inject JavaScript: {e}")
    driver.quit()
    sys.exit(1)

# Record for 30 seconds
duration = 30
print(f"\n[RECORDER] Recording for {duration} seconds...")
print("[RECORDER] Perform your Like + Heart + Reply interaction NOW!")
print("[RECORDER] Timer started...")

for i in range(duration, 0, -5):
    print(f"[RECORDER] {i} seconds remaining...")
    time.sleep(5)

print("\n[RECORDER] Recording complete! Extracting steps...")

# Extract recorded steps
try:
    steps = driver.execute_script("return window.__wardrobeSteps;")
    print(f"[RECORDER] Captured {len(steps)} steps")

    # Print captured steps for verification
    print("\n[RECORDER] Captured Steps:")
    print("-" * 80)
    for i, step in enumerate(steps, 1):
        if step['action'] == 'click':
            print(f"  {i}. CLICK: {step['selector']}")
            if step.get('target_aria_label'):
                print(f"      aria-label: {step['target_aria_label']}")
            if step.get('target_text'):
                print(f"      text: {step['target_text'][:50]}")
        elif step['action'] == 'type':
            print(f"  {i}. TYPE: {step['selector']} = '{step['text']}'")
    print("-" * 80)

except Exception as e:
    print(f"[ERROR] Failed to extract steps: {e}")
    driver.quit()
    sys.exit(1)

# Create and save skill
print("\n[RECORDER] Creating Wardrobe skill...")

skill = WardrobeSkill(
    name="yt_like_heart_reply",
    backend="selenium",
    steps=steps,
    created_at=datetime.now(),
    meta={
        "target_url": driver.current_url,
        "tags": ["youtube", "studio", "engagement"],
        "notes": "Like + Heart + Reply interaction on YouTube Studio comments",
        "step_count": len(steps),
        "recorded_with": "selenium_javascript_capture"
    }
)

try:
    filepath = save_skill(skill)
    print(f"[RECORDER] Skill saved to: {filepath}")
    print(f"[RECORDER] Skill name: {skill.name}")
    print(f"[RECORDER] Steps captured: {len(steps)}")
    print("\n[SUCCESS] Recording complete!")
    print("\nNext step: Test replay with:")
    print("  python -m modules.infrastructure.wardrobe_ide replay --name yt_like_heart_reply")

except Exception as e:
    print(f"[ERROR] Failed to save skill: {e}")

print("\n[RECORDER] Disconnecting from Chrome (browser stays open)")
driver.quit()
