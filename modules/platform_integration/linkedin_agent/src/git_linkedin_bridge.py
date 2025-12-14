#!/usr/bin/env python3
"""
Git to LinkedIn Bridge - Post updates when pushing to Git
Shares development progress with LinkedIn audience
Uses Qwen for 0102-branded condensed content generation
"""

# NOTE: UTF-8 enforcement removed per WSP 90
# Library modules must NOT include UTF-8 enforcement header
# Only entry point files (with if __name__ == "__main__") should have it
# See: main.py for proper UTF-8 enforcement implementation

import os
import re
import sys
import subprocess
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
# Removed direct LinkedIn import - now using unified interface

# Import Qwen for intelligent content generation
try:
    from holo_index.qwen_advisor.llm_engine import QwenInferenceEngine
    QWEN_AVAILABLE = True
except ImportError:
    QWEN_AVAILABLE = False
    print("[INFO] Qwen not available, using template-based generation")

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
        self.repo_root = Path(__file__).resolve().parents[4]

        # Initialize Qwen for 0102-branded content generation
        if QWEN_AVAILABLE:
            # Try HoloIndex model location first (E: drive)
            model_path = Path("E:/HoloIndex/models/qwen-coder-1.5b.gguf")
            if not model_path.exists():
                # Fallback to local models directory
                model_path = Path("models/qwen/qwen-coder-1.5b.gguf")

            if model_path.exists():
                self.qwen = QwenInferenceEngine(model_path=model_path, max_tokens=512, temperature=0.7)
                if self.qwen.initialize():
                    print(f"[0102] Qwen LLM initialized from {model_path} for intelligent git post generation")
                else:
                    self.qwen = None
                    print("[INFO] Qwen initialization failed, using templates")
            else:
                self.qwen = None
                print(f"[INFO] Qwen model not found at E:/HoloIndex/models/, using templates")
        else:
            self.qwen = None

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

            print(f"[DB] Using SQLite database (loaded {len(self.posted_commits)} LinkedIn, {len(self.x_posted_commits)} X posts)")

            # Migrate from JSON if needed
            self._migrate_from_json()

        except Exception as e:
            print(f"[WARN] Database not available, using JSON fallback: {e}")
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
                with open(self.commit_cache_file, 'r', encoding="utf-8") as f:
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
            with open(self.commit_cache_file, 'w', encoding="utf-8") as f:
                json.dump(list(self.posted_commits), f)

    def _load_x_posted_commits(self) -> set:
        """Load X/Twitter posted commits"""
        if os.path.exists(self.x_posted_commits_file):
            try:
                with open(self.x_posted_commits_file, 'r', encoding="utf-8") as f:
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
                with open(ln_json, 'r', encoding="utf-8") as f:
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
                with open(x_json, 'r', encoding="utf-8") as f:
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
            with open(self.x_posted_commits_file, 'w', encoding="utf-8") as f:
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
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=True,
                cwd=str(self.repo_root),
            )
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
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=True,
                cwd=str(self.repo_root),
            )
            return [f for f in result.stdout.strip().split('\n') if f]
        except:
            return []

    def _ascii_safe(self, text: str) -> str:
        """Avoid Windows console encoding issues by stripping non-ascii for messages we print/commit."""
        return "".join(ch for ch in (text or "") if ord(ch) < 128)

    def _compact_subject(self, subject: str, max_len: int = 72) -> str:
        """Compact a subject line to a sane git length without losing the gist."""
        subject = (subject or "").strip().replace("\r", " ").replace("\n", " ")
        subject = re.sub(r"\s+", " ", subject).strip()
        subject = subject.replace("WSP 44", "WSP44").replace("WSP_44", "WSP44")
        subject = subject.replace("YouTube Studio", "YT Studio").replace("YouTube", "YT")
        subject = self._ascii_safe(subject)

        if len(subject) <= max_len:
            return subject

        # Drop parentheticals first
        without_parens = re.sub(r"\s*\([^)]*\)\s*", " ", subject).strip()
        without_parens = re.sub(r"\s+", " ", without_parens).strip()
        without_parens = self._ascii_safe(without_parens)
        if len(without_parens) <= max_len:
            return without_parens

        # Hard truncate as last resort (ASCII-safe)
        return (without_parens[: max_len - 3] + "...") if max_len > 3 else without_parens[:max_len]

    def _extract_context_titles(self, changed_paths: List[str], max_titles: int = 3) -> List[str]:
        """
        Extract human-written context titles from ModLogs (WSP 22), if present.

        This is the most reliable source of "what changed" without LLM hallucination.
        """
        titles: List[str] = []

        def first_title_from_file(path: Path) -> Optional[str]:
            try:
                lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
            except Exception:
                return None

            # Root ModLog style: ## [YYYY-MM-DD] Title
            for line in lines:
                match = re.match(r"^##\s+\[\d{4}-\d{2}-\d{2}\]\s+(.+)$", line.strip())
                if match:
                    return match.group(1).strip()

            # Module ModLog style: ### Phase / ### V### ...
            for line in lines:
                match = re.match(r"^###\s+(.+)$", line.strip())
                if match:
                    return match.group(1).strip()

            return None

        # Prioritize root ModLog, then module ModLogs
        candidates = [p for p in changed_paths if p.endswith("ModLog.md")]
        candidates.sort(key=lambda p: (0 if p == "ModLog.md" else 1, p))

        for rel in candidates:
            if len(titles) >= max_titles:
                break
            title = first_title_from_file(self.repo_root / rel)
            if title:
                compact = self._compact_subject(title, max_len=90)
                if compact and compact not in titles:
                    titles.append(compact)

        return titles

    def _summarize_scope(self, changed_paths: List[str], max_scopes: int = 3) -> List[str]:
        """Summarize changed paths into WSP3 scopes (domain/module) for commit body."""
        counts: Dict[str, int] = {}
        for rel in changed_paths:
            parts = Path(rel).parts
            if len(parts) >= 3 and parts[0] == "modules":
                key = f"{parts[1]}/{parts[2]}"
            elif parts:
                key = parts[0]
            else:
                continue
            counts[key] = counts.get(key, 0) + 1
        ordered = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
        return [item[0] for item in ordered[:max_scopes]]

    def _generate_contextual_commit_message(self, status_lines: List[str]) -> tuple[str, str]:
        """
        Generate a subject + body from repo context.

        Goals:
        - Avoid generic/random templates in autonomous mode
        - Prefer WSP 22 ModLog titles (human-written truth)
        - Include a compact scope summary so future 0102 can reconstruct intent
        """
        changed_paths: List[str] = []
        counts = {"added": 0, "modified": 0, "deleted": 0, "untracked": 0, "renamed": 0}

        for raw in status_lines:
            # Preserve leading spaces: porcelain v1 is fixed-width "XY <path>"
            line = (raw or "").rstrip("\r\n")
            if not line.strip():
                continue
            status = line[:2]
            path_part = line[3:].strip() if len(line) > 3 else ""
            if "->" in path_part:
                counts["renamed"] += 1
                path_part = path_part.split("->")[-1].strip()
            rel = path_part.strip().strip('"')
            if rel:
                changed_paths.append(rel)

            if status == "??":
                counts["untracked"] += 1
            if "D" in status:
                counts["deleted"] += 1
            elif "A" in status:
                counts["added"] += 1
            elif "M" in status or "R" in status:
                counts["modified"] += 1

        titles = self._extract_context_titles(changed_paths)
        scopes = self._summarize_scope(changed_paths)

        # Subject: prefer ModLog title, else a scoped summary
        subject = titles[0] if titles else ""
        if not subject:
            scope = scopes[0] if scopes else "repo"
            subject = f"{scope}: update ({len(changed_paths)} files)"

        subject = self._compact_subject(subject, max_len=72)
        if not subject:
            subject = "chore: update"

        # Body: short, factual, reconstructable
        body_lines: List[str] = []
        if titles:
            body_lines.append("Context:")
            for title in titles[:3]:
                body_lines.append(f"- {self._ascii_safe(title)}")
            body_lines.append("")

        body_lines.append(
            f"Files: {len(changed_paths)} (A:{counts['added']} M:{counts['modified']} D:{counts['deleted']} ?: {counts['untracked']})"
        )
        if scopes:
            body_lines.append(f"Scope: {', '.join(scopes)}")

        # Optional diff shortstat (best-effort; ignore failures)
        try:
            diff = subprocess.run(
                ["git", "diff", "--cached", "--shortstat"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
                cwd=str(self.repo_root),
            )
            shortstat = (diff.stdout or "").strip()
            shortstat = self._ascii_safe(shortstat)
            if shortstat:
                body_lines.append(f"Diff: {shortstat}")
        except Exception:
            pass

        body = "\n".join(body_lines).strip()
        body = self._ascii_safe(body)
        return subject, body

    def generate_linkedin_content(self, commits: List[Dict]) -> str:
        """
        Generate LinkedIn post content from Git commits using direct commit messages.
        Always starts with "0102" and represents WSP_00 Zen State / pArtifact.

        Args:
            commits: List of commit information

        Returns:
            Formatted LinkedIn post content (direct commit message, 0102-branded)
        """
        if not commits:
            return None

        commit = commits[0] if len(commits) == 1 else commits[0]
        commit_msg = commit['subject']
        files = self.get_changed_files(commit['hash'])

        # Direct commit message approach - simplest and most reliable
        content = f"0102: {commit_msg}\n\n"
        content += f"Files updated: {len(files)}\n\n"
        content += f"GitHub: https://github.com/Foundup/Foundups-Agent\n\n"
        content += "#0102 #WSP #AutonomousDevelopment"

        print(f"[0102] Direct commit message content: {len(content)} chars")
        return content
    
    def _format_single_commit(self, commit: Dict) -> str:
        """Format a single commit for LinkedIn"""
        # Get changed files
        files = self.get_changed_files(commit['hash'])
        
        # Determine the type of update
        update_type = self._categorize_commit(commit, files)
        
        # Create engaging content
        content = f"[ROCKET] Development Update: {update_type}\n\n"
        
        # Add commit message
        content += f"[U+2728] {commit['subject']}\n"
        
        if commit['body']:
            # Add first few lines of body if present
            body_lines = commit['body'].strip().split('\n')[:2]
            for line in body_lines:
                if line.strip():
                    content += f"   {line.strip()}\n"
        
        # Add file statistics
        if files:
            content += f"\n[NOTE] {len(files)} file{'s' if len(files) > 1 else ''} updated\n"
            
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
        content += "\n\n[LINK] github.com/Foundups-Agent"
        
        return content
    
    def _format_multiple_commits(self, commits: List[Dict]) -> str:
        """Format multiple commits as a batch update"""
        content = f"[ROCKET] Development Updates - {len(commits)} New Changes\n\n"
        
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
            content += "[U+2728] New Features:\n"
            for commit in features[:3]:
                content += f"  • {commit['subject'][:60]}\n"
        
        # Add fixes
        if fixes:
            content += "\n[TOOL] Bug Fixes:\n"
            for commit in fixes[:3]:
                content += f"  • {commit['subject'][:60]}\n"
        
        # Add other updates
        if other:
            content += "\n[NOTE] Other Updates:\n"
            for commit in other[:2]:
                content += f"  • {commit['subject'][:60]}\n"
        
        # Add summary stats
        total_files = set()
        for commit in commits:
            files = self.get_changed_files(commit['hash'])
            total_files.update(files)
        
        content += f"\n[DATA] Impact: {len(total_files)} files updated across {len(commits)} commits\n"
        
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
        """
        Generate ultra-condensed X/Twitter content using direct commit message.
        Always starts with "0102". Must stay under 280 chars.

        Args:
            commit_msg: Git commit message
            file_count: Number of files changed

        Returns:
            Ultra-condensed 0102-branded X post (<280 chars)
        """
        # Direct approach - most reliable and simple
        short_msg = commit_msg[:60] + "..." if len(commit_msg) > 60 else commit_msg

        content = f"0102: {short_msg}\n\n{file_count} files updated\n\nhttps://github.com/Foundup/Foundups-Agent\n\n#0102"

        # Enforce 280 char limit
        if len(content) > 280:
            content = f"0102: {file_count} files\n\n{commit_msg[:50]}\n\nhttps://github.com/Foundup/Foundups-Agent\n\n#0102"

        print(f"[0102] Direct X content: {len(content)} chars")
        return content

    def push_and_post(self) -> bool:
        """Main function to push to git and post to both LinkedIn and X"""
        try:
            import subprocess
            from datetime import datetime

            # Check git status
            status = subprocess.run(
                ['git', 'status', '--porcelain=v1'],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=True,
                cwd=str(self.repo_root),
            )

            if not status.stdout.strip():
                print("[OK] No changes to commit")
                return False

            # Show changes
            print("\n[NOTE] Changes detected:")
            print("-" * 40)
            # Preserve leading spaces (porcelain v1 is fixed-width "XY <path>")
            files = status.stdout.splitlines()
            for file in files[:10]:
                print(f"  {file}")
            if len(files) > 10:
                print(f"  ... and {len(files) - 10} more files")
            print("-" * 40)

            # Stage changes before generating an auto message so commit notes match what gets committed.
            # Safety: exclude volatile/large paths from autonomous commits.
            excluded_paths = [
                'node_modules',
                'modules/platform_integration/browser_profiles',
                'telemetry',
                'modules/telemetry/feedback',
                'holo_index/holo_index/output',
            ]

            try:
                add_cmd = ['git', 'add', '-A', '--', '.'] + [f':(exclude){p}' for p in excluded_paths]
                subprocess.run(add_cmd, check=True, cwd=str(self.repo_root))
            except subprocess.CalledProcessError:
                # Fallback for older git versions that don't support pathspec excludes.
                subprocess.run(['git', 'add', '-A'], check=True, cwd=str(self.repo_root))
                for path in excluded_paths:
                    subprocess.run(['git', 'reset', '--', path], check=False, cwd=str(self.repo_root))

            staged_status = subprocess.run(
                ['git', 'status', '--porcelain=v1'],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=True,
                cwd=str(self.repo_root),
            )
            staged_lines = [
                ln for ln in staged_status.stdout.splitlines()
                if ln and len(ln) >= 2 and ln[:2] != "??" and ln[0] != " "
            ]
            staged_file_count = len(staged_lines)

            if staged_file_count == 0:
                print("[OK] No staged changes to commit (only excluded paths changed?)")
                return False

            # Get commit message (handle both interactive and auto mode)
            if hasattr(self, 'auto_mode') and self.auto_mode:
                commit_msg = ""
                print("[BOT] Auto mode - generating message...")
            else:
                try:
                    commit_msg = input("\n[NOTE] Enter commit message (or press Enter for auto): ").strip()
                except EOFError:
                    # Running in non-interactive mode
                    commit_msg = ""
                    print("[BOT] Non-interactive mode - generating message...")

            if not commit_msg:
                commit_msg, commit_body = self._generate_contextual_commit_message(staged_lines)
            else:
                commit_body = ""

            print(f"\n[REFRESH] Committing: {commit_msg}")

            # Git operations
            print("\n[U+2699]️  Executing git commands...")
            # Prevent local git hooks from duplicating posting during automation.
            git_env = dict(os.environ)
            git_env["FOUNDUPS_SKIP_POST_COMMIT"] = "1"
            commit_cmd = ['git', 'commit', '-m', commit_msg]
            if commit_body:
                commit_cmd.extend(['-m', commit_body])
            subprocess.run(commit_cmd, check=True, cwd=str(self.repo_root), env=git_env)

            # Get commit hash
            hash_result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=True,
                cwd=str(self.repo_root),
            )
            commit_hash = hash_result.stdout.strip()

            def _push_current_branch(remote: str = "origin") -> bool:
                """Push current branch; auto-set upstream when missing."""
                branch_result = subprocess.run(
                    ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    check=True,
                    cwd=str(self.repo_root),
                )
                branch = branch_result.stdout.strip()

                push_result = subprocess.run(
                    ['git', 'push'],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    cwd=str(self.repo_root),
                )
                if push_result.returncode == 0:
                    return True

                combined = "\n".join(part for part in [push_result.stderr, push_result.stdout] if part).strip()
                combined_lower = combined.lower()
                if "no upstream branch" in combined_lower or "has no upstream branch" in combined_lower:
                    upstream_result = subprocess.run(
                        ['git', 'push', '--set-upstream', remote, branch],
                        capture_output=True,
                        text=True,
                        encoding="utf-8",
                        errors="replace",
                        cwd=str(self.repo_root),
                    )
                    if upstream_result.returncode == 0:
                        print(f"[OK] Set upstream and pushed to {remote}/{branch}")
                        return True

                    upstream_combined = "\n".join(
                        part for part in [upstream_result.stderr, upstream_result.stdout] if part
                    ).strip()
                    print(f"[U+26A0]️  Git push failed after setting upstream: {upstream_combined}")
                    return False

                print(f"[U+26A0]️  Git push failed: {combined}")
                return False

            # Always push before social posting; skip posting if push fails.
            if not _push_current_branch():
                print("\n[U+26A0]️  Note: Git push failed - skipping social media posting")
                return False

            print(f"[OK] Successfully pushed to git! (commit: {commit_hash[:10]})")

            # Skip posting if this commit was already posted to both platforms.
            if commit_hash in self.posted_commits and commit_hash in self.x_posted_commits:
                print(f"[U+26A0]️  Commit {commit_hash[:10]} already posted to both platforms")
                print("[OK] Git push complete; skipping social media.")
                return True

            # Prepare commit info
            commit_info = {
                'hash': commit_hash,
                'subject': commit_msg,
                'body': '',
                'timestamp': int(datetime.now().timestamp())
            }

            # Generate content
            linkedin_content = self.generate_linkedin_content([commit_info])
            x_content = self.generate_x_content(commit_msg, staged_file_count)

            # Show previews
            print(f"\n[U+1F4F1] LinkedIn Post Preview:\n{'-'*40}\n{linkedin_content}\n{'-'*40}")
            print(f"\n[BIRD] X/Twitter Post Preview:\n{'-'*40}\n{x_content}\n{'-'*40}")

            # Confirm posting (handle auto mode)
            if hasattr(self, 'auto_mode') and self.auto_mode:
                confirm = 'y'
                print("\n[U+1F4E4] Auto-posting to LinkedIn and X...")
            else:
                try:
                    confirm = input("\n[U+1F4E4] Post to LinkedIn and X? (y/n): ").lower()
                except EOFError:
                    confirm = 'y'
                    print("\n[U+1F4E4] Non-interactive mode - auto-posting...")

            if confirm != 'y':
                print("⏭️  Skipped social media posting")
                return True

            # Post via Unified Interface (auto-triggers both LinkedIn AND X)
            # All anti-detection timing, delays, and logging handled in daemon
            if commit_hash not in self.posted_commits:
                try:
                    from modules.platform_integration.social_media_orchestrator.src.unified_linkedin_interface import post_git_commits
                    import asyncio

                    print("\n[U+1F4F1] Posting via Social Media DAE (LinkedIn -> Auto X)...")

                    # Single call posts to BOTH platforms with human-like timing
                    result = asyncio.run(post_git_commits(
                        linkedin_content,
                        [commit_hash],
                        x_content=x_content,
                        auto_post_to_x=True
                    ))

                    if result.success:
                        print(f"[OK] {result.message}")

                        # Mark LinkedIn as posted
                        if self.db:
                            from datetime import datetime
                            self.db.execute_write("""
                                INSERT OR REPLACE INTO modules_git_linkedin_posts
                                (commit_hash, commit_message, post_content, success, posted_at)
                                VALUES (?, ?, ?, ?, ?)
                            """, (commit_hash, commit_msg, linkedin_content, 1, datetime.now()))
                        self.posted_commits.add(commit_hash)
                        self._save_posted_commits()

                        # Mark X as posted (auto-triggered by unified interface)
                        if "X:" in result.message:
                            if self.db:
                                from datetime import datetime
                                self.db.execute_write("""
                                    INSERT OR REPLACE INTO modules_git_x_posts
                                    (commit_hash, commit_message, post_content, success, posted_at)
                                    VALUES (?, ?, ?, ?, ?)
                                """, (commit_hash, commit_msg, x_content, 1, datetime.now()))
                            self.x_posted_commits.add(commit_hash)
                            self._save_x_posted_commits()
                    else:
                        # Log failure - daemon has full details
                        print(f"[U+26A0]️  {result.message}")
                        print("   See daemon logs for anti-detection timing and full trace")

                except Exception as e:
                    # Log exception - daemon has full stack trace
                    print(f"[FAIL] {e}")
                    print("   See daemon logs for complete error details")
            else:
                print("[OK] Already posted")

            return True

        except subprocess.CalledProcessError as e:
            print(f"[FAIL] Git error: {e}")
            print("   Make sure you have git configured and are in a git repository")
            return False
        except Exception as e:
            print(f"[FAIL] Error: {e}")
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
