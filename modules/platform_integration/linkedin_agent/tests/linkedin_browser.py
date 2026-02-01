"""
LinkedIn Selenium browser helpers for layer tests.

Provides:
- get_linkedin_driver(): open or attach to browser
- ensure_linkedin_logged_in(): navigate to LinkedIn and wait for login

WSP:
- WSP 50: Pre-action verification
- WSP 91: Observability (structured prints)
"""
from __future__ import annotations

import os
import time
import asyncio
from typing import Optional
import json
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError


def _log(event: str, message: str) -> None:
    print(f"[{event}] {message}")


def get_linkedin_driver():
    """
    Get a Selenium driver for LinkedIn tests.

    Strategy:
    1) If LINKEDIN_USE_DEBUG_PORT=true, attach to existing Chrome (CHROME_PORT).
    2) Otherwise, open a managed Chrome profile via BrowserManager.
    """
    use_debug_port = os.getenv("LINKEDIN_USE_DEBUG_PORT", "true").lower() in {"1", "true", "yes"}
    if use_debug_port:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options

        chrome_port = int(os.getenv("CHROME_PORT", "9222"))
        _log("CONNECT", f"Chrome debug port {chrome_port}")

        options = Options()
        options.add_experimental_option("debuggerAddress", f"localhost:{chrome_port}")
        return webdriver.Chrome(options=options)

    from modules.infrastructure.foundups_selenium.src.browser_manager import get_browser_manager

    profile_name = os.getenv("LINKEDIN_PROFILE", "youtube_undaodu")
    if "LINKEDIN_PROFILE" not in os.environ:
        _log(
            "WARNING",
            "LINKEDIN_PROFILE not set, using YouTube profile: "
            f"{profile_name} (shared with UnDaoDu/Move2Japan)",
        )

    browser_manager = get_browser_manager()
    return browser_manager.get_browser("chrome", profile_name, dae_name="linkedin_digital_twin_tests")


