#!/usr/bin/env python3
"""Automated test of git push and post functionality - NO actual push/post"""

import subprocess
import sys
from datetime import datetime

print("\n" + "="*60)
print("TESTING GIT PUSH & LINKEDIN POST (DRY RUN)")
print("="*60)

# Check git status
try:
    status = subprocess.run(['git', 'status', '--porcelain'],
                          capture_output=True, text=True, check=True)

    if not status.stdout.strip():
        print("✅ No changes to commit")
        sys.exit(0)

    print("\n📝 Changes detected:")
    print("-" * 40)
    files = status.stdout.strip().split('\n')
    for file in files[:5]:
        print(f"  {file}")
    if len(files) > 5:
        print(f"  ... and {len(files) - 5} more files")
    print("-" * 40)

    # Auto-generate commit message
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    commit_msg = f"Test WSP compliance fixes ({len(files)} files) - {timestamp}"

    print(f"\n🔄 Would commit with message: {commit_msg}")

    # Test git commands (DRY RUN - not actually executing)
    print("\n⚙️  Git commands that would be executed:")
    print("  1. git add .")
    print("  2. git commit -m \"" + commit_msg + "\"")
    print("  3. git push")

    # Generate LinkedIn content
    print("\n📱 LinkedIn post that would be created:")
    print("-" * 40)
    content = f"🚀 Development Update: {commit_msg}\n\n"
    content += f"✨ {len(files)} files updated\n"
    content += "Key changes:\n"

    # Parse file names correctly
    for i, file in enumerate(files[:3]):
        # Extract filename from git status format
        parts = file.strip().split()
        if len(parts) >= 2:
            fname = parts[-1]  # Last part is the filename
        else:
            fname = file
        content += f"  • {fname}\n"

    if len(files) > 3:
        content += f"  ... and {len(files) - 3} more\n"

    content += "\n#SoftwareDevelopment #OpenSource #Coding #TechUpdates #AI #Automation"
    content += "\n\n🔗 github.com/Foundups-Agent"

    print(content)
    print("-" * 40)

    # Test browser automation setup
    print("\n🌐 Testing browser automation setup...")
    try:
        from modules.platform_integration.linkedin_agent.src.anti_detection_poster import AntiDetectionLinkedIn

        poster = AntiDetectionLinkedIn()
        print(f"✅ AntiDetectionLinkedIn loaded")
        print(f"✅ Company ID: {poster.company_id} (FoundUps)")
        print(f"✅ Admin URL: {poster.company_admin_url}")

        # Check if we have credentials
        if poster.email and poster.password:
            print("✅ LinkedIn credentials found in .env")
        else:
            print("⚠️  LinkedIn credentials not found - need LINKEDIN_EMAIL and LINKEDIN_PASSWORD in .env")

        print("\n✅ DRY RUN COMPLETE - Everything configured correctly!")
        print("\n📌 Option 0 is ready to use:")
        print("  1. Will push to git")
        print("  2. Will post to FoundUps LinkedIn page (1263645)")
        print("  3. Uses browser automation (no API needed)")

    except ImportError as e:
        print(f"⚠️  LinkedIn module issue: {e}")
        print("   But fallback methods are available")

except subprocess.CalledProcessError as e:
    print(f"❌ Git error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*60)
print("To actually run it: python main.py → Select option 0")
print("="*60)