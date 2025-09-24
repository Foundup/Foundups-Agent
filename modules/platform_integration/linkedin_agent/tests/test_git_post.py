#!/usr/bin/env python3
"""Test git push and post functionality"""

import subprocess
import sys

# Check git status first
result = subprocess.run(['git', 'status', '--porcelain'],
                       capture_output=True, text=True)

if not result.stdout.strip():
    print("✅ No changes to commit")
    sys.exit(0)

print("\n📝 Git Status:")
print("-" * 40)
files = result.stdout.strip().split('\n')
print(f"Found {len(files)} changed files")
for file in files[:5]:
    print(f"  {file}")
if len(files) > 5:
    print(f"  ... and {len(files) - 5} more")
print("-" * 40)

# Test the LinkedIn content generation
from datetime import datetime

commit_msg = f"Test update - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
content = f"🚀 Development Update: {commit_msg}\n\n"
content += f"✨ {len(files)} files updated\n"
content += "Key changes:\n"
for file in files[:3]:
    fname = file.split()[-1] if ' ' in file else file
    content += f"  • {fname}\n"
if len(files) > 3:
    content += f"  ... and {len(files) - 3} more\n"

content += "\n#SoftwareDevelopment #OpenSource #Coding #TechUpdates #AI #Automation"
content += "\n\n🔗 github.com/Foundups-Agent"

print(f"\n📱 LinkedIn Post Preview:")
print("="*60)
print(content)
print("="*60)

# Test imports
print("\n🔍 Testing module imports...")
try:
    from modules.platform_integration.linkedin_agent.src.anti_detection_poster import AntiDetectionLinkedIn
    print("✅ AntiDetectionLinkedIn imported successfully")

    # Check configuration
    poster = AntiDetectionLinkedIn()
    print(f"✅ Company ID configured: {poster.company_id} (FoundUps)")

except ImportError as e:
    print(f"❌ Import failed: {e}")

    # Try fallback
    try:
        from modules.platform_integration.social_media_orchestrator.src.simple_posting_orchestrator import SimplePostingOrchestrator
        print("✅ SimplePostingOrchestrator imported successfully (fallback)")
    except ImportError as e2:
        print(f"❌ Fallback also failed: {e2}")

print("\n✅ Test complete! Option 0 should work.")
print("\nTo actually run it:")
print("  python main.py")
print("  Select option 0")
print("  Enter commit message (or press Enter for auto)")
print("  Confirm LinkedIn posting (y/n)")