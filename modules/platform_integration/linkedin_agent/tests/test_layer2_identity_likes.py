#!/usr/bin/env python3
"""
Layer 2: Identity Like Loop - Switch identities and like 012 comment.

Test Modes:
    --selenium: Pure Selenium DOM automation
    --dry-run: Validate selectors without liking
    --single: Test single identity switch only
    --info: Show layer info only

Usage:
    python -m modules.platform_integration.linkedin_agent.tests.test_layer2_identity_likes --selenium
    python -m modules.platform_integration.linkedin_agent.tests.test_layer2_identity_likes --selenium --dry-run
    python -m modules.platform_integration.linkedin_agent.tests.test_layer2_identity_likes --selenium --single
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))


def load_identity_list() -> list:
    """Load identity list from switcher config."""
    config_path = Path(__file__).parent.parent / "data" / "linkedin_identity_switcher.json"
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Filter to like_only identities
        return [
            ident for ident in data.get("identities", [])
            if ident.get("action") == "like_only"
        ]
    except Exception as e:
        print(f"[WARNING] Could not load identity list: {e}")
        return [{"display_name": "FOUNDUPS", "action": "like_only"}]


def get_return_identity() -> str:
    """Get the identity to return to after likes."""
    config_path = Path(__file__).parent.parent / "data" / "linkedin_identity_switcher.json"
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for ident in data.get("identities", []):
            if ident.get("action") == "return_to_012":
                return ident.get("display_name")
    except Exception:
        pass
    return "UnDaoDu Michael J Trout"


def test_layer2_selenium(dry_run: bool = False, single: bool = False) -> dict:
    """
    Test Layer 2 with pure Selenium.
    
    Args:
        dry_run: If True, validate selectors but don't like
        single: If True, test only first identity switch
    
    Returns:
        dict with keys: success, identities_switched, likes_applied
    """
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from modules.platform_integration.linkedin_agent.tests.linkedin_browser import (
        get_linkedin_driver,
        ensure_linkedin_logged_in,
    )

    print("\n[L2] Layer 2: Identity Like Loop - Selenium Mode")
    print(f"[MODE] {'DRY RUN' if dry_run else 'LIVE'} | {'SINGLE' if single else 'FULL LOOP'}")
    print("=" * 60)
    step_delay = float(os.getenv("LINKEDIN_ACTION_DELAY_SEC", "3") or 3)

    result = {
        "success": False,
        "identities_switched": 0,
        "likes_applied": 0,
        "returned_to_012": False,
        "errors": []
    }

    # Connect to Chrome (debug port or BrowserManager)
    try:
        driver = get_linkedin_driver()
        print(f"[OK] Connected to Chrome: {driver.title[:50]}...")
    except Exception as e:
        print(f"[ERROR] Failed to connect: {e}")
        result["errors"].append(str(e))
        return result

    if not ensure_linkedin_logged_in(driver):
        result["errors"].append("LinkedIn login not confirmed")
        return result

    # Verify we're on LinkedIn
    if "linkedin.com" not in driver.current_url:
        print(f"[ERROR] Not on LinkedIn: {driver.current_url}")
        result["errors"].append("Not on LinkedIn")
        return result

    # Load identity list
    identities = load_identity_list()
    if single:
        identities = identities[:1]
    
    print(f"[INFO] Processing {len(identities)} identities")

    # Step 2.1: Find identity switcher
    print("\n[STEP 2.1] Looking for identity switcher...")
    time.sleep(step_delay)
    
    switcher_selectors = [
        "button[aria-label*='Account']",
        ".global-nav__me-photo",
        ".feed-identity-module__actor-meta button",
        "img.global-nav__me-photo",
        ".nav-profile-logo",
    ]

    switcher_found = False
    for selector in switcher_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                elements[0].click()
                time.sleep(1)
                switcher_found = True
                print(f"[OK] Identity switcher opened: {selector}")
                break
        except Exception:
            continue

    if not switcher_found:
        print("[WARNING] Could not find identity switcher button, trying profile menu...")
        try:
            # Try clicking on profile area in nav
            nav_me = driver.find_element(By.CSS_SELECTOR, "#global-nav-typeahead + button, .global-nav__me")
            nav_me.click()
            time.sleep(1)
            switcher_found = True
            print("[OK] Profile menu opened")
        except Exception as e:
            print(f"[ERROR] Could not open identity switcher: {e}")
            result["errors"].append("Switcher not found")
            return result

    # Look for page switcher option
    page_switcher_selectors = [
        "[data-control-name*='page_switcher']",
        "a[href*='pages']",
        "button:contains('Manage')",
        ".artdeco-dropdown__item",
    ]

    # Process each identity
    for idx, identity in enumerate(identities):
        identity_name = identity.get("display_name", "Unknown")
        print(f"\n[STEP 2.{idx+2}] Processing identity: {identity_name}")
        time.sleep(step_delay)

        # Find and click the identity
        try:
            # Look for identity in dropdown
            identity_elements = driver.find_elements(
                By.XPATH, 
                f"//*[contains(text(), '{identity_name}')]"
            )
            
            if identity_elements:
                if not dry_run:
                    identity_elements[0].click()
                    time.sleep(2)
                    result["identities_switched"] += 1
                    print(f"[OK] Switched to: {identity_name}")
                else:
                    print(f"[DRY RUN] Would switch to: {identity_name}")
                    result["identities_switched"] += 1
            else:
                print(f"[WARNING] Identity not found in dropdown: {identity_name}")
                result["errors"].append(f"Identity not found: {identity_name}")
                continue

        except Exception as e:
            print(f"[ERROR] Failed to switch identity: {e}")
            result["errors"].append(str(e))
            continue

        # Step 2.3-2.4: Locate 012 comment and like it
        if not dry_run:
            print(f"[STEP] Locating 012 comment to like...")
            time.sleep(step_delay)
            try:
                # Find comments containing 012 indicators
                comments = driver.find_elements(
                    By.CSS_SELECTOR, 
                    ".comments-comment-item, .comments-comment-entity"
                )
                
                comment_liked = False
                for comment in comments[:10]:
                    comment_text = comment.text
                    if "0102" in comment_text or "Digital Twin" in comment_text or "FoundUps" in comment_text:
                        # Find like button within comment
                        like_btn = comment.find_element(
                            By.CSS_SELECTOR, 
                            "button[aria-label*='Like'], button[aria-label*='like']"
                        )
                        like_btn.click()
                        time.sleep(max(1.0, step_delay))
                        result["likes_applied"] += 1
                        comment_liked = True
                        print(f"[OK] Liked 012 comment as {identity_name}")
                        break
                
                if not comment_liked:
                    print(f"[WARNING] Could not find 012 comment to like")

            except Exception as e:
                print(f"[WARNING] Like action failed: {e}")

        # Re-open switcher for next identity (if not last)
        if idx < len(identities) - 1:
            time.sleep(max(1.0, step_delay))
            for selector in switcher_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        elements[0].click()
                        time.sleep(max(1.0, step_delay))
                        break
                except Exception:
                    continue

    # Step 2.6: Return to 012 identity
    print("\n[STEP 2.6] Returning to 012 identity...")
    return_identity = get_return_identity()
    time.sleep(step_delay)
    
    try:
        # Open switcher
        for selector in switcher_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    elements[0].click()
                    time.sleep(max(1.0, step_delay))
                    break
            except Exception:
                continue
        
        # Find and click 012 identity
        identity_elements = driver.find_elements(
            By.XPATH, 
            f"//*[contains(text(), '{return_identity}')]"
        )
        
        if identity_elements and not dry_run:
            identity_elements[0].click()
            time.sleep(2)
            result["returned_to_012"] = True
            print(f"[OK] Returned to: {return_identity}")
        elif dry_run:
            print(f"[DRY RUN] Would return to: {return_identity}")
            result["returned_to_012"] = True

    except Exception as e:
        print(f"[WARNING] Could not return to 012: {e}")
        result["errors"].append(str(e))

    result["success"] = result["identities_switched"] > 0
    print(f"\n[{'SUCCESS' if result['success'] else 'PARTIAL'}] Layer 2 complete!")
    print(f"  Identities switched: {result['identities_switched']}")
    print(f"  Likes applied: {result['likes_applied']}")
    print(f"  Returned to 012: {result['returned_to_012']}")

    return result


def test_layer2_info():
    """Show layer info without running."""
    print("\n[L2] Layer 2: Identity Like Loop")
    print("=" * 60)
    print("Purpose: Switch through FoundUp identities, like 012 comment")
    print("")
    print("Steps:")
    print("  2.1 Open identity switcher")
    print("  2.2 Select identity from list")
    print("  2.3 Locate 012 comment")
    print("  2.4 Click Like button")
    print("  2.5 Repeat for each identity")
    print("  2.6 Return to 012 identity")
    print("")
    print("Identity list: linkedin_identity_switcher.json")
    print("")
    print("Identities (like_only):")
    for ident in load_identity_list():
        print(f"  - {ident.get('display_name')}")
    print("")
    print("Return to: " + get_return_identity())
    print("")
    print("Usage:")
    print("  python -m ...test_layer2_identity_likes --selenium")
    print("  python -m ...test_layer2_identity_likes --selenium --single")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Layer 2: Identity Like Loop Test")
    parser.add_argument("--selenium", action="store_true", help="Run with pure Selenium")
    parser.add_argument("--dry-run", action="store_true", help="Validate without liking")
    parser.add_argument("--single", action="store_true", help="Test single identity only")
    parser.add_argument("--info", action="store_true", help="Show layer info only")

    args = parser.parse_args()

    if args.info:
        test_layer2_info()
    elif args.selenium:
        result = test_layer2_selenium(dry_run=args.dry_run, single=args.single)
        sys.exit(0 if result["success"] else 1)
    else:
        test_layer2_info()
        print("\n[TIP] Add --selenium to run the test")
