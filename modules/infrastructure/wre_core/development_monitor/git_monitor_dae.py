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

WRE Development Monitor DAE - WSP-compliant Git activity monitoring
Posts development updates to LinkedIn when code is pushed
Part of the WRE infrastructure for recursive improvement tracking
"""

import os
import sys
import subprocess
import json
import time
from datetime import datetime
from typing import Dict, List, Optional

# Add parent paths for imports
sys.path.insert(0, 'O:/Foundups-Agent')
# Removed direct LinkedIn import - now using unified interface

class DevelopmentMonitorDAE:
    """
    WSP-compliant DAE for monitoring development activity.
    Posts Git updates to LinkedIn company pages.
    Part of WRE recursive improvement system.
    """
    
    # Company pages configuration
    COMPANY_PAGES = {
        'foundups': {
            'id': '104834798',
            'name': 'FoundUps',
            'post_frequency': 'immediate'  # Post live streams immediately
        },
        'development': {
            'id': '1263645',
            'name': 'Development Updates',
            'post_frequency': 'batch'  # Batch Git commits
        }
    }
    
    def __init__(self):
        """Initialize Development Monitor DAE per WSP protocols"""
        # Use unified LinkedIn interface instead of direct poster
        self.memory_dir = "modules/infrastructure/wre_core/development_monitor/memory"
        self.posted_commits_file = f"{self.memory_dir}/posted_commits.json"
        self.posted_commits = self._load_memory()
        
        # Create memory directory if needed
        os.makedirs(self.memory_dir, exist_ok=True)
        
        print("[DAE] Development Monitor initialized (WSP-compliant)")
    
    def _load_memory(self) -> Dict:
        """Load DAE memory per WSP 60 (Three-state architecture)"""
        if os.path.exists(self.posted_commits_file):
            try:
                with open(self.posted_commits_file, 'r') as f:
                    return json.load(f)
            except:
                return {'commits': set(), 'last_check': None}
        return {'commits': set(), 'last_check': None}
    
    def _save_memory(self):
        """Save DAE memory per WSP 60"""
        memory = {
            'commits': list(self.posted_commits.get('commits', set())),
            'last_check': datetime.now().isoformat()
        }
        with open(self.posted_commits_file, 'w') as f:
            json.dump(memory, f, indent=2)
    
    def get_recent_commits(self, count: int = 10) -> List[Dict]:
        """Get recent Git commits per WSP 48 (Recursive improvement tracking)"""
        try:
            # Get commit info with full details
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
                        
                        # Check for WSP references
                        commit['wsp_refs'] = self._extract_wsp_references(
                            commit['subject'] + ' ' + commit.get('body', '')
                        )
                        
                        commits.append(commit)
            
            return commits
            
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to get commits: {e}")
            return []
    
    def _extract_wsp_references(self, text: str) -> List[str]:
        """Extract WSP protocol references from commit messages"""
        import re
        pattern = r'WSP[\s-]?(\d{1,2})'
        matches = re.findall(pattern, text, re.IGNORECASE)
        return [f"WSP {m}" for m in matches]
    
    def get_changed_modules(self, commit_hash: str) -> Dict:
        """Analyze which modules were changed per WSP 3 (Module organization)"""
        try:
            cmd = ['git', 'diff-tree', '--no-commit-id', '--name-only', '-r', commit_hash]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            files = result.stdout.strip().split('\n')
            
            # Categorize by module
            modules = {
                'infrastructure': [],
                'platform_integration': [],
                'communication': [],
                'gamification': [],
                'ai_intelligence': [],
                'wsp_framework': [],
                'other': []
            }
            
            for file in files:
                if file:
                    categorized = False
                    for category in modules.keys():
                        if category in file.lower():
                            modules[category].append(file)
                            categorized = True
                            break
                    if not categorized and file:
                        modules['other'].append(file)
            
            # Remove empty categories
            return {k: v for k, v in modules.items() if v}
            
        except:
            return {}
    
    def generate_development_update(self, commits: List[Dict], target_company: str = 'development') -> str:
        """
        Generate LinkedIn content for development updates.
        Follows WSP 22 (ModLog compliance) format.
        """
        if not commits:
            return None
        
        company_info = self.COMPANY_PAGES.get(target_company, self.COMPANY_PAGES['development'])
        
        # Check if single commit or batch
        if len(commits) == 1:
            return self._format_single_commit_update(commits[0], company_info)
        else:
            return self._format_batch_update(commits, company_info)
    
    def _format_single_commit_update(self, commit: Dict, company_info: Dict) -> str:
        """Format single commit as development update"""
        modules = self.get_changed_modules(commit['hash'])
        
        content = "[ROCKET] Development Update\n\n"
        
        # Add WSP references if present
        if commit.get('wsp_refs'):
            content += f"[CLIPBOARD] WSP Protocols: {', '.join(commit['wsp_refs'])}\n\n"
        
        # Main commit message
        content += f"[U+2728] {commit['subject']}\n"
        
        # Add body if meaningful
        if commit.get('body'):
            body_lines = [l.strip() for l in commit['body'].split('\n')[:2] if l.strip()]
            for line in body_lines:
                content += f"   {line}\n"
        
        # Module impact
        if modules:
            content += f"\n[BOX] Modules Updated:\n"
            for module, files in list(modules.items())[:3]:
                content += f"  • {module}: {len(files)} file{'s' if len(files) > 1 else ''}\n"
        
        # Developer credit
        content += f"\n[U+1F468]‍[U+1F4BB] Developer: {commit['author']}\n"
        
        # Add hashtags
        content += "\n#WRE #WSPCompliant #RecursiveImprovement #OpenSource #AgenticSystems"
        
        # Add repo link
        content += "\n\n[LINK] github.com/FOUNDUPS/Foundups-Agent"
        
        return content
    
    def _format_batch_update(self, commits: List[Dict], company_info: Dict) -> str:
        """Format multiple commits as batch update"""
        content = f"[ROCKET] Development Sprint Update - {len(commits)} Changes\n\n"
        
        # Collect all WSP references
        all_wsp_refs = set()
        for commit in commits:
            all_wsp_refs.update(commit.get('wsp_refs', []))
        
        if all_wsp_refs:
            content += f"[CLIPBOARD] WSP Protocols Updated: {', '.join(sorted(all_wsp_refs))}\n\n"
        
        # Categorize commits
        features = []
        fixes = []
        wsp_updates = []
        other = []
        
        for commit in commits:
            subject = commit['subject'].lower()
            if commit.get('wsp_refs'):
                wsp_updates.append(commit)
            elif 'feat' in subject or 'add' in subject or 'implement' in subject:
                features.append(commit)
            elif 'fix' in subject or 'bug' in subject:
                fixes.append(commit)
            else:
                other.append(commit)
        
        # WSP Updates (highest priority)
        if wsp_updates:
            content += "[TARGET] WSP Protocol Updates:\n"
            for commit in wsp_updates[:3]:
                refs = ', '.join(commit['wsp_refs']) if commit['wsp_refs'] else ''
                content += f"  • {commit['subject'][:50]} [{refs}]\n"
        
        # Features
        if features:
            content += "\n[U+2728] New Features:\n"
            for commit in features[:3]:
                content += f"  • {commit['subject'][:60]}\n"
        
        # Fixes
        if fixes:
            content += "\n[TOOL] Bug Fixes:\n"
            for commit in fixes[:3]:
                content += f"  • {commit['subject'][:60]}\n"
        
        # Module impact summary
        all_modules = {}
        for commit in commits:
            modules = self.get_changed_modules(commit['hash'])
            for module, files in modules.items():
                if module not in all_modules:
                    all_modules[module] = set()
                all_modules[module].update(files)
        
        if all_modules:
            content += f"\n[DATA] Impact Summary:\n"
            total_files = sum(len(files) for files in all_modules.values())
            content += f"  • {total_files} files across {len(all_modules)} modules\n"
            content += f"  • {len(commits)} commits by {len(set(c['author'] for c in commits))} developers\n"
        
        # Add hashtags
        content += "\n#WRE #WSPCompliant #RecursiveImprovement #ContinuousIntegration #AgenticArchitecture"
        
        return content
    
    def post_development_updates(self, count: int = 5, target_company: str = 'development') -> bool:
        """
        Post recent development updates to LinkedIn.
        Follows WSP 50 (Pre-action verification).
        """
        print(f"[WSP 50] Pre-action verification for development updates...")
        
        commits = self.get_recent_commits(count)
        
        if not commits:
            print("[INFO] No commits found")
            return False
        
        # Load memory properly
        if isinstance(self.posted_commits, dict):
            posted_set = set(self.posted_commits.get('commits', []))
        else:
            posted_set = set()
        
        # Filter new commits
        new_commits = [c for c in commits if c['hash'] not in posted_set]
        
        if not new_commits:
            print("[INFO] All recent commits already posted")
            return False
        
        print(f"[INFO] Found {len(new_commits)} new commits to post")
        
        # Generate content
        content = self.generate_development_update(new_commits, target_company)
        
        if content:
            print(f"[POST] Posting to {self.COMPANY_PAGES[target_company]['name']}...")
            print("-" * 40)
            print(content)
            print("-" * 40)
            
            # Post to LinkedIn via unified interface
            import asyncio
            from modules.platform_integration.social_media_orchestrator.src.unified_linkedin_interface import post_development_update

            # Create unique update ID for duplicate detection
            commit_hashes = [commit['hash'] for commit in new_commits]
            update_id = f"dev_update_{hash('|'.join(sorted(commit_hashes)))}"

            # Post via unified interface
            result = asyncio.run(post_development_update(content, update_id))
            success = result.success
            
            if success:
                # Update memory
                for commit in new_commits:
                    posted_set.add(commit['hash'])
                
                self.posted_commits = {
                    'commits': posted_set,
                    'last_check': datetime.now().isoformat()
                }
                self._save_memory()
                
                print(f"[SUCCESS] Posted {len(new_commits)} commits to LinkedIn!")
                return True
            else:
                print("[ERROR] Failed to post update")
                return False
        
        return False
    
    def monitor_development(self, check_interval: int = 300):
        """
        Monitor Git repository per WSP 46 (WRE orchestration).
        
        Args:
            check_interval: Seconds between checks (default 5 minutes)
        """
        print(f"[WRE] Development Monitor DAE starting (interval: {check_interval}s)")
        print("[WSP] Following protocols: WSP 46 (Orchestration), WSP 48 (Recursive improvement)")
        
        while True:
            try:
                print(f"\n[CHECK] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Post updates to development company page
                self.post_development_updates(count=10, target_company='development')
                
                # Wait
                print(f"[WAIT] Next check in {check_interval} seconds...")
                time.sleep(check_interval)
                
            except KeyboardInterrupt:
                print("\n[STOP] Development Monitor DAE stopped")
                break
            except Exception as e:
                print(f"[ERROR] Monitor error: {e}")
                time.sleep(60)


def test_development_monitor():
    """Test the Development Monitor DAE"""
    print("WRE Development Monitor DAE Test")
    print("=" * 60)
    
    monitor = DevelopmentMonitorDAE()
    
    # Get recent commits
    commits = monitor.get_recent_commits(5)
    
    if commits:
        print(f"Found {len(commits)} recent commits:")
        for commit in commits:
            wsp_refs = commit.get('wsp_refs', [])
            wsp_str = f" [{', '.join(wsp_refs)}]" if wsp_refs else ""
            print(f"  • {commit['subject'][:60]}{wsp_str}")
        
        # Check modules
        if commits:
            modules = monitor.get_changed_modules(commits[0]['hash'])
            if modules:
                print(f"\nModules in latest commit:")
                for module, files in modules.items():
                    print(f"  • {module}: {len(files)} files")
        
        # Generate content
        content = monitor.generate_development_update(commits[:3], 'development')
        if content:
            print("\nGenerated LinkedIn content:")
            print("=" * 60)
            print(content)
            print("=" * 60)
            
            # Ask to post
            response = input("\nPost to LinkedIn development page? (y/n): ")
            if response.lower() == 'y':
                success = monitor.post_development_updates(count=3)
                if success:
                    print("[SUCCESS] Posted!")
    else:
        print("No commits found")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--monitor':
        # Run continuous monitoring
        monitor = DevelopmentMonitorDAE()
        monitor.monitor_development()
    else:
        # Run test
        test_development_monitor()