def _warm_up_ui_tars_model(base_url: str, model_name: str, timeout_seconds: int = 15) -> bool:
    """Trigger LM Studio to load UI-TARS model via a minimal completion."""
    try:
        warmup_url = f"{base_url}/v1/chat/completions"
        payload = json.dumps({
            "model": model_name,
            "messages": [{"role": "user", "content": "warmup"}],
            "max_tokens": 1,
            "temperature": 0.0,
        }).encode("utf-8")
        req = Request(
            warmup_url,
            data=payload,
            headers={"User-Agent": "FoundUps-Agent", "Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(req, timeout=timeout_seconds) as resp:
            return 200 <= resp.status < 300
    except Exception as exc:
        _log("WARNING", f"UI-TARS warmup failed: {exc}")
        return False


def check_lm_studio_ready(timeout_seconds: int = 2) -> bool:
    """
    Check LM Studio / UI-TARS endpoint availability.

    Uses TARS_API_URL (default http://127.0.0.1:1234).
    """
    auto_launch = os.getenv("LINKEDIN_LAUNCH_LM_STUDIO", "true").lower() in {"1", "true", "yes"}
    base_url = os.getenv("TARS_API_URL", "http://127.0.0.1:1234").rstrip("/")
    if base_url.endswith("/v1"):
        base_url = base_url[:-3]
    models_url = f"{base_url}/v1/models"
    ui_tars_model = os.getenv("UI_TARS_MODEL", "ui-tars-1.5-7b")
    require_ui_tars_model = os.getenv("LINKEDIN_REQUIRE_UI_TARS_MODEL", "true").lower() in {"1", "true", "yes"}
    auto_load_model = os.getenv("LINKEDIN_AUTO_LOAD_UI_TARS_MODEL", "true").lower() in {"1", "true", "yes"}

    _log("PRECHECK", f"LM Studio: {models_url}")
    try:
        req = Request(models_url, headers={"User-Agent": "FoundUps-Agent"})
        with urlopen(req, timeout=timeout_seconds) as resp:
            if 200 <= resp.status < 300:
                payload = json.loads(resp.read().decode("utf-8"))
                models = payload.get("data", []) if isinstance(payload, dict) else []
                model_ids = {m.get("id") for m in models if isinstance(m, dict)}
                _log("OK", "LM Studio reachable")
                if ui_tars_model not in model_ids:
                    _log("WARNING", f"UI-TARS model not loaded: {ui_tars_model}")
                    if auto_load_model:
                        _log("PRECHECK", f"Attempting UI-TARS warmup: {ui_tars_model}")
                        if _warm_up_ui_tars_model(base_url, ui_tars_model):
                            _log("OK", f"UI-TARS model loaded after warmup: {ui_tars_model}")
                            return True
                    return not require_ui_tars_model
                _log("OK", f"UI-TARS model loaded: {ui_tars_model}")
                return True
    except (HTTPError, URLError, OSError) as exc:
        _log("WARNING", f"LM Studio not reachable: {exc}")
        if auto_launch:
            try:
                from modules.infrastructure.dependency_launcher.src.dae_dependencies import (
                    launch_lm_studio,
                    is_lm_studio_running,
                )
                _log("PRECHECK", "Attempting LM Studio launch...")
                launched, msg = launch_lm_studio()
                _log("PRECHECK", msg)
                if launched and is_lm_studio_running():
                    _log("OK", "LM Studio reachable after launch")
                    return True
            except Exception as launch_exc:
                _log("WARNING", f"LM Studio launch failed: {launch_exc}")
        return False

    _log("WARNING", "LM Studio not reachable (unexpected response)")
    return False


def ensure_linkedin_logged_in(driver, timeout_seconds: int = 120) -> bool:
    """
    Navigate to LinkedIn feed and wait for login state.

    Returns True if logged in, False if timeout.
    """
    feed_url = os.getenv("LINKEDIN_FEED_URL", "https://www.linkedin.com/feed/")
    _log("NAV", f"LinkedIn feed: {feed_url}")
    try:
        driver.get(feed_url)
    except Exception as exc:
        _log("ERROR", f"Navigation failed: {exc}")
        return False

    use_ui_tars = os.getenv("LINKEDIN_USE_UI_TARS", "true").lower() in {"1", "true", "yes"}
    require_ui_tars = os.getenv("LINKEDIN_REQUIRE_UI_TARS", "false").lower() in {"1", "true", "yes"}
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        current_url = driver.current_url.lower()
        if "linkedin.com" not in current_url:
            _log("WARNING", f"Not on LinkedIn yet: {current_url}")
            time.sleep(2)
            continue

        # Detect login or checkpoint pages
        if "login" in current_url or "checkpoint" in current_url:
            _log("LOGIN", "LinkedIn login required - complete login in the browser.")
            time.sleep(3)
            continue

        # Basic DOM check for feed
        try:
            driver.find_element("css selector", "div#voyager-feed")
            _log("OK", "LinkedIn session active")
            return True
        except Exception:
            # Allow time for page to finish loading
            time.sleep(2)

        # UI-TARS verification fallback (visual)
        if use_ui_tars:
            try:
                from modules.infrastructure.foundups_vision.src.ui_tars_bridge import UITarsBridge

                async def _verify():
                    bridge = UITarsBridge(browser_port=int(os.getenv("CHROME_PORT", "9222")))
                    return await bridge.verify(
                        "LinkedIn feed is visible with posts list (not a login page)",
                        driver=driver,
                    )

                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    loop = None
                if loop and loop.is_running():
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as pool:
                        result = pool.submit(asyncio.run, _verify()).result(timeout=30)
                else:
                    result = asyncio.run(_verify())

                if result and result.success:
                    _log("OK", "LinkedIn session active (UI-TARS verified)")
                    return True
            except Exception as exc:
                if require_ui_tars:
                    _log("ERROR", f"UI-TARS verification failed: {exc}")
                    return False

    _log("ERROR", "Login timeout - LinkedIn session not confirmed")
    return False
