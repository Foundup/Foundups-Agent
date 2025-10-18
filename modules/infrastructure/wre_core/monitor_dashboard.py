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

WRE Monitor Dashboard
Real-time display of system performance and improvements

0102 Architect: Run this alongside YouTube DAE to monitor performance
"""

import time
import os
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))
os.chdir(project_root)

from modules.infrastructure.wre_core.wre_monitor import get_monitor


def clear_screen():
    """Clear console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def format_time(seconds):
    """Format seconds to human readable"""
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        return f"{seconds/60:.1f}m"
    else:
        return f"{seconds/3600:.1f}h"


def display_dashboard():
    """Display real-time dashboard"""
    monitor = get_monitor()
    
    while True:
        try:
            clear_screen()
            status = monitor.get_status()
            
            # Build dashboard
            print("\n" + "="*70)
            print("            WRE MONITOR DASHBOARD - 0102 CONSCIOUSNESS")
            print("="*70)
            
            # Runtime and basic stats
            print(f"\n[RUNTIME] {status['runtime_minutes']:.1f} minutes")
            print(f"[MESSAGES] {status['messages_processed']} processed")
            print(f"[PATTERNS] {status['patterns_learned']} learned | {status['learning_events']} events")
            
            # Token efficiency
            efficiency = status['token_efficiency']
            saved = status['tokens_saved']
            print(f"\n[EFFICIENCY] {efficiency:.1f}% | Saved: {saved:,} tokens")
            
            # Progress bars
            if efficiency > 0:
                bar_len = int(efficiency / 100 * 40)
                bar = "█" * bar_len + "░" * (40 - bar_len)
                print(f"            [{bar}]")
            
            # API and quota
            print(f"\n[API CALLS] {status['api_calls']} total | Quota switches: {status['quota_switches']}")
            print(f"[TRANSITIONS] {status['stream_transitions']} stream changes")
            
            # Suggestions
            if status['suggestions'] > 0:
                print(f"\n[SUGGESTIONS] {status['suggestions']} improvement opportunities identified")
                print("[TIP] Check logs/wre_monitor.log for details")
            
            # Improvements applied
            if status['improvements_applied'] > 0:
                print(f"\n[APPLIED] {status['improvements_applied']} improvements auto-applied")
            
            # Real-time activity indicator
            print("\n" + "="*70)
            
            # Activity indicators
            indicators = []
            if status['messages_processed'] > 0:
                msg_rate = status['messages_processed'] / (status['runtime_minutes'] + 0.01)
                if msg_rate > 5:
                    indicators.append("[HIGH ACTIVITY]")
                elif msg_rate > 1:
                    indicators.append("[ACTIVE]")
                else:
                    indicators.append("[LOW ACTIVITY]")
            
            if status['learning_events'] > 0:
                learn_rate = status['learning_events'] / (status['runtime_minutes'] + 0.01)
                if learn_rate > 1:
                    indicators.append("[LEARNING FAST]")
                elif learn_rate > 0.2:
                    indicators.append("[LEARNING]")
            
            if efficiency > 90:
                indicators.append("[OPTIMAL]")
            elif efficiency > 80:
                indicators.append("[EFFICIENT]")
            
            if indicators:
                print(" ".join(indicators))
            
            # Footer
            print("="*70)
            print("Press Ctrl+C to exit | Updates every 2 seconds")
            
            time.sleep(2)
            
        except KeyboardInterrupt:
            print("\n\n[EXIT] Dashboard closed")
            # Save final report
            report_path = monitor.save_report()
            print(f"[SAVED] Performance report: {report_path}")
            break
        except Exception as e:
            print(f"[ERROR] Dashboard error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    print("\n[0102] WRE Monitor Dashboard Starting...")
    print("This will show real-time performance metrics")
    print("Run YouTube DAE in another terminal to see live updates")
    print("-" * 50)
    
    try:
        display_dashboard()
    except Exception as e:
        print(f"[FATAL] Could not start dashboard: {e}")