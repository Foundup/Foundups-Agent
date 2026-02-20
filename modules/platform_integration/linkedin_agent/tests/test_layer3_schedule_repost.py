#!/usr/bin/env python3
"""
Layer 3: Schedule Repost - Repost with thoughts and schedule for future.

Test Modes:
    --selenium: Pure Selenium DOM automation
    --dry-run: Validate selectors without scheduling
    --info: Show layer info only

Usage:
    python -m modules.platform_integration.linkedin_agent.tests.test_layer3_schedule_repost --selenium
    python -m modules.platform_integration.linkedin_agent.tests.test_layer3_schedule_repost --selenium --dry-run
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))


def load_repost_template() -> dict:
    """Load repost template from skill templates."""
    template_path = Path(__file__).parent.parent / "data" / "linkedin_skill_templates.json"
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("repost_templates", {}).get("foundups_thoughts", {})
    except Exception as e:
        print(f"[WARNING] Could not load template: {e}")
        return {
            "text": "AI transforms work. #AGIjobsAPOC",
            "paper_url": ""
        }


def get_next_schedule_slot() -> tuple:
    """
    Calculate next available schedule slot.
    
    Returns:
        (date_str, time_str) in formats for LinkedIn
    """
    now = datetime.now()
    # Schedule 4-6 hours from now, rounded to 15 minutes
    offset_hours = 4 + (hash(str(now)) % 3)  # 4, 5, or 6 hours
    scheduled = now + timedelta(hours=offset_hours)
    
    # Round to 15-minute increment
    minutes = (scheduled.minute // 15) * 15
    scheduled = scheduled.replace(minute=minutes, second=0, microsecond=0)
    
    # Format for LinkedIn (may vary by locale)
    date_str = scheduled.strftime("%b %d, %Y")  # e.g., "Jan 21, 2026"
    time_str = scheduled.strftime("%I:%M %p")   # e.g., "12:00 PM"
    
    return date_str, time_str


def test_layer3_selenium(dry_run: bool = False) -> dict:
    """
    Test Layer 3 with pure Selenium.
    
    Args:
        dry_run: If True, validate selectors but don't schedule
    
    Returns:
        dict with keys: success, repost_modal_opened, scheduled
    """
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from modules.platform_integration.linkedin_agent.tests.linkedin_browser import (
        get_linkedin_driver,
        ensure_linkedin_logged_in,
    )

    print("\n[L3] Layer 3: Schedule Repost - Selenium Mode")
    print(f"[MODE] {'DRY RUN (no schedule)' if dry_run else 'LIVE'}")
    print("=" * 60)
    step_delay = float(os.getenv("LINKEDIN_ACTION_DELAY_SEC", "3") or 3)

    result = {
        "success": False,
        "repost_modal_opened": False,
        "repost_text_entered": False,
        "schedule_picker_opened": False,
        "scheduled": False,
        "scheduled_time": None,
        "error": None
    }

    # Connect to Chrome (debug port or BrowserManager)
    try:
        driver = get_linkedin_driver()
        print(f"[OK] Connected to Chrome: {driver.title[:50]}...")
    except Exception as e:
        print(f"[ERROR] Failed to connect: {e}")
        result["error"] = str(e)
        return result

    if not ensure_linkedin_logged_in(driver):
        result["error"] = "LinkedIn login not confirmed"
        return result

    # Verify we're on LinkedIn
    if "linkedin.com" not in driver.current_url:
        print(f"[ERROR] Not on LinkedIn: {driver.current_url}")
        result["error"] = "Not on LinkedIn"
        return result

    # Step 3.1: Click Repost button
    print("\n[STEP 3.1] Looking for Repost button...")
    time.sleep(step_delay)
    
    repost_selectors = [
        "button[aria-label*='Repost']",
        "button[aria-label*='repost']",
        ".social-reshare-button",
        "button.feed-shared-social-action-bar__action-btn--repost",
    ]

    repost_clicked = False
    for selector in repost_selectors:
        try:
            buttons = driver.find_elements(By.CSS_SELECTOR, selector)
            if buttons:
                buttons[0].click()
                time.sleep(max(1.0, step_delay))
                repost_clicked = True
                print(f"[OK] Repost button clicked: {selector}")
                break
        except Exception:
            continue

    if not repost_clicked:
        # Try text search
        try:
            all_buttons = driver.find_elements(By.TAG_NAME, "button")
            for btn in all_buttons:
                if "repost" in btn.text.lower() or "repost" in btn.get_attribute("aria-label", "").lower():
                    btn.click()
                    time.sleep(max(1.0, step_delay))
                    repost_clicked = True
                    print("[OK] Repost button clicked via text search")
                    break
        except Exception:
            pass

    if not repost_clicked:
        print("[ERROR] Could not find Repost button")
        result["error"] = "Repost button not found"
        return result

    # Step 3.2: Select "Repost with your thoughts"
    print("\n[STEP 3.2] Selecting 'Repost with your thoughts'...")
    time.sleep(max(1.0, step_delay))

    thoughts_selectors = [
        "[data-control-name*='repost_with_thoughts']",
        "button:contains('with your thoughts')",
        ".artdeco-dropdown__item",
    ]

    thoughts_clicked = False
    try:
        # Look for the dropdown item by text
        dropdown_items = driver.find_elements(By.CSS_SELECTOR, ".artdeco-dropdown__item, [role='menuitem']")
        for item in dropdown_items:
            if "thoughts" in item.text.lower() or "your thoughts" in item.text.lower():
                item.click()
                time.sleep(max(1.0, step_delay))
                thoughts_clicked = True
                result["repost_modal_opened"] = True
                print("[OK] Selected 'Repost with your thoughts'")
                break
        
        if not thoughts_clicked:
            # Try XPATH
            thoughts_elem = driver.find_element(By.XPATH, "//*[contains(text(), 'with your thoughts')]")
            thoughts_elem.click()
            time.sleep(max(1.0, step_delay))
            thoughts_clicked = True
            result["repost_modal_opened"] = True
            print("[OK] Selected via XPATH")

    except Exception as e:
        print(f"[WARNING] Could not select 'Repost with your thoughts': {e}")

    if not result["repost_modal_opened"]:
        print("[ERROR] Repost modal did not open")
        result["error"] = "Modal not opened"
        return result

    # Step 3.3: Type repost text
    print("\n[STEP 3.3] Typing repost text...")
    time.sleep(step_delay)
    template = load_repost_template()
    repost_text = template.get("text", "Test repost from 0102.")

    editor_selectors = [
        ".share-creation-state__text-editor .ql-editor",
        "[data-placeholder*='Add a comment']",
        "[contenteditable='true'][role='textbox']",
        ".ql-editor",
    ]

    editor = None
    for selector in editor_selectors:
        try:
            editors = driver.find_elements(By.CSS_SELECTOR, selector)
            if editors:
                editor = editors[0]
                print(f"[OK] Found editor: {selector}")
                break
        except Exception:
            continue

    if editor:
        try:
            editor.click()
            time.sleep(0.3)
            editor.send_keys(repost_text)
            time.sleep(max(0.5, step_delay))
            result["repost_text_entered"] = True
            print(f"[OK] Typed: {repost_text[:40]}...")
        except Exception as e:
            print(f"[WARNING] Could not type text: {e}")
    else:
        print("[WARNING] Could not find repost editor")

    # Step 3.4: Click Schedule button (instead of Post)
    print("\n[STEP 3.4] Looking for Schedule option...")
    time.sleep(step_delay)
    
    schedule_selectors = [
        "button[aria-label*='Schedule']",
        ".share-creation-state__date-time button",
        "button:contains('Schedule')",
        "[data-control-name*='schedule']",
    ]

    schedule_clicked = False
    for selector in schedule_selectors:
        try:
            buttons = driver.find_elements(By.CSS_SELECTOR, selector)
            if buttons:
                if not dry_run:
                    buttons[0].click()
                    time.sleep(max(1.0, step_delay))
                schedule_clicked = True
                print(f"[OK] Schedule button found: {selector}")
                break
        except Exception:
            continue

    if not schedule_clicked:
        # Try looking for clock icon or schedule text
        try:
            schedule_elem = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'chedule') or contains(., 'chedule')]")
            if not dry_run:
                schedule_elem.click()
                time.sleep(max(1.0, step_delay))
            schedule_clicked = True
            print("[OK] Schedule button clicked via XPATH")
        except Exception:
            print("[WARNING] Could not find Schedule button - may need to click dropdown arrow")

    # Step 3.5-3.6: Date and Time picker
    date_str, time_str = get_next_schedule_slot()
    print(f"\n[STEP 3.5-3.6] Target schedule: {date_str} at {time_str}")
    time.sleep(step_delay)

    if schedule_clicked and not dry_run:
        result["schedule_picker_opened"] = True
        
        # Try to interact with date picker
        try:
            date_input = driver.find_element(By.CSS_SELECTOR, "input[type='date'], [aria-label*='date'], .date-picker input")
            date_input.clear()
            date_input.send_keys(date_str)
            print(f"[OK] Date entered: {date_str}")
        except Exception as e:
            print(f"[INFO] Date picker interaction: {e}")

        # Try to interact with time picker
        try:
            time_input = driver.find_element(By.CSS_SELECTOR, "input[type='time'], [aria-label*='time'], .time-picker input")
            time_input.clear()
            time_input.send_keys(time_str)
            print(f"[OK] Time entered: {time_str}")
        except Exception as e:
            print(f"[INFO] Time picker interaction: {e}")

    # Step 3.7: Confirm Schedule
    if dry_run:
        print("\n[STEP 3.7] DRY RUN - Skipping final schedule confirmation")
        result["success"] = result["repost_modal_opened"]
        print(f"\n[SUCCESS] Layer 3 DRY RUN complete!")
        return result

    print("\n[STEP 3.7] Confirming schedule...")
    time.sleep(step_delay)
    
    confirm_selectors = [
        "button.share-actions__primary-action",
        "button[type='submit']",
        "button:contains('Schedule')",
    ]

    confirmed = False
    for selector in confirm_selectors:
        try:
            buttons = driver.find_elements(By.CSS_SELECTOR, selector)
            if buttons:
                buttons[-1].click()  # Usually last button is confirm
                time.sleep(2)
                confirmed = True
                result["scheduled"] = True
                result["scheduled_time"] = f"{date_str} {time_str}"
                print("[OK] Schedule confirmed!")
                break
        except Exception:
            continue

    # Step 3.8: Verify scheduled post
    print("\n[STEP 3.8] Verifying scheduled post...")
    # Check if modal closed and we're back on feed
    try:
        if "feed" in driver.current_url or not driver.find_elements(By.CSS_SELECTOR, ".share-box-modal"):
            print("[OK] Modal closed, back on feed")
    except Exception:
        pass

    result["success"] = result["repost_modal_opened"] and (result["scheduled"] or dry_run)
    print(f"\n[{'SUCCESS' if result['success'] else 'PARTIAL'}] Layer 3 complete!")
    print(f"  Modal opened: {result['repost_modal_opened']}")
    print(f"  Text entered: {result['repost_text_entered']}")
    print(f"  Scheduled: {result['scheduled']}")
    if result["scheduled_time"]:
        print(f"  Scheduled for: {result['scheduled_time']}")

    return result


def test_layer3_info():
    """Show layer info without running."""
    date_str, time_str = get_next_schedule_slot()
    template = load_repost_template()
    
    print("\n[L3] Layer 3: Schedule Repost")
    print("=" * 60)
    print("Purpose: Repost with thoughts and schedule for future")
    print("")
    print("Steps:")
    print("  3.1 Click Repost button")
    print("  3.2 Select 'Repost with your thoughts'")
    print("  3.3 Type repost text (from template)")
    print("  3.4 Click Schedule (not Post)")
    print("  3.5 Select date via calendar")
    print("  3.6 Enter time (15-min increments)")
    print("  3.7 Confirm Schedule")
    print("  3.8 Verify modal closed")
    print("")
    print("DOM Selectors:")
    print("  - Repost: button[aria-label*='Repost']")
    print("  - Editor: .share-creation-state__text-editor .ql-editor")
    print("  - Schedule: button[aria-label*='Schedule']")
    print("")
    print(f"Template text: {template.get('text', 'N/A')[:50]}...")
    print(f"Next slot: {date_str} at {time_str}")
    print("")
    print("Scheduling rules:")
    print("  - 1-3 posts/day")
    print("  - 4-6 hour spacing minimum")
    print("  - 15-minute increments")
    print("")
    print("Usage:")
    print("  python -m ...test_layer3_schedule_repost --selenium")
    print("  python -m ...test_layer3_schedule_repost --selenium --dry-run")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Layer 3: Schedule Repost Test")
    parser.add_argument("--selenium", action="store_true", help="Run with pure Selenium")
    parser.add_argument("--dry-run", action="store_true", help="Validate without scheduling")
    parser.add_argument("--info", action="store_true", help="Show layer info only")

    args = parser.parse_args()

    if args.info:
        test_layer3_info()
    elif args.selenium:
        result = test_layer3_selenium(dry_run=args.dry_run)
        sys.exit(0 if result["success"] else 1)
    else:
        test_layer3_info()
        print("\n[TIP] Add --selenium to run the test")
