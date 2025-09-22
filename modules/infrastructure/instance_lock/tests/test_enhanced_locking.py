#!/usr/bin/env python3
"""
Test enhanced instance locking with health monitoring.
"""

import sys
import os
import time
from pathlib import Path

# Add module path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.instance_manager import get_instance_lock

def test_enhanced_locking():
    """Test the enhanced instance locking system."""
    print("🔒 Testing Enhanced Instance Locking")
    print("=" * 50)

    # Get instance lock
    lock = get_instance_lock("test_monitor")

    print("1. Testing duplicate detection...")
    duplicates = lock.check_duplicates()
    if duplicates:
        print(f"   Found {len(duplicates)} existing instances")
    else:
        print("   ✅ No existing instances")

    print("\n2. Testing lock acquisition...")
    if lock.acquire():
        print("   ✅ Lock acquired successfully")
    else:
        print("   ❌ Lock acquisition failed")
        return False

    print("\n3. Testing health monitoring...")
    health = lock.get_health_status()
    print(f"   Status: {health.get('status')}")
    print(f"   Message: {health.get('message')}")

    # Wait a bit for health updates
    print("\n4. Waiting for health updates...")
    time.sleep(2)

    health = lock.get_health_status()
    print(f"   Updated status: {health.get('status')}")
    print(f"   Updated message: {health.get('message')}")

    print("\n5. Testing lock release...")
    lock.release()
    print("   ✅ Lock released")

    print("\n6. Verifying lock cleanup...")
    if lock.lock_file.exists():
        print("   ❌ Lock file still exists")
        return False
    else:
        print("   ✅ Lock file cleaned up")

    if lock.health_file.exists():
        print("   ❌ Health file still exists")
        return False
    else:
        print("   ✅ Health file cleaned up")

    print("\n🎉 Enhanced locking test completed successfully!")
    return True

if __name__ == "__main__":
    success = test_enhanced_locking()
    sys.exit(0 if success else 1)
