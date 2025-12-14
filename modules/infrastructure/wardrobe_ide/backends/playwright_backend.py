"""
Playwright Backend - Primary recorder for Wardrobe Skills

This backend uses Playwright to:
1. Record browser interactions (clicks, types, navigations)
2. Replay recorded skills

Recording strategy:
- Injects JavaScript to listen for click and input events
- Generates CSS selectors for each interaction
- Records timing and sequence of actions
"""
import json
import time
from typing import Any

from playwright.sync_api import sync_playwright, Page, Browser

from . import WardrobeBackendBase
from ..src.skill import WardrobeSkill
from ..src.config import HEADLESS, SLOW_MO


class PlaywrightBackend(WardrobeBackendBase):
    """
    Playwright-based backend for recording and replaying browser interactions.
    """

    def record_session(
        self,
        target_url: str,
        duration_seconds: int = 15
    ) -> list[dict[str, Any]]:
        """
        Record a browser interaction session using Playwright.

        Opens a browser, navigates to target_url, and records all interactions
        (clicks, typing) for the specified duration.

        Args:
            target_url: URL to navigate to
            duration_seconds: How long to record

        Returns:
            List of recorded steps
        """
        steps = []

        with sync_playwright() as p:
            browser: Browser = p.chromium.launch(
                headless=HEADLESS,
                slow_mo=SLOW_MO
            )
            page: Page = browser.new_page()

            # Navigate to target URL
            page.goto(target_url)
            print(f"[RECORD] Navigated to {target_url}")
            print(f"[RECORD] Recording for {duration_seconds} seconds...")

            # Inject event listener script
            listener_script = """
            window.__wardrobeSteps = [];
            window.__startTime = Date.now();

            // Helper: Generate CSS selector for an element
            function getSelector(el) {
                if (el.id) return '#' + el.id;
                if (el.className && typeof el.className === 'string') {
                    const classes = el.className.trim().split(/\\s+/).join('.');
                    if (classes) return el.tagName.toLowerCase() + '.' + classes;
                }
                // Fallback: use tag name + nth-child
                let path = [];
                while (el.parentElement) {
                    let tag = el.tagName.toLowerCase();
                    let siblings = Array.from(el.parentElement.children);
                    let index = siblings.indexOf(el) + 1;
                    path.unshift(tag + ':nth-child(' + index + ')');
                    el = el.parentElement;
                    if (el.id) {
                        path.unshift('#' + el.id);
                        break;
                    }
                }
                return path.join(' > ');
            }

            // Listen for clicks
            document.addEventListener('click', (e) => {
                const selector = getSelector(e.target);
                const timestamp = (Date.now() - window.__startTime) / 1000;
                window.__wardrobeSteps.push({
                    action: 'click',
                    selector: selector,
                    timestamp: timestamp,
                    target_tag: e.target.tagName,
                    target_text: e.target.textContent?.substring(0, 50) || ''
                });
                console.log('[WARDROBE] Recorded click:', selector);
            }, true);

            // Listen for input/change events
            document.addEventListener('input', (e) => {
                if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
                    const selector = getSelector(e.target);
                    const timestamp = (Date.now() - window.__startTime) / 1000;
                    window.__wardrobeSteps.push({
                        action: 'type',
                        selector: selector,
                        text: e.target.value,
                        timestamp: timestamp
                    });
                    console.log('[WARDROBE] Recorded type:', selector, e.target.value);
                }
            }, true);

            console.log('[WARDROBE] Event listeners installed. Interact with the page!');
            """

            page.evaluate(listener_script)

            # Wait for duration
            start_time = time.time()
            print(f"[RECORD] Interact with the page. Recording will stop automatically.")

            time.sleep(duration_seconds)

            # Collect recorded steps
            steps = page.evaluate("window.__wardrobeSteps || []")

            browser.close()

        print(f"[RECORD] Recorded {len(steps)} steps")
        return steps

    def replay_skill(self, skill: WardrobeSkill) -> None:
        """
        Replay a recorded skill using Playwright.

        Args:
            skill: The WardrobeSkill to replay
        """
        print(f"[REPLAY] Starting replay of skill '{skill.name}'")
        print(f"[REPLAY] Backend: {skill.backend}, Steps: {len(skill.steps)}")

        with sync_playwright() as p:
            browser: Browser = p.chromium.launch(
                headless=HEADLESS,
                slow_mo=SLOW_MO
            )
            page: Page = browser.new_page()

            # Navigate to target URL if specified
            target_url = skill.meta.get("target_url")
            if target_url:
                page.goto(target_url)
                print(f"[REPLAY] Navigated to {target_url}")
            else:
                print("[REPLAY] Warning: No target_url in skill.meta")

            # Replay each step
            for i, step in enumerate(skill.steps, 1):
                action = step.get("action")
                selector = step.get("selector")

                print(f"[REPLAY] Step {i}/{len(skill.steps)}: {action} on {selector}")

                try:
                    if action == "click":
                        page.click(selector, timeout=5000)
                        print(f"  ✓ Clicked {selector}")

                    elif action == "type":
                        text = step.get("text", "")
                        page.fill(selector, text, timeout=5000)
                        print(f"  ✓ Typed '{text}' into {selector}")

                    else:
                        print(f"  ⚠ Unknown action: {action}")

                    # Small delay between actions (can be made smarter later)
                    time.sleep(0.5)

                except Exception as e:
                    print(f"  ✗ Error executing step: {e}")
                    # Continue with next step

            print(f"[REPLAY] Replay complete")

            # Keep browser open for 3 seconds to see result
            time.sleep(3)

            browser.close()


# TODO: Future enhancements
# - Better selector strategy (data-testid, aria-label priority)
# - Smart timing replay (use recorded timestamps)
# - Screenshot capture during recording
# - Validation/verification after replay
