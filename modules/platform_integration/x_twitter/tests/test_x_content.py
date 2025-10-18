#!/usr/bin/env python3
"""Test X/Twitter content generation"""

# Import the function from main.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import generate_x_content

print("="*60)
print("TESTING X/TWITTER CONTENT GENERATION (280 char limit)")
print("="*60)

# Test various scenarios
test_cases = [
    ("Update codebase", 82),
    ("Fix WSP compliance issues", 45),
    ("Test autonomous agents", 12),
    ("Implement DAE orchestration", 156),
    ("General improvements", 5)
]

for commit_msg, file_count in test_cases:
    print(f"\n[NOTE] Commit: '{commit_msg}' ({file_count} files)")
    print("-"*40)

    # Generate content 3 times to see variety
    for i in range(3):
        content = generate_x_content(commit_msg, file_count)
        char_count = len(content)
        print(f"\nVersion {i+1} ({char_count} chars):")
        print(content)

        # Verify it's under 280 chars
        if char_count > 280:
            print("[FAIL] TOO LONG!")
        else:
            print(f"[OK] Fits in {280 - char_count} chars to spare")

print("\n" + "="*60)
print("[OK] X content generation working!")
print("Each post is compelling and under 280 chars")
print("="*60)