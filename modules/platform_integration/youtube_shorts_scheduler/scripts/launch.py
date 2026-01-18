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

    Occam menu design (0102-first):
    - Numeric-only choices (avoid letter-coded "dev" affordances in the 012 path).
    - Expose only stable production actions.
    - Keep tests in `tests/` and in the CLI, not in the 012-facing menu surface.
    - “Videos” remains a placeholder until DOM selectors are implemented (next layer).
    """
    import os

    content_type = os.getenv("YT_SCHEDULER_CONTENT_TYPE", "shorts").strip().lower() or "shorts"
    channel_key = os.getenv("YT_SHORTS_SCHEDULER_CHANNEL_KEY", "move2japan").strip().lower() or "move2japan"

    print("\n[MENU] YouTube Scheduler (PoC: Shorts)")
    print("=" * 60)
    print(f"Mode: content_type={content_type} | channel={channel_key}")
    print("Controls: main.py → YouTube Controls → Scheduler Controls")

    print("\n== SHORTS (PRODUCTION) ==")
    print("1. Schedule NEXT unlisted Short (full cake)")
    print("2. Schedule ALL unlisted Shorts (until empty; safety stops on no slots)")
    print("3. DRY RUN: Preview NEXT Short (no save)")

    print("\n== MULTI-CHANNEL (BROWSER-GROUPED) ==")
    print("4. Chrome rotation (Move2Japan ↔ UnDaoDu)")
    print("5. Edge rotation (FoundUps ↔ RavingANTIFA)")

    print("\n== INDEXING ==")
    print("6. Index ALL videos (handoff → YouTube DAEs menu → [INDEX])")

    print("\n== FULL VIDEOS (FUTURE LAYER) ==")
    print("7. Schedule NEXT unlisted Video [placeholder]")

    print("\n0. Back")
    print("=" * 60)

    return input("\nSelect option: ").strip()


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
        max_videos = (os.getenv("YT_SHORTS_SCHEDULER_MAX_VIDEOS", "1").strip() or "1")
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
        reset_dae_vitals,
    )
    
    # Initialize fresh vitals for this run
    vitals = reset_dae_vitals()

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

    # Process each channel with rotation
    for i, channel_key in enumerate(channels):
        print(f"\n[CHANNEL {i+1}/{len(channels)}] Processing {channel_key.upper()}")
        print("-" * 40)

        # Switch account if not first channel
        if i > 0:
            print(f"[SWITCH] Switching to {channel_key}...")
            try:
                swapper = TarsAccountSwapper(driver)
                # Map channel_key to swapper target name
                target_name = {
                    "move2japan": "Move2Japan",
                    "undaodu": "UnDaoDu",
                    "foundups": "FoundUps",
                    "ravingantifa": "RavingANTIFA",
                }.get(channel_key, channel_key)

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
                target_name = {
                    "move2japan": "Move2Japan",
                    "undaodu": "UnDaoDu",
                    "foundups": "FoundUps",
                    "ravingantifa": "RavingANTIFA",
                }.get(channel_key, channel_key)
                
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
            
            # AUTO-STOP: Check for critical vitals
            alert = vitals.check_and_alert()
            if alert:
                print(alert)
                print("[AUTO-STOP] 🛑 Aborting rotation due to critical vitals")
                results["abort"] = True
                results["vitals"] = vitals.to_dict()
                break

        except Exception as e:
            print(f"[ERROR] {channel_key} failed: {e}")
            vitals.record_op(success=False)
            vitals.record_channel(processed=False)
            results["channels"][channel_key] = {"error": str(e)}

    # Summary
    print("\n" + "=" * 60)
    print("[SUMMARY] Multi-Channel Scheduling Complete")
    print("=" * 60)
    total_scheduled = 0
    total_errors = 0
    for ch, res in results["channels"].items():
        scheduled = res.get("total_scheduled", 0)
        errors = res.get("total_errors", 0)
        total_scheduled += scheduled
        total_errors += errors
        print(f"  {ch}: {scheduled} scheduled, {errors} errors")
    print(f"  TOTAL: {total_scheduled} scheduled, {total_errors} errors")
    print(vitals.to_dashboard())  # Final vitals
    results["vitals"] = vitals.to_dict()

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

    args = parser.parse_args()

    if args.browser:
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
