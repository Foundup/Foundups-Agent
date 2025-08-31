#!/usr/bin/env python3
"""
Test Git push with social media posting
Tests both LinkedIn and X/Twitter posting
"""

import subprocess
import asyncio
import sys
import os
from datetime import datetime

# Add path for imports
sys.path.insert(0, 'O:/Foundups-Agent')

def test_git_push_and_post():
    """
    Test Git push with automatic social media posting.
    """
    print("\n" + "="*60)
    print("GIT PUSH & SOCIAL MEDIA UPDATE TEST")
    print("="*60)
    
    # Check git status first
    try:
        status = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, check=True)
        
        if not status.stdout.strip():
            print("No changes to commit")
            return
        
        print("\nChanges detected:")
        print("-" * 40)
        files = status.stdout.strip().split('\n')
        for file in files[:5]:
            print(f"  {file}")
        if len(files) > 5:
            print(f"  ... and {len(files) - 5} more files")
        print("-" * 40)
        
        # Generate simple commit message
        commit_message = f"Test social media posting integration - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        print(f"\nCommit message: {commit_message}")
        
        # Get recent commits for the post
        commits_result = subprocess.run(
            ['git', 'log', '-3', '--pretty=format:%s'],
            capture_output=True, text=True, check=True
        )
        
        commit_subjects = commits_result.stdout.strip().split('\n')
        commits_data = [{'subject': subject} for subject in commit_subjects if subject]
        
        # Create event for social media posting
        event_data = {
            'commits': commits_data,
            'repository': 'Foundups-Agent',
            'wsp_refs': ['WSP 48'],  # Add WSP 48 for recursive learning
            'timestamp': datetime.now().isoformat()
        }
        
        print("\n[TEST] Testing social media posting...")
        print("Event data:", event_data)
        
        # Import and test the router
        try:
            from modules.platform_integration.social_media_orchestrator.src.multi_account_manager import SocialMediaEventRouter
            
            # Initialize router and post
            router = SocialMediaEventRouter()
            
            # Check which accounts are configured
            accounts = router.manager.get_accounts_for_event('git_push')
            print("\n[CONFIG] Accounts configured for git_push:")
            for platform, account_keys in accounts.items():
                for account_key in account_keys:
                    print(f"  - {platform}/{account_key}")
                    account = router.manager.get_account(platform, account_key)
                    if account:
                        creds = account.credentials
                        if platform == 'linkedin':
                            print(f"    Email: {creds.get('email')}")
                            print(f"    Company ID: {creds.get('company_id')}")
                        elif platform == 'x_twitter':
                            print(f"    Username: {creds.get('username')}")
            
            print("\n[POST] Attempting to post to social media...")
            results = asyncio.run(router.handle_event('git_push', event_data))
            
            # Show results
            print("\n[RESULTS] Social Media Posting Results:")
            print("-" * 40)
            for account, result in results.items():
                if isinstance(result, dict):
                    if result.get('success'):
                        print(f"  ✅ {account}: SUCCESS")
                    else:
                        print(f"  ❌ {account}: FAILED - {result.get('error', 'Unknown error')}")
                else:
                    print(f"  ⚠️  {account}: {result}")
            print("-" * 40)
            
            # Count successes
            success_count = sum(1 for r in results.values() if isinstance(r, dict) and r.get('success'))
            total_count = len(results)
            
            print(f"\n[SUMMARY] {success_count}/{total_count} accounts posted successfully")
            
            if success_count > 0:
                print("\n✅ Social media posting successful!")
                print("Check your LinkedIn and X/Twitter accounts to verify the posts")
            else:
                print("\n⚠️  No posts succeeded - check credentials and configuration")
                
        except ImportError as e:
            print(f"[ERROR] Could not import social media orchestrator: {e}")
        except Exception as e:
            print(f"[ERROR] Social media posting failed: {e}")
            import traceback
            traceback.print_exc()
            
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Git operation failed: {e}")
    except FileNotFoundError:
        print("[ERROR] Git not found. Please install Git.")

if __name__ == "__main__":
    test_git_push_and_post()