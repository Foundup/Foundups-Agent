"""
Interactive browser recording with on-screen START/STOP widget
"""
import sys
import time
import json
from pathlib import Path
from datetime import datetime
import io

# Force UTF-8 encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

repo_root = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(repo_root))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from modules.infrastructure.wardrobe_ide.src.skill import WardrobeSkill
from modules.infrastructure.wardrobe_ide.src.skills_store import save_skill

print("[WARDROBE] Interactive Recording Widget")
print("=" * 80)

# Connect to existing Chrome
print("[WARDROBE] Connecting to Chrome on port 9222...")
chrome_options = ChromeOptions()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

try:
    driver = webdriver.Chrome(options=chrome_options)
    print(f"[WARDROBE] Connected! URL: {driver.current_url}")
except Exception as e:
    print(f"[ERROR] Could not connect: {e}")
    sys.exit(1)

# Navigate to YouTube Studio if needed
studio_url = "https://studio.youtube.com/channel/UC-LSSlOZwpGIRIYihaz8zCw/comments/inbox"
if "studio.youtube.com" not in driver.current_url:
    print(f"[WARDROBE] Navigating to YouTube Studio...")
    driver.get(studio_url)
    time.sleep(3)

# Inject recording widget + event capture
print("[WARDROBE] Injecting recording widget...")

widget_js = """
// Initialize
window.__wardrobeSteps = [];
window.__wardrobeRecording = false;
window.__wardrobeStartTime = null;

// Create widget UI
const widget = document.createElement('div');
widget.id = 'wardrobe-widget';
widget.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 2147483647;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    min-width: 250px;
    pointer-events: auto;
`;

// Create title
const title = document.createElement('div');
title.style.cssText = 'font-size: 16px; font-weight: bold; margin-bottom: 12px;';
title.textContent = 'WARDROBE RECORDER';
widget.appendChild(title);

// Create status
const status = document.createElement('div');
status.id = 'wardrobe-status';
status.style.cssText = 'font-size: 14px; margin-bottom: 12px; opacity: 0.9;';
status.textContent = 'Ready to record';
widget.appendChild(status);

// Create START button
const startBtn = document.createElement('button');
startBtn.id = 'wardrobe-start';
startBtn.style.cssText = 'width: 100%; padding: 12px; background: #48bb78; color: white; border: none; border-radius: 6px; font-size: 14px; font-weight: bold; cursor: pointer; margin-bottom: 8px; pointer-events: auto;';
startBtn.textContent = '> START RECORDING';
startBtn.onclick = function() {
    window.__wardrobeRecording = true;
    window.__wardrobeStartTime = Date.now();
    window.__wardrobeSteps = [];

    const status = document.getElementById('wardrobe-status');
    status.textContent = '[REC] RECORDING...';
    status.style.cssText += ' animation: pulse 1s infinite;';

    document.getElementById('wardrobe-start').style.display = 'none';
    document.getElementById('wardrobe-stop').style.display = 'block';
    document.getElementById('wardrobe-counter').style.display = 'block';
    document.getElementById('step-count').textContent = '0';

    // Change widget background to red
    document.getElementById('wardrobe-widget').style.background = 'linear-gradient(135deg, #fc5c7d 0%, #6a82fb 100%)';

    console.log('[WARDROBE] Recording started');
};
widget.appendChild(startBtn);

// Create STOP button
const stopBtn = document.createElement('button');
stopBtn.id = 'wardrobe-stop';
stopBtn.style.cssText = 'width: 100%; padding: 12px; background: #f56565; color: white; border: none; border-radius: 6px; font-size: 14px; font-weight: bold; cursor: pointer; display: none; pointer-events: auto;';
stopBtn.textContent = '[X] STOP & SAVE';
stopBtn.onclick = function() {
    window.__wardrobeRecording = false;

    document.getElementById('wardrobe-status').textContent = `[OK] Saved ${window.__wardrobeSteps.length} steps`;
    document.getElementById('wardrobe-stop').style.display = 'none';

    // Change widget background back to purple
    document.getElementById('wardrobe-widget').style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';

    console.log('[WARDROBE] Recording stopped. Steps:', window.__wardrobeSteps.length);
};
widget.appendChild(stopBtn);

// Create counter
const counter = document.createElement('div');
counter.id = 'wardrobe-counter';
counter.style.cssText = 'font-size: 12px; margin-top: 8px; opacity: 0.8; display: none;';
const counterText = document.createTextNode('Steps: ');
const stepCount = document.createElement('span');
stepCount.id = 'step-count';
stepCount.textContent = '0';
counter.appendChild(counterText);
counter.appendChild(stepCount);
widget.appendChild(counter);

document.body.appendChild(widget);

// Add CSS animation for pulse
const style = document.createElement('style');
style.textContent = `
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}
`;
document.head.appendChild(style);

// Helper function to generate selector
function getSelector(element) {
    if (element.id) {
        return '#' + element.id;
    }

    if (element.hasAttribute('aria-label')) {
        let label = element.getAttribute('aria-label');
        return `[aria-label="${label}"]`;
    }

    for (let attr of element.attributes) {
        if (attr.name.startsWith('data-')) {
            return `[${attr.name}="${attr.value}"]`;
        }
    }

    let selector = element.tagName.toLowerCase();
    if (element.className && typeof element.className === 'string') {
        let classes = element.className.split(' ').filter(c => c && c.length > 0);
        if (classes.length > 0 && classes.length <= 3) {
            selector += '.' + classes.slice(0, 3).join('.');
        }
    }

    return selector;
}

// Event capture
document.addEventListener('click', (e) => {
    if (!window.__wardrobeRecording) return;
    if (e.target.closest('#wardrobe-widget')) return; // Ignore widget clicks

    const selector = getSelector(e.target);
    const timestamp = (Date.now() - window.__wardrobeStartTime) / 1000;

    window.__wardrobeSteps.push({
        action: 'click',
        selector: selector,
        timestamp: timestamp,
        target_tag: e.target.tagName,
        target_text: e.target.textContent?.substring(0, 50) || '',
        target_aria_label: e.target.getAttribute('aria-label') || ''
    });

    document.getElementById('step-count').textContent = window.__wardrobeSteps.length;
    console.log('[WARDROBE] Captured click:', selector);
}, true);

document.addEventListener('input', (e) => {
    if (!window.__wardrobeRecording) return;
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
        const selector = getSelector(e.target);
        const timestamp = (Date.now() - window.__wardrobeStartTime) / 1000;

        window.__wardrobeSteps.push({
            action: 'type',
            selector: selector,
            text: e.target.value,
            timestamp: timestamp
        });

        document.getElementById('step-count').textContent = window.__wardrobeSteps.length;
        console.log('[WARDROBE] Captured input:', selector);
    }
}, true);

console.log('[WARDROBE] Widget ready! Click START RECORDING to begin.');
return true;
"""

