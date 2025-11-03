#!/usr/bin/env python3
"""
Test Git push to social media posting
Tests the multi-account posting system for development updates
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===


import sys
import os
import asyncio
import subprocess
from datetime import datetime

# Add parent paths for imports
sys.path.insert(0, 'O:/Foundups-Agent')

from modules.platform_integration.social_media_orchestrator.src.multi_account_manager import (
    SocialMediaEventRouter,
    MultiAccountManager
)


def test_git_event_routing():
    """Test that git push events route to correct accounts"""
    print("Git Push Event Routing Test")
    print("=" * 60)
    
    # Initialize manager to check configuration
    manager = MultiAccountManager()
    
    # Check which accounts are configured for git_push events
    accounts = manager.get_accounts_for_event('git_push')
    
    print("\nAccounts configured for git_push events:")
    for platform, account_keys in accounts.items():
        for account_key in account_keys:
            account = manager.get_account(platform, account_key)
            if account:
                print(f"  - {platform}/{account_key}")
                print(f"    Name: {account.config.get('name', 'Unknown')}")
                print(f"    ID: {account.config.get('id', 'N/A')}")
    
    if not accounts:
        print("  [WARNING] No accounts configured for git_push events!")
        print("\n  To enable, add to config/social_accounts.yaml:")
        print("  event_routing:")
        print("    git_push:")
        print("      linkedin: ['development_updates']")
    
    return accounts


async def test_git_push_post():
    """Test posting Git updates to social media"""
    print("\n" + "=" * 60)
    print("Git Push Social Media Post Test")
    print("=" * 60)
    
    # Get recent commits from Git
    try:
        result = subprocess.run(
            ['git', 'log', '-3', '--pretty=format:%H|%s'],
            capture_output=True, text=True, check=True
        )
        
        commits = []
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split('|', 1)
                if len(parts) == 2:
                    commits.append({
                        'hash': parts[0][:7],  # Short hash
                        'subject': parts[1]
                    })
        
        if not commits:
            print("No commits found")
            return
        
        print(f"\nFound {len(commits)} recent commits:")
        for commit in commits:
            print(f"  - {commit['hash']}: {commit['subject'][:50]}")
        
    except:
        # Use test data if Git not available
        commits = [
            {'hash': 'abc123', 'subject': 'Add multi-account social media architecture'},
            {'hash': 'def456', 'subject': 'Implement WSP-compliant event routing'},
            {'hash': 'ghi789', 'subject': 'Fix X/Twitter character-by-character typing'}
        ]
        print("\nUsing test commit data (Git not available)")
    
    # Create event data
    event_data = {
        'commits': commits,
        'repository': 'Foundups-Agent',
        'timestamp': datetime.now().isoformat()
    }
    
    # Initialize router
    router = SocialMediaEventRouter()
    
    # Check configuration
    accounts = router.manager.get_accounts_for_event('git_push')
    if not accounts:
        print("\n[WARNING] No accounts configured for git_push events")
        print("Configure event_routing in social_accounts.yaml")
        return
    
    print("\nPosting to configured accounts...")
    print("-" * 40)
    
    # Handle the event
    results = await router.handle_event('git_push', event_data)
    
    # Show results
    print("\nResults:")
    for account, result in results.items():
        if isinstance(result, dict):
            if result.get('success'):
                print(f"  [OK] {account}")
            else:
                print(f"  [FAIL] {account}: {result.get('error', 'Unknown error')}")
        else:
            print(f"  [ERROR] {account}: {result}")
    
    return results


def main():
    """Run tests"""
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Test 1: Check configuration
    accounts = test_git_event_routing()
    
    if accounts:
        # Test 2: Try posting
        print("\nProceed with test post? (y/n): ", end="")
        response = input().strip().lower()
        
        if response == 'y':
            results = asyncio.run(test_git_push_post())
            
            # Summary
            success_count = sum(1 for r in results.values() 
                              if isinstance(r, dict) and r.get('success'))
            print(f"\n[SUMMARY] {success_count}/{len(results)} accounts posted successfully")
    else:
        print("\n[INFO] Configure git_push routing in social_accounts.yaml first")


if __name__ == "__main__":
    main()