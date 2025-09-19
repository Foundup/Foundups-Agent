#!/usr/bin/env python3
"""
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
                        status = f"🔴 CRITICAL"
                    elif percent >= 80:
                        status = f"🟡 WARNING"
                    else:
                        status = f"🟢 OK"

                    print(f"Set {set_num}: {used:,}/10,000 ({percent:.1f}%) {status}")

                    if percent >= 95:
                        print(f"   ⚠️ Should rotate to next set!")

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
                        print(f"🚫 Exhausted sets: {exhausted}")
                        next_reset = data.get('next_reset', 'Unknown')
                        print(f"   Next reset: {next_reset}")
                    else:
                        print("✅ No exhausted credential sets")

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
                        print(f"📝 Posted streams: {len(posted)} total")
                        if len(posted) > 0:
                            # Show last posted
                            print(f"   Last: {posted[-1]}")
                    else:
                        print("📝 No streams posted yet")

        except Exception as e:
            print(f"Error reading posted streams: {e}")

    def check_current_process(self):
        """Check if YouTube DAE is running"""
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                cmdline = proc.info.get('cmdline', [])
                if cmdline and any('auto_moderator' in str(arg) for arg in cmdline):
                    print(f"🤖 YouTube DAE running (PID: {proc.info['pid']})")
                    return True
            print("❌ YouTube DAE not detected")
            return False
        except:
            # If psutil not available, just skip
            return None

    def display_status(self):
        """Display current system status"""
        os.system('cls' if os.name == 'nt' else 'clear')

        print("="*60)
        print("🎥 YouTube DAE Monitor - Real-time Status")
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)

        print("\n📊 QUOTA STATUS:")
        self.check_quota_status()

        print("\n🔑 CREDENTIAL STATUS:")
        self.check_exhausted_sets()

        print("\n📮 POSTING STATUS:")
        self.check_posted_streams()

        print("\n🤖 PROCESS STATUS:")
        self.check_current_process()

        print("\n" + "="*60)
        print("💡 KEY INDICATORS TO WATCH:")
        print("• Quota approaching 95% = Should trigger rotation")
        print("• Stream detected = Should post to LinkedIn/X")
        print("• Posted streams increases = Social media working")
        print("• Exhausted sets populated = Rotation happened")
        print("\n🔄 Refreshing every 5 seconds... (Ctrl+C to stop)")

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
            print("\n\n👋 Monitoring stopped")
            return

if __name__ == "__main__":
    monitor = YouTubeDAEMonitor()
    monitor.run()