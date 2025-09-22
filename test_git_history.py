#!/usr/bin/env python3
"""Test the git posting history viewing functionality"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import view_git_post_history

print("="*60)
print("TESTING GIT POST HISTORY VIEWER")
print("="*60)

# Mock a posted commits file for testing
import json

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

print("\n✅ Created test data files")
print("   - memory/git_posted_commits.json")
print("   - memory/git_post_log.json")

print("\n" + "="*60)
print("Now calling view_git_post_history()...")
print("="*60)

# Note: This will require user input for the clear history prompt
# For automated testing, we'll just show what would happen
print("\n[NOTE: The function will ask for user input]")
print("Enter 'n' when prompted to keep the test data")
print("Or enter 'y' to clear it")

# Call the function
view_git_post_history()

print("\n✅ Test complete!")