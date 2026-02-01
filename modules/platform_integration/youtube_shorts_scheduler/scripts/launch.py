#!/usr/bin/env python3
"""
YouTube Shorts Scheduler - Launch Script

WSP 62 Compliance: Extracted to scripts/launch.py for main.py integration.

Browser Port Routing:
- Chrome (9222): Move2Japan, UnDaoDu
- Edge (9223): FoundUps, RavingANTIFA

Usage:
    from modules.platform_integration.youtube_shorts_scheduler.scripts.launch import run_shorts_scheduler
    run_shorts_scheduler(mode="enhance")

    # Multi-channel rotation (Edge)
    run_multi_channel_scheduler(browser="edge", mode="schedule")
"""

import logging
from typing import Optional, List

logger = logging.getLogger(__name__)

# Browser-channel mappings for rotation
BROWSER_CHANNELS = {
    "chrome": ["move2japan", "undaodu"],
    "edge": ["foundups", "ravingantifa"],
}

BROWSER_PORTS = {
    "chrome": 9222,
    "edge": 9223,
}


# ---------------------------------------------------------------------------
# Scheduling pre-check cache
# Remembers whether a channel had unlisted videos on the previous cycle.
# If the last cycle found ZERO unlisted videos (not just "all already
# scheduled" — truly empty), skip the channel for a cooldown period to
# avoid a wasteful 30s account-swap + navigate + filter round-trip.
# ---------------------------------------------------------------------------
import json
import os
import time as _time
from pathlib import Path

_SCHEDULE_CACHE_PATH = Path(__file__).resolve().parent.parent / "memory" / "channel_schedule_cache.json"
_SKIP_COOLDOWN_SECONDS = int(os.getenv("YT_SCHEDULE_SKIP_COOLDOWN", "1800"))  # 30 min default


