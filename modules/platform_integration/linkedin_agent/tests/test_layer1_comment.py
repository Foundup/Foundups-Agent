#!/usr/bin/env python3
"""
Layer 1: Comment - Post 012 Digital Twin comment with @mentions.

Test Modes:
    --selenium: Pure Selenium DOM automation
    --dry-run: Validate selectors without submitting
    --info: Show layer info only

Usage:
    python -m modules.platform_integration.linkedin_agent.tests.test_layer1_comment --selenium
    python -m modules.platform_integration.linkedin_agent.tests.test_layer1_comment --selenium --dry-run
"""

import argparse
import asyncio
import json
import os
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))


def load_comment_template() -> dict:
    """Load comment template from skill templates."""
    template_path = Path(__file__).parent.parent / "data" / "linkedin_skill_templates.json"
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("comment_templates", {}).get("undao_du_012", {})
    except Exception as e:
        print(f"[WARNING] Could not load template: {e}")
        return {
            "text": "Test comment from 0102 Digital Twin.",
            "mentions": ["@foundups"]
        }


def test_layer1_selenium(dry_run: bool = False, ai_gate_passed: bool = True) -> dict:
    """
    Test Layer 1 with pure Selenium.
    
    Args:
        dry_run: If True, validate selectors but don't submit comment
    
    Returns:
        dict with keys: success, comment_visible, mention_bolded
    """
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from modules.platform_integration.linkedin_agent.tests.linkedin_browser import (
        get_linkedin_driver,
        ensure_linkedin_logged_in,
    )
    from modules.infrastructure.foundups_selenium.src.human_behavior import get_012_behavior
    try:
        from modules.infrastructure.foundups_vision.src.ui_tars_bridge import UITarsBridge
        UI_TARS_AVAILABLE = True
    except ImportError:
        UI_TARS_AVAILABLE = False
        UITarsBridge = None

    print("\n[L1] Layer 1: Comment - Selenium Mode")
    print(f"[MODE] {'DRY RUN (no submit)' if dry_run else 'LIVE'}")
    print("=" * 60)

    result = {
        "success": False,
        "comment_visible": False,
        "mention_bolded": False,
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

    # Step 1.0: Like post (AI gate)
    human = get_012_behavior(driver)
    use_ui_tars = os.getenv("LINKEDIN_USE_UI_TARS", "true").lower() in {"1", "true", "yes"}
    require_ui_tars = os.getenv("LINKEDIN_REQUIRE_UI_TARS", "true").lower() in {"1", "true", "yes"}
    step_delay = float(os.getenv("LINKEDIN_ACTION_DELAY_SEC", "3") or 3)

    def _ui_tars_verify(description: str) -> bool:
        if not use_ui_tars:
            return True
        if not UI_TARS_AVAILABLE:
            if require_ui_tars:
                result["error"] = "UI-TARS bridge unavailable"
            return False

        async def _run() -> bool:
            bridge = UITarsBridge()
            await bridge.connect()
            action_result = await bridge.execute_action(
                action="verify",
                description=description,
                context={"url": driver.current_url},
                driver=driver,
            )
            return bool(action_result and action_result.success)

        try:
            # Handle case where event loop is already running (e.g., Jupyter, nested calls)
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None
            
            if loop and loop.is_running():
                # Already in async context - create task and run
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(asyncio.run, _run())
                    return future.result(timeout=30)
            else:
                return asyncio.run(_run())
        except Exception as e:
            if require_ui_tars:
                result["error"] = f"UI-TARS verify failed: {e}"
            return False

    if ai_gate_passed:
        print("\n[STEP 1.0] Liking AI post...")
        like_selectors = [
            "button[aria-label*='React Like']",
            "button.react-button__trigger",
            "span.reaction-react-button button",
            "button[aria-pressed][aria-label*='Like']",
        ]
        liked = False
        for selector in like_selectors:
            try:
                buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                if buttons:
                    if not dry_run:
                        human.scroll_to_element(buttons[0])
                        human.human_click(buttons[0])
                    liked = True
                    print(f"[OK] Like clicked: {selector}")
                    break
            except Exception:
                continue
        if not liked:
            print("[WARNING] Could not find Like button")
    else:
        print("[SKIP] AI gate not passed - skip like/comment actions")
        result["success"] = True
        return result

    # Step 1.1: Click Comment button
    print("\n[STEP 1.1] Opening comment box...")
    time.sleep(step_delay)
    comment_button_selectors = [
        "button[aria-label*='Comment']",
        "button.comment-button",
        ".feed-shared-social-action-bar button:nth-child(2)",
        "button[data-control-name='comment']",
        ".social-details-social-counts button[aria-label*='comment']",
        "button[id*='feed-shared-social-action-bar-comment']",
    ]

    comment_box_opened = False
    for selector in comment_button_selectors:
        try:
            buttons = driver.find_elements(By.CSS_SELECTOR, selector)
            if buttons:
                human.scroll_to_element(buttons[0])
                human.human_click(buttons[0])
                comment_box_opened = True
                print(f"[OK] Comment button clicked: {selector}")
                break
        except Exception:
            continue

    if not comment_box_opened:
        # Try finding via text content
        try:
            all_buttons = driver.find_elements(By.TAG_NAME, "button")
            for btn in all_buttons:
                if "comment" in btn.text.lower() or "comment" in btn.get_attribute("aria-label", "").lower():
                    human.scroll_to_element(btn)
                    human.human_click(btn)
                    comment_box_opened = True
                    print("[OK] Comment button clicked via text search")
                    break
        except Exception:
            pass

    if not comment_box_opened:
        print("[ERROR] Could not find comment button")
        result["error"] = "Comment button not found"
        return result

    if not _ui_tars_verify("LinkedIn comment box editor visible under the top post"):
        if not result.get("error"):
            result["error"] = "UI-TARS could not verify comment editor"
        return result

    # Step 1.2: Find and type in comment editor
    print("\n[STEP 1.2] Typing comment...")
    time.sleep(step_delay)
    template = load_comment_template()
    comment_text = template.get("text", "Test comment from 0102.")
    
    # Use shorter text for testing
    test_text = "Test from 0102 Digital Twin - validating L1 flow."

    editor_selectors = [
        ".comments-comment-box-comment__text-editor .ql-editor",
        ".comments-comment-texteditor .ql-editor",
        "[data-placeholder*='Add a comment']",
        ".editor-content[contenteditable='true']",
        "[contenteditable='true'][role='textbox']",
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

    if not editor:
        print("[ERROR] Could not find comment editor")
        result["error"] = "Comment editor not found"
        return result

    # Type comment text
    try:
        human.scroll_to_element(editor)
        human.human_type(editor, test_text)
        print(f"[OK] Typed: {test_text[:40]}...")
    except Exception as e:
        print(f"[ERROR] Failed to type: {e}")
        result["error"] = str(e)
        return result

    if not _ui_tars_verify("Typed comment text visible in LinkedIn editor"):
        if not result.get("error"):
            result["error"] = "UI-TARS could not verify typed comment text"
        return result

    # Step 1.3: Insert @foundups mention
    print("\n[STEP 1.3] Inserting @mention...")
    time.sleep(step_delay)
    try:
        human.human_type(editor, " @foundups")
        time.sleep(1.5)

        # Look for mention dropdown
        dropdown_selectors = [
            ".mentions-autocomplete__results",
            ".basic-typeahead__selectable",
            "[role='listbox'] [role='option']",
            ".mentions-autocomplete__result",
        ]

        dropdown_visible = False
        for selector in dropdown_selectors:
            try:
                items = driver.find_elements(By.CSS_SELECTOR, selector)
                if items:
                    print(f"[OK] Dropdown visible: {selector} ({len(items)} items)")
                    dropdown_visible = True
                    # Click first item
                    human.scroll_to_element(items[0])
                    human.human_click(items[0])
                    print("[OK] Selected top mention item")
                    break
            except Exception:
                continue

        if not dropdown_visible:
            # Try pressing Enter/Tab to select
            editor.send_keys(Keys.RETURN)
            time.sleep(0.5)
            print("[INFO] Pressed Enter to select mention (dropdown not visible)")

        # Verify mention is bolded/linked in editor
        editor_html = driver.execute_script(
            "return arguments[0].innerHTML || '';",
            editor
        )
        
        mention_indicators = ["<a", "<strong", "mention", "data-entity"]
        result["mention_bolded"] = any(ind in editor_html.lower() for ind in mention_indicators)
        
        if result["mention_bolded"]:
            print("[OK] Mention appears formatted (bold/link)")
        else:
            print("[WARNING] Mention may not be properly formatted")
            print(f"[DEBUG] Editor HTML: {editor_html[:200]}...")

    except Exception as e:
        print(f"[WARNING] Mention insertion issue: {e}")

    if not _ui_tars_verify("Foundups @mention appears bolded/selected in comment editor"):
        if not result.get("error"):
            result["error"] = "UI-TARS could not verify mention selection"
        return result

    # Step 1.4: Submit comment (unless dry run)
    if dry_run:
        print("\n[STEP 1.4] DRY RUN - Skipping submit")
        result["success"] = True
        print("\n[SUCCESS] Layer 1 DRY RUN complete!")
        return result

    print("\n[STEP 1.4] Submitting comment...")
    time.sleep(step_delay)
    submit_selectors = [
        "button.comments-comment-box__submit-button",
        "button[type='submit'].comments-comment-box__submit-button",
        "button[aria-label*='Post']",
        ".comments-comment-box button[type='submit']",
    ]

    submitted = False
    for selector in submit_selectors:
        try:
            buttons = driver.find_elements(By.CSS_SELECTOR, selector)
            if buttons:
                human.scroll_to_element(buttons[0])
                human.human_click(buttons[0])
                submitted = True
                print(f"[OK] Submit clicked: {selector}")
                break
        except Exception:
            continue

    if not submitted:
        print("[WARNING] Could not find submit button")
        result["error"] = "Submit button not found"
        return result

    # Step 1.5: Verify comment visible or switch to Most recent
    print("\n[STEP 1.5] Verifying comment visibility...")
    time.sleep(2)

    # Check if our comment is visible
    try:
        comments = driver.find_elements(By.CSS_SELECTOR, ".comments-comment-item, .comments-comment-entity")
        for comment in comments[:5]:
            if "0102" in comment.text or "Digital Twin" in comment.text:
                result["comment_visible"] = True
                print("[OK] Comment visible in thread!")
                break
    except Exception:
        pass

    if not result["comment_visible"]:
        print("[INFO] Comment not immediately visible, trying Most recent...")
        # Try switching to Most recent
        try:
            sort_buttons = driver.find_elements(By.CSS_SELECTOR, "[aria-label*='Sort'], .comments-sort-order-toggle")
            if sort_buttons:
                sort_buttons[0].click()
                time.sleep(1)
                # Click "Most recent"
                recent_options = driver.find_elements(By.XPATH, "//*[contains(text(), 'Most recent')]")
                if recent_options:
                    recent_options[0].click()
                    time.sleep(1)
                    print("[OK] Switched to Most recent")
        except Exception as e:
            print(f"[WARNING] Could not switch sort order: {e}")

    result["success"] = True
    print(f"\n[SUCCESS] Layer 1 complete!")
    print(f"  Comment visible: {result['comment_visible']}")
    print(f"  Mention formatted: {result['mention_bolded']}")

    return result


def test_layer1_info():
    """Show layer info without running."""
    print("\n[L1] Layer 1: Comment")
    print("=" * 60)
    print("Purpose: Post 012 Digital Twin comment with @mentions")
    print("")
    print("Steps:")
    print("  1.0 Like post (AI gate)")
    print("  1.1 Click Comment button")
    print("  1.2 Type comment text")
    print("  1.3 Insert @foundups mention, verify dropdown")
    print("  1.x UI-TARS verifies editor + mention selection")
    print("  1.4 Submit comment")
    print("  1.5 Verify visible or switch to Most recent")
    print("")
    print("DOM Selectors:")
    print("  - Comment btn: button[aria-label*='Comment']")
    print("  - Editor: .comments-comment-box-comment__text-editor .ql-editor")
    print("  - Dropdown: .mentions-autocomplete__results")
    print("  - Submit: button.comments-comment-box__submit-button")
    print("")
    print("Template: linkedin_skill_templates.json -> undao_du_012")
    print("")
    print("Usage:")
    print("  python -m ...test_layer1_comment --selenium")
    print("  python -m ...test_layer1_comment --selenium --dry-run")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Layer 1: Comment Test")
    parser.add_argument("--selenium", action="store_true", help="Run with pure Selenium")
    parser.add_argument("--dry-run", action="store_true", help="Validate without submitting")
    parser.add_argument("--info", action="store_true", help="Show layer info only")

    args = parser.parse_args()

    if args.info:
        test_layer1_info()
    elif args.selenium:
        result = test_layer1_selenium(dry_run=args.dry_run)
        sys.exit(0 if result["success"] else 1)
    else:
        test_layer1_info()
        print("\n[TIP] Add --selenium to run the test")
