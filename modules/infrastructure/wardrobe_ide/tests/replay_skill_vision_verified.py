"""
Replay Wardrobe skill with VISION VERIFICATION and RETRY

This replays skills using vision AI with a verification loop:
1. Execute action (like, heart, reply)
2. Take screenshot to verify action succeeded
3. If failed, retry up to 3 times
"""
import sys
import asyncio
import json
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(repo_root))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from modules.infrastructure.foundups_vision.src.ui_tars_bridge import UITarsBridge

print("[VERIFIED REPLAY] Wardrobe Vision Replay with Verification")
print("=" * 80)

# Connect to existing Chrome on port 9222
print("[VERIFIED REPLAY] Connecting to Chrome on port 9222...")
chrome_options = ChromeOptions()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

try:
    driver = webdriver.Chrome(options=chrome_options)
    print(f"[VERIFIED REPLAY] Connected! Current URL: {driver.current_url}")
except Exception as e:
    print(f"[ERROR] Could not connect to Chrome: {e}")
    print("[ERROR] Make sure Chrome is running with --remote-debugging-port=9222")
    sys.exit(1)

# Load skill file
skill_path = input("\n[VERIFIED REPLAY] Enter path to skill JSON file:\n> ").strip().strip('"')
skill_path = Path(skill_path)

if not skill_path.exists():
    print(f"[ERROR] Skill file not found: {skill_path}")
    driver.quit()
    sys.exit(1)

with open(skill_path) as f:
    skill = json.load(f)

print(f"\n[VERIFIED REPLAY] Loaded skill: {skill['name']}")
print(f"[VERIFIED REPLAY] Steps: {len(skill['steps'])}")
print(f"[VERIFIED REPLAY] Target URL: {skill['meta']['target_url']}")

# Navigate to target URL if needed
current_url = driver.current_url
target_url = skill['meta']['target_url']

# Remove query parameters for comparison
current_base = current_url.split('?')[0]
target_base = target_url.split('?')[0]

if current_base != target_base:
    print(f"\n[VERIFIED REPLAY] Navigating to target URL...")
    driver.get(target_url)
    import time
    time.sleep(3)  # Wait for page load
    print(f"[VERIFIED REPLAY] Navigated! URL: {driver.current_url}")


async def verify_action_succeeded(bridge, action_type, description, driver, max_retries=3):
    """
    Execute action with visual verification and retry.

    Returns True if action succeeded, False otherwise.
    """
    for attempt in range(1, max_retries + 1):
        print(f"\n[VERIFIED REPLAY] Attempt {attempt}/{max_retries}")

        # Execute the action
        result = await bridge.execute_action(
            action='click',
            description=description,
            driver=driver,
            timeout=90
        )

        if result.success:
            print(f"[VERIFIED REPLAY]    OK Clicked: {description}")
            print(f"[VERIFIED REPLAY]   Confidence: {result.confidence:.2f}")
            print(f"[VERIFIED REPLAY]   Duration: {result.duration_ms}ms")
            if result.metadata.get('thought'):
                print(f"[VERIFIED REPLAY]   Thought: {result.metadata['thought'][:80]}...")

            # Wait a moment for UI to update
            import time
            time.sleep(1)

            # Now verify the action succeeded by checking if button is highlighted
            print(f"[VERIFIED REPLAY]   Verifying action succeeded...")

            # Build verification prompt based on action
            if 'Like' in description or 'thumbs up' in description.lower():
                verify_description = "highlighted thumbs up button (filled/blue icon showing it's been liked)"
            elif 'Heart' in description or 'Love' in description:
                verify_description = "highlighted heart button (filled/red icon showing it's been loved)"
            elif 'Reply' in description:
                verify_description = "reply text box is visible and active"
            else:
                verify_description = f"{description} is active/highlighted"

            # Use vision to verify the button is now highlighted
            verify_result = await bridge.execute_action(
                action='verify',
                description=verify_description,
                driver=driver,
                timeout=90
            )

            # Check if verification found the highlighted button
            if verify_result.success and verify_result.confidence > 0.6:
                print(f"[VERIFIED REPLAY]   VERIFIED: Action succeeded!")
                print(f"[VERIFIED REPLAY]   Verification confidence: {verify_result.confidence:.2f}")
                return True
            else:
                print(f"[VERIFIED REPLAY]   VERIFICATION FAILED: Button not highlighted")
                print(f"[VERIFIED REPLAY]   Verification confidence: {verify_result.confidence:.2f}")
                if attempt < max_retries:
                    print(f"[VERIFIED REPLAY]   Retrying...")
                    continue
                else:
                    print(f"[VERIFIED REPLAY]   Max retries reached")
                    return False
        else:
            print(f"[VERIFIED REPLAY]    FAILED: {result.error}")
            if attempt < max_retries:
                print(f"[VERIFIED REPLAY]   Retrying...")
                continue
            else:
                print(f"[VERIFIED REPLAY]   Max retries reached")
                return False

    return False


async def replay_with_verification():
    """Replay skills using UI-TARS vision automation with verification."""

    # Initialize UI-TARS bridge
    print(f"\n[VERIFIED REPLAY] Initializing UI-TARS bridge...")
    bridge = UITarsBridge(browser_port=9222)
    await bridge.connect()

    print(f"\n[VERIFIED REPLAY] Starting vision-based replay with verification...")
    print(f"[VERIFIED REPLAY] Using ui-tars-1.5-7b model via LM Studio")

    for i, step in enumerate(skill['steps'], 1):
        action = step['action']

        print(f"\n[VERIFIED REPLAY] Step {i}/{len(skill['steps'])}: {action}")

        try:
            if action == 'click':
                # Get description from notes or construct from selector
                target_aria_label = step.get('target_aria_label', '')
                selector = step.get('selector', '')

                # Build natural language description
                if target_aria_label:
                    description = target_aria_label
                elif 'Like' in selector:
                    description = "Like button (thumbs up icon)"
                elif 'Love' in selector or 'Heart' in selector:
                    description = "Heart button (love icon)"
                elif 'Reply' in selector:
                    description = "Reply button"
                else:
                    description = "clickable button"

                print(f"[VERIFIED REPLAY]   Looking for: {description}")

                # Execute with verification and retry
                success = await verify_action_succeeded(
                    bridge=bridge,
                    action_type='click',
                    description=description,
                    driver=driver,
                    max_retries=3
                )

                if not success:
                    print(f"[VERIFIED REPLAY]   FINAL FAILURE: Could not complete action after retries")
                    # Continue to next step anyway

            elif action == 'type':
                text = step['text']
                description = "text input field"

                print(f"[VERIFIED REPLAY]   Typing: {text[:50]}...")

                result = await bridge.type_text(
                    description=description,
                    text=text,
                    driver=driver,
                    timeout=90
                )

                if result.success:
                    print(f"[VERIFIED REPLAY]    OK Typed")
                else:
                    print(f"[VERIFIED REPLAY]    FAILED: {result.error}")
                    continue

            # Small delay between steps
            import time
            time.sleep(1)

        except Exception as e:
            print(f"[VERIFIED REPLAY]    ERROR: {str(e)[:150]}")
            continue

    bridge.close()
    print(f"\n[VERIFIED REPLAY] Replay complete!")


# Run async replay
asyncio.run(replay_with_verification())

print("\n[VERIFIED REPLAY] Disconnecting from Chrome (browser stays open)")
driver.quit()