def _load_schedule_cache() -> dict:
    """Load the per-channel scheduling cache."""
    try:
        if _SCHEDULE_CACHE_PATH.exists():
            return json.loads(_SCHEDULE_CACHE_PATH.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def _save_schedule_cache(cache: dict) -> None:
    """Persist the per-channel scheduling cache."""
    try:
        _SCHEDULE_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        _SCHEDULE_CACHE_PATH.write_text(
            json.dumps(cache, indent=2), encoding="utf-8"
        )
    except Exception as e:
        print(f"[CACHE] Warning: could not save schedule cache: {e}")


def _should_skip_channel(channel_key: str, cache: dict) -> bool:
    """
    Return True if this channel had 0 unlisted videos on the last cycle
    AND the cooldown hasn't expired yet.

    Channels that had videos (even if all were already-scheduled "skips")
    are NEVER skipped — new uploads could appear at any time.
    """
    entry = cache.get(channel_key)
    if not entry:
        return False  # Never checked → must process

    last_unlisted = entry.get("last_unlisted_count", -1)
    last_ts = entry.get("last_checked_ts", 0)
    elapsed = _time.time() - last_ts

    if last_unlisted == 0 and elapsed < _SKIP_COOLDOWN_SECONDS:
        return True  # Empty channel, still within cooldown
    return False


def _record_channel_result(channel_key: str, cache: dict, unlisted_count: int, skipped_count: int) -> None:
    """Record this cycle's result for future pre-checks."""
    cache[channel_key] = {
        "last_unlisted_count": unlisted_count,
        "last_skipped_count": skipped_count,
        "last_checked_ts": _time.time(),
        "last_checked": __import__("datetime").datetime.now().isoformat(),
    }


def run_shorts_scheduler(
    mode: str = "enhance",
    channel_id: Optional[str] = None,
    batch: bool = False,
    dry_run: bool = False
) -> None:
    """
    Launch YouTube Shorts Scheduler.
    
    Args:
        mode: Operation mode
            - "enhance": Filter unlisted → enhance title/desc → save (Layer 1+2)
            - "schedule": Filter unlisted → enhance → schedule (Layer 1+2+3)
        channel_id: YouTube channel ID (defaults to CHANNEL_ID env var)
        batch: Process all unlisted shorts (not just first)
        dry_run: Preview changes without saving
    """
    import os
    import time
    import re

    def _ascii_safe(text: str) -> str:
        """
        0102-first console safety on Windows: avoid UnicodeEncodeError on cp932 consoles.
        Keep output machine-readable and ASCII-safe.
        """
        if text is None:
            return ""
        return str(text).encode("ascii", "backslashreplace").decode("ascii")

    def _strip_console_only_emojis(text: str) -> str:
        # Keep it simple: strip common emoji range for console display only.
        # (We still allow the actual title to contain emojis when sent to Studio.)
        return re.sub(r"[\U00010000-\U0010ffff]", "", text or "")
    
    # Get channel ID
    # 012 control: allow selecting by channel key (defaults to move2japan).
    channel_key = (os.getenv("YT_SHORTS_SCHEDULER_CHANNEL_KEY", "").strip().lower() or "")
    channel_id = channel_id or os.getenv("CHANNEL_ID", "UC-LSSlOZwpGIRIYihaz8zCw")
    
    print(f"\n[SHORTS-SCHEDULER] YouTube Shorts Scheduler")
    print("=" * 60)
    print(f"Channel: {channel_id}")
    print(f"Mode: {mode.upper()}")
    print(f"Batch: {'Yes' if batch else 'No (first only)'}")
    print(f"Dry Run: {'Yes (preview only)' if dry_run else 'No (will save)'}")
    print("=" * 60)
    
    try:
        # Import scheduler components
        import importlib
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options as ChromeOptions
        from selenium.webdriver.edge.options import Options as EdgeOptions
        # Hot-reload DOM automation for long-lived menu sessions (0102-first reliability).
        # Prevents stale in-memory imports from running outdated selector logic.
        import modules.platform_integration.youtube_shorts_scheduler.src.dom_automation as dom_automation
        dom_automation = importlib.reload(dom_automation)
        YouTubeStudioDOM = dom_automation.YouTubeStudioDOM
        from modules.platform_integration.youtube_shorts_scheduler.src.schedule_dba import record_schedule_outcome
        from modules.platform_integration.youtube_shorts_scheduler.src.channel_config import CHANNELS
        # If a channel_key was provided, map it to the channel_id for this legacy launcher flow.
        if channel_key and channel_key in CHANNELS and CHANNELS[channel_key].get("id"):
            channel_id = str(CHANNELS[channel_key]["id"])

        from modules.platform_integration.youtube_shorts_scheduler.src.schedule_tracker import ScheduleTracker
        from modules.platform_integration.youtube_shorts_scheduler.skillz.ffcpln_title_enhance.executor import (
            FFCPLNTitleEnhanceSkill,
            SkillContext
        )

        # Determine browser/port from channel_id or explicit port
        chrome_port = int(os.getenv("CHROME_PORT", "9222"))

        # Auto-detect browser from channel_id (Edge for FoundUps/RavingANTIFA)
        use_edge = False
        for cfg in CHANNELS.values():
            if cfg.get("id") == channel_id and cfg.get("chrome_port") == 9223:
                use_edge = True
                chrome_port = 9223
                break

        browser_name = "Edge" if use_edge else "Chrome"
        print(f"\n[CONNECT] Connecting to {browser_name} on port {chrome_port}...")

        try:
            if use_edge:
                options = EdgeOptions()
                options.add_experimental_option("debuggerAddress", f"127.0.0.1:{chrome_port}")
                driver = webdriver.Edge(options=options)
            else:
                options = ChromeOptions()
                options.add_experimental_option("debuggerAddress", f"127.0.0.1:{chrome_port}")
                driver = webdriver.Chrome(options=options)
        except Exception as e:
            print(f"[ERROR] Failed to connect to {browser_name}. Is it running with remote debugging?")
            print(f"  Error: {e}")
            if use_edge:
                print("  Start Edge with: msedge.exe --remote-debugging-port=9223")
            else:
                print("  Start Chrome with: chrome.exe --remote-debugging-port=9222")
            return

        dom = YouTubeStudioDOM(driver)
        print(f"[OK] Connected to {browser_name}")

        # FIX: Close extra tabs if session restore opened multiple (2026-01-18)
        # Keep only the first tab to avoid Selenium confusion
        handles = driver.window_handles
        if len(handles) > 1:
            print(f"[FIX] Closing {len(handles) - 1} extra tab(s) from session restore...")
            main_handle = handles[0]
            for handle in handles[1:]:
                driver.switch_to.window(handle)
                driver.close()
            driver.switch_to.window(main_handle)
            print(f"[OK] Now operating on single tab")

        # Resolve channel config (for scheduling slots)
        channel_cfg = None
        for cfg in CHANNELS.values():
            if cfg.get("id") == channel_id:
                channel_cfg = cfg
                break
        time_slots = (channel_cfg or {}).get("time_slots", ["5:00 AM", "11:00 AM", "5:00 PM"])
        max_per_day = int((channel_cfg or {}).get("max_per_day", 3))

        tracker = ScheduleTracker(channel_id)

        # Optional: sync scheduled count from Studio before choosing next slot (best-effort).
        # This prevents collisions when the JSON tracker is stale.
        if mode == "schedule":
            try:
                dom.navigate_to_shorts(channel_id, "SCHEDULED")
                time.sleep(2)
                scheduled_all = []
                while True:
                    scheduled_all.extend(dom.get_scheduled_videos())
                    if dom.has_next_page():
                        dom.click_next_page()
                        time.sleep(1)
                    else:
                        break
                tracker.sync_from_youtube(scheduled_all)
            except Exception:
                # Proceed with existing tracker state (degraded but functional)
                pass
        
        # Layer 1: Navigate and filter
        print("\n[LAYER 1] Navigating to unlisted shorts...")
        if not dom.navigate_to_shorts_with_fallback(channel_id, "UNLISTED"):
            print("[ERROR] Failed to apply unlisted filter")
            return
        
        print("[OK] Filtered to unlisted shorts")
        time.sleep(2)
        
        # Layer 2: Edit and enhance
        print("\n[LAYER 2] Clicking edit on first video...")
        video_id = dom.click_first_video_edit_button()
        
        if not video_id:
            print("[ERROR] Failed to open edit page")
            return
        
        print(f"[OK] Editing video: {video_id}")
        time.sleep(2)
        
        # Extract current content
        current_title = dom.get_current_title()
        current_desc = dom.get_current_description()
        
        print(f"\n[CURRENT TITLE] {current_title[:60]}..." if current_title else "[WARN] No title found")
        
        # Enhance using SKILLz
        print("\n[SKILLZ] Enhancing with FFCPLN music titles...")
        skill = FFCPLNTitleEnhanceSkill()
        result = skill.execute(SkillContext(
            original_title=current_title or "",
            original_description=current_desc or "",
            video_duration=60
        ))
        
        safe_title_for_console = _ascii_safe(_strip_console_only_emojis(result.enhanced_title))
        print(f"[NEW TITLE] {safe_title_for_console}")
        print(f"[CONFIDENCE] {result.confidence}")
        
        if dry_run:
            print("\n[DRY RUN] Preview only - no changes saved")
            return
        
        # Apply enhanced content via JavaScript
        print("\n[APPLYING] Setting new title and description...")
        
        dom.driver.execute_script(f"""
            const titleField = document.querySelector('ytcp-social-suggestions-textbox#title-textarea #textbox');
            if (titleField) {{
                titleField.innerText = "{result.enhanced_title.replace('"', '\\"')}";
                titleField.dispatchEvent(new Event('input', {{ bubbles: true }}));
            }}
            const descField = document.querySelector('ytcp-social-suggestions-textbox#description-textarea #textbox');
            if (descField) {{
                descField.innerText = `{result.enhanced_description.replace('`', '\\`')}`;
                descField.dispatchEvent(new Event('input', {{ bubbles: true }}));
            }}
        """)
        
        time.sleep(1)

        if mode == "schedule":
            # Layer 3: schedule current video (full flow)
            slot = tracker.get_next_available_slot(time_slots=time_slots, max_per_day=max_per_day)
            if not slot:
                print("[ERROR] No available schedule slots (tracker window filled)")
                return
            date_str, time_str = slot
            print(f"\n[LAYER 3] Scheduling: {date_str} @ {time_str}")
            ok = dom.schedule_video(date_str, time_str)
            if ok:
                tracker.increment(date_str, video_id=video_id)
                record_schedule_outcome(
                    channel_id=channel_id,
                    video_id=video_id,
                    date_str=date_str,
                    time_str=time_str,
                    mode="schedule",
                    success=True,
                    agent="selenium",
                    details={"launcher": "scripts/launch.py"},
                )
                print(f"\n[SUCCESS] Scheduled video {video_id} for {date_str} at {time_str}")
            else:
                record_schedule_outcome(
                    channel_id=channel_id,
                    video_id=video_id,
                    date_str=date_str,
                    time_str=time_str,
                    mode="schedule",
                    success=False,
                    agent="selenium",
                    details={"launcher": "scripts/launch.py", "error": "dom.schedule_video returned false"},
                )
                print("\n[ERROR] Schedule flow failed (see DOM logs above)")
                return
        else:
            # Enhance-only: click Save once
            print("[SAVING] Clicking Save button...")
            save_result = dom.driver.execute_script("""
                const saveBtn = document.querySelector('#save-button button, ytcp-button#save-button');
                if (saveBtn && !saveBtn.disabled) {
                    saveBtn.click();
                    return {success: true};
                }
                return {success: false};
            """)
            
            if save_result.get('success'):
                print("[OK] Save clicked! Waiting for confirmation...")
                time.sleep(3)
                print(f"\n[SUCCESS] Video {video_id} enhanced and saved!")
                print(f"   NEW TITLE: {safe_title_for_console}")
            else:
                print("[WARN] Save button not found or disabled")
        
    except Exception as e:
        print(f"\n[ERROR] Shorts scheduler failed: {e}")
        logger.error(f"Shorts scheduler error: {e}", exc_info=True)


def show_shorts_scheduler_menu() -> str:
    """
    Display the scheduler submenu and return choice.

    Occam menu design (0102-first) - SIMPLIFIED 2026-01-19:
    - ONE primary action: Schedule ALL shorts continuously
    - Dev options accessible via CLI or env vars
    """
    import os

    channel_key = os.getenv("YT_SHORTS_SCHEDULER_CHANNEL_KEY", "move2japan").strip().lower() or "move2japan"

    print("\n[MENU] YouTube Shorts Scheduler")
    print("=" * 60)
    print(f"Channel: {channel_key} (set YT_SHORTS_SCHEDULER_CHANNEL_KEY to change)")
    print("Schedules ALL unlisted shorts until complete (like comment engagement)")
    print("=" * 60)
    print("1. Schedule ALL Shorts (continuous until complete)")
    print("0. Back")
    print("=" * 60)
    print("[DEV] CLI: python -m modules.platform_integration.youtube_shorts_scheduler.scripts.launch --help")
    print("[DEV] Multi-channel: --browser chrome|edge")

    return input("\nSelect: ").strip()


def run_selenium_test(test_name: str) -> bool:
    """Run a specific Selenium layer test."""
    import os
    import subprocess
    import sys
    
    # Aligned with actual test files
    test_map = {
        "full_chain": "test_full_chain",
        "layer0": "test_layer0_entry",
        "layer1": "test_layer1_filter",
        "layer2": "test_layer2_edit",
        "layer3": "test_layer3_schedule",
    }
    
    test_module = test_map.get(test_name)
    if not test_module:
        print(f"[ERROR] Unknown test: {test_name}")
        return False
    
    print(f"\n[SELENIUM] Running {test_module}...")
    print("=" * 60)
    
    cmd = [
        sys.executable, "-m",
        f"modules.platform_integration.youtube_shorts_scheduler.tests.{test_module}",
        "--selenium"
    ]

    # If running the production-aligned full cake, allow channel/max overrides.
    if test_name == "full_chain":
        channel_key = (os.getenv("YT_SHORTS_SCHEDULER_CHANNEL_KEY", "move2japan").strip().lower() or "move2japan")
        max_videos = (os.getenv("YT_SHORTS_SCHEDULER_MAX_VIDEOS", "0").strip() or "0")  # 0 = unlimited (2026-01-28)
        cmd.extend(["--channel", channel_key, "--max", max_videos])
    
    try:
        # 0102-first: make subprocess console UTF-8 safe on Windows.
        env = os.environ.copy()
        env.setdefault("PYTHONUTF8", "1")
        env.setdefault("PYTHONIOENCODING", "utf-8")
        result = subprocess.run(cmd, cwd="o:\\Foundups-Agent", env=env)
        success = result.returncode == 0
        print(f"\n[{'OK' if success else 'FAIL'}] Test completed with code {result.returncode}")
        return success
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        return False


def run_multi_channel_scheduler(
    browser: str = "edge",
    mode: str = "schedule",
    max_per_channel: int = 9999,  # Run until complete
    dry_run: bool = False,
    stop_event: "threading.Event | None" = None,
) -> dict:
    """
    Run scheduler across multiple channels in a single browser session.

    This is the rotation pattern:
    - Chrome (9222): Move2Japan -> UnDaoDu
    - Edge (9223): FoundUps -> RavingANTIFA

    Args:
        browser: "chrome" or "edge"
        mode: "enhance" or "schedule"
        max_per_channel: Max videos to process per channel
        dry_run: Preview mode

    Returns:
        Dict with results per channel
    """
    import os
    import asyncio
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.edge.options import Options as EdgeOptions
    
    # Reuse LEGO blocks from multi_channel_coordinator (oops detection)
    from modules.communication.livechat.src.multi_channel_coordinator import (
        _is_oops_page,
        CHANNEL_FALLBACKS,
        CHANNEL_IDS,
    )
    
    # Import DAE vitals for health monitoring
    from modules.platform_integration.youtube_shorts_scheduler.src.dae_vitals import (
        DAEVitals,
    )

    # Initialize fresh LOCAL vitals for this run (thread-safe: no global singleton)
    # NOTE: When Chrome + Edge run in parallel via asyncio.gather(), each thread
    # gets its own DAEVitals instance through this local variable.
    vitals = DAEVitals()

    browser = browser.lower()
    if browser not in BROWSER_CHANNELS:
        print(f"[ERROR] Unknown browser: {browser}. Use 'chrome' or 'edge'")
        return {"error": f"Unknown browser: {browser}"}

    channels = BROWSER_CHANNELS[browser]
    port = BROWSER_PORTS[browser]

    print(f"\n[MULTI-CHANNEL] {browser.upper()} Rotation Scheduler")
    print("=" * 60)
    print(f"Browser: {browser.upper()} (port {port})")
    print(f"Channels: {' -> '.join(channels)}")
    print(f"Mode: {mode.upper()}")
    print(f"Max per channel: {max_per_channel}")
    print(f"Dry run: {dry_run}")
    print(vitals.to_dashboard())  # Show initial vitals
    print("=" * 60)

    # Connect to browser
    print(f"\n[CONNECT] Connecting to {browser.upper()} on port {port}...")
    try:
        if browser == "edge":
            options = EdgeOptions()
            options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
            driver = webdriver.Edge(options=options)
        else:
            options = ChromeOptions()
            options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
            driver = webdriver.Chrome(options=options)
        print(f"[OK] Connected to {browser.upper()}")
    except Exception as e:
        print(f"[ERROR] Failed to connect: {e}")
        return {"error": str(e)}

    # FIX: Close extra tabs if session restore opened multiple (2026-01-18)
    handles = driver.window_handles
    if len(handles) > 1:
        print(f"[FIX] Closing {len(handles) - 1} extra tab(s) from session restore...")
        main_handle = handles[0]
        for handle in handles[1:]:
            driver.switch_to.window(handle)
            driver.close()
        driver.switch_to.window(main_handle)
        print(f"[OK] Now operating on single tab")

    # Import scheduler components
    from modules.platform_integration.youtube_shorts_scheduler.src.scheduler import YouTubeShortsScheduler
    from modules.communication.video_comments.skillz.tars_account_swapper.account_swapper_skill import TarsAccountSwapper

    results = {"browser": browser, "channels": {}}

    # 2026-01-30: Load schedule cache for pre-check (skip empty channels)
    schedule_cache = _load_schedule_cache()

    # 2026-01-30: Track origin URL so we can restore the browser after scheduling.
    # Without this, the browser stays on the LAST channel processed, leaving the
    # comment engagement loop on the wrong channel.
    origin_url = None
    try:
        origin_url = driver.current_url
        print(f"[ORIGIN] Browser origin: {origin_url[:80]}...")
    except Exception:
        pass

    # Channel key → display name mapping (used in multiple places)
    _DISPLAY_NAMES = {
        "move2japan": "Move2Japan",
        "undaodu": "UnDaoDu",
        "foundups": "FoundUps",
        "ravingantifa": "RavingANTIFA",
    }

    # Process each channel with rotation
    for i, channel_key in enumerate(channels):
        # 2026-02-01: STOP SIGNAL — if caller set stop_event, abort gracefully.
        # This prevents thread leak: when Phase 3 timeout fires in the DAE loop,
        # it sets stop_event so this thread stops touching the browser.
        if stop_event is not None and stop_event.is_set():
            print(f"[STOP] ⛔ Stop signal received — aborting before {channel_key}")
            results["aborted_by_stop_signal"] = True
            break

        print(f"\n[CHANNEL {i+1}/{len(channels)}] Processing {channel_key.upper()}")
        print("-" * 40)

        # 2026-01-30: PRE-CHECK — skip channels that had 0 unlisted videos recently.
        # Avoids a 30s account-swap + navigate + filter round-trip for nothing.
        if _should_skip_channel(channel_key, schedule_cache):
            cache_entry = schedule_cache.get(channel_key, {})
            mins_ago = (_time.time() - cache_entry.get("last_checked_ts", 0)) / 60
            cooldown_mins = _SKIP_COOLDOWN_SECONDS / 60
            print(f"[SKIP] {channel_key} had 0 unlisted videos {mins_ago:.0f}m ago (cooldown: {cooldown_mins:.0f}m)")
            results["channels"][channel_key] = {
                "total_scheduled": 0, "total_errors": 0, "total_skipped": 0,
                "skipped_reason": "no_unlisted_recent", "cycle_seconds": 0,
            }
            vitals.record_channel(processed=True)
            continue

        # Switch account if not first channel
        if i > 0:
            print(f"[SWITCH] Switching to {channel_key}...")
            try:
                swapper = TarsAccountSwapper(driver)
                target_name = _DISPLAY_NAMES.get(channel_key, channel_key)

                switch_ok = asyncio.run(swapper.swap_to(target_name, navigate_to_comments=False))
                if not switch_ok:
                    print(f"[WARN] Account switch may have failed, attempting schedule anyway...")
            except Exception as e:
                print(f"[WARN] Account switch error: {e}")

        # Run scheduler for this channel
        try:
            scheduler = YouTubeShortsScheduler(channel_key, dry_run=dry_run)
            scheduler.driver = driver  # Reuse existing driver
            scheduler.dom = None  # Will be created on first use

            # Initialize DOM
            from modules.platform_integration.youtube_shorts_scheduler.src.dom_automation import YouTubeStudioDOM
            scheduler.dom = YouTubeStudioDOM(driver)
            
            # HARDENED: Check for oops page before scheduling
            if _is_oops_page(driver):
                print(f"[OOPS] 🚨 Permission error detected for {channel_key}")
                vitals.record_oops()  # Track oops event
                
                # Try fallback channel (bidirectional)
                target_name = _DISPLAY_NAMES.get(channel_key, channel_key)
                fallback_channel = CHANNEL_FALLBACKS.get(target_name)
                if fallback_channel:
                    print(f"[FALLBACK] Trying {fallback_channel}...")
                    fallback_key = fallback_channel.lower()
                    swapper = TarsAccountSwapper(driver)
                    switch_ok = asyncio.run(swapper.swap_to(fallback_channel, navigate_to_comments=False))
                    if switch_ok and not _is_oops_page(driver):
                        print(f"[FALLBACK] ✅ Switched to {fallback_channel}")
                        channel_key = fallback_key
                        vitals.record_fallback(success=True)
                    else:
                        print(f"[FALLBACK] ❌ Failed - skipping channel")
                        vitals.record_fallback(success=False)
                        vitals.record_channel(processed=False)
                        results["channels"][channel_key] = {"error": "oops_page_no_fallback"}
                        continue
                else:
                    print(f"[OOPS] No fallback available - skipping {channel_key}")
                    vitals.record_channel(processed=False)
                    results["channels"][channel_key] = {"error": "oops_page"}
                    continue

            channel_results = asyncio.run(
                scheduler.run_scheduling_cycle(max_videos=max_per_channel)
            )
            results["channels"][channel_key] = channel_results
            
            # Track vitals
            scheduled = channel_results.get('total_scheduled', 0)
            errors = channel_results.get('total_errors', 0)
            for _ in range(scheduled):
                vitals.record_op(success=True)
            for _ in range(errors):
                vitals.record_op(success=False)
            vitals.record_channel(processed=True)
            
            print(f"[OK] {channel_key}: Scheduled {scheduled}, Errors {errors}")
            print(vitals.to_dashboard())  # Show updated vitals
            vitals.emit_to_telemetry(phase=f"channel_{channel_key}")  # Store for 012 review

            # 2026-01-30: Record result for pre-check cache.
            # "unlisted_found" = total videos the scheduler saw (scheduled + skipped + errors).
            # If 0, the channel had no unlisted content at all → skip next cycle.
            unlisted_found = scheduled + errors + len(channel_results.get("skipped", []))
            _record_channel_result(channel_key, schedule_cache, unlisted_found, len(channel_results.get("skipped", [])))
            
            # AUTO-STOP: Check for critical vitals
            alert = vitals.check_and_alert()
            if alert:
                print(alert)
                print("[AUTO-STOP] 🛑 Aborting rotation due to critical vitals")
                results["abort"] = True
                results["vitals"] = vitals.to_dict()
                break

            # 2026-02-01: Check stop signal after each channel too
            if stop_event is not None and stop_event.is_set():
                print(f"[STOP] ⛔ Stop signal received after {channel_key} — stopping rotation")
                results["aborted_by_stop_signal"] = True
                break

        except Exception as e:
            print(f"[ERROR] {channel_key} failed: {e}")
            vitals.record_op(success=False)
            vitals.record_channel(processed=False)
            results["channels"][channel_key] = {"error": str(e)}

            # 2026-02-01: CONTENT PAGE FALLBACK — if per-video scheduling fails,
            # try the Content Page Scheduler (inline popup from video list table).
            cps_enabled = os.getenv("YT_CPS_FALLBACK_ENABLED", "true").lower() in ("1", "true", "yes")
            if cps_enabled and not dry_run:
                print(f"[FALLBACK] Trying Content Page Scheduler for {channel_key}...")
                try:
                    from modules.platform_integration.youtube_shorts_scheduler.src.content_page_scheduler import ContentPageScheduler
                    from modules.platform_integration.youtube_shorts_scheduler.src.schedule_tracker import ScheduleTracker

                    cps = ContentPageScheduler(driver)
                    if cps.navigate_to_content(channel_key, visibility="UNLISTED"):
                        cps_tracker = ScheduleTracker(channel_key)
                        cps_config = None
                        try:
                            from modules.platform_integration.youtube_shorts_scheduler.src.channel_config import get_channel_config
                            cps_config = get_channel_config(channel_key)
                        except Exception:
                            pass

                        cps_time_slots = (cps_config or {}).get("time_slots", [
                            "12:00 AM", "3:00 AM", "6:00 AM", "9:00 AM",
                            "12:00 PM", "3:00 PM", "6:00 PM", "9:00 PM",
                        ])
                        cps_max = min(max_per_channel, 5)  # Conservative fallback limit

                        cps_results = asyncio.run(
                            cps.schedule_all_visible(
                                tracker=cps_tracker,
                                time_slots=cps_time_slots,
                                max_per_day=8,
                                max_videos=cps_max,
                                stop_event=stop_event,
                            )
                        )

                        cps_scheduled = cps_results.get("total_scheduled", 0)
                        cps_errors = cps_results.get("total_errors", 0)
                        print(f"[FALLBACK] CPS result: {cps_scheduled} scheduled, {cps_errors} errors")

                        # Merge CPS results
                        if cps_scheduled > 0:
                            results["channels"][channel_key] = cps_results
                            results["channels"][channel_key]["method"] = "content_page_fallback"
                            for _ in range(cps_scheduled):
                                vitals.record_op(success=True)
                            vitals.record_channel(processed=True)
                    else:
                        print(f"[FALLBACK] CPS navigation failed for {channel_key}")
                except ImportError as cps_ie:
                    print(f"[FALLBACK] CPS not available: {cps_ie}")
                except Exception as cps_err:
                    print(f"[FALLBACK] CPS failed: {cps_err}")

    # Summary
    print("\n" + "=" * 60)
    print("[SUMMARY] Multi-Channel Scheduling Complete")
    print("=" * 60)
    total_scheduled = 0
    total_errors = 0
    total_skipped = 0
    total_seconds = 0.0
    for ch, res in results["channels"].items():
        scheduled = res.get("total_scheduled", 0)
        errors = res.get("total_errors", 0)
        skipped = res.get("total_skipped", 0)
        secs = res.get("cycle_seconds", 0)
        total_scheduled += scheduled
        total_errors += errors
        total_skipped += skipped
        total_seconds += secs
        status = "OK" if errors == 0 else "WARN"
        print(f"  [{status}] {ch:<15} {scheduled:>3} scheduled | {errors:>2} errors | {skipped:>2} skipped | {secs:.0f}s")
        # Show date spread per channel
        for v in res.get("scheduled", []):
            print(f"        {v.get('video_id', '?'):>12} → {v.get('date', '?')} @ {v.get('time', '?')}")
    print("-" * 60)
    print(f"  TOTAL:  {total_scheduled} scheduled | {total_errors} errors | {total_skipped} skipped | {total_seconds:.0f}s")
    if total_scheduled > 0:
        print(f"  AVG:    {total_seconds / total_scheduled:.1f}s per video")
    print(vitals.to_dashboard())  # Final vitals
    results["vitals"] = vitals.to_dict()
    results["total_scheduled"] = total_scheduled
    results["total_errors"] = total_errors
    results["total_seconds"] = round(total_seconds, 1)

    # 2026-01-30: Save schedule cache for next cycle's pre-checks
    _save_schedule_cache(schedule_cache)

    # 2026-01-30: RESTORE browser to origin URL after scheduling rotation.
    # Without this, the browser stays on the LAST channel's Studio page,
    # which confuses the next comment engagement cycle (it detects
    # the wrong channel as "active" and reorders incorrectly).
    if origin_url and len(channels) > 1:
        try:
            current_url = driver.current_url
            if current_url != origin_url:
                print(f"[RESTORE] Returning browser to origin channel...")
                driver.get(origin_url)
                import time as _restore_time
                _restore_time.sleep(3)
                print(f"[RESTORE] Browser restored to: {origin_url[:80]}...")
            else:
                print(f"[RESTORE] Browser already on origin — no restore needed")
        except Exception as restore_err:
            print(f"[RESTORE] ⚠️ Failed to restore origin: {restore_err}")

    return results


# CLI entry point
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="YouTube Shorts Scheduler")
    parser.add_argument("--mode", choices=["enhance", "schedule"], default="enhance")
    parser.add_argument("--channel", help="YouTube channel ID")
    parser.add_argument("--batch", action="store_true", help="Process all unlisted")
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    parser.add_argument("--browser", choices=["chrome", "edge"], help="Run multi-channel rotation for browser")
    parser.add_argument("--max-per-channel", type=int, default=5, help="Max videos per channel in rotation")
    # 2026-02-01: Content Page Scheduler CLI options
    parser.add_argument("--content-page", action="store_true", help="Use Content Page Scheduler (inline popup)")
    parser.add_argument("--audit", action="store_true", help="Audit calendar for conflicts/gaps (no scheduling)")
    parser.add_argument("--channel-key", help="Channel key for CPS: move2japan, undaodu, foundups, ravingantifa")

    args = parser.parse_args()

    if args.content_page or args.audit:
        # Content Page Scheduler mode
        from modules.platform_integration.youtube_shorts_scheduler.src.content_page_scheduler import (
            run_content_page_scheduler,
        )
        run_content_page_scheduler(
            browser=args.browser or "edge",
            channel_key=args.channel_key or "foundups",
            mode=args.mode,
            max_videos=args.max_per_channel,
            audit_only=args.audit,
        )
    elif args.browser:
        # Multi-channel rotation mode
        run_multi_channel_scheduler(
            browser=args.browser,
            mode=args.mode,
            max_per_channel=args.max_per_channel,
            dry_run=args.dry_run,
        )
    else:
        run_shorts_scheduler(
            mode=args.mode,
            channel_id=args.channel,
            batch=args.batch,
            dry_run=args.dry_run
        )
