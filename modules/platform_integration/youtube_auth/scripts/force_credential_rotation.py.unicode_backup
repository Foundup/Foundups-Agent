#!/usr/bin/env python3
"""
Force credential rotation to Set 10 when Set 1 is near exhaustion.
WSP 86: Emergency credential rotation script

Usage: python force_credential_rotation.py
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
# === END UTF-8 ENFORCEMENT ===


import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

def force_rotation_to_set_10():
    """Force mark Set 1 as exhausted to trigger rotation to Set 10"""

    print("="*60)
    print("🔄 FORCING CREDENTIAL ROTATION")
    print("="*60)

    # Check current quota usage
    quota_file = Path("memory/quota_usage.json")
    if quota_file.exists():
        with open(quota_file, 'r', encoding="utf-8") as f:
            quota_data = json.load(f)
            if "sets" in quota_data and "1" in quota_data["sets"]:
                used = quota_data["sets"]["1"]["used"]
                print(f"📊 Set 1 Usage: {used}/10000 ({used/100:.1f}%)")

    # Mark Set 1 as exhausted
    exhausted_file = Path("memory/exhausted_credentials.json")

    if exhausted_file.exists():
        with open(exhausted_file, 'r', encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {"exhausted_sets": [], "last_reset": None, "next_reset": None}

    if 1 not in data["exhausted_sets"]:
        data["exhausted_sets"].append(1)
        print("✅ Marked Set 1 as exhausted")
    else:
        print("ℹ️ Set 1 already marked as exhausted")

    # Calculate next midnight PT for reset
    from datetime import datetime, timedelta
    import pytz

    try:
        pt_tz = pytz.timezone('America/Los_Angeles')
        now_pt = datetime.now(pt_tz)

        # Calculate next midnight PT
        tomorrow = now_pt.date() + timedelta(days=1)
        next_midnight_pt = pt_tz.localize(
            datetime.combine(tomorrow, datetime.min.time())
        )

        data["next_reset"] = next_midnight_pt.isoformat()
        print(f"📅 Next reset: {next_midnight_pt.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    except ImportError:
        # Fallback without pytz
        from datetime import timezone
        utc_minus_8 = timezone(timedelta(hours=-8))
        now_pt = datetime.now(utc_minus_8)
        tomorrow = now_pt.date() + timedelta(days=1)
        next_midnight_pt = datetime.combine(tomorrow, datetime.min.time()).replace(tzinfo=utc_minus_8)
        data["next_reset"] = next_midnight_pt.isoformat()
        print(f"📅 Next reset (UTC-8): {next_midnight_pt.strftime('%Y-%m-%d %H:%M:%S')}")

    # Save the updated exhausted credentials
    with open(exhausted_file, 'w', encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print("💾 Saved exhausted credentials status")
    print("\n🎯 NEXT STEPS:")
    print("1. Restart the YouTube DAE")
    print("2. It will now use Set 10 (FoundUps credentials)")
    print("3. Set 1 will be available again after midnight PT")
    print("="*60)

if __name__ == "__main__":
    force_rotation_to_set_10()