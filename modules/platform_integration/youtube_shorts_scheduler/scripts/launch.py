#!/usr/bin/env python3
"""
YouTube Shorts Scheduler - Launch Script

WSP 62 Compliance: Extracted to scripts/launch.py for main.py integration.

Usage:
    from modules.platform_integration.youtube_shorts_scheduler.scripts.launch import run_shorts_scheduler
    run_shorts_scheduler(mode="enhance")
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


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
    
    # Get channel ID
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
        from modules.platform_integration.youtube_shorts_scheduler.src.dom_automation import YouTubeStudioDOM
        from modules.platform_integration.youtube_shorts_scheduler.skills.ffcpln_title_enhance.executor import (
            FFCPLNTitleEnhanceSkill,
            SkillContext
        )
        
        # Connect to Chrome
        chrome_port = int(os.getenv("CHROME_PORT", "9222"))
        print(f"\n[CONNECT] Connecting to Chrome on port {chrome_port}...")
        
        dom = YouTubeStudioDOM(chrome_port=chrome_port)
        if not dom.connect():
            print("[ERROR] Failed to connect to Chrome. Is it running with remote debugging?")
            print("  Start Chrome with: chrome.exe --remote-debugging-port=9222")
            return
        
        print("[OK] Connected to Chrome")
        
        # Layer 1: Navigate and filter
        print("\n[LAYER 1] Navigating to unlisted shorts...")
        if not dom.navigate_to_shorts_with_filter("UNLISTED", channel_id):
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
        
        print(f"[NEW TITLE] {result.enhanced_title}")
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
        
        # Click Save button
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
            print(f"   NEW TITLE: {result.enhanced_title}")
        else:
            print("[WARN] Save button not found or disabled")
        
        if mode == "schedule":
            print("\n[LAYER 3] Scheduling not yet implemented")
            print("   TODO: Open visibility dialog → set schedule → confirm")
        
    except Exception as e:
        print(f"\n[ERROR] Shorts scheduler failed: {e}")
        logger.error(f"Shorts scheduler error: {e}", exc_info=True)


def show_shorts_scheduler_menu() -> str:
    """Display shorts scheduler submenu and return choice."""
    print("\n[MENU] YouTube Shorts Scheduler")
    print("=" * 60)
    print("== AUTOMATION ==")
    print("1. Enhance First Unlisted Short (Filter+Edit+SKILLz)")
    print("2. Enhance First (DRY RUN - preview only)")
    print("3. Schedule First Unlisted Short (Full Flow)")
    print("")
    print("== SELENIUM TESTS ==")
    print("4. [TEST] Full Chain (navigate → enhance → schedule → save)")
    print("5. [TEST] L0: Entry (navigate to unlisted, select video)")
    print("6. [TEST] L1: Filter (apply unlisted filter)")
    print("7. [TEST] L2: Edit (open edit page, find visibility)")
    print("8. [TEST] L3: Schedule (visibility → schedule → date/time → done)")
    print("")
    print("0. Back to YouTube Menu")
    print("=" * 60)
    
    return input("\nSelect option: ").strip()


def run_selenium_test(test_name: str) -> bool:
    """Run a specific Selenium layer test."""
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
    
    try:
        result = subprocess.run(cmd, cwd="o:\\Foundups-Agent")
        success = result.returncode == 0
        print(f"\n[{'OK' if success else 'FAIL'}] Test completed with code {result.returncode}")
        return success
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        return False


# CLI entry point
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="YouTube Shorts Scheduler")
    parser.add_argument("--mode", choices=["enhance", "schedule"], default="enhance")
    parser.add_argument("--channel", help="YouTube channel ID")
    parser.add_argument("--batch", action="store_true", help="Process all unlisted")
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    
    args = parser.parse_args()
    
    run_shorts_scheduler(
        mode=args.mode,
        channel_id=args.channel,
        batch=args.batch,
        dry_run=args.dry_run
    )