try:
    driver.execute_script(widget_js)
    print("[WARDROBE] ✓ Widget injected successfully!")
except Exception as e:
    print(f"[ERROR] Failed to inject widget: {e}")
    driver.quit()
    sys.exit(1)

print("\n" + "=" * 80)
print("INSTRUCTIONS FOR 012:")
print("=" * 80)
print("1. Look at the browser - you should see a purple 'Wardrobe Recorder' widget")
print("   in the top-right corner")
print("2. Click 'START RECORDING' button")
print("3. Perform your Like + Heart + Reply actions")
print("4. Click 'STOP & SAVE' button when done")
print("5. Press Enter in this terminal to save the skill")
print("=" * 80)

input("\n[WARDROBE] Press Enter after you click STOP in the browser...")

# Extract recorded steps
print("\n[WARDROBE] Extracting recorded steps...")
try:
    steps = driver.execute_script("return window.__wardrobeSteps;")
    print(f"[WARDROBE] Captured {len(steps)} steps")

    if len(steps) == 0:
        print("[WARNING] No steps recorded! Did you click START/STOP?")
        driver.quit()
        sys.exit(0)

    # Display captured steps
    print("\n[WARDROBE] Captured Steps:")
    print("-" * 80)
    for i, step in enumerate(steps, 1):
        if step['action'] == 'click':
            print(f"  {i}. CLICK: {step['selector']}")
            if step.get('target_aria_label'):
                print(f"      aria-label: {step['target_aria_label']}")
        elif step['action'] == 'type':
            print(f"  {i}. TYPE: {step['selector']} = '{step['text']}'")
    print("-" * 80)

    # Save skill
    current_url = driver.execute_script("return window.location.href;")
    skill = WardrobeSkill(
        name="yt_like_heart_reply",
        backend="selenium",
        steps=steps,
        created_at=datetime.now(),
        meta={
            "target_url": current_url,
            "tags": ["youtube", "studio", "engagement"],
            "notes": "Recorded by 012 using Wardrobe widget",
            "step_count": len(steps),
            "recorded_with": "wardrobe_widget"
        }
    )

    filepath = save_skill(skill)
    print(f"\n[SUCCESS] Skill saved to: {filepath}")
    print(f"[SUCCESS] Skill name: {skill.name}")
    print(f"[SUCCESS] Steps: {len(steps)}")

    print("\nNext: Test replay with:")
    print("  python -m modules.infrastructure.wardrobe_ide replay --name yt_like_heart_reply")

except Exception as e:
    print(f"[ERROR] Failed to extract steps: {e}")

print("\n[WARDROBE] Disconnecting (Chrome stays open)")
driver.quit()
