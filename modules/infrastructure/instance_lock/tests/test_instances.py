#!/usr/bin/env python3

from modules.infrastructure.instance_lock.src.instance_manager import get_instance_lock

def main():
    lock = get_instance_lock('youtube_monitor')
    summary = lock.get_instance_summary()

    print(f"🖥️  INSTANCE MONITORING TEST")
    print(f"Total YouTube DAE instances: {summary['total_instances']}")
    print(f"Current PID: {summary['current_pid']}")
    print()

    for instance in summary['instances']:
        status = "🏠 CURRENT" if instance['is_current'] else "🚨 OTHER"
        print(f"{status} PID {instance['pid']}")
        print(f"  • Started: {instance['start_time']}")
        print(f"  • Age: {instance['age_minutes']:.1f} minutes")
        print(f"  • Python: {instance['python_type']}")
        print(f"  • Memory: {instance['memory_mb']}")
        print(f"  • CPU: {instance['cpu_percent']}")
        print()

if __name__ == "__main__":
    main()
