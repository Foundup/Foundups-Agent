"""
0102 Teaching System - Learning from Demonstration (LfD)

Pattern: 012 demonstrates → 0102 learns → 0102 replicates with DOM verification

Architecture:
1. TEACH MODE: 012 manually performs action while system records
2. REPLAY MODE: 0102 executes learned action with DOM verification
3. VALIDATION: DOM state changes provide ground truth

WSP Compliance:
- WSP 96: WRE Skills with pattern learning
- WSP 60: Module Memory Architecture
- WSP 48: Recursive Self-Improvement
"""

import asyncio
import json
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


@dataclass
class TeachingRecording:
    """Recording of 012's demonstration"""
    action_name: str
    timestamp: str
    duration_ms: int

    # Before state
    screenshot_before_path: str
    dom_state_before: Dict[str, Any]

    # Action
    click_coordinates: tuple  # (x, y)
    element_selector: Optional[str]

    # After state
    screenshot_after_path: str
    dom_state_after: Dict[str, Any]

    # Pattern signature (for matching)
    state_change_signature: Dict[str, Any]

    # Metadata
    teacher: str = "012"
    confidence: float = 1.0  # Human demonstration = 100% confidence


@dataclass
class DOMState:
    """DOM state snapshot for verification"""
    element_exists: bool
    aria_pressed: Optional[str]
    aria_label: Optional[str]
    classes: List[str]
    visible: bool
    text_content: Optional[str]


