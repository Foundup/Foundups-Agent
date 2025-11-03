#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io


from modules.infrastructure.instance_lock.src.instance_manager import get_instance_lock

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

def main():
    lock = get_instance_lock('youtube_monitor')
    summary = lock.get_instance_summary()

    print(f"[U+1F5A5]️  INSTANCE MONITORING TEST")
    print(f"Total YouTube DAE instances: {summary['total_instances']}")
    print(f"Current PID: {summary['current_pid']}")
    print()

    for instance in summary['instances']:
        status = "[U+1F3E0] CURRENT" if instance['is_current'] else "[ALERT] OTHER"
        print(f"{status} PID {instance['pid']}")
        print(f"  • Started: {instance['start_time']}")
        print(f"  • Age: {instance['age_minutes']:.1f} minutes")
        print(f"  • Python: {instance['python_type']}")
        print(f"  • Memory: {instance['memory_mb']}")
        print(f"  • CPU: {instance['cpu_percent']}")
        print()

if __name__ == "__main__":
    main()
