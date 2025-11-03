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

Git Social Posting Utilities
Extracted from main.py per WSP 62 Large File Refactoring Protocol

Purpose: Git push and social media posting legacy utilities
Domain: infrastructure
Module: git_social_posting

Functions:
- generate_x_content: Generate X/Twitter content (280 char limit)
- git_push_and_post: Legacy git push with social media posting
- view_git_post_history: View history of git posts to social media
"""

import json
import os
from datetime import datetime


def generate_x_content(commit_msg, file_count):
    """Generate compelling X/Twitter content (280 char limit)"""
    import random

    # Short punchy intros for X
    x_intros = [
        "[INFO] FoundUps by @UnDaoDu\n\nDAEs eating startups for breakfast.\n\n",
        "[WARN] Startups die. FoundUps are forever.\n\n",
        "[MENU] No VCs. No employees. Just you + 0102 agents.\n\n",
        "[TIP] Solo unicorns are real. Ask @UnDaoDu.\n\n",
        "[INFO] The startup killer is here.\n\n"
    ]

    content = random.choice(x_intros)

    # Add brief update
    if "fix" in commit_msg.lower():
        content += f"[INFO] {file_count} fixes by 0102 agents\n\n"
    elif "test" in commit_msg.lower():
        content += f"[INFO] Testing future: {file_count} files\n\n"
    else:
        content += f"[WARN] {file_count} autonomous updates\n\n"

    # Short CTA
    ctas = [
        "Join the revolution.",
        "Build a FoundUp.",
        "Be a solo unicorn.",
        "The future is autonomous.",
        "Startups are dead."
    ]
    content += random.choice(ctas)

    # Essential hashtags that fit
    content += "\n\n#FoundUps #DAE #SoloUnicorn @Foundups"

    # Ensure we're under 280 chars
    if len(content) > 280:
        # Trim to fit with link
        content = content[:240] + "...\n\n#FoundUps @Foundups"

    return content


def git_push_and_post():
    """
    LEGACY: Git push with automatic social media posting.
    Uses the git_linkedin_bridge module to handle posting.
    DEPRECATED: Use GitPushDAE instead for full autonomy.
    """
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    from modules.platform_integration.linkedin_agent.src.git_linkedin_bridge import GitLinkedInBridge

    print("\n" + "="*60)
    print("GIT PUSH & LINKEDIN + X POST (FoundUps)")
    print("="*60)
    print("[WARN] LEGACY MODE: Consider using GitPushDAE for full autonomy")

    # Use the git bridge module with X support
    bridge = GitLinkedInBridge(company_id="1263645")
    bridge.push_and_post()

    input("\nPress Enter to continue...")


def view_git_post_history():
    """View the history of git posts to social media."""
    print("\n" + "="*60)
    print("[INFO] GIT POST HISTORY")
    print("="*60)

    # Check posted commits
    posted_commits_file = "memory/git_posted_commits.json"
    if os.path.exists(posted_commits_file):
        try:
            with open(posted_commits_file, 'r') as f:
                posted_commits = json.load(f)
                print(f"\n[INFO]{len(posted_commits)} commits posted to social media")
                print("\nPosted commit hashes:")
                for commit in posted_commits[-10:]:  # Show last 10
                    print(f"  - {commit}")
                if len(posted_commits) > 10:
                    print(f"  ... and {len(posted_commits) - 10} more")
        except Exception as e:
            print(f"[ERROR]Error reading posted commits: {e}")
    else:
        print("[INFO] No posted commits found")

    # Check detailed log
    log_file = "memory/git_post_log.json"
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r') as f:
                log_entries = json.load(f)
                print(f"\n[INFO] Detailed posting log ({len(log_entries)} entries):")
                print("-" * 60)

                # Show last 5 entries
                for entry in log_entries[-5:]:
                    timestamp = entry.get('timestamp', 'Unknown')
                    commit_msg = entry.get('commit_msg', 'No message')[:50]
                    linkedin = "[INFO]" if entry.get('linkedin') else "[ERROR]"
                    x_twitter = "[INFO]" if entry.get('x_twitter') else "[ERROR]"
                    files = entry.get('file_count', 0)

                    print(f"\n[INFO] {timestamp[:19]}")
                    print(f"   Commit: {commit_msg}...")
                    print(f"   Files: {files}")
                    print(f"   LinkedIn: {linkedin}  X/Twitter: {x_twitter}")

                if len(log_entries) > 5:
                    print(f"\n... and {len(log_entries) - 5} more entries")

                # Stats
                total_posts = len(log_entries)
                linkedin_success = sum(1 for e in log_entries if e.get('linkedin'))
                x_success = sum(1 for e in log_entries if e.get('x_twitter'))

                print("\n[INFO] Statistics:")
                print(f"   Total posts: {total_posts}")
                print(f"   LinkedIn success rate: {linkedin_success}/{total_posts} ({linkedin_success*100//max(total_posts,1)}%)")
                print(f"   X/Twitter success rate: {x_success}/{total_posts} ({x_success*100//max(total_posts,1)}%)")

        except Exception as e:
            print(f"[ERROR]Error reading log file: {e}")
    else:
        print("\n[INFO] No posting log found")

    # Option to clear history
    print("\n" + "-"*60)
    clear = input("Clear posting history? (y/n): ").lower()
    if clear == 'y':
        try:
            if os.path.exists(posted_commits_file):
                os.remove(posted_commits_file)
                print("[INFO]Cleared posted commits")
            if os.path.exists(log_file):
                os.remove(log_file)
                print("[INFO]Cleared posting log")
            print("[INFO] History cleared - all commits can be posted again")
        except Exception as e:
            print(f"[ERROR]Error clearing history: {e}")

    input("\nPress Enter to continue...")


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 2:
        if sys.argv[1] == "history":
            view_git_post_history()
        elif sys.argv[1] == "post":
            git_push_and_post()
        else:
            print("Usage: python posting_utilities.py [history|post]")
    else:
        print("Usage: python posting_utilities.py [history|post]")
