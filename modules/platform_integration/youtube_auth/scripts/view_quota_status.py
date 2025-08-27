#!/usr/bin/env python3
"""
View YouTube API Quota Status
Shows current quota usage across all credential sets
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

from modules.platform_integration.youtube_auth.src.quota_monitor import QuotaMonitor
import json

def main():
    """Display quota status."""
    monitor = QuotaMonitor()
    
    # Get and display report
    print(monitor.generate_report())
    
    # Get best credential set
    best = monitor.get_best_credential_set()
    if best:
        print(f"\n📊 Recommended credential set: {best}")
        
        # Show operations remaining for common tasks
        operations = [
            'liveChatMessages.list',
            'liveChatMessages.insert',
            'channels.list',
            'search.list'
        ]
        
        print(f"\nOperations remaining for set {best}:")
        for op in operations:
            remaining = monitor.estimate_operations_remaining(best, op)
            print(f"  {op}: {remaining:,} calls")
    else:
        print("\n⚠️ All credential sets are low on quota!")
    
    # Show summary in JSON for programmatic access
    if '--json' in sys.argv:
        summary = monitor.get_usage_summary()
        print("\nJSON Summary:")
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()