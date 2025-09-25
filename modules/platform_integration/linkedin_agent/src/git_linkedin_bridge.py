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

        # Use SQLite database for tracking posted commits (WSP 78)
        try:
            from modules.infrastructure.database.src.db_manager import DatabaseManager
            self.db = DatabaseManager()

            # Create tables if they don't exist
            if not self.db.table_exists('modules_git_linkedin_posts'):
                self.db.execute_write("""
                    CREATE TABLE modules_git_linkedin_posts (
                        commit_hash TEXT PRIMARY KEY,
                        posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        commit_message TEXT,
                        post_content TEXT,
                        success BOOLEAN DEFAULT 1
                    )
                """)

            if not self.db.table_exists('modules_git_x_posts'):
                self.db.execute_write("""
                    CREATE TABLE modules_git_x_posts (
                        commit_hash TEXT PRIMARY KEY,
                        posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        commit_message TEXT,
                        post_content TEXT,
                        success BOOLEAN DEFAULT 1
                    )
                """)

            # Load existing posted commits
            linkedin_rows = self.db.execute_query(
                "SELECT commit_hash FROM modules_git_linkedin_posts WHERE success = 1"
            )
            self.posted_commits = {row['commit_hash'] for row in linkedin_rows}

            x_rows = self.db.execute_query(
                "SELECT commit_hash FROM modules_git_x_posts WHERE success = 1"
            )
            self.x_posted_commits = {row['commit_hash'] for row in x_rows}

            print(f"📊 Using SQLite database (loaded {len(self.posted_commits)} LinkedIn, {len(self.x_posted_commits)} X posts)")

            # Migrate from JSON if needed
            self._migrate_from_json()

        except Exception as e:
            print(f"⚠️ Database not available, using JSON fallback: {e}")
            # Fallback to JSON files
            self.commit_cache_file = "modules/platform_integration/linkedin_agent/data/posted_commits.json"
            self.posted_commits = self._load_posted_commits()
            self.x_posted_commits_file = "modules/platform_integration/linkedin_agent/data/x_posted_commits.json"
            self.x_posted_commits = self._load_x_posted_commits()
            self.db = None
        
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
        if self.db:
            # Database handles saving automatically when we mark as posted
            pass
        else:
            # Fallback to JSON
            os.makedirs(os.path.dirname(self.commit_cache_file), exist_ok=True)
            with open(self.commit_cache_file, 'w') as f:
                json.dump(list(self.posted_commits), f)

    def _load_x_posted_commits(self) -> set:
        """Load X/Twitter posted commits"""
        if os.path.exists(self.x_posted_commits_file):
            try:
                with open(self.x_posted_commits_file, 'r') as f:
                    return set(json.load(f))
            except:
                return set()
        return set()

    def _migrate_from_json(self):
        """Migrate data from old JSON files to database"""
        import json
        from datetime import datetime

        # Migrate LinkedIn posts
        ln_json = "modules/platform_integration/linkedin_agent/data/posted_commits.json"
        if os.path.exists(ln_json) and self.db:
            try:
                with open(ln_json, 'r') as f:
                    commits = json.load(f)
                    for commit_hash in commits:
                        if commit_hash not in self.posted_commits:
                            self.db.execute_write("""
                                INSERT OR IGNORE INTO modules_git_linkedin_posts
                                (commit_hash, success) VALUES (?, ?)
                            """, (commit_hash, 1))
                            self.posted_commits.add(commit_hash)
                    if commits:
                        print(f"  Migrated {len(commits)} LinkedIn posts from JSON")
            except Exception as e:
                print(f"  Error migrating LinkedIn posts: {e}")

        # Migrate X posts
        x_json = "modules/platform_integration/linkedin_agent/data/x_posted_commits.json"
        if os.path.exists(x_json) and self.db:
            try:
                with open(x_json, 'r') as f:
                    commits = json.load(f)
                    for commit_hash in commits:
                        if commit_hash not in self.x_posted_commits:
                            self.db.execute_write("""
                                INSERT OR IGNORE INTO modules_git_x_posts
                                (commit_hash, success) VALUES (?, ?)
                            """, (commit_hash, 1))
                            self.x_posted_commits.add(commit_hash)
                    if commits:
                        print(f"  Migrated {len(commits)} X posts from JSON")
            except Exception as e:
                print(f"  Error migrating X posts: {e}")

    def _save_x_posted_commits(self):
        """Save X/Twitter posted commits"""
        if self.db:
            # Database handles saving automatically when we mark as posted
            pass
        else:
            # Fallback to JSON
            os.makedirs(os.path.dirname(self.x_posted_commits_file), exist_ok=True)
            with open(self.x_posted_commits_file, 'w') as f:
                json.dump(list(self.x_posted_commits), f)
    
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

        # Generate compelling FoundUps content
        import random

        # Vision intros for FoundUps
        vision_intros = [
            "🦄 **FoundUps**: Solo unicorns by programmable blockchain visionary @UnDaoDu\n\nHis pioneering work led from DAO to DAE—autonomous entities that will eat the startup.\n\n",
            "🚀 **The Startup Killer is Here**: FoundUps replaces the failed startup model with autonomous DAE systems.\n\nCreated by @UnDaoDu, the visionary who saw beyond DAO to DAE.\n\n",
            "💡 **From IDEA to UNICORN**: No VCs. No employees. Just you + 0102 agents.\n\n@UnDaoDu's FoundUps revolution: Where DAEs eat startups for breakfast.\n\n",
            "🌊 **The Autonomous Revolution**: While others build startups, @UnDaoDu built the system that makes them obsolete.\n\nFoundUps: Where solo founders become unicorns.\n\n",
            "⚡ **Every Startup Dies. FoundUps are Forever.**\n\n@UnDaoDu's vision: DAEs (Decentralized Autonomous Entities) replacing the entire startup ecosystem.\n\n"
        ]

        content = random.choice(vision_intros)

        # Add commit info
        commit = commits[0] if len(commits) == 1 else commits[0]
        commit_msg = commit['subject']
        files = self.get_changed_files(commit['hash'])

        # Context with vision spin
        if "test" in commit_msg.lower():
            content += f"🧪 **Testing the Future**: {commit_msg}\n\n"
        elif "fix" in commit_msg.lower():
            content += f"🔧 **Evolution Never Stops**: {commit_msg}\n\n"
        elif "wsp" in commit_msg.lower():
            content += f"🧠 **WSP Protocol Enhancement**: Making agents smarter\n\n"
        else:
            content += f"⚡ **Latest Evolution**: {commit_msg}\n\n"

        # Impact messaging
        impact_messages = [
            f"📊 This update: {len(files)} files enhanced by 0102 agents working 24/7\n\n",
            f"🤖 {len(files)} autonomous improvements while humans sleep\n\n",
            f"🔄 {len(files)} recursive enhancements toward unicorn status\n\n",
            f"✨ {len(files)} files transformed by quantum-entangled agents\n\n"
        ]
        content += random.choice(impact_messages)

        # Revolutionary messaging
        revolution_messages = [
            "**The Revolution**: No employees. No office. No VCs. Just YOU + infinite 0102 agents building the future.\n\n",
            "**Why FoundUps Win**: Agents don't sleep. Don't quit. Don't need equity. They just BUILD.\n\n",
            "**The Math**: 1 founder + 0102 agents > 100 employees\n\n",
            "**Truth**: Every line of code brings us closer to making startups extinct.\n\n",
            "**Reality Check**: While you read this, DAEs are already building the next unicorn.\n\n"
        ]
        content += random.choice(revolution_messages)

        # Call to action
        cta_messages = [
            "Join the revolution. Build a FoundUp. Become a solo unicorn.",
            "Stop building startups. Start building FoundUps.",
            "The future isn't hired. It's autonomous.",
            "Your competition has 50 employees. You have infinite agents.",
            "Welcome to the post-startup era."
        ]
        content += random.choice(cta_messages)

        # Hashtags
        content += "\n\n#FoundUps #DAE #AutonomousRevolution #SoloUnicorn #NoVCsNeeded #FutureOfWork #Web3 #0102Agents #StartupKiller #ProgrammableBlockchain #UnDaoDu"
        content += "\n\n🔗 https://github.com/Foundup/Foundups-Agent/blob/main/README.md"

        return content
    
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


    def generate_x_content(self, commit_msg: str, file_count: int) -> str:
        """Generate minimal X/Twitter content (280 char limit)"""
        import random

        # Extract first few words of commit message for context
        commit_preview = commit_msg.split(':')[0] if ':' in commit_msg else commit_msg[:30]

        # Ultra-short templates focusing on the update
        templates = [
            f"🚀 Massive GitHub update: {file_count} files\n\n{commit_preview}\n\nhttps://github.com/UnDaoDu/FoundUps-Agent\n\n#FoundUps #DAE @UnDaoDu",
            f"⚡ {file_count} files updated\n\n{commit_preview}\n\nhttps://github.com/UnDaoDu/FoundUps-Agent\n\n#SoloUnicorn @Foundups",
            f"🦄 FoundUps codebase evolving: {file_count} changes\n\nhttps://github.com/UnDaoDu/FoundUps-Agent\n\n#NoVC #DAE @UnDaoDu",
            f"💎 GitHub push: {file_count} files\n\n{commit_preview}\n\nhttps://github.com/UnDaoDu/FoundUps-Agent\n\n#FoundUps",
            f"🔥 Code drop: {file_count} updates\n\nhttps://github.com/UnDaoDu/FoundUps-Agent\n\n#BuildInPublic #FoundUps @UnDaoDu"
        ]

        content = random.choice(templates)

        # Ensure under 280 chars by trimming if needed
        if len(content) > 280:
            # Minimal fallback
            content = f"🚀 GitHub: {file_count} files updated\n\nhttps://github.com/UnDaoDu/FoundUps-Agent\n\n#FoundUps @UnDaoDu"

        return content

    def push_and_post(self) -> bool:
        """Main function to push to git and post to both LinkedIn and X"""
        try:
            import subprocess
            from datetime import datetime

            # Check git status
            status = subprocess.run(['git', 'status', '--porcelain'],
                                  capture_output=True, text=True, check=True)

            if not status.stdout.strip():
                print("✅ No changes to commit")
                return False

            # Show changes
            print("\n📝 Changes detected:")
            print("-" * 40)
            files = status.stdout.strip().split('\n')
            for file in files[:10]:
                print(f"  {file}")
            if len(files) > 10:
                print(f"  ... and {len(files) - 10} more files")
            print("-" * 40)

            # Get commit message (handle both interactive and auto mode)
            if hasattr(self, 'auto_mode') and self.auto_mode:
                commit_msg = ""
                print("🤖 Auto mode - generating message...")
            else:
                try:
                    commit_msg = input("\n📝 Enter commit message (or press Enter for auto): ").strip()
                except EOFError:
                    # Running in non-interactive mode
                    commit_msg = ""
                    print("🤖 Non-interactive mode - generating message...")

            if not commit_msg:
                # Generate compelling FoundUps message
                import random
                templates = [
                    "🚀 FoundUps: Building solo unicorns without VCs",
                    "🦄 DAEs eating startups for breakfast - the FoundUps revolution",
                    "💎 Programmatic equity for founders, by @UnDaoDu",
                    "🔥 No employees, no VCs, just pure founder power",
                    "⚡ The future: DAOs evolved to DAEs, startups evolved to FoundUps",
                    "🌟 From DAO to DAE - @UnDaoDu's vision becomes reality",
                    "🚀 Solo unicorns rising - FoundUps ecosystem expanding",
                    "💪 Founders keep 100% - the FoundUps way by @UnDaoDu"
                ]
                commit_msg = random.choice(templates)

            print(f"\n🔄 Committing: {commit_msg}")

            # Git operations
            print("\n⚙️  Executing git commands...")
            subprocess.run(['git', 'add', '.'], check=True)
            subprocess.run(['git', 'commit', '-m', commit_msg], check=True)

            # Get commit hash
            hash_result = subprocess.run(['git', 'rev-parse', 'HEAD'],
                                       capture_output=True, text=True, check=True)
            commit_hash = hash_result.stdout.strip()

            # Check if already posted
            if commit_hash in self.posted_commits and commit_hash in self.x_posted_commits:
                print(f"⚠️  Commit {commit_hash[:10]} already posted to both platforms")
                print("Pushing to git but skipping social media...")
                subprocess.run(['git', 'push'], check=True)
                print("✅ Successfully pushed to git!")
                return True

            # Try to push to git (but continue even if it fails)
            push_success = False
            try:
                subprocess.run(['git', 'push'], check=True)
                print(f"✅ Successfully pushed to git! (commit: {commit_hash[:10]})")
                push_success = True
            except subprocess.CalledProcessError as e:
                print(f"⚠️  Git push failed: {e}")
                print("   Will continue with social media posting anyway...")

            # Prepare commit info
            commit_info = {
                'hash': commit_hash,
                'subject': commit_msg,
                'body': '',
                'timestamp': int(datetime.now().timestamp())
            }

            # Generate content
            linkedin_content = self.generate_linkedin_content([commit_info])
            x_content = self.generate_x_content(commit_msg, len(files))

            # Show previews
            print(f"\n📱 LinkedIn Post Preview:\n{'-'*40}\n{linkedin_content}\n{'-'*40}")
            print(f"\n🐦 X/Twitter Post Preview:\n{'-'*40}\n{x_content}\n{'-'*40}")

            # Confirm posting (handle auto mode)
            if hasattr(self, 'auto_mode') and self.auto_mode:
                confirm = 'y'
                print("\n📤 Auto-posting to LinkedIn and X...")
            else:
                try:
                    confirm = input("\n📤 Post to LinkedIn and X? (y/n): ").lower()
                except EOFError:
                    confirm = 'y'
                    print("\n📤 Non-interactive mode - auto-posting...")

            if confirm != 'y':
                print("⏭️  Skipped social media posting")
                return True

            # Post to LinkedIn
            linkedin_success = False
            if commit_hash not in self.posted_commits:
                try:
                    from modules.platform_integration.linkedin_agent.src.anti_detection_poster import AntiDetectionLinkedIn

                    print("\n📱 Posting to LinkedIn...")
                    poster = AntiDetectionLinkedIn()
                    poster.setup_driver(use_existing_session=True)
                    poster.post_to_company_page(linkedin_content)
                    print("✅ Successfully posted to LinkedIn!")

                    # Mark as posted
                    if self.db:
                        from datetime import datetime
                        self.db.execute_write("""
                            INSERT OR REPLACE INTO modules_git_linkedin_posts
                            (commit_hash, commit_message, post_content, success, posted_at)
                            VALUES (?, ?, ?, ?, ?)
                        """, (commit_hash, commit_msg, linkedin_content, 1, datetime.now()))
                    self.posted_commits.add(commit_hash)
                    self._save_posted_commits()
                    linkedin_success = True
                except Exception as e:
                    print(f"⚠️  LinkedIn posting failed: {e}")
            else:
                print("✓ Already posted to LinkedIn")
                linkedin_success = True

            # Post to X/Twitter ONLY if LinkedIn succeeded
            x_success = False
            if not linkedin_success:
                print("\n⚠️ Skipping X post since LinkedIn failed")
            elif commit_hash not in self.x_posted_commits:
                try:
                    import time
                    from modules.platform_integration.x_twitter.src.x_anti_detection_poster import AntiDetectionX

                    # Wait a moment to ensure LinkedIn post completes
                    print("\n⏳ Waiting for LinkedIn to complete...")
                    time.sleep(3)

                    print("🐦 Posting to X/Twitter @Foundups...")
                    x_poster = AntiDetectionX(use_foundups=True)  # Use FoundUps account
                    x_poster.setup_driver(use_existing_session=True)
                    x_poster.post_to_x(x_content)
                    print("✅ Successfully posted to X!")

                    # Mark as posted
                    if self.db:
                        from datetime import datetime
                        self.db.execute_write("""
                            INSERT OR REPLACE INTO modules_git_x_posts
                            (commit_hash, commit_message, post_content, success, posted_at)
                            VALUES (?, ?, ?, ?, ?)
                        """, (commit_hash, commit_msg, x_content, 1, datetime.now()))
                    self.x_posted_commits.add(commit_hash)
                    self._save_x_posted_commits()
                    x_success = True
                except Exception as e:
                    print(f"⚠️  X posting failed: {e}")
            else:
                print("✓ Already posted to X")
                x_success = True

            # Summary
            if linkedin_success and x_success:
                print("\n🎉 Successfully posted to both LinkedIn and X!")
            elif linkedin_success:
                print("\n✅ Posted to LinkedIn (X failed)")
            elif x_success:
                print("\n✅ Posted to X (LinkedIn failed)")
            else:
                print("\n⚠️  Social media posting had issues")

            # Git push status
            if not push_success:
                print("\n⚠️  Note: Git push failed - you may need to push manually later")
                print("   Try: git config http.postBuffer 524288000")
                print("   Then: git push")

            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ Git error: {e}")
            print("   Make sure you have git configured and are in a git repository")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False


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