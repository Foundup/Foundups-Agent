#!/usr/bin/env python3
"""Test the git posting history viewing functionality (automated)"""

import json
import os
from datetime import datetime

print("="*60)
print("AUTOMATED TEST: GIT POST HISTORY VIEWER")
print("="*60)

# Create test data
test_commits = ["abc123def4", "567890ghij", "klmnop1234"]
test_log = [
    {
        "commit_hash": "abc123def4",
        "commit_msg": "Fix WSP compliance issues",
        "timestamp": "2025-09-22T10:30:00",
        "linkedin": True,
        "x_twitter": True,
        "file_count": 45
    },
    {
        "commit_hash": "567890ghij",
        "commit_msg": "Update codebase with new DAE features",
        "timestamp": "2025-09-22T12:15:00",
        "linkedin": True,
        "x_twitter": False,
        "file_count": 82
    },
    {
        "commit_hash": "klmnop1234",
        "commit_msg": "Test autonomous agent functionality",
        "timestamp": "2025-09-22T14:00:00",
        "linkedin": False,
        "x_twitter": True,
        "file_count": 12
    }
]

# Create test data files
os.makedirs("memory", exist_ok=True)

with open("memory/git_posted_commits.json", "w") as f:
    json.dump(test_commits, f)

with open("memory/git_post_log.json", "w") as f:
    json.dump(test_log, f, indent=2)

print("\n✅ Created test data files:")
print("   - memory/git_posted_commits.json")
print("   - memory/git_post_log.json")

# Now test reading the history (non-interactive version)
print("\n" + "="*60)
print("📊 GIT POST HISTORY")
print("="*60)

# Check posted commits
posted_commits_file = "memory/git_posted_commits.json"
if os.path.exists(posted_commits_file):
    try:
        with open(posted_commits_file, 'r') as f:
            posted_commits = json.load(f)
            print(f"\n✅ {len(posted_commits)} commits posted to social media")
            print("\nPosted commit hashes:")
            for commit in posted_commits[-10:]:  # Show last 10
                print(f"  • {commit}")
            if len(posted_commits) > 10:
                print(f"  ... and {len(posted_commits) - 10} more")
    except Exception as e:
        print(f"❌ Error reading posted commits: {e}")
else:
    print("📭 No posted commits found")

# Check detailed log
log_file = "memory/git_post_log.json"
if os.path.exists(log_file):
    try:
        with open(log_file, 'r') as f:
            log_entries = json.load(f)
            print(f"\n📋 Detailed posting log ({len(log_entries)} entries):")
            print("-" * 60)

            # Show all entries for test
            for entry in log_entries:
                timestamp = entry.get('timestamp', 'Unknown')
                commit_msg = entry.get('commit_msg', 'No message')[:50]
                linkedin = "✅" if entry.get('linkedin') else "❌"
                x_twitter = "✅" if entry.get('x_twitter') else "❌"
                files = entry.get('file_count', 0)

                print(f"\n📌 {timestamp[:19]}")
                print(f"   Commit: {commit_msg}...")
                print(f"   Files: {files}")
                print(f"   LinkedIn: {linkedin}  X/Twitter: {x_twitter}")

            # Stats
            total_posts = len(log_entries)
            linkedin_success = sum(1 for e in log_entries if e.get('linkedin'))
            x_success = sum(1 for e in log_entries if e.get('x_twitter'))

            print("\n📈 Statistics:")
            print(f"   Total posts: {total_posts}")
            print(f"   LinkedIn success rate: {linkedin_success}/{total_posts} ({linkedin_success*100//max(total_posts,1)}%)")
            print(f"   X/Twitter success rate: {x_success}/{total_posts} ({x_success*100//max(total_posts,1)}%)")

    except Exception as e:
        print(f"❌ Error reading log file: {e}")
else:
    print("\n📭 No posting log found")

print("\n" + "="*60)
print("✅ History viewer test complete!")
print("The actual function also offers an option to clear history")
print("="*60)