class TeachingSystem:
    """
    Learning from Demonstration (LfD) system

    012 demonstrates actions → 0102 learns patterns → 0102 replicates with verification
    """

    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path("modules/communication/video_comments/skillz/qwen_studio_engage/teaching_data")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.recordings: Dict[str, TeachingRecording] = {}
        self.load_recordings()

    def load_recordings(self):
        """Load existing teaching recordings"""
        recordings_file = self.storage_path / "recordings.json"
        if recordings_file.exists():
            with open(recordings_file, 'r') as f:
                data = json.load(f)
                for action_name, recording_data in data.items():
                    self.recordings[action_name] = TeachingRecording(**recording_data)
            logger.info(f"[TEACHING] Loaded {len(self.recordings)} recordings")

    def save_recording(self, recording: TeachingRecording):
        """Save teaching recording"""
        self.recordings[recording.action_name] = recording

        recordings_file = self.storage_path / "recordings.json"
        with open(recordings_file, 'w') as f:
            json.dump(
                {k: asdict(v) for k, v in self.recordings.items()},
                f,
                indent=2
            )
        logger.info(f"[TEACHING] Saved recording: {recording.action_name}")

    async def start_teaching_session(
        self,
        driver,
        action_name: str,
        element_selector: str,
        duration_seconds: int = 15
    ) -> Optional[TeachingRecording]:
        """
        Start teaching session - 012 demonstrates, system records

        Args:
            driver: Selenium WebDriver
            action_name: Name of action being taught (e.g., "like")
            element_selector: CSS selector for target element
            duration_seconds: Recording duration

        Returns:
            TeachingRecording if successful
        """
        logger.info(f"[TEACHING] Starting session: {action_name} ({duration_seconds}s)")

        # Show teaching popup
        driver.execute_script("""
            const popup = document.createElement('div');
            popup.id = 'teaching-popup';
            popup.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: #1e88e5;
                color: white;
                padding: 20px;
                border-radius: 8px;
                z-index: 999999;
                font-family: Arial;
                box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            `;
            popup.innerHTML = `
                <h3 style="margin:0 0 10px 0;">🎓 Teach 0102</h3>
                <p style="margin:0 0 10px 0;">Action: <strong>${arguments[0]}</strong></p>
                <p style="margin:0;">Recording in <span id="timer">${arguments[1]}</span>s...</p>
            `;
            document.body.appendChild(popup);

            let timeLeft = arguments[1];
            const interval = setInterval(() => {
                timeLeft--;
                const timer = document.getElementById('timer');
                if (timer) timer.textContent = timeLeft;
                if (timeLeft <= 0) clearInterval(interval);
            }, 1000);
        """, action_name, duration_seconds)

        # Capture BEFORE state
        start_time = time.time()
        screenshot_before = driver.get_screenshot_as_png()
        dom_state_before = await self._capture_dom_state(driver, element_selector)

        screenshot_before_path = self.storage_path / f"{action_name}_before_{int(start_time)}.png"
        with open(screenshot_before_path, 'wb') as f:
            f.write(screenshot_before)

        logger.info(f"[TEACHING] Recording started. 012 has {duration_seconds}s to demonstrate...")

        # Wait for 012 to perform action
        await asyncio.sleep(duration_seconds)

        # Capture AFTER state
        screenshot_after = driver.get_screenshot_as_png()
        dom_state_after = await self._capture_dom_state(driver, element_selector)

        screenshot_after_path = self.storage_path / f"{action_name}_after_{int(start_time)}.png"
        with open(screenshot_after_path, 'wb') as f:
            f.write(screenshot_after)

        # Remove popup
        driver.execute_script("""
            const popup = document.getElementById('teaching-popup');
            if (popup) popup.remove();
        """)

        duration_ms = int((time.time() - start_time) * 1000)

        # Compute state change signature (ground truth)
        state_change = self._compute_state_change(dom_state_before, dom_state_after)

        # Detect click coordinates (approximate - from mouse events if captured)
        # For now, use element's center
        click_coords = await self._get_element_center(driver, element_selector)

        recording = TeachingRecording(
            action_name=action_name,
            timestamp=datetime.now().isoformat(),
            duration_ms=duration_ms,
            screenshot_before_path=str(screenshot_before_path),
            dom_state_before=dom_state_before,
            click_coordinates=click_coords,
            element_selector=element_selector,
            screenshot_after_path=str(screenshot_after_path),
            dom_state_after=dom_state_after,
            state_change_signature=state_change
        )

        self.save_recording(recording)

        logger.info(f"[TEACHING] Recording complete: {action_name}")
        logger.info(f"[TEACHING] State change: {state_change}")

        return recording

    async def _capture_dom_state(self, driver, selector: str) -> Dict[str, Any]:
        """Capture DOM state for element"""
        state = driver.execute_script("""
            const element = document.querySelector(arguments[0]);
            if (!element) return {element_exists: false};

            return {
                element_exists: true,
                aria_pressed: element.getAttribute('aria-pressed'),
                aria_label: element.getAttribute('aria-label'),
                classes: Array.from(element.classList),
                visible: element.offsetParent !== null,
                text_content: element.textContent.trim()
            };
        """, selector)
        return state or {"element_exists": False}

    async def _get_element_center(self, driver, selector: str) -> tuple:
        """Get center coordinates of element"""
        coords = driver.execute_script("""
            const element = document.querySelector(arguments[0]);
            if (!element) return [0, 0];
            const rect = element.getBoundingClientRect();
            return [
                rect.left + rect.width / 2,
                rect.top + rect.height / 2
            ];
        """, selector)
        return tuple(coords) if coords else (0, 0)

    def _compute_state_change(self, before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Any]:
        """Compute state change signature (ground truth)"""
        changes = {}

        for key in before.keys():
            if key in after and before[key] != after[key]:
                changes[key] = {
                    "before": before[key],
                    "after": after[key],
                    "changed": True
                }

        return changes

    async def replicate_action(
        self,
        driver,
        action_name: str,
        element_selector: str,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Replicate learned action with DOM verification

        Pattern: Execute → Capture state → Compare to learned pattern → Verify

        Args:
            driver: Selenium WebDriver
            action_name: Name of learned action
            element_selector: CSS selector for target element
            max_retries: Max retry attempts

        Returns:
            Dict with success, confidence, and verification data
        """
        if action_name not in self.recordings:
            logger.error(f"[REPLAY] No recording found for: {action_name}")
            return {"success": False, "error": "No recording found"}

        recording = self.recordings[action_name]
        logger.info(f"[REPLAY] Replicating action: {action_name}")

        for attempt in range(max_retries):
            try:
                # Capture BEFORE state
                dom_state_before = await self._capture_dom_state(driver, element_selector)

                if not dom_state_before.get("element_exists"):
                    logger.warning(f"[REPLAY] Element not found: {element_selector}")
                    continue

                # Execute action (click)
                driver.execute_script("""
                    const element = document.querySelector(arguments[0]);
                    if (element) element.click();
                """, element_selector)

                # Wait for state change
                await asyncio.sleep(0.5)

                # Capture AFTER state
                dom_state_after = await self._capture_dom_state(driver, element_selector)

                # Compute state change
                actual_change = self._compute_state_change(dom_state_before, dom_state_after)

                # Compare to learned pattern
                verification_result = self._verify_state_change(
                    expected=recording.state_change_signature,
                    actual=actual_change
                )

                if verification_result["match"]:
                    logger.info(f"[REPLAY] ✓ Success! State change matches learned pattern")
                    logger.info(f"[REPLAY] Expected: {recording.state_change_signature}")
                    logger.info(f"[REPLAY] Actual: {actual_change}")

                    return {
                        "success": True,
                        "confidence": 1.0,  # DOM verification = 100% confidence
                        "attempts": attempt + 1,
                        "state_change": actual_change,
                        "verification": verification_result
                    }
                else:
                    logger.warning(f"[REPLAY] ✗ Attempt {attempt+1}/{max_retries} failed")
                    logger.warning(f"[REPLAY] Expected: {recording.state_change_signature}")
                    logger.warning(f"[REPLAY] Actual: {actual_change}")
                    logger.warning(f"[REPLAY] Mismatch: {verification_result['mismatches']}")

            except Exception as e:
                logger.error(f"[REPLAY] Attempt {attempt+1} error: {e}")
                continue

        return {
            "success": False,
            "confidence": 0.0,
            "attempts": max_retries,
            "error": "State change verification failed"
        }

    def _verify_state_change(
        self,
        expected: Dict[str, Any],
        actual: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Verify that actual state change matches expected pattern

        Returns:
            Dict with match status and details
        """
        if not expected:
            # No expected changes - any change is unexpected
            return {
                "match": len(actual) == 0,
                "mismatches": actual if actual else {}
            }

        mismatches = {}

        for key, expected_change in expected.items():
            if key not in actual:
                mismatches[key] = {
                    "expected": expected_change,
                    "actual": "no_change"
                }
            elif actual[key] != expected_change:
                mismatches[key] = {
                    "expected": expected_change,
                    "actual": actual[key]
                }

        return {
            "match": len(mismatches) == 0,
            "mismatches": mismatches
        }
