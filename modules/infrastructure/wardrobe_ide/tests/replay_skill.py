"""
Replay a recorded Wardrobe skill on existing Chrome session
"""
import sys
import time
import json
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(repo_root))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

print("[REPLAY] Wardrobe Skill Replay Test")
print("=" * 80)

# Connect to existing Chrome on port 9222
print("[REPLAY] Connecting to Chrome on port 9222...")
chrome_options = ChromeOptions()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

try:
    driver = webdriver.Chrome(options=chrome_options)
    print(f"[REPLAY] Connected! Current URL: {driver.current_url}")
except Exception as e:
    print(f"[ERROR] Could not connect to Chrome: {e}")
    print("[ERROR] Make sure Chrome is running with --remote-debugging-port=9222")
    sys.exit(1)

# Load skill file
skill_path = input("\n[REPLAY] Enter path to skill JSON file:\n> ").strip().strip('"')
skill_path = Path(skill_path)

if not skill_path.exists():
    print(f"[ERROR] Skill file not found: {skill_path}")
    driver.quit()
    sys.exit(1)

with open(skill_path) as f:
    skill = json.load(f)

print(f"\n[REPLAY] Loaded skill: {skill['name']}")
print(f"[REPLAY] Steps: {len(skill['steps'])}")
print(f"[REPLAY] Target URL: {skill['meta']['target_url']}")

# Navigate to target URL if needed
current_url = driver.current_url
target_url = skill['meta']['target_url']

# Remove query parameters for comparison
current_base = current_url.split('?')[0]
target_base = target_url.split('?')[0]

if current_base != target_base:
    print(f"\n[REPLAY] Navigating to target URL...")
    driver.get(target_url)
    time.sleep(3)  # Wait for page load
    print(f"[REPLAY] Navigated! URL: {driver.current_url}")

# Replay steps
print(f"\n[REPLAY] Starting replay...")
wait = WebDriverWait(driver, 30)  # Increased timeout for YouTube Studio loading

for i, step in enumerate(skill['steps'], 1):
    action = step['action']
    selector = step['selector']

    print(f"\n[REPLAY] Step {i}/{len(skill['steps'])}: {action} {selector}")

    try:
        if action == 'click':
            # Try CSS selector
            try:
                element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                element.click()
                print(f"[REPLAY]   OK Clicked: {selector}")
            except Exception as e1:
                # Fallback: Extract aria-label value for XPath
                try:
                    import re
                    # Extract aria-label value from button[aria-label='VALUE']
                    if 'aria-label=' in selector:
                        match = re.search(r'aria-label=[\'"]([^\'"]+)[\'"]', selector)
                        if match:
                            aria_value = match.group(1)
                            element = wait.until(EC.element_to_be_clickable((By.XPATH, f"//*[@aria-label='{aria_value}']")))
                            element.click()
                            print(f"[REPLAY]   OK Clicked (XPath): {aria_value}")
                        else:
                            raise Exception("Could not extract aria-label value")
                    else:
                        raise Exception("No aria-label in selector")
                except Exception as e2:
                    print(f"[REPLAY]   FAILED to click: {str(e1)[:150]}")
                    continue

        elif action == 'type':
            text = step['text']
            try:
                element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                element.clear()
                element.send_keys(text)
                print(f"[REPLAY]   OK Typed: '{text[:50]}{'...' if len(text) > 50 else ''}'")
            except Exception as e:
                print(f"[REPLAY]   FAILED to type: {str(e)[:150]}")
                continue

        # Delay between steps (1 second)
        time.sleep(1)

    except Exception as e:
        print(f"[REPLAY]   ERROR: {str(e)[:150]}")
        continue

print(f"\n[REPLAY] Replay complete!")
print(f"[REPLAY] Executed {len(skill['steps'])} steps")

print("\n[REPLAY] Disconnecting from Chrome (browser stays open)")
driver.quit()
