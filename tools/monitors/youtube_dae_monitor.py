#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io

"""
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

YouTube DAE Real-time Log Monitor
WSP 86: Monitoring tool for debugging and tracking DAE operations

This tool watches logs and highlights important events in real-time.
"""

import time
import json
import os
from datetime import datetime
from pathlib import Path
import sys

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class YouTubeDAEMonitor:
    def __init__(self):
        self.last_quota_check = None
        self.last_posted_stream = None
        self.monitoring = True

    def check_quota_status(self):
        """Check current quota usage"""
        try:
            quota_file = Path("memory/quota_usage.json")
            if quota_file.exists():
                with open(quota_file, 'r') as f:
                    data = json.load(f)

                for set_num, usage in data.get('sets', {}).items():
                    used = usage.get('used', 0)
                    percent = (used / 10000) * 100

                    # Color code based on usage
                    if percent >= 95:
                        status = f"[U+1F534] CRITICAL"
                    elif percent >= 80:
                        status = f"🟡 WARNING"
                    else:
                        status = f"🟢 OK"

                    print(f"Set {set_num}: {used:,}/10,000 ({percent:.1f}%) {status}")

                    if percent >= 95:
                        print(f"   [U+26A0]️ Should rotate to next set!")

        except Exception as e:
            print(f"Error reading quota: {e}")

    def check_exhausted_sets(self):
        """Check which credential sets are exhausted"""
        try:
            exhausted_file = Path("memory/exhausted_credentials.json")
            if exhausted_file.exists():
                with open(exhausted_file, 'r') as f:
                    data = json.load(f)
                    exhausted = data.get('exhausted_sets', [])

                    if exhausted:
                        print(f"[FORBIDDEN] Exhausted sets: {exhausted}")
                        next_reset = data.get('next_reset', 'Unknown')
                        print(f"   Next reset: {next_reset}")
                    else:
                        print("[OK] No exhausted credential sets")

        except Exception as e:
            print(f"Error reading exhausted sets: {e}")

    def check_posted_streams(self):
        """Check which streams have been posted"""
        try:
            posted_file = Path("memory/posted_streams.json")
            if posted_file.exists():
                with open(posted_file, 'r') as f:
                    posted = json.load(f)

                    if posted:
                        print(f"[NOTE] Posted streams: {len(posted)} total")
                        if len(posted) > 0:
                            # Show last posted
                            print(f"   Last: {posted[-1]}")
                    else:
                        print("[NOTE] No streams posted yet")

        except Exception as e:
            print(f"Error reading posted streams: {e}")

    def check_current_process(self):
        """Check if YouTube DAE is running"""
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                cmdline = proc.info.get('cmdline', [])
                if cmdline and any('auto_moderator' in str(arg) for arg in cmdline):
                    print(f"[BOT] YouTube DAE running (PID: {proc.info['pid']})")
                    return True
            print("[FAIL] YouTube DAE not detected")
            return False
        except:
            # If psutil not available, just skip
            return None

    def display_status(self):
        """Display current system status"""
        os.system('cls' if os.name == 'nt' else 'clear')

        print("="*60)
        print("[CAMERA] YouTube DAE Monitor - Real-time Status")
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)

        print("\n[DATA] QUOTA STATUS:")
        self.check_quota_status()

        print("\n[U+1F511] CREDENTIAL STATUS:")
        self.check_exhausted_sets()

        print("\n[U+1F4EE] POSTING STATUS:")
        self.check_posted_streams()

        print("\n[BOT] PROCESS STATUS:")
        self.check_current_process()

        print("\n" + "="*60)
        print("[IDEA] KEY INDICATORS TO WATCH:")
        print("• Quota approaching 95% = Should trigger rotation")
        print("• Stream detected = Should post to LinkedIn/X")
        print("• Posted streams increases = Social media working")
        print("• Exhausted sets populated = Rotation happened")
        print("\n[REFRESH] Refreshing every 5 seconds... (Ctrl+C to stop)")

    def run(self):
        """Run continuous monitoring"""
        print("Starting YouTube DAE Monitor...")
        print("This will refresh every 5 seconds to show current status")
        print("Press Ctrl+C to stop monitoring\n")

        try:
            while self.monitoring:
                self.display_status()
                time.sleep(5)
        except KeyboardInterrupt:
            print("\n\n[U+1F44B] Monitoring stopped")
            return

if __name__ == "__main__":
    monitor = YouTubeDAEMonitor()
    monitor.run()