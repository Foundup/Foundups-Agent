#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io

"""
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

Test script to verify git push and post fixes
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.platform_integration.linkedin_agent.src.git_linkedin_bridge import GitLinkedInBridge

def test_git_content_generation():
    """Test the fixed content generation"""
    print("Testing Git Content Generation Fixes")
    print("=" * 50)

    bridge = GitLinkedInBridge()

    # Test commit data
    test_commit = {
        'hash': 'abcd1234',
        'subject': 'WSP compliance updates and system improvements',
        'body': '',
        'timestamp': 1640995200
    }

    # Test LinkedIn content generation
    linkedin_content = bridge.generate_linkedin_content([test_commit])
    print(f"LinkedIn Content ({len(linkedin_content)} chars):")
    print("-" * 40)
    print(linkedin_content)
    print("-" * 40)

    # Test X content generation
    x_content = bridge.generate_x_content(test_commit['subject'], 5)
    print(f"\nX Content ({len(x_content)} chars):")
    print("-" * 40)
    print(x_content)
    print("-" * 40)

    # Verify GitHub link is correct
    github_link = "https://github.com/Foundup/Foundups-Agent"
    assert github_link in linkedin_content, f"GitHub link missing from LinkedIn content: {github_link}"
    assert github_link in x_content, f"GitHub link missing from X content: {github_link}"

    # Verify content starts with 0102
    assert linkedin_content.startswith("0102:"), f"LinkedIn content doesn't start with 0102: {linkedin_content[:10]}"
    assert x_content.startswith("0102:"), f"X content doesn't start with 0102: {x_content[:10]}"

    print("\n[PASS] All tests passed!")
    print("[PASS] Content generation is working correctly")
    print("[PASS] GitHub links are correct")
    print("[PASS] Content starts with 0102 branding")

if __name__ == "__main__":
    test_git_content_generation()
