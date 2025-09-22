#!/usr/bin/env python3
"""
Automated test for git push and posting to LinkedIn + X
Runs without user interaction to test the full flow
"""

import os
import sys
import subprocess
from datetime import datetime

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
sys.path.insert(0, project_root)

print("="*60)
print("AUTOMATED GIT PUSH & POST TEST")
print("="*60)

try:
    from modules.platform_integration.linkedin_agent.src.git_linkedin_bridge import GitLinkedInBridge

    print("\n🚀 Initializing Git-LinkedIn-X Bridge...")
    bridge = GitLinkedInBridge(company_id="1263645")

    print("✅ Bridge initialized for FoundUps (1263645)")

    print("\n📋 Checking git status...")
    # Show git status
    result = subprocess.run(['git', 'status', '--short'],
                          capture_output=True, text=True)
    if result.stdout:
        print("Files to commit:")
        print(result.stdout)
    else:
        print("No changes to commit")
        print("\n⚠️ Creating a test change...")
        # Create a small test file to have something to commit
        test_file = f"test_commit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(test_file, 'w') as f:
            f.write("Test commit for FoundUps posting\n")
        print(f"Created {test_file}")

    print("\n🎯 Executing push and post...")
    print("This will:")
    print("  1. Git add all changes")
    print("  2. Git commit with FoundUps message")
    print("  3. Git push to remote")
    print("  4. Post to LinkedIn FoundUps page")
    print("  5. Post to X @Foundups account")
    print("-" * 40)

    # Execute the bridge
    success = bridge.push_and_post()

    if success:
        print("\n✅ SUCCESS - Git pushed and posted to both platforms!")
        print("Check:")
        print("  • LinkedIn: https://www.linkedin.com/company/foundups/")
        print("  • X/Twitter: https://x.com/Foundups")
    else:
        print("\n⚠️ Process completed with some issues - check logs above")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("Test complete!")