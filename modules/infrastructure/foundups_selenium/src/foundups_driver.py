# -*- coding: utf-8 -*-
import sys
import io


# === UTF-8 ENFORCEMENT (WSP 90) ===
# Prevent UnicodeEncodeError on Windows systems
# Only apply when running as main script, not during import
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===

#!/usr/bin/env python3
"""
FoundUps Selenium Driver
Extended Selenium WebDriver with anti-detection, vision, and platform helpers built-in.

This is a wrapper around the official Selenium driver so we inherit upstream fixes
while layering FoundUps capabilities on top.
"""

import hashlib
import os
import shutil
import time
import random
from typing import Optional, Dict, Any, Callable, List

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class FoundUpsDriver(webdriver.Chrome):
    """Extended Selenium WebDriver with FoundUps enhancements."""

    def __init__(
        self,
        vision_enabled: bool = True,
        stealth_mode: bool = True,
        profile_dir: Optional[str] = None,
        port: Optional[int] = None,
        observers: Optional[List[Callable[[str, Dict[str, Any]], None]]] = None,
        **kwargs: Any,
    ) -> None:
        """Initialise the FoundUps WebDriver with optional telemetry observers."""

        self._observers: List[Callable[[str, Dict[str, Any]], None]] = list(observers or [])

        options: ChromeOptions = kwargs.get("options", ChromeOptions())

        if stealth_mode:
            self._apply_stealth_options(options)

        if port:
            options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
            print(f"[FoundUps] connecting to existing browser on port {port}...")

        if profile_dir:
            os.makedirs(profile_dir, exist_ok=True)
            options.add_argument(f"--user-data-dir={profile_dir}")
            options.add_argument("--profile-directory=Default")
            print(f"[FoundUps] using profile: {profile_dir}")

        kwargs["options"] = options

        self._emit_event(
            "init_requested",
            {
                "vision_enabled": vision_enabled,
                "stealth_mode": stealth_mode,
                "profile_dir": profile_dir,
                "port": port,
            },
        )

        retry_error: Optional[str] = None
        used_retry = False

        try:
            super().__init__(**kwargs)
            print("[FoundUps] browser initialised with FoundUps enhancements")
        except Exception as error:
            if port:
                retry_error = str(error)
                used_retry = True
                print(f"[FoundUps] could not connect to port {port}: {error}")
                options._experimental_options.pop("debuggerAddress", None)
                kwargs["options"] = options
                self._emit_event(
                    "init_retry",
                    {
                        "port": port,
                        "error": retry_error,
                    },
                )
                super().__init__(**kwargs)
                print("[FoundUps] created new browser because port connection failed")
            else:
                raise

        if used_retry:
            self._emit_event(
                "init_retry_succeeded",
                {
                    "profile_dir": profile_dir,
                    "stealth_mode": stealth_mode,
                    "error": retry_error,
                },
            )
        else:
            self._emit_event(
                "init_succeeded",
                {
                    "port": port,
                    "profile_dir": profile_dir,
                    "stealth_mode": stealth_mode,
                },
            )

        self.vision_enabled = vision_enabled
        self.vision_analyzer = None
        if vision_enabled:
            try:
                from modules.platform_integration.social_media_orchestrator.src.gemini_vision_analyzer import (  # pylint: disable=import-error
                    GeminiVisionAnalyzer,
                )

                self.vision_analyzer = GeminiVisionAnalyzer()
                print("[FoundUps] Gemini Vision enabled")
                self._emit_event("vision_init_succeeded", {})
            except Exception as error:  # pragma: no cover - defensive
                print(f"[FoundUps] could not enable vision: {error}")
                self.vision_enabled = False
                self._emit_event(
                    "vision_init_failed",
                    {
                        "error": str(error),
                    },
                )

        if stealth_mode:
            self._apply_js_stealth()

    # Observer management -------------------------------------------------

    def register_observer(self, observer: Callable[[str, Dict[str, Any]], None]) -> None:
        """Register a telemetry observer callback."""
        if observer not in self._observers:
            self._observers.append(observer)

    def unregister_observer(self, observer: Callable[[str, Dict[str, Any]], None]) -> None:
        """Remove a telemetry observer if present."""
        if observer in self._observers:
            self._observers.remove(observer)

    def clear_observers(self) -> None:
        """Remove all registered observers."""
        self._observers.clear()

    def _emit_event(self, event: str, payload: Optional[Dict[str, Any]] = None) -> None:
        """Emit a telemetry event to registered observers."""
        if not self._observers:
            return
        data = dict(payload or {})
        for observer in list(self._observers):
            try:
                observer(event, data)
            except Exception as exc:  # pragma: no cover - keep observers best-effort
                print(f"[FoundUps] observer error: {exc}")

    # Driver configuration helpers ---------------------------------------

    def _apply_stealth_options(self, options: ChromeOptions) -> None:
        """Apply anti-detection Chrome options."""
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option(
            "excludeSwitches", ["enable-automation", "enable-logging"]
        )
        options.add_experimental_option("useAutomationExtension", False)

        options.add_argument("--disable-web-security")
        options.add_argument("--disable-features=IsolateOrigins,site-per-process")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")

        options.add_argument("--log-level=3")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--no-first-run")
        options.add_argument("--mute-audio")

        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

    def _apply_js_stealth(self) -> None:
        """Apply JavaScript anti-detection patches."""
        try:
            self.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.execute_script(
                """
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                """
            )
            self.execute_script("window.chrome = { runtime: {} };")
            print("[FoundUps] JavaScript stealth patches applied")
        except Exception:
            pass

    # Core behaviour ------------------------------------------------------

    def connect_or_create(
        self,
        port: int = 9222,
        profile_dir: Optional[str] = None,
        url: Optional[str] = None,
    ) -> bool:
        """Try to reuse an existing browser session or create a new one."""

        self._emit_event(
            "connect_or_create_requested",
            {
                "port": port,
                "profile_dir": profile_dir,
                "url": url,
            },
        )

        try:
            _ = self.current_url
            print("[FoundUps] already connected to browser")
            if url:
                self.get(url)
                self._emit_event(
                    "connect_or_create_navigated",
                    {
                        "url": url,
                    },
                )
            self._emit_event(
                "connect_or_create_reused",
                {
                    "url": url,
                },
            )
            return True
        except Exception:
            pass

        try:
            self.quit()
        except Exception:
            pass

        self.__init__(
            vision_enabled=self.vision_enabled,
            stealth_mode=True,
            profile_dir=profile_dir,
            port=port,
        )

        self._emit_event(
            "connect_or_create_reinitialized",
            {
                "port": port,
                "profile_dir": profile_dir,
            },
        )

        if url:
            self.get(url)
            self._emit_event(
                "connect_or_create_navigated",
                {
                    "url": url,
                },
            )

        return True

    def analyze_ui(
        self,
        save_screenshot: bool = False,
        screenshot_dir: str = "./screenshots",
    ) -> Dict[str, Any]:
        """Analyse the current page UI using the Gemini Vision helper."""

        if not self.vision_enabled or not self.vision_analyzer:
            self._emit_event(
                "vision_analyze_skipped",
                {
                    "reason": "vision_disabled",
                },
            )
            return {"error": "Vision not enabled"}

        self._emit_event(
            "vision_analyze_started",
            {
                "save_screenshot": save_screenshot,
            },
        )

        screenshot_bytes = self.get_screenshot_as_png()
        analysis = self.vision_analyzer.analyze_posting_ui(screenshot_bytes)

        screenshot_hash = hashlib.sha256(screenshot_bytes).hexdigest()
        analysis["screenshot_hash"] = screenshot_hash

        event_payload: Dict[str, Any] = {
            "save_screenshot": save_screenshot,
            "analysis_keys": list(analysis.keys()),
            "screenshot_hash": screenshot_hash,
        }

        if save_screenshot:
            from datetime import datetime

            os.makedirs(screenshot_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = os.path.join(screenshot_dir, f"screenshot_{timestamp}.png")
            with open(screenshot_path, "wb") as handle:
                handle.write(screenshot_bytes)
            analysis["screenshot_path"] = screenshot_path
            event_payload["screenshot_path"] = screenshot_path
            print(f"[FoundUps] screenshot saved: {screenshot_path}")

            annotated_path = self._create_annotated_screenshot(
                screenshot_path,
                analysis,
                screenshot_dir,
                timestamp,
            )
            if annotated_path:
                analysis["annotated_screenshot_path"] = annotated_path
                event_payload["annotated_screenshot_path"] = annotated_path

        self._emit_event("vision_analyze_completed", event_payload)

        return analysis

    def _create_annotated_screenshot(
        self,
        screenshot_path: str,
        analysis: Dict[str, Any],
        screenshot_dir: str,
        timestamp: str,
    ) -> Optional[str]:
        """Create a lightweight annotated copy of the latest screenshot."""

        annotated_path = os.path.join(screenshot_dir, f"screenshot_{timestamp}_annotated.png")
        summary = analysis.get("ui_state") or analysis.get("status") or "analysis"
        details = []

        if "post_button" in analysis:
            details.append(f"post:{analysis['post_button'].get('enabled')}")
        if "text_area" in analysis:
            details.append(f"text:{analysis['text_area'].get('has_text')}")
        if analysis.get("errors"):
            details.append("errors")

        label = f"UI:{summary}"
        if details:
            label = f"{label} | {'/'.join(map(str, details))}"

        try:
            from PIL import Image, ImageDraw

            image = Image.open(screenshot_path).convert("RGBA")
            overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)

            padding = 12
            text_box = [padding, padding, image.width - padding, padding + 32]
            draw.rectangle(text_box, fill=(0, 0, 0, 128))
            draw.text((padding + 4, padding + 6), label, fill=(255, 255, 255, 255))

            annotated = Image.alpha_composite(image, overlay).convert("RGB")
            annotated.save(annotated_path, format="PNG")
            return annotated_path
        except Exception:
            try:
                shutil.copyfile(screenshot_path, annotated_path)
                return annotated_path
            except Exception:
                return None

    def human_type(
        self,
        element,
        text: str,
        min_delay: float = 0.03,
        max_delay: float = 0.08,
    ) -> None:
        """Type text into an element with human-like pauses."""

        self._emit_event(
            "human_type",
            {
                "characters": len(text),
            },
        )

        element.clear()
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(min_delay, max_delay))

        time.sleep(random.uniform(0.5, 1.5))

    def random_delay(self, min_sec: float = 1.0, max_sec: float = 3.0) -> None:
        """Sleep for a small random amount of time."""

        time.sleep(random.uniform(min_sec, max_sec))

    def post_to_x(self, content: str, account: str = "foundups") -> bool:
        """Post content to X/Twitter via the existing AntiDetection helper."""

        self._emit_event(
            "post_to_x_started",
            {
                "account": account,
                "characters": len(content),
            },
        )

        from modules.platform_integration.x_twitter.src.x_anti_detection_poster import (  # pylint: disable=import-error
            AntiDetectionX,
        )

        poster = AntiDetectionX(use_foundups=(account == "foundups"))
        poster.driver = self
        result = poster.post_to_x(content)

        self._emit_event(
            "post_to_x_completed",
            {
                "account": account,
                "success": result,
            },
        )

        return result

    def post_to_linkedin(self, content: str, account: str = "default") -> bool:
        """Placeholder for LinkedIn posting (not yet implemented)."""

        print("[FoundUps] LinkedIn posting not yet implemented")
        return False

    def smart_find_element(
        self,
        selectors: List[str],
        description: str = "",
        timeout: int = 10,
        use_vision: bool = False,
    ):
        """Attempt to locate an element using multiple selectors and optional vision."""

        for selector in selectors:
            try:
                element = WebDriverWait(self, timeout).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
                if element:
                    return element
            except Exception:
                continue

        if use_vision and self.vision_enabled and description:
            print(f"[FoundUps] XPath failed, trying vision to find: {description}")
            self.analyze_ui()

        return None


def create_driver(
    browser: str = "chrome",
    vision: bool = True,
    stealth: bool = True,
    profile: Optional[str] = None,
    port: Optional[int] = None,
    observers: Optional[List[Callable[[str, Dict[str, Any]], None]]] = None,
) -> FoundUpsDriver:
    """Factory helper to create a FoundUpsDriver instance."""

    if browser.lower() != "chrome":
        print("[FoundUps] only Chrome is currently supported; defaulting to Chrome")

    return FoundUpsDriver(
        vision_enabled=vision,
        stealth_mode=stealth,
        profile_dir=profile,
        port=port,
        observers=observers,
    )


if __name__ == "__main__":
    driver = create_driver(port=9222)
    driver.get("https://x.com/home")
    driver.random_delay()
    if driver.vision_enabled:
        print(driver.analyze_ui(save_screenshot=True))
    print("[FoundUps] Browser will remain open; press Ctrl+C to exit")

