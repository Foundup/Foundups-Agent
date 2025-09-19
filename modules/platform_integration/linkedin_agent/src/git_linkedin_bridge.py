#!/usr/bin/env python3
"""
Git to LinkedIn Bridge - Post updates when pushing to Git
Shares development progress with LinkedIn audience
"""

import os
import subprocess
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
# Removed direct LinkedIn import - now using unified interface

class GitLinkedInBridge:
    """
    Bridges Git commits to LinkedIn posts.
    Detects pushes and creates engaging LinkedIn content.
    """
    
    def __init__(self, company_id: str = "1263645"):
        """
        Initialize Git-LinkedIn bridge.

        Args:
            company_id: LinkedIn company page ID (default: 1263645)
        """
        self.company_id = company_id
        # Use unified LinkedIn interface instead of direct poster
        self.commit_cache_file = "modules/platform_integration/linkedin_agent/data/posted_commits.json"
        self.posted_commits = self._load_posted_commits()
        
    def _load_posted_commits(self) -> set:
        """Load set of already posted commit hashes"""
        if os.path.exists(self.commit_cache_file):
            try:
                with open(self.commit_cache_file, 'r') as f:
                    return set(json.load(f))
            except:
                return set()
        return set()
    
    def _save_posted_commits(self):
        """Save posted commit hashes to prevent duplicates"""
        os.makedirs(os.path.dirname(self.commit_cache_file), exist_ok=True)
        with open(self.commit_cache_file, 'w') as f:
            json.dump(list(self.posted_commits), f)
    
    def get_recent_commits(self, count: int = 5) -> List[Dict]:
        """
        Get recent Git commits.
        
        Args:
            count: Number of recent commits to fetch
            
        Returns:
            List of commit information
        """
        try:
            # Get commit info using git log
            cmd = [
                'git', 'log', 
                f'-{count}',
                '--pretty=format:%H|%an|%ae|%at|%s|%b',
                '--no-merges'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            commits = []
            
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('|', 5)
                    if len(parts) >= 5:
                        commit = {
                            'hash': parts[0],
                            'author': parts[1],
                            'email': parts[2],
                            'timestamp': int(parts[3]),
                            'subject': parts[4],
                            'body': parts[5] if len(parts) > 5 else ''
                        }
                        commits.append(commit)
            
            return commits
            
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to get commits: {e}")
            return []
    
    def get_changed_files(self, commit_hash: str) -> List[str]:
        """Get list of files changed in a commit"""
        try:
            cmd = ['git', 'diff-tree', '--no-commit-id', '--name-only', '-r', commit_hash]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return [f for f in result.stdout.strip().split('\n') if f]
        except:
            return []
    
    def generate_linkedin_content(self, commits: List[Dict]) -> str:
        """
        Generate LinkedIn post content from Git commits.
        
        Args:
            commits: List of commit information
            
        Returns:
            Formatted LinkedIn post content
        """
        if not commits:
            return None
        
        # Single commit or multiple?
        if len(commits) == 1:
            commit = commits[0]
            return self._format_single_commit(commit)
        else:
            return self._format_multiple_commits(commits)
    
    def _format_single_commit(self, commit: Dict) -> str:
        """Format a single commit for LinkedIn"""
        # Get changed files
        files = self.get_changed_files(commit['hash'])
        
        # Determine the type of update
        update_type = self._categorize_commit(commit, files)
        
        # Create engaging content
        content = f"🚀 Development Update: {update_type}\n\n"
        
        # Add commit message
        content += f"✨ {commit['subject']}\n"
        
        if commit['body']:
            # Add first few lines of body if present
            body_lines = commit['body'].strip().split('\n')[:2]
            for line in body_lines:
                if line.strip():
                    content += f"   {line.strip()}\n"
        
        # Add file statistics
        if files:
            content += f"\n📝 {len(files)} file{'s' if len(files) > 1 else ''} updated\n"
            
            # Show key files (modules, not tests)
            key_files = [f for f in files if not f.startswith('test') and not f.endswith('_test.py')][:3]
            if key_files:
                content += "Key changes:\n"
                for f in key_files:
                    # Simplify path for readability
                    display_name = f.split('/')[-1] if '/' in f else f
                    content += f"  • {display_name}\n"
        
        # Add hashtags
        content += "\n#SoftwareDevelopment #OpenSource #Coding #TechUpdates #AI #Automation"
        
        # Add link to repo if available
        content += "\n\n🔗 github.com/Foundups-Agent"
        
        return content
    
    def _format_multiple_commits(self, commits: List[Dict]) -> str:
        """Format multiple commits as a batch update"""
        content = f"🚀 Development Updates - {len(commits)} New Changes\n\n"
        
        # Group commits by category
        features = []
        fixes = []
        other = []
        
        for commit in commits:
            subject = commit['subject'].lower()
            if 'feat' in subject or 'add' in subject or 'implement' in subject:
                features.append(commit)
            elif 'fix' in subject or 'bug' in subject or 'correct' in subject:
                fixes.append(commit)
            else:
                other.append(commit)
        
        # Add features
        if features:
            content += "✨ New Features:\n"
            for commit in features[:3]:
                content += f"  • {commit['subject'][:60]}\n"
        
        # Add fixes
        if fixes:
            content += "\n🔧 Bug Fixes:\n"
            for commit in fixes[:3]:
                content += f"  • {commit['subject'][:60]}\n"
        
        # Add other updates
        if other:
            content += "\n📝 Other Updates:\n"
            for commit in other[:2]:
                content += f"  • {commit['subject'][:60]}\n"
        
        # Add summary stats
        total_files = set()
        for commit in commits:
            files = self.get_changed_files(commit['hash'])
            total_files.update(files)
        
        content += f"\n📊 Impact: {len(total_files)} files updated across {len(commits)} commits\n"
        
        # Add hashtags
        content += "\n#SoftwareDevelopment #OpenSource #ContinuousImprovement #TechUpdates #Coding"
        
        return content
    
    def _categorize_commit(self, commit: Dict, files: List[str]) -> str:
        """Categorize commit type based on message and files"""
        subject = commit['subject'].lower()
        
        # Check commit message patterns
        if 'feat' in subject or 'feature' in subject:
            return "New Feature"
        elif 'fix' in subject or 'bug' in subject:
            return "Bug Fix"
        elif 'refactor' in subject:
            return "Code Refactoring"
        elif 'test' in subject:
            return "Testing Improvements"
        elif 'doc' in subject:
            return "Documentation Update"
        elif 'perf' in subject:
            return "Performance Enhancement"
        
        # Check file patterns
        if files:
            if any('test' in f for f in files):
                return "Testing Updates"
            elif any('.md' in f for f in files):
                return "Documentation"
            elif any('config' in f or '.json' in f or '.yaml' in f for f in files):
                return "Configuration Update"
        
        return "Code Enhancement"
    
    def post_recent_commits(self, count: int = 1, batch: bool = False) -> bool:
        """
        Post recent commits to LinkedIn.
        
        Args:
            count: Number of recent commits to post
            batch: If True, post as single batch update. If False, post individually.
            
        Returns:
            True if posted successfully
        """
        commits = self.get_recent_commits(count)
        
        if not commits:
            print("[INFO] No commits to post")
            return False
        
        # Filter out already posted commits
        new_commits = [c for c in commits if c['hash'] not in self.posted_commits]
        
        if not new_commits:
            print("[INFO] All recent commits already posted")
            return False
        
        # Generate content
        if batch or len(new_commits) > 3:
            # Post as batch if too many or requested
            content = self.generate_linkedin_content(new_commits)
            
            if content:
                print(f"[POST] Posting batch update for {len(new_commits)} commits...")

                # Use unified LinkedIn interface
                import asyncio
                import sys
                sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
                from modules.platform_integration.social_media_orchestrator.src.unified_linkedin_interface import post_git_commits

                # Get commit hashes for duplicate detection
                commit_hashes = [commit['hash'] for commit in new_commits]

                # Post via unified interface
                result = asyncio.run(post_git_commits(content, commit_hashes))
                success = result.success
                
                if success:
                    # Mark all as posted
                    for commit in new_commits:
                        self.posted_commits.add(commit['hash'])
                    self._save_posted_commits()
                    print("[SUCCESS] Batch update posted to LinkedIn!")
                    return True
                else:
                    print("[ERROR] Failed to post batch update")
                    return False
        else:
            # Post individually
            posted_any = False
            for commit in new_commits:
                content = self.generate_linkedin_content([commit])
                
                if content:
                    print(f"[POST] Posting commit: {commit['subject'][:50]}...")

                    # Use unified LinkedIn interface
                    import asyncio
                    result = asyncio.run(post_git_commits(content, [commit['hash']]))
                    success = result.success
                    
                    if success:
                        self.posted_commits.add(commit['hash'])
                        self._save_posted_commits()
                        posted_any = True
                        print(f"[SUCCESS] Posted: {commit['subject'][:50]}")
                        
                        # Wait between posts to avoid spam
                        if len(new_commits) > 1:
                            print("[WAIT] Waiting 30 seconds before next post...")
                            time.sleep(30)
                    else:
                        print(f"[ERROR] Failed to post: {commit['subject'][:50]}")
            
            return posted_any
        
        return False
    
    def monitor_and_post(self, check_interval: int = 300):
        """
        Monitor Git repo and post new commits.
        
        Args:
            check_interval: Seconds between checks (default 5 minutes)
        """
        print(f"[MONITOR] Starting Git-LinkedIn bridge (checking every {check_interval}s)...")
        
        while True:
            try:
                # Check for new commits
                print(f"[CHECK] Checking for new commits at {datetime.now()}")
                
                # Post recent commits (batch if more than 3)
                self.post_recent_commits(count=5, batch=False)
                
                # Wait before next check
                print(f"[WAIT] Next check in {check_interval} seconds...")
                time.sleep(check_interval)
                
            except KeyboardInterrupt:
                print("\n[STOP] Git-LinkedIn bridge stopped")
                break
            except Exception as e:
                print(f"[ERROR] Monitor error: {e}")
                time.sleep(60)  # Wait a minute on error


def test_git_linkedin():
    """Test Git to LinkedIn posting"""
    print("Git to LinkedIn Bridge Test")
    print("=" * 60)
    
    bridge = GitLinkedInBridge(company_id="1263645")
    
    # Get recent commits
    commits = bridge.get_recent_commits(3)
    
    if commits:
        print(f"Found {len(commits)} recent commits:")
        for commit in commits:
            print(f"  - {commit['subject'][:60]}")
        
        # Generate content
        content = bridge.generate_linkedin_content(commits[:1])
        print("\nGenerated LinkedIn content:")
        print("-" * 40)
        print(content)
        print("-" * 40)
        
        # Ask to post
        response = input("\nPost this to LinkedIn? (y/n): ")
        if response.lower() == 'y':
            success = bridge.post_recent_commits(count=1)
            if success:
                print("[SUCCESS] Posted to LinkedIn!")
            else:
                print("[FAILED] Could not post")
    else:
        print("No commits found")


if __name__ == "__main__":
    test_git_linkedin()